import pytest

from bangalore_intelligence.explainability.exceptions import ExplainabilityValidationError
from bangalore_intelligence.explainability.models import (
    ConsequenceMapEntry,
    ExplainabilityEntry,
    GlossaryTerm,
    HumanImpact,
    InterpretationMetric,
    VisualComponent,
)
from bangalore_intelligence.explainability.validators import validate_entry


def _interpretation():
    return {
        "reading_summary": "This chart explains road priority in plain language.",
        "visualization_reason": "A quadrant scatter compares congestion and capacity together.",
        "metrics": (
            InterpretationMetric(
                name="Congestion",
                meaning="Traffic pressure on a road.",
                why_it_matters="It shows how strained the road is.",
            ),
        ),
        "visual_components": (
            VisualComponent(
                name="Quadrant zones",
                meaning="Risk zones on the scatter plot.",
                why_it_exists="They separate lower and higher road pressure.",
                what_to_notice="Roads in the high-congestion and high-capacity zone.",
            ),
        ),
        "patterns": ("Upper-right roads deserve closer review.",),
        "real_world_meaning": "It supports road operations prioritization.",
        "intended_interpretation": "Users should identify roads needing follow-up.",
        "misunderstandings": ("The quadrant does not prove the cause of congestion.",),
        "glossary": (
            GlossaryTerm(term="Quadrant", definition="A chart area divided by reference lines."),
        ),
        "related_investigations": ("T-07",),
    }


def _entry(**overrides):
    data = {
        "surface_id": "T-05",
        "dashboard": "traffic",
        "surface_type": "chart",
        "title": "Road Management Priority Quadrant",
        "complexity_level": "intermediate",
        "priority": "high",
        "what_this_shows": "Roads positioned by congestion and capacity pressure.",
        "why_this_visualization": "Quadrant scatter compares two risk dimensions.",
        "when_to_use": "Use it for road priority review.",
        "decision_relevance": "It supports intervention prioritization.",
        "misinterpretation_warning": "It is descriptive, not causal proof.",
        "related_visuals": ("T-07", "T-09"),
        "limitations": ("Sparse records reduce stability.",),
        **_interpretation(),
    }
    data.update(overrides)
    return ExplainabilityEntry(**data)


def _migrated_entry(**overrides):
    data = {
        "semantic_migration_status": "migrated",
        "dominant_takeaway": "Road pressure is concentrated enough to prioritize the highest-risk roads first.",
        "situation_verdict": "Some roads appear operationally fragile in the selected traffic scope.",
        "significance": "That matters because delay risk is more useful when tied to specific roads.",
        "focus_point": "Start with roads that combine congestion and capacity pressure.",
        "human_impact": HumanImpact(
            who_is_affected="People traveling through the selected road scope.",
            what_they_experience="Trips may feel slower and less predictable around fragile roads.",
            duration_or_scope="This applies to the current filter scope.",
        ),
        "pattern_consequence": "Upper-right roads are likely the first candidates for follow-up.",
        "next_investigation_reason": "Use T-07 next to inspect road-level pressure in more detail.",
        "misunderstanding_guard": "This does not prove the cause of congestion.",
        "confidence_anchor": "You now know which road group deserves attention first.",
        "analyst_detail": ("Congestion and capacity are compared as separate risk dimensions.",),
        "visualization_anatomy": (
            VisualComponent(
                name="Quadrant zones",
                meaning="Risk zones on the scatter plot.",
                why_it_exists="They separate lower and higher road pressure.",
                what_to_notice="Roads in the high-congestion and high-capacity zone.",
            ),
        ),
        "guided_reading": "Look for roads that are both crowded and near capacity before reading deeper details.",
    }
    data.update(overrides)
    return _entry(**data)


def test_invalid_complexity_level_is_rejected():
    with pytest.raises(ValueError):
        _entry(complexity_level="expert")


def test_invalid_priority_is_rejected():
    with pytest.raises(ValueError):
        _entry(priority="urgent")


def test_invalid_dashboard_is_rejected():
    with pytest.raises(ValueError):
        _entry(dashboard="mobility")


def test_empty_required_text_is_rejected():
    with pytest.raises(ValueError):
        _entry(what_this_shows=" ")


def test_missing_required_field_is_rejected():
    with pytest.raises(TypeError):
        ExplainabilityEntry(
            surface_id="T-05",
            dashboard="traffic",
            surface_type="chart",
            title="Road Management Priority Quadrant",
            complexity_level="intermediate",
            priority="high",
            what_this_shows="Roads positioned by congestion and capacity pressure.",
            why_this_visualization="Quadrant scatter compares two risk dimensions.",
            when_to_use="Use it for road priority review.",
            decision_relevance="It supports intervention prioritization.",
            related_visuals=("T-07", "T-09"),
            limitations=("Sparse records reduce stability.",),
        )


