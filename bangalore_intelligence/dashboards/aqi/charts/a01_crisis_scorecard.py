"""A-01 · PM2.5 Burden and Category Mix — category burden and reference context."""

import plotly.graph_objects as go

from config.data_config import COL_AQI_CATEGORY
from utils.formatters import hover_days_count, hover_template
from utils.plotly_engine import AQI_CATEGORY_COLORS, apply_dashboard_theme, empty_figure

_A01_BAR_DOMAIN_Y = [0, 1]


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No PM2.5 burden data", "aqi")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "aqi")
    order = ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]
    counts = data[COL_AQI_CATEGORY].value_counts().reindex(order, fill_value=0)
    colors = [AQI_CATEGORY_COLORS.get(cat, "#6B7280") for cat in counts.index]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=counts.index,
            y=counts.values,
            marker=dict(color=colors),
            hovertemplate=hover_template("<b>%{x}</b>", hover_days_count()),
            showlegend=False,
        ),
    )

    fig.update_layout(
        margin=dict(l=48, r=24, t=16, b=56),
        yaxis=dict(domain=_A01_BAR_DOMAIN_Y, title_text="Day Count"),
        xaxis=dict(title_text="AQI Category"),
    )

    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "hero"), show_legend=False)
