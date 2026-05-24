"""Traffic duplicate-key governance — aggregation policy tests."""

from pathlib import Path

import pandas as pd
import pytest

from config.data_config import (
    COL_AREA,
    COL_CAPACITY,
    COL_CONGESTION,
    COL_DATE,
    COL_INCIDENTS,
    COL_PEDESTRIAN,
    COL_PT_USAGE,
    COL_ROAD,
    COL_ROADWORK,
    COL_SIGNAL,
    COL_SPEED,
    COL_TRAFFIC_VOL,
    COL_WEATHER,
    TRAFFIC_RAW_PATH,
)
from data_layer.real_data_import import prepare_import_data, run_dry_run_import
from data_layer.traffic_duplicate_governance import govern_traffic_duplicate_keys
from utils.validators import validate_raw_traffic_dataframe

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "real_data"


def test_partial_duplicate_group_aggregates_to_one_row():
    df = pd.DataFrame(
        {
            COL_DATE: pd.to_datetime(["2022-01-04", "2022-01-04"]),
            COL_AREA: ["Electronic City", "Electronic City"],
            COL_ROAD: ["Road_3", "Road_3"],
            COL_CONGESTION: [72.3, 66.1],
            COL_SPEED: [23.1, 17.3],
            COL_INCIDENTS: [0, 0],
            COL_CAPACITY: [61.8, 77.0],
            COL_PEDESTRIAN: [151, 227],
            COL_PT_USAGE: [64.8, 71.9],
            COL_SIGNAL: [70.9, 82.0],
            COL_TRAFFIC_VOL: [2141, 1657],
            COL_WEATHER: ["Clear", "Cloudy"],
            COL_ROADWORK: [None, "Minor"],
        }
    )
    out, stats = govern_traffic_duplicate_keys(df)
    assert len(out) == 1
    assert stats["partial_groups_aggregated"] == 1
    assert stats["rows_collapsed_by_aggregation"] == 1
    assert out.iloc[0][COL_CONGESTION] == pytest.approx(69.2, abs=0.1)


def test_repo_traffic_csv_passes_validation_after_governance():
    if not TRAFFIC_RAW_PATH.exists():
        return
    prepared = prepare_import_data(TRAFFIC_RAW_PATH, FIXTURES / "aqi_source_sample.csv")
    assert prepared.traffic_duplicate_stats["duplicate_key_rows_before"] > 0
    report = validate_raw_traffic_dataframe(prepared.traffic)
    assert report.duplicate_count == 0
    assert not report.has_blocking_findings


def test_dry_run_repo_csvs_no_traffic_duplicate_error():
    from config.data_config import AQI_RAW_PATH

    if not TRAFFIC_RAW_PATH.exists() or not AQI_RAW_PATH.exists():
        return
    result = run_dry_run_import(TRAFFIC_RAW_PATH, AQI_RAW_PATH)
    tdg = result.profile.traffic_duplicate_governance
    assert tdg.get("rows_collapsed_by_aggregation", 0) == 357
    assert tdg.get("rows_after", 0) == 8579
    assert not result.profile.raw_validation["traffic"]["has_blocking_findings"]
