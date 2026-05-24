"""Native Streamlit section renderers for the editorial interpretation modal."""

from __future__ import annotations

import re

import streamlit as st

from bangalore_intelligence.explainability.interpretation.continuity import derive_analytical_continuity
from bangalore_intelligence.explainability.interpretation.dynamic_context import derive_dynamic_insight_context
from bangalore_intelligence.explainability.interpretation.navigation import related_investigation_flow
from bangalore_intelligence.explainability.interpretation.reading_modes import ReadingModePolicy
from bangalore_intelligence.explainability.interpretation.situation import (
    analyst_detail_items,
    is_semantically_migrated,
    resolve_situation_interpretation,
    uses_special_cognition_flow,
    visualization_anatomy_items,
)
from bangalore_intelligence.explainability.models import ExplainabilityEntry, GlossaryTerm


def _key(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]+", "_", value).strip("_").lower()


def _section_key(entry: ExplainabilityEntry, number: str, suffix: str = "") -> str:
    base = f"suaqis_editorial_{_key(entry.surface_id)}_{number}"
    return f"{base}_{suffix}" if suffix else base


def _render_meta(title: str, lines: tuple[str, ...]) -> None:
    st.markdown(f"**{title}**")
    for line in lines:
        if line:
            st.caption(line)


def _render_section_shell(
    entry: ExplainabilityEntry,
    *,
    number: str,
    title: str,
    summary: str,
    tone: str,
    meta_title: str,
    meta_lines: tuple[str, ...],
    body_renderer,
) -> None:
    with st.container(key=_section_key(entry, number, tone)):
        top = st.columns([0.12, 1, 0.42], gap="medium", vertical_alignment="center")
        with top[0]:
            st.caption(number)
        with top[1]:
            st.markdown(f"### {title}")
            st.caption(summary)
        with top[2]:
            with st.container(key=_section_key(entry, number, "meta")):
                _render_meta(meta_title, meta_lines)
        with st.container(key=_section_key(entry, number, "body")):
            body_renderer()


def _render_compact_section_shell(
    entry: ExplainabilityEntry,
    *,
    number: str,
    title: str,
    summary: str,
    tone: str,
    body_renderer,
) -> None:
    with st.container(key=_section_key(entry, number, tone)):
        top = st.columns([0.1, 1], gap="medium", vertical_alignment="center")
        with top[0]:
            st.caption(number)
        with top[1]:
            st.markdown(f"### {title}")
            if summary:
                st.caption(summary)
        with st.container(key=_section_key(entry, number, "body")):
            body_renderer()


def _render_paragraph(text: str) -> None:
    if text:
        st.markdown(text)


def _render_points(items: tuple[str, ...]) -> None:
    for idx, item in enumerate(items, start=1):
        st.markdown(f"{idx}. {item}")


def _render_dynamic_fragments(fragments: tuple[str, ...]) -> None:
    for fragment in fragments:
        _render_paragraph(f"**Current view:** {fragment}")


def _render_priority_fragments(dynamic_context) -> None:
    priority = dynamic_context.priority
    if priority.emphasis_fragment:
        _render_paragraph(f"**Main focus:** {priority.emphasis_fragment}")
    if priority.suppression_fragment:
        _render_paragraph(f"**Leave aside for now:** {priority.suppression_fragment}")


def _render_uncertainty_priority(dynamic_context) -> None:
    fragment = dynamic_context.priority.uncertainty_fragment
    if fragment:
        _render_paragraph(f"**Read carefully:** {fragment}")


def _render_continuity(entry: ExplainabilityEntry, dynamic_context) -> None:
    continuity = derive_analytical_continuity(entry, dynamic_context)
    if continuity.follow_up_reason:
        _render_paragraph(f"**Why next:** {continuity.follow_up_reason}")
    if continuity.unresolved_question:
        _render_paragraph(f"**Open question:** {continuity.unresolved_question}")
    if continuity.depth_control:
        _render_paragraph(f"**Enough for now:** {continuity.depth_control}")
    elif continuity.analytical_gap:
        _render_paragraph(f"**Still missing:** {continuity.analytical_gap}")


