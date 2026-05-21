"""Crisis Overview — production analytics."""

import streamlit as st

from components.page_production import render_production_page
from data_layer.page_bundles import build_aqi_crisis_bundle


def render() -> None:
    bundle = build_aqi_crisis_bundle(st.session_state)
    render_production_page("aqi", "p1_crisis_overview", bundle)
