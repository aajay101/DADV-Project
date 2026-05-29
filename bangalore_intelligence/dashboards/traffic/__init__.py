"""Traffic Intelligence Dashboard router."""

import importlib

from components.filter_panel import filter_panel
from components.lab_gate import lab_gate
from components.navigation_tab_group import render_tab_navigation
from config.page_config import TRAFFIC_TABS
from filters.state import clear_filter_updating, get_active_tab, init_traffic_state, log_nav_debug

LAB_TAB_INDEX = 5


def _load_page_module(module_name: str):
    return importlib.import_module(f"dashboards.traffic.pages.{module_name}")


def _render_active_page() -> None:
    active_index = get_active_tab("traffic")
    tab_config = TRAFFIC_TABS[active_index]
    page_module_name = tab_config["module"]
    log_nav_debug(
        "traffic",
        "render_active_page",
        active_index=active_index,
        page_module=page_module_name,
        resolved_bundle_key=page_module_name,
    )
    page_module = _load_page_module(page_module_name)

    if tab_config.get("is_lab"):
        lab_gate("traffic", page_module.render)
    else:
        page_module.render()


def traffic_router() -> None:
    """Initialize state, render filters and tabs, route to active page."""
    init_traffic_state()
    filter_panel(dashboard="traffic")
    render_tab_navigation(dashboard="traffic")
    _render_active_page()
    clear_filter_updating("traffic")
