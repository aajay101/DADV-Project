"""Progressive disclosure sections — lazy content_fn hook."""

from collections.abc import Callable

import streamlit as st

from config.spacing import EXPANDER_CONTENT_GAP
from config.typography import TYPE_SUBSECTION_TITLE, css_from_type
from config.theme import get_dashboard_tokens
from utils.html_styles import join_styles, styled_p
from utils.ui_blocks import render_html_block, render_spacer


def collapsible_section(
    label: str,
    key: str,
    default_expanded: bool = False,
    content_fn: Callable[[], None] | None = None,
    dashboard: str = "traffic",
) -> None:
    tokens = get_dashboard_tokens(dashboard)
    hint_style = join_styles(
        css_from_type(TYPE_SUBSECTION_TITLE, tokens["text_muted"]),
        "font-weight:400",
        "text-transform:none",
        "opacity:0.8",
        "line-height:1.5",
    )
    with st.expander(label, expanded=default_expanded):
        render_spacer(EXPANDER_CONTENT_GAP // 2)
        if content_fn is not None:
            content_fn()
        else:
            render_html_block(styled_p(f"Deferred render slot · {key}", hint_style))
        render_spacer(EXPANDER_CONTENT_GAP // 2)
