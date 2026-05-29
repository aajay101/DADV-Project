"""Phase 4 operational observability, health, recovery, and replay tests."""

from filters.observability import (
    CacheExplorer,
    DependencyGraphExplorer,
    EventReplay,
    RecoveryManager,
    RuntimeAssertionGovernance,
    RuntimeHealthMonitor,
    RuntimeObservabilityManager,
    ScalabilityDiagnostics,
)
from filters.state import TRAFFIC_STATE_DEFAULTS
from filters.transitions import ChartFocusChanged, dispatch


def test_transition_dispatch_emits_observability_and_replay(monkeypatch):
    fake = dict(TRAFFIC_STATE_DEFAULTS)
    monkeypatch.setattr("filters.transitions.st.session_state", fake, raising=False)
    monkeypatch.setattr("filters.observability.st.session_state", fake, raising=False)
    monkeypatch.setattr("filters.performance.st.session_state", fake, raising=False)
    monkeypatch.setattr("data_layer.lazy_charts.st.session_state", fake, raising=False)

    dispatch(ChartFocusChanged(dashboard="traffic", payload={"chart": "T-01", "selected_area": "MG Road"}))

    snapshot = RuntimeObservabilityManager.snapshot()
    assert any(event["kind"] == "transition" for event in snapshot["events"])
    assert EventReplay.summary()["actions"]["ChartFocusChanged"] == 1


def test_dependency_explorer_simulates_affected_charts(monkeypatch):
    fake = dict(TRAFFIC_STATE_DEFAULTS)
    monkeypatch.setattr("filters.observability.st.session_state", fake, raising=False)

    sim = DependencyGraphExplorer.simulate("traffic", ("visual_focus",), ("traffic_selected_area",))

    assert "T-05" in sim["affected_charts"]
    assert "T-03" not in sim["affected_charts"]
    assert "chart_render" in sim["cache_tiers"]


def test_cache_explorer_and_recovery_manager(monkeypatch):
    fake = {
        **TRAFFIC_STATE_DEFAULTS,
        "buip_lazy_traffic_T-05_page_x": object(),
        "buip_lazy_traffic_unknown_page_x": object(),
    }
    monkeypatch.setattr("filters.observability.st.session_state", fake, raising=False)

    assert "buip_lazy_traffic_unknown_page_x" in CacheExplorer.orphaned_lazy_keys()
    recovery = RecoveryManager.recover_chart_cache("traffic", "T-05")

    assert recovery["removed"] == ["buip_lazy_traffic_T-05_page_x"]
    assert "buip_lazy_traffic_T-05_page_x" not in fake
    assert fake["runtime_recovery_events"]


def test_runtime_health_monitor_reports_orphaned_cache(monkeypatch):
    fake = {**TRAFFIC_STATE_DEFAULTS, "buip_lazy_traffic_unknown_page_x": object()}
    monkeypatch.setattr("filters.observability.st.session_state", fake, raising=False)

    health = RuntimeHealthMonitor.inspect()

    assert health["status"] == "warning"
    assert health["warnings"][0]["code"] == "orphaned_lazy_cache"


def test_runtime_assertions_and_scalability_snapshot(monkeypatch):
    fake = {
        **TRAFFIC_STATE_DEFAULTS,
        "last_cache_invalidation_trace": {"source": "test"},
        "runtime_observability_events": [{"kind": "transition"}],
    }
    monkeypatch.setattr("filters.observability.st.session_state", fake, raising=False)

    failures = RuntimeAssertionGovernance.assert_runtime_integrity()
    scale = ScalabilityDiagnostics.snapshot()

    assert failures[0]["code"] == "invalidation_without_transition"
    assert scale["registered_charts"] > 0
