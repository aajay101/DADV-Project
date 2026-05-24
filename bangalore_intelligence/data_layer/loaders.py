"""Dataset loading and caching."""

from __future__ import annotations

import json
import logging
import time
import hashlib
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from config.data_config import (
    ALLOW_SYNTHETIC_BOOTSTRAP,
    AQI_CANONICAL_RAW_PARQUET,
    AQI_CLEAN_PATH,
    IMPORT_PROFILE_PATH,
    REQUIRE_GOVERNED_DATA,
    TRAFFIC_CANONICAL_RAW_PARQUET,
    TRAFFIC_CLEAN_PATH,
)
from data_layer.cleaners import clean_aqi, clean_traffic
from data_layer.governance import (
    MissingGovernedDatasetError,
    RuntimeDataIntegrityError,
    active_dataset_fingerprint,
    file_sha256,
    provenance_summary,
    validate_processed_against_canonical,
)
from utils.validators import assert_aqi_schema, assert_traffic_schema

logger = logging.getLogger(__name__)

_MIN_PARQUET_BYTES = 100
_MIN_CSV_BYTES = 10

SOURCE_PROCESSED_PARQUET = "processed_parquet"
SOURCE_CANONICAL_RAW_PARQUET = "canonical_raw_parquet"
SOURCE_LEGACY_CSV_FALLBACK = "legacy_csv_fallback"
SOURCE_MISSING_GOVERNED_DATA = "missing_governed_data"

_LAST_LOAD_SOURCES: dict[str, str] = {}


def _parquet_usable(path: Path) -> bool:
    return path.exists() and path.stat().st_size > _MIN_PARQUET_BYTES


def _csv_usable(path: Path) -> bool:
    return path.exists() and path.stat().st_size >= _MIN_CSV_BYTES


def resolve_traffic_data_source() -> str:
    """Return which storage tier loaders will use for traffic (no reads)."""
    if not _parquet_usable(TRAFFIC_CANONICAL_RAW_PARQUET):
        return SOURCE_MISSING_GOVERNED_DATA
    if _parquet_usable(TRAFFIC_CLEAN_PATH):
        return SOURCE_PROCESSED_PARQUET
    return SOURCE_CANONICAL_RAW_PARQUET


def resolve_aqi_data_source() -> str:
    """Return which storage tier loaders will use for AQI (no reads)."""
    if not _parquet_usable(AQI_CANONICAL_RAW_PARQUET):
        return SOURCE_MISSING_GOVERNED_DATA
    if _parquet_usable(AQI_CLEAN_PATH):
        return SOURCE_PROCESSED_PARQUET
    return SOURCE_CANONICAL_RAW_PARQUET


def get_last_load_source(dataset: str) -> str | None:
    """Last resolved source tier for traffic or aqi (test/diagnostics)."""
    return _LAST_LOAD_SOURCES.get(dataset)


def describe_data_sources() -> dict[str, str]:
    """Snapshot of loader tier selection before ensure_raw_datasets side effects."""
    return {
        "traffic": resolve_traffic_data_source(),
        "aqi": resolve_aqi_data_source(),
    }


