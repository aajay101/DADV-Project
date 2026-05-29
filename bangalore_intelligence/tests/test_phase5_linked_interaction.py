"""Phase 5 - linked chart focus, handlers, and state ownership separation."""

from __future__ import annotations

from unittest.mock import MagicMock

from config.data_config import COL_AREA, COL_ROAD, TRAFFIC_AREAS
from filters.interaction import (
    apply_interaction_payload,
    clear_investigation,
    read_traffic_interaction,
)
from filters.state import TRAFFIC_STATE_DEFAULTS
from filters.traffic_filters import apply_traffic_filters
from services.state.chart_handlers import (
    dispatch_chart_selection,
    handle_t01,
    handle_t05,
    handle_t15,
)


def _point(**kwargs) -> dict:
    return kwargs


def test_t01_handler_sets_area_focus():
    area = TRAFFIC_AREAS[0]
    payload = handle_t01(_point(y=area, label=area), {})
    assert payload["selected_area"] == area
    assert payload["selected_road"] is None
    assert payload["focus_mode"] == "area_ranking"


def test_t05_handler_sets_road_and_area(sample_traffic_df):
    row = sample_traffic_df.iloc[0]
    road = row[COL_ROAD]
    area = row[COL_AREA]
    payload = handle_t05(
        _point(
            text=road,
            x=80.0,
            y=85.0,
            customdata=[area, 22.0, 1, 0.5],
        ),
        {"roads_df": sample_traffic_df.groupby(COL_ROAD).first().reset_index()},
    )
    assert payload["selected_road"] == road
    assert payload["selected_area"] == area


def test_t15_handler_sets_area_and_month():
    area = TRAFFIC_AREAS[1]
    month = "2023-06"
    payload = handle_t15(_point(y=area, x=month), {})
    assert payload["selected_area"] == area
    assert payload["selected_month"] == month
    assert payload["focus_mode"] == "area_month"


def test_dispatch_applies_traffic_visual_state(monkeypatch):
    fake: dict = dict(TRAFFIC_STATE_DEFAULTS)
    monkeypatch.setattr("filters.interaction.st.session_state", fake, raising=False)

    area = TRAFFIC_AREAS[2]
    selection = MagicMock()
    selection.points = [_point(y=area, label=area)]
    plotly_state = MagicMock(selection=selection)

    changed = dispatch_chart_selection("T-01", plotly_state, {})
    assert changed is True
    assert fake["traffic_selected_area"] == area
    assert fake["traffic_focus_chart"] == "T-01"


def test_clear_investigation_preserves_global_filters(monkeypatch):
    fake: dict = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_selected_areas": ["Koramangala"],
        "traffic_selected_weather": ["Rain"],
        "traffic_selected_area": "Indiranagar",
        "traffic_selected_road": "Road_1",
        "traffic_focus_chart": "T-05",
        "traffic_filters_active": True,
    }
    monkeypatch.setattr("filters.interaction.st.session_state", fake, raising=False)
    monkeypatch.setattr("filters.scope_sync.st.session_state", fake, raising=False)

    clear_investigation("traffic")

    assert fake["traffic_selected_area"] is None
    assert fake["traffic_selected_road"] is None
    assert fake["traffic_focus_chart"] is None
    assert "traffic_pending_filter_scope" not in fake
    assert fake["traffic_selected_areas"] == ["Koramangala"]
    assert fake["traffic_selected_weather"] == ["Rain"]
    assert fake["traffic_filters_active"] is True


def test_chart_focus_does_not_queue_global_filters(monkeypatch):
    fake: dict = {
        **TRAFFIC_STATE_DEFAULTS,
        "traffic_selected_area": "Whitefield",
        "traffic_selected_road": None,
    }
    monkeypatch.setattr("filters.interaction.st.session_state", fake, raising=False)
    monkeypatch.setattr("filters.scope_sync.st.session_state", fake, raising=False)

    apply_interaction_payload(
        "traffic",
        {
            "chart": "T-01",
            "selected_area": "Whitefield",
            "selected_road": None,
            "focus_mode": "area_ranking",
        },
    )
    assert fake["traffic_selected_area"] == "Whitefield"
    assert fake["traffic_selected_areas"] == []
    assert "traffic_pending_filter_scope" not in fake


def test_apply_payload_preserves_global_area_filters(monkeypatch):
    fake: dict = dict(TRAFFIC_STATE_DEFAULTS)
    monkeypatch.setattr("filters.interaction.st.session_state", fake, raising=False)
    monkeypatch.setattr("filters.scope_sync.st.session_state", fake, raising=False)

    apply_interaction_payload(
        "traffic",
        {
            "chart": "T-01",
            "selected_area": "Koramangala",
            "selected_road": None,
            "focus_mode": "area_ranking",
        },
    )
    assert fake["traffic_selected_area"] == "Koramangala"
    assert fake["traffic_selected_areas"] == []
    assert "traffic_pending_filter_scope" not in fake


def test_apply_payload_updates_interaction_snapshot(monkeypatch):
    fake: dict = dict(TRAFFIC_STATE_DEFAULTS)
    monkeypatch.setattr("filters.interaction.st.session_state", fake, raising=False)

    apply_interaction_payload(
        "traffic",
        {
            "chart": "T-15",
            "selected_area": "MG Road",
            "selected_month": "2024-01",
            "focus_mode": "area_month",
        },
    )
    state = read_traffic_interaction()
    assert state["selected_area"] == "MG Road"
    assert state["selected_month"] == "2024-01"


def test_clear_investigation_does_not_expand_data_scope(sample_traffic_df, monkeypatch):
    fake: dict = dict(TRAFFIC_STATE_DEFAULTS)
    fake["traffic_selected_areas"] = ["Koramangala"]
    monkeypatch.setattr("filters.interaction.st.session_state", fake, raising=False)
    monkeypatch.setattr("filters.scope_sync.st.session_state", fake, raising=False)

    filtered = apply_traffic_filters(sample_traffic_df, fake, exclude_date_filter=True)
    clear_investigation("traffic")
    filtered_after = apply_traffic_filters(sample_traffic_df, fake, exclude_date_filter=True)

    assert len(filtered_after) == len(filtered)
    assert set(filtered[COL_AREA].unique()) == {"Koramangala"}
