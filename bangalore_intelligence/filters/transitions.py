"""Deterministic dashboard state transitions and runtime invalidation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import time
from typing import Any, Literal, Mapping

import streamlit as st

from filters.state import AQI_STATE_DEFAULTS, TRAFFIC_STATE_DEFAULTS

DashboardId = Literal["traffic", "aqi"]
StateDomain = Literal[
    "global_filters",
    "visual_focus",
    "investigation_overlay",
    "chart_local_state",
    "runtime_state",
]


@dataclass(frozen=True)
class InvalidationPlan:
    """Runtime work requested by a reducer after state mutation."""

    invalidate_visuals: bool = False
    invalidate_lazy_charts: bool = False
    clear_data_cache: bool = False
    data_cache_scope: Literal["none", "dashboard", "all"] = "none"
    lazy_chart_scope: Literal["none", "dashboard", "all"] = "none"
    bump_widget_epoch: bool = False
    mark_filter_updating: bool = False
    clear_selection_signature: bool = False
    affected_charts: tuple[str, ...] = ()
    cache_tiers: tuple[str, ...] = ()
    reason: str | None = None


@dataclass
class TransitionResult:
    """Inspectable result of one reducer transition."""

    action_type: str
    dashboard: DashboardId
    reducer: str
    changed_domains: tuple[StateDomain, ...] = ()
    state_changes: dict[str, Any] = field(default_factory=dict)
    invalidation_plan: InvalidationPlan = field(default_factory=InvalidationPlan)
    rerender_required: bool = False


@dataclass(frozen=True)
class ChartFocusChanged:
    dashboard: DashboardId
    payload: Mapping[str, Any]


@dataclass(frozen=True)
class FocusCleared:
    dashboard: DashboardId


@dataclass(frozen=True)
class GlobalFilterChanged:
    dashboard: DashboardId
    updates: Mapping[str, Any] = field(default_factory=dict)
    filters_active: bool | None = None


@dataclass(frozen=True)
class GlobalFiltersReset:
    dashboard: DashboardId


@dataclass(frozen=True)
class ClearGlobalFilters:
    dashboard: DashboardId


@dataclass(frozen=True)
class ChartLocalStateChanged:
    dashboard: DashboardId
    updates: Mapping[str, Any]


@dataclass(frozen=True)
class FullscreenChanged:
    dashboard: DashboardId
    fullscreen_key: str | None


@dataclass(frozen=True)
class DashboardChanged:
    dashboard: DashboardId


@dataclass(frozen=True)
class ActiveTabChanged:
    dashboard: DashboardId
    tab_index: int
    from_widget: bool = False


@dataclass(frozen=True)
class LabGateChanged:
    dashboard: DashboardId
    passed: bool


Action = (
    ChartFocusChanged
    | FocusCleared
    | GlobalFilterChanged
    | GlobalFiltersReset
    | ClearGlobalFilters
    | ChartLocalStateChanged
    | FullscreenChanged
    | DashboardChanged
    | ActiveTabChanged
    | LabGateChanged
)

TRACE_KEY = "last_transition_trace"
RERENDER_TRACE_KEY = "last_rerender_trace"

TRAFFIC_GLOBAL_FILTER_KEYS = (
    "traffic_date_start",
    "traffic_date_end",
    "traffic_selected_areas",
    "traffic_selected_weather",
    "traffic_selected_roadwork",
    "traffic_selected_roads",
    "traffic_filters_active",
)

AQI_GLOBAL_FILTER_KEYS = (
    "aqi_date_start",
    "aqi_date_end",
    "aqi_selected_categories",
    "aqi_selected_seasons",
    "aqi_filters_active",
)

TRAFFIC_VISUAL_FOCUS_KEYS = (
    "traffic_selected_area",
    "traffic_selected_road",
    "traffic_selected_month",
    "traffic_selected_quadrant",
    "traffic_radar_focus_area",
    "traffic_focus_chart",
    "traffic_focus_mode",
)

AQI_VISUAL_FOCUS_KEYS = (
    "aqi_selected_date",
    "aqi_selected_month",
    "aqi_selected_regime",
    "aqi_selected_season",
    "aqi_selected_category",
    "aqi_selected_year",
    "aqi_selected_week",
    "aqi_selected_pollutant",
    "aqi_focus_chart",
    "aqi_focus_mode",
    "aqi_context_pm25",
)

TRAFFIC_INVESTIGATION_OVERLAY_KEYS = (
    "traffic_investigation_scope",
)

AQI_INVESTIGATION_OVERLAY_KEYS = (
    "aqi_investigation_scope",
)

TRAFFIC_CHART_LOCAL_KEYS = (
    "traffic_t03_zoom_start",
    "traffic_t03_zoom_end",
    "traffic_radar_visible_areas",
    "traffic_radar_dimmed_areas",
    "traffic_radar_comparison_mode",
    "traffic_radar_comparison_n",
    "traffic_lab_use_full_dataset",
    "traffic_lab_t13_view",
)

AQI_CHART_LOCAL_KEYS = (
    "aqi_pairplot_visible_categories",
    "aqi_pairplot_category_preset",
    "aqi_lab_use_full_dataset",
)


def dispatch(action: Action, *, rerun: bool = False) -> TransitionResult:
    """Reduce one action, apply its runtime plan, and optionally rerun."""
    result = dashboard_reducer(action)
    apply_transition_result(result, rerun=rerun)
    return result


def dashboard_reducer(action: Action) -> TransitionResult:
    """Route an explicit action to the reducer that owns its domain."""
    if isinstance(action, ChartFocusChanged):
        return reduce_visual_focus(action)
    if isinstance(action, FocusCleared):
        return reduce_visual_focus(action)
    if isinstance(action, GlobalFilterChanged):
        return reduce_global_filters(action)
    if isinstance(action, (GlobalFiltersReset, ClearGlobalFilters)):
        return reduce_global_filters(action)
    if isinstance(action, ChartLocalStateChanged):
        return reduce_chart_local_state(action)
    if isinstance(action, FullscreenChanged):
        return reduce_runtime_state(action)
    if isinstance(action, DashboardChanged):
        return reduce_runtime_state(action)
    if isinstance(action, ActiveTabChanged):
        return reduce_runtime_state(action)
    if isinstance(action, LabGateChanged):
        return reduce_runtime_state(action)
    raise TypeError(f"Unsupported dashboard action: {action!r}")


def reduce_visual_focus(action: ChartFocusChanged | FocusCleared) -> TransitionResult:
    """Mutate visual focus and its explicit investigation overlay only."""
    if isinstance(action, FocusCleared):
        keys = _visual_keys(action.dashboard) + _investigation_overlay_keys(action.dashboard)
        defaults = _defaults(action.dashboard)
        changes = _write_defaults(keys, defaults)
        return TransitionResult(
            action_type="FocusCleared",
            dashboard=action.dashboard,
            reducer="reduce_visual_focus",
            changed_domains=("visual_focus", "investigation_overlay"),
            state_changes=changes,
            invalidation_plan=_domain_invalidation(
                action.dashboard,
                ("visual_focus", "investigation_overlay"),
                "focus_cleared",
                changed_keys=tuple(changes.keys()),
                clear_selection_signature=True,
            ),
            rerender_required=True,
        )

    payload = dict(action.payload)
    changes: dict[str, Any] = {}
    from filters.interaction_mode import has_active_global_filters

    global_mode = has_active_global_filters(st.session_state, action.dashboard)
    if action.dashboard == "traffic":
        changes.update(_set("traffic_focus_chart", payload.get("chart")))
        changes.update(_set("traffic_focus_mode", payload.get("focus_mode")))
        if "selected_road" in payload:
            changes.update(_set("traffic_selected_road", payload.get("selected_road")))
        if "selected_area" in payload:
            changes.update(_set("traffic_selected_area", payload.get("selected_area")))
        if "selected_quadrant" in payload:
            changes.update(_set("traffic_selected_quadrant", payload.get("selected_quadrant")))
        if "selected_month" in payload:
            changes.update(_set("traffic_selected_month", payload.get("selected_month")))
        if payload.get("focus_entity"):
            changes.update(_set("traffic_radar_focus_area", payload["focus_entity"]))
        elif payload.get("selected_area") and payload.get("focus_mode") == "radar_comparison":
            changes.update(_set("traffic_radar_focus_area", payload["selected_area"]))
        if not global_mode:
            changes.update(_set("traffic_investigation_scope", _traffic_overlay_from_payload(payload)))
    else:
        changes.update(_set("aqi_focus_chart", payload.get("chart")))
        changes.update(_set("aqi_focus_mode", payload.get("focus_mode")))
        for key in (
            "selected_date",
            "selected_category",
            "selected_season",
            "selected_regime",
            "selected_pollutant",
        ):
            if key in payload:
                changes.update(_set(f"aqi_{key}", payload.get(key)))
        if "selected_day" in payload:
            changes.update(_set("aqi_selected_date", payload.get("selected_day")))
        if "selected_year" in payload:
            changes.update(_set("aqi_selected_year", payload.get("selected_year")))
        if "selected_week" in payload:
            changes.update(_set("aqi_selected_week", payload.get("selected_week")))
        if "context_pm25" in payload:
            changes.update(_set("aqi_context_pm25", payload.get("context_pm25")))
        if not global_mode:
            changes.update(_set("aqi_investigation_scope", _aqi_overlay_from_payload(payload)))
    changed_domains: tuple[StateDomain, ...] = (
        ("visual_focus",) if global_mode else ("visual_focus", "investigation_overlay")
    )
    return TransitionResult(
        action_type="ChartFocusChanged",
        dashboard=action.dashboard,
        reducer="reduce_visual_focus",
        changed_domains=changed_domains,
        state_changes=changes,
        invalidation_plan=_domain_invalidation(
            action.dashboard,
            changed_domains,
            "chart_focus_cosmetic_global_filter_mode" if global_mode else "chart_focus_changed",
            changed_keys=tuple(changes.keys()),
        ),
        rerender_required=True,
    )


def reduce_global_filters(action: GlobalFilterChanged | GlobalFiltersReset | ClearGlobalFilters) -> TransitionResult:
    """Mutate only widget-backed global filter keys."""
    if isinstance(action, ClearGlobalFilters):
        keys = _global_filter_keys(action.dashboard)
        defaults = _defaults(action.dashboard)
        changes = _write_defaults(keys, defaults)
        return TransitionResult(
            action_type="ClearGlobalFilters",
            dashboard=action.dashboard,
            reducer="reduce_global_filters",
            changed_domains=("global_filters",),
            state_changes=changes,
            invalidation_plan=_domain_invalidation(
                action.dashboard,
                ("global_filters",),
                "global_filters_cleared",
                changed_keys=tuple(changes.keys()),
            ),
            rerender_required=True,
        )

    if isinstance(action, GlobalFiltersReset):
        keys = (
            _global_filter_keys(action.dashboard)
            + _visual_keys(action.dashboard)
            + _investigation_overlay_keys(action.dashboard)
        )
        defaults = _defaults(action.dashboard)
        changes = _write_defaults(keys, defaults)
        return TransitionResult(
            action_type="GlobalFiltersReset",
            dashboard=action.dashboard,
            reducer="reduce_global_filters",
            changed_domains=("global_filters", "visual_focus", "investigation_overlay"),
            state_changes=changes,
            invalidation_plan=_domain_invalidation(
                action.dashboard,
                ("global_filters", "visual_focus", "investigation_overlay"),
                "global_filters_reset",
                changed_keys=tuple(changes.keys()),
                clear_selection_signature=True,
            ),
            rerender_required=True,
        )

    from filters.interaction_mode import has_active_investigation_overlay

    if has_active_investigation_overlay(st.session_state, action.dashboard):
        return TransitionResult(
            action_type="GlobalFilterChanged",
            dashboard=action.dashboard,
            reducer="reduce_global_filters",
            changed_domains=(),
            state_changes={},
            invalidation_plan=InvalidationPlan(reason="global_filter_blocked_in_investigation_mode"),
            rerender_required=False,
        )

    changes: dict[str, Any] = {}
    allowed = set(_global_filter_keys(action.dashboard))
    for key, value in action.updates.items():
        if key not in allowed:
            raise ValueError(f"{key!r} is not a {action.dashboard} global filter key")
        changes.update(_set(key, _copy_value(value)))
    if action.filters_active is not None:
        key = "traffic_filters_active" if action.dashboard == "traffic" else "aqi_filters_active"
        changes.update(_set(key, bool(action.filters_active)))
    return TransitionResult(
        action_type="GlobalFilterChanged",
        dashboard=action.dashboard,
        reducer="reduce_global_filters",
        changed_domains=("global_filters",),
        state_changes=changes,
        invalidation_plan=_domain_invalidation(
            action.dashboard,
            ("global_filters",),
            "global_filter_changed",
            changed_keys=tuple(changes.keys()),
        ),
        rerender_required=True,
    )


def reduce_chart_local_state(action: ChartLocalStateChanged) -> TransitionResult:
    """Mutate only chart-local control keys."""
    allowed = set(_chart_local_keys(action.dashboard))
    changes: dict[str, Any] = {}
    for key, value in action.updates.items():
        if key not in allowed:
            raise ValueError(f"{key!r} is not a {action.dashboard} chart-local key")
        changes.update(_set(key, _copy_value(value)))
    return TransitionResult(
        action_type="ChartLocalStateChanged",
        dashboard=action.dashboard,
        reducer="reduce_chart_local_state",
        changed_domains=("chart_local_state",),
        state_changes=changes,
        invalidation_plan=_domain_invalidation(
            action.dashboard,
            ("chart_local_state",),
            "chart_local_state_changed",
            changed_keys=tuple(changes.keys()),
        ),
        rerender_required=True,
    )


def reduce_runtime_state(action: FullscreenChanged | DashboardChanged | ActiveTabChanged | LabGateChanged) -> TransitionResult:
    """Mutate only runtime coordination keys."""
    changes: dict[str, Any] = {}
    if isinstance(action, FullscreenChanged):
        changes.update(_set("fullscreen_chart_key", action.fullscreen_key))
        changes.update(_set("fullscreen_dashboard", action.dashboard if action.fullscreen_key else None))
        return TransitionResult(
            action_type="FullscreenChanged",
            dashboard=action.dashboard,
            reducer="reduce_runtime_state",
            changed_domains=("runtime_state",),
            state_changes=changes,
            rerender_required=True,
        )
    if isinstance(action, ActiveTabChanged):
        from config.page_config import AQI_TABS, TRAFFIC_TABS

        tabs = TRAFFIC_TABS if action.dashboard == "traffic" else AQI_TABS
        idx = max(0, min(int(action.tab_index), len(tabs) - 1))
        active_key = "traffic_active_tab" if action.dashboard == "traffic" else "aqi_active_tab"
        changes.update(_set(active_key, idx))
        if not action.from_widget:
            changes.update(_set(f"{action.dashboard}_tab_nav_programmatic_sync", True))
        return TransitionResult(
            action_type="ActiveTabChanged",
            dashboard=action.dashboard,
            reducer="reduce_runtime_state",
            changed_domains=("runtime_state",),
            state_changes=changes,
            rerender_required=True,
        )
    if isinstance(action, LabGateChanged):
        key = "traffic_lab_gate_passed" if action.dashboard == "traffic" else "aqi_lab_gate_passed"
        changes.update(_set(key, bool(action.passed)))
        return TransitionResult(
            action_type="LabGateChanged",
            dashboard=action.dashboard,
            reducer="reduce_runtime_state",
            changed_domains=("runtime_state",),
            state_changes=changes,
            rerender_required=True,
        )
    changes.update(_set("active_dashboard", action.dashboard))
    changes.update(_set("fullscreen_chart_key", None))
    changes.update(_set("fullscreen_dashboard", None))
    st.session_state["_buip_css_injected"] = False
    changes["_buip_css_injected"] = False
    return TransitionResult(
        action_type="DashboardChanged",
        dashboard=action.dashboard,
        reducer="reduce_runtime_state",
        changed_domains=("runtime_state",),
        state_changes=changes,
        rerender_required=True,
    )


def apply_transition_result(result: TransitionResult, *, rerun: bool = False) -> None:
    """Apply cache/widget/runtime work requested by a transition result."""
    plan = result.invalidation_plan
    now = time.time()
    if plan.bump_widget_epoch:
        if plan.affected_charts:
            epochs = dict(st.session_state.get("chart_selection_epochs") or {})
            for chart_id in plan.affected_charts:
                epochs[chart_id] = int(epochs.get(chart_id, 0)) + 1
            st.session_state["chart_selection_epochs"] = epochs
        else:
            st.session_state["chart_selection_epoch"] = int(st.session_state.get("chart_selection_epoch", 0)) + 1
    if plan.invalidate_lazy_charts:
        from data_layer.lazy_charts import clear_lazy_chart_cache

        clear_lazy_chart_cache(result.dashboard, chart_ids=plan.affected_charts or None)
    if plan.clear_data_cache:
        clear_cache = getattr(st.cache_data, "clear", None)
        if callable(clear_cache):
            clear_cache()
    if plan.clear_selection_signature:
        st.session_state.pop("_chart_sel_sig", None)
    if plan.mark_filter_updating:
        prefix = "traffic" if result.dashboard == "traffic" else "aqi"
        st.session_state[f"{prefix}_filter_updating"] = True
    if any(
        (
            plan.invalidate_visuals,
            plan.invalidate_lazy_charts,
            plan.clear_data_cache,
            plan.bump_widget_epoch,
            plan.mark_filter_updating,
        )
    ):
        st.session_state["last_filter_change_at"] = now
    if plan.invalidate_lazy_charts or plan.clear_data_cache:
        from filters.performance import record_cache_invalidation

        record_cache_invalidation(
            dashboard=result.dashboard,
            source=plan.reason or result.action_type,
            cache_tiers=tuple(plan.cache_tiers),
            affected_charts=tuple(plan.affected_charts),
        )
    trace = transition_trace(result, rerender_executed=False)
    st.session_state[TRACE_KEY] = trace
    from filters.observability import RuntimeObservabilityManager

    RuntimeObservabilityManager.record_transition(trace)
    if plan.reason in (
        "chart_focus_cosmetic_global_filter_mode",
        "global_filter_blocked_in_investigation_mode",
        "focus_cleared",
    ):
        RuntimeObservabilityManager.emit(
            "transition",
            source=plan.reason or result.action_type,
            message=plan.reason or result.action_type,
            severity="warning" if "blocked" in (plan.reason or "") else "info",
            payload=trace,
        )
    from filters.interaction_mode import assert_valid_interaction_mode

    try:
        assert_valid_interaction_mode(st.session_state, result.dashboard)
    except RuntimeError as exc:
        RuntimeObservabilityManager.emit(
            "assertion",
            source="interaction_mode",
            message=str(exc),
            severity="critical",
            payload=trace,
        )
        if st.session_state.get("developer_mode"):
            raise
    if rerun and result.rerender_required:
        request_rerun(result, source="dispatch")


def transition_trace(result: TransitionResult, *, rerender_executed: bool = False) -> dict[str, Any]:
    """Return a serializable inspection record for the last transition."""
    from filters.interaction_mode import interaction_mode_snapshot

    return {
        "action_type": result.action_type,
        "dashboard": result.dashboard,
        "reducer": result.reducer,
        "changed_domains": list(result.changed_domains),
        "state_changes": dict(result.state_changes),
        "invalidation_plan": asdict(result.invalidation_plan),
        "interaction_mode": interaction_mode_snapshot(st.session_state, result.dashboard),
        "rerender_required": result.rerender_required,
        "rerender_executed": rerender_executed,
        "timestamp": time.time(),
    }


def get_last_transition_trace() -> dict[str, Any] | None:
    trace = st.session_state.get(TRACE_KEY)
    return dict(trace) if isinstance(trace, dict) else None


def request_rerun(result: TransitionResult, *, source: str) -> None:
    """Record rerender intent and execute rerun only for transition-backed events."""
    trace = {
        "source": source,
        "action_type": result.action_type,
        "dashboard": result.dashboard,
        "reducer": result.reducer,
        "reason": result.invalidation_plan.reason,
        "rerender_required": result.rerender_required,
        "timestamp": time.time(),
    }
    st.session_state[RERENDER_TRACE_KEY] = trace
    from filters.observability import RuntimeObservabilityManager

    RuntimeObservabilityManager.record_rerender(trace)
    if result.rerender_required:
        current = get_last_transition_trace()
        if current:
            current["rerender_executed"] = True
            st.session_state[TRACE_KEY] = current
        st.rerun()


def request_rerun_for_last_transition(*, source: str) -> None:
    """Rerun from a UI boundary after a prior dispatch recorded transition intent."""
    trace = get_last_transition_trace()
    rerender_trace = {
        "source": source,
        "action_type": trace.get("action_type") if trace else None,
        "dashboard": trace.get("dashboard") if trace else None,
        "reducer": trace.get("reducer") if trace else None,
        "reason": (trace.get("invalidation_plan") or {}).get("reason") if trace else None,
        "rerender_required": bool(trace and trace.get("rerender_required")),
        "timestamp": time.time(),
    }
    st.session_state[RERENDER_TRACE_KEY] = rerender_trace
    from filters.observability import RuntimeObservabilityManager

    RuntimeObservabilityManager.record_rerender(rerender_trace)
    if trace and trace.get("rerender_required"):
        trace["rerender_executed"] = True
        st.session_state[TRACE_KEY] = trace
        st.rerun()


def record_deferred_rerun(*, dashboard: DashboardId, source: str, reason: str) -> None:
    """Record rerun intent for framework-required deferred operations."""
    trace = {
        "source": source,
        "action_type": None,
        "dashboard": dashboard,
        "reducer": None,
        "reason": reason,
        "rerender_required": True,
        "deferred_transition": True,
        "timestamp": time.time(),
    }
    st.session_state[RERENDER_TRACE_KEY] = trace
    from filters.observability import RuntimeObservabilityManager

    RuntimeObservabilityManager.record_rerender(trace)


def _domain_invalidation(
    dashboard: DashboardId,
    changed_domains: tuple[StateDomain, ...],
    reason: str,
    *,
    changed_keys: tuple[str, ...] = (),
    clear_selection_signature: bool = False,
) -> InvalidationPlan:
    from filters.performance import affected_charts_for_transition, cache_tiers_for_transition

    affected = affected_charts_for_transition(dashboard, changed_domains, changed_keys)
    tiers = cache_tiers_for_transition(changed_domains)
    clear_data = "filtered_dataset" in tiers
    return InvalidationPlan(
        invalidate_visuals=True,
        invalidate_lazy_charts=True,
        clear_data_cache=clear_data,
        data_cache_scope="dashboard" if clear_data else "none",
        lazy_chart_scope="dashboard" if affected else "none",
        bump_widget_epoch=True,
        mark_filter_updating="global_filters" in changed_domains,
        reason=reason,
        clear_selection_signature=clear_selection_signature,
        affected_charts=affected,
        cache_tiers=tuple(tiers),
    )


def _set(key: str, value: Any) -> dict[str, Any]:
    copied = _copy_value(value)
    st.session_state[key] = copied
    return {key: copied}


def _write_defaults(keys: tuple[str, ...], defaults: Mapping[str, Any]) -> dict[str, Any]:
    changes: dict[str, Any] = {}
    for key in keys:
        changes.update(_set(key, defaults[key]))
    return changes


def _copy_value(value: Any) -> Any:
    if isinstance(value, list):
        return list(value)
    if isinstance(value, dict):
        return dict(value)
    return value


def _defaults(dashboard: DashboardId) -> Mapping[str, Any]:
    return TRAFFIC_STATE_DEFAULTS if dashboard == "traffic" else AQI_STATE_DEFAULTS


def _global_filter_keys(dashboard: DashboardId) -> tuple[str, ...]:
    return TRAFFIC_GLOBAL_FILTER_KEYS if dashboard == "traffic" else AQI_GLOBAL_FILTER_KEYS


def _visual_keys(dashboard: DashboardId) -> tuple[str, ...]:
    return TRAFFIC_VISUAL_FOCUS_KEYS if dashboard == "traffic" else AQI_VISUAL_FOCUS_KEYS


def _investigation_overlay_keys(dashboard: DashboardId) -> tuple[str, ...]:
    return TRAFFIC_INVESTIGATION_OVERLAY_KEYS if dashboard == "traffic" else AQI_INVESTIGATION_OVERLAY_KEYS


def _chart_local_keys(dashboard: DashboardId) -> tuple[str, ...]:
    return TRAFFIC_CHART_LOCAL_KEYS if dashboard == "traffic" else AQI_CHART_LOCAL_KEYS


def _traffic_overlay_from_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    area = payload.get("focus_entity") or payload.get("selected_area")
    return {
        "area": area,
        "road": payload.get("selected_road"),
        "month": payload.get("selected_month"),
        "quadrant": payload.get("selected_quadrant"),
        "source_chart": payload.get("chart"),
        "focus_mode": payload.get("focus_mode"),
    }


def _aqi_overlay_from_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "season": payload.get("selected_season"),
        "category": payload.get("selected_category"),
        "date": payload.get("selected_day") or payload.get("selected_date"),
        "year": payload.get("selected_year"),
        "week": payload.get("selected_week"),
        "regime": payload.get("selected_regime"),
        "pollutant": payload.get("selected_pollutant"),
        "source_chart": payload.get("chart"),
        "focus_mode": payload.get("focus_mode"),
    }
