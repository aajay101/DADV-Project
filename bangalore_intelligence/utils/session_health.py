"""Session duration and data freshness helpers — pure time logic."""

from __future__ import annotations

import time

from config.data_config import LONG_SESSION_THRESHOLD_SECONDS, STATIC_DATASET_MODE


def check_data_freshness(loaded_at: float | None, threshold_seconds: int) -> bool:
    """Return True when cached data should be marked stale."""
    if STATIC_DATASET_MODE or loaded_at is None:
        return False
    return (time.time() - loaded_at) > threshold_seconds


def should_show_long_session_notice(
    now: float,
    start: float | None,
    dismissed: bool,
    threshold_seconds: int = LONG_SESSION_THRESHOLD_SECONDS,
) -> bool:
    """Return whether the review-session notice should render."""
    if dismissed or start is None:
        return False
    return (now - start) >= threshold_seconds


def elapsed_minutes(start: float | None, now: float | None = None) -> int:
    if start is None:
        return 0
    return int((now or time.time() - start) / 60)
