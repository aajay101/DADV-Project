"""Centralized linked-selection and interaction state governance.



Interaction ownership lives here — pages orchestrate, components present,

charts render. Session keys are namespaced and initialized via filters.state.

Temporary investigation focus is separate from persistent filter state.

"""



from __future__ import annotations



from typing import Any, Literal



import streamlit as st



from components.interaction_education.focus_behavior_help import render_clear_focus_hint
from components.interaction_education.interaction_mode_help import render_chart_interaction_mode_hint
from components.interaction_education.overlay_explanations import render_overlay_hint
from filters.state import AQI_STATE_DEFAULTS, TRAFFIC_STATE_DEFAULTS
from filters.transitions import (
    ChartFocusChanged,
    FocusCleared,
    TransitionResult,
    dispatch,
    request_rerun,
    request_rerun_for_last_transition,
)



DashboardId = Literal["traffic", "aqi"]

LinkedDomain = Literal["traffic", "aqi"]



BUNDLE_KEY_LINKED_CONTROLS = "linked_controls"

CHART_EPOCH_KEY = "chart_selection_epoch"



TRAFFIC_INTERACTION_KEYS = (

    "traffic_selected_area",

    "traffic_selected_road",

    "traffic_selected_month",

    "traffic_radar_focus_area",

)



AQI_INTERACTION_KEYS = (

    "aqi_selected_category",

    "aqi_selected_season",

    "aqi_selected_date",

    "aqi_selected_month",

    "aqi_selected_regime",

)



_EXTRA_INTERACTION_KEYS = (

    "traffic_selected_quadrant",

    "traffic_focus_chart",

    "traffic_focus_mode",

    "aqi_selected_year",

    "aqi_selected_week",

    "aqi_selected_pollutant",

    "aqi_focus_chart",

    "aqi_focus_mode",

    "aqi_context_pm25",

)



INTERACTION_DEFAULTS: dict[str, Any] = {

    k: TRAFFIC_STATE_DEFAULTS[k]

    for k in TRAFFIC_INTERACTION_KEYS

} | {

    k: AQI_STATE_DEFAULTS[k]

    for k in AQI_INTERACTION_KEYS

} | {

    k: (TRAFFIC_STATE_DEFAULTS if k.startswith("traffic_") else AQI_STATE_DEFAULTS)[k]

    for k in _EXTRA_INTERACTION_KEYS

}



QUADRANT_LABELS = {

    "critical_overload": "Critical Overload",

    "constrained_flow": "Constrained Flow",

    "capacity_margin": "Capacity Margin",

    "baseline": "Baseline Operations",

}





def quadrant_label(code: str | None) -> str:

    if not code:

        return "—"

    return QUADRANT_LABELS.get(code, code.replace("_", " ").title())





def init_interaction_state() -> None:

    """Ensure all linked-selection keys exist with explicit defaults."""

    for key, value in INTERACTION_DEFAULTS.items():

        if key not in st.session_state:

            st.session_state[key] = value

    if CHART_EPOCH_KEY not in st.session_state:

        st.session_state[CHART_EPOCH_KEY] = 0
    if "chart_selection_epochs" not in st.session_state:

        st.session_state["chart_selection_epochs"] = {}





def _ensure_initialized() -> None:

    init_interaction_state()





def chart_widget_key(page_key: str, chart_id: str, dashboard: str) -> str:

    epochs = st.session_state.get("chart_selection_epochs") or {}
    epoch = int(epochs.get(chart_id, st.session_state.get(CHART_EPOCH_KEY, 0)))

    return f"buip_{dashboard}_{page_key}_{chart_id}_{epoch}"


# --- Normalized interaction snapshots ---





def read_traffic_interaction() -> dict[str, Any]:

    _ensure_initialized()

    area = st.session_state.get("traffic_selected_area")

    road = st.session_state.get("traffic_selected_road")

    return {

        "selected_chart": st.session_state.get("traffic_focus_chart"),
        "selected_area": area,

        "selected_road": road,

        "selected_month": st.session_state.get("traffic_selected_month"),

        "selected_quadrant": st.session_state.get("traffic_selected_quadrant"),

        "focus_mode": st.session_state.get("traffic_focus_mode"),

        "focus_entity": st.session_state.get("traffic_radar_focus_area"),

        "linked_enabled": bool(area or road),

        "active_context": _traffic_context_label(road, area),

    }





