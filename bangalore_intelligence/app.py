"""Bangalore Urban Intelligence Platform — Phase 2.5 + 3."""

import streamlit as st

from config.page_config import DASHBOARD_OPTIONS
from config.theme import SPACING_MD, SPACING_SM, SPACING_XS, get_dashboard_tokens
from dashboards.aqi import aqi_router
from dashboards.traffic import traffic_router
from data_layer.bootstrap_data import ensure_raw_datasets
from filters.state import init_app_state
from utils.css_injector import inject_dashboard_accent, inject_platform_css
from utils.ui_blocks import render_html_block

st.set_page_config(
    page_title="Bangalore Urban Intelligence Platform",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ensure_raw_datasets()
init_app_state()
active = st.session_state.get("active_dashboard", "traffic")
inject_platform_css(active)
inject_dashboard_accent(active)
tokens = get_dashboard_tokens(active)

header_html = f"""
<div style="
    display:flex;justify-content:space-between;align-items:center;
    margin-bottom:{SPACING_MD}px;padding-bottom:{SPACING_SM}px;
    border-bottom:1px solid {tokens['border']};
">
    <div>
        <div style="
            font-size:10px;font-weight:600;letter-spacing:0.1em;
            color:{tokens['text_muted']};text-transform:uppercase;
        ">Bangalore Urban Intelligence Platform</div>
        <div style="
            font-size:17px;font-weight:700;color:{tokens['text_primary']};
            margin-top:{SPACING_XS}px;
        ">SUAQIS · Operational Intelligence</div>
    </div>
    <div style="font-size:12px;color:{tokens['text_muted']};text-align:right;">
        <span style="color:{tokens['accent']};">{tokens['identity_label']}</span>
    </div>
</div>
"""
render_html_block(header_html)

dashboard_labels = list(DASHBOARD_OPTIONS.values())
dashboard_keys = list(DASHBOARD_OPTIONS.keys())
current_key = st.session_state.get("active_dashboard", "traffic")
current_index = dashboard_keys.index(current_key) if current_key in dashboard_keys else 0

selected_label = st.radio(
    "Dashboard Command",
    options=dashboard_labels,
    index=current_index,
    horizontal=True,
    key="dashboard_switcher_widget",
    label_visibility="collapsed",
)

selected_key = dashboard_keys[dashboard_labels.index(selected_label)]
if selected_key != st.session_state.get("active_dashboard"):
    st.session_state["active_dashboard"] = selected_key
    st.session_state["_buip_css_injected"] = False
    inject_platform_css(selected_key)
    inject_dashboard_accent(selected_key)
    st.rerun()

if st.session_state["active_dashboard"] == "traffic":
    traffic_router()
else:
    aqi_router()
