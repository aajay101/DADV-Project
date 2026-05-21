"""Centralized Plotly visualization engine — theming and figure helpers."""

from copy import deepcopy

import plotly.graph_objects as go

from config.chart_defaults import get_base_layout
from config.theme import (
    AQI_COLOR_GOOD,
    AQI_COLOR_MODERATE,
    AQI_COLOR_POOR,
    AQI_COLOR_SATISFACTORY,
    AQI_COLOR_SEVERE,
    AQI_COLOR_VERY_POOR,
    get_dashboard_tokens,
    get_severity_colors,
)

AQI_CATEGORY_COLORS = {
    "Good": AQI_COLOR_GOOD,
    "Satisfactory": AQI_COLOR_SATISFACTORY,
    "Moderate": AQI_COLOR_MODERATE,
    "Poor": AQI_COLOR_POOR,
    "Very Poor": AQI_COLOR_VERY_POOR,
    "Severe": AQI_COLOR_SEVERE,
}

PLOTLY_CONFIG = {
    "displayModeBar": False,
    "responsive": True,
}

ANIMATION_DEFAULTS = {
    "transition": {"duration": 400, "easing": "cubic-in-out"},
    "frame": {"duration": 500, "redraw": False},
}

HEATMAP_SCALE_TRAFFIC = [
    [0.0, "#1C2128"],
    [0.25, "#374151"],
    [0.5, "#8A7B4E"],
    [0.75, "#B07A45"],
    [1.0, "#A85A5A"],
]

TRAFFIC_AREA_COLORS = {
    "Indiranagar": "#58A6FF",
    "Koramangala": "#E5383B",
    "Whitefield": "#2EC4B6",
    "Electronic City": "#FFBA08",
    "Marathahalli": "#8B5CF6",
    "Silk Board": "#10B981",
    "MG Road": "#F97316",
    "Brigade Road": "#EC4899",
}


def area_color(area: str, dashboard: str = "traffic") -> str:
    if dashboard == "traffic":
        return TRAFFIC_AREA_COLORS.get(area, "#8B949E")
    return "#8B949E"


def apply_dashboard_theme(
    fig: go.Figure,
    dashboard: str = "traffic",
    role: str = "supporting",
    show_legend: bool | None = None,
) -> go.Figure:
    tokens = get_dashboard_tokens(dashboard)
    layout = get_base_layout(dashboard)
    fig.update_layout(**layout)
    legend_visible = show_legend if show_legend is not None else (role == "hero")
    fig.update_layout(
        hovermode="closest",
        hoverlabel=dict(
            bgcolor=tokens["surface_2"],
            bordercolor=tokens["border"],
            font=dict(size=12, color=tokens["text_primary"]),
            namelength=-1,
        ),
        showlegend=legend_visible,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            font=dict(size=11, color=tokens["text_muted"]),
        ),
    )
    fig.update_xaxes(
        gridcolor=tokens["border_2"],
        gridwidth=1,
        zeroline=False,
        showline=True,
        linecolor=tokens["border"],
    )
    fig.update_yaxes(
        gridcolor=tokens["border_2"],
        gridwidth=1,
        zeroline=False,
        showline=True,
        linecolor=tokens["border"],
    )
    return fig


def severity_color(value: float, dashboard: str = "traffic") -> str:
    colors = get_severity_colors(dashboard)
    if value >= 90:
        return colors["critical"]
    if value >= 60:
        return colors["warning"]
    return colors["safe"]


def empty_figure(message: str, dashboard: str = "traffic") -> go.Figure:
    tokens = get_dashboard_tokens(dashboard)
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=13, color=tokens["text_muted"]),
    )
    fig.update_layout(
        paper_bgcolor=tokens["surface"],
        plot_bgcolor=tokens["surface_2"],
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=24, r=24, t=24, b=24),
    )
    return fig
