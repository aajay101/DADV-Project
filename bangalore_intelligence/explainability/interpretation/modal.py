"""Fullscreen-style interpretation modal boundary."""

from __future__ import annotations

from typing import Any

import streamlit as st

from bangalore_intelligence.explainability.interpretation.modal_layout import render_interpretation_modal_layout
from bangalore_intelligence.explainability.models import ExplainabilityEntry


def render_interpretation_modal(
    entry: ExplainabilityEntry,
    *,
    fig: Any = None,
    chart_height: int = 560,
) -> None:
    """Open a large educational interpretation modal without mutating dashboard state."""

    if hasattr(st, "dialog"):

        @st.dialog(f"Understand This Analysis - {entry.title}", width="large")
        def _dialog() -> None:
            render_interpretation_modal_layout(entry, fig=fig, chart_height=chart_height)

        _dialog()
        return

    with st.container(key=f"suaqis_editorial_fallback_{entry.surface_id.lower().replace('-', '_')}"):
        render_interpretation_modal_layout(entry, fig=fig, chart_height=chart_height)


__all__ = [
    "render_interpretation_modal",
]
