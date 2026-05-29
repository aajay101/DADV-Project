"""Filter scope callbacks: compound global filters and cache fingerprint."""

from filters.scope_sync import (
    data_scope_fingerprint,
    on_aqi_categories_change,
    on_aqi_seasons_change,
    on_traffic_areas_change,
    on_traffic_roadwork_change,
    on_traffic_roads_change,
    on_traffic_weather_change,
    visual_scope_fingerprint,
)
from filters.state import AQI_STATE_DEFAULTS, TRAFFIC_STATE_DEFAULTS


def test_visual_scope_fingerprint_changes_with_focus(monkeypatch):
    fake: dict = dict(TRAFFIC_STATE_DEFAULTS)
    monkeypatch.setattr("filters.scope_sync.st.session_state", fake, raising=False)
    a = visual_scope_fingerprint("traffic")
    fake["traffic_selected_area"] = "Koramangala"
    b = visual_scope_fingerprint("traffic")
    assert a != b


def test_data_scope_fingerprint_ignores_visual_focus(monkeypatch):
    fake: dict = dict(TRAFFIC_STATE_DEFAULTS)
    monkeypatch.setattr("filters.scope_sync.st.session_state", fake, raising=False)
    a = data_scope_fingerprint("traffic")
    fake["traffic_selected_area"] = "Koramangala"
    b = data_scope_fingerprint("traffic")
    assert a == b


def test_traffic_area_filter_preserves_sibling_global_dimensions(monkeypatch):
    fake: dict = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_selected_areas": ["Indiranagar"],
        "traffic_selected_weather": ["Rain"],
        "traffic_selected_roads": ["Road_1"],
    }
    monkeypatch.setattr("filters.scope_sync.st.session_state", fake, raising=False)
    monkeypatch.setattr("filters.state.st.session_state", fake, raising=False)

    on_traffic_areas_change("traffic")

    assert fake["traffic_selected_areas"] == ["Indiranagar"]
    assert fake["traffic_selected_weather"] == ["Rain"]
    assert fake["traffic_selected_roads"] == ["Road_1"]
    assert fake["traffic_selected_area"] is None


def test_traffic_weather_filter_preserves_area_and_roads(monkeypatch):
    fake: dict = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_selected_weather": ["Clear"],
        "traffic_selected_areas": ["Whitefield"],
        "traffic_selected_roads": ["Road_3"],
        "traffic_selected_area": "Koramangala",
    }
    monkeypatch.setattr("filters.scope_sync.st.session_state", fake, raising=False)
    monkeypatch.setattr("filters.state.st.session_state", fake, raising=False)

    on_traffic_weather_change("traffic")

    assert fake["traffic_selected_weather"] == ["Clear"]
    assert fake["traffic_selected_areas"] == ["Whitefield"]
    assert fake["traffic_selected_roads"] == ["Road_3"]
    assert fake["traffic_selected_area"] == "Koramangala"


def test_traffic_roads_filter_preserves_area_and_weather(monkeypatch):
    fake: dict = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_selected_roads": ["Road_3"],
        "traffic_selected_areas": ["Whitefield"],
        "traffic_selected_weather": ["Clear"],
        "traffic_selected_road": "Road_1",
    }
    monkeypatch.setattr("filters.scope_sync.st.session_state", fake, raising=False)
    monkeypatch.setattr("filters.state.st.session_state", fake, raising=False)

    on_traffic_roads_change("traffic")

    assert fake["traffic_selected_roads"] == ["Road_3"]
    assert fake["traffic_selected_areas"] == ["Whitefield"]
    assert fake["traffic_selected_weather"] == ["Clear"]
    assert fake["traffic_selected_road"] == "Road_1"


def test_traffic_roadwork_filter_preserves_compound_filters(monkeypatch):
    fake: dict = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_selected_areas": ["Whitefield"],
        "traffic_selected_weather": ["Rain"],
        "traffic_selected_roadwork": "Major",
        "traffic_selected_roads": ["Road_3"],
    }
    monkeypatch.setattr("filters.scope_sync.st.session_state", fake, raising=False)
    monkeypatch.setattr("filters.state.st.session_state", fake, raising=False)

    on_traffic_roadwork_change("traffic")

    assert fake["traffic_selected_areas"] == ["Whitefield"]
    assert fake["traffic_selected_weather"] == ["Rain"]
    assert fake["traffic_selected_roadwork"] == "Major"
    assert fake["traffic_selected_roads"] == ["Road_3"]


def test_traffic_compound_callbacks_keep_all_filter_dimensions_active(monkeypatch):
    fake: dict = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_selected_areas": ["Whitefield"],
        "traffic_selected_weather": ["Rain"],
        "traffic_selected_roadwork": "Major",
        "traffic_selected_roads": ["Road_3"],
    }
    monkeypatch.setattr("filters.scope_sync.st.session_state", fake, raising=False)
    monkeypatch.setattr("filters.state.st.session_state", fake, raising=False)

    on_traffic_areas_change("traffic")
    on_traffic_weather_change("traffic")
    on_traffic_roads_change("traffic")

    assert fake["traffic_selected_areas"] == ["Whitefield"]
    assert fake["traffic_selected_weather"] == ["Rain"]
    assert fake["traffic_selected_roadwork"] == "Major"
    assert fake["traffic_selected_roads"] == ["Road_3"]
    assert fake["traffic_filters_active"] is True


def test_aqi_category_and_season_filters_preserve_each_other_and_visual_focus(monkeypatch):
    fake: dict = {
        **AQI_STATE_DEFAULTS,
        "aqi_selected_categories": ["Poor"],
        "aqi_selected_seasons": ["Winter"],
        "aqi_selected_category": "Severe",
        "aqi_selected_season": "Monsoon",
    }
    monkeypatch.setattr("filters.scope_sync.st.session_state", fake, raising=False)
    monkeypatch.setattr("filters.state.st.session_state", fake, raising=False)

    on_aqi_categories_change("aqi")
    assert fake["aqi_selected_categories"] == ["Poor"]
    assert fake["aqi_selected_seasons"] == ["Winter"]
    assert fake["aqi_selected_category"] == "Severe"
    assert fake["aqi_selected_season"] == "Monsoon"

    fake["aqi_selected_seasons"] = ["Winter"]
    on_aqi_seasons_change("aqi")
    assert fake["aqi_selected_categories"] == ["Poor"]
    assert fake["aqi_selected_seasons"] == ["Winter"]
    assert fake["aqi_selected_category"] == "Severe"
    assert fake["aqi_selected_season"] == "Monsoon"
