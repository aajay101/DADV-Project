"""A-04 · Temporal AQI Calendar — month × year environmental rhythm."""

import plotly.graph_objects as go

from utils.plotly_engine import AQI_CATEGORY_COLORS, apply_dashboard_theme, empty_figure


def _pm25_color(val: float) -> str:
    if val <= 30:
        return AQI_CATEGORY_COLORS["Good"]
    if val <= 60:
        return AQI_CATEGORY_COLORS["Satisfactory"]
    if val <= 90:
        return AQI_CATEGORY_COLORS["Moderate"]
    if val <= 120:
        return AQI_CATEGORY_COLORS["Poor"]
    if val <= 250:
        return AQI_CATEGORY_COLORS["Very Poor"]
    return AQI_CATEGORY_COLORS["Severe"]


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No temporal calendar data", "aqi")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "aqi")
    years = sorted(data["year"].unique())
    months = list(range(1, 13))
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    z = []
    for year in years:
        row = []
        for month in months:
            cell = data[(data["year"] == year) & (data["month"] == month)]
            row.append(float(cell["mean_pm25"].iloc[0]) if not cell.empty else None)
        z.append(row)

    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=month_names,
            y=[str(y) for y in years],
            colorscale=[
                [0, AQI_CATEGORY_COLORS["Good"]],
                [0.2, AQI_CATEGORY_COLORS["Satisfactory"]],
                [0.4, AQI_CATEGORY_COLORS["Moderate"]],
                [0.6, AQI_CATEGORY_COLORS["Poor"]],
                [0.8, AQI_CATEGORY_COLORS["Very Poor"]],
                [1, AQI_CATEGORY_COLORS["Severe"]],
            ],
            hovertemplate="%{y} · %{x}<br>Mean PM2.5 %{z:.1f} µg/m³<extra></extra>",
            showscale=True,
            colorbar=dict(title="PM2.5", thickness=12, len=0.6),
        )
    )
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Year",
        margin=dict(l=56, r=80, t=16, b=48),
        height=cfg.get("height"),
    )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "supporting"), show_legend=False)
