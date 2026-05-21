"""T-03 · Temporal Stream Intelligence — monthly congestion flow."""

import plotly.graph_objects as go

from config.data_config import COL_AREA
from config.theme import get_dashboard_tokens
from utils.plotly_engine import apply_dashboard_theme, empty_figure, severity_color


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No temporal stream data", "traffic")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "traffic")
    tokens = get_dashboard_tokens(dashboard)
    months = sorted(data["month"].unique())
    areas = sorted(data[COL_AREA].unique())

    fig = go.Figure()
    for area in areas:
        sub = data[data[COL_AREA] == area].set_index("month").reindex(months)
        fig.add_trace(
            go.Scatter(
                x=months,
                y=sub["mean_congestion"],
                mode="lines",
                stackgroup="one",
                name=area,
                line=dict(width=0.6, color=severity_color(sub["mean_congestion"].mean(), dashboard)),
                fillcolor=severity_color(sub["mean_congestion"].mean(), dashboard),
                opacity=0.55,
                hovertemplate="<b>%{fullData.name}</b><br>Month %{x}<br>Congestion %{y:.1f}<extra></extra>",
            )
        )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Stacked Congestion Pressure",
        margin=dict(l=48, r=24, t=16, b=56),
        height=cfg.get("height"),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "hero"), show_legend=True)
