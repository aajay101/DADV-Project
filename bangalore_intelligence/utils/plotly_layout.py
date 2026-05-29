"""Plotly layout normalization — margins, legends, autosize, density governance."""

from __future__ import annotations


import plotly.graph_objects as go

from components.layout.responsive import Breakpoint, get_active_breakpoint
from config.chart_defaults import CHART_LAYOUT_TYPE_BY_CODE

# Margin presets (spacing tokens — do not scatter per chart)
MARGIN_DEFAULT = dict(l=64, r=40, t=48, b=96)
MARGIN_RADAR = dict(l=72, r=72, t=52, b=120)
MARGIN_PAIRPLOT = dict(l=60, r=36, t=48, b=72)
MARGIN_PARCOORDS = dict(l=64, r=36, t=44, b=128)
MARGIN_RIDGELINE = dict(l=64, r=32, t=44, b=88)
MARGIN_HEATMAP = dict(l=64, r=32, t=48, b=88)
MARGIN_HEATMAP_DENSE = dict(l=68, r=36, t=52, b=104)
MARGIN_COMPACT = dict(l=56, r=28, t=36, b=76)
MARGIN_SCATTER_DENSE = dict(l=64, r=40, t=48, b=104)
MARGIN_TIMESERIES = dict(l=64, r=52, t=56, b=112)
MARGIN_SCORECARD = dict(l=48, r=28, t=20, b=64)

MARGIN_BY_TYPE: dict[str, dict[str, int]] = {
    "default": MARGIN_DEFAULT,
    "radar": MARGIN_RADAR,
    "pairplot": MARGIN_PAIRPLOT,
    "parcoords": MARGIN_PARCOORDS,
    "ridgeline": MARGIN_RIDGELINE,
    "heatmap_small": MARGIN_HEATMAP,
    "heatmap": MARGIN_HEATMAP_DENSE,
    "compact": MARGIN_COMPACT,
    "scatter_dense": MARGIN_SCATTER_DENSE,
    "matrix": MARGIN_COMPACT,
    "timeseries": MARGIN_TIMESERIES,
    "scorecard": MARGIN_SCORECARD,
}

_FULLSCREEN_MARGIN_BOOST = dict(t=20, b=24, l=8, r=8)

# Targeted responsive stabilization (listed modules only).
_CHART_MARGIN_PATCHES: dict[str, dict[str, int]] = {
    "T-02": {"b": 148, "r": 128, "t": 52},
    "T-03": {"b": 116, "t": 58, "r": 56},
    "T-13": {"l": 132, "r": 56, "t": 44, "b": 80},
    "A-02": {"b": 100, "t": 48, "r": 40},
    "A-03": {"b": 96, "t": 44, "l": 56},
    "A-05": {"b": 88, "t": 52, "r": 40, "l": 60},
    "A-01": {"t": 8, "b": 60, "l": 48, "r": 24},
}


def chart_layout_type(chart_id: str | None) -> str:
    if not chart_id:
        return "default"
    return CHART_LAYOUT_TYPE_BY_CODE.get(chart_id, "default")


def _legend_below(fig: go.Figure, tokens: dict, *, y: float = -0.22, orientation: str = "h") -> None:
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation=orientation,
            yanchor="top",
            y=y,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            font=dict(size=10, color=tokens["text_muted"]),
            tracegroupgap=6,
        ),
    )


def _legend_right(fig: go.Figure, tokens: dict) -> None:
    fig.update_layout(
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.04,
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            font=dict(size=10, color=tokens["text_muted"]),
        ),
        margin=dict(r=132),
    )


def _apply_fullscreen_margins(margin: dict[str, int]) -> dict[str, int]:
    out = dict(margin)
    for key, boost in _FULLSCREEN_MARGIN_BOOST.items():
        out[key] = out.get(key, 0) + boost
    return out


