"""Data validation utilities — pure functions, no Streamlit imports."""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import pandas as pd

from config.data_config import (
    AQI_DERIVED_COLUMNS,
    AQI_DUPLICATE_KEY,
    AQI_RAW_REQUIRED_COLUMNS,
    AQI_SEMANTIC_RANGES,
    COL_AREA,
    COL_CAPACITY,
    COL_CONGESTION,
    COL_DATE,
    COL_H,
    COL_INCIDENTS,
    COL_PEDESTRIAN,
    COL_PM25,
    COL_PT_USAGE,
    COL_ROAD,
    COL_ROADWORK,
    COL_SIGNAL,
    COL_SLP,
    COL_SPEED,
    COL_T,
    COL_TM,
    COL_TM_MAX,
    COL_TRAFFIC_VOL,
    COL_V,
    COL_VV,
    COL_WEATHER,
    COL_AQI_CATEGORY,
    COL_SEASON,
    DATA_SCHEMA_VERSION,
    INCIDENT_NULL_FILL_MAX_RATIO,
    RAW_DUPLICATE_TOLERANCE,
    ROADWORK_CATEGORY_ALIASES,
    SUPPORTED_SCHEMA_VERSIONS,
    TRAFFIC_DERIVED_COLUMNS,
    TRAFFIC_DUPLICATE_KEY,
    MIN_PROCESSED_AQI_ROWS,
    MIN_PROCESSED_TRAFFIC_ROWS,
    TRAFFIC_RAW_CATEGORY_COLUMNS,
    TRAFFIC_RAW_REQUIRED_COLUMNS,
    TRAFFIC_SEMANTIC_RANGES,
    UNKNOWN_CATEGORY_ERROR_RATIO,
    UNKNOWN_CATEGORY_WARNING_RATIO,
    WEATHER_CATEGORY_ALIASES,
)

MIN_ROWS_WARNING = 10
MIN_ROWS_ERROR = 1


class DataValidationError(ValueError):
    """Raised when dataset or filter inputs fail validation at data boundaries."""


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    message: str = ""
    level: str = "error"  # "error" | "warning"

    @property
    def is_warning(self) -> bool:
        return not self.ok and self.level == "warning"


def validate_required_columns(df: pd.DataFrame, cols: Sequence[str]) -> ValidationResult:
    """Verify that all required columns are present."""
    if df.empty:
        return ValidationResult(True)
    missing = [c for c in cols if c not in df.columns]
    if missing:
        return ValidationResult(False, f"Missing required column(s): {', '.join(missing)}")
    return ValidationResult(True)


def _check_numeric_column(df: pd.DataFrame, col: str) -> ValidationResult:
    if col not in df.columns:
        return ValidationResult(True)
    if not pd.api.types.is_numeric_dtype(df[col]):
        return ValidationResult(False, f"Column '{col}' must be numeric")
    return ValidationResult(True)


def _check_datetime_column(df: pd.DataFrame, col: str) -> ValidationResult:
    if col not in df.columns:
        return ValidationResult(True)
    if not pd.api.types.is_datetime64_any_dtype(df[col]):
        try:
            pd.to_datetime(df[col].head(5))
        except (TypeError, ValueError):
            return ValidationResult(False, f"Column '{col}' must be parseable as datetime")
    return ValidationResult(True)


TRAFFIC_SCHEMA_COLUMNS = [
    COL_DATE,
    COL_AREA,
    COL_ROAD,
    COL_CONGESTION,
    COL_SPEED,
    COL_INCIDENTS,
    COL_CAPACITY,
]

TRAFFIC_CLEAN_COLUMNS = TRAFFIC_SCHEMA_COLUMNS + list(TRAFFIC_DERIVED_COLUMNS)

AQI_SCHEMA_COLUMNS = [
    COL_DATE,
    COL_PM25,
    COL_T,
    COL_TM,
    COL_TM_MAX,
    COL_SLP,
    COL_H,
    COL_VV,
    COL_V,
]