def render_anatomy_row(entry: ExplainabilityEntry, number: str, idx: int, name: str, purpose: str, notice: str) -> None:
    with st.container(key=_section_key(entry, number, f"anatomy_{idx}")):
        cols = st.columns([0.75, 1, 1.15], gap="medium", vertical_alignment="top")
        with cols[0]:
            st.markdown(f"**{name}**")
        with cols[1]:
            st.markdown(purpose)
        with cols[2]:
            st.markdown(notice)


def _render_human_impact(entry: ExplainabilityEntry, number: str) -> None:
    impact = resolve_situation_interpretation(entry).human_impact
    if impact is None:
        return
    rows = (
        ("Who is affected", impact.who_is_affected),
        ("What they experience", impact.what_they_experience),
        ("How long or how broad", impact.duration_or_scope),
    )
    for idx, (name, value) in enumerate(rows, start=1):
        render_anatomy_row(entry, number, idx, name, value, "Use this as lived context, not a prediction.")


def _render_compact_human_impact(entry: ExplainabilityEntry) -> None:
    impact = resolve_situation_interpretation(entry).human_impact
    if impact is None:
        return
    st.markdown(f"**Who feels it:** {impact.who_is_affected}")
    st.markdown(f"**What it means for them:** {impact.what_they_experience}")
    st.caption(impact.duration_or_scope)


def _render_analyst_detail(entry: ExplainabilityEntry, number: str) -> None:
    for idx, item in enumerate(analyst_detail_items(entry), start=1):
        render_anatomy_row(entry, number, idx, f"Detail {idx}", item, "Useful when you need the boundary or method.")


def _render_components(entry: ExplainabilityEntry, number: str) -> None:
    for idx, component in enumerate(visualization_anatomy_items(entry), start=1):
        render_anatomy_row(entry, number, idx, component.name, component.why_it_exists, component.what_to_notice)


def render_glossary_card(entry: ExplainabilityEntry, number: str, idx: int, term: GlossaryTerm) -> None:
    with st.container(key=_section_key(entry, number, f"term_{idx}")):
        st.markdown(f"**{term.term}**")
        st.caption(term.definition)


def _render_glossary(entry: ExplainabilityEntry, number: str, policy: ReadingModePolicy) -> None:
    terms = entry.glossary[: policy.glossary_preview_count]
    for row_start in range(0, len(terms), 3):
        cols = st.columns(3, gap="medium")
        for offset, term in enumerate(terms[row_start : row_start + 3]):
            with cols[offset]:
                render_glossary_card(entry, number, row_start + offset + 1, term)
    remaining = entry.glossary[policy.glossary_preview_count :]
    if remaining:
        st.caption("More glossary terms")
        for idx, term in enumerate(remaining, start=policy.glossary_preview_count + 1):
            render_glossary_card(entry, number, idx, term)


def render_related_card(entry: ExplainabilityEntry, number: str, idx: int, item) -> None:
    with st.container(key=_section_key(entry, number, f"related_{idx}")):
        st.caption(item.visual_id)
        st.markdown(f"**{item.title}**")
        st.caption(item.label)


def _render_related(entry: ExplainabilityEntry, number: str) -> None:
    related = related_investigation_flow(entry)
    for row_start in range(0, len(related), 3):
        cols = st.columns(3, gap="medium")
        for offset, item in enumerate(related[row_start : row_start + 3]):
            with cols[offset]:
                render_related_card(entry, number, row_start + offset + 1, item)


def _render_visualization_deep_dive(entry: ExplainabilityEntry, number: str, policy: ReadingModePolicy) -> None:
    situation = resolve_situation_interpretation(entry)
    with st.container(key=_section_key(entry, number, "optional_panel")):
        st.markdown("**Understand this visualization**")
        _render_paragraph(situation.guided_reading)
        if policy.show_visualization_anatomy and tuple(visualization_anatomy_items(entry)):
            st.markdown("**Visual cues**")
            _render_components(entry, number)
        if entry.glossary and policy.show_visualization_anatomy:
            st.markdown("**Terms used here**")
            _render_glossary(entry, number, policy)


