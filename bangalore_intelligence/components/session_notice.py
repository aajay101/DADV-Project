"""Long-session and data-freshness notices — presentation only."""

import time

import streamlit as st

from config.data_config import LONG_SESSION_THRESHOLD_SECONDS, STALE_THRESHOLD_SECONDS
from utils.session_health import check_data_freshness, should_show_long_session_notice


def render_long_session_notice(dashboard: str | None = None) -> None:
    if st.session_state.get("long_session_notice_dismissed"):
        return
    start = st.session_state.get("session_start_time")
    if not should_show_long_session_notice(
        time.time(),
        start,
        dismissed=False,
        threshold_seconds=LONG_SESSION_THRESHOLD_SECONDS,
    ):
        return

    st.info(
        "Extended review session (90+ minutes). Refresh data before final decisions.",
    )
    if st.button("Dismiss notice", key="buip_dismiss_long_session"):
        st.session_state["long_session_notice_dismissed"] = True
        st.rerun()


def render_data_freshness_strip(dashboard: str) -> None:
    from data_layer.loaders import refresh_dashboard_data

    prefix = "traffic" if dashboard == "traffic" else "aqi"
    loaded_at = st.session_state.get(f"{prefix}_data_loaded_at")
    stale = check_data_freshness(loaded_at, STALE_THRESHOLD_SECONDS)
    st.session_state[f"{prefix}_data_stale"] = stale
    if not stale:
        return

    c1, c2 = st.columns([4, 1])
    with c1:
        st.warning(
            "Cached dataset may be stale. Refresh before operational sign-off.",
            icon="🔄",
        )
    with c2:
        if st.button("Refresh data", key=f"{prefix}_refresh_data", use_container_width=True):
            refresh_dashboard_data(dashboard)
            st.session_state[f"{prefix}_data_stale"] = False
            st.rerun()
