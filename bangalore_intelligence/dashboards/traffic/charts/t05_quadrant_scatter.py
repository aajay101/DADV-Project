"""T-05 · Road Management Priority Quadrant — congestion × capacity classification."""

import plotly.graph_objects as go

from config.data_config import COL_AREA, COL_ROAD
from config.theme import TRAFFIC_AMBER, TRAFFIC_CRIMSON, TRAFFIC_TEAL
from filters.interaction import emphasis_opacity, related_area_for_road
from utils.plotly_engine import apply_dashboard_theme, area_color, empty_figure
from utils.plotly_helpers import add_quadrant_lines, add_quadrant_zone_labels


def _quadrant_color(congestion: float, capacity: float) -> str:
    if congestion >= 90 and capacity >= 95:
        return TRAFFIC_CRIMSON
    if congestion >= 75 or capacity >= 90:
        return TRAFFIC_AMBER
    if congestion < 60 and capacity < 75:
        return TRAFFIC_TEAL
    return "#8B949E"


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No road operational data", "traffic")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "traffic")
    highlight_road = cfg.get("highlight_road")
    highlight_area = cfg.get("highlight_area")
    related = related_area_for_road(highlight_road, data)

    x_col = "mean_capacity"
    y_col = "mean_congestion"
    if x_col not in data.columns or y_col not in data.columns:
        return empty_figure("Missing capacity or congestion metrics", dashboard)

    data = data.sort_values(y_col, ascending=False)
    max_instability = max(data["flow_instability_index"].max(), 0.1)
    sizes = (data["flow_instability_index"] / max_instability * 28 + 10).tolist()
    colors = [_quadrant_color(c, cap) for c, cap in zip(data[y_col], data[x_col])]
    opacities = []
    for _, row in data.iterrows():
        road = row[COL_ROAD]
        area = row[COL_AREA]
        if highlight_road:
            opacities.append(
                emphasis_opacity(road, highlight_road, related, base=0.78, related_opacity=0.55)
            )
        elif highlight_area:
            opacities.append(emphasis_opacity(area, highlight_area, base=0.78))
        else:
            opacities.append(0.78)
    line_width = [
        2.8 if highlight_road and row[COL_ROAD] == highlight_road else 1.2
        for _, row in data.iterrows()
    ]

    fig = go.Figure(
        go.Scatter(
            x=data[x_col],
            y=data[y_col],
            mode="markers",
            marker=dict(
                size=sizes,
                color=colors,
                opacity=opacities,
                line=dict(width=line_width, color="#21262D"),
            ),
            text=data[COL_ROAD],
            customdata=data[
                [COL_AREA, "mean_speed", "total_incidents", "pct_at_max_capacity"]
            ].values,
            hovertemplate=(
                "<b>%{text}</b> · %{customdata[0]}<br>"
                "Congestion %{y:.1f}<br>"
                "Capacity %{x:.1f}%<br>"
                "Speed %{customdata[1]:.1f} km/h<br>"
                "Incidents %{customdata[2]:.0f}<br>"
                "At max cap %{customdata[3]:.0%}"
                "<extra></extra>"
            ),
        )
    )

    x_mid, y_mid = 75.0, 75.0
    add_quadrant_lines(fig, x_mid, y_mid, dashboard)
    add_quadrant_zone_labels(fig, x_mid, y_mid, dashboard)

    fig.update_layout(
        xaxis_title="Road Capacity Utilization (%)",
        yaxis_title="Mean Congestion Index",
        xaxis=dict(range=[0, 105]),
        yaxis=dict(range=[0, 105]),
        margin=dict(l=56, r=24, t=16, b=56),
        height=cfg.get("height"),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "hero"), show_legend=False)
