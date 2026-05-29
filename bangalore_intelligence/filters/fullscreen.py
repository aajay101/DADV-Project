"""Fullscreen chart session helpers — one active chart at a time."""

from __future__ import annotations

import streamlit as st

FULLSCREEN_ELIGIBLE = frozenset({"t13_radar", "t02_parcoords", "a15_pairplot", "a02_calendar"})

FULLSCREEN_HEIGHT_VH_RATIO = 0.85
FULLSCREEN_HEIGHT_MIN = 520
FULLSCREEN_HEIGHT_MAX = 900


def is_fullscreen_eligible(fullscreen_key: str | None) -> bool:
    return bool(fullscreen_key and fullscreen_key in FULLSCREEN_ELIGIBLE)


def get_active_fullscreen_key(dashboard: str | None = None) -> str | None:
    key = st.session_state.get("fullscreen_chart_key")
    dash = st.session_state.get("fullscreen_dashboard")
    if not key:
        return None
    if dashboard is not None and dash != dashboard:
        return None
    return key if is_fullscreen_eligible(key) else None


def is_fullscreen_active(fullscreen_key: str | None, dashboard: str) -> bool:
    if not fullscreen_key:
        return False
    return get_active_fullscreen_key(dashboard) == fullscreen_key


def set_fullscreen(fullscreen_key: str, dashboard: str) -> None:
    """Set the single active fullscreen chart key."""
    if not is_fullscreen_eligible(fullscreen_key):
        return
    from filters.transitions import FullscreenChanged, dispatch

    return dispatch(FullscreenChanged(dashboard="traffic" if dashboard == "traffic" else "aqi", fullscreen_key=fullscreen_key))


def clear_fullscreen() -> None:
    """Return page to normal analytical layout."""
    dashboard = st.session_state.get("fullscreen_dashboard") or st.session_state.get("active_dashboard", "traffic")
    from filters.transitions import FullscreenChanged, dispatch

    return dispatch(FullscreenChanged(dashboard="traffic" if dashboard == "traffic" else "aqi", fullscreen_key=None))


def get_fullscreen_height() -> int:
    """Approximate 85vh from cached viewport width."""
    width = int(st.session_state.get("viewport_width", 1280))
    return int(
        max(
            FULLSCREEN_HEIGHT_MIN,
            min(FULLSCREEN_HEIGHT_MAX, width * FULLSCREEN_HEIGHT_VH_RATIO),
        )
    )
