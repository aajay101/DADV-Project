"""Read-only explainability lookup helpers."""

from __future__ import annotations

import logging
from functools import lru_cache

from bangalore_intelligence.explainability.exceptions import ExplainabilityRegistryError
from bangalore_intelligence.explainability.interpretation.situation import is_semantically_migrated
from bangalore_intelligence.explainability.models import ExplainabilityEntry
from bangalore_intelligence.explainability.registry_loader import ExplainabilityRegistry, load_explainability_registry

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _safe_registry() -> ExplainabilityRegistry:
    try:
        return load_explainability_registry(validate=True)
    except (ExplainabilityRegistryError, ValueError):
        logger.exception("Explainability registry failed to load; metadata lookups will safely return None.")
        return ExplainabilityRegistry({})


def get_explainability(surface_id: str) -> ExplainabilityEntry | None:
    """Return metadata for any surface ID, or None when unavailable."""

    if not surface_id:
        return None
    return _safe_registry().get(surface_id)


def get_chart_explainability(chart_id: str) -> ExplainabilityEntry | None:
    """Return chart explainability metadata, or None when missing."""

    entry = get_explainability(chart_id)
    return entry if entry and entry.surface_type == "chart" else None


def get_kpi_explainability(kpi_id: str) -> ExplainabilityEntry | None:
    """Return KPI explainability metadata, or None when missing."""

    entry = get_explainability(kpi_id)
    return entry if entry and entry.surface_type == "kpi" else None


def get_chart_interpretation(chart_id: str) -> ExplainabilityEntry | None:
    """Return chart metadata only when deep interpretation fields are available."""

    entry = get_chart_explainability(chart_id)
    if not entry:
        return None
    if is_semantically_migrated(entry):
        if not (
            entry.dominant_takeaway
            and entry.situation_verdict
            and entry.significance
            and entry.focus_point
            and entry.human_impact
            and entry.pattern_consequence
            and entry.guided_reading
        ):
            return None
        return entry
    if not (entry.reading_summary and entry.metrics and entry.visual_components and entry.glossary):
        return None
    return entry


def has_explainability(surface_id: str) -> bool:
    """Return whether explainability metadata exists for a surface ID."""

    return get_explainability(surface_id) is not None


def list_dashboard_explainability(dashboard: str) -> tuple[ExplainabilityEntry, ...]:
    """Return read-only metadata entries for a dashboard."""

    return _safe_registry().by_dashboard(dashboard)


def clear_explainability_registry_cache() -> None:
    """Clear the read-only registry cache after metadata changes during development."""

    _safe_registry.cache_clear()


__all__ = [
    "clear_explainability_registry_cache",
    "get_chart_explainability",
    "get_chart_interpretation",
    "get_explainability",
    "get_kpi_explainability",
    "has_explainability",
    "list_dashboard_explainability",
]
