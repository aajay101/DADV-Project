"""Read-only helpers for dashboard interaction semantics."""

from __future__ import annotations

from collections.abc import Mapping
import sys
from pathlib import Path
from typing import Any, Literal

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from filters.interaction_mode import (
    get_interaction_mode,
    has_active_global_filters,
    has_active_investigation_overlay,
)

DashboardId = Literal["traffic", "aqi"]


def interaction_semantics_snapshot(state: Mapping[str, Any], dashboard: DashboardId) -> dict[str, Any]:
    """Return a read-only interaction semantics snapshot."""

    return {
        "dashboard": dashboard,
        "mode": get_interaction_mode(state, dashboard),
        "global_filters_active": has_active_global_filters(state, dashboard),
        "investigation_overlay_active": has_active_investigation_overlay(state, dashboard),
    }


def chart_can_activate_overlay(state: Mapping[str, Any], dashboard: DashboardId) -> bool:
    """Return whether chart clicks may activate temporary investigation overlays."""

    return get_interaction_mode(state, dashboard) == "baseline"


__all__ = ["DashboardId", "chart_can_activate_overlay", "interaction_semantics_snapshot"]
