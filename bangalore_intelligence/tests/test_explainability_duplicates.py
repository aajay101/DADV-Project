import pytest

from bangalore_intelligence.explainability.exceptions import DuplicateExplainabilityEntryError
from bangalore_intelligence.explainability.models import (
    ExplainabilityEntry,
    GlossaryTerm,
    HumanImpact,
    InterpretationMetric,
    VisualComponent,
)
from bangalore_intelligence.explainability.validators import validate_registry_entries


def _entry(surface_id: str = "T-05") -> ExplainabilityEntry:
    return ExplainabilityEntry(
        surface_id=surface_id,
        dashboard="traffic",
        surface_type="chart",
        title="Road Management Priority Quadrant",
        complexity_level="intermediate",
        priority="high",
        what_this_shows="Roads positioned by congestion and capacity pressure.",
        why_this_visualization="Quadrant scatter compares two risk dimensions.",
        when_to_use="Use it for road priority review.",
        decision_relevance="It supports intervention prioritization.",
        misinterpretation_warning="It is descriptive, not causal proof.",
        related_visuals=("T-07", "T-09"),
        limitations=("Sparse records reduce stability.",),
        reading_summary="This chart explains road priority in plain language.",
        visualization_reason="A quadrant scatter compares congestion and capacity together.",
        metrics=(
            InterpretationMetric(
                name="Congestion",
                meaning="Traffic pressure on a road.",
                why_it_matters="It shows how strained the road is.",
            ),
        ),
        visual_components=(
            VisualComponent(
                name="Quadrant zones",
                meaning="Risk zones on the scatter plot.",
                why_it_exists="They separate lower and higher road pressure.",
                what_to_notice="Roads in the high-congestion and high-capacity zone.",
            ),
        ),
        patterns=("Upper-right roads deserve closer review.",),
        real_world_meaning="It supports road operations prioritization.",
        intended_interpretation="Users should identify roads needing follow-up.",
        misunderstandings=("The quadrant does not prove the cause of congestion.",),
        glossary=(GlossaryTerm(term="Quadrant", definition="A chart area divided by reference lines."),),
        related_investigations=("T-07",),
        dominant_takeaway="Road priority depends on both congestion and capacity pressure.",
        situation_verdict="Some roads appear more operationally fragile than others.",
        significance="Higher-pressure roads deserve closer review before lower-pressure roads.",
        focus_point="Focus first on roads in the high-congestion and high-capacity zone.",
        human_impact=HumanImpact(
            who_is_affected="People traveling through the selected road scope.",
            what_they_experience="More delay and less reliable movement on fragile roads.",
            duration_or_scope="This applies to the current filter scope.",
        ),
        pattern_consequence="Upper-right roads are likely the first candidates for follow-up.",
        next_investigation_reason="Use T-07 next to inspect road-level pressure in more detail.",
        misunderstanding_guard="This chart does not prove the cause of congestion.",
        confidence_anchor="You now know which road group deserves attention first.",
        analyst_detail=("Congestion and capacity are compared as separate risk dimensions.",),
        visualization_anatomy=(
            VisualComponent(
                name="Quadrant zones",
                meaning="Risk zones on the scatter plot.",
                why_it_exists="They separate lower and higher road pressure.",
                what_to_notice="Roads in the high-congestion and high-capacity zone.",
            ),
        ),
    )


def test_duplicate_surface_ids_are_rejected():
    with pytest.raises(DuplicateExplainabilityEntryError):
        validate_registry_entries([_entry(), _entry()])
