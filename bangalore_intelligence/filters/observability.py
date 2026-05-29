"""Operational observability, health, recovery, and replay tooling."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import time
from typing import Any, Literal

import streamlit as st

from filters.performance import CHART_DEPENDENCY_REGISTRY

Severity = Literal["info", "warning", "error", "critical"]
EventKind = Literal[
    "transition",
    "invalidation",
    "rerender",
    "render",
    "cache",
    "dependency",
    "health",
    "recovery",
    "assertion",
    "failure",
]

OBS_EVENTS_KEY = "runtime_observability_events"
OBS_WARNINGS_KEY = "runtime_observability_warnings"
OBS_REPLAY_KEY = "runtime_replay_log"
OBS_HEALTH_KEY = "runtime_health_snapshot"
OBS_RECOVERY_KEY = "runtime_recovery_events"
OBS_ASSERTION_KEY = "runtime_assertion_failures"
OBS_LIMIT = 250


@dataclass(frozen=True)
class RuntimeEvent:
    kind: EventKind
    severity: Severity
    source: str
    message: str
    payload: dict[str, Any]
    timestamp: float


class RuntimeObservabilityManager:
    """Central append-only runtime telemetry manager."""

    @staticmethod
    def emit(
        kind: EventKind,
        *,
        source: str,
        message: str,
        severity: Severity = "info",
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        event = RuntimeEvent(
            kind=kind,
            severity=severity,
            source=source,
            message=message,
            payload=payload or {},
            timestamp=time.time(),
        )
        item = asdict(event)
        events = list(st.session_state.get(OBS_EVENTS_KEY) or [])
        events.append(item)
        st.session_state[OBS_EVENTS_KEY] = events[-OBS_LIMIT:]
        if severity in ("warning", "error", "critical"):
            warnings = list(st.session_state.get(OBS_WARNINGS_KEY) or [])
            warnings.append(item)
            st.session_state[OBS_WARNINGS_KEY] = warnings[-80:]
        return item

    @staticmethod
    def record_transition(trace: dict[str, Any]) -> None:
        RuntimeObservabilityManager.emit(
            "transition",
            source=trace.get("action_type") or "unknown_action",
            message=f"{trace.get('action_type')} via {trace.get('reducer')}",
            payload=trace,
        )
        replay = list(st.session_state.get(OBS_REPLAY_KEY) or [])
        replay.append({"kind": "transition", "trace": trace, "timestamp": time.time()})
        st.session_state[OBS_REPLAY_KEY] = replay[-OBS_LIMIT:]

    @staticmethod
    def record_invalidation(trace: dict[str, Any]) -> None:
        RuntimeObservabilityManager.emit(
            "invalidation",
            source=trace.get("source") or "runtime",
            message="Cache invalidation planned",
            payload=trace,
        )

    @staticmethod
    def record_rerender(trace: dict[str, Any]) -> None:
        RuntimeObservabilityManager.emit(
            "rerender",
            source=trace.get("source") or "runtime",
            message="Rerender requested",
            payload=trace,
        )

    @staticmethod
    def record_render(trace: dict[str, Any]) -> None:
        RuntimeObservabilityManager.emit(
            "render",
            source=trace.get("chart_id") or "chart",
            message=f"Chart render {'hit' if trace.get('cache_hit') else 'miss'}",
            payload=trace,
        )

    @staticmethod
    def record_failure(source: str, exc: Exception, payload: dict[str, Any] | None = None) -> None:
        RuntimeObservabilityManager.emit(
            "failure",
            source=source,
            message=str(exc),
            severity="error",
            payload=payload or {},
        )

    @staticmethod
    def snapshot() -> dict[str, Any]:
        return {
            "events": st.session_state.get(OBS_EVENTS_KEY) or [],
            "warnings": st.session_state.get(OBS_WARNINGS_KEY) or [],
            "replay_log": st.session_state.get(OBS_REPLAY_KEY) or [],
            "health": st.session_state.get(OBS_HEALTH_KEY) or {},
            "recoveries": st.session_state.get(OBS_RECOVERY_KEY) or [],
            "assertions": st.session_state.get(OBS_ASSERTION_KEY) or [],
        }


class RenderProfiler:
    """Summarize render pressure and expensive charts from recorded traces."""

    @staticmethod
    def profile() -> dict[str, Any]:
        stats = dict(st.session_state.get("performance_cache_stats") or {})
        ranking: list[dict[str, Any]] = []
        for chart_id, item in stats.items():
            renders = int(item.get("renders") or 0)
            total_ms = float(item.get("total_ms") or 0.0)
            ranking.append(
                {
                    "chart_id": chart_id,
                    "renders": renders,
                    "hits": int(item.get("hits") or 0),
                    "misses": int(item.get("misses") or 0),
                    "total_ms": total_ms,
                    "avg_ms": total_ms / renders if renders else 0.0,
                }
            )
        ranking.sort(key=lambda row: row["total_ms"], reverse=True)
        return {
            "slowest_charts": ranking[:10],
            "total_renders": sum(row["renders"] for row in ranking),
            "total_misses": sum(row["misses"] for row in ranking),
            "total_hits": sum(row["hits"] for row in ranking),
        }


class RuntimeHealthMonitor:
    """Runtime self-monitoring and anomaly classification."""

    @staticmethod
    def inspect() -> dict[str, Any]:
        warnings: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []
        if not CHART_DEPENDENCY_REGISTRY:
            errors.append({"code": "dependency_registry_empty", "message": "No chart dependencies registered."})
        for chart_id, spec in CHART_DEPENDENCY_REGISTRY.items():
            if spec.chart_id != chart_id:
                errors.append({"code": "chart_id_mismatch", "chart_id": chart_id, "spec_chart_id": spec.chart_id})
            if spec.dashboard not in ("traffic", "aqi"):
                errors.append({"code": "invalid_dashboard", "chart_id": chart_id, "dashboard": spec.dashboard})
        orphaned = CacheExplorer.orphaned_lazy_keys()
        if orphaned:
            warnings.append({"code": "orphaned_lazy_cache", "keys": orphaned[:20], "count": len(orphaned)})
        profiler = RenderProfiler.profile()
        for row in profiler["slowest_charts"][:3]:
            if row["avg_ms"] > 800:
                warnings.append({"code": "slow_chart", **row})
        status = "critical" if errors else "warning" if warnings else "healthy"
        snapshot = {
            "status": status,
            "warnings": warnings,
            "errors": errors,
            "profiler": profiler,
            "timestamp": time.time(),
        }
        st.session_state[OBS_HEALTH_KEY] = snapshot
        RuntimeObservabilityManager.emit(
            "health",
            source="RuntimeHealthMonitor",
            message=f"Runtime health: {status}",
            severity="error" if errors else "warning" if warnings else "info",
            payload=snapshot,
        )
        return snapshot


class RecoveryManager:
    """Scoped operational recovery routines."""

    @staticmethod
    def recover_chart_cache(dashboard: str, chart_id: str) -> dict[str, Any]:
        prefix = f"buip_lazy_{dashboard}_{chart_id}_"
        removed = []
        for key in list(st.session_state.keys()):
            if isinstance(key, str) and key.startswith(prefix):
                removed.append(key)
                del st.session_state[key]
        event = {"strategy": "chart_cache_recovery", "dashboard": dashboard, "chart_id": chart_id, "removed": removed}
        RecoveryManager._record(event)
        return event

    @staticmethod
    def recover_dashboard_lazy_cache(dashboard: str) -> dict[str, Any]:
        prefix = f"buip_lazy_{dashboard}_"
        removed = []
        for key in list(st.session_state.keys()):
            if isinstance(key, str) and key.startswith(prefix):
                removed.append(key)
                del st.session_state[key]
        event = {"strategy": "dashboard_lazy_cache_recovery", "dashboard": dashboard, "removed_count": len(removed)}
        RecoveryManager._record(event)
        return event

    @staticmethod
    def reset_observability() -> dict[str, Any]:
        for key in (OBS_EVENTS_KEY, OBS_WARNINGS_KEY, OBS_REPLAY_KEY, OBS_HEALTH_KEY, OBS_ASSERTION_KEY):
            st.session_state[key] = [] if key != OBS_HEALTH_KEY else {}
        event = {"strategy": "observability_reset"}
        RecoveryManager._record(event)
        return event

    @staticmethod
    def _record(event: dict[str, Any]) -> None:
        event = {**event, "timestamp": time.time()}
        events = list(st.session_state.get(OBS_RECOVERY_KEY) or [])
        events.append(event)
        st.session_state[OBS_RECOVERY_KEY] = events[-80:]
        RuntimeObservabilityManager.emit("recovery", source="RecoveryManager", message=event["strategy"], payload=event)


class CacheExplorer:
    """Cache diagnostics and selective cache metadata."""

    @staticmethod
    def lazy_keys(dashboard: str | None = None) -> list[str]:
        prefix = f"buip_lazy_{dashboard}_" if dashboard else "buip_lazy_"
        return sorted(key for key in st.session_state.keys() if isinstance(key, str) and key.startswith(prefix))

    @staticmethod
    def orphaned_lazy_keys() -> list[str]:
        known = set(CHART_DEPENDENCY_REGISTRY)
        orphaned: list[str] = []
        for key in CacheExplorer.lazy_keys():
            parts = key.split("_")
            chart = next((part for part in parts if part in known), None)
            if chart is None:
                orphaned.append(key)
        return orphaned

    @staticmethod
    def snapshot() -> dict[str, Any]:
        keys = CacheExplorer.lazy_keys()
        return {
            "lazy_cache_count": len(keys),
            "lazy_cache_keys": keys[:120],
            "orphaned_lazy_keys": CacheExplorer.orphaned_lazy_keys(),
            "cache_stats": st.session_state.get("performance_cache_stats") or {},
            "last_invalidation": st.session_state.get("last_cache_invalidation_trace"),
        }


class DependencyGraphExplorer:
    """Dependency graph inspection and invalidation simulation."""

    @staticmethod
    def graph() -> dict[str, Any]:
        return {chart_id: asdict(spec) for chart_id, spec in CHART_DEPENDENCY_REGISTRY.items()}

    @staticmethod
    def simulate(dashboard: str, changed_domains: tuple[str, ...], changed_keys: tuple[str, ...] = ()) -> dict[str, Any]:
        from filters.performance import affected_charts_for_transition, cache_tiers_for_transition

        return {
            "dashboard": dashboard,
            "changed_domains": list(changed_domains),
            "changed_keys": list(changed_keys),
            "affected_charts": list(
                affected_charts_for_transition("traffic" if dashboard == "traffic" else "aqi", changed_domains, changed_keys)
            ),
            "cache_tiers": list(cache_tiers_for_transition(changed_domains)),
        }


class RuntimeAssertionGovernance:
    """Developer-mode runtime assertions."""

    @staticmethod
    def assert_runtime_integrity() -> list[dict[str, Any]]:
        failures: list[dict[str, Any]] = []
        if st.session_state.get("last_cache_invalidation_trace") and not st.session_state.get("last_transition_trace"):
            failures.append({"code": "invalidation_without_transition"})
        if st.session_state.get("last_rerender_trace") and not (
            st.session_state.get("last_transition_trace") or st.session_state.get("last_rerender_trace", {}).get("deferred_transition")
        ):
            failures.append({"code": "rerender_without_trace"})
        orphaned = CacheExplorer.orphaned_lazy_keys()
        if orphaned:
            failures.append({"code": "orphaned_lazy_cache", "count": len(orphaned)})
        from filters.interaction_mode import assert_valid_interaction_mode

        for dashboard in ("traffic", "aqi"):
            try:
                assert_valid_interaction_mode(st.session_state, dashboard)
            except RuntimeError as exc:
                failures.append({"code": "dual_analytical_scope_authority", "dashboard": dashboard, "message": str(exc)})
        st.session_state[OBS_ASSERTION_KEY] = failures
        for failure in failures:
            RuntimeObservabilityManager.emit(
                "assertion",
                source="RuntimeAssertionGovernance",
                message=failure["code"],
                severity="warning",
                payload=failure,
            )
        return failures


class EventReplay:
    """Session transition replay diagnostics."""

    @staticmethod
    def transition_log() -> list[dict[str, Any]]:
        return list(st.session_state.get(OBS_REPLAY_KEY) or [])

    @staticmethod
    def summary() -> dict[str, Any]:
        log = EventReplay.transition_log()
        counts: dict[str, int] = {}
        for item in log:
            action = (item.get("trace") or {}).get("action_type") or item.get("kind") or "unknown"
            counts[action] = counts.get(action, 0) + 1
        return {"count": len(log), "actions": counts, "latest": log[-10:]}


class ScalabilityDiagnostics:
    """Operational scalability pressure metrics."""

    @staticmethod
    def snapshot() -> dict[str, Any]:
        events = st.session_state.get(OBS_EVENTS_KEY) or []
        cache = CacheExplorer.snapshot()
        profiler = RenderProfiler.profile()
        return {
            "registered_charts": len(CHART_DEPENDENCY_REGISTRY),
            "observability_events": len(events),
            "lazy_cache_count": cache["lazy_cache_count"],
            "render_count": profiler["total_renders"],
            "cache_hits": profiler["total_hits"],
            "cache_misses": profiler["total_misses"],
            "warnings": _scalability_warnings(len(events), cache["lazy_cache_count"], profiler["total_misses"]),
        }


def _scalability_warnings(events: int, cache_count: int, misses: int) -> list[str]:
    warnings: list[str] = []
    if events > OBS_LIMIT * 0.9:
        warnings.append("observability_event_buffer_near_limit")
    if cache_count > 120:
        warnings.append("lazy_cache_pressure_high")
    if misses > 80:
        warnings.append("render_miss_pressure_high")
    return warnings


def operational_snapshot() -> dict[str, Any]:
    """Single platform diagnostics payload for developer tooling."""
    return {
        "observability": RuntimeObservabilityManager.snapshot(),
        "health": RuntimeHealthMonitor.inspect(),
        "cache": CacheExplorer.snapshot(),
        "render_profiler": RenderProfiler.profile(),
        "dependencies": DependencyGraphExplorer.graph(),
        "replay": EventReplay.summary(),
        "scalability": ScalabilityDiagnostics.snapshot(),
    }
