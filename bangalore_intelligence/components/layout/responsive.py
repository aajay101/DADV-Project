"""Responsive column and height helpers — desktop-first."""

from config.layout import (
    BREAKPOINT_LAPTOP,
    CHART_HEIGHT_COMPACT,
    CHART_HEIGHT_HERO,
    CHART_HEIGHT_SUPPORT,
    COLUMNS_EQUAL,
    COLUMNS_FULL,
    COLUMNS_HERO_SUPPORT,
)


def get_column_split(layout: str = "hero_support") -> list:
    """Return st.columns ratio list for layout mode."""
    if layout == "equal":
        return COLUMNS_EQUAL
    if layout == "full":
        return COLUMNS_FULL
    return COLUMNS_HERO_SUPPORT


def get_chart_heights(role: str = "hero") -> int:
    """Desktop baseline heights; laptop stacks in page template."""
    if role == "hero":
        return CHART_HEIGHT_HERO
    if role == "support":
        return CHART_HEIGHT_SUPPORT
    return CHART_HEIGHT_COMPACT
