"""Global filter callbacks and separated cache fingerprints."""

from __future__ import annotations

from typing import Any, Literal

import streamlit as st

from filters.interaction_mode import has_active_global_filters
from filters.transitions import GlobalFilterChanged, dispatch

DashboardId = Literal["traffic", "aqi"]


def data_scope_fingerprint(dashboard: DashboardId) -> str:
    """Stable identity for dataset-scope cache keys."""
    keys = (
        (
            "traffic_date_start",
            "traffic_date_end",
            "traffic_selected_areas",
            "traffic_selected_weather",
            "traffic_selected_roads",
            "traffic_selected_roadwork",
        )
        if dashboard == "traffic"
        else (
            "aqi_date_start",
            "aqi_date_end",
            "aqi_selected_categories",
            "aqi_selected_seasons",
        )
    )
    return "|".join(str(st.session_state.get(k)) for k in keys)


def visual_scope_fingerprint(dashboard: DashboardId) -> str:
    """Stable identity for visual focus and chart-widget state."""
    keys = (
        (
            "traffic_selected_area",
            "traffic_selected_road",
            "traffic_selected_month",
            "traffic_selected_quadrant",
            "traffic_radar_focus_area",
            "traffic_focus_mode",
            "traffic_investigation_scope",
            "chart_selection_epoch",
        )
        if dashboard == "traffic"
        else (
            "aqi_selected_category",
            "aqi_selected_season",
            "aqi_selected_date",
            "aqi_selected_regime",
            "aqi_selected_pollutant",
            "aqi_focus_mode",
            "aqi_investigation_scope",
            "chart_selection_epoch",
        )
    )
    return "|".join(str(st.session_state.get(k)) for k in keys)


def _traffic_filters_active(values: dict[str, Any] | None = None) -> bool:
    state = values or st.session_state
    return has_active_global_filters(state, "traffic")


def _aqi_filters_active(values: dict[str, Any] | None = None) -> bool:
    state = values or st.session_state
    return has_active_global_filters(state, "aqi")


def on_traffic_areas_change(prefix: str) -> None:
    areas = st.session_state.get("traffic_selected_areas") or []
    updates: dict[str, Any] = {"traffic_selected_areas": list(areas)}
    projected = dict(st.session_state)
    projected.update(updates)
    dispatch(
        GlobalFilterChanged(
            dashboard="traffic",
            updates=updates,
            filters_active=_traffic_filters_active(projected),
        )
    )


def on_traffic_weather_change(prefix: str) -> None:
    weather = st.session_state.get("traffic_selected_weather") or []
    updates: dict[str, Any] = {"traffic_selected_weather": list(weather)}
    projected = dict(st.session_state)
    projected.update(updates)
    dispatch(
        GlobalFilterChanged(
            dashboard="traffic",
            updates=updates,
            filters_active=_traffic_filters_active(projected),
        )
    )


def on_traffic_roadwork_change(prefix: str) -> None:
    roadwork = st.session_state.get("traffic_selected_roadwork", "Both")
    updates: dict[str, Any] = {"traffic_selected_roadwork": roadwork}
    projected = dict(st.session_state)
    projected.update(updates)
    dispatch(
        GlobalFilterChanged(
            dashboard="traffic",
            updates=updates,
            filters_active=_traffic_filters_active(projected),
        )
    )


def on_traffic_roads_change(prefix: str) -> None:
    roads = st.session_state.get("traffic_selected_roads") or []
    updates: dict[str, Any] = {"traffic_selected_roads": list(roads)}
    projected = dict(st.session_state)
    projected.update(updates)
    dispatch(
        GlobalFilterChanged(
            dashboard="traffic",
            updates=updates,
            filters_active=_traffic_filters_active(projected),
        )
    )


def on_aqi_categories_change(prefix: str) -> None:
    categories = st.session_state.get("aqi_selected_categories") or []
    updates: dict[str, Any] = {"aqi_selected_categories": list(categories)}
    projected = dict(st.session_state)
    projected.update(updates)
    dispatch(
        GlobalFilterChanged(
            dashboard="aqi",
            updates=updates,
            filters_active=_aqi_filters_active(projected),
        )
    )


def on_aqi_seasons_change(prefix: str) -> None:
    seasons = st.session_state.get("aqi_selected_seasons") or []
    updates: dict[str, Any] = {"aqi_selected_seasons": list(seasons)}
    projected = dict(st.session_state)
    projected.update(updates)
    dispatch(
        GlobalFilterChanged(
            dashboard="aqi",
            updates=updates,
            filters_active=_aqi_filters_active(projected),
        )
    )
