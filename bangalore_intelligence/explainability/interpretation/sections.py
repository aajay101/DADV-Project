"""Section assembly for structured chart interpretation metadata."""

from __future__ import annotations

from bangalore_intelligence.explainability.interpretation.layouts import InterpretationSection
from bangalore_intelligence.explainability.interpretation.situation import resolve_situation_interpretation
from bangalore_intelligence.explainability.models import ExplainabilityEntry


def interpretation_sections(entry: ExplainabilityEntry) -> tuple[InterpretationSection, ...]:
    """Return situation-centered sections for data-only interpretation consumers."""

    situation = resolve_situation_interpretation(entry)
    sections: list[InterpretationSection] = []
    sections.append(InterpretationSection("Verdict", situation.verdict))
    sections.append(InterpretationSection("Significance", situation.significance))
    sections.append(InterpretationSection("Focus Point", situation.focus_point))
    if situation.human_impact:
        sections.append(
            InterpretationSection(
                "Human Impact",
                (
                    situation.human_impact.who_is_affected,
                    situation.human_impact.what_they_experience,
                    situation.human_impact.duration_or_scope,
                ),
            )
        )
    sections.append(InterpretationSection("Pattern Consequence", situation.consequence))
    if situation.next_investigation:
        sections.append(InterpretationSection("Next Investigation", situation.next_investigation))
    sections.append(InterpretationSection("Misunderstanding Guard", situation.misunderstanding_guard))
    sections.append(InterpretationSection("Guided Reading", situation.guided_reading))
    if situation.uncertainty_note:
        sections.append(InterpretationSection("Uncertainty Note", situation.uncertainty_note))
    return tuple(sections)


__all__ = ["interpretation_sections"]
