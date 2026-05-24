"""Universal visualization shell — all charts render inside this system."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import streamlit as st

from components.explainability.explainability_trigger import render_explainability_trigger
from components.explainability.explainability_utils import chart_entry
from components.empty_state import empty_state
from components.interaction_education.interaction_mode_help import render_chart_interaction_mode_hint
from components.loading_state import chart_skeleton, inline_loader, resolve_skeleton_type
from components.states import border_for_state
from components.layout.responsive import get_active_breakpoint
from config.chart_defaults import chart_size_for, resolve_chart_height
from config import spacing as spacing_tokens
from config.spacing import (
    CHART_HEADER_TO_CONTROLS,
    CHART_MODULE_BOTTOM,
    CHART_CONTROLS_TO_PLOT,
)
from config.theme import get_dashboard_tokens
from filters.fullscreen import (
    clear_fullscreen,
    is_fullscreen_active,
    is_fullscreen_eligible,
    set_fullscreen,
)
from utils.html_styles import join_styles, pill_badge, styled_p
from utils.plotly_engine import PLOTLY_CONFIG
from utils.plotly_layout import (
    apply_density_marker_defaults,
    chart_layout_type,
    normalize_figure_for_display,
)
from utils.ui_blocks import escape_text, render_html_block, render_spacer

# Targeted modules: compact fullscreen label + plot slot class (responsive stabilization).
_TARGETED_FS_COMPACT = frozenset({"T-02", "T-13", "A-02", "A-03", "A-05", "A-15"})
_TARGETED_PLOT_SLOTS = frozenset({"T-02", "T-13", "T-03", "A-02", "A-03", "A-05"})
_COMPACT_TITLE_TO_PLOT = frozenset({"A-01"})


def _fullscreen_label(chart_id: str | None) -> str:
    return "⤢ FS" if chart_id in _TARGETED_FS_COMPACT else "⤢ Fullscreen"


def _fs_column_weights(chart_id: str | None) -> list[float]:
    if chart_id in ("T-02", "T-13"):
        return [1.45, 4.55]
    return [1, 5]


def _render_chart_title_block(
    *,
    title: str,
    subtitle: str | None,
    selection_label: str | None,
    header_note: str | None,
    role: str,
    dashboard: str,
    chart_id: str | None = None,
) -> None:
    """Chart chrome via safe HTML fragments (no split div/markdown boundaries)."""
    tokens = get_dashboard_tokens(dashboard)
    if role == "hero":
        title_style = join_styles(
            "font-size:16px",
            "font-weight:600",
            f"color:{tokens['text_primary']}",
            "margin:0 0 6px 0",
            "line-height:1.4",
        )
        title_class = "buip-chart-title buip-chart-title--hero"
        if chart_id == "A-01":
            title_class += " buip-chart-title--a01"
    else:
        title_style = join_styles(
            "font-size:14px",
            "font-weight:500",
            f"color:{tokens['text_muted']}",
            "margin:0 0 6px 0",
            "line-height:1.45",
        )
        title_class = "buip-chart-title buip-chart-title--support"

    parts = [
        f'<p class="{title_class}" style="{title_style}">{escape_text(title)}</p>',
    ]
    if subtitle:
        subtitle_bottom = "6px" if chart_id == "A-01" else "8px"
        parts.append(
            styled_p(
                subtitle,
                join_styles(
                    f"color:{tokens['text_muted']}",
                    "font-size:13px",
                    f"margin:0 0 {subtitle_bottom} 0",
                    "line-height:1.5",
                ),
            )
        )
    if header_note:
        parts.append(
            pill_badge(
                header_note,
                f"{tokens['severity_warning']}22",
                tokens["severity_warning"],
                tokens["severity_warning"],
            )
        )
    if selection_label:
        parts.append(
            pill_badge(
                f"Showing: {selection_label}",
                f"{tokens['severity_warning']}22",
                tokens["severity_warning"],
                tokens["severity_warning"],
            )
        )
    render_html_block("".join(parts))


def chart_container(
    fig=None,
    title: str = "",
    subtitle: str | None = None,
    caption: str | None = None,
    height: int | None = None,
    chart_size: str | None = None,
    fullscreen_key: str | None = None,
    use_container_width: bool = True,
    dashboard: str = "traffic",
    role: str = "supporting",
    state: str = "default",
    record_count: str | None = "n = —",
    selection_label: str | None = None,
    header_note: str | None = None,
    *,
    chart_id: str | None = None,
    interactive: bool = False,
    page_key: str = "",
    interaction_meta: dict[str, Any] | None = None,
    selection_mode: str | tuple[str, ...] = "points",
    active_filters: Mapping[str, Any] | None = None,
    reveal_stagger: bool = False,
) -> None:
    del active_filters, reveal_stagger

    tokens = get_dashboard_tokens(dashboard)
    bp = get_active_breakpoint()
    size_key = chart_size or chart_size_for(chart_id, role)
    chart_type = chart_layout_type(chart_id)
    skeleton_type = resolve_skeleton_type(chart_type)
    fs_active = is_fullscreen_active(fullscreen_key, dashboard)
    h = height or resolve_chart_height(
        size_key,
        role=role,
        chart_id=chart_id,
        breakpoint=bp,
        is_fullscreen=fs_active,
    )
    border_for_state("selected" if selection_label else state, tokens)

    with st.container(border=True):
        _render_chart_title_block(
            title=title,
            subtitle=subtitle,
            selection_label=selection_label,
            header_note=header_note,
            role=role,
            dashboard=dashboard,
            chart_id=chart_id,
        )
        render_explainability_trigger(chart_entry(chart_id), fig=fig, chart_height=max(h, 560))
        if interactive:
            render_chart_interaction_mode_hint(st.session_state, "traffic" if dashboard == "traffic" else "aqi")

        has_fs_control = bool(fullscreen_key and is_fullscreen_eligible(fullscreen_key))
        if has_fs_control:
            render_spacer(CHART_HEADER_TO_CONTROLS)
            fs_weights = _fs_column_weights(chart_id)
            fs_cols = st.columns(fs_weights)
            with fs_cols[0]:
                if fs_active:
                    if st.button(
                        "← Exit",
                        key=f"fs_exit_{fullscreen_key}_{dashboard}",
                        help="Return to page layout",
                        type="primary",
                    ):
                        result = clear_fullscreen()
                        from filters.transitions import request_rerun

                        request_rerun(result, source=f"fullscreen_exit_{fullscreen_key}")
                elif st.button(
                    _fullscreen_label(chart_id),
                    key=f"fs_{fullscreen_key}_{dashboard}_{abs(hash(title)) % 10_000}",
                    help="Open chart in fullscreen",
                ):
                    result = set_fullscreen(fullscreen_key, dashboard)
                    from filters.transitions import request_rerun

                    request_rerun(result, source=f"fullscreen_enter_{fullscreen_key}")
            render_spacer(CHART_CONTROLS_TO_PLOT)
        else:
            if chart_id in _COMPACT_TITLE_TO_PLOT:
                pass
            else:
                render_spacer(spacing_tokens.CHART_TITLE_TO_PLOT)

        if chart_id in _TARGETED_PLOT_SLOTS:
            slot_slug = chart_id.lower().replace("-", "")
            render_html_block(
                f'<div class="buip-plot-slot buip-plot-slot--{slot_slug}" aria-hidden="true"></div>'
            )

        render_h = h
        if state == "loading" and fig is None:
            inline_loader(dashboard=dashboard)
            chart_skeleton(height=render_h, dashboard=dashboard, chart_type=skeleton_type)
        elif state == "empty" and fig is None:
            empty_state(
                title="No data matches filters",
                message="Adjust the date range or scope filters to restore chart content.",
                height=render_h,
                dashboard=dashboard,
                semantic_kind="overlay_empty_result" if selection_label else "valid_empty_result",
            )
        elif fig is not None:
            if chart_type in ("scatter_dense", "parcoords", "pairplot"):
                apply_density_marker_defaults(fig)
            normalize_figure_for_display(
                fig,
                dashboard=dashboard,
                chart_type=chart_type,
                role=role,
                is_fullscreen=fs_active,
                breakpoint=bp,
                chart_id=chart_id,
            )
            fig.update_layout(height=render_h)
            if interactive and chart_id and page_key:
                from filters.interaction import chart_widget_key, process_plotly_selection

                widget_key = chart_widget_key(page_key, chart_id, dashboard)
                plotly_state = st.plotly_chart(
                    fig,
                    use_container_width=use_container_width,
                    height=render_h,
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
                    height=render_h,
                    config=PLOTLY_CONFIG,
                )
        else:
            empty_state(
                title="Chart unavailable",
                message="No governed runtime figure was provided for this chart slot.",
                height=render_h,
                dashboard=dashboard,
                semantic_kind="chart_unavailable",
            )

        if caption:
            st.caption(caption)
        if record_count:
            st.caption(record_count)

    render_spacer(CHART_MODULE_BOTTOM)
