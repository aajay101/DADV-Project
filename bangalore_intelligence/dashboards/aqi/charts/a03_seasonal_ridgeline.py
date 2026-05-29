"""A-03 · Seasonal PM2.5 Ridgeline — atmospheric distribution by season."""

import numpy as np
import plotly.graph_objects as go

from config.data_config import COL_SEASON
from config.theme import AQI_COLOR_MODERATE, AQI_TEXT_MUTED
from utils.analytics_kde import gaussian_kde_1d
from utils.formatters import hover_pm25_axis, hover_template
from utils.plotly_engine import apply_dashboard_theme, empty_figure

SEASON_COLORS = {
    "Winter": "#60A5FA",
    "Spring": "#FBBF24",
    "Monsoon": "#34D399",
    "Post-Monsoon": "#A78BFA",
}
SEASON_ORDER = ["Winter", "Spring", "Monsoon", "Post-Monsoon"]


def _hex_rgba(hex_color: str, alpha: float = 0.35) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No seasonal distribution data", "aqi")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "aqi")
    if "value" not in data.columns or COL_SEASON not in data.columns:
        return empty_figure("Seasonal ridgeline requires season and PM2.5 values", dashboard)

    seasons = [s for s in SEASON_ORDER if s in data[COL_SEASON].unique()]
    fig = go.Figure()
    vmax = max(float(data["value"].max()), 50)
    grid = np.linspace(0, vmax * 1.05, 90)
    scale = 10.0

    for i, season in enumerate(seasons):
        vals = data.loc[data[COL_SEASON] == season, "value"].values
        if len(vals) < 5:
            continue
        density = gaussian_kde_1d(vals, grid)
        y_offset = len(seasons) - i
        y_top = y_offset + density * scale
        y_bottom = y_offset - density * scale
        color = SEASON_COLORS.get(season, AQI_COLOR_MODERATE)

        fig.add_trace(
            go.Scatter(x=grid, y=y_top, mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip")
        )
        fig.add_trace(
            go.Scatter(
                x=grid,
                y=y_bottom,
                mode="lines",
                fill="tonexty",
                name=season,
                line=dict(color=color, width=1.4),
                fillcolor=_hex_rgba(color, 0.38),
                hovertemplate=hover_template(f"<b>{season}</b>", hover_pm25_axis("x")),
            )
        )

    fig.update_layout(
        xaxis_title="PM2.5 (µg/m³)",
        yaxis=dict(
            tickmode="array",
            tickvals=list(range(1, len(seasons) + 1)),
            ticktext=list(reversed(seasons)),
        ),
        margin=dict(l=100, r=24, t=16, b=48),
    )
    fig.add_annotation(
        x=0,
        y=-0.4,
        xref="paper",
        yref="paper",
        text="Seasonal atmospheric density — winter accumulation vs monsoon partial relief",
        showarrow=False,
        font=dict(size=10, color=AQI_TEXT_MUTED),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "hero"), show_legend=False)