AQI_CLEAN_COLUMNS = AQI_SCHEMA_COLUMNS + list(AQI_DERIVED_COLUMNS)


def validate_traffic_schema(df: pd.DataFrame) -> ValidationResult:
    """Validate traffic dataset columns and critical dtypes."""
    result = validate_required_columns(df, TRAFFIC_CLEAN_COLUMNS)
    if not result.ok:
        return result
    if df.empty:
        return ValidationResult(True)
    for col in (COL_CONGESTION, COL_SPEED, COL_CAPACITY, COL_INCIDENTS):
        r = _check_numeric_column(df, col)
        if not r.ok:
            return r
    return _check_datetime_column(df, COL_DATE)


def validate_aqi_schema(df: pd.DataFrame) -> ValidationResult:
    """Validate AQI dataset columns and critical dtypes."""
    result = validate_required_columns(df, AQI_CLEAN_COLUMNS)
    if not result.ok:
        return result
    if df.empty:
        return ValidationResult(True)
    r = _check_numeric_column(df, COL_PM25)
    if not r.ok:
        return r
    return _check_datetime_column(df, COL_DATE)


def validate_filter_date_range(start: Any, end: Any) -> ValidationResult:
    """Validate user-selected filter dates (reversed or invalid)."""
    try:
        s = pd.Timestamp(start)
        e = pd.Timestamp(end)
    except (TypeError, ValueError):
        return ValidationResult(False, "Invalid filter date values")
    if pd.isna(s) or pd.isna(e):
        return ValidationResult(False, "Filter dates cannot be empty")
    if s > e:
        return ValidationResult(False, "Start date must be on or before end date")
    return ValidationResult(True)


def validate_date_range(
    df: pd.DataFrame,
    start: Any,
    end: Any,
    date_col: str = COL_DATE,
) -> ValidationResult:
    """Validate requested filter range against dataset bounds."""
    dr = validate_filter_date_range(start, end)
    if not dr.ok:
        return dr
    if df.empty or date_col not in df.columns:
        return ValidationResult(True)
    s = pd.Timestamp(start)
    e = pd.Timestamp(end)
    data_min = pd.Timestamp(df[date_col].min())
    data_max = pd.Timestamp(df[date_col].max())
    if e < data_min or s > data_max:
        return ValidationResult(
            False,
            f"Filter range {fmt_range_label(s, e)} has no overlap with data ({fmt_range_label(data_min, data_max)})",
            level="warning",
        )
    return ValidationResult(True)


def fmt_range_label(start: pd.Timestamp, end: pd.Timestamp) -> str:
    return f"{start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}"


def validate_row_count(df: pd.DataFrame, min_rows: int = MIN_ROWS_WARNING) -> ValidationResult:
    """Return warning semantics for low or empty filtered datasets."""
    n = len(df)
    if n == 0:
        return ValidationResult(False, "No records match the current filters", level="warning")
    if n < min_rows:
        return ValidationResult(
            False,
            f"Low sample size (n={n}); interpret charts with caution",
            level="warning",
        )
    return ValidationResult(True)


def assert_traffic_schema(df: pd.DataFrame) -> None:
    result = validate_traffic_schema(df)
    if not result.ok:
        raise DataValidationError(result.message)


def assert_aqi_schema(df: pd.DataFrame) -> None:
    result = validate_aqi_schema(df)
    if not result.ok:
        raise DataValidationError(result.message)


# ---------------------------------------------------------------------------
# Raw ingestion validation (Phase 2) — canonical normalized dataframes only
# ---------------------------------------------------------------------------


class ValidationSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class ValidationFinding:
    code: str
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    column: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "column": self.column,
        }


