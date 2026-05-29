"""Advanced Lab mode strip — technical atmosphere."""

from config.typography import TYPE_ALERT, TYPE_CAPTION, css_from_type
from config.theme import RADIUS_LG, SPACING_MD, get_dashboard_tokens
from utils.html_styles import join_styles, left_accent_bar, pill_badge, styled_p
from utils.ui_blocks import render_html_block


def lab_header(dashboard: str = "traffic") -> None:
    tokens = get_dashboard_tokens(dashboard)
    title_style = css_from_type(TYPE_ALERT, tokens["text_primary"])
    caption_style = css_from_type(TYPE_CAPTION, tokens["text_muted"])
    container_style = join_styles(
        f"background:linear-gradient(90deg,{tokens['lab_atmosphere']} 0%,{tokens['surface_2']} 100%)",
        left_accent_bar(tokens["accent"]),
        f"padding:{SPACING_MD}px 20px",
        f"margin-bottom:{SPACING_MD}px",
        f"border-radius:0 {RADIUS_LG}px {RADIUS_LG}px 0",
        "display:flex",
        "justify-content:space-between",
        "align-items:center",
        "flex-wrap:wrap",
        f"gap:{SPACING_MD}px",
    )
    badge = pill_badge(
        "HIGH DENSITY",
        tokens["surface_3"],
        tokens["accent_secondary"],
        tokens["border"],
    )
    html = (
        f'<div style="{container_style}">'
        f'<span style="{title_style}">⚗ ADVANCED ANALYTICS LABORATORY · ACTIVE</span>{badge}</div>'
        + styled_p(
            "Breadcrumb: Overview → Lab · Use ⤢ on eligible charts for fullscreen inspection",
            caption_style,
        )
    )
    render_html_block(html)
