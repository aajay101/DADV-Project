"""Long-session and data-freshness notices — presentation only."""

import time

import streamlit as st

from config.data_config import LONG_SESSION_THRESHOLD_SECONDS, STALE_THRESHOLD_SECONDS
from utils.session_health import check_data_freshness, should_show_long_session_notice


def _build_page_bundle(dashboard: str) -> tuple[dict | None, str, str]:
    from config.page_config import AQI_TABS, TRAFFIC_TABS
    from data_layer.page_bundles import get_bundle_builder
    from filters.state import get_active_tab

    tabs = TRAFFIC_TABS if dashboard == "traffic" else AQI_TABS
    tab = tabs[get_active_tab(dashboard)]
    page_key = tab["module"]
    builder = get_bundle_builder(page_key, dashboard)
    if builder is None:
        return None, page_key, tab["title"]
    try:
        return builder(dict(st.session_state)), page_key, tab["title"]
    except Exception as exc:
        st.session_state["last_export_status"] = str(exc)
        return None, page_key, tab["title"]


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

    dash = dashboard or st.session_state.get("active_dashboard", "traffic")
    prefix = "traffic" if dash == "traffic" else "aqi"
    exec_key = f"{prefix}_session_exec_pdf_bytes"

    st.info(
        "Extended review session (90+ minutes). Consider exporting a report snapshot "
        "or refreshing data before final decisions.",
        icon="⏱",
    )
    c1, c2 = st.columns([2, 1])
    with c1:
        if st.button("Export Summary", key="buip_session_export_summary"):
            from utils.export import ExportError, generate_executive_summary
            from utils.formatters import filter_snapshot_from_state

            st.session_state["export_in_progress"] = True
            with st.spinner("Generating executive summary…"):
                filters = filter_snapshot_from_state(st.session_state, dash)
                bundle, _, page_title = _build_page_bundle(dash)
                if bundle and not bundle.get("empty"):
                    try:
                        st.session_state[exec_key] = generate_executive_summary(
                            bundle, filters, dashboard=dash, page_title=page_title
                        )
                        st.session_state["last_export_status"] = "Session summary ready"
                    except ExportError as exc:
                        st.session_state["last_export_status"] = str(exc)
                else:
                    st.session_state["last_export_status"] = "No data to export"
            st.session_state["export_in_progress"] = False
            st.rerun()
    with c2:
        if st.button("Dismiss notice", key="buip_dismiss_long_session"):
            st.session_state["long_session_notice_dismissed"] = True
            st.rerun()

    if exec_key in st.session_state:
        from utils.export import build_export_filename, dashboard_code

        st.download_button(
            "Download executive summary",
            data=st.session_state[exec_key],
            file_name=build_export_filename(dashboard_code(dash), "SESSION_EXEC", extension="pdf"),
            mime="application/pdf",
            key="buip_download_session_exec",
        )


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


def render_runtime_provenance_panel(dashboard: str) -> None:
    """Compact governed-source disclosure for operational auditability."""
    from data_layer.loaders import get_runtime_provenance

    try:
        p = get_runtime_provenance(dashboard)
    except Exception as exc:
        st.error(f"Governance status unavailable: {exc}")
        return
    date_range = p.get("date_range") or {}
    date_label = f"{date_range.get('min', '?')} to {date_range.get('max', '?')}"
    with st.expander("RUNTIME DATA SOURCE", expanded=False):
        st.caption("KPIs and charts use the governed dataset after global filters.")
        st.caption(f"Governance status: {p.get('governance_status')}")
        st.caption(f"Pipeline: {p.get('source')}")
        st.caption(f"Rows (processed): {p.get('row_count'):,}")
        st.caption(f"Date range: {date_label}")
        st.caption(f"Fingerprint: {p.get('fingerprint')}")
        st.caption(f"Last refresh: {p.get('last_refresh')}")
