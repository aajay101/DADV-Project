"""Temporal Patterns — production analytics (A-02)."""

import streamlit as st

from components.page_production import render_production_page
from data_layer.page_bundles import build_aqi_temporal_bundle


def render() -> None:
    bundle = build_aqi_temporal_bundle(st.session_state)
    render_production_page("aqi", "p2_temporal_patterns", bundle)
