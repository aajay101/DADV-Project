"""Normalized Plotly selection → investigation state. Charts emit intent; handlers apply focus."""

from __future__ import annotations

from typing import Any

import streamlit as st

from config.data_config import COL_AREA, COL_ROAD, TRAFFIC_AREAS
from filters.interaction import (
    apply_interaction_payload,
    clear_investigation,
    read_interaction_state,
)

ChartMeta = dict[str, Any]


def _first_point(selection: Any) -> dict | None:
    if selection is None:
        return None
    points = getattr(selection, "points", None) or []
    if not points:
        return None
    pt = points[0]
    if isinstance(pt, dict):
        return pt
    return dict(pt) if hasattr(pt, "items") else None


def _point_label(point: dict) -> str | None:
    for key in ("label", "text", "y"):
        val = point.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None


def _quadrant_from_xy(x: float, y: float, x_mid: float = 75.0, y_mid: float = 75.0) -> str:
    if y >= y_mid and x >= x_mid:
        return "critical_overload"
    if y >= y_mid:
        return "constrained_flow"
    if x >= x_mid:
        return "capacity_margin"
    return "baseline"


def _area_from_point(point: dict) -> str | None:
    label = _point_label(point)
    if label and label in TRAFFIC_AREAS:
        return label
    y = point.get("y")
    if isinstance(y, str) and y in TRAFFIC_AREAS:
        return y
    return None


def _toggle_same_traffic_area(area: str) -> bool:
    state = read_interaction_state("traffic")
    return (
        state.get("selected_area") == area
        and not state.get("selected_road")
        and not state.get("selected_month")
    )


def _toggle_same_traffic_road(road: str) -> bool:
    state = read_interaction_state("traffic")
    return state.get("selected_road") == road


def _toggle_same_area_month(area: str, month: str) -> bool:
    state = read_interaction_state("traffic")
    return state.get("selected_area") == area and state.get("selected_month") == month


def _toggle_same_aqi_day(year: int, week: int) -> bool:
    state = read_interaction_state("aqi")
    return state.get("selected_year") == year and state.get("selected_week") == week


def handle_t01(point: dict, meta: ChartMeta) -> dict:
    area = _area_from_point(point)
    if not area:
        return {}
    if _toggle_same_traffic_area(area):
        clear_investigation("traffic")
        return {"cleared": True}
    return {
        "chart": "T-01",
        "selected_area": area,
        "selected_road": None,
        "selected_month": None,
        "focus_mode": "area_ranking",
    }


def handle_t05(point: dict, meta: ChartMeta) -> dict:
    road = (
        point.get("text")
        or _point_label(point)
        or meta.get("roads_by_index", {}).get(point.get("point_index"))
    )
    if not road:
        return {}
    try:
        x = float(point.get("x", 0))
        y = float(point.get("y", 0))
    except (TypeError, ValueError):
        x, y = 75.0, 75.0
    area = None
    custom = point.get("customdata")
    if isinstance(custom, (list, tuple)) and custom:
        area = custom[0]
    roads_df = meta.get("roads_df")
    if roads_df is not None and not roads_df.empty and COL_ROAD in roads_df.columns:
        match = roads_df[roads_df[COL_ROAD] == road]
        if not match.empty:
            area = match.iloc[0][COL_AREA]
    if _toggle_same_traffic_road(road):
        clear_investigation("traffic")
        return {"cleared": True}
    return {
        "chart": "T-05",
        "selected_road": road,
        "selected_area": area,
        "selected_month": None,
        "selected_quadrant": _quadrant_from_xy(x, y),
        "focus_mode": "road_investigation",
    }


def handle_t06(point: dict, meta: ChartMeta) -> dict:
    label = _point_label(point)
    if not label:
        return {}
    parent = point.get("parent")
    if parent and str(parent) != label:
        if _toggle_same_traffic_road(str(label)):
            clear_investigation("traffic")
            return {"cleared": True}
        return {
            "chart": "T-06",
            "selected_road": str(label),
            "selected_area": str(parent),
            "focus_mode": "burden_hierarchy",
        }
    if read_interaction_state("traffic").get("selected_area") == str(label):
        clear_investigation("traffic")
        return {"cleared": True}
    return {
        "chart": "T-06",
        "selected_area": str(label),
        "selected_road": None,
        "focus_mode": "area_burden",
    }


def handle_t07(point: dict, meta: ChartMeta) -> dict:
    road = _point_label(point)
    if not road:
        return {}
    if _toggle_same_traffic_road(road):
        clear_investigation("traffic")
        return {"cleared": True}
    return {"chart": "T-07", "selected_road": road, "focus_mode": "mobility_penalty"}


def handle_t13(point: dict, meta: ChartMeta) -> dict:
    area = point.get("y")
    if isinstance(area, str) and area in TRAFFIC_AREAS:
        state = read_interaction_state("traffic")
        if state.get("selected_area") == area and not state.get("selected_road"):
            clear_investigation("traffic")
            return {"cleared": True}
        return {
            "chart": "T-13",
            "selected_area": area,
            "selected_road": None,
            "focus_entity": area,
            "focus_mode": "area_stress_heatmap",
        }

    curve = point.get("curve_number", point.get("curveNumber"))
    areas = meta.get("radar_areas") or []
    if curve is None or curve >= len(areas):
        return {}
    area = areas[int(curve)]
    state = read_interaction_state("traffic")
    if state.get("focus_entity") == area:
        clear_investigation("traffic")
        return {"cleared": True}
    return {
        "chart": "T-13",
        "selected_area": area,
        "focus_entity": area,
        "focus_mode": "radar_comparison",
    }


