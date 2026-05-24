"""Deferred chart figure builders — avoid render until UI slot is shown."""

from __future__ import annotations

from collections.abc import Callable
import time
from typing import Any

import streamlit as st

from data_layer.governance import active_dataset_fingerprint

FigureBuilder = Callable[[], Any]


def lazy_fig_builder(builder: FigureBuilder) -> dict[str, Any]:
    """Mark a chart slot as lazy; fig is resolved at render time only."""
    return {"lazy": True, "fig": None, "fig_builder": builder}


def resolve_chart_fig(
    cfg: dict | None,
    *,
    cache_key: str | None = None,
    dashboard: str | None = None,
    page_key: str | None = None,
    chart_id: str | None = None,
) -> Any:
    """
    Return a Plotly figure from eager ``fig`` or deferred ``fig_builder``.

    Optional cache_key stores the built figure for the current filter generation.
    """
    if not cfg:
        return None
    started = time.perf_counter()
    cid = chart_id or cfg.get("chart_id") or "unknown"
    dash = "traffic" if dashboard == "traffic" else "aqi" if dashboard == "aqi" else cfg.get("dashboard")
    if cfg.get("fig") is not None:
        _record_trace(
            dashboard=dash,
            page_key=page_key,
            chart_id=cid,
            cache_key=cache_key,
            cache_hit=True,
            recompute_reason="eager_figure",
            started=started,
        )
        return cfg["fig"]
    if cache_key:
        cached = st.session_state.get(cache_key)
        if cached is not None:
            _record_trace(
                dashboard=dash,
                page_key=page_key,
                chart_id=cid,
                cache_key=cache_key,
                cache_hit=True,
                recompute_reason="lazy_cache_hit",
                started=started,
            )
            return cached
    builder = cfg.get("fig_builder")
    if not callable(builder):
        return None
    try:
        fig = builder()
    except Exception as exc:
        from filters.observability import RecoveryManager, RuntimeObservabilityManager

        RuntimeObservabilityManager.record_failure(
            "lazy_chart_builder",
            exc,
            {"dashboard": dash, "page_key": page_key, "chart_id": cid, "cache_key": cache_key},
        )
        if dash in ("traffic", "aqi"):
            RecoveryManager.recover_chart_cache(dash, cid)
        _record_trace(
            dashboard=dash,
            page_key=page_key,
            chart_id=cid,
            cache_key=cache_key,
            cache_hit=False,
            recompute_reason="lazy_builder_failed",
            started=started,
        )
        return None
    if cache_key and fig is not None:
        st.session_state[cache_key] = fig
    _record_trace(
        dashboard=dash,
        page_key=page_key,
        chart_id=cid,
        cache_key=cache_key,
        cache_hit=False,
        recompute_reason="lazy_cache_miss",
        started=started,
    )
    return fig


def lazy_cache_key(dashboard: str, page_key: str, chart_id: str | None) -> str:
    """Stable chart-level cache key derived from explicit dependencies."""
    from filters.performance import dependency_fingerprint

    try:
        dataset_fp = active_dataset_fingerprint(dashboard)[:12]
    except Exception:
        dataset_fp = "unverified"
    fp = abs(hash(dependency_fingerprint(chart_id, "traffic" if dashboard == "traffic" else "aqi", dataset_fp=dataset_fp)))
    return f"buip_lazy_{dashboard}_{chart_id or 'chart'}_{page_key}_{fp}"


def clear_lazy_chart_cache(dashboard: str | None = None, chart_ids: tuple[str, ...] | None = None) -> None:
    """Drop deferred figure caches after filter updates."""
    prefix = f"buip_lazy_{dashboard}_" if dashboard else "buip_lazy_"
    chart_tokens = tuple(f"_{chart_id}_" for chart_id in (chart_ids or ()))
    for key in list(st.session_state.keys()):
        if not (isinstance(key, str) and key.startswith(prefix)):
            continue
        if chart_tokens and not any(token in key for token in chart_tokens):
            continue
        if isinstance(key, str) and key.startswith(prefix):
            del st.session_state[key]


def _record_trace(
    *,
    dashboard: str | None,
    page_key: str | None,
    chart_id: str,
    cache_key: str | None,
    cache_hit: bool,
    recompute_reason: str,
    started: float,
) -> None:
    if dashboard not in ("traffic", "aqi"):
        return
    from filters.performance import LAST_INVALIDATION_KEY, RenderTrace, record_render_trace

    invalidation = st.session_state.get(LAST_INVALIDATION_KEY) or {}
    record_render_trace(
        RenderTrace(
            chart_id=chart_id,
            dashboard=dashboard,
            page_key=page_key or "unknown",
            cache_key=cache_key,
            cache_hit=cache_hit,
            recompute_reason=recompute_reason,
            invalidation_source=invalidation.get("source"),
            render_duration_ms=(time.perf_counter() - started) * 1000,
            timestamp=time.time(),
        )
    )
