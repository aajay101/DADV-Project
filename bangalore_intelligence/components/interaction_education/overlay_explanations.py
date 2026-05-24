"""Passive explanations for temporary investigation overlays."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .interaction_hints import InteractionHint, render_hint
from .semantics_utils import DashboardId, interaction_semantics_snapshot


def overlay_hint(state: Mapping[str, Any], dashboard: DashboardId) -> InteractionHint | None:
    snapshot = interaction_semantics_snapshot(state, dashboard)
    if not snapshot["investigation_overlay_active"]:
        return None
    return InteractionHint(
        code="investigation_overlay_active",
        message="Investigation focus is temporarily narrowing overlay-aware analysis.",
        detail="It does not rewrite global filters and can be removed with Clear Focus.",
    )


def render_overlay_hint(state: Mapping[str, Any], dashboard: DashboardId) -> None:
    render_hint(overlay_hint(state, dashboard), compact=False)


__all__ = ["overlay_hint", "render_overlay_hint"]
