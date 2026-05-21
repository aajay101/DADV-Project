"""Empty and error fallback panels — presentation only."""

from config.typography import TYPE_BODY, TYPE_SECTION_TITLE, css_from_type
from config.theme import RADIUS_LG, SPACING_LG, SPACING_MD, get_dashboard_tokens
from utils.html_styles import join_styles, styled_p
from utils.ui_blocks import render_html_block


def empty_state(
    title: str,
    message: str,
    height: int = 400,
    icon: str = "📊",
    dashboard: str = "traffic",
    context: str | None = None,
) -> None:
    tokens = get_dashboard_tokens(dashboard)
    context_html = ""
    if context:
        context_style = css_from_type(TYPE_BODY, tokens["text_muted"])
        context_html = styled_p(context, context_style)

    title_style = join_styles(
        css_from_type(TYPE_SECTION_TITLE, tokens["text_primary"]),
        f"margin-bottom:{SPACING_MD}px;",
    )
    message_style = join_styles(
        css_from_type(TYPE_BODY, tokens["text_muted"]),
        "max-width:420px;",
    )

    html = f"""
    <div style="
        height:{height}px;
        background:{tokens['surface_2']};
        border:1px dashed {tokens['border']};
        border-radius:{RADIUS_LG}px;
        display:flex;
        flex-direction:column;
        align-items:center;
        justify-content:center;
        text-align:center;
        padding:{SPACING_LG}px;
    ">
        <div style="font-size:32px;opacity:0.5;margin-bottom:{SPACING_MD}px;">{icon}</div>
        <div style="{title_style}">{title}</div>
        <div style="{message_style}">{message}</div>
        {context_html}
    </div>
    """
    render_html_block(html)
