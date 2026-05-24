"""Passive interpretation navigation helpers."""

from __future__ import annotations

from dataclasses import dataclass

from bangalore_intelligence.explainability.models import ExplainabilityEntry
from components.related_analysis.related_visual_utils import related_visuals_for


@dataclass(frozen=True, slots=True)
class InterpretationNavItem:
    """A passive section navigation item."""

    label: str
    anchor: str


@dataclass(frozen=True, slots=True)
class RelatedInvestigation:
    """Passive related-investigation context for the modal."""

    visual_id: str
    title: str
    label: str
    relationship_type: str


def related_investigation_ids(entry: ExplainabilityEntry) -> tuple[str, ...]:
    """Return related investigations declared in interpretation metadata."""

    return entry.related_investigations


def interpretation_nav_items() -> tuple[InterpretationNavItem, ...]:
    """Return stable section anchors for in-modal navigation."""

    return (
        InterpretationNavItem("Verdict", "verdict"),
        InterpretationNavItem("Significance", "significance"),
        InterpretationNavItem("Focus", "focus-point"),
        InterpretationNavItem("Human Impact", "human-impact"),
        InterpretationNavItem("Consequence", "pattern-consequence"),
        InterpretationNavItem("Next", "next-investigation"),
        InterpretationNavItem("Guardrail", "misunderstanding-guard"),
        InterpretationNavItem("How To Read", "guided-reading"),
        InterpretationNavItem("Analyst Detail", "analyst-detail"),
        InterpretationNavItem("Anatomy", "visualization-anatomy"),
        InterpretationNavItem("Glossary", "glossary"),
    )


def related_investigation_flow(entry: ExplainabilityEntry) -> tuple[RelatedInvestigation, ...]:
    """Return passive relationship cards using existing related-analysis metadata."""

    visual_ids = set(entry.related_investigations)
    related = []
    for visual in related_visuals_for(entry):
        if visual.visual_id not in visual_ids:
            continue
        related.append(
            RelatedInvestigation(
                visual_id=visual.visual_id,
                title=visual.title,
                label=visual.label,
                relationship_type=visual.relationship_type,
            )
        )
    return tuple(related)


__all__ = [
    "InterpretationNavItem",
    "RelatedInvestigation",
    "interpretation_nav_items",
    "related_investigation_flow",
    "related_investigation_ids",
]
