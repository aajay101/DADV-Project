"""Compact display cards for static related-visual relationships."""

from __future__ import annotations

import streamlit as st

from .related_visual_utils import RelatedVisual


def render_relationship_card(visual: RelatedVisual) -> None:
    """Render a compact, non-routing relationship card."""

    metadata_note = "" if visual.has_metadata else " · metadata pending"
    st.caption(f"**{visual.visual_id} · {visual.title}**")
    st.caption(f"{visual.label} ({visual.relationship_type}){metadata_note}")


__all__ = ["render_relationship_card"]
