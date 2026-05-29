"""Metadata-only helpers for related analytical visuals."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from .semantic_labels import RelationshipType, relationship_label

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = PACKAGE_ROOT.parent
for path in (PROJECT_ROOT, PACKAGE_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from bangalore_intelligence.explainability.lookup import get_explainability

if TYPE_CHECKING:
    from bangalore_intelligence.explainability.models import ExplainabilityEntry


@dataclass(frozen=True, slots=True)
class RelatedVisual:
    visual_id: str
    title: str
    relationship_type: RelationshipType
    label: str
    has_metadata: bool


_VISUAL_TITLE_FALLBACKS: dict[str, str] = {
    "T-02": "Parallel Coordinates Matrix",
    "T-05": "Road Management Priority Quadrant",
    "T-07": "Pedestrian-Adjusted Road Pressure",
    "T-08": "Incident Impact On Congestion",
    "T-09": "Speed Collapse Threshold",
    "T-10": "Public Transport Usage Comparison",
    "T-11": "Road Congestion Distribution Profiles",
    "T-13": "Area Stress Profile",
    "T-15": "Area-Month Congestion Heatmap",
    "A-06": "Pressure and Visibility PM2.5 Density",
    "A-07": "PM2.5 Category Weather Profile",
    "A-08": "Minimum Temperature vs PM2.5",
    "A-13": "Rule-Based Atmospheric Regimes",
    "A-14": "Season x Pressure Grid",
    "A-15": "Weather Variable Pairplot",
}


def related_visuals_for(entry: ExplainabilityEntry | None) -> tuple[RelatedVisual, ...]:
    """Return static related visuals for an explainability entry."""

    if entry is None or not entry.related_visuals:
        return ()

    related: list[RelatedVisual] = []
    for visual_id in entry.related_visuals:
        if not isinstance(visual_id, str) or not visual_id.strip():
            continue
        target = get_explainability(visual_id)
        label = relationship_label(entry.surface_id, visual_id)
        related.append(
            RelatedVisual(
                visual_id=visual_id,
                title=target.title if target else _VISUAL_TITLE_FALLBACKS.get(visual_id, visual_id),
                relationship_type=label.relationship_type,
                label=label.label,
                has_metadata=target is not None,
            )
        )
    return tuple(related)


__all__ = ["RelatedVisual", "related_visuals_for"]
