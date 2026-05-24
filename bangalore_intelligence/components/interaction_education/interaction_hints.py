"""Small passive hint primitives for interaction semantics."""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True, slots=True)
class InteractionHint:
    code: str
    message: str
    detail: str = ""


def render_hint(hint: InteractionHint | None, *, compact: bool = True) -> None:
    """Render a subtle semantic hint without modifying dashboard state."""

    if hint is None:
        return
    text = hint.message if compact or not hint.detail else f"{hint.message} {hint.detail}"
    st.caption(text)


__all__ = ["InteractionHint", "render_hint"]
