"""Phase 5 — end-to-end QA hardening for governed real-data paths."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from config import data_config
from config.data_config import IMPORT_PROFILE_PATH
from data_layer.loaders import (
    SOURCE_CANONICAL_RAW_PARQUET,
    SOURCE_MISSING_GOVERNED_DATA,
    SOURCE_PROCESSED_PARQUET,
    describe_data_sources,
    get_last_load_source,
    load_aqi_clean,
    load_traffic_clean,
    read_import_profile_freshness,
    resolve_traffic_data_source,
)
from data_layer.page_bundles import build_aqi_crisis_bundle, build_traffic_command_bundle
from data_layer.real_data_import import run_real_import
from filters.state import AQI_STATE_DEFAULTS, TRAFFIC_STATE_DEFAULTS
from tests.test_real_processed_pipeline import _expand_aqi_csv, _expand_traffic_csv
from data_layer.governance import MissingGovernedDatasetError

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "real_data"


@pytest.fixture
def governed_paths(tmp_path, monkeypatch):
    raw = tmp_path / "raw"
    processed = tmp_path / "processed"
    meta = tmp_path / "metadata"
    archive = tmp_path / "archive"
    temp = tmp_path / ".import_temp"
    for d in (raw, processed, meta, archive, temp):
        d.mkdir(parents=True, exist_ok=True)

    paths = {
        "DATA_TEMP_DIR": temp,
        "TRAFFIC_CANONICAL_RAW_PARQUET": raw / "traffic_canonical_raw.parquet",
        "AQI_CANONICAL_RAW_PARQUET": raw / "aqi_canonical_raw.parquet",
        "TRAFFIC_CANONICAL_RAW_TMP": temp / "traffic_canonical_raw.tmp.parquet",
        "AQI_CANONICAL_RAW_TMP": temp / "aqi_canonical_raw.tmp.parquet",
        "TRAFFIC_CLEAN_PATH": processed / "traffic_clean.parquet",
        "AQI_CLEAN_PATH": processed / "aqi_clean.parquet",
        "TRAFFIC_CLEAN_TMP": temp / "traffic_clean.tmp.parquet",
        "AQI_CLEAN_TMP": temp / "aqi_clean.tmp.parquet",
        "TRAFFIC_CLEAN_BACKUP": processed / "traffic_clean.parquet.bak",
        "AQI_CLEAN_BACKUP": processed / "aqi_clean.parquet.bak",
        "DATA_METADATA_DIR": meta,
        "DATA_ARCHIVE_DIR": archive,
        "IMPORT_PROFILE_PATH": meta / "import_profile.json",
        "IMPORT_HISTORY_DIR": meta / "import_history",
        "IMPORT_LOCK_PATH": meta / ".import.lock",
    }
    import_real_names = [
        "DATA_TEMP_DIR",
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
    ]
    gov_names = [
        "DATA_METADATA_DIR",
        "DATA_ARCHIVE_DIR",
        "IMPORT_PROFILE_PATH",
        "IMPORT_HISTORY_DIR",
        "IMPORT_LOCK_PATH",
    ]
    for name, value in paths.items():
        monkeypatch.setattr(data_config, name, value)
        monkeypatch.setattr("config.data_config." + name, value)
    for name in import_real_names:
        monkeypatch.setattr("data_layer.real_data_import." + name, paths[name])
    for name in gov_names:
        monkeypatch.setattr("data_layer.import_governance." + name, paths[name])
    for name in (
        "TRAFFIC_CLEAN_PATH",
        "AQI_CLEAN_PATH",
        "TRAFFIC_CANONICAL_RAW_PARQUET",
        "AQI_CANONICAL_RAW_PARQUET",
        "IMPORT_PROFILE_PATH",
    ):
        monkeypatch.setattr("data_layer.loaders." + name, paths[name])

    load_traffic_clean.clear()
    load_aqi_clean.clear()
    return paths


@pytest.fixture
def governed_sources(tmp_path):
    traffic = tmp_path / "traffic.csv"
    aqi = tmp_path / "aqi.csv"
    _expand_traffic_csv(traffic)
    _expand_aqi_csv(aqi)
    return traffic, aqi


def test_resolve_source_priority_processed_over_canonical(governed_paths):
    governed_paths["TRAFFIC_CLEAN_PATH"].write_bytes(b"PAR1" * 40)
    governed_paths["TRAFFIC_CANONICAL_RAW_PARQUET"].write_bytes(b"PAR1" * 40)
    assert resolve_traffic_data_source() == SOURCE_PROCESSED_PARQUET


def test_resolve_source_priority_canonical_over_legacy(governed_paths):
    governed_paths["TRAFFIC_CANONICAL_RAW_PARQUET"].write_bytes(b"PAR1" * 40)
    assert resolve_traffic_data_source() == SOURCE_CANONICAL_RAW_PARQUET


def test_resolve_source_legacy_when_no_parquet(governed_paths):
    assert resolve_traffic_data_source() == SOURCE_MISSING_GOVERNED_DATA


def test_require_governed_data_blocks_legacy_fallback(governed_paths, monkeypatch):
    monkeypatch.setattr(data_config, "REQUIRE_GOVERNED_DATA", True)
    monkeypatch.setattr("data_layer.loaders.REQUIRE_GOVERNED_DATA", True)
    load_traffic_clean.clear()
    with patch("data_layer.loaders.st.cache_data", lambda **kw: (lambda fn: fn)):
        with pytest.raises(MissingGovernedDatasetError):
            load_traffic_clean()


def test_governed_import_then_loaders_use_processed(governed_paths, governed_sources):
    traffic_src, aqi_src = governed_sources
    result = run_real_import(traffic_src, aqi_src)
    assert result.success

    load_traffic_clean.clear()
    load_aqi_clean.clear()
    with patch("data_layer.loaders.st.cache_data", lambda **kw: (lambda fn: fn)):
        traffic_df = load_traffic_clean()
        aqi_df = load_aqi_clean()

    assert get_last_load_source("traffic") == SOURCE_PROCESSED_PARQUET
    assert get_last_load_source("aqi") == SOURCE_PROCESSED_PARQUET
    assert len(traffic_df) >= 10
    assert len(aqi_df) >= 30

    sources = describe_data_sources()
    assert sources["traffic"] == SOURCE_PROCESSED_PARQUET
    assert sources["aqi"] == SOURCE_PROCESSED_PARQUET


def test_page_bundles_non_empty_after_governed_load(governed_paths, governed_sources):
    traffic_src, aqi_src = governed_sources
    assert run_real_import(traffic_src, aqi_src).success

    load_traffic_clean.clear()
    load_aqi_clean.clear()
    with patch("data_layer.loaders.st.cache_data", lambda **kw: (lambda fn: fn)):
        traffic_df = load_traffic_clean()
        aqi_df = load_aqi_clean()

    t_state = dict(TRAFFIC_STATE_DEFAULTS)
    a_state = dict(AQI_STATE_DEFAULTS)
    with patch("data_layer.page_bundles.load_traffic_clean", return_value=traffic_df):
        t_bundle = build_traffic_command_bundle(t_state)
    with patch("data_layer.page_bundles.load_aqi_clean", return_value=aqi_df):
        a_bundle = build_aqi_crisis_bundle(a_state)

    assert not t_bundle.get("empty")
    assert not a_bundle.get("empty")
    assert t_bundle["hero_chart"]["fig"] is not None
    assert a_bundle["hero_chart"]["fig"] is not None


def test_dry_run_cli_succeeds():
    traffic = FIXTURES / "traffic_source_sample.csv"
    aqi = FIXTURES / "aqi_source_sample.csv"
    proc = subprocess.run(
        [sys.executable, "scripts/import_real_data.py", "--dry-run",
         "--traffic-source", str(traffic), "--aqi-source", str(aqi)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    assert "DRY RUN" in proc.stdout
    assert "no files written" in proc.stdout.lower() or "dry_run" in proc.stdout


def test_real_data_import_test_modules_smoke():
    """Focused import/validation/processed/governance modules import cleanly."""
    import tests.test_real_data_import  # noqa: F401
    import tests.test_real_data_validation  # noqa: F401
    import tests.test_real_processed_pipeline  # noqa: F401
    import tests.test_import_governance  # noqa: F401


def test_import_profile_freshness_when_present():
    if not IMPORT_PROFILE_PATH.exists():
        pytest.skip("No import profile on disk — run --apply first for local QA")
    meta = read_import_profile_freshness()
    assert "freshness_metadata" in meta or meta.get("import_timestamp")


def test_repo_import_profile_valid_json_if_present():
    if not IMPORT_PROFILE_PATH.exists():
        pytest.skip("No import profile written yet")
    profile = json.loads(IMPORT_PROFILE_PATH.read_text(encoding="utf-8"))
    assert profile.get("schema_version")
    if profile.get("success"):
        assert profile.get("timings", {}).get("total_import_time", 0) >= 0
        assert profile.get("processed_metadata", {}).get("traffic", {}).get("row_count", 0) > 0
