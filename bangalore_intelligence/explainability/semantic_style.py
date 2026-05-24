"""Semantic writing governance for migrated explainability content."""

from __future__ import annotations

from dataclasses import dataclass

from bangalore_intelligence.explainability.models import ExplainabilityEntry

CHART_FIRST_PHRASES = (
    "this chart shows",
    "this chart displays",
    "this visualization shows",
    "this visualization displays",
    "the graph indicates",
    "the chart indicates",
    "the x-axis",
    "the y-axis",
)

ANALYST_FIRST_PHRASES = (
    "multivariate",
    "z-score",
    "regression",
    "statistical significance",
    "statistically significant",
    "correlation coefficient",
    "causal inference",
    "distribution profile",
)

ARCHITECTURE_VOCABULARY = (
    "visual anchor",
    "lived context",
    "semantic",
    "signal scan",
    "interpretation focus",
    "analytical pathway",
    "exploration path",
    "priority engine",
)

CONSULTING_OR_PERFORMANCE_PHRASES = (
    "operational optimization",
    "correlation-driven inference",
    "system-level analytical pathway",
    "multidimensional exploration",
    "expand into multidimensional exploration",
    "deep dive into",
    "leverage this",
)

REPETITIVE_CAUTION_PHRASES = (
    "does not prove",
    "not proof",
    "not guarantee",
    "not enough evidence",
    "insufficient evidence",
    "weak evidence",
    "weak or noisy",
    "uncertain",
    "avoid assuming",
)

MAX_SENTENCE_WORDS = 34
MAX_SIMPLE_VISIBLE_WORDS = 235
MAX_GLOSSARY_TERMS_SIMPLE = 2
MAX_GUIDED_READING_WORDS = 55
MAX_ANALYST_DETAIL_ITEMS = 5
MAX_ANALYST_DETAIL_WORDS = 34
MAX_VISUAL_ANATOMY_ITEMS = 5
MAX_CAUTION_REFERENCES_VISIBLE = 3

FUTURE_AUTHORING_CHECKLIST = (
    "one dominant takeaway",
    "simple mode stays below the visible word limit",
    "one consequence and one next step before optional detail",
    "glossary explains only terms that cannot be replaced with plain language",
    "continuation guidance uses one follow-up path before broader investigation",
    "weak or insufficient data uses a calm fallback instead of forced meaning",
    "no chart-first narration, analyst jargon, or architecture vocabulary",
)


@dataclass(frozen=True, slots=True)
class SemanticStyleIssue:
    """A non-blocking semantic style issue found in migrated content."""

    field: str
    message: str


def _sentences(text: str) -> tuple[str, ...]:
    rough = text.replace("?", ".").replace("!", ".").split(".")
    return tuple(part.strip() for part in rough if part.strip())


def _word_count(text: str) -> int:
    return len([part for part in text.replace("-", " ").split() if part.strip()])


def _phrase_count(text: str, phrases: tuple[str, ...]) -> int:
    lowered = text.lower()
    return sum(lowered.count(phrase) for phrase in phrases)


def _visible_simple_text(entry: ExplainabilityEntry) -> tuple[tuple[str, str], ...]:
    impact = entry.human_impact
    impact_text = ""
    if impact is not None:
        impact_text = " ".join((impact.who_is_affected, impact.what_they_experience, impact.duration_or_scope))
    return (
        ("dominant_takeaway", entry.dominant_takeaway),
        ("situation_verdict", entry.situation_verdict),
        ("significance", entry.significance),
        ("focus_point", entry.focus_point),
        ("human_impact", impact_text),
        ("pattern_consequence", entry.pattern_consequence),
        ("next_investigation_reason", entry.next_investigation_reason),
        ("misunderstanding_guard", entry.misunderstanding_guard),
        ("uncertainty_note", entry.uncertainty_note),
    )


