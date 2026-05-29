"""Reusable passive explainability renderer."""

from __future__ import annotations

from typing import TYPE_CHECKING

import streamlit as st

from .explainability_layout import layout_for_complexity
from .explainability_sections import (
    render_limitations,
    render_text_section,
    render_warning,
)
from ..related_analysis import render_analytical_flow_hint, render_related_visuals

if TYPE_CHECKING:
    from bangalore_intelligence.explainability.models import ExplainabilityEntry


def render_explainability(entry: ExplainabilityEntry | None) -> None:
    """Render explainability metadata without mutating analytical state."""

    if entry is None:
        return

    layout = layout_for_complexity(entry.complexity_level)

    st.markdown(f"**{entry.title}**")
    render_text_section("What this shows", entry.what_this_shows)

    if not layout.compact:
        render_text_section("Why this visualization exists", entry.why_this_visualization)

    render_text_section("When to use this visual", entry.when_to_use)

    if layout.show_decision_relevance:
        render_text_section("Why it matters", entry.decision_relevance)

    render_warning(entry)
    render_limitations(entry, collapsed=layout.collapse_limitations)
    render_analytical_flow_hint(entry)
    render_related_visuals(entry)


__all__ = ["render_explainability"]
