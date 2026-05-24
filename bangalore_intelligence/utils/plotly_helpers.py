"""Shared Plotly element builders."""


from config.theme import get_dashboard_tokens


def add_threshold_line(fig, y, label, color, dashboard="traffic"):
    fig.add_hline(y=y, line_dash="dash", line_color=color, opacity=0.7)
    tokens = get_dashboard_tokens(dashboard)
    fig.add_annotation(
        x=1.01,
        xref="paper",
        y=y,
        yref="y",
        text=label,
        showarrow=False,
        font=dict(size=10, color=tokens["text_muted"]),
        xanchor="left",
        yanchor="middle",
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
    """Quadrant archetype labels in paper margin — kept outside the plot area."""
    del x_mid, y_mid  # paper-anchored layout; mids unused but kept for call-site stability
    from config.theme import TRAFFIC_AMBER, TRAFFIC_CRIMSON, TRAFFIC_TEAL

    tokens = get_dashboard_tokens(dashboard)
    muted = tokens["text_muted"]
    labels = [
        (0.06, 0.96, "CONSTRAINED FLOW", TRAFFIC_AMBER, "left", "top"),
        (0.94, 0.96, "CRITICAL OVERLOAD", TRAFFIC_CRIMSON, "right", "top"),
        (0.06, 0.06, "OPERATIONAL BASELINE", muted, "left", "bottom"),
        (0.94, 0.06, "CAPACITY MARGIN", TRAFFIC_TEAL, "right", "bottom"),
    ]
    for x, y, text, color, xanchor, yanchor in labels:
        fig.add_annotation(
            x=x,
            y=y,
            xref="paper",
            yref="paper",
            text=text,
            showarrow=False,
            font=dict(size=10, color=color),
            opacity=0.85,
            xanchor=xanchor,
            yanchor=yanchor,
        )
    return fig


def build_hover_template(fields, labels):
    lines = [f"<b>{lbl}</b>: %{{customdata[{i}]}}" for i, lbl in enumerate(labels)]
    return "<br>".join(lines) + "<extra></extra>"
