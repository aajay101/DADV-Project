"""T-11 · Road congestion distribution — 4×4 small-multiple histograms."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config.data_config import COL_AREA, COL_ROAD
from config.theme import TRAFFIC_TEXT_MUTED
from utils.formatters import fmt_congestion, hover_congestion, hover_template
from utils.plotly_engine import apply_dashboard_theme, area_color, empty_figure

_GRID_ROWS = 4
_GRID_COLS = 4
_MAX_PANELS = _GRID_ROWS * _GRID_COLS


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No road distribution data", "traffic")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "traffic")
    highlight = cfg.get("highlight_area")

    if "values" in data.columns:
        profiles = data.sort_values("median", ascending=False).head(_MAX_PANELS)
    else:
        from data_layer.traffic_transforms import get_road_distribution_profiles

        profiles = get_road_distribution_profiles(data)

    if profiles.empty:
        return empty_figure("No road distribution data", "traffic")

    roads = profiles.head(_MAX_PANELS)
    titles = [
        f"{row[COL_ROAD]} ({row[COL_AREA]})" for _, row in roads.iterrows()
    ]
    while len(titles) < _MAX_PANELS:
        titles.append("")

    fig = make_subplots(
        rows=_GRID_ROWS,
        cols=_GRID_COLS,
        subplot_titles=titles,
        vertical_spacing=0.12,
        horizontal_spacing=0.08,
    )

    for idx, (_, row) in enumerate(roads.iterrows()):
        if idx >= _MAX_PANELS:
            break
        r = idx // _GRID_COLS + 1
        c = idx % _GRID_COLS + 1
        area = row[COL_AREA]
        vals = row["values"]
        if hasattr(vals, "tolist"):
            vals = vals.tolist()
        color = area_color(area, dashboard)
        opacity = 0.85 if (not highlight or area == highlight) else 0.25

        fig.add_trace(
            go.Histogram(
                x=vals,
                nbinsx=12,
                marker=dict(color=color, line=dict(width=0.5, color="#21262D")),
                opacity=opacity,
                showlegend=False,
                hovertemplate=hover_template(
                    f"<b>{row[COL_ROAD]}</b> ({area})",
                    hover_congestion("x"),
                    f"Median {fmt_congestion(row['median'])}",
                    f"Q25–Q75 {row['q25']:.1f}–{row['q75']:.1f}",
                ),
            ),
            row=r,
            col=c,
        )
        fig.add_vline(
            x=float(row["median"]),
            line_dash="dot",
            line_color=color,
            opacity=0.9,
            row=r,
            col=c,
        )

    fig.update_xaxes(range=[0, 100], title_text="", showticklabels=True)
    fig.update_yaxes(showticklabels=False, title_text="")
    fig.update_layout(
        margin=dict(l=48, r=24, t=48, b=40),
        height=720,
    )
    fig.add_annotation(
        xref="paper",
        yref="paper",
        x=0,
        y=-0.06,
        text=f"16-road distribution grid · {len(roads)} panels in filter scope · dotted line = median",
        showarrow=False,
        font=dict(size=10, color=TRAFFIC_TEXT_MUTED),
        xanchor="left",
    )
    return apply_dashboard_theme(
        fig,
        dashboard,
        role=cfg.get("role", "hero"),
        show_legend=False,
        chart_type="ridgeline",
    )
