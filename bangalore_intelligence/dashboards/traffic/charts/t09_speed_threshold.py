"""T-09 · Speed Collapse Threshold — congestion vs speed scatter."""

import plotly.graph_objects as go

from config.data_config import COL_AREA, COL_CONGESTION, COL_SPEED
from config.theme import TRAFFIC_AMBER, TRAFFIC_TEXT_MUTED
from filters.interaction import trace_opacity
from utils.formatters import hover_congestion, hover_speed, hover_template
from utils.plotly_engine import (
    apply_dashboard_theme,
    empty_figure,
    severity_color,
    traffic_speed_axis_range,
)
from utils.plotly_helpers import add_quadrant_lines


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No congestion–speed data", "traffic")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "traffic")
    highlight = cfg.get("highlight_area")

    fig = go.Figure()
    for area in sorted(data[COL_AREA].unique()):
        sub = data[data[COL_AREA] == area]
        fig.add_trace(
            go.Scatter(
                x=sub[COL_SPEED],
                y=sub[COL_CONGESTION],
                mode="markers",
                name=area,
                marker=dict(
                    size=7,
                    color=severity_color(sub[COL_CONGESTION].mean(), dashboard),
                    opacity=trace_opacity(area, highlight, base=0.45),
                ),
                hovertemplate=hover_template(
                    "<b>%{fullData.name}</b>", hover_speed("x"), hover_congestion()
                ),
            )
        )

    add_quadrant_lines(fig, 30, 75, dashboard)
    fig.add_annotation(
        x=0.98,
        y=0.98,
        xref="paper",
        yref="paper",
        text="CRITICAL OVERLOAD",
        showarrow=False,
        font=dict(size=10, color=TRAFFIC_AMBER),
        xanchor="right",
    )
    sampling = getattr(data, "attrs", {}).get("sampling", {})
    if sampling.get("sampled"):
        fig.add_annotation(
            x=0.02,
            y=0.02,
            xref="paper",
            yref="paper",
            text=(
                f"Sampled {sampling.get('sample_size'):,}/{sampling.get('source_rows'):,} "
                "records · random_state=42"
            ),
            showarrow=False,
            font=dict(size=10, color=TRAFFIC_TEXT_MUTED),
            xanchor="left",
        )
    speed_range = traffic_speed_axis_range(data[COL_SPEED])
    fig.update_layout(
        xaxis_title="Average Speed (km/h)",
        yaxis_title="Congestion Level",
        xaxis=dict(range=list(speed_range)),
        yaxis=dict(range=[0, 100]),
        margin=dict(l=56, r=24, t=16, b=48),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "hero"), show_legend=True)
