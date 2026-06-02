"""Shared Plotly layout defaults and chart sizing — single source of truth."""

from copy import deepcopy

from config.theme import FONT_FAMILY, FONT_MONO, get_dashboard_tokens

# Blueprint §4.6 chart sizing system
CHART_SIZES = {
    "hero_full": 600,
    "hero_half": 500,
    "supporting": 400,
    "compact": 300,
    "ridgeline": 700,
    "pairplot": 800,
    "radar": 550,
    "heatmap_small": 350,
    "matrix": 720,
    "hero_scorecard": 480,
}

CHART_SIZE_BY_CODE: dict[str, str] = {
    "T-01": "hero_full",
    "T-02": "supporting",
    "T-03": "hero_half",
    "T-04": "supporting",
    "T-05": "hero_half",
    "T-06": "supporting",
    "T-07": "compact",
    "T-08": "supporting",
    "T-09": "hero_half",
    "T-10": "supporting",
    "T-11": "matrix",
    "T-12": "heatmap_small",
    "T-13": "heatmap_small",
    "T-14": "compact",
    "T-15": "compact",
    "A-01": "hero_scorecard",
    "A-02": "hero_full",
    "A-03": "ridgeline",
    "A-04": "supporting",
    "A-05": "supporting",
    "A-06": "hero_half",
    "A-07": "radar",
    "A-08": "hero_half",
    "A-09": "supporting",
    "A-10": "supporting",
    "A-11": "supporting",
    "A-12": "compact",
    "A-13": "supporting",
    "A-14": "heatmap_small",
    "A-15": "pairplot",
}

CHART_LAYOUT_TYPE_BY_CODE: dict[str, str] = {
    "T-02": "default",
    "T-03": "timeseries",
    "T-01": "compact",
    "T-05": "scatter_dense",
    "T-08": "compact",
    "T-11": "matrix",
    "T-12": "heatmap_small",
    "T-13": "heatmap",
    "T-14": "scatter_dense",
    "T-15": "matrix",
    "A-01": "scorecard",
    "A-02": "heatmap_small",
    "A-03": "ridgeline",
    "A-06": "scatter_dense",
    "A-07": "radar",
    "A-08": "scatter_dense",
    "A-13": "scatter_dense",
    "A-14": "heatmap_small",
    "A-15": "pairplot",
}

_BREAKPOINT_SCALE: dict[str, float] = {
    "compact": 0.72,
    "tablet": 0.82,
    "laptop": 0.92,
    "desktop": 1.0,
    "ultrawide": 1.0,
}


def chart_size_for(chart_id: str | None, role: str = "hero") -> str:
    if chart_id and chart_id in CHART_SIZE_BY_CODE:
        return CHART_SIZE_BY_CODE[chart_id]
    if role == "hero":
        return "hero_half"
    if role == "supporting":
        return "supporting"
    return "compact"


def resolve_chart_height(
    size_key: str | None = None,
    *,
    role: str = "hero",
    chart_id: str | None = None,
    breakpoint: str = "desktop",
    is_fullscreen: bool = False,
) -> int:
    """Resolve pixel height from CHART_SIZES only — no hardcoded chart heights."""
    key = size_key or chart_size_for(chart_id, role)
    base = CHART_SIZES.get(key, CHART_SIZES["supporting"])
    scale = _BREAKPOINT_SCALE.get(breakpoint, 1.0)
    if breakpoint == "tablet" and key in ("matrix", "heatmap_small", "ridgeline"):
        scale = max(scale, 0.88)
    height = int(base * scale)
    if is_fullscreen:
        from filters.fullscreen import get_fullscreen_height

        fs = get_fullscreen_height()
        if key in ("pairplot", "ridgeline", "matrix"):
            return min(920, max(fs, height + 80))
        if key in ("radar", "hero_full", "heatmap_small"):
            return min(880, max(fs, height + 40))
        return fs
    return max(260, height)


def _build_layout(tokens: dict) -> dict:
    return {
        "paper_bgcolor": tokens["bg"],
        "plot_bgcolor": tokens["surface"],
        "font": {
            "family": FONT_FAMILY,
            "size": 12,
            "color": tokens["text_muted"],
        },
        "margin": {"l": 56, "r": 32, "t": 36, "b": 80},
        "hoverlabel": {
            "bgcolor": tokens["surface_2"],
            "bordercolor": tokens["border"],
            "font": {"family": FONT_MONO, "size": 12, "color": tokens["text_primary"]},
        },
        "legend": {
            "orientation": "h",
            "yanchor": "top",
            "y": -0.18,
            "xanchor": "center",
            "x": 0.5,
            "font": {"size": 11, "color": tokens["text_muted"]},
        },
        "xaxis": {
            "gridcolor": tokens["border_2"],
            "zeroline": False,
            "tickfont": {"size": 11, "color": tokens["text_muted"]},
        },
        "yaxis": {
            "gridcolor": tokens["border_2"],
            "zeroline": False,
            "tickfont": {"size": 11, "color": tokens["text_muted"]},
        },
    }


BASE_LAYOUT = _build_layout(get_dashboard_tokens("traffic"))


def get_base_layout(dashboard: str = "traffic") -> dict:
    """Deep copy of dashboard-scoped BASE_LAYOUT."""
    return deepcopy(_build_layout(get_dashboard_tokens(dashboard)))
