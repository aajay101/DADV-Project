"""A-01 · Chronic Crisis Scorecard — category burden and severity context."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config.data_config import COL_AQI_CATEGORY, COL_PM25
from config.data_config import AQI_PM25_WHO_ANNUAL
from config.theme import AQI_COLOR_SEVERE, AQI_TEXT_MUTED
from utils.plotly_engine import AQI_CATEGORY_COLORS, apply_dashboard_theme, empty_figure


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No AQI crisis data", "aqi")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "aqi")
    mean_pm25 = float(data[COL_PM25].mean())
    chronic_pct = float((data[COL_PM25] > 120).mean() * 100)
    peak_pm25 = float(data[COL_PM25].max())

    order = ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]
    counts = data[COL_AQI_CATEGORY].value_counts().reindex(order, fill_value=0)
    colors = [AQI_CATEGORY_COLORS.get(cat, "#6B7280") for cat in counts.index]

    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.24, 0.76],
        vertical_spacing=0.08,
        specs=[[{"type": "indicator"}], [{"type": "xy"}]],
    )

    fig.add_trace(
        go.Indicator(
            mode="number+delta",
            value=mean_pm25,
            number={"suffix": " µg/m³", "font": {"size": 26, "color": AQI_COLOR_SEVERE}},
            title={"text": "Annual Mean PM2.5 (filtered view)", "font": {"size": 12, "color": AQI_TEXT_MUTED}},
            delta={
                "reference": AQI_PM25_WHO_ANNUAL,
                "relative": False,
                "valueformat": ".1f",
                "increasing": {"color": AQI_COLOR_SEVERE},
            },
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            x=counts.index,
            y=counts.values,
            marker=dict(color=colors),
            hovertemplate="<b>%{x}</b><br>Days: %{y}<extra></extra>",
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    fig.update_layout(
        margin=dict(l=48, r=24, t=28, b=64),
        height=cfg.get("height"),
    )
    fig.update_yaxes(title_text="Day Count", row=2, col=1)
    fig.update_xaxes(title_text="AQI Category", row=2, col=1)

    fig.add_annotation(
        xref="paper",
        yref="paper",
        x=0,
        y=1.04,
        text=(
            f"Chronic crisis rate {chronic_pct:.1f}% · Peak {peak_pm25:.1f} µg/m³ · "
            f"WHO annual guideline {AQI_PM25_WHO_ANNUAL} µg/m³"
        ),
        showarrow=False,
        font=dict(size=10, color=AQI_TEXT_MUTED),
        xanchor="left",
    )

    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "hero"), show_legend=False)
