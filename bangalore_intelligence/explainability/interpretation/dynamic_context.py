"""Bounded state-aware interpretation helpers.

This module derives small analytical state labels from the current rendered
figure. It never generates freeform prose; it only selects from fixed,
governed fragments that can be inserted beside authored interpretation copy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite, sqrt
from numbers import Number
from statistics import mean, pstdev
from typing import Any

from bangalore_intelligence.explainability.models import ExplainabilityEntry


@dataclass(frozen=True, slots=True)
class InterpretationPriority:
    """Deterministic emphasis selection for the current analytical state."""

    theme: str = "baseline"
    emphasis_fragment: str = ""
    suppression_fragment: str = ""
    next_step_fragment: str = ""
    uncertainty_fragment: str = ""
    intensity: str = "neutral"


@dataclass(frozen=True, slots=True)
class DynamicInsightContext:
    """Small deterministic state summary for the current chart view."""

    severity: str = "unknown"
    concentration: str = "unknown"
    stability: str = "unknown"
    relationship_strength: str = "unknown"
    dominant_factor: str = ""
    scope_phrase: str = "Within the current filtered view"
    priority: InterpretationPriority = field(default_factory=InterpretationPriority)
    state_fragments: tuple[str, ...] = ()
    next_step_fragment: str = ""


def _flatten_numeric(value: Any) -> tuple[float, ...]:
    if value is None:
        return ()
    if isinstance(value, Number):
        number = float(value)
        return (number,) if isfinite(number) else ()
    if isinstance(value, str):
        return ()
    try:
        items = list(value)
    except TypeError:
        return ()
    flattened: list[float] = []
    for item in items:
        flattened.extend(_flatten_numeric(item))
    return tuple(flattened)


def _trace_values(fig: Any) -> tuple[float, ...]:
    values: list[float] = []
    for trace in getattr(fig, "data", ()) or ():
        for attr in ("y", "z", "r", "values"):
            values.extend(_flatten_numeric(getattr(trace, attr, None)))
    return tuple(values)


def _severity(values: tuple[float, ...]) -> str:
    if not values:
        return "unknown"
    high = max(values)
    avg = mean(values)
    if high >= 90 or avg >= 75:
        return "severe"
    if high >= 70 or avg >= 50:
        return "moderate"
    return "mild"


def _concentration(values: tuple[float, ...]) -> str:
    positive = [value for value in values if value > 0]
    if len(positive) < 3:
        return "unknown"
    total = sum(positive)
    if total <= 0:
        return "unknown"
    ordered = sorted(positive, reverse=True)
    top_share = sum(ordered[: max(1, min(2, len(ordered)))]) / total
    if top_share >= 0.55:
        return "concentrated"
    if top_share <= 0.35:
        return "distributed"
    return "mixed"


def _stability(values: tuple[float, ...]) -> str:
    if len(values) < 4:
        return "unknown"
    avg = abs(mean(values))
    if avg < 1:
        return "unknown"
    variation = pstdev(values) / avg
    if variation >= 0.45:
        return "unstable"
    if variation <= 0.18:
        return "stable"
    return "mixed"


def _pearson(xs: tuple[float, ...], ys: tuple[float, ...]) -> float | None:
    count = min(len(xs), len(ys))
    if count < 5:
        return None
    xs = xs[:count]
    ys = ys[:count]
    x_mean = mean(xs)
    y_mean = mean(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys, strict=False))
    x_var = sum((x - x_mean) ** 2 for x in xs)
    y_var = sum((y - y_mean) ** 2 for y in ys)
    denominator = sqrt(x_var * y_var)
    if denominator == 0:
        return None
    return numerator / denominator


def _relationship_strength(fig: Any) -> str:
    for trace in getattr(fig, "data", ()) or ():
        trace_type = str(getattr(trace, "type", "")).lower()
        if trace_type not in {"scatter", "scattergl"}:
            continue
        xs = _flatten_numeric(getattr(trace, "x", None))
        ys = _flatten_numeric(getattr(trace, "y", None))
        corr = _pearson(xs, ys)
        if corr is None:
            continue
        strength = abs(corr)
        if strength >= 0.65:
            return "strong"
        if strength >= 0.35:
            return "partial"
        return "weak"
    return "unknown"


def _dominant_factor(entry: ExplainabilityEntry, values: tuple[float, ...], fig: Any) -> str:
    if entry.surface_id in {"T-02", "T-13"}:
        return "congestion, speed, and capacity"
    if entry.surface_id in {"A-06", "A-13", "A-15"}:
        return "PM2.5 with visibility or pressure"
    if entry.dashboard == "aqi":
        return "PM2.5"
    if entry.dashboard == "traffic":
        return "congestion pressure"
    return ""


def _scope_phrase(entry: ExplainabilityEntry) -> str:
    if entry.dashboard == "aqi":
        return "Within the selected AQI scope"
    if entry.dashboard == "traffic":
        return "Within the selected traffic scope"
    return "Within the current filtered view"


def _state_fragments(context: DynamicInsightContext) -> tuple[str, ...]:
    fragments: list[str] = []
    if context.severity == "severe":
        fragments.append(f"{context.scope_phrase}, conditions appear operationally severe.")
    elif context.severity == "moderate":
        fragments.append(f"{context.scope_phrase}, conditions appear elevated but not uniformly severe.")
    elif context.severity == "mild":
        fragments.append(f"{context.scope_phrase}, conditions appear relatively mild.")

    if context.concentration == "concentrated":
        fragments.append("The current pattern appears concentrated rather than evenly spread.")
    elif context.concentration == "distributed":
        fragments.append("The current pattern appears broadly distributed across the view.")

    if context.relationship_strength == "strong":
        fragments.append("The main relationship appears tightly linked enough to deserve focused follow-up.")
    elif context.relationship_strength == "partial":
        fragments.append("The main relationship appears partial, so it should be checked in a related view.")
    elif context.relationship_strength == "weak":
        fragments.append("The main relationship appears weak or noisy, so avoid treating it as a strong signal.")

    if context.dominant_factor:
        fragments.append(f"Start with {context.dominant_factor} before reading secondary details.")

    if context.stability == "unstable":
        fragments.append("Values appear uneven, so temporary spikes may be part of the story.")
    elif context.stability == "stable":
        fragments.append("Values appear relatively stable, so repeated conditions may matter more than isolated spikes.")

    return tuple(fragments[:4])


def _next_step(context: DynamicInsightContext) -> str:
    if context.priority.next_step_fragment:
        return context.priority.next_step_fragment
    if context.relationship_strength == "strong":
        return "Use the next view to check whether the same relationship remains clear in a focused context."
    if context.relationship_strength in {"weak", "partial"}:
        return "Use the next view to check whether this relationship holds in a more focused context."
    if context.concentration == "concentrated":
        return "Use the next view to check whether the same pressure stays localized."
    if context.concentration == "distributed":
        return "Use the next view to check whether the broad pattern also appears over time."
    if context.stability == "unstable":
        return "Use the next view to check whether this is a temporary spike or a repeated condition."
    return ""


def _priority(context: DynamicInsightContext) -> InterpretationPriority:
    """Select one dominant interpretation emphasis from bounded state labels."""

    intensity = "escalated" if context.severity == "severe" else "calm"
    if context.relationship_strength == "weak":
        return InterpretationPriority(
            theme="uncertainty",
            emphasis_fragment="Weak or noisy relationships should control the reading before any stronger conclusion.",
            suppression_fragment="Suppress detailed relationship interpretation until the pattern is checked elsewhere.",
            next_step_fragment="Use the next view to validate the relationship before treating it as meaningful.",
            uncertainty_fragment="Uncertainty deserves higher visibility because the relationship is weak.",
            intensity="cautious",
        )
    if context.concentration == "concentrated":
        return InterpretationPriority(
            theme="localized",
            emphasis_fragment="Localized interpretation matters most because the current pattern is concentrated.",
            suppression_fragment="Suppress broad-system framing until the concentrated pressure is checked locally.",
            next_step_fragment="Use the next view to check whether the same issue stays localized.",
            intensity=intensity,
        )
    if context.severity == "severe" and context.concentration == "distributed":
        return InterpretationPriority(
            theme="broad_escalation",
            emphasis_fragment="Broad interpretation matters most because severe conditions appear distributed.",
            suppression_fragment="Suppress isolated-hotspot framing while the wider pattern is checked.",
            next_step_fragment="Use the next view to check whether broad stress also persists over time.",
            intensity="escalated",
        )
    if context.relationship_strength == "strong":
        return InterpretationPriority(
            theme="relationship",
            emphasis_fragment="Relationship follow-up matters most because the current pattern appears clearly linked.",
            suppression_fragment="Suppress weaker secondary relationships until this primary relationship is checked.",
            next_step_fragment="Use the next view to check whether the same relationship remains clear in a focused context.",
            intensity=intensity,
        )
    if context.stability == "unstable":
        return InterpretationPriority(
            theme="validation",
            emphasis_fragment="Validation matters most because the current pattern appears uneven.",
            suppression_fragment="Suppress stable-pattern interpretation until temporary spikes are ruled out.",
            next_step_fragment="Use the next view to check whether this is a temporary spike or a repeated condition.",
            uncertainty_fragment="Uncertainty deserves more visibility because the pattern is unstable.",
            intensity="cautious",
        )
    if context.concentration == "distributed":
        return InterpretationPriority(
            theme="broad",
            emphasis_fragment="Broad interpretation matters most because the pattern is distributed across the view.",
            suppression_fragment="Suppress isolated-hotspot framing unless a related view confirms it.",
            next_step_fragment="Use the next view to check whether the broad pattern also appears over time.",
            intensity=intensity,
        )
    if context.dominant_factor:
        return InterpretationPriority(
            theme="dominant_factor",
            emphasis_fragment=f"{context.dominant_factor} should stay as the main reading path.",
            suppression_fragment="Suppress secondary-factor detail until the main factor is understood.",
            next_step_fragment="Use the next view to check whether the same main factor remains important.",
            intensity=intensity,
        )
    return InterpretationPriority()


def derive_dynamic_insight_context(entry: ExplainabilityEntry, fig: Any = None) -> DynamicInsightContext:
    """Derive bounded current-view states from a rendered Plotly figure."""

    if fig is None:
        base = DynamicInsightContext(dominant_factor=_dominant_factor(entry, (), fig), scope_phrase=_scope_phrase(entry))
        priority = _priority(base)
        return DynamicInsightContext(
            dominant_factor=base.dominant_factor,
            scope_phrase=base.scope_phrase,
            priority=priority,
            next_step_fragment=_next_step(DynamicInsightContext(priority=priority)),
        )

    values = _trace_values(fig)
    relationship = _relationship_strength(fig)
    base = DynamicInsightContext(
        severity=_severity(values),
        concentration=_concentration(values),
        stability=_stability(values),
        relationship_strength=relationship,
        dominant_factor=_dominant_factor(entry, values, fig),
        scope_phrase=_scope_phrase(entry),
    )
    priority = _priority(base)
    resolved = DynamicInsightContext(
        severity=base.severity,
        concentration=base.concentration,
        stability=base.stability,
        relationship_strength=base.relationship_strength,
        dominant_factor=base.dominant_factor,
        scope_phrase=base.scope_phrase,
        priority=priority,
        state_fragments=_state_fragments(base),
    )
    return DynamicInsightContext(
        severity=resolved.severity,
        concentration=resolved.concentration,
        stability=resolved.stability,
        relationship_strength=resolved.relationship_strength,
        dominant_factor=resolved.dominant_factor,
        scope_phrase=resolved.scope_phrase,
        priority=resolved.priority,
        state_fragments=resolved.state_fragments,
        next_step_fragment=_next_step(resolved),
    )


__all__ = ["DynamicInsightContext", "InterpretationPriority", "derive_dynamic_insight_context"]
