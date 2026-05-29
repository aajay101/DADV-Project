"""KPI explainability entries.

Phase 1 intentionally leaves KPI entries empty while establishing the registry
contract. KPI metadata can be added without changing lookup APIs.
"""

from __future__ import annotations

from bangalore_intelligence.explainability.models import ExplainabilityEntry

KPI_EXPLAINABILITY: tuple[ExplainabilityEntry, ...] = ()
