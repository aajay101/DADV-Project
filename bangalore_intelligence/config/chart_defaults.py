"""Shared Plotly layout defaults and chart sizing."""

from copy import deepcopy

from config.theme import FONT_FAMILY, FONT_MONO, get_dashboard_tokens

CHART_SIZES = {
    "hero_full": 600,
    "hero_half": 540,
    "supporting": 360,
    "compact": 300,
    "ridgeline": 700,
    "pairplot": 800,
    "radar": 550,
    "heatmap_small": 350,
}


def _build_layout(tokens: dict) -> dict:
    return {
        "paper_bgcolor": tokens["bg"],
        "plot_bgcolor": tokens["surface"],
        "font": {
            "family": FONT_FAMILY,
            "size": 12,
            "color": tokens["text_muted"],
        },
        "margin": {"l": 48, "r": 24, "t": 24, "b": 48},
        "hoverlabel": {
            "bgcolor": tokens["surface_2"],
            "bordercolor": tokens["border"],
            "font": {"family": FONT_MONO, "size": 12, "color": tokens["text_primary"]},
        },
        "legend": {
            "orientation": "h",
            "yanchor": "bottom",
            "y": -0.15,
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
