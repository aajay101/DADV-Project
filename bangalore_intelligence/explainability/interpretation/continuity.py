"""Deterministic cross-chart analytical continuity helpers."""

from __future__ import annotations

from dataclasses import dataclass

from bangalore_intelligence.explainability.interpretation.dynamic_context import DynamicInsightContext
from bangalore_intelligence.explainability.models import ExplainabilityEntry


@dataclass(frozen=True, slots=True)
class AnalyticalContinuity:
    """Bounded follow-up rationale for the current interpretation state."""

    primary_visual_id: str = ""
    follow_up_reason: str = ""
    unresolved_question: str = ""
    analytical_gap: str = ""
    suppression_fragment: str = ""
    depth_control: str = ""


_LOCAL_DETAIL_IDS = ("T-05", "T-07", "T-09", "T-11", "A-06", "A-13", "A-14")
_TEMPORAL_IDS = ("T-03", "T-15", "A-02", "A-04", "A-05")
_RELATIONSHIP_IDS = ("A-06", "A-09", "A-10", "A-13", "A-15", "T-09", "T-10")


def _choose_related(entry: ExplainabilityEntry, preferred: tuple[str, ...]) -> str:
    related = tuple(entry.related_investigations)
    for visual_id in preferred:
        if visual_id in related:
            return visual_id
    return related[0] if related else ""


def _gap_for(entry: ExplainabilityEntry, theme: str) -> str:
    if theme == "relationship":
        return "This view can highlight an association, but it cannot confirm whether the pattern persists."
    if theme == "uncertainty":
        return "This view raises a possible pattern, but the evidence is not strong enough to stand alone."
    if theme == "localized":
        return "This view can identify concentration, but not the detailed local operating cause."
    if theme in {"broad", "broad_escalation"}:
        return "This view can show broad pressure, but temporal consistency still needs confirmation."
    if theme == "validation":
        return "This view can show unevenness, but not whether the pattern repeats."
    if entry.dashboard == "aqi":
        return "This view explains environmental context, but exposure duration still matters."
    return "This view explains the current pattern, but follow-up is needed before treating it as complete."


def derive_analytical_continuity(
    entry: ExplainabilityEntry,
    context: DynamicInsightContext,
) -> AnalyticalContinuity:
    """Select one bounded continuation path from the current priority state."""

    theme = context.priority.theme
    severity = context.severity

    if theme == "localized":
        visual_id = _choose_related(entry, _LOCAL_DETAIL_IDS)
        return AnalyticalContinuity(
            primary_visual_id=visual_id,
            follow_up_reason="Because the current pattern is concentrated, local detail matters more than broad averages next.",
            unresolved_question="The next useful question is whether the same pressure appears in the related local view.",
            analytical_gap=_gap_for(entry, theme),
            suppression_fragment="Keep broad trend interpretation secondary until the local pattern is checked.",
            depth_control="A focused follow-up is enough before expanding the investigation.",
        )

    if theme in {"broad", "broad_escalation"}:
        visual_id = _choose_related(entry, _TEMPORAL_IDS)
        return AnalyticalContinuity(
            primary_visual_id=visual_id,
            follow_up_reason="Because the current pattern is broad, continuity over time matters more than one isolated hotspot.",
            unresolved_question="The next useful question is whether the broad pressure persists across periods.",
            analytical_gap=_gap_for(entry, theme),
            suppression_fragment="Keep isolated anomaly checks secondary while the wider pattern is validated.",
            depth_control="Use deeper follow-up only if the broad pattern remains visible in another view.",
        )

    if theme == "relationship":
        visual_id = _choose_related(entry, _RELATIONSHIP_IDS)
        return AnalyticalContinuity(
            primary_visual_id=visual_id,
            follow_up_reason="Because one relationship appears clearer than the rest, focused confirmation matters next.",
            unresolved_question="The next useful question is whether the same relationship remains clear in a focused view.",
            analytical_gap=_gap_for(entry, theme),
            suppression_fragment="Keep weaker relationship paths secondary until the main relationship is checked.",
            depth_control="One relationship follow-up is enough before reading the full relationship set.",
        )

    if theme in {"uncertainty", "validation"}:
        visual_id = _choose_related(entry, _TEMPORAL_IDS + _RELATIONSHIP_IDS)
        return AnalyticalContinuity(
            primary_visual_id=visual_id,
            follow_up_reason="Because the current pattern is uncertain, validation matters more than deeper interpretation.",
            unresolved_question="The next useful question is whether the pattern repeats or weakens in a related view.",
            analytical_gap=_gap_for(entry, theme),
            suppression_fragment="Keep advanced interpretation secondary until the weak pattern is validated.",
            depth_control="Avoid deep continuation if the next view also looks weak or noisy.",
        )

    if theme == "dominant_factor":
        visual_id = _choose_related(entry, _LOCAL_DETAIL_IDS + _RELATIONSHIP_IDS + _TEMPORAL_IDS)
        return AnalyticalContinuity(
            primary_visual_id=visual_id,
            follow_up_reason="Because one factor is the main reading path, the next view should confirm that factor first.",
            unresolved_question="The next useful question is whether the same factor remains important outside this view.",
            analytical_gap=_gap_for(entry, theme),
            suppression_fragment="Keep secondary factors in the background until the main factor is confirmed.",
            depth_control="Stop after one follow-up if the main factor does not remain visible.",
        )

    if severity == "mild":
        return AnalyticalContinuity(
            primary_visual_id=_choose_related(entry, tuple(entry.related_investigations)),
            follow_up_reason="Because current conditions look mild, deep investigation may not be necessary.",
            unresolved_question="The remaining question is whether a related view shows anything meaningfully different.",
            analytical_gap=_gap_for(entry, theme),
            suppression_fragment="Keep escalation paths secondary unless another view shows stronger pressure.",
            depth_control="A shallow check is enough unless the user needs more context.",
        )

    return AnalyticalContinuity(
        primary_visual_id=_choose_related(entry, tuple(entry.related_investigations)),
        follow_up_reason="The current chart gives the main reading, and the related view can test the remaining question.",
        unresolved_question=_gap_for(entry, theme),
        analytical_gap=_gap_for(entry, theme),
        suppression_fragment="Keep other follow-up paths secondary until the first related view is checked.",
        depth_control="Use one follow-up before expanding into a broader investigation.",
    )


__all__ = ["AnalyticalContinuity", "derive_analytical_continuity"]
