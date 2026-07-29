"""Central display formatting — pure functions, no Streamlit imports."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

import pandas as pd

from config.data_config import (
    CONGESTION_STATES,
    CONGESTION_STATE_BOUNDS,
)

_PLACEHOLDER = "—"

# PM2.5 → AQI category — must match data_layer/cleaners._pm25_to_category bins
_PM25_CATEGORY_BOUNDS = (30, 60, 90, 120, 250)

# Semantic severity tokens used by KPI strips, heroes, and bundles
_SEVERITY_LABELS: dict[str, str] = {
    "critical": "CRITICAL",
    "warning": "WARNING",
    "safe": "SAFE",
    "neutral": "NEUTRAL",
    "info": "INFO",
}


def _is_missing(val: Any) -> bool:
    if val is None:
        return True
    try:
        if pd.isna(val):
            return True
    except (TypeError, ValueError):
        pass
    return False


def _safe_float(val: Any) -> float | None:
    if _is_missing(val):
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def fmt_congestion(val: Any) -> str:
    v = _safe_float(val)
    if v is None:
        return _PLACEHOLDER
    return f"{v:.1f}"


def fmt_speed(val: Any) -> str:
    v = _safe_float(val)
    if v is None:
        return _PLACEHOLDER
    return f"{v:.1f} km/h"


def fmt_pm25(val: Any) -> str:
    v = _safe_float(val)
    if v is None:
        return _PLACEHOLDER
    return f"{v:.1f} µg/m³"


def fmt_pct(val: Any) -> str:
    v = _safe_float(val)
    if v is None:
        return _PLACEHOLDER
    return f"{v:.1f}%"


def fmt_count(val: Any) -> str:
    v = _safe_float(val)
    if v is None:
        return _PLACEHOLDER
    return f"{int(round(v)):,}"


def _to_timestamp(val: Any) -> pd.Timestamp | None:
    if _is_missing(val):
        return None
    try:
        return pd.Timestamp(val)
    except (TypeError, ValueError):
        return None


def fmt_date(val: Any, format: str = "short") -> str:
    """Return a dashboard-safe date label such as 'Jan 2022'."""
    ts = _to_timestamp(val)
    if ts is None or pd.isna(ts):
        return _PLACEHOLDER
    if format == "long":
        return ts.strftime("%B %Y")
    if format == "day":
        return ts.strftime("%d %b %Y")
    return ts.strftime("%b %Y")


def fmt_date_long(val: Any) -> str:
    """Return a long date label such as 'January 2022'."""
    return fmt_date(val, format="long")


def fmt_date_range(start: Any, end: Any) -> str:
    """Return 'Jan 2022 - Aug 2024' for visible filter labels."""
    s = _to_timestamp(start)
    e = _to_timestamp(end)
    if s is None or e is None or pd.isna(s) or pd.isna(e):
        return _PLACEHOLDER
    if s > e:
        return _PLACEHOLDER
    if s.year == e.year and s.month == e.month:
        return fmt_date(s)
    return f"{fmt_date(s)} - {fmt_date(e)}"


def fmt_aqi_category(pm25: float | int | None) -> str:
    """Map PM2.5 value to the platform AQI category label."""
    v = _safe_float(pm25)
    if v is None:
        return _PLACEHOLDER
    if v <= _PM25_CATEGORY_BOUNDS[0]:
        return "Good"
    if v <= _PM25_CATEGORY_BOUNDS[1]:
        return "Satisfactory"
    if v <= _PM25_CATEGORY_BOUNDS[2]:
        return "Moderate"
    if v <= _PM25_CATEGORY_BOUNDS[3]:
        return "Poor"
    if v <= _PM25_CATEGORY_BOUNDS[4]:
        return "Very Poor"
    return "Severe"


def fmt_season(season: str | None) -> str:
    if not season or _is_missing(season):
        return _PLACEHOLDER
    return str(season)


def fmt_congestion_state(congestion: float | int | None) -> str:
    """Map congestion level to operational state label."""
    v = _safe_float(congestion)
    if v is None:
        return _PLACEHOLDER
    for i, bound in enumerate(CONGESTION_STATE_BOUNDS[1:], start=0):
        if v < bound:
            return CONGESTION_STATES[i]
    return CONGESTION_STATES[-1]


def fmt_severity(severity: str | None) -> str:
    """Map semantic severity token to display label (e.g. critical → CRITICAL)."""
    if not severity or _is_missing(severity):
        return _PLACEHOLDER
    key = str(severity).strip().lower()
    if key in _SEVERITY_LABELS:
        return _SEVERITY_LABELS[key]
    upper = str(severity).strip().upper()
    return upper if upper else _PLACEHOLDER


def fmt_temperature(val: Any) -> str:
    v = _safe_float(val)
    if v is None:
        return _PLACEHOLDER
    return f"{v:.1f}°C"


def fmt_temp(val: Any) -> str:
    """Alias for fmt_temperature — kept for existing call sites."""
    return fmt_temperature(val)


def fmt_visibility(val: Any) -> str:
    v = _safe_float(val)
    if v is None:
        return _PLACEHOLDER
    return f"{v:.1f} km"


def fmt_humidity(val: Any) -> str:
    v = _safe_float(val)
    if v is None:
        return _PLACEHOLDER
    return f"{v:.0f}%"


def fmt_pressure(val: Any) -> str:
    v = _safe_float(val)
    if v is None:
        return _PLACEHOLDER
    return f"{v:.1f} hPa"


def fmt_wind(val: Any) -> str:
    v = _safe_float(val)
    if v is None:
        return _PLACEHOLDER
    return f"{v:.1f} m/s"


def fmt_wind_speed(val: Any) -> str:
    """Alias for fmt_wind — architecture spec name."""
    return fmt_wind(val)


def fmt_coords(lat: Any, lon: Any) -> str:
    la, lo = _safe_float(lat), _safe_float(lon)
    if la is None or lo is None:
        return _PLACEHOLDER
    return f"{la:.4f}, {lo:.4f}"


def fmt_coordinate(lat: Any, lon: Any) -> str:
    """Bangalore-oriented coordinate label for map and geo tooltips."""
    la, lo = _safe_float(lat), _safe_float(lon)
    if la is None or lo is None:
        return _PLACEHOLDER
    lat_hem = "N" if la >= 0 else "S"
    lon_hem = "E" if lo >= 0 else "W"
    return f"{abs(la):.2f}°{lat_hem}, {abs(lo):.2f}°{lon_hem}"


def fmt_ci(low: Any, high: Any, unit: str = "") -> str:
    return fmt_confidence_interval(low, high, unit=unit)


def fmt_confidence_interval(low: Any, high: Any, unit: str = "") -> str:
    lo, hi = _safe_float(low), _safe_float(high)
    if lo is None or hi is None:
        return _PLACEHOLDER
    text = f"{lo:.1f}–{hi:.1f}"
    unit = (unit or "").strip()
    return f"{text} {unit}".strip() if unit else text


def fmt_model_version(version: str | None) -> str:
    if not version or _is_missing(version):
        return _PLACEHOLDER
    v = str(version).strip()
    if v.lower().startswith("v"):
        return v
    return f"v{v}"


# --- Plotly hover fragments (d3-format; keep precision aligned with fmt_* above) ---


def hover_congestion(field: str = "y") -> str:
    return f"Congestion %{{{field}:.1f}}"


def hover_pm25(field: str = "y") -> str:
    return f"PM2.5 %{{{field}:.1f}} µg/m³"


def hover_speed(field: str = "y") -> str:
    return f"Speed %{{{field}:.1f}} km/h"


def hover_temperature(field: str = "x") -> str:
    return f"Tm %{{{field}:.1f}}°C"


def hover_pct(field: str = "y") -> str:
    return f"%{{{field}:.1f}}%"


def hover_z_congestion() -> str:
    return "Congestion %{z:.1f}"


def hover_z_pm25() -> str:
    return "Mean PM2.5 %{z:.1f} µg/m³"


def hover_count(field: str = "y") -> str:
    return f"Count %{{{field}:.0f}}"


def hover_incidents(field: str = "y") -> str:
    return f"Incidents %{{{field}:.1f}}"


def hover_mobility_penalty(field: str = "x") -> str:
    return f"Mobility penalty %{{{field}:+.1f}} vs baseline"


def hover_radar_theta_r() -> str:
    return "%{theta}: %{r:.0f}"


def hover_correlation() -> str:
    return "r = %{z:.2f}"


def hover_pairplot_scatter() -> str:
    return "%{x:.2f} · %{y:.2f}"


def hover_pm25_axis(field: str = "x") -> str:
    return f"PM2.5 %{{{field}:.0f}} µg/m³"


def hover_days_count() -> str:
    return "Days: %{y}"


def hover_category_transition() -> str:
    return "From %{y} → %{x}<br>Days %{z}"


def hover_density_hex() -> str:
    return "Volume %{x}<br>Congestion %{y}<br>Count %{z}"


def hover_template(*lines: str, extra: bool = True) -> str:
    """Join hover lines and append Plotly's empty trace name suppression."""
    body = "<br>".join(lines)
    return f"{body}<extra></extra>" if extra else body


