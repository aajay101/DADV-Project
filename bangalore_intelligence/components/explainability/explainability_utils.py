"""Lookup helpers for presentation-layer explainability components."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bangalore_intelligence.explainability.lookup import get_chart_explainability, get_kpi_explainability

if TYPE_CHECKING:
    from bangalore_intelligence.explainability.models import ExplainabilityEntry


def chart_entry(chart_id: str | None) -> ExplainabilityEntry | None:
    return get_chart_explainability(chart_id) if chart_id else None


def kpi_entry(explainability_id: str | None) -> ExplainabilityEntry | None:
    return get_kpi_explainability(explainability_id) if explainability_id else None


__all__ = ["chart_entry", "kpi_entry"]