def read_aqi_interaction() -> dict[str, Any]:

    _ensure_initialized()

    season = st.session_state.get("aqi_selected_season")

    category = st.session_state.get("aqi_selected_category")

    return {

        "selected_chart": st.session_state.get("aqi_focus_chart"),

        "selected_day": st.session_state.get("aqi_selected_date"),

        "selected_year": st.session_state.get("aqi_selected_year"),

        "selected_week": st.session_state.get("aqi_selected_week"),

        "selected_pollutant": st.session_state.get("aqi_selected_pollutant"),

        "selected_category": category,

        "selected_season": season,

        "selected_date": st.session_state.get("aqi_selected_date"),

        "selected_month": st.session_state.get("aqi_selected_month"),

        "selected_regime": st.session_state.get("aqi_selected_regime"),

        "focus_mode": st.session_state.get("aqi_focus_mode"),

        "context_pm25": st.session_state.get("aqi_context_pm25"),

        "linked_enabled": bool(

            season

            or category

            or st.session_state.get("aqi_selected_date")

            or st.session_state.get("aqi_selected_regime")

        ),

        "active_context": _aqi_active_context(season, category),

    }





def read_interaction_state(dashboard: DashboardId) -> dict[str, Any]:

    if dashboard == "traffic":

        return read_traffic_interaction()

    return read_aqi_interaction()





def _traffic_context_label(road: str | None, area: str | None) -> str | None:

    month = st.session_state.get("traffic_selected_month")

    if road:

        quad = quadrant_label(st.session_state.get("traffic_selected_quadrant"))

        base = f"{road} · {quad}" if quad != "—" else road

        return f"{base} · {month}" if month else base

    if area and month:

        return f"{area} · {month}"

    return area





def _aqi_active_context(season: str | None, category: str | None) -> str | None:

    day = st.session_state.get("aqi_selected_date")

    if day is not None:

        ts = pd_timestamp_label(day)

        if ts:

            return f"Day · {ts}"

    regime = st.session_state.get("aqi_selected_regime")

    if regime:

        return f"Regime · {regime}"

    if season and category:

        return f"{season} · {category}"

    return season or category





def pd_timestamp_label(value: Any) -> str | None:

    try:

        import pandas as pd



        return pd.Timestamp(value).strftime("%d %b %Y")

    except Exception:

        return str(value) if value else None





# --- Chart highlight context ---





def get_traffic_context() -> dict:

    state = read_traffic_interaction()

    road = state["selected_road"]

    area = state["selected_area"] or (

        state.get("focus_entity") if state.get("focus_mode") == "radar_comparison" else None

    )

    return {

        "highlight_area": area,

        "highlight_road": road,

        "highlight_month": state.get("selected_month"),

        "highlight_quadrant": state.get("selected_quadrant"),

        "focus_mode": state.get("focus_mode"),

    }





def get_aqi_context() -> dict:

    state = read_aqi_interaction()

    return {

        "highlight_category": state["selected_category"],

        "highlight_season": state["selected_season"],

        "highlight_regime": state.get("selected_regime"),

        "highlight_pollutant": state.get("selected_pollutant"),

        "highlight_year": state.get("selected_year"),

        "highlight_week": state.get("selected_week"),

    }





def get_chart_context(dashboard: DashboardId) -> dict:

    if dashboard == "traffic":

        return get_traffic_context()

    return get_aqi_context()





# --- Selection mutators ---





def apply_interaction_payload(dashboard: DashboardId, payload: dict[str, Any]) -> TransitionResult:

    """Apply normalized chart payload to visual focus only."""

    _ensure_initialized()
    return dispatch(ChartFocusChanged(dashboard=dashboard, payload=payload))





def clear_investigation(dashboard: DashboardId) -> TransitionResult:

    """Clear chart-linked visual focus and investigation overlay; global filters remain unchanged."""

    return dispatch(FocusCleared(dashboard=dashboard))


def has_active_traffic_selection() -> bool:

    _ensure_initialized()

    return bool(

        st.session_state.get("traffic_selected_area")

        or st.session_state.get("traffic_selected_road")

        or st.session_state.get("traffic_radar_focus_area")

        or st.session_state.get("traffic_selected_month")

        or st.session_state.get("traffic_focus_mode")

    )





def has_active_aqi_selection() -> bool:

    _ensure_initialized()

    return bool(

        st.session_state.get("aqi_selected_season")

        or st.session_state.get("aqi_selected_category")

        or st.session_state.get("aqi_selected_date")

        or st.session_state.get("aqi_selected_regime")

        or st.session_state.get("aqi_focus_mode")

    )





def has_active_selection(dashboard: DashboardId) -> bool:

    if dashboard == "traffic":

        return has_active_traffic_selection()

    return has_active_aqi_selection()





# --- Selection hierarchy (visual emphasis) ---





def trace_opacity(label: str, highlight: str | None, base: float = 0.38) -> float:

    if not highlight:

        return base

    return 1.0 if label == highlight else 0.12





def emphasis_opacity(

    entity: str,

    selected: str | None,

    related: set[str] | None = None,

    *,

    base: float = 0.42,

    related_opacity: float = 0.58,

    dimmed: float = 0.12,

) -> float:

    if not selected:

        return base

    if entity == selected:

        return 1.0

    if related and entity in related:

        return related_opacity

    return dimmed





