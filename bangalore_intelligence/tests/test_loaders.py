from unittest.mock import patch

import pytest

from config import data_config
from data_layer.loaders import (
    SOURCE_LEGACY_CSV_FALLBACK,
    SOURCE_MISSING_GOVERNED_DATA,
    SOURCE_PROCESSED_PARQUET,
    describe_data_sources,
    get_last_load_source,
    load_traffic_clean,
    resolve_traffic_data_source,
)
from data_layer.governance import MissingGovernedDatasetError
from utils.validators import validate_aqi_schema, validate_traffic_schema


def test_traffic_clean_schema(sample_traffic_df):
    assert validate_traffic_schema(sample_traffic_df).ok
    assert len(sample_traffic_df) > 0


def test_aqi_clean_schema(sample_aqi_df):
    assert validate_aqi_schema(sample_aqi_df).ok
    assert len(sample_aqi_df) > 0


def test_describe_data_sources_reports_tiers(tmp_path, monkeypatch):
    processed = tmp_path / "processed"
    raw = tmp_path / "raw"
    processed.mkdir()
    raw.mkdir()
    clean = processed / "traffic_clean.parquet"
    canonical = raw / "traffic_canonical_raw.parquet"
    clean.write_bytes(b"x" * 200)
    canonical.write_bytes(b"x" * 200)
    monkeypatch.setattr(data_config, "TRAFFIC_CLEAN_PATH", clean)
    monkeypatch.setattr(data_config, "TRAFFIC_CANONICAL_RAW_PARQUET", canonical)
    monkeypatch.setattr("data_layer.loaders.TRAFFIC_CLEAN_PATH", clean)
    monkeypatch.setattr("data_layer.loaders.TRAFFIC_CANONICAL_RAW_PARQUET", canonical)

    assert resolve_traffic_data_source() == SOURCE_PROCESSED_PARQUET
    sources = describe_data_sources()
    assert sources["traffic"] == SOURCE_PROCESSED_PARQUET


def test_load_traffic_records_source_tier(sample_traffic_df, tmp_path, monkeypatch):
    processed = tmp_path / "traffic_clean.parquet"
    canonical = tmp_path / "traffic_canonical_raw.parquet"
    sample_traffic_df.to_parquet(processed, index=False)
    sample_traffic_df.to_parquet(canonical, index=False)
    monkeypatch.setattr(data_config, "TRAFFIC_CLEAN_PATH", processed)
    monkeypatch.setattr(data_config, "TRAFFIC_CANONICAL_RAW_PARQUET", canonical)
    monkeypatch.setattr("data_layer.loaders.TRAFFIC_CLEAN_PATH", processed)
    monkeypatch.setattr("data_layer.loaders.TRAFFIC_CANONICAL_RAW_PARQUET", canonical)
    load_traffic_clean.clear()

    with patch("data_layer.loaders.st.cache_data", lambda **kw: (lambda fn: fn)):
        df = load_traffic_clean()
    assert len(df) > 0
    assert get_last_load_source("traffic") == SOURCE_PROCESSED_PARQUET


def test_legacy_fallback_hard_fails(monkeypatch):
    monkeypatch.setattr(data_config, "REQUIRE_GOVERNED_DATA", False)
    monkeypatch.setattr("data_layer.loaders.REQUIRE_GOVERNED_DATA", False)
    from data_layer.loaders import _guard_fallback_source

    with pytest.raises(MissingGovernedDatasetError):
        _guard_fallback_source("traffic", SOURCE_LEGACY_CSV_FALLBACK)


def test_missing_governed_source_tier_hard_fails(monkeypatch):
    from data_layer.loaders import _guard_fallback_source

    with pytest.raises(MissingGovernedDatasetError):
        _guard_fallback_source("traffic", SOURCE_MISSING_GOVERNED_DATA)
