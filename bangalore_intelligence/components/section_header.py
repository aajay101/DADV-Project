"""Section and subsection headers for visual hierarchy."""

from config.typography import TYPE_SECTION_TITLE, TYPE_SUBSECTION_TITLE, css_from_type
from config.theme import GAP_DEFAULT, SPACING_XS, get_dashboard_tokens
from utils.html_styles import join_styles, pill_badge, styled_div
from utils.ui_blocks import render_html_block


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
        badge_html = " " + pill_badge(
            badge,
            f"{tokens['severity_warning']}22",
            tokens["severity_warning"],
            tokens["severity_warning"],
        )
    subtitle_html = ""
    if subtitle:
        subtitle_style = join_styles(
            css_from_type(TYPE_SUBSECTION_TITLE, tokens["text_muted"]),
            f"margin-top:{SPACING_XS}px",
            "font-weight:400",
            "text-transform:none",
            "letter-spacing:0",
        )
        subtitle_html = styled_div(subtitle, subtitle_style)

    zone_label = zone.upper()
    zone_style = join_styles(css_from_type(TYPE_SUBSECTION_TITLE, tokens["text_muted"]), "opacity:0.7;")
    title_style = join_styles(css_from_type(TYPE_SECTION_TITLE, tokens["text_primary"]), f"margin-top:{SPACING_XS}px;")

    header_html = f"""
    <div style="height:{GAP_DEFAULT}px;"></div>
    <div>
        <div style="{zone_style}">{zone_label} ZONE</div>
        <div style="{title_style}">{title}{badge_html}</div>
        {subtitle_html}
    </div>
    <div style="height:{GAP_DEFAULT}px;"></div>
    """
    render_html_block(header_html)
