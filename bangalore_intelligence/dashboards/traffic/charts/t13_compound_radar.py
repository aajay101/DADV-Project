"""T-13 · Area stress profile — heatmap default, optional radar overlay."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from config.data_config import COL_AREA
from config.theme import TRAFFIC_CRIMSON, TRAFFIC_TEAL, TRAFFIC_TEXT_MUTED
from utils.formatters import hover_radar_theta_r, hover_template
from utils.plotly_engine import HEATMAP_SCALE_TRAFFIC, apply_dashboard_theme, empty_figure


def radar_trace_areas(data: pd.DataFrame, config=None) -> list[str]:
    """Area names in trace order — used for radar click handler metadata."""
    cfg = config or {}
    focus = cfg.get("focus_area") or cfg.get("highlight_area")
    max_overlays = int(cfg.get("max_overlays", 4))
    metrics = [c for c in data.columns if c != COL_AREA and c.endswith("_norm")]
    plot_data = data.copy()
    if metrics:
        plot_data["composite_stress"] = plot_data[metrics].mean(axis=1)
    else:
        plot_data["composite_stress"] = 50.0
    visible_areas = cfg.get("visible_areas") or []
    if visible_areas:
        allowed = [a for a in visible_areas if a in set(data[COL_AREA])][:max_overlays]
        if allowed:
            plot_data = data[data[COL_AREA].isin(allowed)].copy()
            if metrics:
                plot_data["composite_stress"] = plot_data[metrics].mean(axis=1)
        else:
            plot_data = plot_data.nlargest(max_overlays, "composite_stress")
    else:
        plot_data = plot_data.nlargest(max_overlays, "composite_stress")
    if focus and focus in set(data[COL_AREA]):
        focus_row = data[data[COL_AREA] == focus]
        others = plot_data[plot_data[COL_AREA] != focus]
        plot_data = _concat_focus(focus_row, others, max_overlays)
    return [str(a) for a in plot_data[COL_AREA].tolist()]


def _trace_opacity(area: str, cfg: dict) -> float:
    focus = cfg.get("focus_area") or cfg.get("highlight_area")
    dimmed = set(cfg.get("dimmed_areas") or [])
    if area in dimmed:
        return 0.08
    if focus:
        return 0.92 if area == focus else 0.22
    return 0.55


def _hex_fill_rgba(hex_color: str, alpha: float) -> str:
    h = str(hex_color).lstrip("#")
    if len(h) != 6:
        return f"rgba(136,166,255,{alpha})"
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{alpha})"


def _trace_width(area: str, cfg: dict) -> float:
    focus = cfg.get("focus_area") or cfg.get("highlight_area")
    if focus and area == focus:
        return 3.5
    return 1.4


def render_heatmap(data: dict | None, config=None):
    if not data or not data.get("areas"):
        return empty_figure("No area stress heatmap data", "traffic")

    cfg = config or {}
    dashboard = cfg.get("dashboard", "traffic")
    focus = cfg.get("focus_area") or cfg.get("highlight_area")

    areas = data["areas"]
    metrics = data["metrics"]
    z = data["z"]
    text = data["text"]

    opacity = []
    for area in areas:
        if not focus:
            opacity.append(1.0)
        elif area == focus:
            opacity.append(1.0)
        else:
            opacity.append(0.35)

    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=metrics,
            y=areas,
            text=text,
            texttemplate="%{text}",
            textfont=dict(size=9),
            colorscale=HEATMAP_SCALE_TRAFFIC,
            colorbar=dict(title="Stress index", len=0.82, thickness=14, x=1.03, xpad=4),
            hovertemplate="Area %{y}<br>%{x}: %{z:.1f} stress<br>Raw %{text}<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis_title="Normalized stress dimension",
        yaxis_title="Area",
    )
    return apply_dashboard_theme(
        fig,
        dashboard,
        role=cfg.get("role", "hero"),
        show_legend=False,
        chart_type="heatmap",
    )


def render_radar(data: pd.DataFrame, config=None):
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

    visible_areas = cfg.get("visible_areas") or []
    if visible_areas:
        allowed = [a for a in visible_areas if a in set(data[COL_AREA])][:max_overlays]
        if allowed:
            plot_data = data[data[COL_AREA].isin(allowed)].copy()
            if metrics:
                plot_data["composite_stress"] = plot_data[metrics].mean(axis=1)
        else:
            plot_data = plot_data.nlargest(max_overlays, "composite_stress")
    else:
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
        line_color = palette[i % len(palette)]
        fill_alpha = 0.14 if focus and area == focus else 0.07
        fig.add_trace(
            go.Scatterpolar(
                r=r_vals,
                theta=th,
                name=area,
                fill="toself",
                fillcolor=_hex_fill_rgba(line_color, fill_alpha),
                opacity=_trace_opacity(area, cfg),
                line=dict(
                    color=line_color,
                    width=_trace_width(area, cfg),
                ),
                hovertemplate=hover_template("<b>%{fullData.name}</b>", hover_radar_theta_r()),
            )
        )

    from config.theme import get_dashboard_tokens

    surface = get_dashboard_tokens(dashboard)["surface"]
    fig.update_layout(
        polar=dict(
            bgcolor=surface,
            radialaxis=dict(
                range=[0, 100],
                tickvals=[0, 25, 50, 75, 100],
                showticklabels=True,
                tickfont=dict(size=10),
                gridcolor="rgba(139,148,158,0.25)",
            ),
            angularaxis=dict(tickfont=dict(size=10), gridcolor="rgba(139,148,158,0.2)"),
        ),
    )
    if len(data) > max_overlays:
        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=0.5,
            y=1.02,
            xanchor="center",
            yanchor="bottom",
            text=f"Showing top {max_overlays} stress areas · {len(data)} total",
            showarrow=False,
            font=dict(size=10, color=TRAFFIC_TEXT_MUTED),
        )
    return apply_dashboard_theme(
        fig,
        dashboard,
        role=cfg.get("role", "hero"),
        show_legend=True,
        chart_type="radar",
    )


def render(data, config=None):
    """Default T-13 view: normalized area stress heatmap."""
    cfg = config or {}
    if cfg.get("view") == "radar" and isinstance(data, pd.DataFrame):
        return render_radar(data, config)
    if isinstance(data, dict):
        return render_heatmap(data, config)
    if isinstance(data, pd.DataFrame) and cfg.get("view") == "heatmap":
        from data_layer.traffic_transforms import get_area_stress_heatmap

        return render_heatmap(get_area_stress_heatmap(data), config)
    return render_radar(data, config)


def _concat_focus(focus_row: pd.DataFrame, others: pd.DataFrame, max_overlays: int) -> pd.DataFrame:
    others = others.head(max(0, max_overlays - len(focus_row)))
    return pd.concat([focus_row, others], ignore_index=True)
