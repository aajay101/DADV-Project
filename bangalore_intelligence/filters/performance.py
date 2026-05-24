"""Performance governance: chart dependencies, cache tiers, and render traces."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import time
from typing import Any, Literal

import streamlit as st

DashboardId = Literal["traffic", "aqi"]
CacheTier = Literal["raw_dataset", "filtered_dataset", "visual_projection", "chart_render"]


@dataclass(frozen=True)
class ChartDependencySpec:
    chart_id: str
    dashboard: DashboardId
    depends_on_global_filters: tuple[str, ...] = ()
    depends_on_visual_focus: tuple[str, ...] = ()
    depends_on_investigation_overlay: tuple[str, ...] = ()
    depends_on_chart_local: tuple[str, ...] = ()
    depends_on_runtime: tuple[str, ...] = ()


@dataclass
class RenderTrace:
    chart_id: str
    dashboard: DashboardId
    page_key: str
    cache_key: str | None
    cache_hit: bool
    recompute_reason: str
    invalidation_source: str | None
    render_duration_ms: float
    timestamp: float


PERF_TRACE_KEY = "performance_render_traces"
PERF_STATS_KEY = "performance_cache_stats"
LAST_INVALIDATION_KEY = "last_cache_invalidation_trace"

TRAFFIC_GLOBAL_FILTERS = (
    "traffic_date_start",
    "traffic_date_end",
    "traffic_selected_areas",
    "traffic_selected_weather",
    "traffic_selected_roadwork",
    "traffic_selected_roads",
)

AQI_GLOBAL_FILTERS = (
    "aqi_date_start",
    "aqi_date_end",
    "aqi_selected_categories",
    "aqi_selected_seasons",
)

TRAFFIC_VISUAL_FOCUS = (
    "traffic_selected_area",
    "traffic_selected_road",
    "traffic_selected_month",
    "traffic_selected_quadrant",
    "traffic_radar_focus_area",
    "traffic_focus_chart",
    "traffic_focus_mode",
    "chart_selection_epoch",
)

AQI_VISUAL_FOCUS = (
    "aqi_selected_date",
    "aqi_selected_regime",
    "aqi_selected_season",
    "aqi_selected_category",
    "aqi_selected_year",
    "aqi_selected_week",
    "aqi_selected_pollutant",
    "aqi_focus_mode",
    "chart_selection_epoch",
)

TRAFFIC_INVESTIGATION_OVERLAY = (
    "traffic_investigation_scope",
)

AQI_INVESTIGATION_OVERLAY = (
    "aqi_investigation_scope",
)

TRAFFIC_CHART_LOCAL = (
    "traffic_radar_visible_areas",
    "traffic_radar_dimmed_areas",
    "traffic_radar_comparison_mode",
    "traffic_radar_comparison_n",
    "traffic_lab_use_full_dataset",
    "traffic_lab_t13_view",
)

AQI_CHART_LOCAL = (
    "aqi_pairplot_visible_categories",
    "aqi_pairplot_category_preset",
    "aqi_lab_use_full_dataset",
)


def _traffic_spec(
    chart_id: str,
    *,
    visual: bool = False,
    overlay: bool = False,
    local: tuple[str, ...] = (),
) -> ChartDependencySpec:
    return ChartDependencySpec(
        chart_id=chart_id,
        dashboard="traffic",
        depends_on_global_filters=TRAFFIC_GLOBAL_FILTERS,
        depends_on_visual_focus=TRAFFIC_VISUAL_FOCUS if visual else (),
        depends_on_investigation_overlay=TRAFFIC_INVESTIGATION_OVERLAY if overlay else (),
        depends_on_chart_local=local,
    )


def _aqi_spec(
    chart_id: str,
    *,
    visual: bool = False,
    overlay: bool = False,
    local: tuple[str, ...] = (),
) -> ChartDependencySpec:
    return ChartDependencySpec(
        chart_id=chart_id,
        dashboard="aqi",
        depends_on_global_filters=AQI_GLOBAL_FILTERS,
        depends_on_visual_focus=AQI_VISUAL_FOCUS if visual else (),
        depends_on_investigation_overlay=AQI_INVESTIGATION_OVERLAY if overlay else (),
        depends_on_chart_local=local,
    )


CHART_DEPENDENCY_REGISTRY: dict[str, ChartDependencySpec] = {
    "T-01": _traffic_spec("T-01"),
    "T-02": _traffic_spec("T-02", visual=True, overlay=True),
    "T-03": _traffic_spec("T-03"),
    "T-04": _traffic_spec("T-04"),
    "T-05": _traffic_spec("T-05", visual=True, overlay=True),
    "T-06": _traffic_spec("T-06", visual=True, overlay=True),
    "T-07": _traffic_spec("T-07", visual=True, overlay=True),
    "T-08": _traffic_spec("T-08"),
    "T-09": _traffic_spec("T-09", visual=True, overlay=True),
    "T-10": _traffic_spec("T-10"),
    "T-11": _traffic_spec("T-11", visual=True, overlay=True),
    "T-12": _traffic_spec("T-12"),
    "T-13": _traffic_spec("T-13", visual=True, overlay=True, local=TRAFFIC_CHART_LOCAL),
    "T-14": _traffic_spec("T-14"),
    "T-15": _traffic_spec("T-15", overlay=True),
    "A-01": _aqi_spec("A-01"),
    "A-02": _aqi_spec("A-02", visual=True, overlay=True),
    "A-03": _aqi_spec("A-03"),
    "A-04": _aqi_spec("A-04"),
    "A-05": _aqi_spec("A-05"),
    "A-06": _aqi_spec("A-06", visual=True, overlay=True),
    "A-07": _aqi_spec("A-07"),
    "A-08": _aqi_spec("A-08"),
    "A-09": _aqi_spec("A-09"),
    "A-10": _aqi_spec("A-10"),
    "A-11": _aqi_spec("A-11"),
    "A-12": _aqi_spec("A-12"),
    "A-13": _aqi_spec("A-13", visual=True, overlay=True),
    "A-14": _aqi_spec("A-14"),
    "A-15": _aqi_spec("A-15", visual=True, overlay=True, local=AQI_CHART_LOCAL),
}


def chart_dependency_spec(chart_id: str | None, dashboard: DashboardId) -> ChartDependencySpec:
    if chart_id and chart_id in CHART_DEPENDENCY_REGISTRY:
        return CHART_DEPENDENCY_REGISTRY[chart_id]
    return _traffic_spec(chart_id or "unknown") if dashboard == "traffic" else _aqi_spec(chart_id or "unknown")


def affected_charts_for_transition(
    dashboard: DashboardId,
    changed_domains: tuple[str, ...],
    changed_keys: tuple[str, ...] = (),
) -> tuple[str, ...]:
    specs = [spec for spec in CHART_DEPENDENCY_REGISTRY.values() if spec.dashboard == dashboard]
    affected: list[str] = []
    changed_key_set = set(changed_keys)
    for spec in specs:
        if "global_filters" in changed_domains and spec.depends_on_global_filters:
            affected.append(spec.chart_id)
            continue
        if "visual_focus" in changed_domains and spec.depends_on_visual_focus:
            affected.append(spec.chart_id)
            continue
        if "investigation_overlay" in changed_domains and spec.depends_on_investigation_overlay:
            affected.append(spec.chart_id)
            continue
        if "chart_local_state" in changed_domains:
            if changed_key_set and changed_key_set.intersection(spec.depends_on_chart_local):
                affected.append(spec.chart_id)
            elif not changed_key_set and spec.depends_on_chart_local:
                affected.append(spec.chart_id)
            continue
        if "runtime_state" in changed_domains and spec.depends_on_runtime:
            affected.append(spec.chart_id)
    return tuple(dict.fromkeys(affected))


def dependency_fingerprint(chart_id: str | None, dashboard: DashboardId, *, dataset_fp: str = "") -> str:
    spec = chart_dependency_spec(chart_id, dashboard)
    parts = [dataset_fp]
    for group in (
        spec.depends_on_global_filters,
        spec.depends_on_visual_focus,
        spec.depends_on_investigation_overlay,
        spec.depends_on_chart_local,
        spec.depends_on_runtime,
    ):
        if group:
            parts.append("|".join(f"{key}={st.session_state.get(key)}" for key in group))
    return "::".join(parts)


def cache_tiers_for_transition(changed_domains: tuple[str, ...]) -> tuple[CacheTier, ...]:
    tiers: list[CacheTier] = []
    if "global_filters" in changed_domains:
        tiers.extend(["filtered_dataset", "visual_projection", "chart_render"])
    if "visual_focus" in changed_domains:
        tiers.extend(["visual_projection", "chart_render"])
    if "investigation_overlay" in changed_domains:
        tiers.extend(["visual_projection", "chart_render"])
    if "chart_local_state" in changed_domains:
        tiers.append("chart_render")
    return tuple(dict.fromkeys(tiers))


def record_cache_invalidation(
    *,
    dashboard: DashboardId,
    source: str,
    cache_tiers: tuple[CacheTier, ...],
    affected_charts: tuple[str, ...],
) -> None:
    st.session_state[LAST_INVALIDATION_KEY] = {
        "dashboard": dashboard,
        "source": source,
        "cache_tiers": list(cache_tiers),
        "affected_charts": list(affected_charts),
        "timestamp": time.time(),
    }
    from filters.observability import RuntimeObservabilityManager

    RuntimeObservabilityManager.record_invalidation(st.session_state[LAST_INVALIDATION_KEY])


def record_render_trace(trace: RenderTrace) -> None:
    traces = list(st.session_state.get(PERF_TRACE_KEY) or [])
    traces.append(asdict(trace))
    st.session_state[PERF_TRACE_KEY] = traces[-80:]
    stats = dict(st.session_state.get(PERF_STATS_KEY) or {})
    chart_stats = dict(stats.get(trace.chart_id) or {"hits": 0, "misses": 0, "renders": 0, "total_ms": 0.0})
    chart_stats["renders"] += 1
    chart_stats["total_ms"] += trace.render_duration_ms
    if trace.cache_hit:
        chart_stats["hits"] += 1
    else:
        chart_stats["misses"] += 1
    stats[trace.chart_id] = chart_stats
    st.session_state[PERF_STATS_KEY] = stats
    from filters.observability import RuntimeObservabilityManager

    RuntimeObservabilityManager.record_render(asdict(trace))


def performance_snapshot() -> dict[str, Any]:
    return {
        "dependency_graph": {chart_id: asdict(spec) for chart_id, spec in CHART_DEPENDENCY_REGISTRY.items()},
        "last_invalidation": st.session_state.get(LAST_INVALIDATION_KEY),
        "render_traces": st.session_state.get(PERF_TRACE_KEY) or [],
        "cache_stats": st.session_state.get(PERF_STATS_KEY) or {},
    }
