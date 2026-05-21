"""Global operational filter command strip."""

import streamlit as st

from config.data_config import AQI_CATEGORIES, TRAFFIC_AREAS
from config.typography import TYPE_CAPTION, TYPE_SUBSECTION_TITLE, css_from_type
from config.theme import RADIUS_LG, SPACING_MD, SPACING_SM, SPACING_XS, get_dashboard_tokens
from filters.aqi_filters import reset_aqi_filters
from filters.state import AQI_STATE_DEFAULTS, TRAFFIC_STATE_DEFAULTS
from filters.traffic_filters import reset_traffic_filters
from utils.html_styles import join_styles, pill_badge, styled_div
from utils.ui_blocks import render_html_block


def _sync_filters_active(prefix: str, defaults: dict) -> None:
    if prefix == "traffic":
        date_changed = (
            st.session_state.get("traffic_date_start") != defaults["traffic_date_start"]
            or st.session_state.get("traffic_date_end") != defaults["traffic_date_end"]
        )
        area_changed = bool(st.session_state.get("traffic_selected_areas"))
        st.session_state["traffic_filters_active"] = date_changed or area_changed
    else:
        date_changed = (
            st.session_state.get("aqi_date_start") != defaults["aqi_date_start"]
            or st.session_state.get("aqi_date_end") != defaults["aqi_date_end"]
        )
        cat_changed = bool(st.session_state.get("aqi_selected_categories"))
        season_changed = bool(st.session_state.get("aqi_selected_seasons"))
        st.session_state["aqi_filters_active"] = date_changed or cat_changed or season_changed


def _zone_label(style: str, text: str) -> None:
    label_style = join_styles(style, f"margin-bottom:{SPACING_XS}px;")
    render_html_block(styled_div(text, label_style))


def filter_panel(dashboard: str = "traffic") -> None:
    tokens = get_dashboard_tokens(dashboard)
    prefix = "traffic" if dashboard == "traffic" else "aqi"
    defaults = TRAFFIC_STATE_DEFAULTS if dashboard == "traffic" else AQI_STATE_DEFAULTS
    filters_active = st.session_state.get(f"{prefix}_filters_active", False)

    active_badge = pill_badge(
        "FILTERS ACTIVE",
        f"{tokens['severity_warning']}33",
        tokens["severity_warning"],
        tokens["severity_warning"],
    ) if filters_active else ""

    strip_title_style = css_from_type(TYPE_SUBSECTION_TITLE, tokens["text_muted"])
    strip_html = f"""
    <div class="filter-strip buip-filter-strip" style="
        position:sticky;top:0;z-index:100;
        background:{tokens['filter_shelf']};
        border-bottom:1px solid {tokens['border']};
        padding:{SPACING_MD}px {SPACING_MD}px {SPACING_SM}px;
        margin-bottom:{SPACING_MD}px;
        border-radius:{RADIUS_LG}px {RADIUS_LG}px 0 0;
    ">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="{strip_title_style}">OPERATIONAL FILTER COMMAND</span>
            <span>{active_badge}</span>
        </div>
    </div>
    """
    render_html_block(strip_html)

    zone_date, zone_scope, zone_actions = st.columns([2, 2, 1])
    caption_style = css_from_type(TYPE_CAPTION, tokens["text_muted"])

    with zone_date:
        _zone_label(caption_style, "TEMPORAL SCOPE")
        c1, c2 = st.columns(2)
        with c1:
            st.date_input(
                "Start",
                value=st.session_state[f"{prefix}_date_start"],
                key=f"{prefix}_date_start",
                format="DD/MM/YYYY",
            )
        with c2:
            st.date_input(
                "End",
                value=st.session_state[f"{prefix}_date_end"],
                key=f"{prefix}_date_end",
                format="DD/MM/YYYY",
            )

    with zone_scope:
        label = "SPATIAL SCOPE" if dashboard == "traffic" else "ATMOSPHERIC SCOPE"
        _zone_label(caption_style, label)
        if dashboard == "traffic":
            st.multiselect(
                "Areas",
                options=TRAFFIC_AREAS,
                default=st.session_state.get("traffic_selected_areas", []),
                key="traffic_selected_areas",
                placeholder="All areas",
            )
        else:
            st.multiselect(
                "AQI categories",
                options=AQI_CATEGORIES,
                default=st.session_state.get("aqi_selected_categories", []),
                key="aqi_selected_categories",
                placeholder="All categories",
            )
            st.multiselect(
                "Seasons",
                options=["Winter", "Spring", "Monsoon", "Post-Monsoon"],
                default=st.session_state.get("aqi_selected_seasons", []),
                key="aqi_selected_seasons",
                placeholder="All seasons",
            )

    with zone_actions:
        _zone_label(caption_style, "ACTIONS")
        if st.button("Reset All", key=f"{prefix}_reset_all", use_container_width=True):
            if dashboard == "traffic":
                reset_traffic_filters()
            else:
                reset_aqi_filters()
            st.rerun()

    _sync_filters_active(prefix, defaults)

    if filters_active:
        active_bar_html = f"""
        <div style="
            height:2px;
            background:{tokens['severity_warning']}99;
            margin:{SPACING_SM}px 0 {SPACING_MD}px 0;
            border-radius:2px;
        "></div>
        """
        render_html_block(active_bar_html)
