"""A-15 · Full Meteorological Pairplot — multivariate co-factor matrix."""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config.data_config import COL_AQI_CATEGORY, COL_H, COL_PM25, COL_SLP, COL_T, COL_TM, COL_V, COL_VV
from utils.analytics_kde import gaussian_kde_1d
from utils.plotly_engine import AQI_CATEGORY_COLORS, apply_dashboard_theme, empty_figure

PAIRPLOT_VARS = [COL_T, COL_TM, COL_SLP, COL_H, COL_VV, COL_V, COL_PM25]


def _correlation_fallback(data, dashboard, cfg):
    cols = [c for c in PAIRPLOT_VARS if c in data.columns]
    if len(cols) < 2:
        return empty_figure("Insufficient variables for correlation view", dashboard)
    corr = data[cols].corr()
    labels = [c.replace("_", " ") for c in cols]
    fig = go.Figure(
        go.Heatmap(
            z=corr.values,
            x=labels,
            y=labels,
            zmid=0,
            colorscale=[[0, "#1A2333"], [0.5, "#5A8F72"], [1.0, "#A85A5A"]],
            text=[[f"{v:.2f}" for v in row] for row in corr.values],
            texttemplate="%{text}",
            hovertemplate="%{y} × %{x}<br>r = %{z:.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        margin=dict(l=72, r=24, t=24, b=72),
        height=cfg.get("height"),
    )
    fig.add_annotation(
        text="Correlation view (insufficient rows for scatter matrix)",
        xref="paper",
        yref="paper",
        x=0.5,
        y=1.04,
        showarrow=False,
        font=dict(size=10, color="#6B7280"),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "hero"), show_legend=False)


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No pairplot data", "aqi")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "aqi")
    vars_ = [c for c in PAIRPLOT_VARS if c in data.columns]
    if len(data) < 30 or len(vars_) < 3:
        return _correlation_fallback(data, dashboard, cfg)

    sample = data.sample(min(len(data), 800), random_state=42) if len(data) > 800 else data
    n = len(vars_)
    labels = [v.replace("_", " ") for v in vars_]
    fig = make_subplots(
        rows=n,
        cols=n,
        shared_xaxes=False,
        shared_yaxes=False,
        horizontal_spacing=0.05,
        vertical_spacing=0.05,
    )

    for i, yi in enumerate(vars_):
        for j, xj in enumerate(vars_):
            row, col = i + 1, j + 1
            if i == j:
                vals = sample[yi].dropna().values
                grid = np.linspace(vals.min(), vals.max(), 40)
                if len(vals) >= 5:
                    density = gaussian_kde_1d(vals, grid)
                    fig.add_trace(
                        go.Scatter(
                            x=grid,
                            y=density,
                            mode="lines",
                            fill="tozeroy",
                            line=dict(color="rgba(168, 90, 90, 0.9)", width=1.2),
                            fillcolor="rgba(168, 90, 90, 0.35)",
                            showlegend=False,
                            hoverinfo="skip",
                        ),
                        row=row,
                        col=col,
                    )
                else:
                    fig.add_trace(
                        go.Histogram(x=vals, nbinsx=16, marker_color="rgba(168, 90, 90, 0.65)", showlegend=False),
                        row=row,
                        col=col,
                    )
            else:
                if COL_AQI_CATEGORY in sample.columns:
                    for cat in sample[COL_AQI_CATEGORY].dropna().unique():
                        sub = sample[sample[COL_AQI_CATEGORY] == cat]
                        fig.add_trace(
                            go.Scatter(
                                x=sub[xj],
                                y=sub[yi],
                                mode="markers",
                                name=cat,
                                marker=dict(
                                    size=3,
                                    color=AQI_CATEGORY_COLORS.get(cat, "#5A8F72"),
                                    opacity=0.45,
                                ),
                                showlegend=False,
                                hovertemplate="%{x:.2f} · %{y:.2f}<extra></extra>",
                            ),
                            row=row,
                            col=col,
                        )
                else:
                    fig.add_trace(
                        go.Scatter(
                            x=sample[xj],
                            y=sample[yi],
                            mode="markers",
                            marker=dict(size=3, opacity=0.4),
                            showlegend=False,
                        ),
                        row=row,
                        col=col,
                    )
            if i == n - 1:
                fig.update_xaxes(title_text=labels[j], row=row, col=col, title_font=dict(size=9))
            if j == 0:
                fig.update_yaxes(title_text=labels[i], row=row, col=col, title_font=dict(size=9))

    fig.update_layout(
        margin=dict(l=40, r=12, t=20, b=40),
        height=cfg.get("height") or 720,
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "hero"), show_legend=False)
