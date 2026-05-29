"""T-07 · Active Mobility Exclusion — diverging penalty by road."""

import plotly.graph_objects as go

from config.data_config import COL_ROAD
from config.theme import TRAFFIC_AMBER, TRAFFIC_CRIMSON, TRAFFIC_TEAL
from filters.interaction import emphasis_opacity
from utils.formatters import hover_mobility_penalty, hover_template
from utils.plotly_engine import apply_dashboard_theme, empty_figure


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No mobility exclusion data", "traffic")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "traffic")
    data = data.sort_values("exclusion_delta", ascending=True)

    colors = [
        TRAFFIC_CRIMSON if v > 8 else (TRAFFIC_AMBER if v > 0 else TRAFFIC_TEAL)
        for v in data["exclusion_delta"]
    ]
    highlight_road = cfg.get("highlight_road")
    opacities = [
        emphasis_opacity(str(r), highlight_road, base=0.85) if highlight_road else 0.9
        for r in data[COL_ROAD]
    ]
    line_width = [
        2.5 if highlight_road and str(r) == highlight_road else 0
        for r in data[COL_ROAD]
    ]

    fig = go.Figure(
        go.Bar(
            x=data["exclusion_delta"],
            y=data[COL_ROAD],
            orientation="h",
            marker=dict(
                color=colors,
                opacity=opacities,
                line=dict(width=line_width, color="#F0F6FC"),
            ),
            hovertemplate=hover_template("<b>%{y}</b>", hover_mobility_penalty()),
        )
    )
    fig.add_vline(x=0, line_width=1.5, line_color="#484F58", opacity=0.8)
    fig.update_layout(
        xaxis_title="Congestion Penalty vs System Baseline",
        yaxis_title="",
        margin=dict(l=140, r=32, t=16, b=48),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "supporting"), show_legend=False)
