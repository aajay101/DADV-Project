"""Small rendering helpers for explainability content sections."""

from __future__ import annotations

from typing import TYPE_CHECKING

import streamlit as st

if TYPE_CHECKING:
    from bangalore_intelligence.explainability.models import ExplainabilityEntry


def render_text_section(title: str, body: str) -> None:
    if body:
        st.markdown(f"**{title}**")
        st.caption(body)


def render_warning(entry: ExplainabilityEntry) -> None:
    if entry.misinterpretation_warning:
        st.warning(entry.misinterpretation_warning, icon=":material/info:")


def render_limitations(entry: ExplainabilityEntry, *, collapsed: bool) -> None:
    if not entry.limitations:
        return
    if collapsed:
        with st.expander("Limitations", expanded=False):
            for item in entry.limitations:
                st.caption(f"- {item}")
        return
    st.markdown("**Limitations**")
    for item in entry.limitations:
        st.caption(f"- {item}")


__all__ = ["render_limitations", "render_text_section", "render_warning"]
