"""Static analytical flow hints for chart families."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bangalore_intelligence.explainability.models import ExplainabilityEntry

_TRAFFIC_FLOW = ("T-01", "T-03", "T-05", "T-09", "T-08")
_AQI_FLOW = ("A-01", "A-05", "A-06", "A-13", "A-15")

_FLOW_LABELS = {
    "T-01": "system congestion",
    "T-03": "temporal rhythm",
    "T-05": "road priority",
    "T-09": "speed-collapse threshold",
    "T-08": "incident sensitivity",
    "A-01": "PM2.5 burden",
    "A-05": "pollution persistence",
    "A-06": "atmospheric context",
    "A-13": "regime analysis",
    "A-15": "pairwise exploration",
}


def analytical_flow_hint(entry: ExplainabilityEntry | None) -> str | None:
    if entry is None:
        return None
    flow = _TRAFFIC_FLOW if entry.dashboard == "traffic" else _AQI_FLOW if entry.dashboard == "aqi" else ()
    if entry.surface_id not in flow:
        return None
    index = flow.index(entry.surface_id)
    start = max(0, index - 1)
    end = min(len(flow), index + 2)
    segment = flow[start:end]
    labels = [f"{visual_id} { _FLOW_LABELS.get(visual_id, visual_id)}" for visual_id in segment]
    return " -> ".join(labels)


__all__ = ["analytical_flow_hint"]
