"""Phase 1 state ownership invariants."""

from filters.aqi_filters import reset_aqi_filters
from filters.interaction import apply_interaction_payload, clear_investigation
from filters.state import AQI_STATE_DEFAULTS, TRAFFIC_STATE_DEFAULTS
from filters.traffic_filters import reset_traffic_filters
import streamlit as st


TRAFFIC_GLOBAL_KEYS = (
    "traffic_date_start",
    "traffic_date_end",
    "traffic_selected_areas",
    "traffic_selected_weather",
    "traffic_selected_roadwork",
    "traffic_selected_roads",
    "traffic_filters_active",
)

TRAFFIC_VISUAL_KEYS = (
    "traffic_selected_area",
    "traffic_selected_road",
    "traffic_selected_month",
    "traffic_selected_quadrant",
    "traffic_radar_focus_area",
    "traffic_focus_chart",
    "traffic_focus_mode",
)

AQI_GLOBAL_KEYS = (
    "aqi_date_start",
    "aqi_date_end",
    "aqi_selected_categories",
    "aqi_selected_seasons",
    "aqi_filters_active",
)

AQI_VISUAL_KEYS = (
    "aqi_selected_date",
    "aqi_selected_month",
    "aqi_selected_regime",
    "aqi_selected_season",
    "aqi_selected_category",
    "aqi_selected_year",
    "aqi_selected_week",
    "aqi_selected_pollutant",
    "aqi_focus_chart",
    "aqi_focus_mode",
    "aqi_context_pm25",
)


def _snapshot(state: dict, keys: tuple[str, ...]) -> dict:
    return {key: state.get(key) for key in keys}


def test_chart_click_does_not_mutate_traffic_global_filters(monkeypatch):
    fake = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_selected_areas": ["Koramangala"],
        "traffic_selected_roads": ["Road_1"],
        "traffic_selected_weather": ["Rain"],
    }
    before = _snapshot(fake, TRAFFIC_GLOBAL_KEYS)
    monkeypatch.setattr("filters.interaction.st.session_state", fake, raising=False)

    apply_interaction_payload(
        "traffic",
        {
            "chart": "T-05",
            "selected_area": "Indiranagar",
            "selected_road": "Road_2",
            "focus_mode": "road_investigation",
        },
    )

    assert _snapshot(fake, TRAFFIC_GLOBAL_KEYS) == before


def test_chart_click_does_not_mutate_aqi_global_filters(monkeypatch):
    fake = {
        **AQI_STATE_DEFAULTS,
        "aqi_selected_categories": ["Poor"],
        "aqi_selected_seasons": ["Winter"],
    }
    before = _snapshot(fake, AQI_GLOBAL_KEYS)
    monkeypatch.setattr("filters.interaction.st.session_state", fake, raising=False)

    apply_interaction_payload(
        "aqi",
        {
            "chart": "A-02",
            "selected_category": "Severe",
            "selected_year": 2023,
            "selected_week": 4,
            "focus_mode": "calendar_event",
        },
    )

    assert _snapshot(fake, AQI_GLOBAL_KEYS) == before


def test_clear_focus_does_not_mutate_global_filters(monkeypatch):
    fake = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_selected_areas": ["Koramangala"],
        "traffic_selected_weather": ["Rain"],
        "traffic_selected_area": "Indiranagar",
        "traffic_focus_chart": "T-01",
    }
    before = _snapshot(fake, TRAFFIC_GLOBAL_KEYS)
    monkeypatch.setattr("filters.interaction.st.session_state", fake, raising=False)

    clear_investigation("traffic")

    assert _snapshot(fake, TRAFFIC_GLOBAL_KEYS) == before
    assert fake["traffic_selected_area"] is None
    assert fake["traffic_focus_chart"] is None


def test_reset_traffic_filters_restores_visual_focus(monkeypatch):
    fake = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_selected_areas": ["Koramangala"],
        "traffic_selected_area": "Indiranagar",
        "traffic_selected_road": "Road_1",
        "traffic_focus_chart": "T-05",
    }
    monkeypatch.setattr(st, "session_state", fake, raising=False)
    monkeypatch.setattr(st, "cache_data", type("CD", (), {"clear": staticmethod(lambda: None)})(), raising=False)

    reset_traffic_filters()

    assert _snapshot(fake, TRAFFIC_VISUAL_KEYS) == _snapshot(TRAFFIC_STATE_DEFAULTS, TRAFFIC_VISUAL_KEYS)
    assert fake["traffic_selected_areas"] == []


def test_reset_aqi_filters_restores_visual_focus(monkeypatch):
    fake = {
        **AQI_STATE_DEFAULTS,
        "aqi_selected_categories": ["Poor"],
        "aqi_selected_category": "Severe",
        "aqi_selected_season": "Winter",
        "aqi_focus_chart": "A-02",
    }
    monkeypatch.setattr(st, "session_state", fake, raising=False)
    monkeypatch.setattr(st, "cache_data", type("CD", (), {"clear": staticmethod(lambda: None)})(), raising=False)

    reset_aqi_filters()

    assert _snapshot(fake, AQI_VISUAL_KEYS) == _snapshot(AQI_STATE_DEFAULTS, AQI_VISUAL_KEYS)
    assert fake["aqi_selected_categories"] == []
