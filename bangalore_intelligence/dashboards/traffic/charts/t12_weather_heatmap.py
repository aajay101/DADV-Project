"""T-12 · Weather × Roadwork Matrix — grouped heatmap."""

import plotly.graph_objects as go

from config.data_config import COL_ROADWORK, COL_WEATHER
from utils.plotly_engine import apply_dashboard_theme, empty_figure


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No weather–roadwork matrix", "traffic")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "traffic")
    w_col = COL_WEATHER if COL_WEATHER in data.columns else "weather"
    r_col = COL_ROADWORK if COL_ROADWORK in data.columns else "roadwork"
    pivot = data.pivot(index=w_col, columns=r_col, values="mean_congestion")
    if pivot.empty:
        return empty_figure("Insufficient matrix dimensions", "traffic")

    z = pivot.values
    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=pivot.columns.astype(str).tolist(),
            y=pivot.index.astype(str).tolist(),
            colorscale=[
                [0, "#1A1F26"],
                [0.5, "#2A9D8F"],
                [1, "#E5383B"],
            ],
            hovertemplate="Weather %{y}<br>Roadwork %{x}<br>Congestion %{z:.1f}<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis_title="Roadwork Status",
        yaxis_title="Weather",
        margin=dict(l=80, r=24, t=16, b=56),
        height=cfg.get("height"),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "supporting"), show_legend=False)
