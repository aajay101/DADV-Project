"""Passive explanations for visual focus and Clear Focus behavior."""

from __future__ import annotations

from .interaction_hints import InteractionHint, render_hint


def clear_focus_hint() -> InteractionHint:
    return InteractionHint(
        code="clear_focus_preserves_filters",
        message="Clear Focus removes temporary investigation context while preserving persistent filters.",
    )


def render_clear_focus_hint() -> None:
    render_hint(clear_focus_hint())


__all__ = ["clear_focus_hint", "render_clear_focus_hint"]
