"""A-09 · Pressure Universal Trigger — SLP band × season grouped bars."""

import plotly.graph_objects as go

from config.data_config import COL_SEASON
from config.theme import AQI_COLOR_MODERATE, AQI_COLOR_POOR, AQI_COLOR_SEVERE, AQI_COLOR_VERY_POOR
from utils.plotly_engine import apply_dashboard_theme, empty_figure

SEASON_COLORS = {
    "Winter": AQI_COLOR_SEVERE,
    "Spring": AQI_COLOR_MODERATE,
    "Monsoon": AQI_COLOR_POOR,
    "Post-Monsoon": AQI_COLOR_VERY_POOR,
}


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No pressure band data", "aqi")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "aqi")
    fig = go.Figure()
    for season, grp in data.groupby(COL_SEASON):
        fig.add_trace(
            go.Bar(
                x=grp["slp_band"].astype(str),
                y=grp["mean_pm25"],
                name=season,
                marker_color=SEASON_COLORS.get(season, AQI_COLOR_MODERATE),
                hovertemplate="%{x}<br>%{fullData.name}<br>%{y:.1f} µg/m³<extra></extra>",
            )
        )

    fig.update_layout(
        barmode="group",
        xaxis_title="Sea Level Pressure Band",
        yaxis_title="Mean PM2.5 (µg/m³)",
        margin=dict(l=56, r=24, t=16, b=72),
        height=cfg.get("height"),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "supporting"), show_legend=True)
