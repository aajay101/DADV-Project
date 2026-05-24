"""T-04 · Weekly Congestion Distribution — day-of-week violin/box."""

import plotly.graph_objects as go

from config.data_config import COL_CONGESTION
from config.theme import TRAFFIC_CRIMSON, TRAFFIC_TEAL
from utils.formatters import hover_congestion, hover_template
from utils.plotly_engine import apply_dashboard_theme, empty_figure

WEEK_ORDER = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No weekly distribution data", "traffic")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "traffic")
    use_box = cfg.get("fallback_box", len(data) < 30)

    fig = go.Figure()
    if use_box:
        for day in WEEK_ORDER:
            sub = data.loc[data["day_of_week"] == day, COL_CONGESTION]
            if sub.empty:
                continue
            fig.add_trace(
                go.Box(
                    y=sub,
                    name=day,
                    marker_color=TRAFFIC_CRIMSON,
                    line_color=TRAFFIC_TEAL,
                    hovertemplate=hover_template(day, hover_congestion()),
                )
            )
    else:
        for day in WEEK_ORDER:
            sub = data.loc[data["day_of_week"] == day, COL_CONGESTION]
            if len(sub) < 5:
                continue
            fig.add_trace(
                go.Violin(
                    y=sub,
                    name=day,
                    line_color=TRAFFIC_CRIMSON,
                    fillcolor="rgba(229, 56, 59, 0.3)",
                    points=False,
                    box_visible=True,
                    meanline_visible=True,
                    hovertemplate=hover_template(day, hover_congestion()),
                )
            )

    fig.update_layout(
        xaxis_title="Day of Week",
        yaxis_title="Congestion Index",
        yaxis=dict(range=[0, 100]),
        margin=dict(l=48, r=24, t=16, b=56),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "supporting"), show_legend=False)
