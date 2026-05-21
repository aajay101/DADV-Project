"""T-10 · Public Transport Decoupling — PT quartile vs congestion (observational)."""

import plotly.graph_objects as go

from config.theme import TRAFFIC_CRIMSON, TRAFFIC_SLATE, TRAFFIC_TEAL
from utils.plotly_engine import apply_dashboard_theme, empty_figure


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No PT quartile summary", "traffic")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "traffic")
    x = data["pt_quartile"].astype(str)

    fig = go.Figure(
        data=[
            go.Bar(
                name="Congestion",
                x=x,
                y=data["mean_congestion"],
                marker_color=TRAFFIC_CRIMSON,
                hovertemplate="%{x}<br>Congestion %{y:.1f}<extra></extra>",
            ),
            go.Bar(
                name="Speed",
                x=x,
                y=data["mean_speed"],
                marker_color=TRAFFIC_TEAL,
                hovertemplate="%{x}<br>Speed %{y:.1f} km/h<extra></extra>",
            ),
            go.Scatter(
                name="Incidents",
                x=x,
                y=data["mean_incidents"],
                mode="lines+markers",
                yaxis="y2",
                line=dict(color=TRAFFIC_SLATE, width=2),
                hovertemplate="%{x}<br>Incidents %{y:.1f}<extra></extra>",
            ),
        ]
    )
    fig.update_layout(
        barmode="group",
        xaxis_title="Public Transport Usage Quartile",
        yaxis_title="Congestion / Speed",
        yaxis2=dict(title="Mean Incidents", overlaying="y", side="right", showgrid=False),
        margin=dict(l=48, r=56, t=16, b=72),
        height=cfg.get("height"),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "supporting"), show_legend=True)
