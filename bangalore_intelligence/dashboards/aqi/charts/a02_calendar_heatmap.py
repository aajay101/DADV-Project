"""A-02 · 3-Year AQI Calendar Heatmap."""

import plotly.graph_objects as go

from config.data_config import COL_PM25
from utils.formatters import hover_pm25, hover_template
from utils.plotly_engine import AQI_CATEGORY_COLORS, apply_dashboard_theme, empty_figure


def _pm25_to_color(pm25: float) -> str:
    if pm25 <= 30:
        return AQI_CATEGORY_COLORS["Good"]
    if pm25 <= 60:
        return AQI_CATEGORY_COLORS["Satisfactory"]
    if pm25 <= 90:
        return AQI_CATEGORY_COLORS["Moderate"]
    if pm25 <= 120:
        return AQI_CATEGORY_COLORS["Poor"]
    if pm25 <= 250:
        return AQI_CATEGORY_COLORS["Very Poor"]
    return AQI_CATEGORY_COLORS["Severe"]


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No calendar data available", "aqi")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "aqi")
    highlight_year = cfg.get("highlight_year")
    highlight_week = cfg.get("highlight_week")
    years = sorted(data["year"].unique())
    max_week = int(data["week"].max())

    z_text = []
    z_color = []
    y_labels = [str(y) for y in years]

    for year in years:
        row_pm25 = []
        row_colors = []
        year_df = data[data["year"] == year]
        for week in range(1, max_week + 1):
            cell = year_df[year_df["week"] == week]
            if cell.empty:
                row_pm25.append(None)
                row_colors.append("#111827")
            else:
                val = float(cell[COL_PM25].mean())
                row_pm25.append(val)
                row_colors.append(_pm25_to_color(val))
        z_text.append(row_pm25)
        z_color.append(row_colors)

    opacity = 1.0
    if highlight_year is not None and highlight_week is not None:
        opacity = [
            [
                1.0
                if str(y) == str(highlight_year) and x == highlight_week
                else 0.35
                for x in range(1, max_week + 1)
            ]
            for y in y_labels
        ]

    fig = go.Figure(
        go.Heatmap(
            z=z_text,
            x=list(range(1, max_week + 1)),
            y=y_labels,
            opacity=opacity,
            colorscale=[
                [0, AQI_CATEGORY_COLORS["Good"]],
                [0.2, AQI_CATEGORY_COLORS["Satisfactory"]],
                [0.4, AQI_CATEGORY_COLORS["Moderate"]],
                [0.6, AQI_CATEGORY_COLORS["Poor"]],
                [0.8, AQI_CATEGORY_COLORS["Very Poor"]],
                [1, AQI_CATEGORY_COLORS["Severe"]],
            ],
            hovertemplate=hover_template("Year %{y} · Week %{x}", f"{hover_pm25('z')}"),
            showscale=True,
            colorbar=dict(title="PM2.5", thickness=12, len=0.6),
        )
    )
    fig.update_layout(
        xaxis_title="Week of Year",
        yaxis_title="Year",
        margin=dict(l=56, r=80, t=16, b=48),
    )
    return apply_dashboard_theme(fig, dashboard)
