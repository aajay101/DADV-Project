"""Validation helpers for explainability metadata."""

from __future__ import annotations

import logging
from collections.abc import Iterable

from bangalore_intelligence.explainability.constants import KNOWN_CHART_IDS, VALID_DASHBOARDS
from bangalore_intelligence.explainability.exceptions import (
    DuplicateExplainabilityEntryError,
    ExplainabilityValidationError,
)
from bangalore_intelligence.explainability.models import ExplainabilityEntry
from bangalore_intelligence.explainability.semantic_style import semantic_style_issues
from bangalore_intelligence.explainability.interpretation.situation import (
    MAX_DYNAMIC_ITEMS_PER_VIEW,
    analyst_detail_items,
    is_semantically_migrated,
    resolve_situation_interpretation,
    visualization_anatomy_items,
)

logger = logging.getLogger(__name__)


_OVERCONFIDENT_PHRASES = (
    "definitely causes",
    "guarantees",
    "will always",
    "proves that",
    "is caused by",
)

_UNCERTAINTY_TERMS = (
    "not enough evidence",
    "insufficient",
    "unclear",
    "weak",
    "sparse",
    "unstable",
    "low-confidence",
)


def validate_entry(entry: ExplainabilityEntry) -> None:
    """Validate a single entry's cross-references and dashboard/chart consistency."""

    if entry.dashboard not in VALID_DASHBOARDS:
        raise ExplainabilityValidationError(f"{entry.surface_id}: invalid dashboard {entry.dashboard!r}")

    if entry.surface_type == "chart":
        if entry.surface_id not in KNOWN_CHART_IDS:
            raise ExplainabilityValidationError(f"{entry.surface_id}: unknown chart surface ID")
        expected_prefix = "T-" if entry.dashboard == "traffic" else "A-" if entry.dashboard == "aqi" else None
        if expected_prefix and not entry.surface_id.startswith(expected_prefix):
            raise ExplainabilityValidationError(
                f"{entry.surface_id}: chart ID does not match dashboard {entry.dashboard!r}"
            )

    for related_id in entry.related_visuals:
        if related_id not in KNOWN_CHART_IDS:
            raise ExplainabilityValidationError(
                f"{entry.surface_id}: related visual {related_id!r} is not a known chart ID"
            )
        if related_id == entry.surface_id:
            raise ExplainabilityValidationError(f"{entry.surface_id}: related visuals cannot reference self")
        if entry.surface_type == "chart" and entry.dashboard == "traffic" and not related_id.startswith("T-"):
            raise ExplainabilityValidationError(
                f"{entry.surface_id}: traffic chart cannot reference cross-dashboard visual {related_id!r}"
            )
        if entry.surface_type == "chart" and entry.dashboard == "aqi" and not related_id.startswith("A-"):
            raise ExplainabilityValidationError(
                f"{entry.surface_id}: AQI chart cannot reference cross-dashboard visual {related_id!r}"
            )

    _validate_interpretation(entry)


def _validate_interpretation(entry: ExplainabilityEntry) -> None:
    if entry.surface_type != "chart":
        return

    missing_sections = [
        name
        for name, value in (
            ("reading_summary", entry.reading_summary),
            ("visualization_reason", entry.visualization_reason),
            ("real_world_meaning", entry.real_world_meaning),
            ("intended_interpretation", entry.intended_interpretation),
        )
        if not value
    ]
    if missing_sections:
        raise ExplainabilityValidationError(
            f"{entry.surface_id}: missing interpretation sections: {', '.join(missing_sections)}"
        )

    if not entry.metrics:
        raise ExplainabilityValidationError(f"{entry.surface_id}: interpretation requires at least one metric")
    if not entry.visual_components:
        raise ExplainabilityValidationError(f"{entry.surface_id}: interpretation requires visual components")
    if not entry.patterns:
        raise ExplainabilityValidationError(f"{entry.surface_id}: interpretation requires notable patterns")
    if not entry.misunderstandings:
        raise ExplainabilityValidationError(f"{entry.surface_id}: interpretation requires misunderstandings")
    if not entry.glossary:
        raise ExplainabilityValidationError(f"{entry.surface_id}: interpretation requires glossary entries")

    terms = [item.term.lower() for item in entry.glossary]
    if len(terms) != len(set(terms)):
        raise ExplainabilityValidationError(f"{entry.surface_id}: duplicate glossary terms are not allowed")

    for related_id in entry.related_investigations:
        if related_id not in KNOWN_CHART_IDS:
            raise ExplainabilityValidationError(
                f"{entry.surface_id}: related investigation {related_id!r} is not a known chart ID"
            )
        if related_id == entry.surface_id:
            raise ExplainabilityValidationError(f"{entry.surface_id}: related investigations cannot reference self")
        if entry.dashboard == "traffic" and not related_id.startswith("T-"):
            raise ExplainabilityValidationError(
                f"{entry.surface_id}: traffic chart cannot reference cross-dashboard investigation {related_id!r}"
            )
        if entry.dashboard == "aqi" and not related_id.startswith("A-"):
            raise ExplainabilityValidationError(
                f"{entry.surface_id}: AQI chart cannot reference cross-dashboard investigation {related_id!r}"
            )

    _validate_situation_centered_content(entry)


