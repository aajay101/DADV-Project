"""A-07 · Extreme Day Radar — category meteorological profiles."""

import plotly.graph_objects as go

from config.data_config import COL_AQI_CATEGORY, COL_H, COL_SLP, COL_T, COL_TM, COL_V, COL_VV
from config.theme import AQI_COLOR_GOOD, AQI_COLOR_MODERATE, AQI_COLOR_SEVERE
from utils.plotly_engine import apply_dashboard_theme, empty_figure

PROFILE_METRICS = [COL_T, COL_TM, COL_H, COL_VV, COL_V, COL_SLP]
RADAR_LABELS = ["Temp", "Min Temp", "Humidity", "Visibility", "Wind", "Pressure"]
HIGHLIGHT_CATS = ["Good", "Moderate", "Severe"]
CAT_COLORS = {"Good": AQI_COLOR_GOOD, "Moderate": AQI_COLOR_MODERATE, "Severe": AQI_COLOR_SEVERE}


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No category profile data", "aqi")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "aqi")
    fig = go.Figure()
    for cat in HIGHLIGHT_CATS:
        row = data[data[COL_AQI_CATEGORY] == cat]
        if row.empty:
            continue
        r_vals = [float(row[m].iloc[0]) for m in PROFILE_METRICS if m in row.columns]
        if not r_vals:
            continue
        r_vals.append(r_vals[0])
        th = RADAR_LABELS + [RADAR_LABELS[0]]
        fig.add_trace(
            go.Scatterpolar(
                r=r_vals,
                theta=th,
                name=cat,
                fill="toself",
                opacity=0.35,
                line=dict(color=CAT_COLORS.get(cat, AQI_COLOR_MODERATE), width=2),
                hovertemplate="<b>%{fullData.name}</b><br>%{theta}: %{r:.0f}<extra></extra>",
            )
        )

    fig.update_layout(
        polar=dict(radialaxis=dict(range=[0, 100], showticklabels=True)),
        margin=dict(l=48, r=48, t=24, b=48),
        height=cfg.get("height"),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "supporting"), show_legend=True)
