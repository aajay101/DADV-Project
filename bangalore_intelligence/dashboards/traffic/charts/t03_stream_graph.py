"""T-03 · Monthly congestion trend by area — multi-line time series."""

import plotly.graph_objects as go

from config.data_config import COL_AREA
from utils.formatters import hover_congestion, hover_template
from utils.plotly_engine import (
    apply_dashboard_theme,
    area_color,
    congestion_axis_range,
    empty_figure,
)


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No temporal stream data", "traffic")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "traffic")
    months = sorted(data["month"].unique())
    areas = sorted(data[COL_AREA].unique())
    y_domain = congestion_axis_range(data["mean_congestion"])

    fig = go.Figure()
    for area in areas:
        sub = data[data[COL_AREA] == area].set_index("month").reindex(months)
        color = area_color(area, dashboard)
        fig.add_trace(
            go.Scatter(
                x=months,
                y=sub["mean_congestion"],
                mode="lines+markers",
                name=area,
                line=dict(width=2, color=color),
                marker=dict(size=6, color=color),
                hovertemplate=hover_template(
                    "<b>%{fullData.name}</b>", "Month %{x}", hover_congestion()
                ),
            )
        )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Mean Congestion (%)",
        yaxis=dict(range=list(y_domain)),
    )
    return apply_dashboard_theme(
        fig,
        dashboard,
        role=cfg.get("role", "hero"),
        show_legend=True,
        chart_type="timeseries",
    )
