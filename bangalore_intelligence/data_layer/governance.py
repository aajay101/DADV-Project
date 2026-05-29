"""Runtime data governance, provenance, and source-integrity checks."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from config import data_config as cfg
from data_layer.cleaners import clean_aqi, clean_traffic
from utils.validators import DataValidationError


class RuntimeDataIntegrityError(DataValidationError):
    """Raised when governed runtime data cannot be trusted."""


class SyntheticDataDetectedError(RuntimeDataIntegrityError):
    """Raised when runtime would use generated/synthetic data."""


class MissingGovernedDatasetError(RuntimeDataIntegrityError):
    """Raised when required governed parquet artifacts are missing."""


class DatasetFingerprintMismatchError(RuntimeDataIntegrityError):
    """Raised when processed data does not match canonical provenance."""


@dataclass(frozen=True)
class DatasetPaths:
    canonical: Path
    processed: Path


def is_production_runtime() -> bool:
    env = os.getenv("BUIP_RUNTIME_ENV", cfg.RUNTIME_ENV).strip().lower()
    return env in {"prod", "production", ""}


def governed_manifest_path() -> Path:
    return cfg.DATA_METADATA_DIR / cfg.GOVERNED_MANIFEST_FILENAME


def dataset_paths(dataset: str) -> DatasetPaths:
    if dataset == "traffic":
        return DatasetPaths(cfg.TRAFFIC_CANONICAL_RAW_PARQUET, cfg.TRAFFIC_CLEAN_PATH)
    if dataset == "aqi":
        return DatasetPaths(cfg.AQI_CANONICAL_RAW_PARQUET, cfg.AQI_CLEAN_PATH)
    raise ValueError(f"Unknown dataset: {dataset}")


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def dataframe_schema_hash(df: pd.DataFrame) -> str:
    payload = json.dumps(
        [{"name": str(col), "dtype": str(dtype)} for col, dtype in df.dtypes.items()],
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _numeric_ranges(df: pd.DataFrame) -> dict[str, dict[str, float | None]]:
    ranges: dict[str, dict[str, float | None]] = {}
    for col in df.select_dtypes(include="number").columns:
        s = pd.to_numeric(df[col], errors="coerce")
        ranges[str(col)] = {
            "min": None if s.dropna().empty else float(s.min()),
            "max": None if s.dropna().empty else float(s.max()),
        }
    return ranges


def dataframe_profile(dataset: str, df: pd.DataFrame) -> dict[str, Any]:
    profile: dict[str, Any] = {
        "dataset": dataset,
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "columns": [str(c) for c in df.columns],
        "schema_hash": dataframe_schema_hash(df),
        "numeric_ranges": _numeric_ranges(df),
    }
    if cfg.COL_DATE in df.columns:
        dates = pd.to_datetime(df[cfg.COL_DATE], errors="coerce").dropna()
        profile["date_range"] = {
            "min": None if dates.empty else dates.min().strftime("%Y-%m-%d"),
            "max": None if dates.empty else dates.max().strftime("%Y-%m-%d"),
        }
    if dataset == "traffic":
        if cfg.COL_AREA in df.columns:
            profile["unique_areas"] = int(df[cfg.COL_AREA].nunique(dropna=True))
        if cfg.COL_ROAD in df.columns:
            profile["unique_roads"] = int(df[cfg.COL_ROAD].nunique(dropna=True))
    if dataset == "aqi" and cfg.COL_AQI_CATEGORY in df.columns:
        profile["unique_categories"] = int(df[cfg.COL_AQI_CATEGORY].nunique(dropna=True))
    return profile


def artifact_fingerprint(dataset: str, path: Path, df: pd.DataFrame) -> dict[str, Any]:
    return {
        "path": str(path),
        "file_sha256": file_sha256(path),
        "modified_utc": datetime.fromtimestamp(
            path.stat().st_mtime, tz=timezone.utc
        ).isoformat(),
        **dataframe_profile(dataset, df),
    }


def ensure_governed_artifacts_exist(dataset: str) -> None:
    paths = dataset_paths(dataset)
    missing = [str(p) for p in (paths.canonical, paths.processed) if not p.exists()]
    if missing:
        raise MissingGovernedDatasetError(
            f"{dataset}: missing governed parquet artifact(s): {', '.join(missing)}. "
            "Run the governed import pipeline; runtime synthetic/CSV fallback is disabled."
        )


def _read_parquet(path: Path, dataset: str, role: str) -> pd.DataFrame:
    try:
        return pd.read_parquet(path)
    except Exception as exc:
        raise RuntimeDataIntegrityError(
            f"{dataset}: failed to read {role} parquet at {path}: {exc}"
        ) from exc


def expected_processed_from_canonical(dataset: str, canonical: pd.DataFrame) -> pd.DataFrame:
    return clean_traffic(canonical) if dataset == "traffic" else clean_aqi(canonical)


def validate_processed_against_canonical(dataset: str) -> dict[str, Any]:
    ensure_governed_artifacts_exist(dataset)
    paths = dataset_paths(dataset)
    canonical = _read_parquet(paths.canonical, dataset, "canonical raw")
    processed = _read_parquet(paths.processed, dataset, "processed")
    expected = expected_processed_from_canonical(dataset, canonical)

    if len(expected) != len(processed):
        raise DatasetFingerprintMismatchError(
            f"{dataset}: processed row count {len(processed)} does not match canonical-derived "
            f"row count {len(expected)}."
        )
    missing = [c for c in expected.columns if c not in processed.columns]
    if missing:
        raise DatasetFingerprintMismatchError(
            f"{dataset}: processed parquet missing canonical-derived columns: {missing}"
        )

    profile = {
        "canonical": artifact_fingerprint(dataset, paths.canonical, canonical),
        "processed": artifact_fingerprint(dataset, paths.processed, processed),
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "governance_status": "PASS",
        "origin": "governed_canonical_parquet",
    }
    return profile


def build_governed_manifest() -> dict[str, Any]:
    return {
        "schema_version": "phase0.1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "runtime_env": os.getenv("BUIP_RUNTIME_ENV", cfg.RUNTIME_ENV),
        "synthetic_bootstrap_allowed": bool(cfg.ALLOW_SYNTHETIC_BOOTSTRAP),
        "datasets": {
            "traffic": validate_processed_against_canonical("traffic"),
            "aqi": validate_processed_against_canonical("aqi"),
        },
    }


def write_governed_manifest(manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    out = manifest or build_governed_manifest()
    path = governed_manifest_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    return out


def read_governed_manifest() -> dict[str, Any]:
    path = governed_manifest_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeDataIntegrityError(f"Invalid governed manifest at {path}: {exc}") from exc


def validate_manifest_current(manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    current = build_governed_manifest()
    stored = manifest if manifest is not None else read_governed_manifest()
    if not stored:
        return write_governed_manifest(current)
    for dataset in ("traffic", "aqi"):
        cur = current["datasets"][dataset]
        old = stored.get("datasets", {}).get(dataset, {})
        for role in ("canonical", "processed"):
            if cur[role]["file_sha256"] != old.get(role, {}).get("file_sha256"):
                raise DatasetFingerprintMismatchError(
                    f"{dataset}: {role} fingerprint mismatch against governed manifest."
                )
    return current


def active_dataset_fingerprint(dataset: str) -> str:
    profile = validate_processed_against_canonical(dataset)
    processed_hash = profile["processed"]["file_sha256"]
    canonical_hash = profile["canonical"]["file_sha256"]
    return hashlib.sha256(f"{dataset}:{canonical_hash}:{processed_hash}".encode("utf-8")).hexdigest()


def provenance_summary(dataset: str) -> dict[str, Any]:
    profile = validate_processed_against_canonical(dataset)
    processed = profile["processed"]
    return {
        "dataset": dataset,
        "source": "canonical_raw_parquet -> processed_parquet",
        "row_count": processed["row_count"],
        "date_range": processed.get("date_range", {}),
        "fingerprint": active_dataset_fingerprint(dataset)[:16],
        "last_refresh": processed["modified_utc"],
        "governance_status": profile["governance_status"],
    }


def assert_synthetic_runtime_disabled() -> None:
    if is_production_runtime() and cfg.ALLOW_SYNTHETIC_BOOTSTRAP:
        raise SyntheticDataDetectedError(
            "Production runtime cannot allow synthetic bootstrap generation."
        )


def run_startup_governance_checks(write_manifest_if_missing: bool = True) -> dict[str, Any]:
    assert_synthetic_runtime_disabled()
    manifest = read_governed_manifest()
    if manifest:
        return validate_manifest_current(manifest)
    current = build_governed_manifest()
    return write_governed_manifest(current) if write_manifest_if_missing else current
