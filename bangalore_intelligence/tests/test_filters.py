from datetime import datetime

from filters.aqi_filters import apply_aqi_filters
from filters.traffic_filters import apply_traffic_filters
from filters.state import AQI_STATE_DEFAULTS, TRAFFIC_STATE_DEFAULTS


def test_reversed_traffic_dates_return_empty(sample_traffic_df):
    state = dict(TRAFFIC_STATE_DEFAULTS)
    state["traffic_date_start"] = datetime(2024, 1, 1)
    state["traffic_date_end"] = datetime(2022, 1, 1)
    out = apply_traffic_filters(sample_traffic_df, state)
    assert out.empty


def test_extreme_aqi_filter_can_empty(sample_aqi_df):
    state = dict(AQI_STATE_DEFAULTS)
    state["aqi_date_start"] = datetime(2030, 1, 1)
    state["aqi_date_end"] = datetime(2030, 12, 31)
    out = apply_aqi_filters(sample_aqi_df, state)
    assert out.empty
