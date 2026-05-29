"""T-14 · Volume–Congestion Density — 2D histogram."""

import plotly.graph_objects as go

from config.data_config import COL_CONGESTION, COL_TRAFFIC_VOL
from config.theme import TRAFFIC_TEXT_MUTED
from utils.formatters import hover_density_hex, hover_template
from utils.plotly_engine import apply_dashboard_theme, empty_figure, traffic_volume_axis_range


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No volume–congestion data", "traffic")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "traffic")
    x = data[COL_TRAFFIC_VOL] if COL_TRAFFIC_VOL in data.columns else data.get("traffic_volume", data.iloc[:, 0])
    y = data[COL_CONGESTION]

    fig = go.Figure(
        go.Histogram2d(
            x=x,
            y=y,
            nbinsx=20,
            nbinsy=20,
            colorscale="Reds",
            hovertemplate=hover_template(hover_density_hex()),
        )
    )
    volume_range = traffic_volume_axis_range(x)
    fig.update_layout(
        xaxis_title="Traffic Volume",
        yaxis_title="Congestion Level",
        xaxis=dict(range=list(volume_range)),
        yaxis=dict(range=[0, 100]),
        margin=dict(l=56, r=24, t=16, b=48),
    )
    sampling = getattr(data, "attrs", {}).get("sampling", {})
    if sampling.get("sampled"):
        fig.add_annotation(
            x=0.02,
            y=0.02,
            xref="paper",
            yref="paper",
            text=(
                f"Sampled {sampling.get('sample_size'):,}/{sampling.get('source_rows'):,} "
                "records · random_state=42"
            ),
            showarrow=False,
            font=dict(size=10, color=TRAFFIC_TEXT_MUTED),
            xanchor="left",
        )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "supporting"), show_legend=False)