def normalize_figure_for_display(
    fig: go.Figure,
    *,
    dashboard: str = "traffic",
    chart_type: str = "default",
    role: str = "supporting",
    is_fullscreen: bool = False,
    breakpoint: Breakpoint | None = None,
    show_legend: bool | None = None,
    chart_id: str | None = None,
) -> go.Figure:
    """Apply blueprint margins, legend placement, axis standoff, and overflow safety."""
    from config.theme import get_dashboard_tokens

    bp = breakpoint or get_active_breakpoint()
    tokens = get_dashboard_tokens(dashboard)
    margin = dict(MARGIN_BY_TYPE.get(chart_type, MARGIN_DEFAULT))
    if chart_type == "scatter_dense":
        margin["t"] = max(margin.get("t", 48), 56)
        margin["r"] = max(margin.get("r", 40), 52)
    if chart_type == "compact" and chart_id in ("T-08", "T-01"):
        margin["b"] = max(margin.get("b", 76), 88)
        margin["t"] = max(margin.get("t", 36), 52)
    if chart_id and chart_id in _CHART_MARGIN_PATCHES:
        for key, val in _CHART_MARGIN_PATCHES[chart_id].items():
            margin[key] = max(margin.get(key, 0), val)
    if is_fullscreen:
        margin = _apply_fullscreen_margins(margin)

    fig.update_layout(
        autosize=True,
        height=None,
        margin=margin,
        paper_bgcolor=tokens["bg"],
        plot_bgcolor=tokens["surface"],
    )

    standoff = 14 if bp in ("compact", "tablet") else 18
    fig.update_xaxes(
        automargin=True,
        title_standoff=standoff,
        tickangle=-45 if bp == "compact" and chart_type in ("heatmap_small", "heatmap", "pairplot") else 0,
    )
    fig.update_yaxes(automargin=True, title_standoff=standoff)

    legend_on = show_legend if show_legend is not None else bool(fig.layout.showlegend)
    if not legend_on:
        fig.update_layout(showlegend=False)
        return fig

    trace_count = len(fig.data)
    if trace_count <= 1 and chart_type not in ("parcoords", "radar"):
        fig.update_layout(showlegend=False)
        return fig

    if chart_type == "radar":
        _legend_below(fig, tokens, y=-0.26 if chart_id == "T-13" else -0.3 if bp == "compact" else -0.24)
        fig.update_layout(
            margin=dict(margin, b=max(margin["b"], 132), t=max(margin.get("t", 52), 60)),
        )
        return fig

    if chart_type == "parcoords":
        if chart_id == "T-02" or bp in ("compact", "tablet") or trace_count > 6:
            _legend_below(fig, tokens, y=-0.28 if chart_id == "T-02" else -0.34)
            fig.update_layout(margin=dict(margin, b=max(margin["b"], 152 if chart_id == "T-02" else 140)))
        else:
            _legend_right(fig, tokens)
        return fig

    if chart_type in ("heatmap", "heatmap_small"):
        _legend_below(fig, tokens, y=-0.24 if is_fullscreen else -0.2)
        fig.update_layout(margin=dict(margin, b=max(margin["b"], 108 if is_fullscreen else 96)))
        return fig

    if bp in ("compact", "tablet") or trace_count > 6:
        _legend_below(fig, tokens, y=-0.22 if role == "hero" else -0.2)
        fig.update_layout(margin=dict(margin, b=max(margin["b"], 112)))
    elif chart_type in ("scatter_dense", "ridgeline"):
        _legend_below(fig, tokens, y=-0.18)
        fig.update_layout(margin=dict(margin, b=max(margin["b"], 104)))
    else:
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.04,
                xanchor="right",
                x=1,
                bgcolor="rgba(0,0,0,0)",
                borderwidth=0,
                font=dict(size=11, color=tokens["text_muted"]),
            ),
            margin=dict(margin, t=max(margin.get("t", 48), 56)),
        )

    return fig


def apply_density_marker_defaults(
    fig: go.Figure,
    *,
    base_opacity: float = 0.42,
    highlight_opacity: float = 0.88,
    dim_opacity: float = 0.14,
    max_size: float = 28,
) -> go.Figure:
    """Normalize scatter/marker opacity for overdraw-heavy traces."""
    for trace in fig.data:
        if trace.type not in ("scatter", "scattergl", "scatterpolar"):
            continue
        marker = trace.marker
        if marker is None:
            continue
        op = marker.opacity
        if isinstance(op, (list, tuple)):
            continue
        if op is None or op > 0.85:
            trace.marker.opacity = base_opacity
        elif op < dim_opacity:
            trace.marker.opacity = dim_opacity
        if hasattr(marker, "size") and marker.size and isinstance(marker.size, (int, float)):
            if marker.size > max_size:
                trace.marker.size = max_size
    return fig


def strip_figure_height(fig: go.Figure) -> go.Figure:
    fig.update_layout(height=None)
    return fig
