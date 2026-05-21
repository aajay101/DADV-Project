"""AQI Environmental Intelligence Dashboard router."""

import importlib

from components.filter_panel import filter_panel
from components.lab_gate import lab_gate
from components.navigation_tab_group import render_tab_navigation
from config.page_config import AQI_TABS
from filters.state import get_active_tab, init_aqi_state

LAB_TAB_INDEX = 5


def _load_page_module(module_name: str):
    return importlib.import_module(f"dashboards.aqi.pages.{module_name}")


def _render_active_page() -> None:
    active_index = get_active_tab("aqi")
    tab_config = AQI_TABS[active_index]
    page_module = _load_page_module(tab_config["module"])

    if tab_config.get("is_lab"):
        lab_gate("aqi", page_module.render)
    else:
        page_module.render()


def aqi_router() -> None:
    """Initialize state, render filters and tabs, route to active page."""
    init_aqi_state()
    filter_panel(dashboard="aqi")
    render_tab_navigation(dashboard="aqi")
    _render_active_page()
