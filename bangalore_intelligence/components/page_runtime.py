"""Page runtime helper — bundle resolution from session state."""

import streamlit as st

from components.page_production import render_production_page
from components.page_template import render_analytical_page
from data_layer.page_bundles import get_bundle_builder
from filters.state import log_nav_debug
from utils.validators import DataValidationError


def render_page(dashboard: str, page_key: str, is_lab: bool = False) -> None:
    log_nav_debug(dashboard, "render_page", page_key=page_key, is_lab=is_lab)
    builder = get_bundle_builder(page_key, dashboard)
    if builder is None:
        render_analytical_page(dashboard=dashboard, page_key=page_key, is_lab=is_lab)
        return
    state = dict(st.session_state)
    try:
        bundle = builder(state)
    except DataValidationError as exc:
        st.error(f"Data validation failed: {exc}")
        st.caption("Restore raw/processed datasets or reset filters, then reload the dashboard.")
        return
    render_production_page(dashboard, page_key, bundle, is_lab=is_lab)
