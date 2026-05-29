"""Global operational filter command strip."""

import streamlit as st

from config.data_config import (
    AQI_CATEGORIES,
    TRAFFIC_AREAS,
    TRAFFIC_ROADS,
    TRAFFIC_ROADWORK_FILTER_OPTIONS,
    TRAFFIC_WEATHER_OPTIONS,
)
from config.typography import TYPE_CAPTION, TYPE_SUBSECTION_TITLE, css_from_type
from config.theme import RADIUS_LG, SPACING_MD, SPACING_SM, SPACING_XS, get_dashboard_tokens
from components.layout.responsive import should_show_compact_filter_warning
from components.interaction_education.filter_scope_explanations import render_filter_scope_hint
from components.runtime_debug import render_transition_debug_panel
from components.session_notice import render_data_freshness_strip
from filters.scope_sync import (
    on_aqi_categories_change,
    on_aqi_seasons_change,
    on_traffic_areas_change,
    on_traffic_roadwork_change,
    on_traffic_roads_change,
    on_traffic_weather_change,
)
from filters.state import (
    AQI_STATE_DEFAULTS,
    TRAFFIC_STATE_DEFAULTS,
    apply_pending_filter_reset,
    is_filter_updating,
    request_global_filter_clear,
    request_filter_reset,
)
from filters.interaction_mode import get_interaction_mode, has_active_global_filters
from filters.transitions import GlobalFilterChanged, dispatch, record_deferred_rerun
from utils.formatters import filter_snapshot_from_state, fmt_filter_summary
from utils.html_styles import join_styles, pill_badge, styled_div
from utils.ui_blocks import render_html_block


def _filters_active(prefix: str, defaults: dict) -> bool:
    dashboard = "traffic" if prefix == "traffic" else "aqi"
    return has_active_global_filters(st.session_state, dashboard)


def _zone_label(style: str, text: str) -> None:
    label_style = join_styles(style, f"margin-bottom:{SPACING_XS}px;")
    render_html_block(styled_div(text, label_style))


def _on_filter_widget_change(prefix: str) -> None:
    dashboard = "traffic" if prefix == "traffic" else "aqi"
    defaults = TRAFFIC_STATE_DEFAULTS if dashboard == "traffic" else AQI_STATE_DEFAULTS
    updates = {
        f"{prefix}_date_start": st.session_state.get(f"{prefix}_date_start"),
        f"{prefix}_date_end": st.session_state.get(f"{prefix}_date_end"),
    }
    dispatch(GlobalFilterChanged(dashboard=dashboard, updates=updates, filters_active=_filters_active(prefix, defaults)))


