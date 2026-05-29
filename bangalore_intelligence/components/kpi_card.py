"""Executive-grade KPI card — severity, trend, gauge, states."""

from components.explainability.explainability_trigger import render_explainability_trigger
from components.explainability.explainability_utils import kpi_entry
from components.loading_state import kpi_skeleton
from components.states import border_for_state, opacity_for_state
from config.spacing import KPI_CARD_MIN_HEIGHT, KPI_LABEL_TO_VALUE, KPI_VALUE_LINE_HEIGHT
from config.typography import TYPE_KPI_LABEL, TYPE_KPI_VALUE, TYPE_KPI_VALUE_COMPACT, TYPE_KPI_VALUE_LARGE, css_from_type
from config.theme import FONT_MONO, RADIUS_LG, SPACING_MD, SPACING_SM, get_dashboard_tokens, get_severity_colors
from utils.html_styles import join_styles, pill_badge, styled_span
from utils.ui_blocks import escape_text, render_html_block


def _gauge_svg(percent: float, color: str, border_color: str) -> str:
    fill = max(0, min(100, percent)) / 100 * 201
    return f"""
    <svg width="56" height="56" viewBox="0 0 80 80" style="flex-shrink:0;">
      <circle cx="40" cy="40" r="32" fill="none" stroke="{border_color}" stroke-width="4"/>
      <circle cx="40" cy="40" r="32" fill="none" stroke="{color}" stroke-width="4"
        stroke-dasharray="{fill:.0f} 201" stroke-linecap="round"
        transform="rotate(-90 40 40)" style="transition:stroke-dasharray 0.6s ease-out;"/>
    </svg>
    """


def kpi_card(
    label: str,
    value: str,
    delta: str | None = None,
    delta_positive: bool | None = None,
    gauge_percent: float | None = None,
    severity: str = "neutral",
    size: str = "normal",
    dashboard: str = "traffic",
    state: str = "default",
    icon: str | None = None,
    note: str | None = None,
    loading: bool = False,
    filtered_note: bool = False,
    explainability_id: str | None = None,
) -> None:
    if loading:
        kpi_skeleton(dashboard)
        return

    tokens = get_dashboard_tokens(dashboard)
    severity_colors = get_severity_colors(dashboard)
    value_color = severity_colors.get(severity, tokens["text_primary"])

    if size == "large":
        value_style = css_from_type(TYPE_KPI_VALUE_LARGE, value_color, "font-variant-numeric:tabular-nums;")
    elif size == "compact":
        value_style = css_from_type(TYPE_KPI_VALUE_COMPACT, value_color, "font-variant-numeric:tabular-nums;")
    else:
        value_style = css_from_type(TYPE_KPI_VALUE, value_color, "font-variant-numeric:tabular-nums;")

    label_style = join_styles(
        css_from_type(TYPE_KPI_LABEL, tokens["text_muted"]),
        "display:block",
        "overflow-wrap:anywhere",
    )
    border = border_for_state(state, tokens)
    opacity = opacity_for_state(state)

    note_html = ""
    if note:
        note_style = join_styles(
            css_from_type(TYPE_KPI_LABEL, tokens["text_muted"]),
            f"margin-top:{SPACING_SM + 2}px",
            "font-style:italic",
            "line-height:1.5",
        )
        note_html = f'<div style="{note_style}">{escape_text(note)}</div>'

    delta_html = ""
    if delta:
        delta_color = tokens["severity_safe"] if delta_positive else tokens["severity_critical"]
        arrow = "▲" if delta_positive else "▼"
        delta_html = f"""
        <div style="font-family:{FONT_MONO};font-size:12px;color:{delta_color};margin-top:{SPACING_SM}px;line-height:1.4;">
            {arrow} {escape_text(delta)}
        </div>
        """

    icon_html = (
        styled_span(icon, f"font-size:16px;margin-right:{SPACING_SM}px;opacity:0.7;vertical-align:middle;")
        if icon
        else ""
    )
    badge_html = ""
    if state == "stale":
        badge_html = pill_badge(
            "Stale",
            f"{tokens['severity_warning']}22",
            tokens["severity_warning"],
            tokens["severity_warning"],
        )
    elif filtered_note:
        badge_html = pill_badge("Filtered", tokens["surface_3"], tokens["text_muted"], tokens["border"])

    gauge_html = ""
    if gauge_percent is not None and size != "compact":
        gauge_html = _gauge_svg(gauge_percent, value_color, tokens["border"])

    left_border = ""
    if severity in ("critical", "warning"):
        left_border = f"border-left:3px solid {value_color};"

    card_style = join_styles(
        f"background:{tokens['surface']}",
        border,
        left_border,
        f"border-radius:{RADIUS_LG}px",
        f"padding:{SPACING_MD + 4}px {SPACING_MD}px",
        f"min-height:{KPI_CARD_MIN_HEIGHT}px",
        "box-sizing:border-box",
        f"opacity:{opacity}",
        "display:flex",
        "justify-content:space-between",
        "align-items:flex-start",
        f"gap:{SPACING_MD}px",
    )
    value_block_style = join_styles(
        value_style,
        f"margin-top:{KPI_LABEL_TO_VALUE}px",
        f"line-height:{KPI_VALUE_LINE_HEIGHT}",
        "overflow-wrap:anywhere",
        "word-break:break-word",
    )
    label_row_style = join_styles(
        label_style,
        "display:flex",
        "flex-wrap:wrap",
        "align-items:center",
        f"gap:{SPACING_SM}px",
    )

    html = (
        f'<div class="buip-kpi-card" style="{card_style}">'
        f'<div style="flex:1;min-width:0;">'
        f'<div style="{label_row_style}">{icon_html}<span>{escape_text(label)}</span> {badge_html}</div>'
        f'<div style="{value_block_style}">{escape_text(value)}</div>'
        f"{note_html}{delta_html}</div>{gauge_html}</div>"
    )
    render_html_block(html)
    render_explainability_trigger(kpi_entry(explainability_id), label="Explain KPI")
