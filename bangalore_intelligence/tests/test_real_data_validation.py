"""Phase 2 — raw validation governance."""

from pathlib import Path

import pandas as pd

from config.data_config import DATA_SCHEMA_VERSION
from data_layer.real_data_import import normalize_traffic_dataframe, run_dry_run_import
from utils.validators import (
    ValidationSeverity,
    hash_source_file,
    validate_raw_aqi_dataframe,
    validate_raw_traffic_dataframe,
    validate_schema_version,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "real_data"


def test_schema_version_incompatible_is_critical():
    finding = validate_schema_version("0.9.0")
    assert finding is not None
    assert finding.severity == ValidationSeverity.CRITICAL


def test_hash_source_file_metadata():
    path = FIXTURES / "traffic_source_sample.csv"
    meta = hash_source_file(path)
    assert meta["size_bytes"] > 0
    assert len(meta["sha256"]) == 64


def test_traffic_duplicate_keys_detected():
    df = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2022-01-01", "2022-01-01"]),
            "Area Name": ["A", "A"],
            "Road Name": ["R1", "R1"],
            "Congestion_Level": [80.0, 81.0],
            "Average_Speed": [30.0, 29.0],
            "Incident_Reports": [1, 2],
            "Road_Capacity_Utilization": [85.0, 86.0],
            "Pedestrian_and_Cyclist_Count": [10, 11],
            "Public_Transport_Usage": [50.0, 51.0],
            "Traffic_Signal_Compliance": [70.0, 71.0],
            "Traffic_Volume": [1000, 1001],
            "Weather_Condition": ["Clear", "Clear"],
            "Roadwork_Activity": ["None", "None"],
        }
    )
    report = validate_raw_traffic_dataframe(df)
    assert report.duplicate_count == 2
    assert any(f.code == "duplicate_keys" for f in report.findings)


def test_aqi_duplicate_dates_detected():
    df = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2021-01-01", "2021-01-01"]),
            "PM_2_5": [40.0, 41.0],
            "T": [28.0, 27.0],
            "Tm": [18.0, 17.0],
            "TM": [28.0, 27.0],
            "SLP": [1010.0, 1011.0],
            "H": [60.0, 61.0],
            "VV": [2.0, 2.1],
            "V": [1.5, 1.4],
            "VM": [3.0, 2.9],
        }
    )
    report = validate_raw_aqi_dataframe(df)
    assert report.duplicate_count == 2
    assert any(f.code == "duplicate_keys" for f in report.findings)


def test_unknown_weather_category_warning():
    df = pd.read_csv(FIXTURES / "traffic_source_sample.csv")
    out = normalize_traffic_dataframe(df)
    out.loc[0, "Weather_Condition"] = "Typhoon"
    report = validate_raw_traffic_dataframe(out)
    unknown = [f for f in report.findings if f.code == "unknown_category_values"]
    assert unknown
    assert unknown[0].severity in (ValidationSeverity.WARNING, ValidationSeverity.ERROR)


def test_semantic_range_violation():
    df = pd.read_csv(FIXTURES / "traffic_source_sample.csv")
    out = normalize_traffic_dataframe(df)
    out.loc[0, "Congestion_Level"] = 150.0
    report = validate_raw_traffic_dataframe(out)
    assert any(f.code == "semantic_range_violation" for f in report.findings)


def test_dry_run_profile_includes_raw_validation():
    result = run_dry_run_import(
        FIXTURES / "traffic_source_sample.csv",
        FIXTURES / "aqi_source_sample.csv",
    )
    rv = result.profile.raw_validation
    assert "traffic" in rv
    assert "aqi" in rv
    assert "severity_totals" in rv
    assert rv["traffic"]["source_metadata"]["sha256"]
    assert result.profile.schema_version == DATA_SCHEMA_VERSION


def test_repo_csvs_run_raw_validation_when_present():
    from config.data_config import AQI_RAW_PATH, TRAFFIC_RAW_PATH

    if not TRAFFIC_RAW_PATH.exists() or not AQI_RAW_PATH.exists():
        return
    result = run_dry_run_import(TRAFFIC_RAW_PATH, AQI_RAW_PATH)
    rv = result.profile.raw_validation
    assert "traffic" in rv and "aqi" in rv
    assert rv["traffic"]["source_metadata"]["sha256"]
    assert not rv["traffic"]["has_blocking_findings"]
    assert result.profile.traffic_duplicate_governance.get("rows_collapsed_by_aggregation", 0) >= 0
    assert "TM" in result.aqi.columns
    assert not rv["aqi"]["has_blocking_findings"]
