"""T-02 · Parallel Coordinates Intelligence — multivariate area profiling."""

import plotly.graph_objects as go

from config.data_config import COL_AREA
from filters.interaction import trace_opacity
from utils.plotly_engine import apply_dashboard_theme, empty_figure


def _line_opacity(area: str, config: dict) -> float:
    return trace_opacity(area, config.get("highlight_area"), base=0.42)


DEFAULT_DIMS = [
    ("mean_congestion", "Congestion"),
    ("mean_speed", "Speed"),
    ("total_incidents", "Incidents"),
]


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No multivariate area data", "traffic")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "traffic")
    dims = cfg.get("dimensions", DEFAULT_DIMS)

    fig = go.Figure()
    frame = data.copy()
    for col, _ in dims:
        mu = frame[col].mean()
        sd = frame[col].std() or 1.0
        frame[col] = (frame[col] - mu) / sd

    for _, row in frame.iterrows():
        area = row[COL_AREA]
        values = [float(row[col]) for col, _ in dims]
        fig.add_trace(
            go.Scatter(
                x=list(range(len(dims))),
                y=values,
                mode="lines+markers",
                name=area,
                line=dict(width=2.5 if cfg.get("highlight_area") == area else 1.5),
                marker=dict(size=6),
                opacity=_line_opacity(area, cfg),
                hovertemplate="<b>%{fullData.name}</b><extra></extra>",
            )
        )

    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(len(dims))),
            ticktext=[label for _, label in dims],
            title="",
        ),
        yaxis=dict(title="Normalized scale (z-score per dimension)", showgrid=True),
        margin=dict(l=48, r=24, t=24, b=64),
        height=cfg.get("height"),
    )
    fig.add_annotation(
        text="Hover legend entries to isolate · 3-axis investigative view",
        xref="paper",
        yref="paper",
        x=0,
        y=-0.18,
        showarrow=False,
        font=dict(size=11),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "supporting"), show_legend=True)
