"""A-08 · Temperature Scatter / Category Transition Matrix."""

import plotly.graph_objects as go

from config.data_config import AQI_CATEGORIES, COL_AQI_CATEGORY, COL_PM25, COL_TM
from utils.plotly_engine import AQI_CATEGORY_COLORS, apply_dashboard_theme, empty_figure


def _render_transition(data, cfg, dashboard):
    z = data.values.tolist()
    text = [[str(int(v)) for v in row] for row in z]
    colorscale = [
        [i / max(len(AQI_CATEGORIES) - 1, 1), AQI_CATEGORY_COLORS[c]]
        for i, c in enumerate(AQI_CATEGORIES)
    ]
    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=AQI_CATEGORIES,
            y=AQI_CATEGORIES,
            colorscale=colorscale,
            text=text,
            texttemplate="%{text}",
            hovertemplate="From %{y} → %{x}<br>Days %{z}<extra></extra>",
            showscale=False,
        )
    )
    fig.update_layout(
        xaxis_title="To Category",
        yaxis_title="From Category",
        margin=dict(l=96, r=32, t=16, b=96),
        height=cfg.get("height"),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "hero"), show_legend=False)


def _render_scatter(data, cfg, dashboard):
    fig = go.Figure()
    for cat, grp in data.groupby(COL_AQI_CATEGORY):
        fig.add_trace(
            go.Scatter(
                x=grp[COL_TM],
                y=grp[COL_PM25],
                mode="markers",
                name=cat,
                marker=dict(size=6, color=AQI_CATEGORY_COLORS.get(cat, "#5A8F72"), opacity=0.55),
                hovertemplate="Tm %{x:.1f}°C<br>PM2.5 %{y:.1f} µg/m³<extra></extra>",
            )
        )
    fig.update_layout(
        xaxis_title="Minimum Temperature (°C)",
        yaxis_title="PM2.5 (µg/m³)",
        margin=dict(l=56, r=24, t=16, b=48),
        height=cfg.get("height"),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "hero"), show_legend=True)


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No temperature relationship data", "aqi")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "aqi")
    if COL_TM in data.columns and COL_PM25 in data.columns:
        return _render_scatter(data, cfg, dashboard)
    if set(data.columns) >= set(AQI_CATEGORIES) or data.shape[0] == len(AQI_CATEGORIES):
        return _render_transition(data, cfg, dashboard)
    return _render_transition(data, cfg, dashboard)
