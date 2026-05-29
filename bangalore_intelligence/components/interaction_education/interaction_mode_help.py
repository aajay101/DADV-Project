"""Passive explanations for interaction-mode behavior."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .interaction_hints import InteractionHint, render_hint
from .semantics_utils import DashboardId, interaction_semantics_snapshot


def cosmetic_click_hint(state: Mapping[str, Any], dashboard: DashboardId) -> InteractionHint | None:
    snapshot = interaction_semantics_snapshot(state, dashboard)
    if snapshot["mode"] != "global_filter_mode":
        return None
    return InteractionHint(
        code="chart_click_cosmetic_global_filter_mode",
        message="Persistent filters are active, so chart clicks remain contextual only.",
        detail="Use Clear Global Filters or Reset All before chart clicks can create investigation overlays.",
    )


def render_chart_interaction_mode_hint(state: Mapping[str, Any], dashboard: DashboardId) -> None:
    render_hint(cosmetic_click_hint(state, dashboard), compact=False)


__all__ = ["cosmetic_click_hint", "render_chart_interaction_mode_hint"]
