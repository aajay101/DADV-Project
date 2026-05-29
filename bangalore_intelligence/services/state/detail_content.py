"""Detail panel payloads — contextual investigation summaries."""

from __future__ import annotations

from typing import Any

import pandas as pd

from config.data_config import (
    COL_AQI_CATEGORY,
    COL_AREA,
    COL_DATE,
    COL_PM25,
    COL_ROAD,
    COL_SEASON,
)
from data_layer.traffic_transforms import get_road_stats
from filters.interaction import quadrant_label, read_interaction_state


def build_traffic_road_detail(df: pd.DataFrame, road: str | None) -> dict[str, Any] | None:
    if not road or df.empty:
        return None

    stats = get_road_stats(df)
    row = stats[stats[COL_ROAD] == road]
    if row.empty:
        return None

    r = row.iloc[0]
    state = read_interaction_state("traffic")
    quad = quadrant_label(state.get("selected_quadrant"))

    cong = float(r["mean_congestion"])
    cap = float(r["mean_capacity"])
    sev = "critical" if cong >= 90 else ("warning" if cong >= 75 else "neutral")

    return {
        "title": road,
        "dashboard": "traffic",
        "metrics": [
            {"label": "Area", "value": str(r[COL_AREA])},
            {"label": "Congestion", "value": f"{cong:.1f}"},
            {"label": "Capacity", "value": f"{cap:.1f}%"},
            {"label": "Speed", "value": f"{float(r['mean_speed']):.1f} km/h"},
            {"label": "Incidents", "value": f"{int(r['total_incidents'])}"},
            {"label": "Instability", "value": f"{float(r.get('flow_instability_index', 0)):.2f}"},
        ],
        "notes": (
            f"Operational quadrant: {quad}. "
            f"{'Critical overload corridor — capacity near saturation.' if cong >= 90 and cap >= 95 else 'Investigate flow constraints and incident load for remediation priority.'}"
        ),
        "severity": sev,
    }


def build_aqi_day_detail(df: pd.DataFrame) -> dict[str, Any] | None:
    state = read_interaction_state("aqi")
    day = state.get("selected_day")
    if day is None or df.empty:
        year, week = state.get("selected_year"), state.get("selected_week")
        if year is None or week is None:
            return None
        cell = df[(df["year"] == year) & (df["week"] == week)]
        if cell.empty:
            return None
        day = cell.loc[cell[COL_PM25].idxmax(), COL_DATE]

    ts = pd.Timestamp(day)
    day_df = df[df[COL_DATE] == ts]
    if day_df.empty:
        day_df = df[df[COL_DATE].dt.date == ts.date()]
    if day_df.empty:
        return None

    row = day_df.iloc[0]
    pm25 = float(row[COL_PM25])
    cat = str(row.get(COL_AQI_CATEGORY, "—"))
    prev = df[df[COL_DATE] < ts].tail(1)
    transition = "—"
    if not prev.empty:
        transition = f"{prev.iloc[0].get(COL_AQI_CATEGORY, '—')} → {cat}"

    return {
        "title": ts.strftime("%d %b %Y"),
        "dashboard": "aqi",
        "metrics": [
            {"label": "PM2.5", "value": f"{pm25:.1f} µg/m³"},
            {"label": "Category", "value": cat},
            {"label": "Season", "value": str(row.get(COL_SEASON, "—"))},
            {"label": "Week", "value": f"W{int(row.get('week', state.get('selected_week') or 0))}"},
            {"label": "Transition", "value": transition},
        ],
        "notes": (
            f"Calendar investigation · week {state.get('selected_week')} {state.get('selected_year')}. "
            f"{'Spike above Very Poor threshold — review associated visibility and pressure conditions.' if pm25 > 120 else 'Moderate event — compare seasonal baseline in supporting charts.'}"
        ),
        "severity": "critical" if pm25 > 250 else ("warning" if pm25 > 120 else "neutral"),
    }


def build_aqi_regime_detail() -> dict[str, Any] | None:
    state = read_interaction_state("aqi")
    regime = state.get("selected_regime")
    if not regime:
        return None
    return {
        "title": regime,
        "dashboard": "aqi",
        "metrics": [
            {"label": "Regime", "value": regime},
            {"label": "Focus", "value": "Atmospheric state"},
            {"label": "Mode", "value": state.get("focus_mode") or "comparison"},
        ],
        "notes": (
            "Radar comparison focus active — pairplot and regime scatter emphasize "
            "this classification; clear focus to restore full multivariate view."
        ),
        "severity": "warning" if regime == "Stagnation Trap" else "neutral",
    }
