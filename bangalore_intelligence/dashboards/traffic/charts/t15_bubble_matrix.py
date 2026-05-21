"""T-15 · Area × Month Bubble Matrix — temporal area stress comparison."""

import plotly.graph_objects as go

from config.data_config import COL_AREA
from utils.plotly_engine import apply_dashboard_theme, area_color, empty_figure


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No monthly area bubble data", "traffic")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "traffic")
    highlight = cfg.get("highlight_area")

    max_inc = max(data["total_incidents"].max(), 1)
    sizes = (data["total_incidents"] / max_inc * 36 + 10).clip(10, 44)
    colors = [area_color(a, dashboard) for a in data[COL_AREA]]
    opacities = [0.85 if (not highlight or a == highlight) else 0.25 for a in data[COL_AREA]]

    fig = go.Figure(
        go.Scatter(
            x=data["month"].astype(str),
            y=data[COL_AREA],
            mode="markers",
            marker=dict(
                size=sizes,
                color=colors,
                opacity=opacities,
                line=dict(width=1, color="#30363D"),
            ),
            customdata=data[["mean_congestion", "total_incidents", "pct_at_max_capacity"]].values,
            hovertemplate=(
                "<b>%{y}</b> · %{x}<br>"
                "Congestion %{customdata[0]:.1f}<br>"
                "Incidents %{customdata[1]:.0f}<br>"
                "At max cap %{customdata[2]:.0%}"
                "<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Area",
        margin=dict(l=120, r=24, t=16, b=72),
        height=cfg.get("height"),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "supporting"), show_legend=False)
