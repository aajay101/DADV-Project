"""Session state initialization and helpers — single source of truth."""

import time
from datetime import datetime
from typing import Any

import streamlit as st

APP_STATE_DEFAULTS = {
    "active_dashboard": "traffic",
    "viewport_width": 1280,
    "viewport_breakpoint": "desktop",
    "compact_mode": False,
    "advanced_lab_disabled_compact": False,
    "traffic_filter_updating": False,
    "aqi_filter_updating": False,
    "last_filter_change_at": None,
    "fullscreen_chart_key": None,
    "fullscreen_dashboard": None,
    "session_start_time": None,
    "long_session_notice_dismissed": False,
    "traffic_data_loaded_at": None,
    "aqi_data_loaded_at": None,
    "traffic_data_stale": False,
    "aqi_data_stale": False,
    "export_in_progress": False,
    "last_export_status": None,
    "developer_mode": False,
    "runtime_debug_enabled": False,
    "last_transition_trace": None,
    "last_rerender_trace": None,
    "chart_selection_epochs": {},
    "performance_render_traces": [],
    "performance_cache_stats": {},
    "last_cache_invalidation_trace": None,
    "runtime_observability_events": [],
    "runtime_observability_warnings": [],
    "runtime_replay_log": [],
    "runtime_health_snapshot": {},
    "runtime_recovery_events": [],
    "runtime_assertion_failures": [],
}

TRAFFIC_STATE_DEFAULTS = {
    "traffic_active_tab": 0,
    "traffic_lab_gate_passed": False,
    "traffic_date_start": datetime(2022, 1, 1),
    "traffic_date_end": datetime(2024, 8, 31),
    "traffic_selected_areas": [],
    "traffic_selected_weather": [],
    "traffic_selected_roadwork": "Both",
    "traffic_selected_roads": [],
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
    "traffic_investigation_scope": {
        "area": None,
        "road": None,
        "month": None,
        "quadrant": None,
        "source_chart": None,
        "focus_mode": None,
    },
    "traffic_lab_use_full_dataset": True,
    "traffic_lab_t13_view": "heatmap",
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
    "aqi_investigation_scope": {
        "season": None,
        "category": None,
        "date": None,
        "year": None,
        "week": None,
        "regime": None,
        "pollutant": None,
        "source_chart": None,
        "focus_mode": None,
    },
    "aqi_pairplot_visible_categories": [],
    "aqi_pairplot_category_preset": None,
    "aqi_lab_use_full_dataset": True,
}

STATE_DOMAIN_KEYS = {
    "traffic": {
        "global_filters": (
            "traffic_date_start",
            "traffic_date_end",
            "traffic_selected_areas",
            "traffic_selected_weather",
            "traffic_selected_roadwork",
            "traffic_selected_roads",
            "traffic_filters_active",
        ),
        "visual_focus": (
            "traffic_selected_road",
            "traffic_selected_area",
            "traffic_selected_month",
            "traffic_selected_quadrant",
            "traffic_radar_focus_area",
            "traffic_focus_chart",
            "traffic_focus_mode",
        ),
        "investigation_overlay": (
            "traffic_investigation_scope",
        ),
        "chart_local_state": (
            "traffic_t03_zoom_start",
            "traffic_t03_zoom_end",
            "traffic_radar_visible_areas",
            "traffic_radar_dimmed_areas",
            "traffic_radar_comparison_mode",
            "traffic_radar_comparison_n",
            "traffic_lab_use_full_dataset",
            "traffic_lab_t13_view",
        ),
    },
    "aqi": {
        "global_filters": (
            "aqi_date_start",
            "aqi_date_end",
            "aqi_selected_categories",
            "aqi_selected_seasons",
            "aqi_filters_active",
        ),
        "visual_focus": (
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
        ),
        "investigation_overlay": (
            "aqi_investigation_scope",
        ),
        "chart_local_state": (
            "aqi_pairplot_visible_categories",
            "aqi_pairplot_category_preset",
            "aqi_lab_use_full_dataset",
        ),
    },
}

RUNTIME_STATE_KEYS = (
    "active_dashboard",
    "viewport_width",
    "viewport_breakpoint",
    "compact_mode",
    "advanced_lab_disabled_compact",
    "traffic_filter_updating",
    "aqi_filter_updating",
    "last_filter_change_at",
    "fullscreen_chart_key",
    "fullscreen_dashboard",
    "session_start_time",
    "long_session_notice_dismissed",
    "traffic_data_loaded_at",
    "aqi_data_loaded_at",
    "traffic_data_stale",
    "aqi_data_stale",
    "export_in_progress",
    "last_export_status",
    "developer_mode",
    "runtime_debug_enabled",
    "last_transition_trace",
    "last_rerender_trace",
    "chart_selection_epoch",
    "chart_selection_epochs",
    "performance_render_traces",
    "performance_cache_stats",
    "last_cache_invalidation_trace",
    "runtime_observability_events",
    "runtime_observability_warnings",
    "runtime_replay_log",
    "runtime_health_snapshot",
    "runtime_recovery_events",
    "runtime_assertion_failures",
)


def _init_defaults(defaults: dict) -> None:
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def dashboard_state_snapshot(dashboard: str) -> dict[str, dict[str, Any]]:
    """Return existing session keys grouped by explicit state ownership domain."""
    domains = STATE_DOMAIN_KEYS["traffic" if dashboard == "traffic" else "aqi"]
    return {
        "global_filters": {key: st.session_state.get(key) for key in domains["global_filters"]},
        "visual_focus": {key: st.session_state.get(key) for key in domains["visual_focus"]},
        "investigation_overlay": {
            key: st.session_state.get(key) for key in domains["investigation_overlay"]
        },
        "chart_local_state": {key: st.session_state.get(key) for key in domains["chart_local_state"]},
        "runtime_state": {key: st.session_state.get(key) for key in RUNTIME_STATE_KEYS},
    }


