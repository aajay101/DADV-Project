"""Reading mode policy for interpretation renderers."""

from __future__ import annotations

from dataclasses import dataclass

READING_MODE_SIMPLE = "Simple Mode"
READING_MODE_ANALYTICAL = "Analytical Mode"
READING_MODE_OPERATIONAL = "Operational Mode"

VALID_READING_MODES = (READING_MODE_SIMPLE, READING_MODE_ANALYTICAL, READING_MODE_OPERATIONAL)


@dataclass(frozen=True, slots=True)
class ReadingModePolicy:
    """Rendering policy for a lightweight reading mode."""

    mode: str
    audience: str
    emphasis: str
    pattern_limit: int | None
    glossary_preview_count: int
    expand_metrics: bool
    expand_components: bool
    show_misunderstandings: bool
    show_limitations: bool
    show_analyst_detail: bool
    show_visualization_anatomy: bool
    simple_statement_limit: int


_POLICIES = {
    READING_MODE_SIMPLE: ReadingModePolicy(
        mode=READING_MODE_SIMPLE,
        audience="General public and students",
        emphasis="Quick intuition, plain meaning, and why the chart matters.",
        pattern_limit=2,
        glossary_preview_count=2,
        expand_metrics=False,
        expand_components=False,
        show_misunderstandings=False,
        show_limitations=False,
        show_analyst_detail=False,
        show_visualization_anatomy=False,
        simple_statement_limit=6,
    ),
    READING_MODE_ANALYTICAL: ReadingModePolicy(
        mode=READING_MODE_ANALYTICAL,
        audience="Students, researchers, and analysts",
        emphasis="Metrics, components, patterns, and analytical nuance.",
        pattern_limit=None,
        glossary_preview_count=3,
        expand_metrics=True,
        expand_components=True,
        show_misunderstandings=True,
        show_limitations=True,
        show_analyst_detail=True,
        show_visualization_anatomy=True,
        simple_statement_limit=12,
    ),
    READING_MODE_OPERATIONAL: ReadingModePolicy(
        mode=READING_MODE_OPERATIONAL,
        audience="Planners, decision-makers, and operational stakeholders",
        emphasis="City impact, operational consequences, and where to investigate next.",
        pattern_limit=3,
        glossary_preview_count=2,
        expand_metrics=False,
        expand_components=False,
        show_misunderstandings=True,
        show_limitations=True,
        show_analyst_detail=False,
        show_visualization_anatomy=False,
        simple_statement_limit=7,
    ),
}


def reading_mode_policy(mode: str | None) -> ReadingModePolicy:
    """Return a rendering policy, defaulting to Simple Mode for safety."""

    return _POLICIES.get(mode or READING_MODE_SIMPLE, _POLICIES[READING_MODE_SIMPLE])


__all__ = [
    "READING_MODE_ANALYTICAL",
    "READING_MODE_OPERATIONAL",
    "READING_MODE_SIMPLE",
    "ReadingModePolicy",
    "VALID_READING_MODES",
    "reading_mode_policy",
]