def read_import_profile_freshness() -> dict[str, Any]:
    """Load freshness block from latest import profile when present."""
    if not IMPORT_PROFILE_PATH.exists():
        return {}
    try:
        profile = json.loads(IMPORT_PROFILE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return {
        "import_timestamp": profile.get("import_timestamp"),
        "success": profile.get("success"),
        "freshness_metadata": profile.get("freshness_metadata", {}),
        "processed_metadata": profile.get("processed_metadata", {}),
    }


def _guard_fallback_source(dataset: str, source: str) -> None:
    if source not in (SOURCE_LEGACY_CSV_FALLBACK, SOURCE_MISSING_GOVERNED_DATA):
        return
    raise MissingGovernedDatasetError(
        f"{dataset}: governed canonical parquet is required. Runtime CSV/synthetic fallback "
        f"is disabled (ALLOW_SYNTHETIC_BOOTSTRAP={ALLOW_SYNTHETIC_BOOTSTRAP}, "
        f"REQUIRE_GOVERNED_DATA={REQUIRE_GOVERNED_DATA})."
    )


def _load_traffic_from_source(source: str) -> pd.DataFrame:
    if source == SOURCE_PROCESSED_PARQUET:
        validate_processed_against_canonical("traffic")
        return pd.read_parquet(TRAFFIC_CLEAN_PATH)
    if source == SOURCE_CANONICAL_RAW_PARQUET:
        df = pd.read_parquet(TRAFFIC_CANONICAL_RAW_PARQUET)
        df = clean_traffic(df)
        TRAFFIC_CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(TRAFFIC_CLEAN_PATH, index=False)
        validate_processed_against_canonical("traffic")
        return df
    _guard_fallback_source("traffic", source)
    raise RuntimeDataIntegrityError(f"traffic: unsupported source tier {source}")


def _load_aqi_from_source(source: str) -> pd.DataFrame:
    if source == SOURCE_PROCESSED_PARQUET:
        validate_processed_against_canonical("aqi")
        return pd.read_parquet(AQI_CLEAN_PATH)
    if source == SOURCE_CANONICAL_RAW_PARQUET:
        df = pd.read_parquet(AQI_CANONICAL_RAW_PARQUET)
        df = clean_aqi(df)
        AQI_CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(AQI_CLEAN_PATH, index=False)
        validate_processed_against_canonical("aqi")
        return df
    _guard_fallback_source("aqi", source)
    raise RuntimeDataIntegrityError(f"aqi: unsupported source tier {source}")


@st.cache_data(show_spinner=False)
def _load_traffic_clean_cached(fingerprint: str) -> pd.DataFrame:
    source = resolve_traffic_data_source()
    _guard_fallback_source("traffic", source)
    df = _load_traffic_from_source(source)
    assert_traffic_schema(df)
    _LAST_LOAD_SOURCES["traffic"] = source
    _mark_loaded("traffic")
    return df


@st.cache_data(show_spinner=False)
def _load_aqi_clean_cached(fingerprint: str) -> pd.DataFrame:
    source = resolve_aqi_data_source()
    _guard_fallback_source("aqi", source)
    df = _load_aqi_from_source(source)
    assert_aqi_schema(df)
    _LAST_LOAD_SOURCES["aqi"] = source
    _mark_loaded("aqi")
    return df


def load_traffic_clean() -> pd.DataFrame:
    """Load governed traffic data; cache key includes active parquet fingerprints."""
    return _load_traffic_clean_cached(_cache_token("traffic"))


def load_aqi_clean() -> pd.DataFrame:
    """Load governed AQI data; cache key includes active parquet fingerprints."""
    return _load_aqi_clean_cached(_cache_token("aqi"))


load_traffic_clean.clear = _load_traffic_clean_cached.clear  # type: ignore[attr-defined]
load_aqi_clean.clear = _load_aqi_clean_cached.clear  # type: ignore[attr-defined]


def get_runtime_provenance(dataset: str) -> dict[str, Any]:
    """Return source disclosure for runtime panels/export metadata."""
    return provenance_summary(dataset)


def _cache_token(dataset: str) -> str:
    source = resolve_traffic_data_source() if dataset == "traffic" else resolve_aqi_data_source()
    _guard_fallback_source(dataset, source)
    try:
        return active_dataset_fingerprint(dataset)
    except MissingGovernedDatasetError:
        canonical = TRAFFIC_CANONICAL_RAW_PARQUET if dataset == "traffic" else AQI_CANONICAL_RAW_PARQUET
        if not _parquet_usable(canonical):
            raise
        digest = hashlib.sha256(f"{dataset}:{file_sha256(canonical)}:processed_missing".encode("utf-8"))
        return digest.hexdigest()


def _mark_loaded(dashboard: str) -> None:
    try:
        key = f"{dashboard}_data_loaded_at"
        st.session_state[key] = time.time()
        st.session_state[f"{dashboard}_data_stale"] = False
    except Exception:
        pass


def refresh_dashboard_data(dashboard: str) -> None:
    """Clear loader cache and reload datasets for one dashboard."""
    _load_traffic_clean_cached.clear() if dashboard == "traffic" else _load_aqi_clean_cached.clear()
    if dashboard == "traffic":
        load_traffic_clean()
    else:
        load_aqi_clean()
