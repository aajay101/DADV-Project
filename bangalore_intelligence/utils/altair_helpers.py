"""
Altair spec builders — intentionally deferred.

Production charts use Plotly only. These stubs exist for future ridgeline/pairplot
experiments and must not be imported from dashboards, page bundles, or app startup.
"""

from __future__ import annotations


def build_ridgeline_base(data, x_col, group_col):
    """Deferred — use dashboards/*/charts Plotly ridgeline modules instead."""
    return None


def add_aqi_color_scale():
    """Deferred — AQI colors live in config.theme / plotly_engine."""
    return []


def build_pairplot_base(data, var_cols, color_col):
    """Deferred — use dashboards/aqi/charts/a15_pairplot instead."""
    return None


def kde_layer(data, col, offset, color):
    """Deferred."""
    return None
