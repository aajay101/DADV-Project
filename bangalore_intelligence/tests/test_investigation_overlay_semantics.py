"""Investigation overlay semantics and multiselect governance."""

from datetime import date, datetime

import pandas as pd

from filters.investigation_scope import apply_investigation_overlay_scope
from filters.state import AQI_STATE_DEFAULTS, TRAFFIC_STATE_DEFAULTS
from filters.transitions import (
    ChartFocusChanged,
    ClearGlobalFilters,
    FocusCleared,
    GlobalFiltersReset,
    dispatch,
)


def test_chart_focus_mutates_overlay_without_global_filters(monkeypatch):
    fake = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_selected_roads": [],
    }
    before_global = {
        "traffic_selected_areas": list(fake["traffic_selected_areas"]),
        "traffic_selected_roads": list(fake["traffic_selected_roads"]),
    }
    monkeypatch.setattr("filters.transitions.st.session_state", fake, raising=False)

    result = dispatch(
        ChartFocusChanged(
            dashboard="traffic",
            payload={"chart": "T-01", "selected_area": "Whitefield", "focus_mode": "area_ranking"},
        )
    )

    assert result.changed_domains == ("visual_focus", "investigation_overlay")
    assert fake["traffic_investigation_scope"]["area"] == "Whitefield"
    assert fake["traffic_investigation_scope"]["source_chart"] == "T-01"
    assert fake["traffic_selected_roads"] == before_global["traffic_selected_roads"]


def test_global_filter_mode_blocks_overlay_but_keeps_visual_focus(monkeypatch):
    fake = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_selected_areas": ["Whitefield"],
    }
    before_overlay = dict(fake["traffic_investigation_scope"])
    monkeypatch.setattr("filters.transitions.st.session_state", fake, raising=False)

    result = dispatch(
        ChartFocusChanged(
            dashboard="traffic",
            payload={"chart": "T-01", "selected_area": "Whitefield", "focus_mode": "area_ranking"},
        )
    )

    assert result.changed_domains == ("visual_focus",)
    assert result.invalidation_plan.reason == "chart_focus_cosmetic_global_filter_mode"
    assert fake["traffic_selected_area"] == "Whitefield"
    assert fake["traffic_investigation_scope"] == before_overlay


def test_clear_focus_clears_overlay_and_preserves_global_filters(monkeypatch):
    fake = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_selected_areas": ["Indiranagar", "Whitefield"],
        "traffic_selected_area": "Whitefield",
        "traffic_focus_chart": "T-01",
        "traffic_investigation_scope": {
            "area": "Whitefield",
            "road": None,
            "month": None,
            "quadrant": None,
            "source_chart": "T-01",
            "focus_mode": "area_ranking",
        },
    }
    monkeypatch.setattr("filters.transitions.st.session_state", fake, raising=False)

    dispatch(FocusCleared(dashboard="traffic"))

    assert fake["traffic_selected_areas"] == ["Indiranagar", "Whitefield"]
    assert fake["traffic_selected_area"] is None
    assert fake["traffic_investigation_scope"] == TRAFFIC_STATE_DEFAULTS["traffic_investigation_scope"]
    assert "traffic_pending_linked_selector_reconcile" not in fake
    assert "traffic_suppress_linked_selector_dispatch" not in fake


def test_linked_selector_dropdown_ui_is_removed():
    import filters.interaction as interaction

    assert not hasattr(interaction, "render_traffic_linked_selector")
    assert not hasattr(interaction, "render_aqi_linked_selector")
    assert not hasattr(interaction, "render_page_linked_controls")
    assert not hasattr(interaction, "set_traffic_area")
    assert not hasattr(interaction, "set_aqi_season")
    assert not hasattr(interaction, "set_aqi_category")


