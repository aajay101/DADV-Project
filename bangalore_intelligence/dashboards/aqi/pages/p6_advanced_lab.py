"""Analytical Workspace — A-15 pairplot · A-13 support · A-14 collapsed."""

import streamlit as st

from components.page_runtime import render_page
from filters.state import reset_lab_gate, set_active_tab
from filters.transitions import request_rerun


def render() -> None:
    if st.button("← Return to Air Quality Overview", key="aqi_lab_breadcrumb"):
        reset_lab_gate("aqi")
        result = set_active_tab("aqi", 0)
        request_rerun(result, source="aqi_lab_breadcrumb")

    render_page("aqi", "p6_advanced_lab", is_lab=True)
