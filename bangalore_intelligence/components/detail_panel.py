"""Drilldown detail panel — selected state presentation."""

from components.states import border_for_state
from config.typography import TYPE_BODY, TYPE_SUBSECTION_TITLE, css_from_type
from config.theme import RADIUS_LG, SPACING_MD, SPACING_SM, get_dashboard_tokens
from utils.html_styles import join_styles, left_accent_bar, pill_badge, styled_p
from utils.ui_blocks import escape_text, render_html_block


def detail_panel(
    title: str,
    metrics: list[dict],
    notes: str | None = None,
    visible: bool = True,
    dashboard: str = "traffic",
    state: str = "selected",
) -> None:
    if not visible:
        return

    tokens = get_dashboard_tokens(dashboard)
    border = border_for_state(state, tokens)
    metric_label_style = join_styles(
        css_from_type(TYPE_BODY, tokens["text_muted"]),
        "font-size:11px",
        "text-transform:uppercase",
    )
    metric_value_style = join_styles(
        "font-family:'JetBrains Mono',monospace",
        "font-size:15px",
        "font-weight:600",
        f"color:{tokens['text_primary']}",
    )
    metrics_html = "".join(
        f'<div style="margin-right:28px;margin-bottom:{SPACING_SM}px;">'
        f'<div style="{metric_label_style}">{escape_text(m.get("label", ""))}</div>'
        f'<div style="{metric_value_style}">{escape_text(m.get("value", "—"))}</div></div>'
        for m in metrics
    )
    notes_html = ""
    if notes:
        notes_style = join_styles(
            css_from_type(TYPE_BODY, tokens["text_muted"]),
            f"margin-top:{SPACING_MD}px",
        )
        notes_html = styled_p(notes, notes_style)
    elif dashboard == "traffic":
        hint_style = join_styles(
            css_from_type(TYPE_BODY, tokens["text_muted"]),
            f"margin-top:{SPACING_MD}px",
            "font-size:12px",
        )
        notes_html = styled_p(
            "Chart focus is local until you choose Apply as filter in the focus strip.",
            hint_style,
        )

    title_style = css_from_type(TYPE_SUBSECTION_TITLE, tokens["text_primary"])
    container_style = join_styles(
        f"background:{tokens['surface_2']}",
        left_accent_bar(tokens["accent"]),
        border,
        f"padding:{SPACING_MD}px 20px",
        f"margin-bottom:{SPACING_MD}px",
        f"border-radius:0 {RADIUS_LG}px {RADIUS_LG}px 0",
    )
    badge = pill_badge(
        "Selection Active",
        tokens["surface_3"],
        tokens["severity_warning"],
        tokens["border"],
    )
    header_row = join_styles(
        "display:flex",
        "justify-content:space-between",
        "align-items:center",
    )
    metrics_row = join_styles(
        "display:flex",
        "flex-wrap:wrap",
        f"margin-top:{SPACING_MD}px",
    )

    html = (
        f'<div style="{container_style}">'
        f'<div style="{header_row}">'
        f'<div style="{title_style}">Detail · {escape_text(title)}</div>{badge}</div>'
        f'<div style="{metrics_row}">{metrics_html}</div>{notes_html}</div>'
    )
    render_html_block(html)
