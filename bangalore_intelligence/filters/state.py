"""Session state initialization and helpers — single source of truth."""

from datetime import datetime

import streamlit as st

APP_STATE_DEFAULTS = {
    "active_dashboard": "traffic",
}

TRAFFIC_STATE_DEFAULTS = {
    "traffic_active_tab": 0,
    "traffic_lab_gate_passed": False,
    "traffic_date_start": datetime(2022, 1, 1),
    "traffic_date_end": datetime(2024, 8, 31),
    "traffic_selected_areas": [],
    "traffic_filters_active": False,
    "traffic_selected_road": None,
    "traffic_selected_area": None,
    "traffic_selected_month": None,
    "traffic_t03_zoom_start": None,
    "traffic_t03_zoom_end": None,
    "traffic_radar_visible_areas": [],
    "traffic_radar_focus_area": None,
    "traffic_radar_dimmed_areas": [],
    "traffic_radar_comparison_mode": None,
    "traffic_radar_comparison_n": 3,
    "traffic_selected_quadrant": None,
    "traffic_focus_chart": None,
    "traffic_focus_mode": None,
}

AQI_STATE_DEFAULTS = {
    "aqi_active_tab": 0,
    "aqi_lab_gate_passed": False,
    "aqi_date_start": datetime(2021, 1, 1),
    "aqi_date_end": datetime(2023, 12, 31),
    "aqi_selected_categories": [],
    "aqi_selected_seasons": [],
    "aqi_filters_active": False,
    "aqi_selected_date": None,
    "aqi_selected_month": None,
    "aqi_selected_regime": None,
    "aqi_selected_season": None,
    "aqi_selected_category": None,
    "aqi_selected_year": None,
    "aqi_selected_week": None,
    "aqi_selected_pollutant": None,
    "aqi_focus_chart": None,
    "aqi_focus_mode": None,
    "aqi_context_pm25": None,
}


def _init_defaults(defaults: dict) -> None:
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def init_app_state() -> None:
    """Initialize cross-dashboard application state."""
    _init_defaults(APP_STATE_DEFAULTS)


def init_traffic_state() -> None:
    """Initialize traffic dashboard session state."""
    _init_defaults(TRAFFIC_STATE_DEFAULTS)
    from filters.interaction import init_interaction_state

    init_interaction_state()


def init_aqi_state() -> None:
    """Initialize AQI dashboard session state."""
    _init_defaults(AQI_STATE_DEFAULTS)
    from filters.interaction import init_interaction_state

    init_interaction_state()


def get_active_tab_key(dashboard: str) -> str:
    return "traffic_active_tab" if dashboard == "traffic" else "aqi_active_tab"


def get_lab_gate_key(dashboard: str) -> str:
    return "traffic_lab_gate_passed" if dashboard == "traffic" else "aqi_lab_gate_passed"


def set_active_tab(dashboard: str, tab_index: int) -> None:
    st.session_state[get_active_tab_key(dashboard)] = tab_index


def get_active_tab(dashboard: str) -> int:
    return int(st.session_state.get(get_active_tab_key(dashboard), 0))


def pass_lab_gate(dashboard: str) -> None:
    st.session_state[get_lab_gate_key(dashboard)] = True


def is_lab_gate_passed(dashboard: str) -> bool:
    return bool(st.session_state.get(get_lab_gate_key(dashboard), False))


def reset_lab_gate(dashboard: str) -> None:
    st.session_state[get_lab_gate_key(dashboard)] = False
