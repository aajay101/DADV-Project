"""Advanced Lab — A-15 pairplot · A-13 support · A-14 collapsed."""

import streamlit as st

from components.page_runtime import render_page
from filters.state import reset_lab_gate, set_active_tab


def render() -> None:
    if st.button("← Return to Dashboard Overview", key="aqi_lab_breadcrumb"):
        reset_lab_gate("aqi")
        set_active_tab("aqi", 0)
        st.rerun()

    render_page("aqi", "p6_advanced_lab", is_lab=True)