@dataclass
class RawValidationReport:
    """Collects multiple raw-ingestion findings with severity accounting."""

    dataset: str
    findings: list[ValidationFinding] = field(default_factory=list)
    duplicate_count: int = 0
    null_stats: dict[str, Any] = field(default_factory=dict)
    source_metadata: dict[str, Any] = field(default_factory=dict)

    def add(self, finding: ValidationFinding) -> None:
        self.findings.append(finding)

    @property
    def severity_counts(self) -> dict[str, int]:
        counts = {s.value: 0 for s in ValidationSeverity}
        for f in self.findings:
            counts[f.severity.value] = counts.get(f.severity.value, 0) + 1
        return counts

    @property
    def has_blocking_findings(self) -> bool:
        return any(
            f.severity in (ValidationSeverity.CRITICAL, ValidationSeverity.ERROR)
            for f in self.findings
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset": self.dataset,
            "findings": [f.to_dict() for f in self.findings],
            "severity_counts": self.severity_counts,
            "duplicate_count": self.duplicate_count,
            "null_stats": self.null_stats,
            "source_metadata": self.source_metadata,
            "has_blocking_findings": self.has_blocking_findings,
        }


def hash_source_file(path: Path | str) -> dict[str, Any]:
    """SHA-256 hash and size for source drift detection."""
    p = Path(path)
    digest = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return {
        "path": str(p.resolve()),
        "size_bytes": p.stat().st_size,
        "sha256": digest.hexdigest(),
    }


def validate_schema_version(
    version: str,
    *,
    supported: frozenset[str] | None = None,
) -> ValidationFinding | None:
    allowed = supported or SUPPORTED_SCHEMA_VERSIONS
    if version not in allowed:
        return ValidationFinding(
            code="schema_version_incompatible",
            message=f"Schema version '{version}' is not supported (expected one of {sorted(allowed)})",
            severity=ValidationSeverity.CRITICAL,
        )
    return None


