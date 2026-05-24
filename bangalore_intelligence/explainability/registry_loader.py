"""Deterministic registry loading for presentation-only explainability metadata."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from types import MappingProxyType

from bangalore_intelligence.explainability.models import ExplainabilityEntry
from bangalore_intelligence.explainability.interpretation import enrich_entries_with_chart_interpretation
from bangalore_intelligence.explainability.registry import aqi, kpis, traffic
from bangalore_intelligence.explainability.validators import validate_registry_entries


class ExplainabilityRegistry:
    """Thin immutable API boundary around explainability entries."""

    def __init__(self, entries: Mapping[str, ExplainabilityEntry]) -> None:
        self._entries: Mapping[str, ExplainabilityEntry] = MappingProxyType(dict(entries))

    def get(self, surface_id: str) -> ExplainabilityEntry | None:
        return self._entries.get(surface_id)

    def contains(self, surface_id: str) -> bool:
        return surface_id in self._entries

    def by_dashboard(self, dashboard: str) -> tuple[ExplainabilityEntry, ...]:
        return tuple(entry for entry in self._entries.values() if entry.dashboard == dashboard)

    def values(self) -> tuple[ExplainabilityEntry, ...]:
        return tuple(self._entries.values())

    def keys(self) -> tuple[str, ...]:
        return tuple(self._entries.keys())

    def items(self) -> tuple[tuple[str, ExplainabilityEntry], ...]:
        return tuple(self._entries.items())

    def __contains__(self, surface_id: object) -> bool:
        return surface_id in self._entries

    def __getitem__(self, surface_id: str) -> ExplainabilityEntry:
        return self._entries[surface_id]

    def __iter__(self) -> Iterator[str]:
        return iter(self._entries)

    def __len__(self) -> int:
        return len(self._entries)


def _registry_entries() -> tuple[ExplainabilityEntry, ...]:
    entries = (*traffic.TRAFFIC_EXPLAINABILITY, *aqi.AQI_EXPLAINABILITY, *kpis.KPI_EXPLAINABILITY)
    return enrich_entries_with_chart_interpretation(entries)


def load_explainability_registry(*, validate: bool = True) -> ExplainabilityRegistry:
    """Return a deterministic, surface-ID keyed explainability registry."""

    entries = _registry_entries()
    if validate:
        return ExplainabilityRegistry(validate_registry_entries(entries))
    return ExplainabilityRegistry({entry.surface_id: entry for entry in entries})


__all__ = ["ExplainabilityRegistry", "load_explainability_registry"]
