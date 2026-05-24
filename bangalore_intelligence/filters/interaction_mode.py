"""Strict analytical interaction mode governance."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal, Mapping

from filters.state import AQI_STATE_DEFAULTS, TRAFFIC_STATE_DEFAULTS

DashboardId = Literal["traffic", "aqi"]
InteractionMode = Literal["baseline", "global_filter_mode", "investigation_mode"]

BASELINE_CANONICAL_SCOPE: dict[DashboardId, dict[str, Any]] = {
    "traffic": {
        "traffic_date_start": TRAFFIC_STATE_DEFAULTS["traffic_date_start"],
        "traffic_date_end": TRAFFIC_STATE_DEFAULTS["traffic_date_end"],
        "traffic_selected_areas": TRAFFIC_STATE_DEFAULTS["traffic_selected_areas"],
        "traffic_selected_weather": TRAFFIC_STATE_DEFAULTS["traffic_selected_weather"],
        "traffic_selected_roadwork": TRAFFIC_STATE_DEFAULTS["traffic_selected_roadwork"],
        "traffic_selected_roads": TRAFFIC_STATE_DEFAULTS["traffic_selected_roads"],
    },
    "aqi": {
        "aqi_date_start": AQI_STATE_DEFAULTS["aqi_date_start"],
        "aqi_date_end": AQI_STATE_DEFAULTS["aqi_date_end"],
        "aqi_selected_categories": AQI_STATE_DEFAULTS["aqi_selected_categories"],
        "aqi_selected_seasons": AQI_STATE_DEFAULTS["aqi_selected_seasons"],
    },
}


def has_active_global_filters(state: Mapping[str, Any], dashboard: DashboardId | None = None) -> bool:
    """Return true only for canonical persistent filter state."""
    if dashboard in (None, "traffic") and canonical_filters_active(state, "traffic"):
        return True
    if dashboard in (None, "aqi") and canonical_filters_active(state, "aqi"):
        return True
    return False


def canonical_filters_active(state: Mapping[str, Any], dashboard: DashboardId) -> bool:
    """Return true only when canonical filter values differ from baseline scope."""
    baseline = BASELINE_CANONICAL_SCOPE[dashboard]
    return any(not is_baseline_filter_value(state.get(key), default) for key, default in baseline.items())


def normalize_canonical_value(value: Any) -> Any:
    """Normalize widget/reducer values before canonical filter comparison."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if hasattr(value, "to_pydatetime"):
        try:
            converted = value.to_pydatetime()
        except Exception:
            converted = None
        if isinstance(converted, datetime):
            return converted.date()
    if isinstance(value, list):
        return [normalize_canonical_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(normalize_canonical_value(item) for item in value)
    return value


def is_baseline_filter_value(current: Any, baseline: Any) -> bool:
    """Compare canonical filter values by analytical meaning, not object type."""
    return normalize_canonical_value(current) == normalize_canonical_value(baseline)


def has_active_investigation_overlay(state: Mapping[str, Any], dashboard: DashboardId | None = None) -> bool:
    """Return true when temporary drilldown overlay scope contains analytical scope."""
    if dashboard in (None, "traffic") and _scope_active(
        state.get("traffic_investigation_scope"),
        ("area", "road", "month"),
    ):
        return True
    if dashboard in (None, "aqi") and _scope_active(
        state.get("aqi_investigation_scope"),
        ("season", "category", "date", "year", "week", "regime", "pollutant"),
    ):
        return True
    return False


def get_interaction_mode(state: Mapping[str, Any], dashboard: DashboardId | None = None) -> InteractionMode:
    """Resolve the current strict analytical authority mode."""
    if has_active_investigation_overlay(state, dashboard):
        return "investigation_mode"
    if has_active_global_filters(state, dashboard):
        return "global_filter_mode"
    return "baseline"


def assert_valid_interaction_mode(state: Mapping[str, Any], dashboard: DashboardId | None = None) -> None:
    """Fail if persistent global filters and temporary overlay scope coexist."""
    if has_active_global_filters(state, dashboard) and has_active_investigation_overlay(state, dashboard):
        scope = dashboard or "any"
        raise RuntimeError(f"Invalid interaction mode for {scope}: global filters and investigation overlay both active")


def interaction_mode_snapshot(state: Mapping[str, Any], dashboard: DashboardId) -> dict[str, Any]:
    """Serializable mode inspection payload for traces and debug panels."""
    return {
        "dashboard": dashboard,
        "mode": get_interaction_mode(state, dashboard),
        "global_filters_active": has_active_global_filters(state, dashboard),
        "investigation_overlay_active": has_active_investigation_overlay(state, dashboard),
    }


def _scope_active(scope: Any, keys: tuple[str, ...]) -> bool:
    if not isinstance(scope, Mapping):
        return False
    return any(_truthy_scope_value(scope.get(key)) for key in keys)


def _truthy_scope_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True

