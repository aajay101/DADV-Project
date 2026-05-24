"""Developer-only runtime transition diagnostics."""

from __future__ import annotations

import streamlit as st

from filters.transitions import RERENDER_TRACE_KEY, TRACE_KEY
from filters.performance import performance_snapshot
from filters.state import dashboard_state_snapshot
from filters.interaction_mode import interaction_mode_snapshot
from filters.observability import (
    CacheExplorer,
    DependencyGraphExplorer,
    EventReplay,
    RecoveryManager,
    RuntimeAssertionGovernance,
    RuntimeObservabilityManager,
    ScalabilityDiagnostics,
    operational_snapshot,
)


def render_transition_debug_panel() -> None:
    """Render reducer/runtime trace diagnostics when developer mode is enabled."""
    if not st.session_state.get("developer_mode"):
        return
    enabled = st.toggle(
        "Runtime trace",
        value=bool(st.session_state.get("runtime_debug_enabled", False)),
        key="runtime_debug_enabled",
        help="Show the last reducer transition and rerender decision.",
    )
    if not enabled:
        return
    trace = st.session_state.get(TRACE_KEY) or {}
    rerender = st.session_state.get(RERENDER_TRACE_KEY) or {}
    active_dashboard = st.session_state.get("active_dashboard", "traffic")
    state_snapshot = dashboard_state_snapshot(active_dashboard)
    epoch = st.session_state.get("chart_selection_epoch", 0)
    chart_epochs = st.session_state.get("chart_selection_epochs") or {}
    perf = performance_snapshot()
    operational = operational_snapshot()
    with st.expander("Reducer runtime trace", expanded=False):
        st.caption(f"Widget epoch: {epoch}")
        st.json(
            {
                "transition": trace,
                "rerender": rerender,
                "chart_epochs": chart_epochs,
                "interaction_mode": interaction_mode_snapshot(st.session_state, active_dashboard),
                "investigation_overlay": state_snapshot.get("investigation_overlay"),
                "performance": {
                    "last_invalidation": perf["last_invalidation"],
                    "cache_stats": perf["cache_stats"],
                    "recent_render_traces": perf["render_traces"][-12:],
                },
            }
        )
    with st.expander("Chart dependency graph", expanded=False):
        st.json(perf["dependency_graph"])
    with st.expander("Operational health", expanded=False):
        st.json(operational["health"])
        if st.button("Run runtime assertions", key="runtime_assertions_run"):
            st.json(RuntimeAssertionGovernance.assert_runtime_integrity())
    with st.expander("Transition explorer", expanded=False):
        st.json(RuntimeObservabilityManager.snapshot()["events"][-40:])
    with st.expander("Dependency explorer", expanded=False):
        sim_col1, sim_col2 = st.columns(2)
        with sim_col1:
            sim_dashboard = st.selectbox("Dashboard", ["traffic", "aqi"], key="dep_sim_dashboard")
        with sim_col2:
            sim_domain = st.selectbox(
                "Changed domain",
                ["global_filters", "visual_focus", "chart_local_state", "runtime_state"],
                key="dep_sim_domain",
            )
        st.json(DependencyGraphExplorer.simulate(sim_dashboard, (sim_domain,)))
    with st.expander("Cache explorer", expanded=False):
        st.json(CacheExplorer.snapshot())
        purge_col1, purge_col2 = st.columns(2)
        with purge_col1:
            purge_dashboard = st.selectbox("Purge dashboard", ["traffic", "aqi"], key="cache_purge_dashboard")
        with purge_col2:
            purge_chart = st.text_input("Chart ID", value="", key="cache_purge_chart")
        if st.button("Recover chart cache", key="cache_recover_chart") and purge_chart:
            st.json(RecoveryManager.recover_chart_cache(purge_dashboard, purge_chart))
    with st.expander("Render profiler", expanded=False):
        st.json(operational["render_profiler"])
    with st.expander("Replay and scalability", expanded=False):
        st.json({"replay": EventReplay.summary(), "scalability": ScalabilityDiagnostics.snapshot()})
