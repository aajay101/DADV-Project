"""Deferred chart bundle slots."""

from unittest.mock import patch

from data_layer.page_bundles import build_traffic_lab_bundle, build_traffic_patterns_bundle, build_traffic_temporal_bundle
from filters.state import TRAFFIC_STATE_DEFAULTS


def test_temporal_secondary_t15_is_lazy(sample_traffic_df):
    state = dict(TRAFFIC_STATE_DEFAULTS)
    with patch("data_layer.page_bundles.load_traffic_clean", return_value=sample_traffic_df):
        bundle = build_traffic_temporal_bundle(state)
    secondary = bundle["secondary_charts"][0]
    assert secondary.get("chart_id") == "T-15"
    assert secondary.get("lazy") is True
    assert secondary.get("fig") is None
    assert callable(secondary.get("fig_builder"))


def test_patterns_support_t12_deferred(sample_traffic_df):
    state = dict(TRAFFIC_STATE_DEFAULTS)
    with patch("data_layer.page_bundles.load_traffic_clean", return_value=sample_traffic_df):
        bundle = build_traffic_patterns_bundle(state)
    support = bundle["support_chart"]
    assert support.get("lazy") is True
    assert support.get("fig") is None
    assert callable(support.get("fig_builder"))


def test_lab_secondary_t14_is_lazy(sample_traffic_df):
    state = dict(TRAFFIC_STATE_DEFAULTS)
    with patch("data_layer.page_bundles.load_traffic_clean", return_value=sample_traffic_df):
        with patch("data_layer.page_bundles.get_lab_dataset", return_value=sample_traffic_df):
            bundle = build_traffic_lab_bundle(state)
    secondary = bundle["secondary_charts"][0]
    assert secondary.get("chart_id") == "T-14"
    assert secondary.get("lazy") is True
    assert secondary.get("fig") is None
    assert callable(secondary.get("fig_builder"))
