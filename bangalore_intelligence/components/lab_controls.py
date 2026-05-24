"""Advanced Lab control panels — orchestration only, not chart rendering."""

from __future__ import annotations

import streamlit as st

from config.data_config import AQI_CATEGORIES, TRAFFIC_AREAS
from config.spacing import CHART_FILTER_GAP
from config.theme import SPACING_MD, get_dashboard_tokens
from filters.transitions import ChartLocalStateChanged, dispatch, request_rerun
from utils.ui_blocks import render_micro_heading

MAX_RADAR_OVERLAYS = 4


def _enforce_radar_limit(selected: list[str]) -> list[str]:
    if len(selected) > MAX_RADAR_OVERLAYS:
        st.warning(f"Radar overlay limit is {MAX_RADAR_OVERLAYS}. Extra selections were not applied.")
        return selected[:MAX_RADAR_OVERLAYS]
    return selected


def render_traffic_lab_controls(
    available_areas: list[str],
    top_stress_areas: list[str],
    baseline_areas: list[str],
) -> list[str]:
    """Render T-13 view toggle and optional radar overlay controls."""
    tokens = get_dashboard_tokens("traffic")
    render_micro_heading(
        "T-13 stress view",
        color=tokens["text_muted"],
        margin_bottom=CHART_FILTER_GAP,
    )

    view_options = ["heatmap", "radar"]
    view_labels = {"heatmap": "Area stress heatmap", "radar": "Radar comparison"}
    current_view = st.session_state.get("traffic_lab_t13_view", "heatmap")
    if current_view not in view_options:
        current_view = "heatmap"

    choice = st.radio(
        "T-13 display mode",
        options=view_options,
        index=view_options.index(current_view),
        format_func=lambda v: view_labels[v],
        key="traffic_lab_t13_view_radio",
        horizontal=True,
    )
    if choice != st.session_state.get("traffic_lab_t13_view"):
        result = dispatch(ChartLocalStateChanged(dashboard="traffic", updates={"traffic_lab_t13_view": choice}))
        request_rerun(result, source="traffic_lab_t13_view")

    if choice != "radar":
        st.caption("Heatmap is the default lab view. Switch to radar for overlay comparison.")
        return list(st.session_state.get("traffic_radar_visible_areas") or [])

    render_micro_heading(
        "RADAR OVERLAY CONTROL",
        color=tokens["text_muted"],
        margin_top=SPACING_MD,
        margin_bottom=CHART_FILTER_GAP,
    )

    current = list(st.session_state.get("traffic_radar_visible_areas") or [])
    options = available_areas or list(TRAFFIC_AREAS)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("Top 3 Stress", key="lab_radar_top3", use_container_width=True):
            result = dispatch(
                ChartLocalStateChanged(
                    dashboard="traffic",
                    updates={
                        "traffic_radar_visible_areas": _enforce_radar_limit(
                            [a for a in top_stress_areas if a in options][:3]
                        ),
                        "traffic_radar_comparison_mode": "top_stress",
                    },
                )
            )
            request_rerun(result, source="lab_radar_top3")
    with c2:
        if st.button("Baseline 3", key="lab_radar_baseline3", use_container_width=True):
            result = dispatch(
                ChartLocalStateChanged(
                    dashboard="traffic",
                    updates={
                        "traffic_radar_visible_areas": _enforce_radar_limit(
                            [a for a in baseline_areas if a in options][:3]
                        ),
                        "traffic_radar_comparison_mode": "baseline",
                    },
                )
            )
            request_rerun(result, source="lab_radar_baseline3")
    with c3:
        if st.button("Clear All", key="lab_radar_clear", use_container_width=True):
            result = dispatch(
                ChartLocalStateChanged(
                    dashboard="traffic",
                    updates={"traffic_radar_visible_areas": [], "traffic_radar_comparison_mode": None},
                )
            )
            request_rerun(result, source="lab_radar_clear")
    with c4:
        st.caption(f"Overlay limit: {MAX_RADAR_OVERLAYS}")

    selected = st.multiselect(
        "Visible areas",
        options=options,
        default=current,
        key="traffic_radar_visible_areas",
        placeholder="Empty = top stress overlays from chart config",
    )
    if len(selected) > MAX_RADAR_OVERLAYS:
        dispatch(
            ChartLocalStateChanged(
                dashboard="traffic",
                updates={"traffic_radar_visible_areas": _enforce_radar_limit(selected)},
            )
        )

    return list(st.session_state.get("traffic_radar_visible_areas") or [])


def render_aqi_lab_controls(categories: list[str] | None = None) -> list[str]:
    """Render A-15 AQI category toggles; return selected categories."""
    tokens = get_dashboard_tokens("aqi")
    render_micro_heading(
        "A-15 PAIRPLOT PM2.5 CATEGORY CONTROL",
        color=tokens["text_muted"],
        margin_bottom=CHART_FILTER_GAP,
    )

    options = categories or list(AQI_CATEGORIES)
    current = list(st.session_state.get("aqi_pairplot_visible_categories") or [])

    c1, c2 = st.columns(2)
    with c1:
        if st.button("All categories", key="lab_aqi_all_cats", use_container_width=True):
            result = dispatch(
                ChartLocalStateChanged(
                    dashboard="aqi",
                    updates={"aqi_pairplot_visible_categories": [], "aqi_pairplot_category_preset": "all"},
                )
            )
            request_rerun(result, source="lab_aqi_all_cats")
    with c2:
        if st.button("Poor + Very Poor + Severe", key="lab_aqi_high_cats", use_container_width=True):
            preset = ["Poor", "Very Poor", "Severe"]
            result = dispatch(
                ChartLocalStateChanged(
                    dashboard="aqi",
                    updates={
                        "aqi_pairplot_visible_categories": [c for c in preset if c in options],
                        "aqi_pairplot_category_preset": "high_pollution",
                    },
                )
            )
            request_rerun(result, source="lab_aqi_high_cats")

    selected = st.multiselect(
        "Visible PM2.5 categories",
        options=options,
        default=current,
        key="aqi_pairplot_visible_categories",
        placeholder="Empty = all categories in pairplot",
    )
    return list(selected)
