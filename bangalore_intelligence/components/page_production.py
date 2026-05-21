"""Production page renderer — uses data bundles, presentation-only layout."""

import streamlit as st

from components.chart_container import chart_container
from components.collapsible_section import collapsible_section
from components.hero_section import hero_section
from components.insight_card import insight_card
from components.lab_header import lab_header
from components.layout.page_zones import (
    command_zone_close,
    command_zone_open,
    context_zone,
    investigation_zone_close,
    investigation_zone_open,
)
from components.layout.responsive import get_chart_heights, get_column_split
from components.metric_strip import metric_strip
from components.nav_card import nav_card
from components.section_header import section_header
from config.page_config import AQI_TABS, TRAFFIC_TABS
from components.detail_panel import detail_panel
from filters.interaction import render_investigation_chrome


def _interaction_chart_kwargs(cfg: dict, page_key: str) -> dict:
    return {
        "chart_id": cfg.get("chart_id"),
        "interactive": bool(cfg.get("interactive")),
        "page_key": page_key,
        "interaction_meta": cfg.get("interaction_meta"),
        "selection_mode": cfg.get("selection_mode", "points"),
    }


def render_production_page(
    dashboard: str,
    page_key: str,
    bundle: dict,
    is_lab: bool = False,
) -> None:
    tabs = TRAFFIC_TABS if dashboard == "traffic" else AQI_TABS
    tab = next((t for t in tabs if t["module"] == page_key), tabs[0])

    if is_lab:
        lab_header(dashboard=dashboard)

    if bundle.get("empty"):
        st.warning("No records match the current filter selection. Adjust filters to restore analytics.")
        return

    command_zone_open(dashboard)
    hero_section(
        title=tab["title"],
        subtitle=tab["subtitle"],
        severity_badge=bundle.get("severity_badge"),
        dashboard=dashboard,
    )
    metric_strip(bundle.get("primary_kpis", []), dashboard=dashboard, tier="primary")
    if bundle.get("secondary_kpis"):
        metric_strip(bundle.get("secondary_kpis", []), dashboard=dashboard, tier="secondary")
    command_zone_close()

    investigation_zone_open(dashboard)
    with st.container(border=True):
        section_header(
            "Analytical Modules",
            subtitle="Hero investigation · Supporting context",
            zone="investigation",
            dashboard=dashboard,
        )

        hero_cfg = bundle.get("hero_chart", {})
        support_cfg = bundle.get("support_chart", {})
        hero_col, support_col = st.columns(get_column_split("hero_support"))

        inv_meta = render_investigation_chrome(bundle, dashboard, page_key)
        sel = inv_meta.get("selection_label")
        hero_state = "loading" if hero_cfg.get("lazy") and hero_cfg.get("fig") is None else (
            "default" if hero_cfg.get("fig") is not None else "empty"
        )
        chart_kw = _interaction_chart_kwargs

        with hero_col:
            chart_container(
                fig=hero_cfg.get("fig"),
                title=hero_cfg.get("title", ""),
                subtitle=hero_cfg.get("subtitle"),
                caption=hero_cfg.get("caption"),
                height=get_chart_heights("hero"),
                role="hero",
                dashboard=dashboard,
                fullscreen_key=hero_cfg.get("fullscreen_key"),
                record_count=bundle.get("record_count"),
                selection_label=sel,
                state=hero_state,
                **chart_kw(hero_cfg, page_key),
            )

        with support_col:
            support_fig = support_cfg.get("fig")
            chart_container(
                fig=support_fig,
                title=support_cfg.get("title", ""),
                subtitle=support_cfg.get("subtitle"),
                caption=support_cfg.get("caption"),
                height=get_chart_heights("support"),
                role="supporting",
                dashboard=dashboard,
                record_count=bundle.get("record_count"),
                selection_label=sel,
                state="default" if support_fig is not None else "empty",
                **chart_kw(support_cfg, page_key),
            )

        detail = bundle.get("detail_panel")
        if detail:
            detail_panel(
                title=detail.get("title", "Selection"),
                metrics=detail.get("metrics", []),
                notes=detail.get("notes"),
                visible=True,
                dashboard=detail.get("dashboard", dashboard),
                state="selected",
            )

        collapsed_cfg = bundle.get("collapsed_chart") or {}
        collapsed_fig = collapsed_cfg.get("fig")

        def _render_collapsed():
            chart_container(
                fig=collapsed_fig,
                title=collapsed_cfg.get("title", "Secondary analytical module"),
                subtitle=collapsed_cfg.get("subtitle"),
                caption=collapsed_cfg.get("caption"),
                height=get_chart_heights("support"),
                role="supporting",
                dashboard=dashboard,
                record_count=bundle.get("record_count"),
                selection_label=sel,
                state="default" if collapsed_fig is not None else "empty",
                **_interaction_chart_kwargs(collapsed_cfg, page_key),
            )

        collapsible_section(
            label=collapsed_cfg.get("label", "▶ SECONDARY MODULE · Progressive disclosure"),
            key=f"{page_key}_collapsed",
            default_expanded=False,
            content_fn=_render_collapsed,
            dashboard=dashboard,
        )
    investigation_zone_close()

    context_zone(dashboard)
    insight_card(
        heading="Operational Interpretation",
        body=bundle.get("insight", ""),
        severity=bundle.get("insight_severity", "neutral"),
        collapsible=True,
        default_expanded=False,
        dashboard=dashboard,
    )

    nav_tab = bundle.get("nav_tab")
    if nav_tab is not None:
        nav_card(
            label="INVESTIGATE FURTHER",
            destination_title=bundle.get("nav_title", ""),
            destination_description=bundle.get("nav_desc", ""),
            tab_index=nav_tab,
            dashboard=dashboard,
        )
