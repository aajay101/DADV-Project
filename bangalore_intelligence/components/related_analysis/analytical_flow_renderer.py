"""Passive renderer for static analytical progression hints."""

from __future__ import annotations

from typing import TYPE_CHECKING

import streamlit as st

from .navigation_hints import analytical_flow_hint
from .styles import ANALYTICAL_FLOW_HEADING

if TYPE_CHECKING:
    from bangalore_intelligence.explainability.models import ExplainabilityEntry


def render_analytical_flow_hint(entry: ExplainabilityEntry | None) -> None:
    hint = analytical_flow_hint(entry)
    if not hint:
        return
    st.caption(f"{ANALYTICAL_FLOW_HEADING}: {hint}")


__all__ = ["render_analytical_flow_hint"]