def validate_raw_required_columns(
    df: pd.DataFrame,
    required: Sequence[str],
    dataset: str,
) -> list[ValidationFinding]:
    if df.empty:
        return [
            ValidationFinding(
                code="empty_dataset",
                message=f"{dataset} normalized dataframe is empty after intake",
                severity=ValidationSeverity.CRITICAL,
            )
        ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        return [
            ValidationFinding(
                code="missing_required_columns",
                message=f"Missing required column(s): {', '.join(missing)}",
                severity=ValidationSeverity.CRITICAL,
            )
        ]
    return []


def _normalize_category_value(value: Any, alias_map: dict[str, str]) -> str | None:
    if pd.isna(value):
        return None
    text = " ".join(str(value).strip().split())
    if not text:
        return None
    key = text.lower()
    if key in alias_map:
        return alias_map[key]
    if text in alias_map.values():
        return text
    return text


def validate_raw_categories(
    df: pd.DataFrame,
    column: str,
    allowed: tuple[str, ...],
    alias_map: dict[str, str],
    *,
    warning_ratio: float = UNKNOWN_CATEGORY_WARNING_RATIO,
    error_ratio: float = UNKNOWN_CATEGORY_ERROR_RATIO,
) -> list[ValidationFinding]:
    if column not in df.columns or df.empty:
        return []

    normalized = df[column].map(lambda v: _normalize_category_value(v, alias_map))
    known = set(allowed)
    valid_mask = normalized.notna()
    unknown_mask = valid_mask & ~normalized.isin(known)
    unknown_count = int(unknown_mask.sum())
    if unknown_count == 0:
        return []

    ratio = unknown_count / max(len(df), 1)
    sample = sorted(normalized[unknown_mask].dropna().unique().tolist())[:5]
    severity = ValidationSeverity.WARNING
    if ratio > error_ratio:
        severity = ValidationSeverity.ERROR
    elif ratio > warning_ratio:
        severity = ValidationSeverity.WARNING
    else:
        return []

    return [
        ValidationFinding(
            code="unknown_category_values",
            message=(
                f"{unknown_count} unknown value(s) in '{column}' "
                f"({ratio:.2%} of rows); examples: {sample}"
            ),
            severity=severity,
            column=column,
        )
    ]


def validate_raw_duplicates(
    df: pd.DataFrame,
    key_columns: Sequence[str],
    *,
    tolerance: int = RAW_DUPLICATE_TOLERANCE,
) -> tuple[int, ValidationFinding | None]:
    if df.empty or any(c not in df.columns for c in key_columns):
        return 0, None
    dup_count = int(df.duplicated(subset=list(key_columns), keep=False).sum())
    if dup_count <= tolerance:
        return dup_count, None
    return dup_count, ValidationFinding(
        code="duplicate_keys",
        message=(
            f"{dup_count} row(s) participate in duplicate keys "
            f"({', '.join(key_columns)}); tolerance={tolerance}"
        ),
        severity=ValidationSeverity.ERROR,
    )


def collect_raw_null_stats(df: pd.DataFrame, columns: Sequence[str]) -> dict[str, int]:
    return {col: int(df[col].isna().sum()) for col in columns if col in df.columns}


def validate_raw_null_policy_traffic(df: pd.DataFrame) -> tuple[dict[str, Any], list[ValidationFinding]]:
    """Report nulls; incident fill is policy metadata only (no mutation in validation)."""
    findings: list[ValidationFinding] = []
    required_metrics = [
        COL_CONGESTION,
        COL_SPEED,
        COL_CAPACITY,
        COL_PEDESTRIAN,
        COL_PT_USAGE,
        COL_SIGNAL,
        COL_TRAFFIC_VOL,
    ]
    null_stats = collect_raw_null_stats(df, TRAFFIC_RAW_REQUIRED_COLUMNS)

    for col in required_metrics:
        n = null_stats.get(col, 0)
        if n:
            findings.append(
                ValidationFinding(
                    code="required_metric_null",
                    message=f"{n} null value(s) in required metric '{col}'",
                    severity=ValidationSeverity.ERROR,
                    column=col,
                )
            )

    incident_nulls = null_stats.get(COL_INCIDENTS, 0)
    incident_ratio = incident_nulls / max(len(df), 1)
    policy: dict[str, Any] = {
        "incident_null_count": incident_nulls,
        "incident_null_ratio": round(incident_ratio, 4),
        "incident_fill_allowed": incident_ratio <= INCIDENT_NULL_FILL_MAX_RATIO,
    }
    if incident_nulls and not policy["incident_fill_allowed"]:
        findings.append(
            ValidationFinding(
                code="incident_null_exceeds_fill_threshold",
                message=(
                    f"{incident_nulls} null Incident_Reports exceed fill threshold "
                    f"({INCIDENT_NULL_FILL_MAX_RATIO:.0%})"
                ),
                severity=ValidationSeverity.ERROR,
                column=COL_INCIDENTS,
            )
        )
    elif incident_nulls:
        findings.append(
            ValidationFinding(
                code="incident_null_fill_eligible",
                message=(
                    f"{incident_nulls} null Incident_Reports may be filled with 0 at import "
                    f"(ratio {incident_ratio:.2%} <= {INCIDENT_NULL_FILL_MAX_RATIO:.0%})"
                ),
                severity=ValidationSeverity.INFO,
                column=COL_INCIDENTS,
            )
        )

    for col in (COL_DATE, COL_AREA, COL_ROAD):
        n = null_stats.get(col, 0)
        if n:
            findings.append(
                ValidationFinding(
                    code="required_dimension_null",
                    message=f"{n} null value(s) in '{col}'",
                    severity=ValidationSeverity.CRITICAL,
                    column=col,
                )
            )

    return {"null_counts": null_stats, "incident_policy": policy}, findings


def validate_raw_null_policy_aqi(df: pd.DataFrame) -> tuple[dict[str, Any], list[ValidationFinding]]:
    """Reject critical atmospheric nulls; never interpolate PM2.5 (report only)."""
    findings: list[ValidationFinding] = []
    null_stats = collect_raw_null_stats(df, AQI_RAW_REQUIRED_COLUMNS)
    atmospheric = [c for c in AQI_RAW_REQUIRED_COLUMNS if c != COL_DATE]

    for col in atmospheric:
        n = null_stats.get(col, 0)
        if n:
            findings.append(
                ValidationFinding(
                    code="critical_atmospheric_null",
                    message=f"{n} null value(s) in critical atmospheric field '{col}'",
                    severity=ValidationSeverity.ERROR,
                    column=col,
                )
            )

    if null_stats.get(COL_DATE, 0):
        findings.append(
            ValidationFinding(
                code="required_dimension_null",
                message=f"{null_stats[COL_DATE]} null value(s) in '{COL_DATE}'",
                severity=ValidationSeverity.CRITICAL,
                column=COL_DATE,
            )
        )

    return {
        "null_counts": null_stats,
        "pm25_interpolation": "forbidden",
    }, findings


def validate_raw_semantic_ranges(
    df: pd.DataFrame,
    ranges: dict[str, tuple[float, float]],
) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    if df.empty:
        return findings
    for col, (lo, hi) in ranges.items():
        if col not in df.columns:
            continue
        series = pd.to_numeric(df[col], errors="coerce")
        out_of_range = series.notna() & ((series < lo) | (series > hi))
        count = int(out_of_range.sum())
        if count:
            findings.append(
                ValidationFinding(
                    code="semantic_range_violation",
                    message=f"{count} value(s) in '{col}' outside [{lo}, {hi}]",
                    severity=ValidationSeverity.ERROR,
                    column=col,
                )
            )
    return findings


def validate_raw_traffic_dataframe(
    df: pd.DataFrame,
    *,
    source_path: Path | str | None = None,
    schema_version: str = DATA_SCHEMA_VERSION,
) -> RawValidationReport:
    report = RawValidationReport(dataset="traffic")
    if source_path:
        report.source_metadata = hash_source_file(source_path)

    finding = validate_schema_version(schema_version)
    if finding:
        report.add(finding)

    for f in validate_raw_required_columns(df, TRAFFIC_RAW_REQUIRED_COLUMNS, "traffic"):
        report.add(f)
    if report.has_blocking_findings:
        return report

    dup_count, dup_finding = validate_raw_duplicates(df, TRAFFIC_DUPLICATE_KEY)
    report.duplicate_count = dup_count
    if dup_finding:
        report.add(dup_finding)

    null_meta, null_findings = validate_raw_null_policy_traffic(df)
    report.null_stats = null_meta
    for f in null_findings:
        report.add(f)

    for col, allowed in TRAFFIC_RAW_CATEGORY_COLUMNS.items():
        alias_map = WEATHER_CATEGORY_ALIASES if col == COL_WEATHER else ROADWORK_CATEGORY_ALIASES
        for f in validate_raw_categories(df, col, allowed, alias_map):
            report.add(f)

    for f in validate_raw_semantic_ranges(df, TRAFFIC_SEMANTIC_RANGES):
        report.add(f)

    return report


def validate_raw_aqi_dataframe(
    df: pd.DataFrame,
    *,
    source_path: Path | str | None = None,
    schema_version: str = DATA_SCHEMA_VERSION,
) -> RawValidationReport:
    report = RawValidationReport(dataset="aqi")
    if source_path:
        report.source_metadata = hash_source_file(source_path)

    finding = validate_schema_version(schema_version)
    if finding:
        report.add(finding)

    for f in validate_raw_required_columns(df, AQI_RAW_REQUIRED_COLUMNS, "aqi"):
        report.add(f)
    if report.has_blocking_findings:
        return report

    dup_count, dup_finding = validate_raw_duplicates(df, AQI_DUPLICATE_KEY)
    report.duplicate_count = dup_count
    if dup_finding:
        report.add(dup_finding)

    null_meta, null_findings = validate_raw_null_policy_aqi(df)
    report.null_stats = null_meta
    for f in null_findings:
        report.add(f)

    for f in validate_raw_semantic_ranges(df, AQI_SEMANTIC_RANGES):
        report.add(f)

    return report


# ---------------------------------------------------------------------------
# Processed parquet validation (Phase 3) — cleaned/derived data only
# ---------------------------------------------------------------------------


TRAFFIC_CHART_COLUMNS = [
    COL_DATE,
    COL_AREA,
    COL_ROAD,
    COL_CONGESTION,
    COL_CAPACITY,
    COL_SPEED,
    COL_WEATHER,
    COL_ROADWORK,
]

AQI_CHART_COLUMNS = [
    COL_DATE,
    COL_PM25,
    COL_AQI_CATEGORY,
    COL_SEASON,
    COL_SLP,
    COL_VV,
    COL_V,
    COL_TM,
]


@dataclass
class ProcessedValidationReport:
    dataset: str
    findings: list[ValidationFinding] = field(default_factory=list)

    def add(self, finding: ValidationFinding) -> None:
        self.findings.append(finding)

    @property
    def severity_counts(self) -> dict[str, int]:
        counts = {s.value: 0 for s in ValidationSeverity}
        for f in self.findings:
            counts[f.severity.value] = counts.get(f.severity.value, 0) + 1
        return counts

    @property
    def has_blocking_findings(self) -> bool:
        return any(
            f.severity in (ValidationSeverity.CRITICAL, ValidationSeverity.ERROR)
            for f in self.findings
        )

    @property
    def ok(self) -> bool:
        return not self.has_blocking_findings

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset": self.dataset,
            "findings": [f.to_dict() for f in self.findings],
            "severity_counts": self.severity_counts,
            "has_blocking_findings": self.has_blocking_findings,
            "ok": self.ok,
        }


