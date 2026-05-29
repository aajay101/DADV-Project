"""T-15 · Area-month congestion heatmap — mean congestion by area and month."""

import plotly.graph_objects as go

from config.data_config import COL_AREA
from utils.formatters import hover_congestion, hover_template
from utils.plotly_engine import (
    HEATMAP_SCALE_TRAFFIC,
    apply_dashboard_theme,
    empty_figure,
)


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No monthly area heatmap data", "traffic")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "traffic")
    months = sorted(data["month"].unique())
    areas = sorted(data[COL_AREA].unique())

    congestion = (
        data.pivot(index=COL_AREA, columns="month", values="mean_congestion")
        .reindex(index=areas, columns=months)
    )
    incidents = (
        data.pivot(index=COL_AREA, columns="month", values="total_incidents")
        .reindex(index=areas, columns=months)
        .fillna(0)
    )

    fig = go.Figure(
        go.Heatmap(
            z=congestion.values,
            x=[str(m) for m in congestion.columns],
            y=list(congestion.index),
            customdata=incidents.values,
            colorscale=HEATMAP_SCALE_TRAFFIC,
            colorbar=dict(title="Congestion %"),
            hovertemplate=hover_template(
                "<b>%{y}</b> · %{x}",
                hover_congestion("z"),
                "Incidents %{customdata:.0f}",
            ),
        )
    )
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Area",
        margin=dict(l=120, r=24, t=16, b=72),
    )
    return apply_dashboard_theme(
        fig,
        dashboard,
        role=cfg.get("role", "supporting"),
        show_legend=False,
        chart_type="heatmap",
    )