def handle_t15(point: dict, meta: ChartMeta) -> dict:
    area = point.get("y")
    month = point.get("x")
    if isinstance(area, (int, float)):
        area = None
    if area is not None:
        area = str(area)
    if month is not None:
        month = str(month)
    if not area or area not in TRAFFIC_AREAS or not month:
        return {}
    if _toggle_same_area_month(area, month):
        clear_investigation("traffic")
        return {"cleared": True}
    return {
        "chart": "T-15",
        "selected_area": area,
        "selected_month": month,
        "selected_road": None,
        "focus_mode": "area_month",
    }


def handle_t02(point: dict, meta: ChartMeta) -> dict:
    curve = point.get("curve_number", point.get("curveNumber"))
    areas = meta.get("parcoords_areas") or []
    if curve is None or curve >= len(areas):
        return {}
    area = areas[int(curve)]
    state = read_interaction_state("traffic")
    if state.get("selected_area") == area and not state.get("selected_road"):
        clear_investigation("traffic")
        return {"cleared": True}
    return {
        "chart": "T-02",
        "selected_area": area,
        "selected_road": None,
        "focus_mode": "multivariate_profile",
    }


def handle_a02(point: dict, meta: ChartMeta) -> dict:
    try:
        year = int(float(point.get("y", 0)))
        week = int(float(point.get("x", 0)))
    except (TypeError, ValueError):
        return {}
    if _toggle_same_aqi_day(year, week):
        clear_investigation("aqi")
        return {"cleared": True}
    cal = meta.get("calendar_df")
    selected_date = None
    category = None
    pm25 = None
    if cal is not None and not cal.empty:
        from config.data_config import COL_DATE, COL_PM25, COL_AQI_CATEGORY

        cell = cal[(cal["year"] == year) & (cal["week"] == week)]
        if not cell.empty:
            peak = cell.loc[cell[COL_PM25].idxmax()]
            selected_date = peak[COL_DATE]
            category = peak.get(COL_AQI_CATEGORY)
            pm25 = float(peak[COL_PM25])
    return {
        "chart": "A-02",
        "selected_year": year,
        "selected_week": week,
        "selected_day": selected_date,
        "selected_category": category,
        "selected_pollutant": "PM2.5",
        "focus_mode": "calendar_event",
        "context_pm25": pm25,
    }


def handle_a13(point: dict, meta: ChartMeta) -> dict:
    curve = point.get("curve_number", point.get("curveNumber"))
    regimes = meta.get("regime_order") or []
    if curve is None or curve >= len(regimes):
        return {}
    regime = regimes[int(curve)]
    state = read_interaction_state("aqi")
    if state.get("selected_regime") == regime:
        clear_investigation("aqi")
        return {"cleared": True}
    return {
        "chart": "A-13",
        "selected_regime": regime,
        "focus_mode": "atmospheric_regime",
    }


def handle_a15(point: dict, meta: ChartMeta) -> dict:
    label = point.get("x") or point.get("y")
    if label is None:
        return {}
    pollutant = str(label).replace(" ", "_").upper()
    mapping = {
        "T": "T",
        "TM": "Tm",
        "SLP": "SLP",
        "H": "H",
        "VV": "VV",
        "V": "V",
        "PM2.5": "PM2.5",
    }
    for key, col in mapping.items():
        if key in str(label).upper().replace(".", ""):
            pollutant = col
            break
    return {
        "chart": "A-15",
        "selected_pollutant": pollutant if pollutant != "PM25" else "PM2.5",
        "focus_mode": "pairplot_axis",
    }


HANDLERS = {
    "T-01": handle_t01,
    "T-05": handle_t05,
    "T-06": handle_t06,
    "T-07": handle_t07,
    "T-13": handle_t13,
    "T-15": handle_t15,
    "T-02": handle_t02,
    "A-02": handle_a02,
    "A-13": handle_a13,
    "A-15": handle_a15,
}


def dispatch_chart_selection(
    chart_id: str,
    plotly_state: Any,
    meta: ChartMeta | None = None,
) -> bool:
    """Apply normalized payload from Plotly selection; return True if state changed."""
    meta = meta or {}
    point = _first_point(getattr(plotly_state, "selection", None))
    if not point:
        return False

    handler = HANDLERS.get(chart_id)
    if not handler:
        return False

    payload = handler(point, meta)
    if not payload:
        return False
    if payload.pop("cleared", False):
        return True
    dashboard = "traffic" if chart_id.startswith("T-") else "aqi"
    from filters.interaction_mode import get_interaction_mode

    if get_interaction_mode(st.session_state, dashboard) == "global_filter_mode":
        from filters.observability import RuntimeObservabilityManager

        RuntimeObservabilityManager.emit(
            "transition",
            source="dispatch_chart_selection",
            message="Investigation overlay activation blocked while global filters are active",
            severity="warning",
            payload={"dashboard": dashboard, "chart_id": chart_id},
        )
    apply_interaction_payload(dashboard, payload)
    return True