def validate_processed_traffic_dataframe(df: pd.DataFrame) -> ProcessedValidationReport:
    """Validate cleaned traffic parquet: derived columns, types, chart readiness."""
    report = ProcessedValidationReport(dataset="traffic")
    if df.empty:
        report.add(
            ValidationFinding(
                code="empty_processed",
                message="Processed traffic dataframe is empty",
                severity=ValidationSeverity.CRITICAL,
            )
        )
        return report

    schema = validate_traffic_schema(df)
    if not schema.ok:
        report.add(
            ValidationFinding(
                code="processed_schema",
                message=schema.message,
                severity=ValidationSeverity.ERROR,
            )
        )

    for col in TRAFFIC_DERIVED_COLUMNS:
        if col not in df.columns:
            report.add(
                ValidationFinding(
                    code="missing_derived_column",
                    message=f"Missing derived column '{col}'",
                    severity=ValidationSeverity.ERROR,
                    column=col,
                )
            )

    if "at_max_capacity" in df.columns and df["at_max_capacity"].dtype != bool:
        report.add(
            ValidationFinding(
                code="derived_type_mismatch",
                message="Column 'at_max_capacity' must be boolean",
                severity=ValidationSeverity.ERROR,
                column="at_max_capacity",
            )
        )

    if len(df) < MIN_PROCESSED_TRAFFIC_ROWS:
        report.add(
            ValidationFinding(
                code="insufficient_rows",
                message=f"Processed traffic has {len(df)} rows (minimum {MIN_PROCESSED_TRAFFIC_ROWS})",
                severity=ValidationSeverity.ERROR,
            )
        )

    for col in TRAFFIC_CHART_COLUMNS:
        if col not in df.columns:
            report.add(
                ValidationFinding(
                    code="chart_column_missing",
                    message=f"Chart compatibility column '{col}' missing",
                    severity=ValidationSeverity.ERROR,
                    column=col,
                )
            )

    if COL_DATE in df.columns and df[COL_DATE].isna().any():
        report.add(
            ValidationFinding(
                code="invalid_dates",
                message="Processed traffic contains null dates",
                severity=ValidationSeverity.ERROR,
                column=COL_DATE,
            )
        )

    return report


