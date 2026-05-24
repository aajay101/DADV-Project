"""Phase 6 — advanced analytical chart refactors (T-11, T-13, T-02)."""

from __future__ import annotations

import importlib
from unittest.mock import patch

import plotly.graph_objects as go

from config.data_config import COL_AREA
from data_layer.page_bundles import build_traffic_lab_bundle, build_traffic_patterns_bundle
from data_layer.traffic_transforms import (
    PARALLEL_AREA_DIMENSIONS,
    get_area_stress_heatmap,
    get_parallel_coords_data,
    get_parallel_coords_records,
    get_road_distribution_profiles,
)
from filters.state import TRAFFIC_STATE_DEFAULTS

t11 = importlib.import_module("dashboards.traffic.charts.t11_ridgeline")
t13 = importlib.import_module("dashboards.traffic.charts.t13_compound_radar")
t02 = importlib.import_module("dashboards.traffic.charts.t02_parallel_coords")


def test_road_distribution_profiles_max_16(sample_traffic_df):
    profiles = get_road_distribution_profiles(sample_traffic_df)
    assert not profiles.empty
    assert len(profiles) <= 16
    assert "values" in profiles.columns
    assert "median" in profiles.columns


def test_area_stress_heatmap_shape(sample_traffic_df):
    heat = get_area_stress_heatmap(sample_traffic_df)
    assert len(heat["areas"]) == sample_traffic_df[COL_AREA].nunique()
    assert len(heat["metrics"]) == 6
    assert len(heat["z"]) == len(heat["areas"])
    assert len(heat["z"][0]) == 6


def test_t11_small_multiples_render(sample_traffic_df):
    profiles = get_road_distribution_profiles(sample_traffic_df)
    fig = t11.render(profiles, {"dashboard": "traffic", "role": "hero"})
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= len(profiles)


def test_t13_heatmap_default_render(sample_traffic_df):
    heat = get_area_stress_heatmap(sample_traffic_df)
    fig = t13.render_heatmap(heat, {"dashboard": "traffic", "role": "hero"})
    assert isinstance(fig, go.Figure)
    assert fig.data[0].type == "heatmap"


def test_t13_radar_toggle_preserves_focus(sample_traffic_df):
    focus = sample_traffic_df[COL_AREA].iloc[0]
    from data_layer.traffic_transforms import get_radar_normalized_metrics

    radar_data = get_radar_normalized_metrics(sample_traffic_df)
    cfg = {"dashboard": "traffic", "focus_area": focus, "view": "radar"}
    fig = t13.render_radar(radar_data, cfg)
    assert isinstance(fig, go.Figure)
    assert any(t.type == "scatterpolar" for t in fig.data)


def test_t02_eight_axis_area_profile(sample_traffic_df):
    area = get_parallel_coords_data(sample_traffic_df)
    assert len(PARALLEL_AREA_DIMENSIONS) == 8
    fig = t02.render(area, {"dashboard": "traffic", "dimensions": PARALLEL_AREA_DIMENSIONS})
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == area[COL_AREA].nunique()


def test_t02_record_level_parcoords(sample_traffic_df):
    records = get_parallel_coords_records(sample_traffic_df, max_points=500)
    fig = t02.render(records, {"dashboard": "traffic", "record_level": True})
    assert isinstance(fig, go.Figure)
    assert fig.data[0].type == "parcoords"


def test_lab_bundle_heatmap_default(sample_traffic_df):
    state = dict(TRAFFIC_STATE_DEFAULTS)
    state["traffic_lab_t13_view"] = "heatmap"
    with patch("data_layer.page_bundles.load_traffic_clean", return_value=sample_traffic_df):
        with patch("data_layer.page_bundles.get_lab_dataset", return_value=sample_traffic_df):
            bundle = build_traffic_lab_bundle(state)
    assert bundle["hero_chart"]["fig"].data[0].type == "heatmap"


def test_patterns_bundle_uses_distribution_profiles(sample_traffic_df):
    state = dict(TRAFFIC_STATE_DEFAULTS)
    with patch("data_layer.page_bundles.load_traffic_clean", return_value=sample_traffic_df):
        bundle = build_traffic_patterns_bundle(state)
    assert "4×4" in bundle["hero_chart"]["subtitle"].lower() or "small" in bundle["hero_chart"]["subtitle"].lower()
    assert bundle["hero_chart"]["fig"] is not None
