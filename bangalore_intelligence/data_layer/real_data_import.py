"""
Canonical real-data normalization and governed import pipeline.

Phase 1–2: read/normalize sources, raw validation, dry-run profiles.
Phase 3: write canonical raw + processed parquet with temp staging and atomic promotion.
Phase 4: import locks, snapshots, profile/history persistence, timings, freshness metadata.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from config.data_config import (
    AQI_DERIVED_COLUMNS,
    AQI_CANONICAL_RAW_PARQUET,
    AQI_CANONICAL_RAW_TMP,
    AQI_CLEAN_BACKUP,
    AQI_CLEAN_PATH,
    AQI_CLEAN_TMP,
    AQI_PM25_SOURCE_ALIASES,
    AQI_RAW_NUMERIC_COLUMNS,
    AQI_SOURCE_COLUMN_ALIASES,
    COL_AREA,
    COL_CAPACITY,
    COL_CONGESTION,
    COL_DATE,
    COL_ENVIRONMENTAL_IMPACT_SOURCE,
    COL_H,
    COL_INCIDENTS,
    COL_PARKING_USAGE,
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
    COL_TRAVEL_TIME_INDEX,
    COL_V,
    COL_VM,
    COL_VV,
    COL_WEATHER,
    DATA_SCHEMA_VERSION,
    DATA_TEMP_DIR,
    TRAFFIC_CANONICAL_RAW_PARQUET,
    TRAFFIC_CANONICAL_RAW_TMP,
    TRAFFIC_CLEAN_BACKUP,
    TRAFFIC_CLEAN_PATH,
    TRAFFIC_CLEAN_TMP,
    TRAFFIC_DERIVED_COLUMNS,
    TRAFFIC_RAW_NUMERIC_COLUMNS,
    TRAFFIC_SOURCE_COLUMN_ALIASES,
)
from data_layer.cleaners import clean_aqi, clean_traffic
from data_layer.traffic_duplicate_governance import govern_traffic_duplicate_keys
from data_layer.import_governance import (
    ImportLockError,
    iso_timestamp,
    stamp_for_filename,
    archive_canonical_raw_snapshots,
    import_lock,
    write_import_profiles,
)
from utils.validators import (
    RawValidationReport,
    validate_processed_aqi_dataframe,
    validate_processed_traffic_dataframe,
    validate_raw_aqi_dataframe,
    validate_raw_traffic_dataframe,
)

TRAFFIC_CANONICAL_BASE_COLUMNS = [
    COL_DATE,
    COL_AREA,
    COL_ROAD,
    COL_CONGESTION,
    COL_SPEED,
    COL_INCIDENTS,
    COL_CAPACITY,
    COL_PEDESTRIAN,
    COL_PT_USAGE,
    COL_SIGNAL,
    COL_TRAFFIC_VOL,
    COL_WEATHER,
    COL_ROADWORK,
]

TRAFFIC_CANONICAL_OPTIONAL_COLUMNS = [
    COL_TRAVEL_TIME_INDEX,
    COL_ENVIRONMENTAL_IMPACT_SOURCE,
    COL_PARKING_USAGE,
]

AQI_CANONICAL_COLUMNS = [
    COL_DATE,
    COL_PM25,
    COL_T,
    COL_TM,
    COL_TM_MAX,
    COL_SLP,
    COL_H,
    COL_VV,
    COL_V,
    COL_VM,
]


def _normalize_header_key(name: str) -> str:
    return " ".join(str(name).strip().lower().split())


def _rename_columns_from_aliases(
    df: pd.DataFrame,
    alias_map: dict[str, str],
    *,
    exact_headers: dict[str, str] | None = None,
) -> pd.DataFrame:
    rename: dict[str, str] = {}
    exact = exact_headers or {}
    for col in df.columns:
        stripped = str(col).strip()
        if stripped in exact:
            rename[col] = exact[stripped]
            continue
        key = _normalize_header_key(col)
        if key in alias_map:
            rename[col] = alias_map[key]
        elif key.replace(" ", "_") in alias_map:
            rename[col] = alias_map[key.replace(" ", "_")]
    if not rename:
        return df.copy()
    out = df.rename(columns=rename)
    return out.loc[:, ~out.columns.duplicated(keep="first")]


def _resolve_pm25_source_column(df: pd.DataFrame) -> str | None:
    for alias in AQI_PM25_SOURCE_ALIASES:
        if alias in df.columns:
            return alias
    for col in df.columns:
        if _normalize_header_key(col) in {_normalize_header_key(a) for a in AQI_PM25_SOURCE_ALIASES}:
            return col
    return None


def preclean_aqi_source(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """
    Drop fully blank rows and rows missing PM2.5 before renaming/coercion/date work.
    Operates on source headers (e.g. 'PM 2.5').
    """
    stats = {"rows_read": len(df), "blank_rows_dropped": 0, "missing_pm25_dropped": 0}
    if df.empty:
        return df.copy(), stats

    work = df.copy()
    work.columns = [str(c).strip() for c in work.columns]

    blank_mask = work.apply(
        lambda row: row.isna().all()
        or all(str(v).strip() == "" for v in row if pd.notna(v)),
        axis=1,
    )
    blank_dropped = int(blank_mask.sum())
    if blank_dropped:
        work = work.loc[~blank_mask]
    stats["blank_rows_dropped"] = blank_dropped

    pm_col = _resolve_pm25_source_column(work)
    if pm_col is None:
        stats["missing_pm25_dropped"] = len(work)
        return work.iloc[0:0].copy(), stats

    pm_series = work[pm_col]
    missing_pm = pm_series.isna() | (pm_series.astype(str).str.strip() == "")
    missing_count = int(missing_pm.sum())
    if missing_count:
        work = work.loc[~missing_pm]
    stats["missing_pm25_dropped"] = missing_count

    return work.reset_index(drop=True), stats


def coerce_numeric_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in columns:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def normalize_traffic_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Map source traffic headers to canonical names; preserve optional extra fields."""
    renamed = _rename_columns_from_aliases(df, TRAFFIC_SOURCE_COLUMN_ALIASES)
    out = coerce_numeric_columns(renamed, TRAFFIC_RAW_NUMERIC_COLUMNS)
    if COL_DATE in out.columns:
        out[COL_DATE] = pd.to_datetime(out[COL_DATE], errors="coerce")
    present_base = [c for c in TRAFFIC_CANONICAL_BASE_COLUMNS if c in out.columns]
    present_optional = [c for c in TRAFFIC_CANONICAL_OPTIONAL_COLUMNS if c in out.columns]
    return out[present_base + present_optional].copy()


