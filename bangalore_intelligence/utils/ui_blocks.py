"""Safe HTML block rendering — prevents leaked tags and broken wrappers."""

from __future__ import annotations

import html
import re
from collections.abc import Callable

import streamlit as st

# Streamlit markdown sanitizer breaks multiline attributes and nested divs split across widgets.
_MULTILINE_TAG_RE = re.compile(r">\s+")
_ORPHAN_CLOSE_RE = re.compile(r"^\s*(?:</div>|</span>|</p>)\s*", re.IGNORECASE)


def escape_text(value: object) -> str:
    """Escape dynamic text before embedding in HTML fragments."""
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def collapse_html_whitespace(fragment: str) -> str:
    """Single-line HTML — multiline style attributes leak as raw text in Streamlit."""
    return re.sub(r"\s+", " ", fragment.strip())


def sanitize_html_fragment(fragment: str) -> str:
    """Normalize fragment: trim, collapse whitespace, strip leading orphan closers."""
    cleaned = collapse_html_whitespace(fragment)
    while _ORPHAN_CLOSE_RE.match(cleaned):
        cleaned = _ORPHAN_CLOSE_RE.sub("", cleaned, count=1).strip()
    return cleaned


def render_html_block(fragment: str) -> None:
    """Render a self-contained HTML fragment via st.html (fallback: markdown)."""
    safe = sanitize_html_fragment(fragment)
    if not safe:
        return
    html_fn: Callable[..., object] | None = getattr(st, "html", None)
    if html_fn is not None:
        html_fn(safe, unsafe_allow_javascript=False)
    else:
        st.markdown(safe, unsafe_allow_html=True)


def render_spacer(px: int) -> None:
    """Vertical gap that must not be split across Streamlit widget boundaries."""
    height = max(0, int(px))
    render_html_block(f'<div style="height:{height}px;" aria-hidden="true"></div>')


def render_micro_heading(
    text: str,
    *,
    color: str,
    margin_bottom: int = 8,
    margin_top: int = 0,
) -> None:
    """Section micro-label (replaces raw div markdown in lab/filter chrome)."""
    style = (
        f"font-size:11px;font-weight:600;letter-spacing:0.06em;color:{color};"
        f"margin:{margin_top}px 0 {margin_bottom}px 0;"
    )
    render_html_block(f'<p style="{style}">{escape_text(text)}</p>')
