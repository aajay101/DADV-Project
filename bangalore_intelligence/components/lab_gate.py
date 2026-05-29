"""Analytical Workspace gate — higher-density analytical environment."""

from collections.abc import Callable

import streamlit as st

from config.typography import TYPE_BODY, TYPE_HERO_TITLE, css_from_type
from config.theme import RADIUS_XL, SPACING_LG, SPACING_MD, SPACING_XS, get_dashboard_tokens
from filters.state import is_lab_gate_passed, pass_lab_gate, set_active_tab
from filters.transitions import request_rerun
from utils.html_styles import join_styles
from utils.ui_blocks import render_html_block


def lab_gate(dashboard: str, page_content_fn: Callable[[], None]) -> None:
    if st.session_state.get("advanced_lab_disabled_compact"):
        st.warning(
            "Analytical Workspace requires a viewport width of at least 768px. "
            "Widen the browser window or use a larger display to enter workspace mode.",
            icon="📐",
        )
        set_active_tab(dashboard, 0)
        return

    if is_lab_gate_passed(dashboard):
        page_content_fn()
        return

    tokens = get_dashboard_tokens(dashboard)
    atmosphere = tokens["lab_atmosphere"]
    title_style = css_from_type(TYPE_HERO_TITLE, tokens["text_primary"])
    body_style = join_styles(
        css_from_type(TYPE_BODY, tokens["text_muted"]),
        "max-width:560px",
        f"margin:{SPACING_MD}px auto 0",
    )
    chip_style = join_styles(
        "font-size:11px",
        f"color:{tokens['text_muted']}",
        f"padding:{SPACING_XS}px 10px",
        f"border:1px solid {tokens['border']}",
        "border-radius:20px",
    )

    container_style = join_styles(
        f"background:linear-gradient(135deg,{atmosphere} 0%,{tokens['bg']} 70%)",
        f"border:1px solid {tokens['border']}",
        f"border-radius:{RADIUS_XL}px",
        f"padding:{SPACING_LG}px 40px",
        "text-align:center",
        f"margin:{SPACING_LG}px 0",
        f"box-shadow:0 0 0 1px {tokens['accent']}22 inset",
    )
    chip_row = join_styles(
        "margin-top:20px",
        "display:flex",
        f"gap:{SPACING_MD}px",
        "justify-content:center",
        "flex-wrap:wrap",
    )
    html = (
        f'<div style="{container_style}">'
        f'<div style="font-size:56px;margin-bottom:{SPACING_MD}px;opacity:0.85;">⚗</div>'
        f'<div style="{title_style}">Analytical Workspace</div>'
        f'<div style="{body_style}">High-density multi-variable analysis environment. '
        f"Radar overlays, pairplot matrices, and parallel coordinate brushing are "
        f"reserved for focused exploration.</div>"
        f'<div style="{chip_row}">'
        f'<span style="{chip_style}">HIGH DENSITY</span>'
        f'<span style="{chip_style}">FULLSCREEN READY</span>'
        f'<span style="{chip_style}">ANALYST GATE</span></div></div>'
    )
    render_html_block(html)

    st.warning(
        "This section has higher cognitive load than standard dashboard pages. "
        "Enter only when multi-dimensional comparison is required.",
        icon="⚠️",
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        enter_col, back_col = st.columns(2)
        with enter_col:
            if st.button("Enter Workspace", type="primary", use_container_width=True):
                result = pass_lab_gate(dashboard)
                request_rerun(result, source=f"{dashboard}_lab_gate_enter")
        with back_col:
            if st.button("← Back to Overview", use_container_width=True):
                result = set_active_tab(dashboard, 0)
                request_rerun(result, source=f"{dashboard}_lab_gate_back")
