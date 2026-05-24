from bangalore_intelligence.explainability.interpretation import (
    CHART_INTERPRETATION_METADATA,
    build_educational_interpretation,
    interpretation_sections,
)
from bangalore_intelligence.explainability.registry_loader import load_explainability_registry


def test_chart_info_ingestion_covers_all_chart_entries():
    registry = load_explainability_registry()

    assert set(CHART_INTERPRETATION_METADATA) == set(registry.keys())


def test_interpretation_sections_are_structured_not_markdown_blob():
    entry = load_explainability_registry()["A-05"]

    sections = interpretation_sections(entry)

    assert sections
    assert any(section.title == "Verdict" for section in sections)
    assert any(section.title == "Human Impact" for section in sections)
    assert all(section.title.strip() for section in sections)


def test_educational_payload_is_metadata_only():
    entry = load_explainability_registry()["T-09"]

    payload = build_educational_interpretation(entry)

    assert payload.surface_id == "T-09"
    assert payload.metrics == entry.metrics
    assert payload.visual_components == entry.visual_components
    assert payload.related_investigations == entry.related_investigations
