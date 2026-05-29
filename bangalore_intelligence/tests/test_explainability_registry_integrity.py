import pytest

from bangalore_intelligence.explainability.constants import HIGH_PRIORITY_CHART_IDS
from bangalore_intelligence.explainability.registry_loader import load_explainability_registry


def test_registry_loads_high_priority_chart_entries():
    registry = load_explainability_registry()

    assert HIGH_PRIORITY_CHART_IDS.issubset(set(registry))
    assert {"T-01", "T-03"}.issubset(set(registry))
    assert all(entry.surface_type == "chart" for entry in registry.values())
    assert all(registry[chart_id].priority == "high" for chart_id in HIGH_PRIORITY_CHART_IDS)


def test_registry_is_read_only():
    registry = load_explainability_registry()

    with pytest.raises(TypeError):
        registry["T-02"] = registry["T-02"]  # type: ignore[index]


def test_registry_entries_have_required_explanatory_text():
    registry = load_explainability_registry()

    for entry in registry.values():
        assert entry.what_this_shows.strip()
        assert entry.why_this_visualization.strip()
        assert entry.when_to_use.strip()
        assert entry.decision_relevance.strip()
        assert entry.misinterpretation_warning.strip()
        assert entry.limitations


def test_chart_registry_entries_have_structured_interpretation_metadata():
    registry = load_explainability_registry()

    for entry in registry.values():
        assert entry.reading_summary.strip()
        assert entry.visualization_reason.strip()
        assert entry.metrics
        assert entry.visual_components
        assert entry.patterns
        assert entry.real_world_meaning.strip()
        assert entry.intended_interpretation.strip()
        assert entry.misunderstandings
        assert entry.glossary
        assert entry.related_investigations


def test_migrated_charts_use_authored_situation_content():
    registry = load_explainability_registry()

    migrated_chart_ids = (
        "T-02",
        "T-01",
        "A-05",
        "T-03",
        "T-05",
        "A-01",
        "A-06",
        "T-04",
        "T-06",
        "T-07",
        "T-08",
        "T-09",
        "T-10",
        "T-11",
        "T-12",
        "T-14",
        "T-15",
        "A-02",
        "A-03",
        "A-04",
        "A-07",
        "A-08",
        "A-09",
        "A-10",
        "A-11",
        "A-12",
        "A-14",
        "T-13",
        "A-13",
        "A-15",
    )

    for chart_id in migrated_chart_ids:
        entry = registry[chart_id]
        assert entry.semantic_migration_status == "migrated"
        assert entry.dominant_takeaway != entry.reading_summary
        assert entry.situation_verdict != entry.reading_summary
        assert entry.significance != entry.real_world_meaning
        assert entry.focus_point != entry.intended_interpretation
        assert entry.pattern_consequence != entry.patterns[0]
        assert entry.misunderstanding_guard != entry.misunderstandings[0]
        assert entry.guided_reading
        assert entry.human_impact is not None


def test_special_cognition_charts_are_migrated():
    registry = load_explainability_registry()

    for chart_id in ("T-02", "T-13", "A-13", "A-15"):
        entry = registry[chart_id]
        assert entry.semantic_migration_status == "migrated"
        assert entry.guided_reading