def normalize_aqi_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Pre-clean source rows, rename headers, coerce numerics, parse dates."""
    precleaned, stats = preclean_aqi_source(df)
    if precleaned.empty:
        return precleaned, stats

    aqi_exact = {
        "Tm": COL_TM,
        "TM": COL_TM_MAX,
        "T": COL_T,
        "H": COL_H,
        "VV": COL_VV,
        "V": COL_V,
        "VM": COL_VM,
        "SLP": COL_SLP,
        "Date": COL_DATE,
        "PM 2.5": COL_PM25,
        "PM_2_5": COL_PM25,
    }
    renamed = _rename_columns_from_aliases(
        precleaned, AQI_SOURCE_COLUMN_ALIASES, exact_headers=aqi_exact
    )

    out = coerce_numeric_columns(renamed, AQI_RAW_NUMERIC_COLUMNS)
    if COL_DATE in out.columns:
        out[COL_DATE] = pd.to_datetime(out[COL_DATE], errors="coerce")
    present = [c for c in AQI_CANONICAL_COLUMNS if c in out.columns]
    return out[present].copy(), stats


def read_traffic_source(path: Path | str) -> pd.DataFrame:
    return pd.read_csv(path)


def read_aqi_source(path: Path | str) -> pd.DataFrame:
    return pd.read_csv(path)


def _dataset_summary(df: pd.DataFrame, dataset: str) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "dataset": dataset,
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "columns": list(df.columns),
    }
    if COL_DATE in df.columns and not df.empty:
        dates = pd.to_datetime(df[COL_DATE], errors="coerce").dropna()
        if not dates.empty:
            summary["date_min"] = str(dates.min().date())
            summary["date_max"] = str(dates.max().date())
    if dataset == "traffic":
        for opt in TRAFFIC_CANONICAL_OPTIONAL_COLUMNS:
            summary[f"has_{opt}"] = opt in df.columns
    if dataset == "aqi" and COL_PM25 in df.columns:
        summary["pm25_non_null"] = int(df[COL_PM25].notna().sum())
    return summary


@dataclass
class ImportProfile:
    """In-memory import profile scaffold (Phase 1 — no persistence)."""

    schema_version: str = DATA_SCHEMA_VERSION
    mode: str = "dry_run"
    traffic: dict[str, Any] = field(default_factory=dict)
    aqi: dict[str, Any] = field(default_factory=dict)
    aqi_preclean: dict[str, int] = field(default_factory=dict)
    traffic_duplicate_governance: dict[str, Any] = field(default_factory=dict)
    traffic_source_path: str = ""
    aqi_source_path: str = ""
    raw_validation: dict[str, Any] = field(default_factory=dict)
    processed_validation: dict[str, Any] = field(default_factory=dict)
    artifacts_written: list[str] = field(default_factory=list)
    error: str = ""
    success: bool = False
    import_timestamp: str = ""
    timings: dict[str, float] = field(default_factory=dict)
    source_metadata: dict[str, Any] = field(default_factory=dict)
    processed_metadata: dict[str, Any] = field(default_factory=dict)
    freshness_metadata: dict[str, Any] = field(default_factory=dict)
    governance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "mode": self.mode,
            "success": self.success,
            "import_timestamp": self.import_timestamp,
            "traffic": self.traffic,
            "aqi": self.aqi,
            "aqi_preclean": self.aqi_preclean,
            "traffic_duplicate_governance": self.traffic_duplicate_governance,
            "traffic_source_path": self.traffic_source_path,
            "aqi_source_path": self.aqi_source_path,
            "source_metadata": self.source_metadata,
            "raw_validation": self.raw_validation,
            "processed_validation": self.processed_validation,
            "timings": self.timings,
            "processed_metadata": self.processed_metadata,
            "freshness_metadata": self.freshness_metadata,
            "governance": self.governance,
            "artifacts_written": self.artifacts_written,
            "error": self.error,
        }


@dataclass
class DryRunResult:
    traffic: pd.DataFrame
    aqi: pd.DataFrame
    profile: ImportProfile


@dataclass
class PreparedImport:
    traffic: pd.DataFrame
    aqi: pd.DataFrame
    preclean_stats: dict[str, int]
    traffic_duplicate_stats: dict[str, Any]
    traffic_val: RawValidationReport
    aqi_val: RawValidationReport
    traffic_source_path: str
    aqi_source_path: str


@dataclass
class ImportResult:
    success: bool
    traffic: pd.DataFrame
    aqi: pd.DataFrame
    profile: ImportProfile


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _unlink_if_exists(path: Path) -> None:
    if path.exists():
        path.unlink()


def _backup_active(active: Path, backup: Path) -> None:
    _unlink_if_exists(backup)
    if active.exists() and active.stat().st_size > 0:
        _ensure_parent(backup)
        active.replace(backup)


def _promote_temp(temp: Path, active: Path, backup: Path) -> None:
    """Replace active file with validated temp; keep prior active as backup."""
    _ensure_parent(active)
    _backup_active(active, backup)
    if temp.exists():
        temp.replace(active)


def _write_parquet(df: pd.DataFrame, path: Path) -> None:
    _ensure_parent(path)
    df.to_parquet(path, index=False)


def _read_parquet_if_usable(path: Path) -> pd.DataFrame | None:
    if path.exists() and path.stat().st_size > 100:
        return pd.read_parquet(path)
    return None


def prepare_import_data(
    traffic_source: Path | str,
    aqi_source: Path | str,
    *,
    timings: dict[str, float] | None = None,
) -> PreparedImport:
    """Read, normalize, and raw-validate both datasets (no file writes)."""
    norm_start = time.perf_counter()
    traffic_raw = read_traffic_source(traffic_source)
    aqi_raw = read_aqi_source(aqi_source)

    traffic_norm = normalize_traffic_dataframe(traffic_raw)
    traffic_norm, traffic_duplicate_stats = govern_traffic_duplicate_keys(traffic_norm)
    aqi_norm, preclean_stats = normalize_aqi_dataframe(aqi_raw)
    if timings is not None:
        timings["normalization_time"] = round(time.perf_counter() - norm_start, 4)

    val_start = time.perf_counter()
    traffic_val = validate_raw_traffic_dataframe(
        traffic_norm, source_path=traffic_source, schema_version=DATA_SCHEMA_VERSION
    )
    aqi_val = validate_raw_aqi_dataframe(
        aqi_norm, source_path=aqi_source, schema_version=DATA_SCHEMA_VERSION
    )
    if timings is not None:
        timings["validation_time"] = round(
            timings.get("validation_time", 0.0) + (time.perf_counter() - val_start),
            4,
        )

    return PreparedImport(
        traffic=traffic_norm,
        aqi=aqi_norm,
        preclean_stats=preclean_stats,
        traffic_duplicate_stats=traffic_duplicate_stats,
        traffic_val=traffic_val,
        aqi_val=aqi_val,
        traffic_source_path=str(Path(traffic_source).resolve()),
        aqi_source_path=str(Path(aqi_source).resolve()),
    )


def _build_profile_from_prepared(
    prepared: PreparedImport,
    *,
    mode: str,
    processed_validation: dict[str, Any] | None = None,
    artifacts_written: list[str] | None = None,
    error: str = "",
) -> ImportProfile:
    return ImportProfile(
        mode=mode,
        traffic=_dataset_summary(prepared.traffic, "traffic"),
        aqi=_dataset_summary(prepared.aqi, "aqi"),
        aqi_preclean=prepared.preclean_stats,
        traffic_duplicate_governance=prepared.traffic_duplicate_stats,
        traffic_source_path=prepared.traffic_source_path,
        aqi_source_path=prepared.aqi_source_path,
        raw_validation={
            "traffic": prepared.traffic_val.to_dict(),
            "aqi": prepared.aqi_val.to_dict(),
            "severity_totals": _merge_severity_counts(prepared.traffic_val, prepared.aqi_val),
        },
        processed_validation=processed_validation or {},
        artifacts_written=artifacts_written or [],
        error=error,
    )


def _raw_validation_blocks(prepared: PreparedImport) -> bool:
    return prepared.traffic_val.has_blocking_findings or prepared.aqi_val.has_blocking_findings


def _source_metadata_from_prepared(prepared: PreparedImport) -> dict[str, Any]:
    return {
        "traffic": prepared.traffic_val.source_metadata,
        "aqi": prepared.aqi_val.source_metadata,
    }


def _processed_file_metadata(
    df: pd.DataFrame,
    path: Path,
    derived_columns: list[str],
) -> dict[str, Any]:
    return {
        "row_count": int(len(df)),
        "derived_column_count": int(sum(1 for col in derived_columns if col in df.columns)),
        "parquet_size_bytes": int(path.stat().st_size) if path.exists() else 0,
        "generated_at": iso_timestamp(),
    }


def _freshness_for_dataset(
    *,
    source_date_max: str | None,
    processed_df: pd.DataFrame,
    reference: datetime | None = None,
) -> dict[str, Any]:
    ref = reference or datetime.now(timezone.utc)
    processed_dates = (
        pd.to_datetime(processed_df[COL_DATE], errors="coerce").dropna()
        if COL_DATE in processed_df.columns and not processed_df.empty
        else pd.Series(dtype="datetime64[ns]")
    )
    processed_last = (
        str(processed_dates.max().date()) if not processed_dates.empty else None
    )
    days_since_processed: int | None = None
    if processed_last:
        days_since_processed = (ref.date() - pd.Timestamp(processed_last).date()).days

    return {
        "source_last_date": source_date_max,
        "processed_last_date": processed_last,
        "days_since_latest_record": days_since_processed,
    }


def _finalize_successful_import(
    profile: ImportProfile,
    prepared: PreparedImport,
    traffic_clean: pd.DataFrame,
    aqi_clean: pd.DataFrame,
    *,
    timings: dict[str, float],
    lock_payload: dict[str, Any],
    import_stamp: str,
) -> ImportProfile:
    profile.success = True
    profile.import_timestamp = iso_timestamp()
    profile.source_metadata = _source_metadata_from_prepared(prepared)
    profile.timings = timings
    profile.processed_metadata = {
        "traffic": _processed_file_metadata(
            traffic_clean, TRAFFIC_CLEAN_PATH, TRAFFIC_DERIVED_COLUMNS
        ),
        "aqi": _processed_file_metadata(aqi_clean, AQI_CLEAN_PATH, AQI_DERIVED_COLUMNS),
    }
    profile.freshness_metadata = {
        "traffic": _freshness_for_dataset(
            source_date_max=profile.traffic.get("date_max"),
            processed_df=traffic_clean,
        ),
        "aqi": _freshness_for_dataset(
            source_date_max=profile.aqi.get("date_max"),
            processed_df=aqi_clean,
        ),
    }
    snapshots = archive_canonical_raw_snapshots(
        TRAFFIC_CANONICAL_RAW_PARQUET,
        AQI_CANONICAL_RAW_PARQUET,
        stamp=import_stamp,
    )
    from config.data_config import IMPORT_HISTORY_DIR, IMPORT_PROFILE_PATH

    history_path = IMPORT_HISTORY_DIR / f"import_{import_stamp}.json"
    profile.governance = {
        "lock": lock_payload,
        "snapshots": snapshots,
        "profile_path": str(IMPORT_PROFILE_PATH.resolve()),
        "history_path": str(history_path.resolve()),
    }
    write_import_profiles(profile.to_dict(), stamp=import_stamp)
    profile.artifacts_written.extend(
        [
            profile.governance["profile_path"],
            profile.governance["history_path"],
            snapshots["traffic_snapshot"],
            snapshots["aqi_snapshot"],
        ]
    )
    return profile


def run_dry_run_import(
    traffic_source: Path | str,
    aqi_source: Path | str,
) -> DryRunResult:
    """
    Read and normalize both datasets in memory. Does not write parquet, metadata, or profiles to disk.
    """
    prepared = prepare_import_data(traffic_source, aqi_source)
    profile = _build_profile_from_prepared(prepared, mode="dry_run")
    return DryRunResult(traffic=prepared.traffic, aqi=prepared.aqi, profile=profile)


def run_real_import(
    traffic_source: Path | str,
    aqi_source: Path | str,
) -> ImportResult:
    """
    Governed import: lock -> raw validate -> canonical raw -> clean -> processed parquet.
    On success: snapshots, latest profile, and history entry. Failed imports write no governance artifacts.
    """
    try:
        with import_lock() as lock_payload:
            return _run_real_import_locked(
                traffic_source, aqi_source, lock_payload=lock_payload
            )
    except ImportLockError as exc:
        profile = ImportProfile(mode="apply", error=str(exc))
        return ImportResult(
            success=False,
            traffic=pd.DataFrame(),
            aqi=pd.DataFrame(),
            profile=profile,
        )


def _run_real_import_locked(
    traffic_source: Path | str,
    aqi_source: Path | str,
    *,
    lock_payload: dict[str, Any],
) -> ImportResult:
    total_start = time.perf_counter()
    timings: dict[str, float] = {}
    import_stamp = stamp_for_filename()

    prepared = prepare_import_data(traffic_source, aqi_source, timings=timings)
    if _raw_validation_blocks(prepared):
        profile = _build_profile_from_prepared(
            prepared,
            mode="apply",
            error="Raw validation has blocking findings; import aborted before writes.",
        )
        profile.timings = {
            **timings,
            "total_import_time": round(time.perf_counter() - total_start, 4),
        }
        profile.source_metadata = _source_metadata_from_prepared(prepared)
        return ImportResult(
            success=False,
            traffic=prepared.traffic,
            aqi=prepared.aqi,
            profile=profile,
        )

    DATA_TEMP_DIR.mkdir(parents=True, exist_ok=True)
    artifacts: list[str] = []

    try:
        write_start = time.perf_counter()
        _write_parquet(prepared.traffic, TRAFFIC_CANONICAL_RAW_TMP)
        _write_parquet(prepared.aqi, AQI_CANONICAL_RAW_TMP)

        _promote_temp(
            TRAFFIC_CANONICAL_RAW_TMP,
            TRAFFIC_CANONICAL_RAW_PARQUET,
            DATA_TEMP_DIR / "traffic_canonical_raw.bak",
        )
        _promote_temp(
            AQI_CANONICAL_RAW_TMP,
            AQI_CANONICAL_RAW_PARQUET,
            DATA_TEMP_DIR / "aqi_canonical_raw.bak",
        )
        artifacts.extend([str(TRAFFIC_CANONICAL_RAW_PARQUET), str(AQI_CANONICAL_RAW_PARQUET)])

        clean_start = time.perf_counter()
        traffic_clean = clean_traffic(prepared.traffic)
        aqi_clean = clean_aqi(prepared.aqi)
        timings["cleaning_time"] = round(time.perf_counter() - clean_start, 4)

        proc_val_start = time.perf_counter()
        traffic_proc_val = validate_processed_traffic_dataframe(traffic_clean)
        aqi_proc_val = validate_processed_aqi_dataframe(aqi_clean)
        timings["validation_time"] = round(
            timings.get("validation_time", 0.0) + (time.perf_counter() - proc_val_start),
            4,
        )
        proc_validation = {
            "traffic": traffic_proc_val.to_dict(),
            "aqi": aqi_proc_val.to_dict(),
            "severity_totals": _merge_severity_counts(traffic_proc_val, aqi_proc_val),
        }

        if traffic_proc_val.has_blocking_findings or aqi_proc_val.has_blocking_findings:
            profile = _build_profile_from_prepared(
                prepared,
                mode="apply",
                processed_validation=proc_validation,
                artifacts_written=artifacts,
                error="Processed validation failed; active processed parquet unchanged.",
            )
            profile.timings = {
                **timings,
                "total_import_time": round(time.perf_counter() - total_start, 4),
            }
            profile.source_metadata = _source_metadata_from_prepared(prepared)
            return ImportResult(
                success=False,
                traffic=traffic_clean,
                aqi=aqi_clean,
                profile=profile,
            )

        _write_parquet(traffic_clean, TRAFFIC_CLEAN_TMP)
        _write_parquet(aqi_clean, AQI_CLEAN_TMP)

        tmp_traffic = _read_parquet_if_usable(TRAFFIC_CLEAN_TMP)
        tmp_aqi = _read_parquet_if_usable(AQI_CLEAN_TMP)
        if tmp_traffic is None or tmp_aqi is None:
            raise RuntimeError("Processed temp parquet missing after write")

        timings["parquet_write_time"] = round(time.perf_counter() - write_start, 4)

        reread_start = time.perf_counter()
        reread_traffic_val = validate_processed_traffic_dataframe(tmp_traffic)
        reread_aqi_val = validate_processed_aqi_dataframe(tmp_aqi)
        timings["validation_time"] = round(
            timings.get("validation_time", 0.0) + (time.perf_counter() - reread_start),
            4,
        )

        if reread_traffic_val.has_blocking_findings or reread_aqi_val.has_blocking_findings:
            _unlink_if_exists(TRAFFIC_CLEAN_TMP)
            _unlink_if_exists(AQI_CLEAN_TMP)
            profile = _build_profile_from_prepared(
                prepared,
                mode="apply",
                processed_validation={
                    "traffic": reread_traffic_val.to_dict(),
                    "aqi": reread_aqi_val.to_dict(),
                    "severity_totals": _merge_severity_counts(reread_traffic_val, reread_aqi_val),
                },
                artifacts_written=artifacts,
                error="Processed temp parquet failed re-read validation.",
            )
            profile.timings = {
                **timings,
                "total_import_time": round(time.perf_counter() - total_start, 4),
            }
            profile.source_metadata = _source_metadata_from_prepared(prepared)
            return ImportResult(success=False, traffic=traffic_clean, aqi=aqi_clean, profile=profile)

        _promote_temp(TRAFFIC_CLEAN_TMP, TRAFFIC_CLEAN_PATH, TRAFFIC_CLEAN_BACKUP)
        _promote_temp(AQI_CLEAN_TMP, AQI_CLEAN_PATH, AQI_CLEAN_BACKUP)
        artifacts.extend([str(TRAFFIC_CLEAN_PATH), str(AQI_CLEAN_PATH)])

        profile = _build_profile_from_prepared(
            prepared,
            mode="apply",
            processed_validation=proc_validation,
            artifacts_written=artifacts,
        )
        timings["total_import_time"] = round(time.perf_counter() - total_start, 4)
        profile = _finalize_successful_import(
            profile,
            prepared,
            traffic_clean,
            aqi_clean,
            timings=timings,
            lock_payload=lock_payload,
            import_stamp=import_stamp,
        )
        return ImportResult(
            success=True,
            traffic=traffic_clean,
            aqi=aqi_clean,
            profile=profile,
        )
    except Exception as exc:
        for tmp in (
            TRAFFIC_CANONICAL_RAW_TMP,
            AQI_CANONICAL_RAW_TMP,
            TRAFFIC_CLEAN_TMP,
            AQI_CLEAN_TMP,
        ):
            _unlink_if_exists(tmp)
        profile = _build_profile_from_prepared(
            prepared,
            mode="apply",
            artifacts_written=artifacts,
            error=f"Import failed: {exc}",
        )
        profile.timings = {
            **timings,
            "total_import_time": round(time.perf_counter() - total_start, 4),
        }
        profile.source_metadata = _source_metadata_from_prepared(prepared)
        return ImportResult(success=False, traffic=prepared.traffic, aqi=prepared.aqi, profile=profile)


def _merge_severity_counts(*reports) -> dict[str, int]:
    totals: dict[str, int] = {}
    for report in reports:
        for level, count in report.severity_counts.items():
            totals[level] = totals.get(level, 0) + count
    return totals


def _format_validation_block(
    lines: list[str],
    title: str,
    validation: dict[str, Any],
    *,
    show_findings: bool = True,
) -> None:
    if not validation:
        return
    totals = validation.get("severity_totals", {})
    lines.extend(["", title, f"  Severity totals: {totals}"])
    for dataset in ("traffic", "aqi"):
        block = validation.get(dataset, {})
        if not block:
            continue
        dup = block.get("duplicate_count")
        dup_text = f", duplicates={dup}" if dup is not None else ""
        lines.append(
            f"  {dataset}: ok={block.get('ok')}, findings={len(block.get('findings', []))}{dup_text}"
        )
        if block.get("has_blocking_findings"):
            lines.append("    BLOCKING findings present")
        if not show_findings:
            continue
        for finding in block.get("findings", []):
            severity = finding.get("severity", "")
            if severity not in ("warning", "error", "critical"):
                continue
            lines.append(
                f"    [{severity}] {finding.get('code')}: {finding.get('message')}"
            )


def format_import_summary(
    profile: ImportProfile,
    *,
    header: str,
    success: bool | None = None,
) -> str:
    """Structured CLI summary for dry-run and apply modes."""
    p = profile
    mode_line = f"Mode: {p.mode}"
    if p.mode == "dry_run":
        mode_line += " (no files written)"
    elif success is not None:
        mode_line += f" (success={success})"

    lines = [
        header,
        f"Schema version: {p.schema_version}",
        mode_line,
    ]
    if p.import_timestamp:
        lines.append(f"Import timestamp: {p.import_timestamp}")

    lines.extend(
        [
            "",
            "Traffic:",
            f"  Source: {p.traffic_source_path}",
            f"  Rows: {p.traffic.get('row_count', 0)}",
            f"  Columns: {p.traffic.get('column_count', 0)}",
        ]
    )
    if "date_min" in p.traffic:
        lines.append(f"  Date range: {p.traffic['date_min']} -> {p.traffic['date_max']}")
    for opt in TRAFFIC_CANONICAL_OPTIONAL_COLUMNS:
        key = f"has_{opt}"
        if key in p.traffic:
            lines.append(f"  {opt}: {'yes' if p.traffic[key] else 'no'}")

    lines.extend(
        [
            "",
            "AQI:",
            f"  Source: {p.aqi_source_path}",
            f"  Rows: {p.aqi.get('row_count', 0)}",
            f"  Columns: {p.aqi.get('column_count', 0)}",
        ]
    )
    if "date_min" in p.aqi:
        lines.append(f"  Date range: {p.aqi['date_min']} -> {p.aqi['date_max']}")
    if p.aqi_preclean:
        lines.extend(
            [
                "",
                "AQI pre-clean:",
                f"  Rows read: {p.aqi_preclean.get('rows_read', 0)}",
                f"  Blank rows dropped: {p.aqi_preclean.get('blank_rows_dropped', 0)}",
                f"  Missing PM2.5 dropped: {p.aqi_preclean.get('missing_pm25_dropped', 0)}",
            ]
        )

    tdg = p.traffic_duplicate_governance or {}
    if tdg:
        lines.extend(
            [
                "",
                "Traffic duplicate governance:",
                f"  Policy: {tdg.get('policy', '')}",
                f"  Rows before: {tdg.get('rows_before', 0)}",
                f"  Duplicate key rows before: {tdg.get('duplicate_key_rows_before', 0)}",
                f"  Partial groups aggregated: {tdg.get('partial_groups_aggregated', 0)}",
                f"  Rows collapsed: {tdg.get('rows_collapsed_by_aggregation', 0)}",
                f"  Exact duplicates removed: {tdg.get('exact_duplicates_removed', 0)}",
                f"  Rows after: {tdg.get('rows_after', 0)}",
            ]
        )

    if p.source_metadata:
        lines.extend(["", "Source metadata:"])
        for dataset in ("traffic", "aqi"):
            meta = p.source_metadata.get(dataset, {})
            if meta:
                lines.append(
                    f"  {dataset}: sha256={meta.get('sha256', '')[:12]}... "
                    f"size={meta.get('size_bytes', 0)} bytes"
                )

    _format_validation_block(lines, "Raw validation:", p.raw_validation or {})
    _format_validation_block(
        lines,
        "Processed validation:",
        p.processed_validation or {},
        show_findings=False,
    )

    if p.timings:
        lines.extend(["", "Timing (seconds):"])
        for key in (
            "normalization_time",
            "validation_time",
            "cleaning_time",
            "parquet_write_time",
            "total_import_time",
        ):
            if key in p.timings:
                lines.append(f"  {key}: {p.timings[key]}")

    if p.processed_metadata:
        lines.extend(["", "Processed metadata:"])
        for dataset in ("traffic", "aqi"):
            meta = p.processed_metadata.get(dataset, {})
            if meta:
                lines.append(
                    f"  {dataset}: rows={meta.get('row_count')}, "
                    f"derived_cols={meta.get('derived_column_count')}, "
                    f"size={meta.get('parquet_size_bytes')} bytes, "
                    f"generated_at={meta.get('generated_at')}"
                )

    if p.freshness_metadata:
        lines.extend(["", "Freshness:"])
        for dataset in ("traffic", "aqi"):
            fresh = p.freshness_metadata.get(dataset, {})
            if fresh:
                lines.append(
                    f"  {dataset}: source_last={fresh.get('source_last_date')}, "
                    f"processed_last={fresh.get('processed_last_date')}, "
                    f"days_since={fresh.get('days_since_latest_record')}"
                )

    if p.governance:
        lines.extend(["", "Governance:"])
        if p.governance.get("profile_path"):
            lines.append(f"  Latest profile: {p.governance['profile_path']}")
        if p.governance.get("history_path"):
            lines.append(f"  History profile: {p.governance['history_path']}")
        snapshots = p.governance.get("snapshots", {})
        if snapshots.get("traffic_snapshot"):
            lines.append(f"  Traffic snapshot: {snapshots['traffic_snapshot']}")
        if snapshots.get("aqi_snapshot"):
            lines.append(f"  AQI snapshot: {snapshots['aqi_snapshot']}")

    if p.artifacts_written:
        lines.extend(["", "Artifacts written:"])
        for path in p.artifacts_written:
            lines.append(f"  {path}")
    if p.error:
        lines.extend(["", f"Error: {p.error}"])
    return "\n".join(lines)


def format_dry_run_summary(result: DryRunResult) -> str:
    return format_import_summary(
        result.profile,
        header="=== Real Data Import (DRY RUN) ===",
    )


def format_apply_summary(result: ImportResult) -> str:
    header = (
        "=== Real Data Import (APPLY) ==="
        if result.success
        else "=== Real Data Import (APPLY FAILED) ==="
    )
    return format_import_summary(
        result.profile,
        header=header,
        success=result.success,
    )