def related_area_for_road(road: str | None, roads_df: Any) -> set[str]:

    if not road or roads_df is None or getattr(roads_df, "empty", True):

        return set()

    from config.data_config import COL_AREA, COL_ROAD



    match = roads_df[roads_df[COL_ROAD] == road]

    if match.empty:

        return set()

    return {str(match.iloc[0][COL_AREA])}





# --- Page-linked interaction ---





def get_linked_domain(bundle: dict) -> LinkedDomain | None:

    mode = bundle.get(BUNDLE_KEY_LINKED_CONTROLS)

    if mode in ("traffic", "aqi"):

        return mode

    return None





def is_linked_page(bundle: dict) -> bool:

    return get_linked_domain(bundle) is not None





def investigation_breadcrumb(dashboard: DashboardId) -> str | None:

    state = read_interaction_state(dashboard)

    if not has_active_selection(dashboard):

        return None

    chart = state.get("selected_chart") or st.session_state.get(

        f"{'traffic' if dashboard == 'traffic' else 'aqi'}_focus_chart"

    )

    ctx = state.get("active_context")

    if chart and ctx:

        return f"{chart} · {ctx}"

    return ctx or chart





def resolve_selection_label(bundle: dict, dashboard: DashboardId) -> str | None:

    if not is_linked_page(bundle) and not has_active_selection(dashboard):

        return None

    if get_linked_domain(bundle) not in (None, dashboard) and not has_active_selection(dashboard):

        return None

    return investigation_breadcrumb(dashboard) or selection_label(dashboard)





def prepare_investigation_interaction(

    bundle: dict,

    dashboard: DashboardId,

) -> dict[str, Any]:

    linked_domain = get_linked_domain(bundle)

    return {

        "is_linked_page": linked_domain is not None,

        "linked_domain": linked_domain,

        "selection_label": resolve_selection_label(bundle, dashboard),

        "has_investigation": has_active_selection(dashboard),

        "breadcrumb": investigation_breadcrumb(dashboard),

    }





def render_investigation_chrome(bundle: dict, dashboard: DashboardId, page_key: str) -> dict[str, Any]:

    """Chart-focus strip: breadcrumb and clear action."""

    meta = prepare_investigation_interaction(bundle, dashboard)

    if meta["has_investigation"] or meta.get("breadcrumb"):

        bc = meta.get("breadcrumb") or "Chart focus active"

        c1, c2, c3 = st.columns([4.2, 1.2, 1.6])

        with c1:

            focus_label = "Selected chart context" if dashboard == "aqi" else "Chart-linked focus"
            st.caption(f"**{focus_label}** · {bc}")

        with c2:

            if st.button("× Clear focus", key=f"clear_focus_{dashboard}_{page_key}"):

                result = clear_investigation(dashboard)

                request_rerun(result, source=f"clear_focus_{dashboard}_{page_key}")

        with c3:

            if meta.get("has_investigation"):

                pass
            else:
                render_chart_interaction_mode_hint(st.session_state, dashboard)

    return meta





def render_investigation_interaction(bundle: dict, dashboard: DashboardId) -> str | None:

    """Legacy entry — returns chart selection badge text."""

    meta = prepare_investigation_interaction(bundle, dashboard)

    return meta["selection_label"]





def selection_label(dashboard: DashboardId) -> str | None:

    state = read_interaction_state(dashboard)

    return state.get("active_context")





def merge_chart_config(base: dict | None, dashboard: DashboardId) -> dict:

    from config.chart_defaults import chart_size_for

    cfg = dict(base or {})

    cfg["dashboard"] = dashboard

    cfg.update(get_chart_context(dashboard))

    chart_id = cfg.get("chart_id")

    if chart_id and "chart_size" not in cfg:

        cfg["chart_size"] = chart_size_for(chart_id, cfg.get("role", "hero"))

    return cfg





def process_plotly_selection(

    chart_id: str,

    plotly_state: Any,

    meta: dict | None,

    dashboard: DashboardId,

) -> None:

    """Bridge from chart_container to handler dispatch."""

    from services.state.chart_handlers import _first_point, dispatch_chart_selection



    point = _first_point(getattr(plotly_state, "selection", None))

    if not point:

        return

    sig = (

        chart_id,

        point.get("point_index"),

        point.get("curve_number"),

        point.get("x"),

        point.get("y"),

        point.get("label"),

    )

    if st.session_state.get("_chart_sel_sig") == sig:

        return

    if dispatch_chart_selection(chart_id, plotly_state, meta):

        st.session_state["_chart_sel_sig"] = sig

        request_rerun_for_last_transition(source=f"plotly_selection_{chart_id}")
