"""Command Overview — production analytics."""

import streamlit as st

from components.page_production import render_production_page
from data_layer.page_bundles import build_traffic_command_bundle


def render() -> None:
    bundle = build_traffic_command_bundle(st.session_state)
    render_production_page("traffic", "p1_command_overview", bundle)
