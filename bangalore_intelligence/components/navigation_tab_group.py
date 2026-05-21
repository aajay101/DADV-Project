"""Dashboard tab navigation — horizontal command strip."""

import streamlit as st

from config.page_config import AQI_TABS, TRAFFIC_TABS
from config.theme import SPACING_MD, SPACING_SM, get_dashboard_tokens
from filters.state import get_active_tab, set_active_tab
from utils.ui_blocks import render_html_block


def render_tab_navigation(dashboard: str) -> None:
    tabs = TRAFFIC_TABS if dashboard == "traffic" else AQI_TABS
    tokens = get_dashboard_tokens(dashboard)
    active_index = get_active_tab(dashboard)

    render_html_block(
        f"""
        <div class="buip-tab-row" style="
            border-bottom:1px solid {tokens['border']};
            margin-bottom:{SPACING_MD}px;
            padding-bottom:{SPACING_SM}px;
        "></div>
        """
    )

    tab_labels = [t["label"] for t in tabs]
    selected = st.radio(
        "Page navigation",
        options=tab_labels,
        index=active_index,
        horizontal=True,
        key=f"{dashboard}_tab_nav",
        label_visibility="collapsed",
    )
    new_index = tab_labels.index(selected)
    if new_index != active_index:
        set_active_tab(dashboard, new_index)
        st.rerun()
