"""What This Means insight card — context zone, subdued hierarchy."""

import streamlit as st

from config.typography import TYPE_ALERT, TYPE_BODY, css_from_type
from config.spacing import EXPANDER_CONTENT_GAP, INSIGHT_BODY_TOP
from config.theme import RADIUS_LG, SPACING_MD, get_dashboard_tokens
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
            from utils.ui_blocks import render_spacer

            render_spacer(EXPANDER_CONTENT_GAP // 2)
            _render_body(body, tokens, accent)
            render_spacer(EXPANDER_CONTENT_GAP // 2)
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
        f"padding:{SPACING_MD + 4}px {SPACING_MD + 6}px",
        f"border-radius:0 {RADIUS_LG}px {RADIUS_LG}px 0",
        f"margin-top:{INSIGHT_BODY_TOP}px",
        "line-height:1.65",
    )
    html = f"""
    <div class="buip-insight-body" style="{container_style}">
        <p style="{body_style}">{body}</p>
    </div>
    """
    render_html_block(html)
