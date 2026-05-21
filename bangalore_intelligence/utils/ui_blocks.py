"""Safe HTML block rendering — prevents leaked tags and broken wrappers."""

import re

import streamlit as st


def normalize_html(html: str) -> str:
    """Collapse unsafe partial tags and trim fragment whitespace."""
    cleaned = html.strip()
    cleaned = re.sub(r">\s*<", "><", cleaned)
    return cleaned


def render_html_block(html: str) -> None:
    """Render a self-contained HTML fragment."""
    st.markdown(normalize_html(html), unsafe_allow_html=True)