def validate_processed_aqi_dataframe(df: pd.DataFrame) -> ProcessedValidationReport:
    """Validate cleaned AQI parquet including rolling window and category fields."""
    report = ProcessedValidationReport(dataset="aqi")
    if df.empty:
        report.add(
            ValidationFinding(
                code="empty_processed",
                message="Processed AQI dataframe is empty",
                severity=ValidationSeverity.CRITICAL,
            )
        )
        return report

    schema = validate_aqi_schema(df)
    if not schema.ok:
        report.add(
            ValidationFinding(
                code="processed_schema",
                message=schema.message,
                severity=ValidationSeverity.ERROR,
            )
        )

    for col in AQI_DERIVED_COLUMNS:
        if col not in df.columns:
            report.add(
                ValidationFinding(
                    code="missing_derived_column",
                    message=f"Missing derived column '{col}'",
                    severity=ValidationSeverity.ERROR,
                    column=col,
                )
            )

    if "rolling_7d_pm25" in df.columns:
        roll = df["rolling_7d_pm25"]
        if roll.isna().all():
            report.add(
                ValidationFinding(
                    code="rolling_not_ready",
                    message="rolling_7d_pm25 is entirely null",
                    severity=ValidationSeverity.ERROR,
                    column="rolling_7d_pm25",
                )
            )
        elif roll.notna().sum() < 2:
            report.add(
                ValidationFinding(
                    code="rolling_not_ready",
                    message="rolling_7d_pm25 has insufficient populated values",
                    severity=ValidationSeverity.WARNING,
                    column="rolling_7d_pm25",
                )
            )

    for band_col in ("slp_band", "vv_band", "wind_band"):
        if band_col in df.columns and df[band_col].isna().all():
            report.add(
                ValidationFinding(
                    code="band_column_empty",
                    message=f"Derived band column '{band_col}' is entirely null",
                    severity=ValidationSeverity.ERROR,
                    column=band_col,
                )
            )

    if len(df) < MIN_PROCESSED_AQI_ROWS:
        report.add(
            ValidationFinding(
                code="insufficient_rows",
                message=f"Processed AQI has {len(df)} rows (minimum {MIN_PROCESSED_AQI_ROWS})",
                severity=ValidationSeverity.ERROR,
            )
        )

    for col in AQI_CHART_COLUMNS:
        if col not in df.columns:
            report.add(
                ValidationFinding(
                    code="chart_column_missing",
                    message=f"Chart compatibility column '{col}' missing",
                    severity=ValidationSeverity.ERROR,
                    column=col,
                )
            )

    if COL_AQI_CATEGORY in df.columns:
        invalid_cats = ~df[COL_AQI_CATEGORY].isin(
            ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]
        )
        if invalid_cats.any():
            report.add(
                ValidationFinding(
                    code="invalid_aqi_category",
                    message="Processed AQI contains invalid aqi_category labels",
                    severity=ValidationSeverity.ERROR,
                    column=COL_AQI_CATEGORY,
                )
            )

    return report


def assert_processed_traffic(df: pd.DataFrame) -> None:
    report = validate_processed_traffic_dataframe(df)
    if not report.ok:
        first = report.findings[0].message if report.findings else "Processed traffic validation failed"
        raise DataValidationError(first)


def assert_processed_aqi(df: pd.DataFrame) -> None:
    report = validate_processed_aqi_dataframe(df)
    if not report.ok:
        first = report.findings[0].message if report.findings else "Processed AQI validation failed"
        raise DataValidationError(first)
