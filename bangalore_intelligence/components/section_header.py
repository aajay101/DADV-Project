"""Section and subsection headers for visual hierarchy."""

from config.spacing import SECTION_GAP_MD, SECTION_GAP_SM, SECTION_HEADER_SUBTITLE_GAP
from config.typography import TYPE_SECTION_TITLE, TYPE_SUBSECTION_TITLE, css_from_type
from config.theme import get_dashboard_tokens
from utils.html_styles import join_styles, pill_badge, styled_div
from utils.ui_blocks import escape_text, render_html_block, render_spacer


def section_header(
    title: str,
    subtitle: str | None = None,
    badge: str | None = None,
    zone: str = "investigation",
    dashboard: str = "traffic",
) -> None:
    tokens = get_dashboard_tokens(dashboard)
    badge_html = ""
    if badge:
        badge_html = pill_badge(
            badge,
            f"{tokens['severity_warning']}22",
            tokens["severity_warning"],
            tokens["severity_warning"],
        )
    subtitle_html = ""
    if subtitle:
        subtitle_style = join_styles(
            css_from_type(TYPE_SUBSECTION_TITLE, tokens["text_muted"]),
            f"margin-top:{SECTION_HEADER_SUBTITLE_GAP}px",
            "font-weight:400",
            "text-transform:none",
            "letter-spacing:0",
            "line-height:1.55",
            "max-width:920px",
        )
        subtitle_html = styled_div(subtitle, subtitle_style)

    del zone
    title_row_style = join_styles(
        css_from_type(TYPE_SECTION_TITLE, tokens["text_primary"]),
        "margin-top:0",
        "display:flex",
        "flex-wrap:wrap",
        "align-items:center",
        "justify-content:center" if title in ("Analytical Modules", "Extended Analysis") else "",
        "gap:10px",
        "line-height:1.45",
    )

    render_spacer(SECTION_GAP_SM)
    header_html = (
        f'<div class="buip-section-header">'
        f'<div style="{title_row_style}"><span>{escape_text(title)}</span>{badge_html}</div>'
        f"{subtitle_html}</div>"
    )
    render_html_block(header_html)
    render_spacer(SECTION_GAP_MD)
