"""Passive explanations for persistent global filter scope."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .interaction_hints import InteractionHint, render_hint
from .semantics_utils import DashboardId, interaction_semantics_snapshot


def filter_scope_hint(state: Mapping[str, Any], dashboard: DashboardId) -> InteractionHint | None:
    snapshot = interaction_semantics_snapshot(state, dashboard)
    if snapshot["mode"] == "global_filter_mode":
        return InteractionHint(
            code="global_filter_scope_active",
            message="Global filters are narrowing the active analytical dataset.",
            detail="They combine together and affect dependent charts until cleared.",
        )
    if snapshot["mode"] == "investigation_mode":
        return InteractionHint(
            code="global_filters_disabled_for_overlay",
            message="Global filters are paused while temporary investigation focus is active.",
            detail="Clear Focus restores baseline interaction before persistent filters change.",
        )
    return None


def render_filter_scope_hint(state: Mapping[str, Any], dashboard: DashboardId) -> None:
    render_hint(filter_scope_hint(state, dashboard), compact=False)


__all__ = ["filter_scope_hint", "render_filter_scope_hint"]
