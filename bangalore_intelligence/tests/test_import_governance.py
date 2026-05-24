"""Phase 4 — import locks, snapshots, profiles, and retention."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from config import data_config
from data_layer.import_governance import (
    ImportGovernanceError,
    ImportLockError,
    acquire_import_lock,
    archive_canonical_raw_snapshots,
    clear_stale_import_lock,
    import_lock,
    is_lock_stale,
    release_import_lock,
    write_import_profiles,
)
from data_layer.real_data_import import run_dry_run_import, run_real_import
from tests.test_real_processed_pipeline import _expand_aqi_csv, _expand_traffic_csv

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "real_data"


@pytest.fixture
def gov_paths(tmp_path, monkeypatch):
    meta = tmp_path / "metadata"
    archive = tmp_path / "archive"
    raw = tmp_path / "raw"
    processed = tmp_path / "processed"
    temp = tmp_path / ".import_temp"
    for d in (meta, archive, raw, processed, temp):
        d.mkdir(parents=True, exist_ok=True)

    paths = {
        "DATA_METADATA_DIR": meta,
        "DATA_ARCHIVE_DIR": archive,
        "IMPORT_PROFILE_PATH": meta / "import_profile.json",
        "IMPORT_HISTORY_DIR": meta / "import_history",
        "IMPORT_LOCK_PATH": meta / ".import.lock",
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
    }

    import_names = list(paths.keys())
    for name, value in paths.items():
        monkeypatch.setattr(data_config, name, value)
        monkeypatch.setattr("config.data_config." + name, value)
    for name in import_names:
        if hasattr(__import__("data_layer.real_data_import", fromlist=["x"]), name):
            monkeypatch.setattr("data_layer.real_data_import." + name, paths[name])
    for name in (
        "DATA_METADATA_DIR",
        "DATA_ARCHIVE_DIR",
        "IMPORT_PROFILE_PATH",
        "IMPORT_HISTORY_DIR",
        "IMPORT_LOCK_PATH",
    ):
        monkeypatch.setattr("data_layer.import_governance." + name, paths[name])

    return paths


@pytest.fixture
def import_sources(tmp_path):
    traffic = tmp_path / "traffic.csv"
    aqi = tmp_path / "aqi.csv"
    _expand_traffic_csv(traffic)
    _expand_aqi_csv(aqi)
    return traffic, aqi


def test_import_lock_blocks_concurrent_acquire(gov_paths):
    acquire_import_lock()
    try:
        with pytest.raises(ImportLockError):
            acquire_import_lock()
    finally:
        release_import_lock()


def test_stale_lock_cleanup(gov_paths, monkeypatch):
    monkeypatch.setattr(data_config, "IMPORT_LOCK_STALE_SECONDS", 1)
    monkeypatch.setattr("data_layer.import_governance.IMPORT_LOCK_STALE_SECONDS", 1)

    gov_paths["IMPORT_LOCK_PATH"].write_text(
        json.dumps({"pid": 1, "started_at_unix": time.time() - 10}),
        encoding="utf-8",
    )
    assert is_lock_stale()
    assert clear_stale_import_lock()
    assert not gov_paths["IMPORT_LOCK_PATH"].exists()


def test_dry_run_writes_no_governance_artifacts(gov_paths, import_sources):
    traffic_src, aqi_src = import_sources
    run_dry_run_import(traffic_src, aqi_src)

    assert not gov_paths["IMPORT_PROFILE_PATH"].exists()
    assert list(gov_paths["IMPORT_HISTORY_DIR"].glob("import_*.json")) == []
    assert list(gov_paths["DATA_ARCHIVE_DIR"].glob("*.parquet")) == []
    assert not gov_paths["IMPORT_LOCK_PATH"].exists()


def test_successful_apply_writes_profile_history_and_snapshots(gov_paths, import_sources):
    traffic_src, aqi_src = import_sources
    result = run_real_import(traffic_src, aqi_src)
    assert result.success, result.profile.error

    assert gov_paths["IMPORT_PROFILE_PATH"].exists()
    history = list(gov_paths["IMPORT_HISTORY_DIR"].glob("import_*.json"))
    assert len(history) == 1

    profile = json.loads(gov_paths["IMPORT_PROFILE_PATH"].read_text(encoding="utf-8"))
    assert profile["success"] is True
    assert profile["source_metadata"]["traffic"]["sha256"]
    assert profile["timings"]["total_import_time"] > 0
    assert profile["processed_metadata"]["traffic"]["row_count"] >= 10
    assert profile["freshness_metadata"]["aqi"]["processed_last_date"]
    assert profile["governance"]["profile_path"]
    assert profile["governance"]["history_path"]

    traffic_snaps = list(gov_paths["DATA_ARCHIVE_DIR"].glob("traffic_raw_*.parquet"))
    aqi_snaps = list(gov_paths["DATA_ARCHIVE_DIR"].glob("aqi_raw_*.parquet"))
    assert len(traffic_snaps) == 1
    assert len(aqi_snaps) == 1


def test_failed_apply_does_not_write_profile(gov_paths, import_sources, monkeypatch):
    traffic_src, aqi_src = import_sources
    monkeypatch.setattr(data_config, "MIN_PROCESSED_TRAFFIC_ROWS", 10_000)
    monkeypatch.setattr("utils.validators.MIN_PROCESSED_TRAFFIC_ROWS", 10_000)

    result = run_real_import(traffic_src, aqi_src)
    assert not result.success
    assert not gov_paths["IMPORT_PROFILE_PATH"].exists()
    assert list(gov_paths["IMPORT_HISTORY_DIR"].glob("import_*.json")) == []


def test_snapshot_retention_policy(gov_paths, import_sources, monkeypatch):
    monkeypatch.setattr(data_config, "ARCHIVE_SNAPSHOT_RETENTION", 2)
    monkeypatch.setattr("data_layer.import_governance.ARCHIVE_SNAPSHOT_RETENTION", 2)

    counter = {"n": 0}

    def _unique_stamp() -> str:
        counter["n"] += 1
        return f"2024_01_01_12000{counter['n']}"

    monkeypatch.setattr("data_layer.real_data_import.stamp_for_filename", _unique_stamp)

    traffic_src, aqi_src = import_sources
    for _ in range(3):
        result = run_real_import(traffic_src, aqi_src)
        assert result.success

    assert len(list(gov_paths["DATA_ARCHIVE_DIR"].glob("traffic_raw_*.parquet"))) == 2
    assert len(list(gov_paths["DATA_ARCHIVE_DIR"].glob("aqi_raw_*.parquet"))) == 2


def test_import_lock_context_manager_releases(gov_paths):
    with import_lock() as payload:
        assert payload["pid"]
        assert gov_paths["IMPORT_LOCK_PATH"].exists()
    assert not gov_paths["IMPORT_LOCK_PATH"].exists()


def test_write_import_profiles_latest_and_history(gov_paths):
    payload = {"schema_version": "1.0.0", "mode": "test"}
    paths = write_import_profiles(payload, stamp="2024_01_01_120000")
    assert gov_paths["IMPORT_PROFILE_PATH"].exists()
    assert Path(paths["history_path"]).name == "import_2024_01_01_120000.json"


def test_archive_snapshots_require_canonical_files(gov_paths, tmp_path):
    missing = tmp_path / "missing.parquet"
    with pytest.raises(ImportGovernanceError):
        archive_canonical_raw_snapshots(missing, missing)
