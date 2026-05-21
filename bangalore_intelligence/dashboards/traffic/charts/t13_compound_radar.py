"""T-13 · Compound Stress Radar — normalized multi-metric area comparison."""

import pandas as pd
import plotly.graph_objects as go

from config.data_config import COL_AREA
from config.theme import TRAFFIC_CRIMSON, TRAFFIC_TEAL, TRAFFIC_TEXT_MUTED
from utils.plotly_engine import apply_dashboard_theme, empty_figure


def radar_trace_areas(data, config=None) -> list[str]:
    """Area names in trace order — used for click handler metadata."""
    cfg = config or {}
    focus = cfg.get("focus_area") or cfg.get("highlight_area")
    max_overlays = int(cfg.get("max_overlays", 4))
    metrics = [c for c in data.columns if c != COL_AREA and c.endswith("_norm")]
    plot_data = data.copy()
    if metrics:
        plot_data["composite_stress"] = plot_data[metrics].mean(axis=1)
    else:
        plot_data["composite_stress"] = 50.0
    plot_data = plot_data.nlargest(max_overlays, "composite_stress")
    if focus and focus in set(data[COL_AREA]):
        focus_row = data[data[COL_AREA] == focus]
        others = plot_data[plot_data[COL_AREA] != focus]
        plot_data = _concat_focus(focus_row, others, max_overlays)
    return [str(a) for a in plot_data[COL_AREA].tolist()]


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No radar metrics", "traffic")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "traffic")
    focus = cfg.get("focus_area") or cfg.get("highlight_area")
    max_overlays = int(cfg.get("max_overlays", 4))

    metrics = [c for c in data.columns if c != COL_AREA and c.endswith("_norm")]
    if not metrics:
        metrics = [c for c in data.columns if c != COL_AREA and c != "composite_stress"]

    plot_data = data.copy()
    if metrics:
        plot_data["composite_stress"] = plot_data[metrics].mean(axis=1)
    else:
        plot_data["composite_stress"] = 50.0

    plot_data = plot_data.nlargest(max_overlays, "composite_stress")
    if focus and focus in set(data[COL_AREA]):
        focus_row = data[data[COL_AREA] == focus]
        others = plot_data[plot_data[COL_AREA] != focus]
        plot_data = _concat_focus(focus_row, others, max_overlays)

    theta = [m.replace("_norm", "").replace("_", " ").title() for m in metrics]
    if not theta:
        theta = ["Stress Index"]

    fig = go.Figure()
    palette = [TRAFFIC_CRIMSON, TRAFFIC_TEAL, "#F4A261", "#9B5DE5"]

    for i, (_, row) in enumerate(plot_data.iterrows()):
        area = str(row[COL_AREA])
        r_vals = [float(row[m]) for m in metrics] if metrics else [float(row["composite_stress"])]
        r_vals.append(r_vals[0])
        th = theta + [theta[0]]
        is_focus = focus and area == focus
        fig.add_trace(
            go.Scatterpolar(
                r=r_vals,
                theta=th,
                name=area,
                fill="toself",
                opacity=0.82 if is_focus else 0.28,
                line=dict(
                    color=palette[i % len(palette)],
                    width=3 if is_focus else 1.5,
                ),
                hovertemplate="<b>%{fullData.name}</b><br>%{theta}: %{r:.0f}<extra></extra>",
            )
        )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(range=[0, 100], tickvals=[0, 25, 50, 75, 100], showticklabels=True),
        ),
        margin=dict(l=48, r=48, t=24, b=48),
        height=cfg.get("height"),
    )
    if len(data) > max_overlays:
        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=0,
            y=1.06,
            text=f"Showing top {max_overlays} stress areas · {len(data)} total",
            showarrow=False,
            font=dict(size=10, color=TRAFFIC_TEXT_MUTED),
        )
    return apply_dashboard_theme(fig, dashboard, role=cfg.get("role", "hero"), show_legend=True)


def _concat_focus(focus_row: pd.DataFrame, others: pd.DataFrame, max_overlays: int) -> pd.DataFrame:
    others = others.head(max(0, max_overlays - len(focus_row)))
    return pd.concat([focus_row, others], ignore_index=True)
