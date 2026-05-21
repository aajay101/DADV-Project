"""Shared Plotly element builders."""

import plotly.graph_objects as go

from config.theme import get_dashboard_tokens


def add_threshold_line(fig, y, label, color, dashboard="traffic"):
    fig.add_hline(y=y, line_dash="dash", line_color=color, opacity=0.7)
    tokens = get_dashboard_tokens(dashboard)
    fig.add_annotation(
        x=1,
        xref="paper",
        y=y,
        text=label,
        showarrow=False,
        font=dict(size=10, color=tokens["text_muted"]),
        xanchor="right",
    )
    return fig


def add_quadrant_lines(fig, x_val, y_val, dashboard="traffic"):
    tokens = get_dashboard_tokens(dashboard)
    color = tokens["border"]
    fig.add_vline(x=x_val, line_dash="dot", line_color=color, opacity=0.5)
    fig.add_hline(y=y_val, line_dash="dot", line_color=color, opacity=0.5)
    return fig


def add_quadrant_zone_labels(
    fig,
    x_mid: float,
    y_mid: float,
    dashboard: str = "traffic",
):
    """Permanent quadrant archetype labels for operational scatter charts."""
    from config.theme import TRAFFIC_AMBER, TRAFFIC_CRIMSON, TRAFFIC_TEAL

    tokens = get_dashboard_tokens(dashboard)
    muted = tokens["text_muted"]
    labels = [
        (x_mid * 0.45, y_mid * 1.35, "CONSTRAINED FLOW", TRAFFIC_AMBER),
        (x_mid * 1.55, y_mid * 1.35, "CRITICAL OVERLOAD", TRAFFIC_CRIMSON),
        (x_mid * 0.45, y_mid * 0.55, "OPERATIONAL BASELINE", muted),
        (x_mid * 1.55, y_mid * 0.55, "CAPACITY MARGIN", TRAFFIC_TEAL),
    ]
    for x, y, text, color in labels:
        fig.add_annotation(
            x=x,
            y=y,
            text=text,
            showarrow=False,
            font=dict(size=10, color=color),
            opacity=0.75,
        )
    return fig


def build_hover_template(fields, labels):
    lines = [f"<b>{lbl}</b>: %{{customdata[{i}]}}" for i, lbl in enumerate(labels)]
    return "<br>".join(lines) + "<extra></extra>"