def semantic_style_issues(entry: ExplainabilityEntry) -> tuple[SemanticStyleIssue, ...]:
    """Return non-blocking style issues for migrated chart entries."""

    issues: list[SemanticStyleIssue] = []
    visible = _visible_simple_text(entry)
    for field, text in visible + (("guided_reading", entry.guided_reading),):
        lowered = text.lower()
        for phrase in CHART_FIRST_PHRASES:
            if phrase in lowered:
                issues.append(SemanticStyleIssue(field, f"chart-first phrase found: {phrase!r}"))
        for phrase in ANALYST_FIRST_PHRASES:
            if phrase in lowered:
                issues.append(SemanticStyleIssue(field, f"analyst-first phrase found: {phrase!r}"))
        for phrase in ARCHITECTURE_VOCABULARY:
            if phrase in lowered:
                issues.append(SemanticStyleIssue(field, f"architecture vocabulary found: {phrase!r}"))
        for phrase in CONSULTING_OR_PERFORMANCE_PHRASES:
            if phrase in lowered:
                issues.append(SemanticStyleIssue(field, f"consulting-style phrase found: {phrase!r}"))
        for sentence in _sentences(text):
            if _word_count(sentence) > MAX_SENTENCE_WORDS:
                issues.append(SemanticStyleIssue(field, "sentence is too dense for beginner-first reading"))

    total_words = sum(_word_count(text) for _, text in visible if text)
    if total_words > MAX_SIMPLE_VISIBLE_WORDS:
        issues.append(SemanticStyleIssue("simple_mode", "visible Simple Mode text is too dense"))

    if len(entry.glossary) > MAX_GLOSSARY_TERMS_SIMPLE + 3:
        issues.append(SemanticStyleIssue("glossary", "glossary may be carrying too much interpretation weight"))

    caution_count = _phrase_count(" ".join(text for _, text in visible if text), REPETITIVE_CAUTION_PHRASES)
    if caution_count > MAX_CAUTION_REFERENCES_VISIBLE:
        issues.append(SemanticStyleIssue("simple_mode", "visible explanation repeats caution language too often"))

    if entry.guided_reading and _word_count(entry.guided_reading) > MAX_GUIDED_READING_WORDS:
        issues.append(SemanticStyleIssue("guided_reading", "guided reading is too long for optional learning"))

    if len(entry.analyst_detail) > MAX_ANALYST_DETAIL_ITEMS:
        issues.append(SemanticStyleIssue("analyst_detail", "analyst detail has too many items for a secondary layer"))
    for idx, item in enumerate(entry.analyst_detail, start=1):
        if _word_count(item) > MAX_ANALYST_DETAIL_WORDS:
            issues.append(SemanticStyleIssue("analyst_detail", f"detail {idx} is too dense"))

    if len(entry.visualization_anatomy) > MAX_VISUAL_ANATOMY_ITEMS:
        issues.append(SemanticStyleIssue("visualization_anatomy", "visual anatomy has too many visible cues"))

    if entry.dominant_takeaway and entry.dominant_takeaway in (
        entry.situation_verdict,
        entry.significance,
        entry.pattern_consequence,
    ):
        issues.append(SemanticStyleIssue("dominant_takeaway", "dominant takeaway is repeated instead of developed"))

    return tuple(issues)


__all__ = [
    "ANALYST_FIRST_PHRASES",
    "ARCHITECTURE_VOCABULARY",
    "CHART_FIRST_PHRASES",
    "CONSULTING_OR_PERFORMANCE_PHRASES",
    "FUTURE_AUTHORING_CHECKLIST",
    "MAX_ANALYST_DETAIL_ITEMS",
    "MAX_ANALYST_DETAIL_WORDS",
    "MAX_CAUTION_REFERENCES_VISIBLE",
    "MAX_GUIDED_READING_WORDS",
    "MAX_GLOSSARY_TERMS_SIMPLE",
    "MAX_SENTENCE_WORDS",
    "MAX_SIMPLE_VISIBLE_WORDS",
    "MAX_VISUAL_ANATOMY_ITEMS",
    "REPETITIVE_CAUTION_PHRASES",
    "SemanticStyleIssue",
    "semantic_style_issues",
]