def _validate_situation_centered_content(entry: ExplainabilityEntry) -> None:
    if not is_semantically_migrated(entry):
        return

    situation = resolve_situation_interpretation(entry)
    required = {
        "dominant_takeaway": situation.dominant_takeaway,
        "verdict": situation.verdict,
        "significance": situation.significance,
        "focus_point": situation.focus_point,
        "human_impact": situation.human_impact,
        "consequence": situation.consequence,
        "next_investigation": situation.next_investigation,
        "misunderstanding_guard": situation.misunderstanding_guard,
        "confidence_anchor": situation.confidence_anchor,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        logger.warning("%s: missing migrated situation content: %s", entry.surface_id, ", ".join(missing))
        return

    dynamic_items = (
        situation.verdict,
        situation.significance,
        situation.focus_point,
        situation.human_impact.what_they_experience if situation.human_impact else "",
        situation.consequence,
        situation.next_investigation,
    )
    if sum(bool(item) for item in dynamic_items) > MAX_DYNAMIC_ITEMS_PER_VIEW:
        logger.warning("%s: dynamic interpretation exceeds item limit", entry.surface_id)

    _validate_confidence_language(entry, dynamic_items + (situation.misunderstanding_guard,))
    _validate_uncertainty_language(entry)

    if not analyst_detail_items(entry):
        logger.warning("%s: migrated entry has no analyst_detail", entry.surface_id)
    if not tuple(visualization_anatomy_items(entry)):
        logger.warning("%s: migrated entry has no visualization_anatomy", entry.surface_id)

    if entry.consequence_map and not any(item.is_normal_state for item in entry.consequence_map):
        logger.warning("%s: consequence maps require at least one normal/good state", entry.surface_id)

    _warn_if_mechanical_semantic_copy(entry)
    _warn_if_semantic_style_drifts(entry)


def _validate_confidence_language(entry: ExplainabilityEntry, values: tuple[str, ...]) -> None:
    text = " ".join(values).lower()
    for phrase in _OVERCONFIDENT_PHRASES:
        if phrase in text:
            logger.warning("%s: overconfident interpretation phrase found: %r", entry.surface_id, phrase)


def _validate_uncertainty_language(entry: ExplainabilityEntry) -> None:
    if not entry.uncertainty_note:
        return
    note = entry.uncertainty_note.lower()
    if not any(term in note for term in _UNCERTAINTY_TERMS):
        logger.warning("%s: uncertainty note does not clearly name weak or insufficient evidence", entry.surface_id)


def _warn_if_mechanical_semantic_copy(entry: ExplainabilityEntry) -> None:
    mechanical_pairs = (
        ("dominant_takeaway", entry.dominant_takeaway, "reading_summary", entry.reading_summary),
        ("situation_verdict", entry.situation_verdict, "reading_summary", entry.reading_summary),
        ("significance", entry.significance, "real_world_meaning", entry.real_world_meaning),
        ("focus_point", entry.focus_point, "intended_interpretation", entry.intended_interpretation),
        (
            "pattern_consequence",
            entry.pattern_consequence,
            "patterns[0]",
            entry.patterns[0] if entry.patterns else "",
        ),
        (
            "misunderstanding_guard",
            entry.misunderstanding_guard,
            "misunderstandings[0]",
            entry.misunderstandings[0] if entry.misunderstandings else "",
        ),
    )
    for new_name, new_value, old_name, old_value in mechanical_pairs:
        if new_value and old_value and new_value.strip() == old_value.strip():
            logger.warning(
                "%s: migrated field %s mechanically duplicates legacy %s",
                entry.surface_id,
                new_name,
                old_name,
            )


def _warn_if_semantic_style_drifts(entry: ExplainabilityEntry) -> None:
    for issue in semantic_style_issues(entry):
        logger.warning("%s: %s: %s", entry.surface_id, issue.field, issue.message)


def validate_registry_entries(entries: Iterable[ExplainabilityEntry]) -> dict[str, ExplainabilityEntry]:
    """Validate all registry entries and return an ID-indexed registry."""

    registry: dict[str, ExplainabilityEntry] = {}
    for entry in entries:
        if entry.surface_id in registry:
            raise DuplicateExplainabilityEntryError(f"Duplicate explainability surface ID: {entry.surface_id}")
        validate_entry(entry)
        registry[entry.surface_id] = entry
    return registry


__all__ = ["validate_entry", "validate_registry_entries"]
