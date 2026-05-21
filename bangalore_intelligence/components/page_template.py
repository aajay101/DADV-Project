"""Analytical page shell — zones, hierarchy, mock content (presentation only)."""

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
from config.mock_content import get_page_mock
from config.page_config import AQI_TABS, TRAFFIC_TABS


def render_analytical_page(
    dashboard: str,
    page_key: str,
    is_lab: bool = False,
) -> None:
    """Render full page zones with mock analytical content."""
    tabs = TRAFFIC_TABS if dashboard == "traffic" else AQI_TABS
    tab = next((t for t in tabs if t["module"] == page_key), tabs[0])
    mock = get_page_mock(dashboard, page_key)

    if is_lab:
        lab_header(dashboard=dashboard)

    # ── Command Zone ─────────────────────────────────────────────────────
    command_zone_open(dashboard)
    hero_section(
        title=tab["title"],
        subtitle=tab["subtitle"],
        severity_badge=mock.get("severity_badge"),
        dashboard=dashboard,
        page_indicator=tab["subtitle"],
    )
    metric_strip(mock.get("primary_kpis", []), dashboard=dashboard, tier="primary")
    if mock.get("secondary_kpis"):
        metric_strip(mock.get("secondary_kpis", []), dashboard=dashboard, tier="secondary")
    command_zone_close()

    # ── Investigation Zone ─────────────────────────────────────────────
    investigation_zone_open(dashboard)
    section_header(
        "Analytical Modules",
        subtitle="Hero dominance · Supporting context de-emphasized",
        zone="investigation",
        dashboard=dashboard,
    )

    hero_cfg = mock.get("hero_chart", {})
    support_cfg = mock.get("support_chart", {})
    cols = get_column_split("hero_support")
    hero_col, support_col = st.columns(cols)

    with hero_col:
        chart_container(
            fig=None,
            title=hero_cfg.get("title", "Hero Chart"),
            subtitle=hero_cfg.get("subtitle"),
            caption="Primary analytical finding placeholder",
            height=get_chart_heights("hero"),
            role="hero",
            dashboard=dashboard,
            fullscreen_key=hero_cfg.get("fullscreen_key"),
            record_count="n = 8,936" if dashboard == "traffic" else "n = 1,095",
        )

    with support_col:
        chart_container(
            fig=None,
            title=support_cfg.get("title", "Supporting Chart"),
            subtitle=support_cfg.get("subtitle"),
            caption="Supporting context placeholder",
            height=get_chart_heights("support"),
            role="supporting",
            dashboard=dashboard,
            fullscreen_key=support_cfg.get("fullscreen_key"),
            record_count="n = 8,936" if dashboard == "traffic" else "n = 1,095",
        )

    collapsible_section(
        label="▶ SECONDARY MODULE · Progressive disclosure",
        key=f"{page_key}_collapsed",
        default_expanded=False,
        content_fn=lambda: chart_container(
            fig=None,
            title="Collapsible analytical slot",
            subtitle="Lazy-rendered in Phase 5+",
            role="supporting",
            dashboard=dashboard,
            height=get_chart_heights("compact"),
        ),
    )
    investigation_zone_close()

    # ── Context Zone ─────────────────────────────────────────────────────
    context_zone(dashboard)
    insight_card(
        heading="Operational Interpretation",
        body=mock.get("insight", "Interpretation placeholder."),
        severity="neutral",
        collapsible=True,
        default_expanded=False,
        dashboard=dashboard,
    )

    nav_tab = mock.get("nav_tab")
    if nav_tab is not None:
        nav_card(
            label="INVESTIGATE FURTHER",
            destination_title=mock.get("nav_title", "Next Page"),
            destination_description=mock.get("nav_desc", ""),
            tab_index=nav_tab,
            dashboard=dashboard,
        )
