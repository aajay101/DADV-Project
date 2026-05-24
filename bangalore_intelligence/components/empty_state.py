"""Empty and error fallback panels — presentation only."""

from components.interaction_education.empty_state_guidance import render_empty_state_guidance
from config.typography import TYPE_BODY, TYPE_SECTION_TITLE, css_from_type
from config.theme import RADIUS_LG, SPACING_LG, SPACING_MD, get_dashboard_tokens
from utils.html_styles import join_styles, styled_p
from utils.ui_blocks import escape_text, render_html_block


def empty_state(
    title: str,
    message: str,
    height: int = 400,
    icon: str = "📊",
    dashboard: str = "traffic",
    context: str | None = None,
    semantic_kind: str | None = "valid_empty_result",
) -> None:
    tokens = get_dashboard_tokens(dashboard)
    context_html = styled_p(context, css_from_type(TYPE_BODY, tokens["text_muted"])) if context else ""

    title_style = join_styles(
        css_from_type(TYPE_SECTION_TITLE, tokens["text_primary"]),
        f"margin-bottom:{SPACING_MD}px",
    )
    message_style = join_styles(
        css_from_type(TYPE_BODY, tokens["text_muted"]),
        "max-width:420px",
    )
    container_style = join_styles(
        f"height:{height}px",
        f"background:{tokens['surface_2']}",
        f"border:1px dashed {tokens['border']}",
        f"border-radius:{RADIUS_LG}px",
        "display:flex",
        "flex-direction:column",
        "align-items:center",
        "justify-content:center",
        "text-align:center",
        f"padding:{SPACING_LG}px",
    )
    icon_style = join_styles(
        "font-size:32px",
        "opacity:0.5",
        f"margin-bottom:{SPACING_MD}px",
    )

    html = (
        f'<div style="{container_style}">'
        f'<div style="{icon_style}">{escape_text(icon)}</div>'
        f'<div style="{title_style}">{escape_text(title)}</div>'
        f'<div style="{message_style}">{escape_text(message)}</div>'
        f"{context_html}</div>"
    )
    render_html_block(html)
    render_empty_state_guidance(semantic_kind)