def _infer_t13_visual_mode(fig) -> str:
    """Infer T-13's visible mode from the figure without reading dashboard state."""

    if fig is None:
        return "heatmap"
    for trace in getattr(fig, "data", ()) or ():
        trace_type = str(getattr(trace, "type", "")).lower()
        if trace_type == "scatterpolar":
            return "radar"
        if trace_type == "heatmap":
            return "heatmap"
    layout = getattr(fig, "layout", None)
    if layout is not None and getattr(layout, "polar", None):
        return "radar"
    return "heatmap"


def _t13_mode_focus_text(mode: str) -> str:
    if mode == "radar":
        return (
            "You are seeing radar comparison mode. Start with the largest outward spike in the focused shape. "
            "Use the overall shape only after the main stress driver is clear."
        )
    return (
        "You are seeing heatmap mode. Start with the darkest stress cell for the focused area. "
        "Treat lighter cells as background until the main stress driver is clear."
    )


def _special_flow_titles(entry: ExplainabilityEntry) -> dict[str, str]:
    if entry.surface_id == "A-15":
        return {
            "main": "Main Relationship Situation",
            "main_summary": "The one environmental relationship to understand before reading the matrix.",
            "focus": "First Relationship Focus",
            "focus_summary": "How to inspect one relationship without decoding every cell.",
            "guardrail_summary": "How to avoid false confidence from noisy relationship patterns.",
            "next": "Practical Follow-Up",
            "next_summary": "One useful place to continue once the main relationship is clear.",
            "lab": "Optional Relationship Interpretation Lab",
            "lab_summary": "Scatter, diagonal, and strength-reading help only when you need it.",
            "analyst_summary": "Sampling, correlation, and relationship-comparison boundaries.",
        }
    if entry.surface_id == "T-02":
        return {
            "main": "Main Profile Situation",
            "main_summary": "The area stress profile to understand before reading every line.",
            "focus": "First Focus Path",
            "focus_summary": "How to read one area profile without decoding everything.",
            "guardrail_summary": "How to avoid false precision from normalized profile lines.",
            "next": "Practical Follow-Up",
            "next_summary": "One useful place to continue once the profile pattern is clear.",
            "lab": "Optional Profile Interpretation Lab",
            "lab_summary": "Profile, axis, and comparison help only when you need it.",
            "analyst_summary": "Normalization caveats, profile assumptions, and comparison boundaries.",
        }
    if entry.surface_id == "A-13":
        return {
            "main": "Main Atmospheric Situation",
            "main_summary": "The practical condition pattern to understand first.",
            "focus": "Dominant Condition Focus",
            "focus_summary": "Which environmental condition deserves attention first.",
            "guardrail_summary": "How to avoid false certainty from regime labels.",
            "next": "Practical Follow-Up",
            "next_summary": "One useful place to continue if the condition pattern matters.",
            "lab": "Optional Environmental Interpretation Lab",
            "lab_summary": "Condition and regime-reading help only when you need it.",
            "analyst_summary": "Condition rules, assumptions, and comparison boundaries.",
        }
    return {
        "main": "Main Situation",
        "main_summary": "The stress pattern to understand before reading every dimension.",
        "focus": "First Focus Path",
        "focus_summary": "Where to look first and what to ignore at the beginning.",
        "guardrail_summary": "How to avoid overreading small profile differences.",
        "next": "Next Investigation",
        "next_summary": "One useful follow-up once the main stress driver is clear.",
        "lab": "Optional Relationship Lab",
        "lab_summary": "Stress-factor and view-reading help only when you need it.",
        "analyst_summary": "Mode caveats, assumptions, and comparison boundaries.",
    }


def _special_focus_text(entry: ExplainabilityEntry, mode: str) -> str:
    if entry.surface_id == "A-15":
        return (
            "Start with one PM2.5 relationship, preferably visibility or pressure. "
            "Ignore the rest of the matrix until that relationship looks clear or weak."
        )
    if entry.surface_id == "T-02":
        return (
            "Start with one area line. Ignore crossings at first, then check whether congestion, speed, "
            "and capacity pressure stay concerning together."
        )
    if entry.surface_id == "A-13":
        return (
            "Start with the condition group where high PM2.5 appears with low visibility. "
            "Use cleaner or more dispersed groups only as comparison context at first."
        )
    return _t13_mode_focus_text(mode)


