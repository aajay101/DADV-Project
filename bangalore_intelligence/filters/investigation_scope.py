"""Investigation overlay scope composition for chart data projections."""

from __future__ import annotations

from typing import Any, Literal

import pandas as pd

from config.data_config import COL_AREA, COL_AQI_CATEGORY, COL_DATE, COL_ROAD, COL_SEASON
from filters.performance import chart_dependency_spec

DashboardId = Literal["traffic", "aqi"]


def build_effective_traffic_scope(state: dict[str, Any], chart_id: str | None) -> dict[str, Any]:
    """Return the temporary traffic overlay scope for a participating chart."""
    if not _participates(chart_id, "traffic"):
        return {}
    scope = state.get("traffic_investigation_scope") or {}
    return {
        "area": scope.get("area"),
        "road": scope.get("road"),
        "month": scope.get("month"),
        "source_chart": scope.get("source_chart"),
        "focus_mode": scope.get("focus_mode"),
    }


def build_effective_aqi_scope(state: dict[str, Any], chart_id: str | None) -> dict[str, Any]:
    """Return the temporary AQI overlay scope for a participating chart."""
    if not _participates(chart_id, "aqi"):
        return {}
    scope = state.get("aqi_investigation_scope") or {}
    return {
        "season": scope.get("season"),
        "category": scope.get("category"),
        "date": scope.get("date"),
        "year": scope.get("year"),
        "week": scope.get("week"),
        "regime": scope.get("regime"),
        "source_chart": scope.get("source_chart"),
        "focus_mode": scope.get("focus_mode"),
    }


def apply_investigation_overlay_scope(
    df: pd.DataFrame,
    dashboard: DashboardId,
    chart_id: str | None,
    state: dict[str, Any],
) -> pd.DataFrame:
    """Apply temporary investigation overlay scope without touching global filters."""
    if df.empty or not _participates(chart_id, dashboard):
        return df
    if dashboard == "traffic":
        return _apply_traffic_overlay(df, build_effective_traffic_scope(state, chart_id))
    return _apply_aqi_overlay(df, build_effective_aqi_scope(state, chart_id))


def _participates(chart_id: str | None, dashboard: DashboardId) -> bool:
    spec = chart_dependency_spec(chart_id, dashboard)
    return bool(spec.depends_on_investigation_overlay)


def _apply_traffic_overlay(df: pd.DataFrame, scope: dict[str, Any]) -> pd.DataFrame:
    out = df
    road = scope.get("road")
    area = scope.get("area")
    month = scope.get("month")
    if road and COL_ROAD in out.columns:
        out = out[out[COL_ROAD] == road]
    elif area and COL_AREA in out.columns:
        out = out[out[COL_AREA] == area]
    if month and COL_DATE in out.columns:
        month_period = _month_period(month)
        if month_period is not None:
            out = out[pd.to_datetime(out[COL_DATE], errors="coerce").dt.to_period("M") == month_period]
    return out


def _apply_aqi_overlay(df: pd.DataFrame, scope: dict[str, Any]) -> pd.DataFrame:
    out = df
    category = scope.get("category")
    season = scope.get("season")
    selected_date = scope.get("date")
    year = scope.get("year")
    week = scope.get("week")
    if category and COL_AQI_CATEGORY in out.columns:
        out = out[out[COL_AQI_CATEGORY] == category]
    if season and COL_SEASON in out.columns:
        out = out[out[COL_SEASON] == season]
    if selected_date and COL_DATE in out.columns:
        selected = pd.Timestamp(selected_date).normalize()
        dates = pd.to_datetime(out[COL_DATE], errors="coerce").dt.normalize()
        out = out[dates == selected]
    elif year is not None and week is not None and COL_DATE in out.columns:
        dates = pd.to_datetime(out[COL_DATE], errors="coerce")
        iso = dates.dt.isocalendar()
        out = out[(iso.year == int(year)) & (iso.week == int(week))]
    return out


def _month_period(value: Any) -> pd.Period | None:
    try:
        return pd.Period(value, freq="M")
    except Exception:
        try:
            return pd.Timestamp(value).to_period("M")
        except Exception:
            return None
