"""Fullscreen-style modal layout helpers for chart interpretation."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import streamlit as st

from bangalore_intelligence.explainability.interpretation.mode_selector import render_reading_mode_selector
from bangalore_intelligence.explainability.interpretation.modal_sections import render_interpretation_sections
from bangalore_intelligence.explainability.interpretation.navigation import interpretation_nav_items
from bangalore_intelligence.explainability.interpretation.situation import (
    is_semantically_migrated,
    resolve_situation_interpretation,
    uses_special_cognition_flow,
)
from bangalore_intelligence.explainability.models import ExplainabilityEntry
from utils.plotly_engine import PLOTLY_CONFIG


def inject_interpretation_modal_styles() -> None:
    """Inject CSS for the native Streamlit editorial modal tree."""

    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap');

        div[data-testid="stModalOverlay"],
        div[data-testid="stDialogOverlay"] {
            background: rgba(18, 18, 18, 0.45) !important;
            backdrop-filter: blur(6px) !important;
        }

        div[data-testid="stDialog"],
        div[role="dialog"] {
            width: 94vw !important;
            max-width: 1600px !important;
            height: 94vh !important;
            border-radius: 28px !important;
            overflow: hidden !important;
            background: #f5f3ef !important;
            color: #1f1728 !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 20px 60px rgba(0, 0, 0, 0.14) !important;
        }

        div[data-testid="stDialog"] > div,
        div[role="dialog"] > div {
            max-height: 94vh !important;
            overflow-y: auto !important;
            padding: 48px 56px !important;
            background: #f5f3ef !important;
            color: #1f1728 !important;
        }

        div[data-testid="stDialog"] button[aria-label="Close"],
        div[data-testid="stDialog"] button[title="Close"],
        div[role="dialog"] button[aria-label="Close"],
        div[role="dialog"] button[title="Close"] {
            opacity: 1 !important;
            visibility: visible !important;
            color: #1f1728 !important;
            background: rgba(255,255,255,0.84) !important;
            border: 1px solid rgba(20,20,20,0.10) !important;
            border-radius: 999px !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.06) !important;
        }

        div[data-testid="stDialog"] button[aria-label="Close"] svg,
        div[data-testid="stDialog"] button[title="Close"] svg,
        div[role="dialog"] button[aria-label="Close"] svg,
        div[role="dialog"] button[title="Close"] svg {
            color: #1f1728 !important;
            fill: #1f1728 !important;
            stroke: #1f1728 !important;
        }

        div[data-testid="stDialog"] button[aria-label="Close"]:hover,
        div[data-testid="stDialog"] button[title="Close"]:hover,
        div[role="dialog"] button[aria-label="Close"]:hover,
        div[role="dialog"] button[title="Close"]:hover {
            background: #ffffff !important;
            transform: translateY(-1px);
        }

        div[data-testid="stDialog"] .st-key-suaqis_editorial_modal,
        div[data-testid="stDialog"] .st-key-suaqis_editorial_modal *,
        div[role="dialog"] .st-key-suaqis_editorial_modal,
        div[role="dialog"] .st-key-suaqis_editorial_modal * {
            box-sizing: border-box;
            letter-spacing: 0;
            font-family: Inter, "Source Sans 3", system-ui, sans-serif !important;
        }

        div[data-testid="stDialog"] .st-key-suaqis_editorial_modal {
            max-width: 1400px !important;
            margin: 0 auto !important;
            color: #1f1728 !important;
            background: #f5f3ef !important;
        }

        div[data-testid="stDialog"] .st-key-suaqis_editorial_header h1,
        div[data-testid="stDialog"] div[class*="st-key-suaqis_editorial_"] h3 {
            color: #1f1728 !important;
            font-family: "DM Serif Display", Georgia, serif !important;
            font-weight: 400 !important;
            letter-spacing: -0.03em !important;
        }

        div[data-testid="stDialog"] .st-key-suaqis_editorial_header h1 {
            font-size: clamp(42px, 5vw, 64px) !important;
            line-height: 1.02 !important;
            margin-bottom: 16px !important;
        }

        div[data-testid="stDialog"] .st-key-suaqis_editorial_header .stCaptionContainer,
        div[data-testid="stDialog"] div[class*="st-key-suaqis_editorial_"] .stCaptionContainer {
            color: #6e6772 !important;
            font-size: 15px !important;
            line-height: 1.7 !important;
        }

        div[data-testid="stDialog"] .st-key-suaqis_editorial_header .stCaptionContainer:first-child {
            color: #6e6772 !important;
            font-family: "JetBrains Mono", monospace !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            letter-spacing: 0.12em !important;
            text-transform: uppercase !important;
        }

        div[data-testid="stDialog"] [data-testid="stSegmentedControl"] {
            width: 100% !important;
            padding: 4px !important;
            border: 1px solid rgba(20,20,20,0.06) !important;
            border-radius: 999px !important;
            background: #ffffff !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.06) !important;
        }

        div[data-testid="stDialog"] [data-testid="stSegmentedControl"] label {
            min-height: 48px;
            padding: 0 22px;
            border-radius: 14px;
            color: #6e6772 !important;
            font-weight: 700 !important;
        }

        div[data-testid="stDialog"] .st-key-suaqis_editorial_insight,
        div[data-testid="stDialog"] .st-key-suaqis_editorial_notice,
        div[data-testid="stDialog"] .st-key-suaqis_editorial_pro_tip {
            border-radius: 22px !important;
            padding: 24px 28px !important;
            color: #1f1728 !important;
        }

        div[data-testid="stDialog"] .st-key-suaqis_editorial_insight {
            margin: 24px 0 40px !important;
            border: 1px solid rgba(20,20,20,0.06) !important;
            background: #f6e7c8 !important;
        }

        div[data-testid="stDialog"] .st-key-suaqis_editorial_chart_card {
            margin-bottom: 16px !important;
            padding: 32px !important;
            border: 1px solid rgba(20,20,20,0.06) !important;
            border-radius: 28px !important;
            background: #ffffff !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.06) !important;
        }

        div[data-testid="stDialog"] .st-key-suaqis_editorial_chart_context,
        div[data-testid="stDialog"] .st-key-suaqis_editorial_chart_surface {
            min-height: 420px !important;
            padding: 28px !important;
            border: 1px solid rgba(20,20,20,0.06) !important;
            border-radius: 24px !important;
            background: #f7f5f2 !important;
        }

        div[data-testid="stDialog"] .st-key-suaqis_editorial_notice,
        div[data-testid="stDialog"] .st-key-suaqis_editorial_pro_tip {
            border: 1px solid rgba(91,108,255,0.12) !important;
            background: #eef1fb !important;
        }

        div[data-testid="stDialog"] .st-key-suaqis_editorial_navigation {
            margin-top: 40px !important;
            margin-bottom: 24px !important;
        }

        div[data-testid="stDialog"] div[class*="st-key-suaqis_editorial_"][class*="_blue"],
        div[data-testid="stDialog"] div[class*="st-key-suaqis_editorial_"][class*="_green"],
        div[data-testid="stDialog"] div[class*="st-key-suaqis_editorial_"][class*="_purple"],
        div[data-testid="stDialog"] div[class*="st-key-suaqis_editorial_"][class*="_amber"],
        div[data-testid="stDialog"] div[class*="st-key-suaqis_editorial_"][class*="_red"],
        div[data-testid="stDialog"] div[class*="st-key-suaqis_editorial_"][class*="_gray"],
        div[data-testid="stDialog"] div[class*="st-key-suaqis_editorial_"][class*="_cyan"] {
            margin-bottom: 24px !important;
            padding: 32px !important;
            border: 1px solid rgba(20,20,20,0.06) !important;
            border-radius: 28px !important;
            background: #ffffff !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.06) !important;
        }

        div[data-testid="stDialog"] div[class*="st-key-suaqis_editorial_"][class*="_meta"],
        div[data-testid="stDialog"] div[class*="st-key-suaqis_editorial_"][class*="_term_"],
        div[data-testid="stDialog"] div[class*="st-key-suaqis_editorial_"][class*="_related_"],
        div[data-testid="stDialog"] div[class*="st-key-suaqis_editorial_"][class*="_anatomy_"],
        div[data-testid="stDialog"] div[class*="st-key-suaqis_editorial_"][class*="_optional_panel"],
        div[data-testid="stDialog"] div[class*="st-key-suaqis_editorial_"][class*="_relationship_lab"] {
            padding: 18px !important;
            border: 1px solid rgba(20,20,20,0.06) !important;
            border-radius: 18px !important;
            background: #f7f5f2 !important;
        }

        div[data-testid="stDialog"] div[class*="st-key-suaqis_editorial_"][class*="_optional_panel"],
        div[data-testid="stDialog"] div[class*="st-key-suaqis_editorial_"][class*="_relationship_lab"] {
            margin-top: 8px !important;
            overflow: visible !important;
        }

        div[data-testid="stDialog"] div[class*="st-key-suaqis_editorial_"][class*="_related_"] {
            width: 100% !important;
            min-height: 180px !important;
            background: #ffffff !important;
        }

        div[data-testid="stDialog"] div[class*="st-key-suaqis_editorial_"][class*="_body"] {
            padding-top: 16px;
        }

        div[data-testid="stDialog"] .st-key-suaqis_editorial_navigation p,
        div[data-testid="stDialog"] .st-key-suaqis_editorial_navigation .stCaptionContainer {
            color: #6e6772 !important;
            font-size: 12px !important;
            line-height: 1.35 !important;
        }

        div[data-testid="stDialog"] div[class*="st-key-suaqis_editorial_"] p,
        div[data-testid="stDialog"] div[class*="st-key-suaqis_editorial_"] li {
            color: #1f1728 !important;
            font-size: 16px !important;
            line-height: 1.8 !important;
        }

        div[data-testid="stDialog"] div[class*="st-key-suaqis_editorial_"] strong {
            color: #1f1728 !important;
            font-weight: 700 !important;
        }

        div[data-testid="stDialog"] div[class*="st-key-suaqis_editorial_"] [data-testid="stMarkdownContainer"] {
            color: #1f1728 !important;
        }

        @media (max-width: 900px) {
            div[data-testid="stDialog"] > div {
                padding: 32px 24px !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_modal_chart(fig: Any, *, height: int) -> None:
    if fig is None:
        st.info("The chart is not available in this view, but the interpretation remains available.")
        return
    modal_fig = deepcopy(fig)
    if hasattr(modal_fig, "update_layout"):
        modal_fig.update_layout(
            height=height,
            margin=dict(l=48, r=24, t=40, b=48),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font=dict(color="#362d3f", family="Inter, sans-serif", size=13),
        )
    if hasattr(modal_fig, "update_xaxes"):
        modal_fig.update_xaxes(
            gridcolor="rgba(20,20,20,0.08)",
            zerolinecolor="rgba(20,20,20,0.12)",
            color="#4b4355",
            tickfont=dict(color="#4b4355", size=13),
            title_font=dict(color="#4b4355", size=14),
        )
    if hasattr(modal_fig, "update_yaxes"):
        modal_fig.update_yaxes(
            gridcolor="rgba(20,20,20,0.08)",
            zerolinecolor="rgba(20,20,20,0.12)",
            color="#4b4355",
            tickfont=dict(color="#4b4355", size=13),
            title_font=dict(color="#4b4355", size=14),
        )
    st.plotly_chart(modal_fig, use_container_width=True, height=height, config=PLOTLY_CONFIG)


def _render_section_navigation(entry: ExplainabilityEntry, policy) -> None:
    with st.container(key="suaqis_editorial_navigation"):
        st.markdown("**Explore This Analysis**")
        if uses_special_cognition_flow(entry):
            if entry.surface_id == "A-13":
                labels = ["Atmosphere", "Condition", "Guardrail", "Follow-Up", "Environment Lab"]
            elif entry.surface_id == "A-15":
                labels = ["Relationship", "First Focus", "Guardrail", "Follow-Up", "Relation Lab"]
            elif entry.surface_id == "T-02":
                labels = ["Profile", "First Focus", "Guardrail", "Follow-Up", "Profile Lab"]
            else:
                labels = ["Main Situation", "First Focus", "Guardrail", "Next", "Relationship Lab"]
            if policy.show_analyst_detail:
                labels.append("Analyst Detail")
        elif is_semantically_migrated(entry):
            labels = ["Situation", "Guardrail", "Next Step", "Learn More"]
            if policy.show_analyst_detail:
                labels.append("Analyst Detail")
        else:
            labels = [item.label for item in interpretation_nav_items()]
        cols = st.columns(len(labels), gap="medium")
        for idx, label in enumerate(labels, start=1):
            with cols[idx - 1]:
                st.caption(f"{idx:02d}")
                st.markdown(label)


def _render_header(entry: ExplainabilityEntry) -> None:
    situation = resolve_situation_interpretation(entry)
    with st.container(key="suaqis_editorial_header"):
        st.caption("Understand This Analysis")
        st.markdown(f"# {entry.title}")
        st.caption(situation.verdict)


def _render_key_insight(entry: ExplainabilityEntry) -> None:
    situation = resolve_situation_interpretation(entry)
    body = situation.dominant_takeaway
    if not body:
        return
    with st.container(key="suaqis_editorial_insight"):
        cols = st.columns([0.22, 1], gap="medium", vertical_alignment="center")
        with cols[0]:
            st.markdown("**Key Insight**")
        with cols[1]:
            st.markdown(body)


def _render_chart_context(entry: ExplainabilityEntry) -> None:
    situation = resolve_situation_interpretation(entry)
    with st.container(key="suaqis_editorial_chart_context"):
        if not is_semantically_migrated(entry):
            st.caption("Visual Anchor")
        st.markdown(f"### {entry.title}")
        st.markdown(situation.focus_point)
        if situation.confidence_anchor:
            st.caption(situation.confidence_anchor)


def render_interpretation_modal_layout(
    entry: ExplainabilityEntry,
    *,
    fig: Any = None,
    chart_height: int = 560,
) -> None:
    """Render chart context and interpretation sections with one native Streamlit tree."""

    inject_interpretation_modal_styles()
    with st.container(key="suaqis_editorial_modal"):
        header_left, header_right = st.columns([0.68, 0.32], gap="large", vertical_alignment="top")
        with header_left:
            _render_header(entry)
        with header_right:
            st.markdown("**Reading Mode**")
            policy = render_reading_mode_selector(entry)

        _render_key_insight(entry)

        with st.container(key="suaqis_editorial_chart_card"):
            chart_left, chart_right = st.columns([2, 1], gap="large", vertical_alignment="center")
            chart_height = max(chart_height, 620)
            with chart_left:
                with st.container(key="suaqis_editorial_chart_surface"):
                    _render_modal_chart(fig, height=chart_height)
            with chart_right:
                _render_chart_context(entry)

        with st.container(key="suaqis_editorial_notice"):
            situation = resolve_situation_interpretation(entry)
            st.markdown(f"**What to notice first:** {situation.focus_point}")

        _render_section_navigation(entry, policy)
        render_interpretation_sections(entry, policy=policy, fig=fig)

        with st.container(key="suaqis_editorial_pro_tip"):
            st.markdown(
                "**Pro Tip**  \nUse Analytical mode for deeper metric and component details. Use Operational mode for decision-making focus."
            )


__all__ = ["inject_interpretation_modal_styles", "render_interpretation_modal_layout"]
