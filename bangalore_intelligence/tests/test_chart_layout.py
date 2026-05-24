"""Chart sizing and layout governance tests."""

from config.chart_defaults import CHART_SIZES, chart_size_for, resolve_chart_height
from utils.plotly_layout import chart_layout_type


def test_chart_size_by_code():
    assert chart_size_for("T-13", "hero") == "heatmap_small"
    assert chart_size_for("A-15", "hero") == "pairplot"
    assert chart_size_for("T-15", "supporting") == "compact"
    assert chart_size_for(None, "hero") == "hero_half"


def test_resolve_chart_height_uses_constants_only():
    h = resolve_chart_height("pairplot", breakpoint="desktop")
    assert h == CHART_SIZES["pairplot"]
    compact = resolve_chart_height("hero_full", breakpoint="compact")
    assert compact < CHART_SIZES["hero_full"]


def test_chart_layout_type_mapping():
    assert chart_layout_type("T-13") == "heatmap"
    assert chart_layout_type("A-15") == "pairplot"
    assert chart_layout_type("T-11") == "matrix"
    assert chart_layout_type("T-05") == "scatter_dense"
