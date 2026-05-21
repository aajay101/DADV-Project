"""Investigate Further — secondary navigation."""

import streamlit as st

from config.typography import TYPE_BODY, TYPE_SUBSECTION_TITLE, css_from_type
from config.theme import RADIUS_LG, SPACING_MD, SPACING_SM, get_dashboard_tokens
from filters.state import set_active_tab
from utils.html_styles import join_styles, left_accent_bar
from utils.ui_blocks import render_html_block


def nav_card(
    label: str,
    destination_title: str,
    destination_description: str,
    tab_index: int,
    dashboard: str = "traffic",
) -> None:
    tokens = get_dashboard_tokens(dashboard)
    label_style = css_from_type(TYPE_SUBSECTION_TITLE, tokens["text_muted"])
    title_style = join_styles(
        css_from_type(TYPE_SUBSECTION_TITLE, tokens["text_primary"]),
        f"margin-top:{SPACING_SM}px;",
    )
    desc_style = join_styles(
        css_from_type(TYPE_BODY, tokens["text_muted"]),
        f"margin-top:{SPACING_SM}px;",
    )
    card_style = join_styles(
        f"background:{tokens['surface']}",
        f"border:1px solid {tokens['border_2']}",
        left_accent_bar(tokens["accent"]),
        f"border-radius:{RADIUS_LG}px",
        f"padding:{SPACING_MD}px 20px",
        f"margin-top:{SPACING_MD}px",
    )

    html = f"""
    <div class="buip-nav-card" style="{card_style}">
        <div style="{label_style}">{label}</div>
        <div style="{title_style}">{destination_title} →</div>
        <div style="{desc_style}">{destination_description}</div>
    </div>
    """
    render_html_block(html)

    if st.button(
        f"Continue to {destination_title}",
        key=f"buip_nav_{dashboard}_{tab_index}",
        use_container_width=True,
    ):
        set_active_tab(dashboard, tab_index)
        st.rerun()
