"""Complexity-aware layout policy for explainability rendering."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExplainabilityLayout:
    show_decision_relevance: bool
    collapse_limitations: bool
    compact: bool


def layout_for_complexity(complexity_level: str) -> ExplainabilityLayout:
    if complexity_level == "basic":
        return ExplainabilityLayout(show_decision_relevance=False, collapse_limitations=True, compact=True)
    if complexity_level == "advanced":
        return ExplainabilityLayout(show_decision_relevance=True, collapse_limitations=True, compact=False)
    return ExplainabilityLayout(show_decision_relevance=True, collapse_limitations=False, compact=False)


__all__ = ["ExplainabilityLayout", "layout_for_complexity"]
