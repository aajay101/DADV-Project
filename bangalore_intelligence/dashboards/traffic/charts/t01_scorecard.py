"""T-01 · Network congestion scorecard — bullet summary and area ranking."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config.data_config import COL_AREA
from config.theme import TRAFFIC_AMBER, TRAFFIC_CRIMSON, TRAFFIC_TEAL, TRAFFIC_TEXT_MUTED
from utils.formatters import hover_congestion, hover_template
from utils.plotly_engine import apply_dashboard_theme, empty_figure, severity_color

_BULLET_BANDS = (
    (0, 50, TRAFFIC_TEAL),
    (50, 75, TRAFFIC_AMBER),
    (75, 100, TRAFFIC_CRIMSON),
)


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No area command data", "traffic")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "traffic")
    system_cong = float(cfg.get("system_congestion", data["mean_congestion"].mean()))
    cap_sat = float(
        cfg.get("capacity_saturation_rate", (data["mean_capacity"] >= 99.5).mean() * 100)
    )
    worst_area = data.loc[data["mean_congestion"].idxmax(), COL_AREA]
    prior_cong = cfg.get("prior_system_congestion")

    data = data.sort_values("mean_congestion", ascending=True)
    colors = [severity_color(v, dashboard) for v in data["mean_congestion"]]

    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.22, 0.78],
        vertical_spacing=0.14,
        specs=[[{"type": "xy"}], [{"type": "xy"}]],
    )

    sev_color = severity_color(system_cong, dashboard)
    for x0, x1, band_color in _BULLET_BANDS:
        fig.add_shape(
            type="rect",
            x0=x0,
            x1=x1,
            y0=-0.35,
            y1=0.35,
            fillcolor=band_color,
            opacity=0.22,
            line_width=0,
            row=1,
            col=1,
        )

    fig.add_trace(
        go.Scatter(
            x=[system_cong],
            y=[0],
            mode="markers",
            marker=dict(size=14, color=sev_color, symbol="diamond", line=dict(width=1, color="#F0F6FC")),
            name="System Congestion",
            showlegend=False,
            hovertemplate=hover_template(
                "System Congestion",
                hover_congestion("x"),
            ),
        ),
        row=1,
        col=1,
    )

    if prior_cong is not None:
        fig.add_trace(
            go.Scatter(
                x=[float(prior_cong)],
                y=[0],
                mode="markers",
                marker=dict(size=10, color=TRAFFIC_TEXT_MUTED, symbol="line-ns-open", line=dict(width=2)),
                name="Prior period",
                showlegend=False,
                hovertemplate="Prior mean: %{x:.1f}<extra></extra>",
            ),
            row=1,
            col=1,
        )

    fig.add_vline(
        x=75,
        line_dash="dot",
        line_color=TRAFFIC_CRIMSON,
        opacity=0.45,
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            x=data["mean_congestion"],
            y=data[COL_AREA],
            orientation="h",
            marker=dict(color=colors, line=dict(width=0)),
            hovertemplate=hover_template("<b>%{y}</b>", hover_congestion("x")),
            showlegend=False,
        ),
        row=2,
        col=1,
    )

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

    fig.update_xaxes(range=[0, 100], title_text="", row=1, col=1)
    fig.update_yaxes(visible=False, showticklabels=False, range=[-0.5, 0.5], row=1, col=1)
    fig.add_annotation(
        text="System Congestion Index",
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.92,
        showarrow=False,
        font=dict(size=11, color=TRAFFIC_TEXT_MUTED),
        xanchor="center",
    )
    fig.update_xaxes(range=[0, 100], title_text="Mean Congestion Index", row=2, col=1)
    fig.update_yaxes(title_text="", row=2, col=1)

    fig.update_layout(margin=dict(l=120, r=40, t=56, b=48))
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
