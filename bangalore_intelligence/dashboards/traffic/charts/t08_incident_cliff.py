"""T-08 · First Incident Cliff — step threshold chart."""

import plotly.graph_objects as go

from config.theme import TRAFFIC_AMBER, TRAFFIC_CRIMSON, TRAFFIC_TEXT_MUTED
from utils.formatters import hover_congestion, hover_template
from utils.plotly_engine import apply_dashboard_theme, empty_figure
from utils.plotly_helpers import add_threshold_line


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No incident band data available", "traffic")

    dashboard = (config or {}).get("dashboard", "traffic")
    fig = go.Figure(
        go.Scatter(
            x=data["incident_band"],
            y=data["mean_congestion"],
            mode="lines+markers",
            line=dict(shape="hv", color=TRAFFIC_CRIMSON, width=2.5),
            marker=dict(size=9, color=TRAFFIC_CRIMSON),
            hovertemplate=hover_template("Incidents: %{x}", f"Mean {hover_congestion()}"),
        )
    )

    if len(data) >= 2:
        delta = data["mean_congestion"].iloc[1] - data["mean_congestion"].iloc[0]
        fig.add_annotation(
            x=data["incident_band"].iloc[1],
            y=data["mean_congestion"].iloc[1],
            text=f"+{delta:.1f} pts",
            showarrow=True,
            arrowhead=2,
            font=dict(size=11, color=TRAFFIC_AMBER),
            ax=40,
            ay=-42,
            yshift=8,
        )

    fig.update_layout(
        xaxis_title="Incident Reports (band)",
        yaxis_title="Mean Congestion Index",
    )
    add_threshold_line(fig, 75, "Congestion threshold 75", TRAFFIC_TEXT_MUTED, dashboard)
    return apply_dashboard_theme(fig, dashboard)