def _special_ignore_text(entry: ExplainabilityEntry) -> str:
    if entry.surface_id == "A-15":
        return "Ignore diagonal distributions and secondary weather pairs until the first PM2.5 relationship is understood."
    if entry.surface_id == "T-02":
        return "Ignore secondary dimensions and crossing lines until the main profile pattern is clear."
    if entry.surface_id == "A-13":
        return "Ignore secondary environmental interactions until the dominant condition pattern is clear."
    return "Ignore secondary stress factors until the strongest driver is clear."


def _special_lab_intro(entry: ExplainabilityEntry, mode: str) -> str:
    if entry.surface_id == "A-15":
        return (
            "Use this lab to understand one relationship at a time. A tight directional pattern is stronger than a scattered cloud."
        )
    if entry.surface_id == "T-02":
        return (
            "Use this lab to understand profile comparison. Normalized line height is a comparison score, "
            "not the original raw unit."
        )
    if entry.surface_id == "A-13":
        return (
            "Use this lab to translate regime labels into practical condition meaning. "
            "Treat regimes as descriptive groups, not predictions or source diagnosis."
        )
    if mode == "radar":
        return "Radar mode is useful for comparing profile shape across a few areas. Large outward spikes deserve attention first."
    return "Heatmap mode is useful for finding the strongest stress factor before comparing the full area profile."


def _render_t13_relationship_lab(
    entry: ExplainabilityEntry,
    number: str,
    policy: ReadingModePolicy,
    mode: str,
) -> None:
    titles = _special_flow_titles(entry)
    with st.container(key=_section_key(entry, number, "relationship_lab")):
        st.markdown(f"**{titles['lab']}**")
        _render_paragraph(_special_lab_intro(entry, mode))
        _render_paragraph(resolve_situation_interpretation(entry).guided_reading)
        if policy.show_visualization_anatomy and tuple(visualization_anatomy_items(entry)):
            st.markdown("**How to read this safely**")
            _render_components(entry, number)
        if entry.glossary and policy.show_visualization_anatomy:
            st.markdown("**Terms used here**")
            _render_glossary(entry, number, policy)


def _render_special_cognition_sections(
    entry: ExplainabilityEntry,
    *,
    policy: ReadingModePolicy,
    fig=None,
) -> None:
    situation = resolve_situation_interpretation(entry)
    dynamic_context = derive_dynamic_insight_context(entry, fig)
    mode = _infer_t13_visual_mode(fig) if entry.surface_id == "T-13" else "regime"
    titles = _special_flow_titles(entry)

    _render_compact_section_shell(
        entry,
        number="01",
        title=titles["main"],
        summary=titles["main_summary"],
        tone="blue",
        body_renderer=lambda: (
            _render_paragraph(situation.verdict),
            _render_paragraph(situation.significance),
            _render_priority_fragments(dynamic_context),
            _render_dynamic_fragments(dynamic_context.state_fragments),
            _render_compact_human_impact(entry),
            _render_paragraph(situation.consequence),
            _render_paragraph(situation.confidence_anchor),
        ),
    )
    _render_compact_section_shell(
        entry,
        number="02",
        title=titles["focus"],
        summary=titles["focus_summary"],
        tone="green",
        body_renderer=lambda: (
            _render_paragraph(_special_focus_text(entry, mode)),
            _render_paragraph(f"**Start here:** {situation.focus_point}"),
            _render_paragraph(_special_ignore_text(entry)),
        ),
    )
    _render_compact_section_shell(
        entry,
        number="03",
        title="Guardrail",
        summary=titles["guardrail_summary"],
        tone="gray",
        body_renderer=lambda: (
            _render_uncertainty_priority(dynamic_context),
            _render_paragraph(situation.misunderstanding_guard),
            _render_paragraph(situation.uncertainty_note),
        ),
    )
    _render_compact_section_shell(
        entry,
        number="04",
        title=titles["next"],
        summary=titles["next_summary"],
        tone="red",
        body_renderer=lambda: (
            _render_paragraph(dynamic_context.next_step_fragment),
            _render_continuity(entry, dynamic_context),
            _render_paragraph(situation.next_investigation),
            _render_related(entry, "04"),
        ),
    )
    _render_compact_section_shell(
        entry,
        number="05",
        title=titles["lab"],
        summary=titles["lab_summary"],
        tone="purple",
        body_renderer=lambda: _render_t13_relationship_lab(entry, "05", policy, mode),
    )
    if policy.show_analyst_detail:
        _render_compact_section_shell(
            entry,
            number="06",
            title="Analyst Detail",
            summary=titles["analyst_summary"],
            tone="blue",
            body_renderer=lambda: _render_points(analyst_detail_items(entry)),
        )


