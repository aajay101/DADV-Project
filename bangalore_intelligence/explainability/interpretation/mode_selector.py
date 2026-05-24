"""Reading mode selector for interpretation modals."""

from __future__ import annotations

import streamlit as st

from bangalore_intelligence.explainability.interpretation.reading_modes import (
    READING_MODE_SIMPLE,
    VALID_READING_MODES,
    ReadingModePolicy,
    reading_mode_policy,
)
from bangalore_intelligence.explainability.models import ExplainabilityEntry


def render_reading_mode_selector(entry: ExplainabilityEntry) -> ReadingModePolicy:
    """Render a lightweight reading mode selector and return its policy."""

    key = f"interpretation_reading_mode_{entry.surface_id}"
    help_text = "Choose how much detail this interpretation should emphasize."
    if hasattr(st, "segmented_control"):
        selected = st.segmented_control(
            "Reading mode",
            options=VALID_READING_MODES,
            default=READING_MODE_SIMPLE,
            key=key,
            help=help_text,
        )
    else:
        selected = st.radio(
            "Reading mode",
            options=VALID_READING_MODES,
            index=0,
            key=key,
            help=help_text,
            horizontal=True,
        )
    policy = reading_mode_policy(selected)
    st.caption(f"{policy.audience} - {policy.emphasis}")
    return policy


__all__ = ["render_reading_mode_selector"]
