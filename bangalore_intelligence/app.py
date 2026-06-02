"""Bangalore Urban Intelligence Platform — Phase 2.5 + 3."""

import streamlit as st

from config.page_config import DASHBOARD_OPTIONS
from config.theme import SPACING_MD, SPACING_SM, SPACING_XS, get_dashboard_tokens
from dashboards.aqi import aqi_router
from dashboards.traffic import traffic_router
from data_layer.governance import RuntimeDataIntegrityError, run_startup_governance_checks
from components.layout.viewport import sync_viewport_width
from components.session_notice import render_long_session_notice
from filters.state import init_app_state
from utils.css_injector import inject_dashboard_accent, inject_platform_css
from utils.html_styles import join_styles
from utils.ui_blocks import escape_text, render_html_block

st.set_page_config(
    page_title="Bangalore Urban Intelligence Platform",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

try:
    run_startup_governance_checks()
except RuntimeDataIntegrityError as exc:
    st.error(f"Runtime data governance check failed: {exc}")
    st.stop()
init_app_state()
sync_viewport_width()
active = st.session_state.get("active_dashboard", "traffic")
inject_platform_css(active)
inject_dashboard_accent(active)
tokens = get_dashboard_tokens(active)

_header_style = join_styles(
    "display:flex",
    "justify-content:space-between",
    "align-items:center",
    f"margin-bottom:{SPACING_MD}px",
    f"padding-bottom:{SPACING_SM}px",
    f"border-bottom:1px solid {tokens['border']}",
)
_identity_muted = join_styles(
    "font-size:10px",
    "font-weight:600",
    "letter-spacing:0.1em",
    f"color:{tokens['text_muted']}",
    "text-transform:uppercase",
)
_title_style = join_styles(
    "font-size:17px",
    "font-weight:700",
    f"color:{tokens['text_primary']}",
    f"margin-top:{SPACING_XS}px",
)
_right_style = join_styles(
    "font-size:12px",
    f"color:{tokens['text_muted']}",
    "text-align:right",
)
render_html_block(
    f'<div style="{_header_style}"><div>'
    f'<div style="{_identity_muted}">Bangalore Urban Intelligence Platform</div>'
    f'<div style="{_title_style}">SUAQIS · Operational Intelligence</div></div>'
    f'<div style="{_right_style}"><span style="color:{tokens["accent"]};">'
    f'{escape_text(tokens["identity_label"])}</span></div></div>'
)
render_long_session_notice(dashboard=active)

dashboard_labels = list(DASHBOARD_OPTIONS.values())
dashboard_keys = list(DASHBOARD_OPTIONS.keys())
current_key = st.session_state.get("active_dashboard", "traffic")
current_index = dashboard_keys.index(current_key) if current_key in dashboard_keys else 0

selected_label = st.radio(
    "Select dashboard",
    options=dashboard_labels,
    index=current_index,
    horizontal=True,
    key="dashboard_switcher_widget",
    label_visibility="collapsed",
)

selected_key = dashboard_keys[dashboard_labels.index(selected_label)]
if selected_key != st.session_state.get("active_dashboard"):
    from filters.transitions import DashboardChanged, dispatch, request_rerun

    result = dispatch(DashboardChanged(dashboard=selected_key))
    request_rerun(result, source="dashboard_switcher")

if st.session_state["active_dashboard"] == "traffic":
    traffic_router()
else:
    aqi_router()
