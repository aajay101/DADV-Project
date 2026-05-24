"""Data-only assembly for future educational interpretation renderers."""

from __future__ import annotations

from dataclasses import dataclass

from bangalore_intelligence.explainability.interpretation.sections import interpretation_sections
from bangalore_intelligence.explainability.interpretation.situation import SituationInterpretation, resolve_situation_interpretation
from bangalore_intelligence.explainability.models import (
    ExplainabilityEntry,
    GlossaryTerm,
    InterpretationMetric,
    VisualComponent,
)


@dataclass(frozen=True, slots=True)
class EducationalInterpretation:
    """Structured payload suitable for future fullscreen interpretation UI."""

    surface_id: str
    title: str
    situation: SituationInterpretation
    sections: tuple[object, ...]
    metrics: tuple[InterpretationMetric, ...]
    visual_components: tuple[VisualComponent, ...]
    glossary: tuple[GlossaryTerm, ...]
    related_investigations: tuple[str, ...]


def build_educational_interpretation(entry: ExplainabilityEntry) -> EducationalInterpretation:
    """Build a renderable interpretation payload without Streamlit or state access."""

    return EducationalInterpretation(
        surface_id=entry.surface_id,
        title=entry.title,
        situation=resolve_situation_interpretation(entry),
        sections=interpretation_sections(entry),
        metrics=entry.metrics,
        visual_components=entry.visual_components,
        glossary=entry.glossary,
        related_investigations=entry.related_investigations,
    )


__all__ = ["EducationalInterpretation", "build_educational_interpretation"]
