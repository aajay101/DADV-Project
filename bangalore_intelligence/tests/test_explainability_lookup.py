import logging

from bangalore_intelligence.explainability import lookup
from bangalore_intelligence.explainability.constants import AQI_CHART_IDS, TRAFFIC_CHART_IDS
from bangalore_intelligence.explainability.lookup import (
    get_chart_explainability,
    get_chart_interpretation,
    get_explainability,
    get_kpi_explainability,
    has_explainability,
    list_dashboard_explainability,
)


def test_lookup_returns_chart_entry():
    entry = get_chart_explainability("T-05")

    assert entry is not None
    assert entry.surface_id == "T-05"
    assert entry.dashboard == "traffic"


def test_lookup_returns_deep_chart_interpretation():
    entry = get_chart_interpretation("T-05")

    assert entry is not None
    assert entry.reading_summary
    assert entry.metrics
    assert entry.visual_components
    assert entry.glossary


def test_lookup_missing_key_fails_safely():
    assert get_explainability("missing") is None
    assert get_chart_explainability("missing") is None
    assert get_kpi_explainability("missing") is None
    assert has_explainability("missing") is False


def test_dashboard_listing_is_scoped():
    traffic_entries = list_dashboard_explainability("traffic")
    aqi_entries = list_dashboard_explainability("aqi")

    assert {entry.surface_id for entry in traffic_entries} == set(TRAFFIC_CHART_IDS)
    assert {entry.surface_id for entry in aqi_entries} == set(AQI_CHART_IDS)


def test_safe_registry_logs_failure_once(monkeypatch, caplog):
    lookup._safe_registry.cache_clear()

    def fail_load(*, validate=True):
        raise ValueError("broken registry")

    monkeypatch.setattr(lookup, "load_explainability_registry", fail_load)

    with caplog.at_level(logging.ERROR, logger=lookup.logger.name):
        assert lookup.get_explainability("T-05") is None
        assert lookup.get_explainability("T-09") is None

    lookup._safe_registry.cache_clear()
    assert caplog.text.count("Explainability registry failed to load") == 1
