"""Phase 4 — global traffic filter expansion (weather, roadwork, roads)."""

from __future__ import annotations

import pandas as pd

from config.data_config import COL_AREA, COL_ROAD, COL_ROADWORK, COL_WEATHER
from data_layer.page_bundles import build_traffic_patterns_bundle, build_traffic_command_bundle
from filters.state import TRAFFIC_STATE_DEFAULTS
from filters.traffic_filters import apply_traffic_filters, reset_traffic_filters
from utils.formatters import filter_snapshot_from_state, fmt_filter_summary


def _state(**overrides) -> dict:
    state = dict(TRAFFIC_STATE_DEFAULTS)
    state.update(overrides)
    return state


def test_weather_filter_restricts_rows(sample_traffic_df):
    full = apply_traffic_filters(sample_traffic_df, _state(), exclude_date_filter=True)
    weather = sample_traffic_df[COL_WEATHER].iloc[0]
    filtered = apply_traffic_filters(
        sample_traffic_df,
        _state(traffic_selected_weather=[weather]),
        exclude_date_filter=True,
    )
    assert len(filtered) <= len(full)
    assert not filtered.empty
    assert filtered[COL_WEATHER].eq(weather).all()


def test_roadwork_filter_restricts_rows(sample_traffic_df):
    roadwork = sample_traffic_df[COL_ROADWORK].iloc[0]
    filtered = apply_traffic_filters(
        sample_traffic_df,
        _state(traffic_selected_roadwork=roadwork),
        exclude_date_filter=True,
    )
    assert filtered[COL_ROADWORK].eq(roadwork).all()


def test_roadwork_both_matches_unfiltered(sample_traffic_df):
    baseline = apply_traffic_filters(sample_traffic_df, _state(), exclude_date_filter=True)
    both = apply_traffic_filters(
        sample_traffic_df,
        _state(traffic_selected_roadwork="Both"),
        exclude_date_filter=True,
    )
    assert len(baseline) == len(both)


def test_roads_filter_restricts_rows(sample_traffic_df):
    road = sample_traffic_df[COL_ROAD].iloc[0]
    filtered = apply_traffic_filters(
        sample_traffic_df,
        _state(traffic_selected_roads=[road]),
        exclude_date_filter=True,
    )
    assert filtered[COL_ROAD].eq(road).all()


def test_combined_area_and_weather_filters(sample_traffic_df):
    area = sample_traffic_df[COL_AREA].iloc[0]
    weather = sample_traffic_df.loc[sample_traffic_df[COL_AREA] == area, COL_WEATHER].iloc[0]
    filtered = apply_traffic_filters(
        sample_traffic_df,
        _state(traffic_selected_areas=[area], traffic_selected_weather=[weather]),
        exclude_date_filter=True,
    )
    assert filtered[COL_AREA].eq(area).all()
    assert filtered[COL_WEATHER].eq(weather).all()


def test_empty_compound_filter_result_preserves_user_filter_state():
    df = pd.DataFrame(
        [
            {
                COL_AREA: "Whitefield",
                COL_WEATHER: "Clear",
                COL_ROADWORK: "Major",
                COL_ROAD: "Road_1",
            },
            {
                COL_AREA: "Indiranagar",
                COL_WEATHER: "Rain",
                COL_ROADWORK: "Minor",
                COL_ROAD: "Road_2",
            },
        ]
    )
    state = _state(
        traffic_selected_areas=["Whitefield"],
        traffic_selected_weather=["Rain"],
        traffic_selected_roadwork="Major",
        traffic_selected_roads=["Road_2"],
    )
    before = {
        "traffic_selected_areas": list(state["traffic_selected_areas"]),
        "traffic_selected_weather": list(state["traffic_selected_weather"]),
        "traffic_selected_roadwork": state["traffic_selected_roadwork"],
        "traffic_selected_roads": list(state["traffic_selected_roads"]),
    }

    filtered = apply_traffic_filters(df, state, exclude_date_filter=True)

    assert filtered.empty
    assert state["traffic_selected_areas"] == before["traffic_selected_areas"]
    assert state["traffic_selected_weather"] == before["traffic_selected_weather"]
    assert state["traffic_selected_roadwork"] == before["traffic_selected_roadwork"]
    assert state["traffic_selected_roads"] == before["traffic_selected_roads"]


def test_filter_snapshot_and_summary_include_new_fields():
    state = _state(
        traffic_selected_weather=["Rain"],
        traffic_selected_roadwork="Minor",
        traffic_selected_roads=["Road_1"],
    )
    snap = filter_snapshot_from_state(state, "traffic")
    assert snap["traffic_selected_weather"] == ["Rain"]
    assert snap["traffic_selected_roadwork"] == "Minor"
    assert snap["traffic_selected_roads"] == ["Road_1"]
    summary = fmt_filter_summary(snap, "traffic")
    assert "Weather: Rain" in summary
    assert "Roadwork: Minor" in summary
    assert "Roads: Road_1" in summary


def test_reset_traffic_filters_clears_expanded_fields(monkeypatch):
    import streamlit as st

    fake: dict = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_selected_weather": ["Haze"],
        "traffic_selected_roadwork": "Major",
        "traffic_selected_roads": ["Road_3"],
        "traffic_filters_active": True,
    }
    monkeypatch.setattr(st, "session_state", fake, raising=False)
    monkeypatch.setattr(
        "filters.interaction.clear_traffic_selection",
        lambda: None,
        raising=False,
    )

    class _Cache:
        @staticmethod
        def clear():
            return None

    monkeypatch.setattr(st, "cache_data", type("CD", (), {"clear": staticmethod(lambda: None)})(), raising=False)

    reset_traffic_filters()

    assert fake["traffic_selected_weather"] == []
    assert fake["traffic_selected_roadwork"] == "Both"
    assert fake["traffic_selected_roads"] == []
    assert fake["traffic_filters_active"] is False


def test_weather_filter_changes_patterns_bundle_kpis(sample_traffic_df):
    from unittest.mock import patch

    baseline_state = _state()
    weather = sample_traffic_df[COL_WEATHER].mode().iloc[0]
    narrow_state = _state(traffic_selected_weather=[weather])

    with patch("data_layer.page_bundles.load_traffic_clean", return_value=sample_traffic_df):
        base_bundle = build_traffic_patterns_bundle(baseline_state)
        narrow_bundle = build_traffic_patterns_bundle(narrow_state)

    assert base_bundle["record_count"] != narrow_bundle["record_count"] or base_bundle["n"] != narrow_bundle["n"]


def test_area_filter_changes_command_bundle(sample_traffic_df):
    from unittest.mock import patch

    area = sample_traffic_df[COL_AREA].iloc[0]
    with patch("data_layer.page_bundles.load_traffic_clean", return_value=sample_traffic_df):
        all_bundle = build_traffic_command_bundle(_state())
        area_bundle = build_traffic_command_bundle(_state(traffic_selected_areas=[area]))
    assert area_bundle["n"] <= all_bundle["n"]
