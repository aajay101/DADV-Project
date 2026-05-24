"""Phase 0 — governed runtime traffic data contract (repository canonical truth)."""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd
import pytest

from config.data_config import (
    AQI_RAW_PATH,
    COL_AREA,
    COL_CAPACITY,
    COL_CONGESTION,
    COL_DATE,
    COL_INCIDENTS,
    COL_ROAD,
    COL_SPEED,
    TRAFFIC_CANONICAL_RAW_PARQUET,
    TRAFFIC_CLEAN_PATH,
    TRAFFIC_RAW_PATH,
    TRAFFIC_RUNTIME_AREAS,
    TRAFFIC_RUNTIME_CANONICAL_ROWS,
    TRAFFIC_RUNTIME_DATE_MAX,
    TRAFFIC_RUNTIME_DATE_MIN,
    TRAFFIC_RUNTIME_DUPLICATE_GROUPS_AGGREGATED,
    TRAFFIC_RUNTIME_DUPLICATE_ROWS_COLLAPSED,
    TRAFFIC_RUNTIME_INCIDENT_SUM_PROCESSED,
    TRAFFIC_RUNTIME_KPI_TOLERANCE,
    TRAFFIC_RUNTIME_MEAN_CAPACITY,
    TRAFFIC_RUNTIME_MEAN_CONGESTION,
    TRAFFIC_RUNTIME_MEAN_SPEED,
    TRAFFIC_RUNTIME_PROCESSED_ROWS,
    TRAFFIC_RUNTIME_ROAD_COUNT,
    TRAFFIC_RUNTIME_ROAD_PREFIX,
    TRAFFIC_RUNTIME_SOURCE_CSV_ROWS,
)
from data_layer.loaders import (
    SOURCE_PROCESSED_PARQUET,
    describe_data_sources,
    get_last_load_source,
    load_traffic_clean,
    resolve_traffic_data_source,
)
from data_layer.real_data_import import normalize_traffic_dataframe, run_dry_run_import
from utils.validators import validate_raw_traffic_dataframe

TOL = TRAFFIC_RUNTIME_KPI_TOLERANCE


@pytest.fixture
def require_governed_artifacts():
    missing = [
        p for p in (TRAFFIC_RAW_PATH, TRAFFIC_CANONICAL_RAW_PARQUET, TRAFFIC_CLEAN_PATH)
        if not p.exists()
    ]
    if missing:
        pytest.skip(f"Governed artifacts missing: {missing}. Run import_real_data.py --apply.")


def test_runtime_constants_match_config_module():
    assert TRAFFIC_RUNTIME_SOURCE_CSV_ROWS == 8936
    assert TRAFFIC_RUNTIME_CANONICAL_ROWS == 8579
    assert TRAFFIC_RUNTIME_PROCESSED_ROWS == 8579
    assert len(TRAFFIC_RUNTIME_AREAS) == 8


def test_source_csv_row_count(require_governed_artifacts):
    raw = pd.read_csv(TRAFFIC_RAW_PATH)
    assert len(raw) == TRAFFIC_RUNTIME_SOURCE_CSV_ROWS


def test_traffic_aliases_map_repo_headers():
    raw = pd.read_csv(TRAFFIC_RAW_PATH, nrows=5)
    out = normalize_traffic_dataframe(raw)
    assert COL_DATE in out.columns
    assert COL_AREA in out.columns
    assert COL_ROAD in out.columns
    assert COL_CONGESTION in out.columns


def test_dry_run_repo_contract(require_governed_artifacts):
    if not AQI_RAW_PATH.exists():
        pytest.skip("AQI raw missing")
    result = run_dry_run_import(TRAFFIC_RAW_PATH, AQI_RAW_PATH)
    tdg = result.profile.traffic_duplicate_governance
    assert result.profile.traffic["row_count"] == TRAFFIC_RUNTIME_CANONICAL_ROWS
    assert tdg["rows_before"] == TRAFFIC_RUNTIME_SOURCE_CSV_ROWS
    assert tdg["rows_collapsed_by_aggregation"] == TRAFFIC_RUNTIME_DUPLICATE_ROWS_COLLAPSED
    assert tdg["partial_groups_aggregated"] == TRAFFIC_RUNTIME_DUPLICATE_GROUPS_AGGREGATED
    assert not result.profile.raw_validation["traffic"]["has_blocking_findings"]


def test_canonical_and_processed_parquet_contract(require_governed_artifacts):
    canonical = pd.read_parquet(TRAFFIC_CANONICAL_RAW_PARQUET)
    processed = pd.read_parquet(TRAFFIC_CLEAN_PATH)

    assert len(canonical) == TRAFFIC_RUNTIME_CANONICAL_ROWS
    assert len(processed) == TRAFFIC_RUNTIME_PROCESSED_ROWS

    for df in (canonical, processed):
        dates = pd.to_datetime(df[COL_DATE])
        assert str(dates.min().date()) == TRAFFIC_RUNTIME_DATE_MIN
        assert str(dates.max().date()) == TRAFFIC_RUNTIME_DATE_MAX
        assert set(df[COL_AREA].unique()) == set(TRAFFIC_RUNTIME_AREAS)
        assert df[COL_ROAD].nunique() == TRAFFIC_RUNTIME_ROAD_COUNT
        assert all(str(r).startswith(TRAFFIC_RUNTIME_ROAD_PREFIX) for r in df[COL_ROAD].unique())

        assert df[COL_CONGESTION].mean() == pytest.approx(
            TRAFFIC_RUNTIME_MEAN_CONGESTION, abs=TOL
        )
        assert df[COL_SPEED].mean() == pytest.approx(TRAFFIC_RUNTIME_MEAN_SPEED, abs=TOL)
        assert df[COL_CAPACITY].mean() == pytest.approx(
            TRAFFIC_RUNTIME_MEAN_CAPACITY, abs=TOL
        )

    assert int(processed[COL_INCIDENTS].sum()) == TRAFFIC_RUNTIME_INCIDENT_SUM_PROCESSED

    dup_report = validate_raw_traffic_dataframe(canonical)
    assert dup_report.duplicate_count == 0
    assert not dup_report.has_blocking_findings


def test_loader_uses_processed_tier_and_matches_contract(require_governed_artifacts):
    assert resolve_traffic_data_source() == SOURCE_PROCESSED_PARQUET
    assert describe_data_sources()["traffic"] == SOURCE_PROCESSED_PARQUET

    load_traffic_clean.clear()
    with patch("data_layer.loaders.st.cache_data", lambda **kw: (lambda fn: fn)):
        df = load_traffic_clean()

    assert get_last_load_source("traffic") == SOURCE_PROCESSED_PARQUET
    assert len(df) == TRAFFIC_RUNTIME_PROCESSED_ROWS
    assert "day_of_week" in df.columns
    assert "at_max_capacity" in df.columns
