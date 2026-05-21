"""A-05 · Pollution Persistence Series — daily PM2.5 with rolling mean."""

import plotly.graph_objects as go

from config.data_config import COL_DATE, COL_PM25
from config.theme import AQI_COLOR_SEVERE, AQI_COLOR_VERY_POOR
from utils.plotly_engine import apply_dashboard_theme, empty_figure


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No persistence series data", "aqi")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "aqi")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data[COL_DATE],
            y=data[COL_PM25],
            mode="lines",
            name="Daily PM2.5",
            line=dict(width=1, color="rgba(168, 90, 90, 0.45)"),
            hovertemplate="%{x|%Y-%m-%d}<br>%{y:.1f} µg/m³<extra></extra>",
        )
    )
    if "rolling_7d_pm25" in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data[COL_DATE],
                y=data["rolling_7d_pm25"],
                mode="lines",
                name="7-day rolling mean",
                line=dict(width=2.5, color=AQI_COLOR_VERY_POOR),
                hovertemplate="%{x|%Y-%m-%d}<br>Rolling %{y:.1f} µg/m³<extra></extra>",
            )
        )
    fig.add_hrect(y0=60, y1=120, fillcolor="rgba(168, 90, 90, 0.12)", line_width=0)
    fig.add_hline(y=250, line_dash="dot", line_color=AQI_COLOR_SEVERE, annotation_text="Severe 250")
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="PM2.5 (µg/m³)",
        margin=dict(l=56, r=24, t=16, b=48),
        height=cfg.get("height"),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "supporting"), show_legend=True)