def _render_migrated_interpretation_sections(entry: ExplainabilityEntry, *, policy: ReadingModePolicy, fig=None) -> None:
    situation = resolve_situation_interpretation(entry)
    dynamic_context = derive_dynamic_insight_context(entry, fig)

    _render_compact_section_shell(
        entry,
        number="01",
        title="Situation Understanding",
        summary="What is happening, why it matters, and who is affected.",
        tone="blue",
        body_renderer=lambda: (
            _render_paragraph(situation.verdict),
            _render_paragraph(situation.significance),
            _render_priority_fragments(dynamic_context),
            _render_dynamic_fragments(dynamic_context.state_fragments),
            _render_compact_human_impact(entry),
            _render_paragraph(situation.consequence),
            _render_paragraph(f"**What to watch:** {situation.focus_point}"),
            _render_paragraph(situation.confidence_anchor),
        ),
    )
    _render_compact_section_shell(
        entry,
        number="02",
        title="Guardrail",
        summary="The main interpretation mistake to avoid.",
        tone="gray",
        body_renderer=lambda: (
            _render_uncertainty_priority(dynamic_context),
            _render_paragraph(situation.misunderstanding_guard),
            _render_paragraph(situation.uncertainty_note),
        ),
    )
    _render_compact_section_shell(
        entry,
        number="03",
        title="Next Step",
        summary="One useful place to continue if you need more context.",
        tone="red",
        body_renderer=lambda: (
            _render_paragraph(dynamic_context.next_step_fragment),
            _render_continuity(entry, dynamic_context),
            _render_paragraph(situation.next_investigation),
            _render_related(entry, "03"),
        ),
    )
    _render_compact_section_shell(
        entry,
        number="04",
        title="Optional Deeper Understanding",
        summary="Chart-reading help and terms only when you want them.",
        tone="purple",
        body_renderer=lambda: _render_visualization_deep_dive(entry, "04", policy),
    )
    if policy.show_analyst_detail:
        _render_compact_section_shell(
            entry,
            number="05",
            title="Analyst Detail",
            summary="Metrics, thresholds, assumptions, methodology, and limitations.",
            tone="blue",
            body_renderer=lambda: _render_points(analyst_detail_items(entry)),
        )


