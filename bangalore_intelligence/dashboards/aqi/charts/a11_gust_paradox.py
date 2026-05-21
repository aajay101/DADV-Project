"""A-11 · Gust Ratio Paradox — quintile PM2.5 with CI bands."""

import plotly.graph_objects as go

from config.theme import AQI_COLOR_VERY_POOR
from utils.plotly_engine import apply_dashboard_theme, empty_figure


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No gust quintile data", "aqi")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "aqi")
    x = data["gust_quintile"].astype(str)

    fig = go.Figure(
        go.Bar(
            x=x,
            y=data["mean_pm25"],
            marker_color=AQI_COLOR_VERY_POOR,
            error_y=dict(
                type="data",
                array=(data["ci_high"] - data["mean_pm25"]).clip(lower=0),
                arrayminus=(data["mean_pm25"] - data["ci_low"]).clip(lower=0),
                color="rgba(255,255,255,0.35)",
            ),
            hovertemplate="%{x}<br>Mean %{y:.1f} µg/m³<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis_title="Gust Ratio Quintile",
        yaxis_title="Mean PM2.5 (µg/m³)",
        margin=dict(l=56, r=24, t=16, b=56),
        height=cfg.get("height"),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "supporting"), show_legend=False)
