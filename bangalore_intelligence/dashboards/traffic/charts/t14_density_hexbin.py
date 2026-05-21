"""T-14 · Volume–Congestion Density — 2D histogram."""

import plotly.graph_objects as go

from config.data_config import COL_CONGESTION, COL_TRAFFIC_VOL
from utils.plotly_engine import apply_dashboard_theme, empty_figure


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No volume–congestion data", "traffic")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "traffic")
    x = data[COL_TRAFFIC_VOL] if COL_TRAFFIC_VOL in data.columns else data.get("traffic_volume", data.iloc[:, 0])
    y = data[COL_CONGESTION]

    fig = go.Figure(
        go.Histogram2d(
            x=x,
            y=y,
            nbinsx=20,
            nbinsy=20,
            colorscale="Reds",
            hovertemplate="Volume %{x}<br>Congestion %{y}<br>Count %{z}<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis_title="Traffic Volume",
        yaxis_title="Congestion Level",
        yaxis=dict(range=[0, 100]),
        margin=dict(l=56, r=24, t=16, b=48),
        height=cfg.get("height"),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "supporting"), show_legend=False)
