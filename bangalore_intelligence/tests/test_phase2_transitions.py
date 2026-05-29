"""Phase 2 deterministic transition invariants."""

from filters.state import AQI_STATE_DEFAULTS, TRAFFIC_STATE_DEFAULTS
from filters.transitions import (
    ChartFocusChanged,
    ChartLocalStateChanged,
    FocusCleared,
    GlobalFilterChanged,
    GlobalFiltersReset,
    dispatch,
    get_last_transition_trace,
)


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


def _snapshot(state: dict, keys: tuple[str, ...]) -> dict:
    return {key: state.get(key) for key in keys}


def test_chart_focus_changed_mutates_visual_domain_only(monkeypatch):
    fake = {
        **TRAFFIC_STATE_DEFAULTS,
    }
    before_global = _snapshot(fake, TRAFFIC_GLOBAL_KEYS)
    monkeypatch.setattr("filters.transitions.st.session_state", fake, raising=False)

    result = dispatch(
        ChartFocusChanged(
            dashboard="traffic",
            payload={
                "chart": "T-01",
                "selected_area": "Indiranagar",
                "selected_road": None,
                "focus_mode": "area_ranking",
            },
        )
    )

    assert result.reducer == "reduce_visual_focus"
    assert result.changed_domains == ("visual_focus", "investigation_overlay")
    assert _snapshot(fake, TRAFFIC_GLOBAL_KEYS) == before_global
    assert fake["traffic_selected_area"] == "Indiranagar"
    assert fake["traffic_investigation_scope"]["area"] == "Indiranagar"
    assert fake["chart_selection_epochs"]["T-02"] == 1
    assert fake["chart_selection_epochs"]["T-05"] == 1


def test_focus_cleared_preserves_global_filters(monkeypatch):
    fake = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_selected_areas": ["Koramangala"],
        "traffic_selected_area": "Indiranagar",
        "traffic_focus_chart": "T-01",
        "_chart_sel_sig": ("T-01", 1),
    }
    before_global = _snapshot(fake, TRAFFIC_GLOBAL_KEYS)
    monkeypatch.setattr("filters.transitions.st.session_state", fake, raising=False)

    result = dispatch(FocusCleared(dashboard="traffic"))

    assert result.action_type == "FocusCleared"
    assert result.changed_domains == ("visual_focus", "investigation_overlay")
    assert _snapshot(fake, TRAFFIC_GLOBAL_KEYS) == before_global
    assert fake["traffic_selected_area"] is None
    assert fake["traffic_focus_chart"] is None
    assert fake["traffic_investigation_scope"] == TRAFFIC_STATE_DEFAULTS["traffic_investigation_scope"]
    assert "_chart_sel_sig" not in fake


def test_global_filter_change_does_not_mutate_visual_focus(monkeypatch):
    fake = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_selected_area": "Indiranagar",
        "traffic_focus_chart": "T-01",
    }
    before_visual = _snapshot(fake, TRAFFIC_VISUAL_KEYS)
    monkeypatch.setattr("filters.transitions.st.session_state", fake, raising=False)

    result = dispatch(
        GlobalFilterChanged(
            dashboard="traffic",
            updates={"traffic_selected_weather": ["Rain"], "traffic_selected_areas": []},
            filters_active=True,
        )
    )

    assert result.reducer == "reduce_global_filters"
    assert result.changed_domains == ("global_filters",)
    assert _snapshot(fake, TRAFFIC_VISUAL_KEYS) == before_visual
    assert fake["traffic_selected_weather"] == ["Rain"]
    assert fake["traffic_filter_updating"] is True


def test_global_filters_reset_restores_baseline_mode(monkeypatch):
    fake = {
        **AQI_STATE_DEFAULTS,
        "aqi_selected_categories": ["Poor"],
        "aqi_selected_category": "Severe",
        "aqi_focus_chart": "A-02",
        "aqi_investigation_scope": {**AQI_STATE_DEFAULTS["aqi_investigation_scope"], "category": "Severe"},
    }
    monkeypatch.setattr("filters.transitions.st.session_state", fake, raising=False)

    result = dispatch(GlobalFiltersReset(dashboard="aqi"))

    assert result.action_type == "GlobalFiltersReset"
    assert result.changed_domains == ("global_filters", "visual_focus", "investigation_overlay")
    assert _snapshot(fake, AQI_GLOBAL_KEYS) == _snapshot(AQI_STATE_DEFAULTS, AQI_GLOBAL_KEYS)
    assert fake["aqi_selected_category"] is None
    assert fake["aqi_focus_chart"] is None
    assert fake["aqi_investigation_scope"] == AQI_STATE_DEFAULTS["aqi_investigation_scope"]


def test_transition_trace_records_reducer_and_invalidation(monkeypatch):
    fake = dict(TRAFFIC_STATE_DEFAULTS)
    monkeypatch.setattr("filters.transitions.st.session_state", fake, raising=False)

    dispatch(ChartFocusChanged(dashboard="traffic", payload={"chart": "T-07", "selected_road": "Road_1"}))
    trace = get_last_transition_trace()

    assert trace["action_type"] == "ChartFocusChanged"
    assert trace["reducer"] == "reduce_visual_focus"
    assert trace["changed_domains"] == ["visual_focus", "investigation_overlay"]
    assert trace["invalidation_plan"]["bump_widget_epoch"] is True


def test_visual_focus_does_not_clear_streamlit_data_cache(monkeypatch):
    fake = dict(TRAFFIC_STATE_DEFAULTS)
    calls = {"clear": 0}

    class Cache:
        @staticmethod
        def clear():
            calls["clear"] += 1

    monkeypatch.setattr("filters.transitions.st.session_state", fake, raising=False)
    monkeypatch.setattr("filters.transitions.st.cache_data", Cache(), raising=False)

    dispatch(ChartFocusChanged(dashboard="traffic", payload={"chart": "T-01", "selected_area": "Koramangala"}))

    assert calls["clear"] == 0
    assert fake["last_transition_trace"]["invalidation_plan"]["data_cache_scope"] == "none"


def test_global_filter_change_declares_dashboard_data_cache_scope(monkeypatch):
    fake = dict(TRAFFIC_STATE_DEFAULTS)
    calls = {"clear": 0}

    class Cache:
        @staticmethod
        def clear():
            calls["clear"] += 1

    monkeypatch.setattr("filters.transitions.st.session_state", fake, raising=False)
    monkeypatch.setattr("filters.transitions.st.cache_data", Cache(), raising=False)

    dispatch(GlobalFilterChanged(dashboard="traffic", updates={"traffic_selected_areas": ["Koramangala"]}))

    assert calls["clear"] == 1
    assert fake["last_transition_trace"]["invalidation_plan"]["data_cache_scope"] == "dashboard"


def test_chart_local_state_changed_uses_chart_local_domain(monkeypatch):
    fake = dict(TRAFFIC_STATE_DEFAULTS)
    monkeypatch.setattr("filters.transitions.st.session_state", fake, raising=False)

    result = dispatch(
        ChartLocalStateChanged(
            dashboard="traffic",
            updates={"traffic_radar_visible_areas": ["Koramangala"], "traffic_radar_comparison_mode": "top_stress"},
        )
    )

    assert result.action_type == "ChartLocalStateChanged"
    assert result.changed_domains == ("chart_local_state",)
    assert fake["traffic_radar_visible_areas"] == ["Koramangala"]
    assert fake["last_transition_trace"]["invalidation_plan"]["data_cache_scope"] == "none"
