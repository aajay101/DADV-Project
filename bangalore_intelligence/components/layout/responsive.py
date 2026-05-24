"""Responsive column and height helpers — breakpoint-aware public API."""

from __future__ import annotations

from typing import Literal

import streamlit as st

from config.chart_defaults import chart_size_for, resolve_chart_height
from config.layout import (
    BREAKPOINT_DESKTOP,
    BREAKPOINT_LAPTOP,
    BREAKPOINT_TABLET,
    BREAKPOINT_ULTRAWIDE,
    COLUMNS_EQUAL,
    COLUMNS_FULL,
    COLUMNS_HERO_SUPPORT,
)

Breakpoint = Literal["compact", "tablet", "laptop", "desktop", "ultrawide"]


def get_breakpoint(width: int | None) -> Breakpoint:
    """Classify viewport width according to SUAQIS breakpoints."""
    w = width if width is not None else get_viewport_width()
    if w < BREAKPOINT_TABLET:
        return "compact"
    if w < BREAKPOINT_LAPTOP:
        return "tablet"
    if w < BREAKPOINT_DESKTOP:
        return "laptop"
    if w < BREAKPOINT_ULTRAWIDE:
        return "desktop"
    return "ultrawide"


def is_compact(width: int | None = None) -> bool:
    return get_breakpoint(width) == "compact"


def get_viewport_width() -> int:
    """Read cached viewport width from session (desktop default if unset)."""
    return int(st.session_state.get("viewport_width", 1280))


def get_active_breakpoint() -> Breakpoint:
    stored = st.session_state.get("viewport_breakpoint")
    if stored in ("compact", "tablet", "laptop", "desktop", "ultrawide"):
        return stored  # type: ignore[return-value]
    return get_breakpoint(get_viewport_width())


def get_column_split(layout: str = "hero_support", width: int | None = None) -> list[int]:
    """Return st.columns ratio list for layout mode after breakpoint decisions."""
    bp = get_breakpoint(width)
    if layout == "equal":
        if bp in ("compact", "tablet"):
            return COLUMNS_FULL
        return COLUMNS_EQUAL
    if layout == "full":
        return COLUMNS_FULL
    if bp in ("compact", "tablet"):
        return COLUMNS_FULL
    if bp == "laptop" and layout == "hero_support":
        return [1, 1]
    return COLUMNS_HERO_SUPPORT


def get_chart_heights(
    role: str = "hero",
    width: int | None = None,
    *,
    chart_size: str | None = None,
    chart_id: str | None = None,
    is_fullscreen: bool = False,
) -> int:
    """Breakpoint-aware heights from CHART_SIZES only."""
    bp = get_breakpoint(width)
    size_key = chart_size or chart_size_for(chart_id, role)
    return resolve_chart_height(
        size_key,
        role=role,
        chart_id=chart_id,
        breakpoint=bp,
        is_fullscreen=is_fullscreen,
    )


def should_hide_kpi_gauges(width: int | None = None) -> bool:
    """Laptop and below: hide gauge rings to preserve KPI density."""
    return get_breakpoint(width) in ("laptop", "tablet", "compact")


def should_collapse_secondary_kpis(width: int | None = None) -> bool:
    """Laptop and below: omit secondary KPI row."""
    return get_breakpoint(width) in ("laptop", "tablet", "compact")


def should_show_compact_filter_warning(width: int | None = None) -> bool:
    return get_breakpoint(width) == "compact"


def should_recommend_fullscreen(width: int | None = None, threshold: int = 1200) -> bool:
    return get_viewport_width() if width is None else int(width) < threshold


def should_collapse_chart(chart_id: str, width: int | None = None) -> bool:
    """Return whether chart should move behind progressive disclosure."""
    bp = get_breakpoint(width)
    if bp in ("compact", "tablet"):
        return chart_id in (
            "t12_weather",
            "t11_ridgeline",
            "t13_heatmap",
            "t02_parcoords",
            "a14_season_grid",
        )
    if bp == "laptop":
        return chart_id in ("t12_weather",)
    return False