def filter_panel(dashboard: str = "traffic") -> None:
    apply_pending_filter_reset(dashboard)
    tokens = get_dashboard_tokens(dashboard)
    prefix = "traffic" if dashboard == "traffic" else "aqi"
    defaults = TRAFFIC_STATE_DEFAULTS if dashboard == "traffic" else AQI_STATE_DEFAULTS
    filters_active = _filters_active(prefix, defaults)
    filter_updating = is_filter_updating(prefix)
    interaction_mode = get_interaction_mode(st.session_state, "traffic" if dashboard == "traffic" else "aqi")
    strip_classes = "filter-strip buip-filter-strip"
    if filter_updating:
        strip_classes += " buip-filter-strip--updating"

    active_badge = pill_badge(
        "FILTERS ACTIVE",
        f"{tokens['severity_warning']}33",
        tokens["severity_warning"],
        tokens["severity_warning"],
    ) if filters_active else ""

    strip_title_style = css_from_type(TYPE_SUBSECTION_TITLE, tokens["text_muted"])
    strip_style = join_styles(
        "position:sticky",
        "top:0",
        "z-index:100",
        f"background:{tokens['filter_shelf']}",
        f"border-bottom:1px solid {tokens['border']}",
        f"padding:{SPACING_MD}px {SPACING_MD}px {SPACING_SM}px",
        f"margin-bottom:{SPACING_MD}px",
        f"border-radius:{RADIUS_LG}px {RADIUS_LG}px 0 0",
    )
    strip_row = join_styles(
        "display:flex",
        "justify-content:space-between",
        "align-items:center",
    )
    strip_html = (
        f'<div class="{strip_classes}" style="{strip_style}">'
        f'<div style="{strip_row}">'
        f'<span style="{strip_title_style}">Global filters</span>'
        f"<span>{active_badge}</span></div></div>"
    )
    render_html_block(strip_html)

    if should_show_compact_filter_warning():
        st.warning(
            "Compact viewport: analytical layout is degraded. Use landscape or a wider window "
            "for full chart density. Analytical Workspace is unavailable below 768px.",
            icon="📐",
        )

    if interaction_mode == "investigation_mode":
        st.warning(
            "Investigative drilldown active. Clear Focus to restore baseline and re-enable global filters.",
        )
    render_filter_scope_hint(st.session_state, "traffic" if dashboard == "traffic" else "aqi")

    controls_disabled = interaction_mode == "investigation_mode"
    if filter_updating:
        render_html_block(
            '<div class="buip-filter-controls buip-filter-controls--updating" aria-busy="true"></div>'
        )

    zone_date, zone_scope, zone_actions = st.columns([2, 2, 1])
    caption_style = css_from_type(TYPE_CAPTION, tokens["text_muted"])

    with zone_date:
        with st.container(border=True):
            _zone_label(caption_style, "Date Filters")
            c1, c2 = st.columns(2)
            with c1:
                st.date_input(
                    "Start",
                    key=f"{prefix}_date_start",
                    format="DD/MM/YYYY",
                    on_change=_on_filter_widget_change,
                    args=(prefix,),
                    disabled=controls_disabled,
                )
            with c2:
                st.date_input(
                    "End",
                    key=f"{prefix}_date_end",
                    format="DD/MM/YYYY",
                    on_change=_on_filter_widget_change,
                    args=(prefix,),
                    disabled=controls_disabled,
                )

    with zone_scope:
        with st.container(border=True):
            _zone_label(caption_style, "Data Filters")
            if dashboard == "traffic":
                st.multiselect(
                    "Areas",
                    options=TRAFFIC_AREAS,
                    key="traffic_selected_areas",
                    placeholder="All areas",
                    on_change=on_traffic_areas_change,
                    args=(prefix,),
                    disabled=controls_disabled,
                )
                w_col, rw_col, rd_col = st.columns(3)
                with w_col:
                    st.multiselect(
                        "Weather",
                        options=TRAFFIC_WEATHER_OPTIONS,
                        key="traffic_selected_weather",
                        placeholder="All weather",
                        on_change=on_traffic_weather_change,
                        args=(prefix,),
                        disabled=controls_disabled,
                    )
                with rw_col:
                    st.selectbox(
                        "Roadwork",
                        options=TRAFFIC_ROADWORK_FILTER_OPTIONS,
                        key="traffic_selected_roadwork",
                        on_change=on_traffic_roadwork_change,
                        args=(prefix,),
                        disabled=controls_disabled,
                    )
                with rd_col:
                    st.multiselect(
                        "Roads",
                        options=TRAFFIC_ROADS,
                        key="traffic_selected_roads",
                        placeholder="All roads",
                        on_change=on_traffic_roads_change,
                        args=(prefix,),
                        disabled=controls_disabled,
                    )
            else:
                st.multiselect(
                    "PM2.5 categories",
                    options=AQI_CATEGORIES,
                    key="aqi_selected_categories",
                    placeholder="All categories",
                    on_change=on_aqi_categories_change,
                    args=(prefix,),
                    disabled=controls_disabled,
                )
                st.multiselect(
                    "Seasons",
                    options=["Winter", "Spring", "Monsoon", "Post-Monsoon"],
                    key="aqi_selected_seasons",
                    placeholder="All seasons",
                    on_change=on_aqi_seasons_change,
                    args=(prefix,),
                    disabled=controls_disabled,
                )

    with zone_actions:
        _zone_label(caption_style, "ACTIONS")
        render_data_freshness_strip(dashboard)
        render_transition_debug_panel()
        if filters_active and st.button(
            "Clear Global Filters",
            key=f"{prefix}_clear_global_filters",
            use_container_width=True,
        ):
            request_global_filter_clear(dashboard)
            record_deferred_rerun(
                dashboard="traffic" if dashboard == "traffic" else "aqi",
                source=f"{prefix}_clear_global_filters",
                reason="pending_global_filter_clear_before_widget_mount",
            )
            st.rerun()
        if st.button(
            "Reset All",
            key=f"{prefix}_reset_all",
            use_container_width=True,
        ):
            request_filter_reset(dashboard)
            record_deferred_rerun(
                dashboard="traffic" if dashboard == "traffic" else "aqi",
                source=f"{prefix}_reset_all",
                reason="pending_global_filter_reset_before_widget_mount",
            )
            st.rerun()

    if filters_active:
        summary = fmt_filter_summary(filter_snapshot_from_state(st.session_state, dashboard), dashboard)
        summary_style = join_styles(caption_style, f"margin-top:{SPACING_XS}px;")
        render_html_block(styled_div(summary, summary_style))
        bar_style = join_styles(
            "height:2px",
            f"background:{tokens['severity_warning']}99",
            f"margin:{SPACING_SM}px 0 {SPACING_MD}px 0",
            "border-radius:2px",
        )
        render_html_block(f'<div style="{bar_style}"></div>')
