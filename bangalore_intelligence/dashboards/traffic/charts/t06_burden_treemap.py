"""T-06 · Environmental Burden Treemap — area × road hierarchy."""

import plotly.graph_objects as go

from config.data_config import COL_AREA, COL_ROAD
from utils.plotly_engine import apply_dashboard_theme, empty_figure, severity_color


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No environmental burden data", "traffic")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "traffic")
    labels = data[COL_ROAD].tolist()
    parents = data[COL_AREA].tolist()
    values = data["environmental_impact"].tolist()
    highlight_road = cfg.get("highlight_road")
    highlight_area = cfg.get("highlight_area")
    colors = []
    line_colors = []
    for road, area, cong in zip(labels, parents, data["mean_congestion"]):
        base = severity_color(cong, dashboard)
        if highlight_road:
            active = str(road) == highlight_road
        elif highlight_area:
            active = str(area) == highlight_area
        else:
            active = True
        colors.append(base if active else "#2D333B")
        line_colors.append("#F0F6FC" if active and (highlight_road or highlight_area) else "#21262D")

    fig = go.Figure(
        go.Treemap(
            labels=labels,
            parents=parents,
            values=values,
            marker=dict(
                colors=colors,
                line=dict(width=1.5, color=line_colors),
            ),
            hovertemplate=(
                "<b>%{label}</b><br>Area %{parent}<br>"
                "Impact %{value:.1f}<br>Congestion %{customdata:.1f}<extra></extra>"
            ),
            customdata=data["mean_congestion"],
        )
    )
    fig.update_layout(
        margin=dict(l=8, r=8, t=8, b=8),
        height=cfg.get("height"),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "supporting"), show_legend=False)
