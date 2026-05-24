"""Explainability trigger for chart interpretation and lightweight KPI help."""

from __future__ import annotations

from typing import Any
from typing import TYPE_CHECKING

import streamlit as st

from .explainability_renderer import render_explainability
from .styles import TRIGGER_LABEL
from bangalore_intelligence.explainability.interpretation.modal import render_interpretation_modal

if TYPE_CHECKING:
    from bangalore_intelligence.explainability.models import ExplainabilityEntry


def _has_deep_interpretation(entry: ExplainabilityEntry) -> bool:
    return bool(
        entry.surface_type == "chart"
        and entry.dominant_takeaway
        and entry.situation_verdict
        and entry.significance
        and entry.focus_point
        and entry.human_impact
        and entry.pattern_consequence
        and entry.misunderstanding_guard
    )


def render_explainability_trigger(
    entry: ExplainabilityEntry | None,
    *,
    label: str = TRIGGER_LABEL,
    fig: Any = None,
    chart_height: int = 560,
) -> None:
    """Render chart interpretation or lightweight non-chart explainability."""

    if entry is None:
        return

    if _has_deep_interpretation(entry):
        if st.button(
            f":material/school: {label}",
            key=f"interpretation_{entry.surface_id}",
            help="Open a focused explanation of what this analysis means",
        ):
            render_interpretation_modal(entry, fig=fig, chart_height=chart_height)
        return

    if entry.surface_type == "chart":
        return

    if hasattr(st, "popover"):
        with st.popover(f":material/info: {label}", help="Explain this analytical surface"):
            render_explainability(entry)
        return

    with st.expander(label, expanded=False):
        render_explainability(entry)


__all__ = ["render_explainability_trigger"]
