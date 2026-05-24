"""Typed metadata contracts for explainability entries."""

from __future__ import annotations

from dataclasses import dataclass, replace

from bangalore_intelligence.explainability.constants import (
    VALID_COMPLEXITY_LEVELS,
    VALID_DASHBOARDS,
    VALID_PRIORITIES,
    VALID_SURFACE_TYPES,
)

VALID_SEMANTIC_MIGRATION_STATUSES = frozenset({"legacy", "migrated"})


def _require_non_empty(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _require_string_tuple(name: str, value: tuple[str, ...]) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise ValueError(f"{name} must be a tuple of strings")
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{name} must contain only non-empty strings")
        normalized.append(item.strip())
    return tuple(normalized)


def _normalize_optional_text(name: str, value: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a string")
    return value.strip()


def _require_instance_tuple(name: str, value: tuple[object, ...], expected_type: type) -> tuple[object, ...]:
    if not isinstance(value, tuple):
        raise ValueError(f"{name} must be a tuple")
    for item in value:
        if not isinstance(item, expected_type):
            raise ValueError(f"{name} must contain only {expected_type.__name__} entries")
    return value


@dataclass(frozen=True, slots=True)
class InterpretationMetric:
    """Structured explanation for a metric or variable used in a visual."""

    name: str
    meaning: str
    why_it_matters: str
    high_values: str = ""
    low_values: str = ""
    caution: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _require_non_empty("metric.name", self.name))
        object.__setattr__(self, "meaning", _require_non_empty("metric.meaning", self.meaning))
        object.__setattr__(self, "why_it_matters", _require_non_empty("metric.why_it_matters", self.why_it_matters))
        object.__setattr__(self, "high_values", _normalize_optional_text("metric.high_values", self.high_values))
        object.__setattr__(self, "low_values", _normalize_optional_text("metric.low_values", self.low_values))
        object.__setattr__(self, "caution", _normalize_optional_text("metric.caution", self.caution))


@dataclass(frozen=True, slots=True)
class VisualComponent:
    """Structured explanation for one visual element in a chart."""

    name: str
    meaning: str
    why_it_exists: str
    what_to_notice: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _require_non_empty("component.name", self.name))
        object.__setattr__(self, "meaning", _require_non_empty("component.meaning", self.meaning))
        object.__setattr__(self, "why_it_exists", _require_non_empty("component.why_it_exists", self.why_it_exists))
        object.__setattr__(self, "what_to_notice", _require_non_empty("component.what_to_notice", self.what_to_notice))


@dataclass(frozen=True, slots=True)
class GlossaryTerm:
    """Plain-language definition for a term used by interpretation content."""

    term: str
    definition: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "term", _require_non_empty("glossary.term", self.term))
        object.__setattr__(self, "definition", _require_non_empty("glossary.definition", self.definition))


@dataclass(frozen=True, slots=True)
class HumanImpact:
    """Plain-language translation of an analytical state into lived experience."""

    who_is_affected: str
    what_they_experience: str
    duration_or_scope: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "who_is_affected", _require_non_empty("human_impact.who_is_affected", self.who_is_affected))
        object.__setattr__(
            self,
            "what_they_experience",
            _require_non_empty("human_impact.what_they_experience", self.what_they_experience),
        )
        object.__setattr__(
            self,
            "duration_or_scope",
            _require_non_empty("human_impact.duration_or_scope", self.duration_or_scope),
        )


@dataclass(frozen=True, slots=True)
class ConsequenceMapEntry:
    """Authored if/then consequence used by deterministic interpretation selection."""

    data_state: str
    consequence: str
    affected_group: str
    confidence: str = "medium"
    is_normal_state: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "data_state", _require_non_empty("consequence_map.data_state", self.data_state))
        object.__setattr__(self, "consequence", _require_non_empty("consequence_map.consequence", self.consequence))
        object.__setattr__(
            self,
            "affected_group",
            _require_non_empty("consequence_map.affected_group", self.affected_group),
        )
        object.__setattr__(self, "confidence", _require_non_empty("consequence_map.confidence", self.confidence))
        if not isinstance(self.is_normal_state, bool):
            raise ValueError("consequence_map.is_normal_state must be a boolean")


