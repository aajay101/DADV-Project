"""Semantic clarification for empty and unavailable analytical states."""

from __future__ import annotations

from typing import Literal

from .interaction_hints import InteractionHint, render_hint

EmptyStateKind = Literal[
    "valid_empty_result",
    "overlay_empty_result",
    "chart_unavailable",
    "lazy_not_hydrated",
    "dataset_unavailable",
]

_EMPTY_STATE_MESSAGES: dict[EmptyStateKind, InteractionHint] = {
    "valid_empty_result": InteractionHint(
        code="valid_empty_result",
        message="No matching data is a valid analytical result.",
        detail="The dashboard preserves your current scope instead of silently clearing filters.",
    ),
    "overlay_empty_result": InteractionHint(
        code="overlay_empty_result",
        message="The temporary investigation context has no matching rows for this view.",
        detail="Clear Focus removes the temporary context without changing global filters.",
    ),
    "chart_unavailable": InteractionHint(
        code="chart_unavailable",
        message="This chart could not safely render in the current view.",
        detail="Your filters and investigation state were preserved.",
    ),
    "lazy_not_hydrated": InteractionHint(
        code="lazy_not_hydrated",
        message="This chart is waiting for its lazy visual to hydrate.",
        detail="The analytical scope has not been changed.",
    ),
    "dataset_unavailable": InteractionHint(
        code="dataset_unavailable",
        message="The governed dataset is unavailable for this view.",
        detail="This is a data availability issue, not a filter or overlay action.",
    ),
}


def empty_state_message(kind: EmptyStateKind | str | None = "valid_empty_result") -> InteractionHint:
    if kind in _EMPTY_STATE_MESSAGES:
        return _EMPTY_STATE_MESSAGES[kind]  # type: ignore[index]
    return _EMPTY_STATE_MESSAGES["valid_empty_result"]


def render_empty_state_guidance(kind: EmptyStateKind | str | None = "valid_empty_result") -> None:
    render_hint(empty_state_message(kind), compact=False)


__all__ = ["EmptyStateKind", "empty_state_message", "render_empty_state_guidance"]
