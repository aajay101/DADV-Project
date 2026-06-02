"""Page hero - Command Zone anchor."""

from config.spacing import (
    HERO_BADGE_GAP,
    HERO_IDENTITY_BOTTOM,
    HERO_PADDING_X,
    HERO_PADDING_Y,
    HERO_TITLE_GAP,
    SECTION_GAP_SM,
)
from config.typography import TYPE_CAPTION, TYPE_HERO_TITLE, css_from_type
from config.theme import RADIUS_LG, get_dashboard_tokens
from utils.html_styles import join_styles, left_accent_bar, styled_div
from utils.ui_blocks import escape_text, render_html_block


def hero_section(
    title: str,
    subtitle: str | None = None,
    severity_badge: str | None = None,
    dashboard: str = "traffic",
    page_indicator: str | None = None,
) -> None:
    del page_indicator  # reserved for future page chrome
    del severity_badge
    tokens = get_dashboard_tokens(dashboard)

    subtitle_html = ""
    if subtitle:
        subtitle_style = join_styles(
            css_from_type(TYPE_CAPTION, tokens["text_muted"]),
            f"margin-top:{HERO_TITLE_GAP}px",
            "font-size:13px",
            "line-height:1.65",
            "max-width:920px",
        )
        subtitle_html = styled_div(subtitle, subtitle_style)

    title_style = join_styles(
        css_from_type(TYPE_HERO_TITLE, tokens["text_primary"]),
        "font-size:clamp(20px,2.1vw,26px)",
        "overflow-wrap:anywhere",
        "word-break:break-word",
    )
    title_row_style = join_styles(
        "display:flex",
        "flex-wrap:wrap",
        "align-items:center",
        f"gap:{HERO_BADGE_GAP}px",
        f"margin-top:{HERO_IDENTITY_BOTTOM}px",
    )
    accent_bar = left_accent_bar(tokens["accent"])
    container_style = join_styles(
        f"background:linear-gradient(90deg,{tokens['surface']} 0%,{tokens['bg']} 100%)",
        accent_bar,
        f"padding:{HERO_PADDING_Y}px {HERO_PADDING_X}px",
        f"margin-bottom:{SECTION_GAP_SM}px",
        f"border-radius:0 {RADIUS_LG}px {RADIUS_LG}px 0",
    )
    identity_style = join_styles(
        "font-size:10px",
        "font-weight:600",
        "letter-spacing:0.1em",
        f"color:{tokens['text_muted']}",
        "line-height:1.5",
    )

    hero_html = (
        f'<div class="buip-hero" style="{container_style}">'
        f'<div style="{identity_style}">{escape_text(tokens["identity_label"])}</div>'
        f'<div style="{title_row_style}">'
        f'<div style="{title_style}">{escape_text(title)}</div>'
        f"</div>{subtitle_html}</div>"
    )
    render_html_block(hero_html)
