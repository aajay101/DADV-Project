"""Universal visualization shell — all charts render inside this system."""

from typing import Any

import streamlit as st

from components.empty_state import empty_state
from components.loading_state import chart_skeleton, inline_loader
from components.states import border_for_state
from config.chart_defaults import CHART_SIZES
from config.typography import TYPE_CAPTION, TYPE_CHART_HERO, TYPE_CHART_SUPPORT, css_from_type
from config.theme import RADIUS_LG, SPACING_LG, SPACING_MD, SPACING_SM, SPACING_XS, get_dashboard_tokens
from utils.html_styles import chart_shell_classes, join_styles, pill_badge, styled_div, styled_p
from utils.plotly_engine import PLOTLY_CONFIG
from utils.ui_blocks import render_html_block


def _shell_style(tokens: dict, border: str, role: str) -> str:
    if role == "hero":
        bg = tokens["surface_3"]
        border_color = tokens["border_hover"]
        padding = SPACING_LG
        extra = f"min-height:{CHART_SIZES['hero_half'] + 80}px;"
    else:
        bg = tokens["surface"]
        border_color = tokens["border"]
        padding = SPACING_MD
        extra = ""
    return join_styles(
        f"background:{bg}",
        border,
        f"border-color:{border_color}",
        f"border-radius:{RADIUS_LG}px",
        f"padding:{padding}px",
        f"margin-bottom:{SPACING_MD}px",
        f"box-shadow:inset 0 1px 0 {tokens['border_2']}",
        extra,
    )


def chart_container(
    fig=None,
    title: str = "",
    subtitle: str | None = None,
    caption: str | None = None,
    height: int | None = None,
    fullscreen_key: str | None = None,
    use_container_width: bool = True,
    dashboard: str = "traffic",
    role: str = "supporting",
    state: str = "default",
    record_count: str | None = "n = —",
    selection_label: str | None = None,
    *,
    chart_id: str | None = None,
    interactive: bool = False,
    page_key: str = "",
    interaction_meta: dict[str, Any] | None = None,
    selection_mode: str | tuple[str, ...] = "points",
) -> None:
    tokens = get_dashboard_tokens(dashboard)
    h = height or (CHART_SIZES["hero_half"] if role == "hero" else CHART_SIZES["supporting"])
    title_type = TYPE_CHART_HERO if role == "hero" else TYPE_CHART_SUPPORT
    title_color = tokens["text_primary"] if role == "hero" else tokens["text_muted"]
    display_state = "selected" if selection_label else state
    border = border_for_state(display_state, tokens)
    shell_class = chart_shell_classes(role)

    subtitle_html = ""
    if subtitle:
        subtitle_style = join_styles(
            css_from_type(TYPE_CAPTION, tokens["text_muted"]),
            f"margin-top:{SPACING_XS}px",
            "text-transform:none",
            "letter-spacing:0.02em",
        )
        subtitle_html = styled_div(subtitle, subtitle_style)

    badge_html = ""
    if selection_label:
        badge_html = pill_badge(
            f"Showing: {selection_label}",
            f"{tokens['severity_warning']}22",
            tokens["severity_warning"],
            tokens["severity_warning"],
        )

    title_style = css_from_type(title_type, title_color)
    header_html = f"""
    <div class="{shell_class}" style="{_shell_style(tokens, border, role)}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:{SPACING_MD}px;">
            <div>
                <div style="{title_style}">{title}</div>
                {subtitle_html}
            </div>
            <div>{badge_html}</div>
        </div>
    </div>
    """
    render_html_block(header_html)

    if fullscreen_key:
        _, fs_col = st.columns([6, 1])
        with fs_col:
            st.button(
                "⤢",
                key=f"fs_{fullscreen_key}_{dashboard}_{abs(hash(title)) % 10_000}",
                help="Fullscreen mount · Phase 5",
            )

    if state == "loading":
        inline_loader(dashboard=dashboard)
        chart_skeleton(height=h, dashboard=dashboard)
    elif state == "empty":
        empty_state(
            title="No data matches filters",
            message="Adjust the date range or scope filters to restore chart content.",
            height=h,
            dashboard=dashboard,
        )
    elif fig is not None:
        if interactive and chart_id and page_key:
            from filters.interaction import chart_widget_key, process_plotly_selection

            widget_key = chart_widget_key(page_key, chart_id, dashboard)
            plotly_state = st.plotly_chart(
                fig,
                use_container_width=use_container_width,
                height=h,
                config=PLOTLY_CONFIG,
                key=widget_key,
                on_select="rerun",
                selection_mode=selection_mode,
            )
            process_plotly_selection(
                chart_id,
                plotly_state,
                interaction_meta,
                dashboard,  # type: ignore[arg-type]
            )
        else:
            st.plotly_chart(
                fig,
                use_container_width=use_container_width,
                height=h,
                config=PLOTLY_CONFIG,
            )
    else:
        placeholder_html = f"""
        <div class="buip-chart-placeholder" style="
            height:{h}px;
            background:linear-gradient(180deg,{tokens['surface_3']} 0%,{tokens['surface_2']} 100%);
            border:1px dashed {tokens['border']};
            border-radius:{RADIUS_LG}px;
            display:flex;flex-direction:column;align-items:center;justify-content:center;
            color:{tokens['text_muted']};font-size:13px;gap:{SPACING_SM}px;
            margin-bottom:{SPACING_SM}px;
        ">
            <div class="buip-skeleton" style="width:72%;height:14px;border-radius:4px;"></div>
            <div class="buip-skeleton" style="width:55%;height:120px;border-radius:6px;"></div>
            <div class="buip-skeleton" style="width:40%;height:10px;border-radius:4px;"></div>
            <span style="font-size:11px;opacity:0.75;">Visualization slot · upcoming phase</span>
        </div>
        """
        render_html_block(placeholder_html)

    footer_parts = []
    if caption:
        caption_style = join_styles(
            css_from_type(TYPE_CAPTION, tokens["text_muted"]),
            f"margin:{SPACING_SM}px 0 0 0",
        )
        footer_parts.append(styled_p(caption, caption_style))

    footer_style = css_from_type(TYPE_CAPTION, tokens["text_muted"])
    footer_parts.append(
        f"""
        <div style="display:flex;justify-content:space-between;margin-top:{SPACING_SM}px;">
            <span style="{footer_style}">{record_count}</span>
        </div>
        """
    )
    render_html_block("".join(footer_parts))