def test_overlay_participating_chart_gets_scoped_projection():
    df = pd.DataFrame(
        {
            "Date": pd.to_datetime([datetime(2024, 1, 1), datetime(2024, 1, 2)]),
            "Area Name": ["Whitefield", "Indiranagar"],
            "Road Name": ["Road A", "Road B"],
        }
    )
    state = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_investigation_scope": {
            "area": "Whitefield",
            "road": None,
            "month": None,
            "quadrant": None,
            "source_chart": "T-01",
            "focus_mode": "area_ranking",
        },
    }

    scoped = apply_investigation_overlay_scope(df, "traffic", "T-05", state)
    unrelated = apply_investigation_overlay_scope(df, "traffic", "T-03", state)

    assert scoped["Area Name"].tolist() == ["Whitefield"]
    assert unrelated["Area Name"].tolist() == ["Whitefield", "Indiranagar"]


def test_multiselect_callback_dispatches_changed_value_without_sibling_cleanup(monkeypatch):
    from filters.scope_sync import on_traffic_areas_change

    fake = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_selected_areas": ["Indiranagar", "Whitefield"],
        "traffic_selected_weather": ["Rain"],
        "traffic_selected_roads": ["Road A"],
    }
    monkeypatch.setattr("filters.scope_sync.st.session_state", fake, raising=False)
    monkeypatch.setattr("filters.transitions.st.session_state", fake, raising=False)

    on_traffic_areas_change("traffic")

    assert fake["traffic_selected_areas"] == ["Indiranagar", "Whitefield"]
    assert fake["traffic_selected_weather"] == ["Rain"]
    assert fake["traffic_selected_roads"] == ["Road A"]
    assert fake["last_transition_trace"]["state_changes"]["traffic_selected_areas"] == [
        "Indiranagar",
        "Whitefield",
    ]
    assert "traffic_selected_weather" not in fake["last_transition_trace"]["state_changes"]
    assert "traffic_selected_roads" not in fake["last_transition_trace"]["state_changes"]


def test_interaction_mode_helpers_are_strict():
    from filters.interaction_mode import (
        assert_valid_interaction_mode,
        get_interaction_mode,
        has_active_global_filters,
        has_active_investigation_overlay,
    )

    baseline = dict(TRAFFIC_STATE_DEFAULTS)
    global_state = {**TRAFFIC_STATE_DEFAULTS, "traffic_selected_areas": ["Whitefield"]}
    overlay_state = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_investigation_scope": {
            **TRAFFIC_STATE_DEFAULTS["traffic_investigation_scope"],
            "area": "Whitefield",
        },
    }
    invalid_state = {**global_state, "traffic_investigation_scope": overlay_state["traffic_investigation_scope"]}

    assert get_interaction_mode(baseline, "traffic") == "baseline"
    assert has_active_global_filters(global_state, "traffic")
    assert get_interaction_mode(global_state, "traffic") == "global_filter_mode"
    assert has_active_investigation_overlay(overlay_state, "traffic")
    assert get_interaction_mode(overlay_state, "traffic") == "investigation_mode"
    try:
        assert_valid_interaction_mode(invalid_state, "traffic")
    except RuntimeError:
        pass
    else:
        raise AssertionError("dual analytical authority should fail")


def test_traffic_default_canonical_scope_is_baseline():
    from filters.interaction_mode import get_interaction_mode, has_active_global_filters

    state = dict(TRAFFIC_STATE_DEFAULTS)

    assert has_active_global_filters(state, "traffic") is False
    assert get_interaction_mode(state, "traffic") == "baseline"


def test_aqi_default_canonical_scope_is_baseline():
    from filters.interaction_mode import get_interaction_mode, has_active_global_filters

    state = dict(AQI_STATE_DEFAULTS)

    assert has_active_global_filters(state, "aqi") is False
    assert get_interaction_mode(state, "aqi") == "baseline"


