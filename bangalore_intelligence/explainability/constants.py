"""Constants for the presentation-only explainability registry."""

from __future__ import annotations

VALID_COMPLEXITY_LEVELS = frozenset({"basic", "intermediate", "advanced"})
VALID_PRIORITIES = frozenset({"low", "medium", "high"})
VALID_SURFACE_TYPES = frozenset({"chart", "kpi", "metric", "insight"})
VALID_DASHBOARDS = frozenset({"traffic", "aqi", "shared"})

TRAFFIC_CHART_IDS = tuple(f"T-{idx:02d}" for idx in range(1, 16))
AQI_CHART_IDS = tuple(f"A-{idx:02d}" for idx in range(1, 16))
KNOWN_CHART_IDS = frozenset((*TRAFFIC_CHART_IDS, *AQI_CHART_IDS))

HIGH_PRIORITY_TRAFFIC_CHART_IDS = frozenset({"T-02", "T-05", "T-09", "T-13"})
HIGH_PRIORITY_AQI_CHART_IDS = frozenset({"A-06", "A-13", "A-15"})
HIGH_PRIORITY_CHART_IDS = HIGH_PRIORITY_TRAFFIC_CHART_IDS | HIGH_PRIORITY_AQI_CHART_IDS

__all__ = [
    "AQI_CHART_IDS",
    "HIGH_PRIORITY_AQI_CHART_IDS",
    "HIGH_PRIORITY_CHART_IDS",
    "HIGH_PRIORITY_TRAFFIC_CHART_IDS",
    "KNOWN_CHART_IDS",
    "TRAFFIC_CHART_IDS",
    "VALID_COMPLEXITY_LEVELS",
    "VALID_DASHBOARDS",
    "VALID_PRIORITIES",
    "VALID_SURFACE_TYPES",
]
