from components.loading_state import chart_skeleton_html, resolve_skeleton_type


def test_resolve_skeleton_type_maps_layout_keys():
    assert resolve_skeleton_type("radar") == "radar"
    assert resolve_skeleton_type("pairplot") == "pairplot"
    assert resolve_skeleton_type("heatmap_small") == "heatmap"
    assert resolve_skeleton_type("scatter_dense") == "scatter"
    assert resolve_skeleton_type("unknown_type") == "default"


def test_chart_skeleton_html_varies_by_type():
    bar = chart_skeleton_html(400, "traffic", "bar")
    radar = chart_skeleton_html(400, "traffic", "radar")
    assert 'data-skeleton-type="bar"' in bar
    assert 'data-skeleton-type="radar"' in radar
    assert bar != radar
