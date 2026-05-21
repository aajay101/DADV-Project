"""Page hero — Command Zone anchor (compressed)."""

from config.typography import TYPE_CAPTION, TYPE_HERO_TITLE, css_from_type
from config.theme import RADIUS_LG, SPACING_MD, SPACING_SM, SPACING_XS, get_dashboard_tokens
from utils.html_styles import join_styles, left_accent_bar, pill_badge, styled_div
from utils.ui_blocks import render_html_block


def hero_section(
    title: str,
    subtitle: str | None = None,
    severity_badge: str | None = None,
    dashboard: str = "traffic",
    page_indicator: str | None = None,
) -> None:
    tokens = get_dashboard_tokens(dashboard)
    badge_html = ""
    if severity_badge:
        sev_color = tokens["severity_critical"] if severity_badge in ("CRITICAL", "SEVERE") else tokens["severity_warning"]
        badge_html = pill_badge(severity_badge, f"{sev_color}33", sev_color, sev_color)

    subtitle_html = ""
    if subtitle:
        subtitle_style = join_styles(
            css_from_type(TYPE_CAPTION, tokens["text_muted"]),
            f"margin-top:{SPACING_XS}px",
            "font-size:13px",
            "line-height:1.5",
        )
        subtitle_html = styled_div(subtitle, subtitle_style)

    title_style = join_styles(css_from_type(TYPE_HERO_TITLE, tokens["text_primary"]), "font-size:18px;")
    accent_bar = left_accent_bar(tokens["accent"])
    container_style = join_styles(
        f"background:linear-gradient(90deg,{tokens['surface']} 0%,{tokens['bg']} 100%)",
        accent_bar,
        f"padding:{SPACING_MD}px {SPACING_MD}px",
        f"margin-bottom:{SPACING_MD}px",
        f"border-radius:0 {RADIUS_LG}px {RADIUS_LG}px 0",
    )
    identity_style = join_styles(
        "font-size:10px",
        "font-weight:600",
        "letter-spacing:0.1em",
        f"color:{tokens['text_muted']}",
        "text-transform:uppercase",
    )

    hero_html = f"""
    <div class="buip-hero" style="{container_style}">
        <div style="{identity_style}">BUIP · {tokens['identity_label']}</div>
        <div style="{title_style}">{title} {badge_html}</div>
        {subtitle_html}
    </div>
    """
    render_html_block(hero_html)
