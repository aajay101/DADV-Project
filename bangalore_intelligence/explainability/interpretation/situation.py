"""Situation-centered interpretation helpers.

Migrated charts read independently authored situation fields. Legacy charts use
an explicit compatibility fallback so chart-by-chart migration can proceed
without breaking existing registry entries.
"""

from __future__ import annotations

from dataclasses import dataclass

from bangalore_intelligence.explainability.models import ExplainabilityEntry, HumanImpact


MAX_DYNAMIC_ITEMS_PER_VIEW = 6


@dataclass(frozen=True, slots=True)
class SituationInterpretation:
    """Compressed, render-ready situation interpretation for one chart view."""

    dominant_takeaway: str
    verdict: str
    significance: str
    focus_point: str
    human_impact: HumanImpact | None
    consequence: str
    next_investigation: str
    misunderstanding_guard: str
    confidence_anchor: str
    uncertainty_note: str
    guided_reading: str


def _first(items: tuple[str, ...]) -> str:
    return items[0] if items else ""


def _legacy_human_impact(entry: ExplainabilityEntry) -> HumanImpact:
    if entry.dashboard == "aqi":
        return HumanImpact(
            who_is_affected="People spending time outdoors in the selected air-quality scope.",
            what_they_experience=entry.real_world_meaning or entry.decision_relevance,
            duration_or_scope="This applies to the filtered period and category context, not every day in the city.",
        )
    return HumanImpact(
        who_is_affected="People traveling through the selected traffic scope.",
        what_they_experience=entry.real_world_meaning or entry.decision_relevance,
        duration_or_scope="This applies to the filtered records, not guaranteed live citywide traffic.",
    )

def is_semantically_migrated(entry: ExplainabilityEntry) -> bool:
    """Return whether the entry is expected to use authored situation fields."""

    return entry.semantic_migration_status == "migrated"


def uses_special_cognition_flow(entry: ExplainabilityEntry) -> bool:
    """Return whether the migrated entry needs focus-first special-cognition pacing."""

    return is_semantically_migrated(entry) and entry.surface_id in {"T-02", "T-13", "A-13", "A-15"}


def resolve_situation_interpretation(entry: ExplainabilityEntry) -> SituationInterpretation:
    """Resolve one concise situation interpretation for migrated or legacy entries."""

    if not is_semantically_migrated(entry):
        next_step = entry.next_investigation_reason
        if not next_step and entry.related_investigations:
            next_step = f"Use {entry.related_investigations[0]} next if you need one connected follow-up view."
        return SituationInterpretation(
            dominant_takeaway=entry.dominant_takeaway or entry.reading_summary,
            verdict=entry.situation_verdict or entry.reading_summary,
            significance=entry.significance or entry.real_world_meaning or entry.decision_relevance,
            focus_point=entry.focus_point or entry.intended_interpretation or entry.when_to_use,
            human_impact=entry.human_impact or _legacy_human_impact(entry),
            consequence=entry.pattern_consequence or _first(entry.patterns) or entry.real_world_meaning,
            next_investigation=next_step,
            misunderstanding_guard=entry.misunderstanding_guard
            or _first(entry.misunderstandings)
            or entry.misinterpretation_warning,
            confidence_anchor=entry.confidence_anchor
            or "You now have the main takeaway; use deeper sections only if you need evidence details.",
            uncertainty_note=entry.uncertainty_note,
            guided_reading=entry.guided_reading or entry.intended_interpretation or entry.when_to_use,
        )

    return SituationInterpretation(
        dominant_takeaway=entry.dominant_takeaway,
        verdict=entry.situation_verdict,
        significance=entry.significance,
        focus_point=entry.focus_point,
        human_impact=entry.human_impact,
        consequence=entry.pattern_consequence,
        next_investigation=entry.next_investigation_reason,
        misunderstanding_guard=entry.misunderstanding_guard,
        confidence_anchor=entry.confidence_anchor,
        uncertainty_note=entry.uncertainty_note,
        guided_reading=entry.guided_reading,
    )


def analyst_detail_items(entry: ExplainabilityEntry) -> tuple[str, ...]:
    """Return methodology-oriented detail without mixing in visual anatomy."""

    if is_semantically_migrated(entry):
        return entry.analyst_detail
    metric_items = tuple(
        f"{metric.name}: {metric.meaning} {metric.why_it_matters}".strip() for metric in entry.metrics
    )
    return entry.analyst_detail or metric_items + entry.limitations


def visualization_anatomy_items(entry: ExplainabilityEntry):
    """Return visual anatomy components from the new anatomy field only."""

    return entry.visualization_anatomy or (() if is_semantically_migrated(entry) else entry.visual_components)


def has_insufficient_data_signal(entry: ExplainabilityEntry) -> bool:
    """Return whether the entry has explicit weak-signal fallback messaging."""

    return bool(entry.uncertainty_note)


__all__ = [
    "MAX_DYNAMIC_ITEMS_PER_VIEW",
    "SituationInterpretation",
    "analyst_detail_items",
    "has_insufficient_data_signal",
    "is_semantically_migrated",
    "resolve_situation_interpretation",
    "uses_special_cognition_flow",
    "visualization_anatomy_items",
]
