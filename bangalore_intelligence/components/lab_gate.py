"""Advanced Analytics Laboratory gate — deeper technical atmosphere."""

from collections.abc import Callable

import streamlit as st

from config.typography import TYPE_BODY, TYPE_HERO_TITLE, css_from_type
from config.theme import RADIUS_XL, SPACING_LG, SPACING_MD, SPACING_SM, SPACING_XS, get_dashboard_tokens
from filters.state import is_lab_gate_passed, pass_lab_gate, set_active_tab
from utils.html_styles import join_styles
from utils.ui_blocks import render_html_block


def lab_gate(dashboard: str, page_content_fn: Callable[[], None]) -> None:
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

    html = f"""
    <div style="
        background:linear-gradient(135deg,{atmosphere} 0%,{tokens['bg']} 70%);
        border:1px solid {tokens['border']};
        border-radius:{RADIUS_XL}px;
        padding:{SPACING_LG}px 40px;
        text-align:center;
        margin:{SPACING_LG}px 0;
        box-shadow:0 0 0 1px {tokens['accent']}22 inset;
    ">
        <div style="font-size:56px;margin-bottom:{SPACING_MD}px;opacity:0.85;">⚗</div>
        <div style="{title_style}">Advanced Analytics Laboratory</div>
        <div style="{body_style}">
            High-density multi-variable analysis environment. Radar overlays, pairplot matrices,
            and parallel coordinate brushing activate in later phases.
        </div>
        <div style="margin-top:20px;display:flex;gap:{SPACING_MD}px;justify-content:center;flex-wrap:wrap;">
            <span style="{chip_style}">HIGH DENSITY</span>
            <span style="{chip_style}">FULLSCREEN READY</span>
            <span style="{chip_style}">ANALYST GATE</span>
        </div>
    </div>
    """
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
            if st.button("Enter Lab", type="primary", use_container_width=True):
                pass_lab_gate(dashboard)
                st.rerun()
        with back_col:
            if st.button("← Back to Overview", use_container_width=True):
                set_active_tab(dashboard, 0)
                st.rerun()
