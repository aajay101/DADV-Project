"""Dashboard tab navigation — horizontal command strip."""

import streamlit as st

from config.page_config import AQI_TABS, TRAFFIC_TABS
from config.theme import SPACING_MD, SPACING_SM, get_dashboard_tokens
from filters.state import (
    apply_programmatic_nav_sync,
    get_active_tab,
    get_tab_nav_widget_key,
    log_nav_debug,
    set_active_tab,
)
from filters.transitions import request_rerun
from utils.html_styles import join_styles
from utils.ui_blocks import render_html_block


def render_tab_navigation(dashboard: str) -> None:
    tabs = TRAFFIC_TABS if dashboard == "traffic" else AQI_TABS
    tokens = get_dashboard_tokens(dashboard)
    tab_labels = [t["label"] for t in tabs]
    nav_key = get_tab_nav_widget_key(dashboard)
    active_index = get_active_tab(dashboard)

    # Breadcrumb / nav-card / lab: update radio label before widget mounts.
    apply_programmatic_nav_sync(dashboard)

    if nav_key not in st.session_state:
        st.session_state[nav_key] = tab_labels[active_index]

    tab_row_style = join_styles(
        f"border-bottom:1px solid {tokens['border']}",
        f"margin-bottom:{SPACING_MD}px",
        f"padding-bottom:{SPACING_SM}px",
    )
    render_html_block(f'<div class="buip-tab-row" style="{tab_row_style}"></div>')

    selected = st.radio(
        "Page navigation",
        options=tab_labels,
        horizontal=True,
        key=nav_key,
        label_visibility="collapsed",
    )

    try:
        new_index = tab_labels.index(selected)
    except ValueError:
        new_index = active_index

    log_nav_debug(
        dashboard,
        "tab_radio",
        selected=selected,
        new_index=new_index,
        active_index=active_index,
    )

    if new_index != active_index:
        # Widget already holds `selected`; only persist canonical index — do not touch nav_key.
        result = set_active_tab(dashboard, new_index, from_widget=True)
        log_nav_debug(dashboard, "tab_change_rerun", new_index=new_index)
        request_rerun(result, source=f"{dashboard}_tab_navigation")