def test_date_objects_matching_canonical_baseline_remain_baseline():
    from filters.interaction_mode import get_interaction_mode, has_active_global_filters

    traffic = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_date_start": date(2022, 1, 1),
        "traffic_date_end": date(2024, 8, 31),
    }
    aqi = {
        **AQI_STATE_DEFAULTS,
        "aqi_date_start": date(2021, 1, 1),
        "aqi_date_end": date(2023, 12, 31),
    }

    assert has_active_global_filters(traffic, "traffic") is False
    assert get_interaction_mode(traffic, "traffic") == "baseline"
    assert has_active_global_filters(aqi, "aqi") is False
    assert get_interaction_mode(aqi, "aqi") == "baseline"


def test_timestamp_objects_matching_canonical_baseline_remain_baseline():
    from filters.interaction_mode import get_interaction_mode, has_active_global_filters

    traffic = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_date_start": pd.Timestamp("2022-01-01"),
        "traffic_date_end": pd.Timestamp("2024-08-31"),
    }

    assert has_active_global_filters(traffic, "traffic") is False
    assert get_interaction_mode(traffic, "traffic") == "baseline"


def test_changed_dates_activate_global_filter_mode():
    from filters.interaction_mode import get_interaction_mode, has_active_global_filters

    traffic = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_date_start": date(2022, 2, 1),
        "traffic_date_end": date(2024, 8, 31),
    }
    aqi = {
        **AQI_STATE_DEFAULTS,
        "aqi_date_start": date(2021, 1, 1),
        "aqi_date_end": date(2023, 11, 30),
    }

    assert has_active_global_filters(traffic, "traffic") is True
    assert get_interaction_mode(traffic, "traffic") == "global_filter_mode"
    assert has_active_global_filters(aqi, "aqi") is True
    assert get_interaction_mode(aqi, "aqi") == "global_filter_mode"


def test_selected_canonical_dimensions_activate_global_filter_mode():
    from filters.interaction_mode import get_interaction_mode, has_active_global_filters

    traffic_area = {**TRAFFIC_STATE_DEFAULTS, "traffic_selected_areas": ["Whitefield"]}
    traffic_weather = {**TRAFFIC_STATE_DEFAULTS, "traffic_selected_weather": ["Rain"]}
    traffic_roads = {**TRAFFIC_STATE_DEFAULTS, "traffic_selected_roads": ["Road A"]}
    traffic_roadwork = {**TRAFFIC_STATE_DEFAULTS, "traffic_selected_roadwork": "Yes"}
    aqi_category = {**AQI_STATE_DEFAULTS, "aqi_selected_categories": ["Severe"]}
    aqi_season = {**AQI_STATE_DEFAULTS, "aqi_selected_seasons": ["Winter"]}

    for state in (traffic_area, traffic_weather, traffic_roads, traffic_roadwork):
        assert has_active_global_filters(state, "traffic") is True
        assert get_interaction_mode(state, "traffic") == "global_filter_mode"
    for state in (aqi_category, aqi_season):
        assert has_active_global_filters(state, "aqi") is True
        assert get_interaction_mode(state, "aqi") == "global_filter_mode"


def test_filter_panel_badge_uses_normalized_canonical_scope(monkeypatch):
    from components.filter_panel import _filters_active

    fake = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_date_start": date(2022, 1, 1),
        "traffic_date_end": date(2024, 8, 31),
    }
    monkeypatch.setattr("components.filter_panel.st.session_state", fake, raising=False)

    assert _filters_active("traffic", TRAFFIC_STATE_DEFAULTS) is False


def test_default_startup_interaction_mode_is_baseline():
    from filters.interaction_mode import get_interaction_mode

    assert get_interaction_mode(dict(TRAFFIC_STATE_DEFAULTS), "traffic") == "baseline"
    assert get_interaction_mode(dict(AQI_STATE_DEFAULTS), "aqi") == "baseline"