@dataclass(frozen=True, slots=True)
class ExplainabilityEntry:
    """Presentation metadata for a chart, KPI, metric, or insight surface."""

    surface_id: str
    dashboard: str
    surface_type: str
    title: str
    complexity_level: str
    priority: str
    what_this_shows: str
    why_this_visualization: str
    when_to_use: str
    decision_relevance: str
    misinterpretation_warning: str
    related_visuals: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    reading_summary: str = ""
    visualization_reason: str = ""
    metrics: tuple[InterpretationMetric, ...] = ()
    visual_components: tuple[VisualComponent, ...] = ()
    patterns: tuple[str, ...] = ()
    real_world_meaning: str = ""
    intended_interpretation: str = ""
    misunderstandings: tuple[str, ...] = ()
    glossary: tuple[GlossaryTerm, ...] = ()
    related_investigations: tuple[str, ...] = ()
    dominant_takeaway: str = ""
    situation_verdict: str = ""
    significance: str = ""
    focus_point: str = ""
    human_impact: HumanImpact | None = None
    pattern_consequence: str = ""
    next_investigation_reason: str = ""
    misunderstanding_guard: str = ""
    confidence_anchor: str = ""
    uncertainty_note: str = ""
    consequence_map: tuple[ConsequenceMapEntry, ...] = ()
    analyst_detail: tuple[str, ...] = ()
    visualization_anatomy: tuple[VisualComponent, ...] = ()
    guided_reading: str = ""
    semantic_migration_status: str = "legacy"

    def __post_init__(self) -> None:
        object.__setattr__(self, "surface_id", _require_non_empty("surface_id", self.surface_id))
        object.__setattr__(self, "dashboard", _require_non_empty("dashboard", self.dashboard))
        object.__setattr__(self, "surface_type", _require_non_empty("surface_type", self.surface_type))
        object.__setattr__(self, "title", _require_non_empty("title", self.title))
        object.__setattr__(
            self,
            "complexity_level",
            _require_non_empty("complexity_level", self.complexity_level),
        )
        object.__setattr__(self, "priority", _require_non_empty("priority", self.priority))
        object.__setattr__(self, "what_this_shows", _require_non_empty("what_this_shows", self.what_this_shows))
        object.__setattr__(
            self,
            "why_this_visualization",
            _require_non_empty("why_this_visualization", self.why_this_visualization),
        )
        object.__setattr__(self, "when_to_use", _require_non_empty("when_to_use", self.when_to_use))
        object.__setattr__(
            self,
            "decision_relevance",
            _require_non_empty("decision_relevance", self.decision_relevance),
        )
        object.__setattr__(
            self,
            "misinterpretation_warning",
            _require_non_empty("misinterpretation_warning", self.misinterpretation_warning),
        )
        object.__setattr__(self, "related_visuals", _require_string_tuple("related_visuals", self.related_visuals))
        object.__setattr__(self, "limitations", _require_string_tuple("limitations", self.limitations))
        object.__setattr__(self, "reading_summary", _normalize_optional_text("reading_summary", self.reading_summary))
        object.__setattr__(
            self,
            "visualization_reason",
            _normalize_optional_text("visualization_reason", self.visualization_reason),
        )
        object.__setattr__(self, "metrics", _require_instance_tuple("metrics", self.metrics, InterpretationMetric))
        object.__setattr__(
            self,
            "visual_components",
            _require_instance_tuple("visual_components", self.visual_components, VisualComponent),
        )
        object.__setattr__(self, "patterns", _require_string_tuple("patterns", self.patterns))
        object.__setattr__(
            self,
            "real_world_meaning",
            _normalize_optional_text("real_world_meaning", self.real_world_meaning),
        )
        object.__setattr__(
            self,
            "intended_interpretation",
            _normalize_optional_text("intended_interpretation", self.intended_interpretation),
        )
        object.__setattr__(self, "misunderstandings", _require_string_tuple("misunderstandings", self.misunderstandings))
        object.__setattr__(self, "glossary", _require_instance_tuple("glossary", self.glossary, GlossaryTerm))
        object.__setattr__(
            self,
            "related_investigations",
            _require_string_tuple("related_investigations", self.related_investigations),
        )
        object.__setattr__(self, "dominant_takeaway", _normalize_optional_text("dominant_takeaway", self.dominant_takeaway))
        object.__setattr__(self, "situation_verdict", _normalize_optional_text("situation_verdict", self.situation_verdict))
        object.__setattr__(self, "significance", _normalize_optional_text("significance", self.significance))
        object.__setattr__(self, "focus_point", _normalize_optional_text("focus_point", self.focus_point))
        if self.human_impact is not None and not isinstance(self.human_impact, HumanImpact):
            raise ValueError("human_impact must be a HumanImpact entry or None")
        object.__setattr__(
            self,
            "pattern_consequence",
            _normalize_optional_text("pattern_consequence", self.pattern_consequence),
        )
        object.__setattr__(
            self,
            "next_investigation_reason",
            _normalize_optional_text("next_investigation_reason", self.next_investigation_reason),
        )
        object.__setattr__(
            self,
            "misunderstanding_guard",
            _normalize_optional_text("misunderstanding_guard", self.misunderstanding_guard),
        )
        object.__setattr__(self, "confidence_anchor", _normalize_optional_text("confidence_anchor", self.confidence_anchor))
        object.__setattr__(self, "uncertainty_note", _normalize_optional_text("uncertainty_note", self.uncertainty_note))
        object.__setattr__(
            self,
            "consequence_map",
            _require_instance_tuple("consequence_map", self.consequence_map, ConsequenceMapEntry),
        )
        object.__setattr__(self, "analyst_detail", _require_string_tuple("analyst_detail", self.analyst_detail))
        object.__setattr__(
            self,
            "visualization_anatomy",
            _require_instance_tuple("visualization_anatomy", self.visualization_anatomy, VisualComponent),
        )
        object.__setattr__(self, "guided_reading", _normalize_optional_text("guided_reading", self.guided_reading))
        object.__setattr__(
            self,
            "semantic_migration_status",
            _require_non_empty("semantic_migration_status", self.semantic_migration_status),
        )

        if self.dashboard not in VALID_DASHBOARDS:
            raise ValueError(f"dashboard must be one of {sorted(VALID_DASHBOARDS)}")
        if self.surface_type not in VALID_SURFACE_TYPES:
            raise ValueError(f"surface_type must be one of {sorted(VALID_SURFACE_TYPES)}")
        if self.complexity_level not in VALID_COMPLEXITY_LEVELS:
            raise ValueError(f"complexity_level must be one of {sorted(VALID_COMPLEXITY_LEVELS)}")
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {sorted(VALID_PRIORITIES)}")
        if self.semantic_migration_status not in VALID_SEMANTIC_MIGRATION_STATUSES:
            raise ValueError(
                f"semantic_migration_status must be one of {sorted(VALID_SEMANTIC_MIGRATION_STATUSES)}"
            )

    def with_interpretation(
        self,
        *,
        reading_summary: str,
        visualization_reason: str,
        metrics: tuple[InterpretationMetric, ...],
        visual_components: tuple[VisualComponent, ...],
        patterns: tuple[str, ...],
        real_world_meaning: str,
        intended_interpretation: str,
        misunderstandings: tuple[str, ...],
        glossary: tuple[GlossaryTerm, ...],
        related_investigations: tuple[str, ...] = (),
        dominant_takeaway: str = "",
        situation_verdict: str = "",
        significance: str = "",
        focus_point: str = "",
        human_impact: HumanImpact | None = None,
        pattern_consequence: str = "",
        next_investigation_reason: str = "",
        misunderstanding_guard: str = "",
        confidence_anchor: str = "",
        uncertainty_note: str = "",
        consequence_map: tuple[ConsequenceMapEntry, ...] = (),
        analyst_detail: tuple[str, ...] = (),
        visualization_anatomy: tuple[VisualComponent, ...] = (),
        guided_reading: str = "",
        semantic_migration_status: str = "legacy",
    ) -> "ExplainabilityEntry":
        """Return a copy enriched with structured deep interpretation metadata."""

        return replace(
            self,
            reading_summary=reading_summary,
            visualization_reason=visualization_reason,
            metrics=metrics,
            visual_components=visual_components,
            patterns=patterns,
            real_world_meaning=real_world_meaning,
            intended_interpretation=intended_interpretation,
            misunderstandings=misunderstandings,
            glossary=glossary,
            related_investigations=related_investigations,
            dominant_takeaway=dominant_takeaway,
            situation_verdict=situation_verdict,
            significance=significance,
            focus_point=focus_point,
            human_impact=human_impact,
            pattern_consequence=pattern_consequence,
            next_investigation_reason=next_investigation_reason,
            misunderstanding_guard=misunderstanding_guard,
            confidence_anchor=confidence_anchor,
            uncertainty_note=uncertainty_note,
            consequence_map=consequence_map,
            analyst_detail=analyst_detail,
            visualization_anatomy=visualization_anatomy,
            guided_reading=guided_reading,
            semantic_migration_status=semantic_migration_status,
        )

__all__ = [
    "ConsequenceMapEntry",
    "ExplainabilityEntry",
    "GlossaryTerm",
    "HumanImpact",
    "InterpretationMetric",
    "VALID_SEMANTIC_MIGRATION_STATUSES",
    "VisualComponent",
]
