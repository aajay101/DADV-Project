"""p6_advanced_lab — T-13 investigative · staged radar mount."""

import streamlit as st

from components.page_runtime import render_page
from filters.state import reset_lab_gate, set_active_tab
from filters.transitions import request_rerun


def render() -> None:
    if st.button("← Return to Dashboard Overview", key="traffic_lab_breadcrumb"):
        reset_lab_gate("traffic")
        result = set_active_tab("traffic", 0)
        request_rerun(result, source="traffic_lab_breadcrumb")

    render_page("traffic", "p6_advanced_lab", is_lab=True)
