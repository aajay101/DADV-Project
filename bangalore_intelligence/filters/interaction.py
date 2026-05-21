"""Centralized linked-selection and interaction state governance.



Interaction ownership lives here — pages orchestrate, components present,

charts render. Session keys are namespaced and initialized via filters.state.

Temporary investigation focus is separate from persistent filter state.

"""



from __future__ import annotations



from typing import Any, Literal



import streamlit as st



from config.data_config import AQI_CATEGORIES, TRAFFIC_AREAS

from filters.state import AQI_STATE_DEFAULTS, TRAFFIC_STATE_DEFAULTS



DashboardId = Literal["traffic", "aqi"]

LinkedDomain = Literal["traffic", "aqi"]



BUNDLE_KEY_LINKED_CONTROLS = "linked_controls"

INTERACTION_SESSION_KEY = "interaction"

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



_TRAFFIC_VIEW_DEFAULTS: dict[str, Any] = {

    "selected_chart": None,

    "selected_road": None,

    "selected_area": None,

    "selected_month": None,

    "selected_quadrant": None,

    "focus_mode": None,

    "focus_entity": None,

}



_AQI_VIEW_DEFAULTS: dict[str, Any] = {

    "selected_chart": None,

    "selected_day": None,

    "selected_year": None,

    "selected_week": None,

    "selected_pollutant": None,

    "selected_category": None,

    "selected_season": None,

    "selected_regime": None,

    "focus_mode": None,

    "context_pm25": None,

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

    if INTERACTION_SESSION_KEY not in st.session_state:

        st.session_state[INTERACTION_SESSION_KEY] = {

            "traffic": dict(_TRAFFIC_VIEW_DEFAULTS),

            "aqi": dict(_AQI_VIEW_DEFAULTS),

        }

    if CHART_EPOCH_KEY not in st.session_state:

        st.session_state[CHART_EPOCH_KEY] = 0





def _ensure_initialized() -> None:

    init_interaction_state()





def _sync_interaction_view(dashboard: DashboardId) -> None:

    _ensure_initialized()

    blob = st.session_state[INTERACTION_SESSION_KEY]

    if dashboard == "traffic":

        blob["traffic"] = {

            "selected_chart": st.session_state.get("traffic_focus_chart"),

            "selected_road": st.session_state.get("traffic_selected_road"),

            "selected_area": st.session_state.get("traffic_selected_area"),

            "selected_month": st.session_state.get("traffic_selected_month"),

            "selected_quadrant": st.session_state.get("traffic_selected_quadrant"),

            "focus_mode": st.session_state.get("traffic_focus_mode"),

            "focus_entity": st.session_state.get("traffic_radar_focus_area"),

        }

    else:

        blob["aqi"] = {

            "selected_chart": st.session_state.get("aqi_focus_chart"),

            "selected_day": st.session_state.get("aqi_selected_date"),

            "selected_year": st.session_state.get("aqi_selected_year"),

            "selected_week": st.session_state.get("aqi_selected_week"),

            "selected_pollutant": st.session_state.get("aqi_selected_pollutant"),

            "selected_category": st.session_state.get("aqi_selected_category"),

            "selected_season": st.session_state.get("aqi_selected_season"),

            "selected_regime": st.session_state.get("aqi_selected_regime"),

            "focus_mode": st.session_state.get("aqi_focus_mode"),

            "context_pm25": st.session_state.get("aqi_context_pm25"),

        }





def bump_chart_epoch() -> int:

    _ensure_initialized()

    st.session_state[CHART_EPOCH_KEY] = int(st.session_state.get(CHART_EPOCH_KEY, 0)) + 1

    return st.session_state[CHART_EPOCH_KEY]





def chart_widget_key(page_key: str, chart_id: str, dashboard: str) -> str:

    epoch = st.session_state.get(CHART_EPOCH_KEY, 0)

    return f"buip_{dashboard}_{page_key}_{chart_id}_{epoch}"





# --- Normalized interaction snapshots ---





def read_traffic_interaction() -> dict[str, Any]:

    _ensure_initialized()

    _sync_interaction_view("traffic")

    area = st.session_state.get("traffic_selected_area")

    road = st.session_state.get("traffic_selected_road")

    return {

        **st.session_state[INTERACTION_SESSION_KEY]["traffic"],

        "selected_area": area,

        "selected_road": road,

        "selected_month": st.session_state.get("traffic_selected_month"),

        "focus_entity": st.session_state.get("traffic_radar_focus_area"),

        "linked_enabled": bool(area or road),

        "active_context": _traffic_context_label(road, area),

    }





def read_aqi_interaction() -> dict[str, Any]:

    _ensure_initialized()

    _sync_interaction_view("aqi")

    season = st.session_state.get("aqi_selected_season")

    category = st.session_state.get("aqi_selected_category")

    return {

        **st.session_state[INTERACTION_SESSION_KEY]["aqi"],

        "selected_category": category,

        "selected_season": season,

        "selected_date": st.session_state.get("aqi_selected_date"),

        "selected_month": st.session_state.get("aqi_selected_month"),

        "selected_regime": st.session_state.get("aqi_selected_regime"),

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

    if road:

        quad = quadrant_label(st.session_state.get("traffic_selected_quadrant"))

        return f"{road} · {quad}" if quad != "—" else road

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





def apply_interaction_payload(dashboard: DashboardId, payload: dict[str, Any]) -> None:

    """Apply normalized investigation payload from chart handlers."""

    _ensure_initialized()

    chart = payload.get("chart")

    if dashboard == "traffic":

        st.session_state["traffic_focus_chart"] = chart

        st.session_state["traffic_focus_mode"] = payload.get("focus_mode")

        if "selected_road" in payload:

            st.session_state["traffic_selected_road"] = payload.get("selected_road")

            if payload.get("selected_road"):

                st.session_state["traffic_selected_area"] = payload.get("selected_area")

        elif "selected_area" in payload:

            st.session_state["traffic_selected_area"] = payload.get("selected_area")

            if payload.get("selected_area"):

                st.session_state["traffic_selected_road"] = None

        if "selected_quadrant" in payload:

            st.session_state["traffic_selected_quadrant"] = payload.get("selected_quadrant")

        if payload.get("focus_entity"):

            st.session_state["traffic_radar_focus_area"] = payload["focus_entity"]

        elif payload.get("selected_area") and payload.get("focus_mode") == "radar_comparison":

            st.session_state["traffic_radar_focus_area"] = payload["selected_area"]

    else:

        st.session_state["aqi_focus_chart"] = chart

        st.session_state["aqi_focus_mode"] = payload.get("focus_mode")

        for key in (

            "selected_date",

            "selected_category",

            "selected_season",

            "selected_regime",

            "selected_pollutant",

        ):

            sk = f"aqi_{key}"

            if key in payload:

                st.session_state[sk] = payload.get(key)

        if "selected_year" in payload:

            st.session_state["aqi_selected_year"] = payload.get("selected_year")

        if "selected_week" in payload:

            st.session_state["aqi_selected_week"] = payload.get("selected_week")

        if "context_pm25" in payload:

            st.session_state["aqi_context_pm25"] = payload.get("context_pm25")

    _sync_interaction_view(dashboard)





def set_traffic_area(area: str | None) -> None:

    _ensure_initialized()

    st.session_state["traffic_selected_area"] = area

    if area:

        st.session_state["traffic_selected_road"] = None

    _sync_interaction_view("traffic")





def set_traffic_road(road: str | None) -> None:

    _ensure_initialized()

    st.session_state["traffic_selected_road"] = road

    if road:

        st.session_state["traffic_selected_area"] = None

    _sync_interaction_view("traffic")





def set_aqi_season(season: str | None) -> None:

    _ensure_initialized()

    st.session_state["aqi_selected_season"] = season

    _sync_interaction_view("aqi")





def set_aqi_category(category: str | None) -> None:

    _ensure_initialized()

    st.session_state["aqi_selected_category"] = category

    _sync_interaction_view("aqi")





def clear_traffic_selection() -> None:

    _ensure_initialized()

    st.session_state["traffic_selected_area"] = None

    st.session_state["traffic_selected_road"] = None

    st.session_state["traffic_selected_month"] = None

    st.session_state["traffic_radar_focus_area"] = None

    st.session_state["traffic_selected_quadrant"] = None

    st.session_state["traffic_focus_chart"] = None

    st.session_state["traffic_focus_mode"] = None

    _sync_interaction_view("traffic")





def clear_aqi_selection() -> None:

    _ensure_initialized()

    st.session_state["aqi_selected_category"] = None

    st.session_state["aqi_selected_season"] = None

    st.session_state["aqi_selected_date"] = None

    st.session_state["aqi_selected_month"] = None

    st.session_state["aqi_selected_regime"] = None

    st.session_state["aqi_selected_year"] = None

    st.session_state["aqi_selected_week"] = None

    st.session_state["aqi_selected_pollutant"] = None

    st.session_state["aqi_focus_chart"] = None

    st.session_state["aqi_focus_mode"] = None

    st.session_state["aqi_context_pm25"] = None

    _sync_interaction_view("aqi")





def clear_selection(dashboard: DashboardId) -> None:

    if dashboard == "traffic":

        clear_traffic_selection()

    else:

        clear_aqi_selection()





def clear_investigation(dashboard: DashboardId) -> None:

    """Reset investigation focus only — filters and navigation unchanged."""

    clear_selection(dashboard)

    st.session_state.pop("_chart_sel_sig", None)

    bump_chart_epoch()





def has_active_traffic_selection() -> bool:

    _ensure_initialized()

    return bool(

        st.session_state.get("traffic_selected_area")

        or st.session_state.get("traffic_selected_road")

        or st.session_state.get("traffic_radar_focus_area")

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

    """Investigation strip: linked selectors, breadcrumb, clear actions."""

    meta = prepare_investigation_interaction(bundle, dashboard)

    if meta["is_linked_page"]:

        render_page_linked_controls(bundle)



    if meta["has_investigation"] or meta.get("breadcrumb"):

        bc = meta.get("breadcrumb") or "Investigation active"

        c1, c2, c3 = st.columns([5, 1.2, 1.2])

        with c1:

            st.caption(f"**Filtered by investigation** · {bc}")

        with c2:

            if st.button("× Clear Focus", key=f"clear_focus_{dashboard}_{page_key}"):

                clear_investigation(dashboard)

                st.rerun()

        with c3:

            if st.button("Reset Investigation", key=f"reset_inv_{dashboard}_{page_key}"):

                clear_investigation(dashboard)

                st.rerun()

    return meta





def render_investigation_interaction(bundle: dict, dashboard: DashboardId) -> str | None:

    """Legacy entry — returns chart selection badge text."""

    meta = prepare_investigation_interaction(bundle, dashboard)

    if meta["is_linked_page"]:

        render_page_linked_controls(bundle)

    return meta["selection_label"]





def selection_label(dashboard: DashboardId) -> str | None:

    state = read_interaction_state(dashboard)

    return state.get("active_context")





def render_traffic_linked_selector() -> None:

    _ensure_initialized()

    areas = ["— All areas —", *TRAFFIC_AREAS]

    current = st.session_state.get("traffic_selected_area")

    idx = areas.index(current) if current in areas else 0

    choice = st.selectbox(

        "Linked focus · area",

        options=areas,

        index=idx,

        key="traffic_linked_area_selector",

    )

    new_val = None if choice == "— All areas —" else choice

    if new_val != current:

        set_traffic_area(new_val)

        st.rerun()





def render_aqi_linked_selector() -> None:

    _ensure_initialized()

    seasons = ["— All seasons —", "Winter", "Spring", "Monsoon", "Post-Monsoon"]

    current = st.session_state.get("aqi_selected_season")

    idx = seasons.index(current) if current in seasons else 0

    choice = st.selectbox(

        "Linked focus · season",

        options=seasons,

        index=idx,

        key="aqi_linked_season_selector",

    )

    new_val = None if choice == "— All seasons —" else choice

    if new_val != current:

        set_aqi_season(new_val)

        st.rerun()



    categories = ["— All categories —", *AQI_CATEGORIES]

    cat_current = st.session_state.get("aqi_selected_category")

    cat_idx = categories.index(cat_current) if cat_current in categories else 0

    cat_choice = st.selectbox(

        "Linked focus · AQI category",

        options=categories,

        index=cat_idx,

        key="aqi_linked_category_selector",

    )

    new_cat = None if cat_choice == "— All categories —" else cat_choice

    if new_cat != cat_current:

        set_aqi_category(new_cat)

        st.rerun()





def render_page_linked_controls(bundle: dict) -> None:

    domain = get_linked_domain(bundle)

    if domain == "traffic":

        render_traffic_linked_selector()

    elif domain == "aqi":

        render_aqi_linked_selector()





def merge_chart_config(base: dict | None, dashboard: DashboardId) -> dict:

    cfg = dict(base or {})

    cfg["dashboard"] = dashboard

    cfg.update(get_chart_context(dashboard))

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

        st.rerun()


