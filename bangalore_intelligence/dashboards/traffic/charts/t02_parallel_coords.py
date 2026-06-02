"""T-02 - Area traffic profile bars."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
import plotly.graph_objects as go

from utils.plotly_engine import apply_dashboard_theme, empty_figure


@dataclass(frozen=True)
class MetricSpec:
    field: str
    label: str
    higher_is: str
    suffix: str = ""
    candidates: tuple[str, ...] = ()


METRICS: tuple[MetricSpec, ...] = (
    MetricSpec("congestion_index", "Traffic Level", "bad", candidates=("Congestion", "congestion")),
    MetricSpec("avg_speed", "Average Speed", "good", " km/h", candidates=("Speed", "speed")),
    MetricSpec("incident_count", "Incidents", "bad", candidates=("Incidents", "incidents")),
    MetricSpec("capacity_utilization", "Road Usage", "bad", "%", candidates=("Capacity", "capacity")),
    MetricSpec("pedestrian_exposure", "Walking Activity", "context", candidates=("Pedestrian", "pedestrian")),
    MetricSpec("public_transport_usage", "Public Transport", "good", "%", candidates=("PT Usage", "pt_usage")),
    MetricSpec("signal_compliance", "Signal Compliance", "good", "%", candidates=("Signal", "signal")),
    MetricSpec("traffic_volume", "Traffic Volume", "bad", candidates=("Traffic Vol", "traffic_vol")),
)

AREA_CANDIDATES = ("area", "Area", "area_name", "Area Name", "location", "Location")
EXCLUDED_NUMERIC_COLUMNS = {
    "year",
    "month",
    "day",
    "date",
    "latitude",
    "longitude",
    "lat",
    "lon",
    "lng",
}
UI_LABEL_BY_COLUMN = {
    "congestion": "Traffic Level",
    "congestion_index": "Traffic Level",
    "mean_congestion": "Traffic Level",
    "mean_congestion_index": "Traffic Level",
    "speed": "Average Speed",
    "avg_speed": "Average Speed",
    "average_speed": "Average Speed",
    "mean_speed": "Average Speed",
    "incidents": "Incidents",
    "incident_count": "Incidents",
    "total_incidents": "Incidents",
    "capacity": "Road Usage",
    "capacity_utilization": "Road Usage",
    "mean_capacity": "Road Usage",
    "pedestrian": "Walking Activity",
    "pedestrian_exposure": "Walking Activity",
    "mean_pedestrian": "Walking Activity",
    "pt_usage": "Public Transport",
    "public_transport_usage": "Public Transport",
    "mean_pt_usage": "Public Transport",
    "signal": "Signal Compliance",
    "signal_compliance": "Signal Compliance",
    "mean_signal": "Signal Compliance",
    "traffic_vol": "Traffic Volume",
    "traffic_volume": "Traffic Volume",
    "record_count": "Traffic Volume",
}
BAR_COLORS = {
    "Traffic Level": "#FFBA08",
    "Average Speed": "#58A6FF",
    "Incidents": "#E5383B",
    "Road Usage": "#F97316",
    "Walking Activity": "#AEB6C2",
    "Public Transport": "#2EC4B6",
    "Signal Compliance": "#10B981",
    "Traffic Volume": "#8B5CF6",
}
STATUS_BADGES = {
    "Low": ("rgba(80,140,255,0.15)", "#7AA8FF"),
    "Moderate": ("rgba(255,190,60,0.15)", "#FFC13C"),
    "High": ("rgba(255,140,0,0.15)", "#FF9D00"),
    "Critical": ("rgba(255,80,80,0.15)", "#FF5555"),
}
BAR_REGION_MAX = 64.0
VALUE_X = 77.0
STATUS_X = 91.0


def _first_existing_column(data: pd.DataFrame, candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        if candidate in data.columns:
            return candidate
    return None


def _column_key(column: str) -> str:
    return str(column).strip().lower().replace(" ", "_").replace("-", "_")


def _metric_column(data: pd.DataFrame, spec: MetricSpec) -> str | None:
    return _first_existing_column(data, (spec.field, *spec.candidates))


def _spec_for_numeric_column(column: str) -> MetricSpec:
    key = _column_key(column)
    label = UI_LABEL_BY_COLUMN.get(key, str(column).replace("_", " ").title())
    if key in {
        "avg_speed",
        "speed",
        "average_speed",
        "mean_speed",
        "public_transport_usage",
        "pt_usage",
        "mean_pt_usage",
        "signal",
        "signal_compliance",
        "mean_signal",
    }:
        direction = "good"
    elif key in {"pedestrian", "pedestrian_exposure", "mean_pedestrian", "walking_activity"}:
        direction = "context"
    else:
        direction = "bad"
    if key in {
        "capacity",
        "capacity_utilization",
        "mean_capacity",
        "pt_usage",
        "public_transport_usage",
        "mean_pt_usage",
        "signal",
        "signal_compliance",
        "mean_signal",
    }:
        suffix = "%"
    elif key in {"avg_speed", "speed", "average_speed", "mean_speed"}:
        suffix = " km/h"
    else:
        suffix = ""
    return MetricSpec(key, label, direction, suffix, candidates=(column,))


def _fallback_metric_specs(data: pd.DataFrame, area_col: str) -> tuple[MetricSpec, ...]:
    specs: list[MetricSpec] = []
    for column in data.columns:
        key = _column_key(column)
        if column == area_col or key in EXCLUDED_NUMERIC_COLUMNS:
            continue
        values = pd.to_numeric(data[column], errors="coerce")
        if pd.api.types.is_numeric_dtype(data[column]) or values.notna().any():
            specs.append(_spec_for_numeric_column(str(column)))
    return tuple(specs[:8])


def _area_column(data: pd.DataFrame) -> str | None:
    column = _first_existing_column(data, AREA_CANDIDATES)
    if column:
        return column
    if data.index.name and data.index.name.lower() in {"area", "area_name", "location"}:
        return data.index.name
    return None


def _normalize(value: float, low: float, high: float) -> float:
    if pd.isna(value):
        return 0.0
    if high <= low:
        return 50.0
    return max(0.0, min(100.0, ((value - low) / (high - low)) * 100.0))


def _status(spec: MetricSpec, value: float, norm: float) -> str:
    field = spec.field
    if field in {"congestion_index", "congestion", "mean_congestion", "mean_congestion_index"}:
        if value >= 80:
            return "Critical"
        if value >= 65:
            return "High"
        if value >= 50:
            return "Moderate"
        return "Low"
    if field in {"capacity_utilization", "capacity", "mean_capacity"}:
        if value >= 95:
            return "Critical"
        if value >= 85:
            return "High"
        if value >= 70:
            return "Moderate"
        return "Low"
    if field in {"avg_speed", "speed", "average_speed", "mean_speed"}:
        if value >= 35:
            return "High"
        if value >= 25:
            return "Moderate"
        if value >= 15:
            return "Low"
        return "Critical"
    if field in {"public_transport_usage", "pt_usage", "mean_pt_usage"}:
        if value >= 70:
            return "High"
        if value >= 50:
            return "Moderate"
        if value >= 30:
            return "Low"
        return "Critical"
    if field in {"signal_compliance", "signal", "mean_signal"}:
        if value >= 90:
            return "High"
        if value >= 75:
            return "Moderate"
        if value >= 60:
            return "Low"
        return "Critical"
    if spec.higher_is == "context":
        if norm >= 70:
            return "High"
        if norm >= 35:
            return "Moderate"
        return "Low"
    if norm >= 75:
        return "Critical"
    if norm >= 50:
        return "High"
    if norm >= 25:
        return "Moderate"
    return "Low"


def _fmt_value(value: float, suffix: str) -> str:
    if pd.isna(value):
        return "Unavailable"
    if suffix == "%":
        return f"{value:.0f}%"
    if suffix == " km/h":
        return f"{value:.1f} km/h"
    if abs(value) >= 1000:
        return f"{value:,.0f}"
    if abs(value - round(value)) < 0.05:
        return f"{value:.0f}"
    return f"{value:.1f}"


def _session_state() -> dict[str, Any]:
    try:
        import streamlit as st

        return st.session_state
    except Exception:
        return {}


def _string_from_config(cfg: dict[str, Any], keys: tuple[str, ...], areas: set[str]) -> str | None:
    for key in keys:
        value = cfg.get(key)
        if isinstance(value, str) and value in areas:
            return value
    return None


def _focused_area(cfg: dict[str, Any], areas: set[str]) -> str | None:
    value = _string_from_config(cfg, ("focused_area", "focus_area", "selected_area", "area"), areas)
    if value:
        return value

    state = _session_state()
    for key, value in state.items():
        key_l = str(key).lower()
        if "area" in key_l and "focus" in key_l and isinstance(value, str) and value in areas:
            return value
    return None


def _selected_area(areas: set[str]) -> str | None:
    selected = _session_state().get("traffic_selected_areas")
    if isinstance(selected, (list, tuple, set)) and len(selected) == 1:
        value = next(iter(selected))
        if value in areas:
            return value
    return None


def _default_area(cfg: dict[str, Any], profile: pd.DataFrame, areas: set[str]) -> str | None:
    value = _string_from_config(cfg, ("default_area", "area_default", "area"), areas)
    if value:
        return value
    if len(profile.index) == 1:
        return str(profile.index[0])
    return None


def _highest_pressure_area(profile: pd.DataFrame, metric_cols: dict[str, str]) -> str:
    score = pd.Series(0.0, index=profile.index)
    for field in (
        "congestion_index",
        "mean_congestion",
        "capacity_utilization",
        "mean_capacity",
        "incident_count",
        "total_incidents",
        "traffic_volume",
        "record_count",
    ):
        column = metric_cols.get(field)
        if not column:
            continue
        values = pd.to_numeric(profile[column], errors="coerce")
        score = score.add(values.fillna(values.mean()).fillna(0.0), fill_value=0.0)
    return str(score.sort_values(ascending=False).index[0])


def _active_area(cfg: dict[str, Any], profile: pd.DataFrame, metric_cols: dict[str, str]) -> tuple[str, str]:
    areas = {str(area) for area in profile.index}
    focused_area = _focused_area(cfg, areas)
    if focused_area:
        return focused_area, "Chart Focus"
    selected_area = _selected_area(areas)
    if selected_area:
        return selected_area, "Global Filter"
    default_area = _default_area(cfg, profile, areas)
    if default_area:
        return default_area, "Default Area"
    return _highest_pressure_area(profile, metric_cols), "Highest Pressure"


def _status_annotation(label: str, status: str) -> dict[str, Any]:
    bgcolor, color = STATUS_BADGES[status]
    return {
        "x": STATUS_X,
        "y": label,
        "xref": "x",
        "yref": "y",
        "text": status.upper(),
        "showarrow": False,
        "xanchor": "center",
        "yanchor": "middle",
        "align": "center",
        "bgcolor": bgcolor,
        "bordercolor": color,
        "borderwidth": 1,
        "borderpad": 4,
        "font": {"size": 10, "color": color},
    }


def _value_annotation(label: str, value: str) -> dict[str, Any]:
    return {
        "x": VALUE_X,
        "y": label,
        "xref": "x",
        "yref": "y",
        "text": f"<b>{value}</b>",
        "showarrow": False,
        "xanchor": "right",
        "yanchor": "middle",
        "font": {"size": 11, "color": "#F0F6FC"},
    }


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No area traffic profile data", "traffic")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "traffic")
    frame = data.copy()
    area_col = _area_column(frame)
    if area_col is None:
        return empty_figure("Area field unavailable for traffic profile", dashboard)
    if area_col == frame.index.name:
        frame = frame.reset_index()

    active_metrics = METRICS
    metric_cols = {spec.field: _metric_column(frame, spec) for spec in active_metrics}
    metric_cols = {field: column for field, column in metric_cols.items() if column is not None}
    if not metric_cols:
        active_metrics = _fallback_metric_specs(frame, area_col)
        metric_cols = {spec.field: _metric_column(frame, spec) for spec in active_metrics}
        metric_cols = {field: column for field, column in metric_cols.items() if column is not None}
    if not metric_cols:
        return empty_figure("Traffic profile metrics unavailable", dashboard)

    for column in metric_cols.values():
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    profile = frame.groupby(area_col, dropna=True)[list(metric_cols.values())].mean(numeric_only=True)
    if profile.empty:
        return empty_figure("No area traffic profile data", dashboard)

    area, area_source = _active_area(cfg, profile, metric_cols)
    network_avg = profile.mean(numeric_only=True)

    labels: list[str] = []
    bar_values: list[float] = []
    avg_values: list[float] = []
    bar_colors: list[str] = []
    customdata: list[list[str]] = []
    annotations: list[dict[str, Any]] = []

    for spec in active_metrics:
        column = metric_cols.get(spec.field)
        if not column:
            continue
        series = pd.to_numeric(profile[column], errors="coerce")
        value = float(profile.loc[area, column])
        average = float(network_avg[column])
        low = float(series.min())
        high = float(series.max())
        norm = _normalize(value, low, high)
        avg_norm = _normalize(average, low, high)
        status = _status(spec, value, norm)
        scaled_value = (norm / 100.0) * BAR_REGION_MAX
        scaled_average = (avg_norm / 100.0) * BAR_REGION_MAX
        value_text = _fmt_value(value, spec.suffix)
        average_text = _fmt_value(average, spec.suffix)

        labels.append(spec.label)
        bar_values.append(scaled_value)
        avg_values.append(scaled_average)
        bar_colors.append(BAR_COLORS.get(spec.label, "#58A6FF"))
        annotations.append(_value_annotation(spec.label, value_text))
        annotations.append(_status_annotation(spec.label, status))
        customdata.append([str(area), spec.label, value_text, average_text, status])

    if not labels:
        return empty_figure("Traffic profile metrics unavailable", dashboard)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=bar_values,
            y=labels,
            orientation="h",
            marker=dict(color=bar_colors, line=dict(width=0)),
            width=0.48,
            customdata=customdata,
            hovertemplate=(
                "%{customdata[0]}<br><br>"
                "%{customdata[1]}<br>"
                "%{customdata[2]}<br><br>"
                "Network Average<br>"
                "%{customdata[3]}<br><br>"
                "Status<br>"
                "%{customdata[4]}<extra></extra>"
            ),
            name=str(area),
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=avg_values,
            y=labels,
            mode="markers",
            marker=dict(symbol="line-ns-open", size=18, color="#F0F6FC", line=dict(width=2, color="#F0F6FC")),
            hoverinfo="skip",
            name="Network Average",
            showlegend=False,
        )
    )

    fig = apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "supporting"), show_legend=False)
    fig.update_layout(
        title=dict(
            text=(
                f"Showing: {area}<br>"
                f"<span style='font-size:11px;color:#8B949E'>Source: {area_source}</span>"
            ),
            x=0.5,
            xanchor="center",
            font=dict(size=13),
        ),
        barmode="overlay",
        bargap=0.52,
        annotations=annotations,
        xaxis_title="",
        yaxis_title="",
        xaxis=dict(range=[0, 100], showticklabels=False, showgrid=False, zeroline=False, fixedrange=True),
        yaxis=dict(autorange="reversed", automargin=True, tickfont=dict(size=11)),
        margin=dict(l=138, r=146, t=50, b=26),
    )
    return fig