def render_interpretation_sections(entry: ExplainabilityEntry, *, policy: ReadingModePolicy, fig=None) -> None:
    """Render interpretation sections with one native Streamlit pipeline."""

    if uses_special_cognition_flow(entry):
        _render_special_cognition_sections(entry, policy=policy, fig=fig)
        return

    if is_semantically_migrated(entry):
        _render_migrated_interpretation_sections(entry, policy=policy, fig=fig)
        return

    situation = resolve_situation_interpretation(entry)

    _render_section_shell(
        entry,
        number="01",
        title="Verdict",
        summary="The main situation to understand first.",
        tone="blue",
        meta_title="One core takeaway",
        meta_lines=("Start here", "Everything else is optional context"),
        body_renderer=lambda: _render_paragraph(situation.verdict),
    )
    _render_section_shell(
        entry,
        number="02",
        title="Significance",
        summary="Whether this situation matters and why.",
        tone="green",
        meta_title="Meaning",
        meta_lines=("Good, normal, concerning, or critical",),
        body_renderer=lambda: _render_paragraph(situation.significance),
    )
    _render_section_shell(
        entry,
        number="03",
        title="Focus Point",
        summary="The single place, time, group, or pattern to notice first.",
        tone="purple",
        meta_title="Attention",
        meta_lines=("One primary signal", "Avoid insight overload"),
        body_renderer=lambda: _render_paragraph(situation.focus_point),
    )
    _render_section_shell(
        entry,
        number="04",
        title="Human Impact",
        summary="What this can mean for people, movement, health, or city operations.",
        tone="amber",
        meta_title="Lived meaning",
        meta_lines=("Who is affected", "What they may experience"),
        body_renderer=lambda: _render_human_impact(entry, "04"),
    )
    _render_section_shell(
        entry,
        number="05",
        title="Pattern Consequence",
        summary="The practical consequence of the visible pattern.",
        tone="green",
        meta_title="So what",
        meta_lines=("Consequence, not just observation",),
        body_renderer=lambda: _render_paragraph(situation.consequence),
    )
    _render_section_shell(
        entry,
        number="06",
        title="Next Investigation",
        summary="One connected place to continue, if you need more context.",
        tone="red",
        meta_title="Exploration path",
        meta_lines=("One next step", "User-controlled"),
        body_renderer=lambda: (
            _render_paragraph(situation.next_investigation),
            _render_related(entry, "06"),
        ),
    )
    _render_section_shell(
        entry,
        number="07",
        title="Misunderstanding Guard",
        summary="The most important thing this chart does not prove.",
        tone="gray",
        meta_title="Avoid mistakes",
        meta_lines=("Prevents over-reading",),
        body_renderer=lambda: _render_paragraph(situation.misunderstanding_guard),
    )
    _render_section_shell(
        entry,
        number="08",
        title="Guided Reading",
        summary="How to read this chart after you understand the situation.",
        tone="amber",
        meta_title="Reading path",
        meta_lines=("Chart mechanics after meaning",),
        body_renderer=lambda: _render_paragraph(situation.guided_reading),
    )
    if situation.uncertainty_note:
        _render_section_shell(
            entry,
            number="09",
            title="Uncertainty Note",
            summary="When the available evidence is weak or unclear.",
            tone="gray",
            meta_title="Confidence",
            meta_lines=("Avoid forced interpretation",),
            body_renderer=lambda: _render_paragraph(situation.uncertainty_note),
        )
    next_number = 10 if situation.uncertainty_note else 9
    if policy.show_analyst_detail:
        _render_section_shell(
            entry,
            number=f"{next_number:02d}",
            title="Analyst Detail",
            summary="Metrics, thresholds, assumptions, methodology, and limitations.",
            tone="blue",
            meta_title="Deeper context",
            meta_lines=(f"{len(analyst_detail_items(entry))} details", "Separate from visual anatomy"),
            body_renderer=lambda: _render_points(analyst_detail_items(entry)),
        )
        next_number += 1
    if policy.show_visualization_anatomy:
        _render_section_shell(
            entry,
            number=f"{next_number:02d}",
            title="Visualization Anatomy",
            summary="Axes, encodings, legends, markers, and chart elements.",
            tone="purple",
            meta_title="Chart mechanics",
            meta_lines=(f"{len(tuple(visualization_anatomy_items(entry)))} elements",),
            body_renderer=lambda: _render_components(entry, f"{next_number:02d}"),
        )
        next_number += 1
    if entry.glossary:
        _render_section_shell(
            entry,
            number=f"{next_number:02d}",
            title="Glossary",
            summary="Only the most relevant terms for the visible explanation.",
            tone="blue",
            meta_title="Plain-English terms",
            meta_lines=(f"{min(len(entry.glossary), policy.glossary_preview_count)} visible terms",),
            body_renderer=lambda: _render_glossary(entry, f"{next_number:02d}", policy),
        )


__all__ = [
    "render_anatomy_row",
    "render_glossary_card",
    "render_interpretation_sections",
    "render_related_card",
]
