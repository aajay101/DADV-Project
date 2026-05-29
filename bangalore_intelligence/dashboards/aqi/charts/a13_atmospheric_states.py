"""A-13 · Rule-Based Atmospheric Regimes — regime scatter."""

import plotly.graph_objects as go

from config.data_config import COL_PM25, COL_VV
from config.theme import AQI_COLOR_GOOD, AQI_COLOR_MODERATE, AQI_COLOR_SEVERE, AQI_COLOR_VERY_POOR
from utils.formatters import hover_pm25, hover_template
from utils.plotly_engine import apply_dashboard_theme, empty_figure

REGIME_COLORS = {
    "Baseline": AQI_COLOR_MODERATE,
    "Stagnation Trap": AQI_COLOR_SEVERE,
    "Dispersive Relief": AQI_COLOR_GOOD,
    "Pressure Lock": AQI_COLOR_VERY_POOR,
}


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No atmospheric regime data", "aqi")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "aqi")
    focus_regime = cfg.get("highlight_regime")
    fig = go.Figure()
    for regime, grp in data.groupby("regime"):
        is_focus = focus_regime and regime == focus_regime
        fig.add_trace(
            go.Scatter(
                x=grp[COL_VV],
                y=grp[COL_PM25],
                mode="markers",
                name=regime,
                marker=dict(
                    size=8 if is_focus else 6,
                    color=REGIME_COLORS.get(regime, AQI_COLOR_MODERATE),
                    opacity=0.9 if is_focus else (0.18 if focus_regime else 0.55),
                    line=dict(width=1, color="#F0F6FC") if is_focus else dict(width=0),
                ),
                hovertemplate=hover_template(
                    f"<b>{regime}</b>", "VV %{x:.2f}", hover_pm25()
                ),
            )
        )

    fig.update_layout(
        xaxis_title="Vertical Visibility (VV)",
        yaxis_title="PM2.5 (µg/m³)",
        margin=dict(l=56, r=24, t=16, b=48),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "supporting"), show_legend=True)
