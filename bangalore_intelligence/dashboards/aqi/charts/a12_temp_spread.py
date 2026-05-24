"""A-12 · Temperature Spread Bands — diurnal spread vs PM2.5."""

import plotly.graph_objects as go

from config.theme import AQI_COLOR_POOR
from utils.formatters import hover_pm25, hover_template
from utils.plotly_engine import apply_dashboard_theme, empty_figure


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No temperature spread data", "aqi")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "aqi")
    labels = data["spread_band"].astype(str)

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=data["mean_pm25"],
            marker_color=AQI_COLOR_POOR,
            hovertemplate=hover_template(
                "%{x}", f"Mean {hover_pm25()}", "Median %{customdata:.1f} µg/m³"
            ),
            customdata=data["median_pm25"],
        )
    )
    fig.update_layout(
        xaxis_title="Diurnal Temperature Spread",
        yaxis_title="Mean PM2.5 (µg/m³)",
        margin=dict(l=56, r=24, t=16, b=56),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "supporting"), show_legend=False)
