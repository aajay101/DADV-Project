"""A-14 · Season × Pressure Grid — mean PM2.5 heatmap."""

import plotly.graph_objects as go

from config.data_config import COL_SEASON
from utils.formatters import hover_template, hover_z_pm25
from utils.plotly_engine import apply_dashboard_theme, empty_figure


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No season–pressure grid data", "aqi")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "aqi")
    pivot = data.pivot(index=COL_SEASON, columns="slp_band", values="mean_pm25")
    if pivot.empty:
        return empty_figure("Insufficient grid dimensions", "aqi")

    fig = go.Figure(
        go.Heatmap(
            z=pivot.values,
            x=[str(c) for c in pivot.columns],
            y=[str(i) for i in pivot.index],
            colorscale=[
                [0, "#1A2333"],
                [0.5, "#5A8F72"],
                [1, "#A85A5A"],
            ],
            hovertemplate=hover_template("%{y} · %{x}", hover_z_pm25()),
        )
    )
    fig.update_layout(
        xaxis_title="SLP Band",
        yaxis_title="Season",
        margin=dict(l=88, r=32, t=16, b=56),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "supporting"), show_legend=False)
