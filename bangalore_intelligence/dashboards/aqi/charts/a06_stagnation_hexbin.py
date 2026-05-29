"""A-06 · Stagnation Hexbin / Seasonal Drift — density or trend lines."""

import plotly.graph_objects as go

from config.data_config import COL_PM25, COL_SEASON, COL_SLP, COL_VV
from config.theme import AQI_COLOR_MODERATE, AQI_COLOR_POOR, AQI_COLOR_SEVERE, AQI_COLOR_VERY_POOR
from filters.interaction import trace_opacity
from utils.formatters import hover_pm25, hover_template, hover_z_pm25
from utils.plotly_engine import apply_dashboard_theme, empty_figure

SEASON_COLORS = {
    "Winter": AQI_COLOR_SEVERE,
    "Spring": AQI_COLOR_MODERATE,
    "Monsoon": AQI_COLOR_POOR,
    "Post-Monsoon": AQI_COLOR_VERY_POOR,
}


def _render_hexbin(data, cfg, dashboard):
    fig = go.Figure(
        go.Histogram2d(
            x=data[COL_SLP],
            y=data[COL_VV],
            z=data[COL_PM25],
            histfunc="avg",
            colorscale=[[0, "#1A2333"], [0.5, "#5A8F72"], [1, "#A85A5A"]],
            hovertemplate=hover_template("SLP %{x}", "VV %{y}", hover_z_pm25()),
        )
    )
    fig.update_layout(
        xaxis_title="Sea Level Pressure (hPa)",
        yaxis_title="Vertical Visibility (VV)",
        margin=dict(l=56, r=24, t=16, b=48),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "hero"), show_legend=False)


def _render_drift(data, cfg, dashboard):
    highlight = cfg.get("highlight_season")
    fig = go.Figure()
    for season, grp in data.groupby(COL_SEASON):
        fig.add_trace(
            go.Scatter(
                x=grp["year"],
                y=grp["mean_pm25"],
                mode="lines+markers",
                name=season,
                line=dict(width=2.5, color=SEASON_COLORS.get(season, AQI_COLOR_MODERATE)),
                marker=dict(size=7),
                opacity=trace_opacity(season, highlight, base=0.65),
                hovertemplate=hover_template("<b>%{fullData.name}</b>", "%{x}: " + hover_pm25()),
            )
        )
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Mean PM2.5 (µg/m³)",
        margin=dict(l=56, r=24, t=16, b=48),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "hero"), show_legend=True)


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No stagnation data", "aqi")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "aqi")
    if COL_SLP in data.columns and COL_VV in data.columns and "year" not in data.columns:
        return _render_hexbin(data, cfg, dashboard)
    if COL_SEASON in data.columns and "mean_pm25" in data.columns:
        return _render_drift(data, cfg, dashboard)
    return empty_figure("Unrecognized stagnation dataset", dashboard)
