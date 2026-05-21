"""What This Means insight card — context zone, subdued hierarchy."""

import streamlit as st

from config.typography import TYPE_ALERT, TYPE_BODY, css_from_type
from config.theme import RADIUS_LG, SPACING_MD, SPACING_SM, get_dashboard_tokens
from utils.html_styles import join_styles, left_accent_bar, styled_div
from utils.ui_blocks import render_html_block


def insight_card(
    heading: str,
    body: str,
    severity: str = "neutral",
    collapsible: bool = True,
    key: str | None = None,
    dashboard: str = "traffic",
    default_expanded: bool = False,
) -> None:
    tokens = get_dashboard_tokens(dashboard)
    accent = tokens["severity_critical"] if severity == "critical" else tokens["accent"]
    label = f"WHAT THIS MEANS · {heading}"

    if collapsible:
        with st.expander(label, expanded=default_expanded):
            _render_body(body, tokens, accent)
    else:
        label_style = css_from_type(TYPE_ALERT, tokens["text_muted"])
        render_html_block(styled_div(label, label_style))
        _render_body(body, tokens, accent)


def _render_body(body: str, tokens: dict, accent: str) -> None:
    body_style = css_from_type(TYPE_BODY, tokens["text_muted"])
    accent_bar = left_accent_bar(accent)
    container_style = join_styles(
        f"background:{tokens['surface_2']}",
        accent_bar,
        f"padding:{SPACING_MD}px {SPACING_MD + 4}px",
        f"border-radius:0 {RADIUS_LG}px {RADIUS_LG}px 0",
        f"margin-top:{SPACING_SM}px",
    )
    html = f"""
    <div style="{container_style}">
        <p style="{body_style}">{body}</p>
    </div>
    """
    render_html_block(html)
