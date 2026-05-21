"""T-01 · Saturation Command Scorecard — executive area stress profile."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config.data_config import COL_AREA
from config.theme import TRAFFIC_AMBER, TRAFFIC_CRIMSON, TRAFFIC_TEXT_MUTED
from utils.plotly_engine import apply_dashboard_theme, empty_figure, severity_color


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No area command data", "traffic")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "traffic")
    system_cong = float(data["mean_congestion"].mean())
    cap_sat = float((data["mean_capacity"] >= 99.5).mean() * 100)
    worst_area = data.loc[data["mean_congestion"].idxmax(), COL_AREA]

    data = data.sort_values("mean_congestion", ascending=True)
    colors = [severity_color(v, dashboard) for v in data["mean_congestion"]]

    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.22, 0.78],
        vertical_spacing=0.06,
        specs=[[{"type": "indicator"}], [{"type": "xy"}]],
    )

    sev_color = (
        TRAFFIC_CRIMSON
        if system_cong >= 90
        else (TRAFFIC_AMBER if system_cong >= 60 else "#2EC4B6")
    )
    fig.add_trace(
        go.Indicator(
            mode="number+delta+gauge",
            value=system_cong,
            number={"font": {"size": 28, "color": sev_color}},
            title={"text": "System Congestion Index", "font": {"size": 12, "color": TRAFFIC_TEXT_MUTED}},
            delta={"reference": 75, "relative": False, "valueformat": ".1f"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": sev_color},
                "bgcolor": "#21262D",
                "threshold": {
                    "line": {"color": TRAFFIC_CRIMSON, "width": 2},
                    "thickness": 0.75,
                    "value": 90,
                },
            },
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            x=data["mean_congestion"],
            y=data[COL_AREA],
            orientation="h",
            marker=dict(color=colors, line=dict(width=0)),
            hovertemplate="<b>%{y}</b><br>Congestion %{x:.1f}<extra></extra>",
            showlegend=False,
        ),
        row=2,
        col=1,
    )
    # Indicator subplots have no x-axis — target the bar chart axes (x2/y2) only.
    fig.add_shape(
        type="line",
        x0=90,
        x1=90,
        y0=0,
        y1=1,
        xref="x2",
        yref="y2 domain",
        line=dict(color=TRAFFIC_CRIMSON, width=1, dash="dash"),
        opacity=0.55,
        layer="below",
    )

    fig.update_layout(
        margin=dict(l=120, r=24, t=24, b=40),
        height=cfg.get("height"),
    )
    fig.update_xaxes(title_text="Mean Congestion Index", row=2, col=1)
    fig.update_yaxes(title_text="", row=2, col=1)

    fig.add_annotation(
        xref="paper",
        yref="paper",
        x=1,
        y=1.02,
        text=f"Capacity saturation {cap_sat:.0f}% · Peak stress: {worst_area}",
        showarrow=False,
        font=dict(size=10, color=TRAFFIC_TEXT_MUTED),
        xanchor="right",
    )

    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "hero"), show_legend=False)
