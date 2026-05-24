"""Import operational governance — locks, snapshots, profiles, retention."""

from __future__ import annotations

import json
import os
import shutil
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from config.data_config import (
    AQI_ARCHIVE_PREFIX,
    ARCHIVE_SNAPSHOT_RETENTION,
    DATA_ARCHIVE_DIR,
    DATA_METADATA_DIR,
    IMPORT_HISTORY_DIR,
    IMPORT_LOCK_PATH,
    IMPORT_LOCK_STALE_SECONDS,
    IMPORT_PROFILE_PATH,
    TRAFFIC_ARCHIVE_PREFIX,
)


class ImportLockError(RuntimeError):
    """Raised when another import holds the lock."""


class ImportGovernanceError(RuntimeError):
    """Raised when profile or snapshot persistence fails."""


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_timestamp(dt: datetime | None = None) -> str:
    return (dt or _utc_now()).strftime("%Y-%m-%dT%H:%M:%SZ")


def _iso_timestamp(dt: datetime | None = None) -> str:
    return iso_timestamp(dt)


def stamp_for_filename(dt: datetime | None = None) -> str:
    return (dt or _utc_now()).strftime("%Y_%m_%d_%H%M%S")


def _stamp_for_filename(dt: datetime | None = None) -> str:
    return stamp_for_filename(dt)


def _read_lock_payload() -> dict[str, Any] | None:
    if not IMPORT_LOCK_PATH.exists():
        return None
    try:
        return json.loads(IMPORT_LOCK_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _lock_age_seconds(payload: dict[str, Any] | None) -> float | None:
    if payload is None:
        if IMPORT_LOCK_PATH.exists():
            return time.time() - IMPORT_LOCK_PATH.stat().st_mtime
        return None
    started = payload.get("started_at_unix")
    if isinstance(started, (int, float)):
        return time.time() - float(started)
    if IMPORT_LOCK_PATH.exists():
        return time.time() - IMPORT_LOCK_PATH.stat().st_mtime
    return None


def is_lock_stale(payload: dict[str, Any] | None = None) -> bool:
    age = _lock_age_seconds(payload if payload is not None else _read_lock_payload())
    return age is not None and age >= IMPORT_LOCK_STALE_SECONDS


def clear_stale_import_lock() -> bool:
    """Remove lock file when older than configured timeout. Returns True if removed."""
    payload = _read_lock_payload()
    if not IMPORT_LOCK_PATH.exists():
        return False
    if is_lock_stale(payload):
        IMPORT_LOCK_PATH.unlink(missing_ok=True)
        return True
    return False


def acquire_import_lock() -> dict[str, Any]:
    """
    Acquire exclusive import lock. Clears stale locks first.
    Raises ImportLockError if a live lock is held.
    """
    DATA_METADATA_DIR.mkdir(parents=True, exist_ok=True)
    clear_stale_import_lock()

    if IMPORT_LOCK_PATH.exists():
        payload = _read_lock_payload() or {}
        raise ImportLockError(
            f"Import already in progress (pid={payload.get('pid', 'unknown')}, "
            f"started={payload.get('started_at', 'unknown')})"
        )

    payload = {
        "pid": os.getpid(),
        "started_at": _iso_timestamp(),
        "started_at_unix": time.time(),
    }
    IMPORT_LOCK_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def release_import_lock() -> None:
    IMPORT_LOCK_PATH.unlink(missing_ok=True)


@contextmanager
def import_lock() -> Iterator[dict[str, Any]]:
    payload = acquire_import_lock()
    try:
        yield payload
    finally:
        release_import_lock()


def _sorted_archive_snapshots(prefix: str) -> list[Path]:
    if not DATA_ARCHIVE_DIR.exists():
        return []
    return sorted(
        DATA_ARCHIVE_DIR.glob(f"{prefix}*.parquet"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )


def _enforce_snapshot_retention(prefix: str, retention: int | None = None) -> list[str]:
    limit = ARCHIVE_SNAPSHOT_RETENTION if retention is None else retention
    removed: list[str] = []
    snapshots = _sorted_archive_snapshots(prefix)
    for old in snapshots[limit:]:
        old.unlink(missing_ok=True)
        removed.append(str(old))
    return removed


def archive_canonical_raw_snapshots(
    traffic_canonical: Path,
    aqi_canonical: Path,
    *,
    stamp: str | None = None,
) -> dict[str, str]:
    """
    Copy validated canonical raw parquet into timestamped archive paths.
    Returns paths written; enforces retention policy per dataset prefix.
    """
    if not traffic_canonical.exists() or not aqi_canonical.exists():
        raise ImportGovernanceError("Canonical raw parquet missing; cannot snapshot")

    DATA_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    tag = stamp or _stamp_for_filename()

    traffic_dest = DATA_ARCHIVE_DIR / f"{TRAFFIC_ARCHIVE_PREFIX}{tag}.parquet"
    aqi_dest = DATA_ARCHIVE_DIR / f"{AQI_ARCHIVE_PREFIX}{tag}.parquet"
    shutil.copy2(traffic_canonical, traffic_dest)
    shutil.copy2(aqi_canonical, aqi_dest)

    traffic_removed = _enforce_snapshot_retention(TRAFFIC_ARCHIVE_PREFIX)
    aqi_removed = _enforce_snapshot_retention(AQI_ARCHIVE_PREFIX)

    return {
        "traffic_snapshot": str(traffic_dest.resolve()),
        "aqi_snapshot": str(aqi_dest.resolve()),
        "traffic_snapshots_removed": traffic_removed,
        "aqi_snapshots_removed": aqi_removed,
    }


def write_import_profiles(profile: dict[str, Any], *, stamp: str | None = None) -> dict[str, str]:
    """Persist latest profile and append-only history entry (same payload)."""
    DATA_METADATA_DIR.mkdir(parents=True, exist_ok=True)
    IMPORT_HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    tag = stamp or _stamp_for_filename()
    history_path = IMPORT_HISTORY_DIR / f"import_{tag}.json"
    payload = json.dumps(profile, indent=2, default=str)

    IMPORT_PROFILE_PATH.write_text(payload, encoding="utf-8")
    history_path.write_text(payload, encoding="utf-8")

    return {
        "profile_path": str(IMPORT_PROFILE_PATH.resolve()),
        "history_path": str(history_path.resolve()),
    }
