"""Static semantic labels for related visual transitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

RelationshipType = Literal["diagnostic", "temporal", "spatial", "threshold", "multivariate"]


@dataclass(frozen=True, slots=True)
class RelationshipLabel:
    relationship_type: RelationshipType
    label: str


_EXPLICIT_LABELS: dict[tuple[str, str], RelationshipLabel] = {
    ("T-02", "T-13"): RelationshipLabel("multivariate", "Compare area stress profile"),
    ("T-02", "T-05"): RelationshipLabel("diagnostic", "Move from area profile to road priority"),
    ("T-02", "T-07"): RelationshipLabel("spatial", "Inspect road pressure contribution"),
    ("T-05", "T-07"): RelationshipLabel("spatial", "Compare road pressure against baseline"),
    ("T-05", "T-09"): RelationshipLabel("threshold", "Investigate speed-collapse boundary"),
    ("T-05", "T-11"): RelationshipLabel("diagnostic", "Inspect road congestion distribution"),
    ("T-09", "T-05"): RelationshipLabel("diagnostic", "Return to road priority classification"),
    ("T-09", "T-08"): RelationshipLabel("threshold", "Check incident sensitivity"),
    ("T-09", "T-10"): RelationshipLabel("diagnostic", "Compare mobility mix context"),
    ("T-13", "T-02"): RelationshipLabel("multivariate", "Compare multi-axis area fingerprint"),
    ("T-13", "T-15"): RelationshipLabel("temporal", "Continue into area-month timing"),
    ("T-13", "T-05"): RelationshipLabel("diagnostic", "Connect area stress to road priority"),
    ("A-06", "A-13"): RelationshipLabel("diagnostic", "Compare atmospheric regime context"),
    ("A-06", "A-14"): RelationshipLabel("temporal", "Inspect seasonal pressure grid"),
    ("A-06", "A-07"): RelationshipLabel("multivariate", "Compare category weather profiles"),
    ("A-13", "A-06"): RelationshipLabel("diagnostic", "Return to pressure-visibility density"),
    ("A-13", "A-14"): RelationshipLabel("temporal", "Compare season-pressure structure"),
    ("A-13", "A-15"): RelationshipLabel("multivariate", "Continue multivariate exploration"),
    ("A-15", "A-06"): RelationshipLabel("diagnostic", "Ground pairwise patterns in atmospheric density"),
    ("A-15", "A-08"): RelationshipLabel("diagnostic", "Inspect temperature relationship"),
    ("A-15", "A-13"): RelationshipLabel("multivariate", "Compare against rule-based regimes"),
}

_TYPE_FALLBACK_LABELS: dict[RelationshipType, str] = {
    "diagnostic": "Investigate why this pattern exists",
    "temporal": "Continue into time-based analysis",
    "spatial": "Inspect area or road distribution",
    "threshold": "Investigate operational risk boundaries",
    "multivariate": "Expand into multidimensional exploration",
}


def relationship_label(source_id: str, target_id: str) -> RelationshipLabel:
    """Return a deterministic semantic transition label."""

    if (source_id, target_id) in _EXPLICIT_LABELS:
        return _EXPLICIT_LABELS[(source_id, target_id)]
    inferred = _infer_relationship_type(target_id)
    return RelationshipLabel(inferred, _TYPE_FALLBACK_LABELS[inferred])


def _infer_relationship_type(target_id: str) -> RelationshipType:
    if target_id in {"T-03", "T-08", "T-15", "A-02", "A-04", "A-05", "A-14"}:
        return "temporal"
    if target_id in {"T-05", "T-07", "T-11", "T-14"}:
        return "spatial"
    if target_id in {"T-09", "T-12"}:
        return "threshold"
    if target_id in {"T-02", "T-13", "A-07", "A-13", "A-15"}:
        return "multivariate"
    return "diagnostic"


__all__ = ["RelationshipLabel", "RelationshipType", "relationship_label"]