def test_aqi_overlay_scope_filters_category_for_participant():
    df = pd.DataFrame(
        {
            "Date": pd.to_datetime([datetime(2023, 1, 1), datetime(2023, 1, 2)]),
            "aqi_category": ["Poor", "Severe"],
            "season": ["Winter", "Winter"],
        }
    )
    state = {
        **AQI_STATE_DEFAULTS,
        "aqi_investigation_scope": {
            "season": None,
            "category": "Severe",
            "date": None,
            "year": None,
            "week": None,
            "regime": None,
            "pollutant": None,
            "source_chart": "A-02",
            "focus_mode": "calendar_event",
        },
    }

    scoped = apply_investigation_overlay_scope(df, "aqi", "A-06", state)

    assert scoped["aqi_category"].tolist() == ["Severe"]


def test_reset_all_restores_baseline_interaction_mode(monkeypatch):
    from filters.interaction_mode import get_interaction_mode

    fake = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_selected_areas": ["Whitefield"],
        "traffic_selected_area": "Whitefield",
        "traffic_investigation_scope": {
            **TRAFFIC_STATE_DEFAULTS["traffic_investigation_scope"],
            "area": "Whitefield",
            "source_chart": "T-01",
        },
    }
    monkeypatch.setattr("filters.transitions.st.session_state", fake, raising=False)

    result = dispatch(GlobalFiltersReset(dashboard="traffic"))

    assert result.changed_domains == ("global_filters", "visual_focus", "investigation_overlay")
    assert fake["traffic_selected_areas"] == []
    assert fake["traffic_selected_area"] is None
    assert fake["traffic_investigation_scope"] == TRAFFIC_STATE_DEFAULTS["traffic_investigation_scope"]
    assert get_interaction_mode(fake, "traffic") == "baseline"


def test_clear_global_filters_clears_canonical_filters_only(monkeypatch):
    fake = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_selected_areas": ["Whitefield"],
        "traffic_selected_weather": ["Rain"],
        "traffic_selected_roadwork": "Yes",
        "traffic_selected_roads": ["Old Airport Road"],
        "traffic_filters_active": True,
        "traffic_selected_area": "Indiranagar",
        "traffic_focus_chart": "T-01",
        "traffic_investigation_scope": {
            **TRAFFIC_STATE_DEFAULTS["traffic_investigation_scope"],
            "area": "Indiranagar",
            "source_chart": "T-01",
        },
        "last_transition_trace": {"keep": "trace"},
    }
    monkeypatch.setattr("filters.transitions.st.session_state", fake, raising=False)

    result = dispatch(ClearGlobalFilters(dashboard="traffic"))

    assert result.changed_domains == ("global_filters",)
    assert fake["traffic_selected_areas"] == []
    assert fake["traffic_selected_weather"] == []
    assert fake["traffic_selected_roadwork"] == TRAFFIC_STATE_DEFAULTS["traffic_selected_roadwork"]
    assert fake["traffic_selected_roads"] == []
    assert fake["traffic_filters_active"] is False
    assert fake["traffic_selected_area"] == "Indiranagar"
    assert fake["traffic_focus_chart"] == "T-01"
    assert fake["traffic_investigation_scope"]["area"] == "Indiranagar"


def test_pending_global_filter_clear_uses_pre_widget_queue(monkeypatch):
    from filters.state import apply_pending_filter_reset, request_global_filter_clear

    fake = {
        **AQI_STATE_DEFAULTS,
        "aqi_selected_categories": ["Severe"],
        "aqi_selected_seasons": ["Winter"],
        "aqi_filters_active": True,
        "aqi_selected_category": "Poor",
    }
    monkeypatch.setattr("filters.state.st.session_state", fake, raising=False)
    monkeypatch.setattr("filters.transitions.st.session_state", fake, raising=False)

    request_global_filter_clear("aqi")
    apply_pending_filter_reset("aqi")

    assert fake["aqi_selected_categories"] == []
    assert fake["aqi_selected_seasons"] == []
    assert fake["aqi_filters_active"] is False
    assert fake["aqi_selected_category"] == "Poor"