def fmt_export_timestamp() -> str:
    """Return a formatted timestamp for export footers."""
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def fmt_filter_summary(filters: Mapping[str, Any], dashboard: str = "traffic") -> str:
    """Return a reproducible summary of active date, area, road, category, and season filters."""
    parts: list[str] = []

    if dashboard == "traffic":
        start = filters.get("traffic_date_start")
        end = filters.get("traffic_date_end")
        areas = filters.get("traffic_selected_areas") or []
        weather = filters.get("traffic_selected_weather") or []
        roadwork = filters.get("traffic_selected_roadwork", "Both")
        roads = filters.get("traffic_selected_roads") or []
        date_label = fmt_date_range(start, end)
        if date_label != _PLACEHOLDER:
            parts.append(f"Dates: {date_label}")
        if areas:
            area_str = ", ".join(areas[:4])
            if len(areas) > 4:
                area_str += f" (+{len(areas) - 4} more)"
            parts.append(f"Areas: {area_str}")
        else:
            parts.append("Areas: All")
        if weather:
            parts.append(f"Weather: {', '.join(weather)}")
        else:
            parts.append("Weather: All")
        parts.append(f"Roadwork: {roadwork}")
        if roads:
            road_str = ", ".join(roads[:4])
            if len(roads) > 4:
                road_str += f" (+{len(roads) - 4} more)"
            parts.append(f"Roads: {road_str}")
        else:
            parts.append("Roads: All")
    else:
        start = filters.get("aqi_date_start")
        end = filters.get("aqi_date_end")
        categories = filters.get("aqi_selected_categories") or []
        seasons = filters.get("aqi_selected_seasons") or []
        date_label = fmt_date_range(start, end)
        if date_label != _PLACEHOLDER:
            parts.append(f"Dates: {date_label}")
        if categories:
            parts.append(f"Categories: {', '.join(categories)}")
        else:
            parts.append("Categories: All")
        if seasons:
            parts.append(f"Seasons: {', '.join(seasons)}")
        else:
            parts.append("Seasons: All")

    return " | ".join(parts) if parts else "No active filters"


def filter_snapshot_from_state(state: Mapping[str, Any], dashboard: str) -> dict[str, Any]:
    """Extract filter-relevant keys from session state for formatter use."""
    if dashboard == "traffic":
        return {
            "traffic_date_start": state.get("traffic_date_start"),
            "traffic_date_end": state.get("traffic_date_end"),
            "traffic_selected_areas": state.get("traffic_selected_areas", []),
            "traffic_selected_weather": state.get("traffic_selected_weather", []),
            "traffic_selected_roadwork": state.get(
                "traffic_selected_roadwork", "Both"
            ),
            "traffic_selected_roads": state.get("traffic_selected_roads", []),
        }
    return {
        "aqi_date_start": state.get("aqi_date_start"),
        "aqi_date_end": state.get("aqi_date_end"),
        "aqi_selected_categories": state.get("aqi_selected_categories", []),
        "aqi_selected_seasons": state.get("aqi_selected_seasons", []),
    }
