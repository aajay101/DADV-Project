"""Phase 0 governance validation suite."""

from __future__ import annotations

import pandas as pd
import pytest

from config import data_config
from data_layer.aggregation_audit import validate_sampling_metadata, validate_t01_config_parity
from data_layer.bootstrap_data import ensure_raw_datasets
from data_layer.governance import (
    SyntheticDataDetectedError,
    active_dataset_fingerprint,
    run_startup_governance_checks,
    validate_processed_against_canonical,
)
from data_layer.lab_data import get_lab_dataset
from data_layer.loaders import SOURCE_MISSING_GOVERNED_DATA, resolve_traffic_data_source
from data_layer.traffic_transforms import get_congestion_speed_scatter
from filters.state import TRAFFIC_STATE_DEFAULTS


def test_synthetic_bootstrap_disabled_in_runtime():
    with pytest.raises(SyntheticDataDetectedError):
        ensure_raw_datasets()


def test_missing_canonical_source_reports_missing(tmp_path, monkeypatch):
    processed = tmp_path / "traffic_clean.parquet"
    processed.write_bytes(b"x" * 200)
    missing = tmp_path / "traffic_canonical_raw.parquet"
    monkeypatch.setattr(data_config, "TRAFFIC_CLEAN_PATH", processed)
    monkeypatch.setattr(data_config, "TRAFFIC_CANONICAL_RAW_PARQUET", missing)
    monkeypatch.setattr("data_layer.loaders.TRAFFIC_CLEAN_PATH", processed)
    monkeypatch.setattr("data_layer.loaders.TRAFFIC_CANONICAL_RAW_PARQUET", missing)
    assert resolve_traffic_data_source() == SOURCE_MISSING_GOVERNED_DATA


def test_active_dataset_fingerprint_is_stable_for_current_artifacts():
    first = active_dataset_fingerprint("traffic")
    second = active_dataset_fingerprint("traffic")
    assert first == second
    assert len(first) == 64


def test_processed_matches_canonical_current_artifacts():
    profile = validate_processed_against_canonical("traffic")
    assert profile["governance_status"] == "PASS"
    assert profile["canonical"]["row_count"] == profile["processed"]["row_count"]


def test_startup_governance_checks_generate_manifest():
    manifest = run_startup_governance_checks()
    assert manifest["datasets"]["traffic"]["governance_status"] == "PASS"
    assert manifest["synthetic_bootstrap_allowed"] is False


def test_lab_dataset_inherits_global_traffic_filters(monkeypatch):
    full = pd.read_parquet(data_config.TRAFFIC_CLEAN_PATH)
    full["Date"] = pd.to_datetime(full["Date"])
    state = dict(TRAFFIC_STATE_DEFAULTS)
    state["traffic_selected_areas"] = ["Koramangala"]
    filtered = get_lab_dataset("traffic", state)
    assert len(filtered) < len(full)
    assert set(filtered["Area Name"].unique()) == {"Koramangala"}


def test_t01_kpi_chart_config_parity_current_dataset():
    df = pd.read_parquet(data_config.TRAFFIC_CLEAN_PATH)
    cfg = {
        "system_congestion": float(df["Congestion_Level"].mean()),
        "capacity_saturation_rate": float((df["Road_Capacity_Utilization"] >= 99.5).mean() * 100),
    }
    result = validate_t01_config_parity(df, cfg)
    assert result["ok"]


def test_sampling_metadata_attached_to_t09_dataset():
    df = pd.read_parquet(data_config.TRAFFIC_CLEAN_PATH)
    data = get_congestion_speed_scatter(df, max_points=100)
    result = validate_sampling_metadata(data)
    assert result["ok"]
    assert result["sampled"]
    assert result["metadata"]["sample_size"] == 100
