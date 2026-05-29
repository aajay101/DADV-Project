"""Phase 3 — processed pipeline integration and loader preference."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from config import data_config
from config.data_config import (
    AQI_DERIVED_COLUMNS,
    TRAFFIC_DERIVED_COLUMNS,
)
from data_layer import loaders
from data_layer.real_data_import import run_real_import
from utils.validators import (
    validate_processed_aqi_dataframe,
    validate_processed_traffic_dataframe,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "real_data"
TRAFFIC_TEMPLATE = FIXTURES / "traffic_source_sample.csv"
AQI_TEMPLATE = FIXTURES / "aqi_source_sample.csv"


def _expand_traffic_csv(path: Path, rows: int = 12) -> None:
    template = pd.read_csv(TRAFFIC_TEMPLATE).iloc[0]
    records = []
    for i in range(rows):
        row = template.copy()
        row["Date"] = (pd.Timestamp("2022-01-01") + pd.Timedelta(days=i)).strftime("%Y-%m-%d")
        row["Area Name"] = f"Area_{i}"
        row["Road Name"] = f"Road_{i}"
        records.append(row)
    pd.DataFrame(records).to_csv(path, index=False)


def _expand_aqi_csv(path: Path, rows: int = 32) -> None:
    base = pd.read_csv(AQI_TEMPLATE)
    template = base.dropna(how="all").dropna(subset=["PM 2.5"]).iloc[0]
    records = []
    for i in range(rows):
        row = template.copy()
        row["Date"] = (pd.Timestamp("2021-01-01") + pd.Timedelta(days=i)).strftime("%Y-%m-%d")
        row["PM 2.5"] = 40.0 + i
        records.append(row)
    pd.DataFrame(records).to_csv(path, index=False)


@pytest.fixture
def import_paths(tmp_path, monkeypatch):
    """Redirect governed data paths into an isolated temp tree."""
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    temp_dir = tmp_path / ".import_temp"
    raw_dir.mkdir()
    processed_dir.mkdir()
    temp_dir.mkdir()

    paths = {
        "DATA_TEMP_DIR": temp_dir,
        "TRAFFIC_CANONICAL_RAW_PARQUET": raw_dir / "traffic_canonical_raw.parquet",
        "AQI_CANONICAL_RAW_PARQUET": raw_dir / "aqi_canonical_raw.parquet",
        "TRAFFIC_CANONICAL_RAW_TMP": temp_dir / "traffic_canonical_raw.tmp.parquet",
        "AQI_CANONICAL_RAW_TMP": temp_dir / "aqi_canonical_raw.tmp.parquet",
        "TRAFFIC_CLEAN_PATH": processed_dir / "traffic_clean.parquet",
        "AQI_CLEAN_PATH": processed_dir / "aqi_clean.parquet",
        "TRAFFIC_CLEAN_TMP": temp_dir / "traffic_clean.tmp.parquet",
        "AQI_CLEAN_TMP": temp_dir / "aqi_clean.tmp.parquet",
        "TRAFFIC_CLEAN_BACKUP": processed_dir / "traffic_clean.parquet.bak",
        "AQI_CLEAN_BACKUP": processed_dir / "aqi_clean.parquet.bak",
    }
    import_paths = [
        "TRAFFIC_CANONICAL_RAW_PARQUET",
        "AQI_CANONICAL_RAW_PARQUET",
        "TRAFFIC_CANONICAL_RAW_TMP",
        "AQI_CANONICAL_RAW_TMP",
        "TRAFFIC_CLEAN_PATH",
        "AQI_CLEAN_PATH",
        "TRAFFIC_CLEAN_TMP",
        "AQI_CLEAN_TMP",
        "TRAFFIC_CLEAN_BACKUP",
        "AQI_CLEAN_BACKUP",
        "DATA_TEMP_DIR",
    ]
    for name, value in paths.items():
        monkeypatch.setattr(data_config, name, value)
        monkeypatch.setattr("config.data_config." + name, value)
    for name in import_paths:
        monkeypatch.setattr("data_layer.real_data_import." + name, paths[name])
    monkeypatch.setattr(loaders, "TRAFFIC_CLEAN_PATH", paths["TRAFFIC_CLEAN_PATH"])
    monkeypatch.setattr(loaders, "AQI_CLEAN_PATH", paths["AQI_CLEAN_PATH"])
    monkeypatch.setattr(loaders, "TRAFFIC_CANONICAL_RAW_PARQUET", paths["TRAFFIC_CANONICAL_RAW_PARQUET"])
    monkeypatch.setattr(loaders, "AQI_CANONICAL_RAW_PARQUET", paths["AQI_CANONICAL_RAW_PARQUET"])
    loaders.load_traffic_clean.clear()
    loaders.load_aqi_clean.clear()
    return paths


@pytest.fixture
def import_sources(tmp_path):
    traffic = tmp_path / "traffic.csv"
    aqi = tmp_path / "aqi.csv"
    _expand_traffic_csv(traffic)
    _expand_aqi_csv(aqi)
    return traffic, aqi


def test_real_import_writes_canonical_and_processed(import_paths, import_sources):
    traffic_src, aqi_src = import_sources
    result = run_real_import(traffic_src, aqi_src)
    assert result.success, result.profile.error

    assert import_paths["TRAFFIC_CANONICAL_RAW_PARQUET"].exists()
    assert import_paths["AQI_CANONICAL_RAW_PARQUET"].exists()
    assert import_paths["TRAFFIC_CLEAN_PATH"].exists()
    assert import_paths["AQI_CLEAN_PATH"].exists()

    traffic_proc = pd.read_parquet(import_paths["TRAFFIC_CLEAN_PATH"])
    aqi_proc = pd.read_parquet(import_paths["AQI_CLEAN_PATH"])
    assert validate_processed_traffic_dataframe(traffic_proc).ok
    assert validate_processed_aqi_dataframe(aqi_proc).ok
    for col in TRAFFIC_DERIVED_COLUMNS:
        assert col in traffic_proc.columns
    for col in AQI_DERIVED_COLUMNS:
        assert col in aqi_proc.columns


def test_failed_processed_validation_preserves_prior_clean(import_paths, import_sources, monkeypatch):
    traffic_src, aqi_src = import_sources
    first = run_real_import(traffic_src, aqi_src)
    assert first.success

    kept_before = pd.read_parquet(import_paths["TRAFFIC_CLEAN_PATH"])
    rows_before = len(kept_before)

    monkeypatch.setattr(data_config, "MIN_PROCESSED_TRAFFIC_ROWS", 10_000)
    monkeypatch.setattr("utils.validators.MIN_PROCESSED_TRAFFIC_ROWS", 10_000)

    second = run_real_import(traffic_src, aqi_src)
    assert not second.success

    kept_after = pd.read_parquet(import_paths["TRAFFIC_CLEAN_PATH"])
    assert len(kept_after) == rows_before


def test_loader_prefers_canonical_raw_when_processed_missing(import_paths, import_sources):
    traffic_src, aqi_src = import_sources
    result = run_real_import(traffic_src, aqi_src)
    assert result.success

    import_paths["TRAFFIC_CLEAN_PATH"].unlink()
    import_paths["AQI_CLEAN_PATH"].unlink()

    traffic_df = loaders.load_traffic_clean()
    aqi_df = loaders.load_aqi_clean()
    assert len(traffic_df) >= 12
    assert len(aqi_df) >= 32
    assert import_paths["TRAFFIC_CLEAN_PATH"].exists()
    assert import_paths["AQI_CLEAN_PATH"].exists()
