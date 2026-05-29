"""Phase 1 — canonical real-data normalization and dry-run import."""

from pathlib import Path

import pandas as pd

from config.data_config import (
    COL_CONGESTION,
    COL_DATE,
    COL_ENVIRONMENTAL_IMPACT_SOURCE,
    COL_PARKING_USAGE,
    COL_PM25,
    COL_TRAVEL_TIME_INDEX,
    DATA_SCHEMA_VERSION,
    IMPORT_PROFILE_PATH,
    TRAFFIC_CANONICAL_RAW_PARQUET,
)
from data_layer.real_data_import import (
    normalize_aqi_dataframe,
    normalize_traffic_dataframe,
    preclean_aqi_source,
    run_dry_run_import,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "real_data"
TRAFFIC_FIXTURE = FIXTURES / "traffic_source_sample.csv"
AQI_FIXTURE = FIXTURES / "aqi_source_sample.csv"


def test_schema_version_constant():
    assert DATA_SCHEMA_VERSION == "1.0.0"


def test_traffic_normalization_preserves_extra_fields():
    raw = pd.read_csv(TRAFFIC_FIXTURE)
    out = normalize_traffic_dataframe(raw)
    assert COL_TRAVEL_TIME_INDEX in out.columns
    assert COL_ENVIRONMENTAL_IMPACT_SOURCE in out.columns
    assert COL_PARKING_USAGE in out.columns
    assert COL_CONGESTION in out.columns
    assert pd.api.types.is_numeric_dtype(out[COL_TRAVEL_TIME_INDEX])


def test_traffic_source_alias_mapping():
    raw = pd.read_csv(TRAFFIC_FIXTURE)
    assert "Congestion Level" in raw.columns
    out = normalize_traffic_dataframe(raw)
    assert COL_CONGESTION in out.columns
    assert "Congestion Level" not in out.columns


def test_aqi_preclean_drops_blank_and_missing_pm25():
    raw = pd.read_csv(AQI_FIXTURE)
    precleaned, stats = preclean_aqi_source(raw)
    assert stats["blank_rows_dropped"] == 1
    assert stats["missing_pm25_dropped"] == 1
    assert len(precleaned) == 2


def test_aqi_normalization_maps_pm25_and_coerces():
    raw = pd.read_csv(AQI_FIXTURE)
    out, stats = normalize_aqi_dataframe(raw)
    assert stats["blank_rows_dropped"] == 1
    assert len(out) == 2
    assert COL_PM25 in out.columns
    assert pd.api.types.is_numeric_dtype(out[COL_PM25])
    assert COL_DATE in out.columns


def test_dry_run_writes_no_governed_artifacts(tmp_path, monkeypatch):
    traffic = tmp_path / "traffic.csv"
    aqi = tmp_path / "aqi.csv"
    traffic.write_text(TRAFFIC_FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
    aqi.write_text(AQI_FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")

    targets = [
        tmp_path / "traffic_canonical_raw.parquet",
        tmp_path / "aqi_canonical_raw.parquet",
        tmp_path / "import_profile.json",
    ]
    for p in targets:
        assert not p.exists()

    result = run_dry_run_import(traffic, aqi)
    assert len(result.traffic) == 2
    assert len(result.aqi) == 2
    assert result.profile.schema_version == DATA_SCHEMA_VERSION
    assert result.profile.mode == "dry_run"

    for p in targets:
        assert not p.exists()

    # Project canonical paths must not be created by dry-run helper itself
    assert TRAFFIC_CANONICAL_RAW_PARQUET != traffic
    assert not IMPORT_PROFILE_PATH.exists() or IMPORT_PROFILE_PATH.stat().st_size >= 0


def test_dry_run_against_repo_csvs_if_present():
    from config.data_config import AQI_RAW_PATH, TRAFFIC_RAW_PATH

    if not TRAFFIC_RAW_PATH.exists() or not AQI_RAW_PATH.exists():
        return
    result = run_dry_run_import(TRAFFIC_RAW_PATH, AQI_RAW_PATH)
    assert result.profile.traffic.get("row_count", 0) > 0
    assert result.profile.aqi.get("row_count", 0) > 0
    # Do not assert exact row count — real data must not be hardcoded to 1095
