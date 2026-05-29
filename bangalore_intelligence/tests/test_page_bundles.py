from datetime import datetime

from data_layer.page_bundles import build_aqi_crisis_bundle, build_traffic_command_bundle
from filters.state import AQI_STATE_DEFAULTS, TRAFFIC_STATE_DEFAULTS


def test_extreme_traffic_filter_returns_empty_bundle(sample_traffic_df):
    state = dict(TRAFFIC_STATE_DEFAULTS)
    state["traffic_date_start"] = datetime(2030, 1, 1)
    state["traffic_date_end"] = datetime(2030, 6, 1)
    state["traffic_selected_areas"] = ["Indiranagar"]

    from unittest.mock import patch

    with patch("data_layer.page_bundles.load_traffic_clean", return_value=sample_traffic_df):
        bundle = build_traffic_command_bundle(state)
    assert bundle.get("empty") is True


def test_traffic_command_bundle_has_hero_figure(sample_traffic_df):
    state = dict(TRAFFIC_STATE_DEFAULTS)
    from unittest.mock import patch

    with patch("data_layer.page_bundles.load_traffic_clean", return_value=sample_traffic_df):
        bundle = build_traffic_command_bundle(state)
    assert not bundle.get("empty")
    assert bundle["hero_chart"]["fig"] is not None


def test_aqi_crisis_bundle_structure(sample_aqi_df):
    state = dict(AQI_STATE_DEFAULTS)
    from unittest.mock import patch

    with patch("data_layer.page_bundles.load_aqi_clean", return_value=sample_aqi_df):
        bundle = build_aqi_crisis_bundle(state)
    assert not bundle.get("empty")
    assert bundle["hero_chart"]["fig"] is not None
