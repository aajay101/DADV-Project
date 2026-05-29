"""Passive renderer for related analytical visuals."""

from __future__ import annotations

from typing import TYPE_CHECKING

import streamlit as st

from .related_visual_utils import related_visuals_for
from .relationship_cards import render_relationship_card
from .styles import RELATED_ANALYSIS_HEADING

if TYPE_CHECKING:
    from bangalore_intelligence.explainability.models import ExplainabilityEntry


def render_related_visuals(entry: ExplainabilityEntry | None, *, compact: bool = True) -> None:
    """Render static related-visual guidance without navigation side effects."""

    related = related_visuals_for(entry)
    if not related:
        return

    ids = ", ".join(visual.visual_id for visual in related)
    st.caption(f"Related visuals: {ids}")
    if compact:
        with st.expander(RELATED_ANALYSIS_HEADING, expanded=False):
            for visual in related:
                render_relationship_card(visual)
        return

    st.markdown(f"**{RELATED_ANALYSIS_HEADING}**")
    for visual in related:
        render_relationship_card(visual)


__all__ = ["render_related_visuals"]
