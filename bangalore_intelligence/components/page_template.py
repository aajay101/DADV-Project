"""Analytical page fallback shell - no fabricated analytical content."""

import streamlit as st

from components.hero_section import hero_section
from components.insight_card import insight_card
from components.lab_header import lab_header
from components.layout.page_zones import command_zone_close, command_zone_open, context_zone
from components.nav_card import nav_card
from config.page_config import AQI_TABS, TRAFFIC_TABS


def render_analytical_page(
    dashboard: str,
    page_key: str,
    is_lab: bool = False,
) -> None:
    """Render a governed-data fallback when no bundle builder exists."""
    tabs = TRAFFIC_TABS if dashboard == "traffic" else AQI_TABS
    tab = next((t for t in tabs if t["module"] == page_key), tabs[0])

    if is_lab:
        lab_header(dashboard=dashboard)

    command_zone_open(dashboard)
    hero_section(
        title=tab["title"],
        subtitle=tab["subtitle"],
        severity_badge=None,
        dashboard=dashboard,
        page_indicator=tab["subtitle"],
    )
    command_zone_close()

    st.warning(
        "This page does not have a governed runtime bundle available. "
        "No analytical content was rendered without governed runtime data."
    )

    context_zone(dashboard)
    insight_card(
        heading="What This Means" if dashboard == "aqi" else "Operational Interpretation",
        body=(
            "A governed runtime bundle is required before analytical interpretation can be shown. "
            "This fallback intentionally avoids fabricated data."
        ),
        severity="neutral",
        collapsible=True,
        default_expanded=False,
        dashboard=dashboard,
    )

    if tab["index"] < len(tabs) - 1:
        next_tab = tabs[tab["index"] + 1]
        nav_card(
            label="Continue analysis" if dashboard == "aqi" else "Investigate further",
            destination_title=next_tab["title"],
            destination_description=next_tab["subtitle"],
            tab_index=next_tab["index"],
            dashboard=dashboard,
        )