def test_malformed_related_visuals_are_rejected():
    with pytest.raises(ValueError):
        _entry(related_visuals=("T-07", ""))


def test_unknown_related_visual_is_rejected():
    entry = _entry(related_visuals=("T-99",))

    with pytest.raises(ExplainabilityValidationError):
        validate_entry(entry)


def test_chart_id_must_match_dashboard():
    entry = _entry(surface_id="A-06", dashboard="traffic", related_visuals=("T-07",))

    with pytest.raises(ExplainabilityValidationError):
        validate_entry(entry)


def test_cross_dashboard_related_visual_is_rejected():
    entry = _entry(related_visuals=("A-06",))

    with pytest.raises(ExplainabilityValidationError):
        validate_entry(entry)


def test_missing_interpretation_sections_are_rejected():
    entry = _entry(reading_summary="")

    with pytest.raises(ExplainabilityValidationError):
        validate_entry(entry)


def test_missing_metrics_are_rejected():
    entry = _entry(metrics=())

    with pytest.raises(ExplainabilityValidationError):
        validate_entry(entry)


def test_missing_components_are_rejected():
    entry = _entry(visual_components=())

    with pytest.raises(ExplainabilityValidationError):
        validate_entry(entry)


def test_duplicate_glossary_terms_are_rejected():
    entry = _entry(
        glossary=(
            GlossaryTerm(term="Threshold", definition="A reference level."),
            GlossaryTerm(term="threshold", definition="Duplicate reference level."),
        )
    )

    with pytest.raises(ExplainabilityValidationError):
        validate_entry(entry)


def test_invalid_related_investigation_is_rejected():
    entry = _entry(related_investigations=("A-06",))

    with pytest.raises(ExplainabilityValidationError):
        validate_entry(entry)


def test_overconfident_situation_language_warns_for_migrated_chart(caplog):
    entry = _migrated_entry(situation_verdict="This proves that congestion is caused by roadwork.")

    validate_entry(entry)

    assert "overconfident interpretation phrase found" in caplog.text


def test_uncertainty_note_warns_when_not_confidence_aware(caplog):
    entry = _migrated_entry(uncertainty_note="Review this chart carefully before drawing conclusions.")

    validate_entry(entry)

    assert "uncertainty note does not clearly name weak or insufficient evidence" in caplog.text


def test_consequence_map_missing_normal_state_warns_for_migrated_chart(caplog):
    entry = _migrated_entry(
        consequence_map=(
            ConsequenceMapEntry(
                data_state="High congestion",
                consequence="Delay risk becomes more relevant.",
                affected_group="Road users",
            ),
        )
    )

    validate_entry(entry)

    assert "consequence maps require at least one normal/good state" in caplog.text


def test_mechanical_semantic_copy_warns_for_migrated_chart(caplog):
    entry = _migrated_entry(dominant_takeaway="This chart explains road priority in plain language.")

    validate_entry(entry)

    assert "mechanically duplicates legacy reading_summary" in caplog.text


def test_consulting_style_language_warns_for_migrated_chart(caplog):
    entry = _migrated_entry(
        next_investigation_reason="Expand into multidimensional exploration for operational optimization."
    )

    validate_entry(entry)

    assert "consulting-style phrase found" in caplog.text


def test_repeated_caution_language_warns_for_migrated_chart(caplog):
    entry = _migrated_entry(
        misunderstanding_guard="This does not prove cause and is not proof of a permanent issue.",
        uncertainty_note="There is not enough evidence and insufficient evidence for a firm conclusion.",
    )

    validate_entry(entry)

    assert "visible explanation repeats caution language too often" in caplog.text


def test_oversized_optional_learning_warns_for_migrated_chart(caplog):
    entry = _migrated_entry(
        guided_reading=(
            "Start with the road group that looks most fragile, then compare every surrounding pattern "
            "carefully across congestion, capacity, speed, location, vehicle mix, delay risk, operational "
            "scope, related context, boundary conditions, and follow-up evidence before deciding what matters. "
            "Then repeat the same review for secondary patterns, historical context, adjacent roads, and "
            "possible edge cases before opening the next related view."
        ),
        analyst_detail=(
            "This detail explains a boundary condition.",
            "This detail explains another boundary condition.",
            "This detail explains a third boundary condition.",
            "This detail explains a fourth boundary condition.",
            "This detail explains a fifth boundary condition.",
            "This detail explains a sixth boundary condition.",
        ),
    )

    validate_entry(entry)

    assert "guided reading is too long for optional learning" in caplog.text
    assert "analyst detail has too many items for a secondary layer" in caplog.text
