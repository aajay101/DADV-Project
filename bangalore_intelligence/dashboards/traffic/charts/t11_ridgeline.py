"""T-11 · Congestion Distribution Ridgeline — KDE ridges by road."""

import numpy as np
import plotly.graph_objects as go

from config.data_config import COL_AREA, COL_ROAD
from config.theme import TRAFFIC_TEXT_MUTED
from utils.analytics_kde import gaussian_kde_1d
from utils.plotly_engine import apply_dashboard_theme, area_color, empty_figure


def _hex_rgba(hex_color: str, alpha: float = 0.3) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No road distribution data", "traffic")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "traffic")
    highlight = cfg.get("highlight_area")

    roads = (
        data.groupby(COL_ROAD)
        .agg(median_cong=("value", "median"), area=(COL_AREA, "first"))
        .reset_index()
        .sort_values("median_cong", ascending=False)
    )

    fig = go.Figure()
    grid = np.linspace(0, 100, 80)
    scale = 7.5
    road_order = roads[COL_ROAD].tolist()

    for idx, row in roads.iterrows():
        road = row[COL_ROAD]
        area = row["area"]
        vals = data.loc[data[COL_ROAD] == road, "value"].values
        if len(vals) < 5:
            continue
        density = gaussian_kde_1d(vals, grid)
        y_offset = len(road_order) - road_order.index(road)
        y_top = y_offset + density * scale
        y_bottom = y_offset - density * scale
        color = area_color(area, dashboard)
        opacity = 0.78 if (not highlight or area == highlight) else 0.22

        fig.add_trace(
            go.Scatter(x=grid, y=y_top, mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip")
        )
        fig.add_trace(
            go.Scatter(
                x=grid,
                y=y_bottom,
                mode="lines",
                fill="tonexty",
                name=str(road),
                line=dict(color=color, width=1.3),
                fillcolor=_hex_rgba(color, 0.30),
                opacity=opacity,
                hovertemplate=(
                    f"<b>{road}</b> ({area})<br>"
                    "Congestion %{x:.0f}<br>"
                    f"Median {row['median_cong']:.1f}<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        xaxis_title="Congestion Level",
        yaxis=dict(
            tickmode="array",
            tickvals=list(range(1, len(road_order) + 1)),
            ticktext=road_order[::-1],
        ),
        margin=dict(l=140, r=24, t=16, b=48),
        height=cfg.get("height"),
    )
    fig.add_annotation(
        x=0,
        y=-0.42,
        xref="paper",
        yref="paper",
        text="KDE ridges sorted by median congestion — right-skew indicates overload persistence",
        showarrow=False,
        font=dict(size=10, color=TRAFFIC_TEXT_MUTED),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "hero"), show_legend=False)