def init_app_state() -> None:
    """Initialize cross-dashboard application state."""
    _init_defaults(APP_STATE_DEFAULTS)
    if st.session_state.get("session_start_time") is None:
        st.session_state["session_start_time"] = time.time()


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


def get_tab_nav_widget_key(dashboard: str) -> str:
    """Streamlit radio key for page labels (widget display only)."""
    return f"{dashboard}_tab_nav"


def _nav_programmatic_flag_key(dashboard: str) -> str:
    return f"{dashboard}_tab_nav_programmatic_sync"


def apply_programmatic_nav_sync(dashboard: str) -> None:
    """
    Sync radio widget label BEFORE st.radio() when tab changed via code (not user click).
    Must run before the widget is instantiated on this rerun.
    """
    from config.page_config import AQI_TABS, TRAFFIC_TABS

    if not st.session_state.pop(_nav_programmatic_flag_key(dashboard), False):
        return
    tabs = TRAFFIC_TABS if dashboard == "traffic" else AQI_TABS
    idx = get_active_tab(dashboard)
    st.session_state[get_tab_nav_widget_key(dashboard)] = tabs[idx]["label"]


def set_active_tab(dashboard: str, tab_index: int, *, from_widget: bool = False):
    """
    Single source of truth: traffic_active_tab / aqi_active_tab (integer index).

    from_widget=True: user clicked the nav radio — only update index (widget already set).
    from_widget=False: breadcrumb/nav card/lab — flag sync for next rerun before radio mounts.
    """
    from filters.transitions import ActiveTabChanged, dispatch

    return dispatch(
        ActiveTabChanged(
            dashboard="traffic" if dashboard == "traffic" else "aqi",
            tab_index=tab_index,
            from_widget=from_widget,
        )
    )


def get_active_tab(dashboard: str) -> int:
    return int(st.session_state.get(get_active_tab_key(dashboard), 0))


def get_active_page_module(dashboard: str) -> str:
    """Resolve page module key (e.g. p2_temporal_intelligence) from active tab index."""
    from config.page_config import AQI_TABS, TRAFFIC_TABS

    tabs = TRAFFIC_TABS if dashboard == "traffic" else AQI_TABS
    return tabs[get_active_tab(dashboard)]["module"]


def log_nav_debug(dashboard: str, event: str, **extra: object) -> None:
    """Optional nav diagnostics — enable with st.session_state['buip_nav_debug'] = True."""
    if not st.session_state.get("buip_nav_debug"):
        return
    import logging

    parts = [
        f"dashboard={dashboard}",
        f"active_tab={get_active_tab(dashboard)}",
        f"page={get_active_page_module(dashboard)}",
        f"event={event}",
    ]
    for key, val in extra.items():
        parts.append(f"{key}={val}")
    logging.getLogger("buip.nav").info(" | ".join(parts))


def pass_lab_gate(dashboard: str):
    from filters.transitions import LabGateChanged, dispatch

    return dispatch(LabGateChanged(dashboard="traffic" if dashboard == "traffic" else "aqi", passed=True))


def is_lab_gate_passed(dashboard: str) -> bool:
    return bool(st.session_state.get(get_lab_gate_key(dashboard), False))


def reset_lab_gate(dashboard: str):
    from filters.transitions import LabGateChanged, dispatch

    return dispatch(LabGateChanged(dashboard="traffic" if dashboard == "traffic" else "aqi", passed=False))


def clear_filter_updating(prefix: str) -> None:
    """Clear rerun progress state after filter values have synchronized."""
    st.session_state[f"{prefix}_filter_updating"] = False


def is_filter_updating(prefix: str) -> bool:
    return bool(st.session_state.get(f"{prefix}_filter_updating", False))


def _pending_filter_reset_key(dashboard: str) -> str:
    return f"{dashboard}_pending_filter_reset"


def _pending_global_filter_clear_key(dashboard: str) -> str:
    return f"{dashboard}_pending_global_filter_clear"


def request_filter_reset(dashboard: str) -> None:
    """Queue filter reset for the next rerun (before filter widgets mount)."""
    st.session_state[_pending_filter_reset_key(dashboard)] = True


def request_global_filter_clear(dashboard: str) -> None:
    """Queue canonical global-filter clearing before filter widgets mount."""
    st.session_state[_pending_global_filter_clear_key(dashboard)] = True


def apply_pending_filter_reset(dashboard: str) -> None:
    """
    Apply queued filter reset before st.date_input / multiselect widgets render.
    Must run at the top of filter_panel on each rerun.
    """
    reset_requested = st.session_state.pop(_pending_filter_reset_key(dashboard), False)
    clear_requested = st.session_state.pop(_pending_global_filter_clear_key(dashboard), False)
    if not reset_requested:
        if not clear_requested:
            return
        from filters.transitions import ClearGlobalFilters, dispatch

        dispatch(ClearGlobalFilters(dashboard="traffic" if dashboard == "traffic" else "aqi"))
        return
    from filters.transitions import GlobalFiltersReset, dispatch

    dispatch(GlobalFiltersReset(dashboard="traffic" if dashboard == "traffic" else "aqi"))
