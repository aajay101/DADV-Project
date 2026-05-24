from pathlib import Path

from bangalore_intelligence.explainability.models import ExplainabilityEntry
from components.related_analysis.analytical_flow_renderer import render_analytical_flow_hint
from components.related_analysis.navigation_hints import analytical_flow_hint
from components.related_analysis.related_visual_utils import related_visuals_for
from components.related_analysis.related_visuals_renderer import render_related_visuals
from components.related_analysis.semantic_labels import relationship_label


class _Block:
    def __init__(self, calls, kind, label, expanded=None):
        self.calls = calls
        self.kind = kind
        self.label = label
        self.expanded = expanded

    def __enter__(self):
        self.calls.append((self.kind, self.label, self.expanded))
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _FakeStreamlit:
    def __init__(self):
        self.calls = []

    def caption(self, text):
        self.calls.append(("caption", text))

    def markdown(self, text):
        self.calls.append(("markdown", text))

    def expander(self, label, expanded=False):
        return _Block(self.calls, "expander", label, expanded)


def _entry(related_visuals=("T-07", "T-09", "T-99")) -> ExplainabilityEntry:
    return ExplainabilityEntry(
        surface_id="T-05",
        dashboard="traffic",
        surface_type="chart",
        title="Road Management Priority Quadrant",
        complexity_level="intermediate",
        priority="high",
        what_this_shows="Roads positioned by congestion and capacity pressure.",
        why_this_visualization="Quadrant scatter compares two risk dimensions.",
        when_to_use="Use it for road priority review.",
        decision_relevance="It supports intervention prioritization.",
        misinterpretation_warning="It is descriptive, not causal proof.",
        related_visuals=related_visuals,
        limitations=("Sparse records reduce stability.",),
    )


def _patch_streamlit(monkeypatch, fake):
    import components.related_analysis.analytical_flow_renderer as flow_renderer
    import components.related_analysis.related_visuals_renderer as visuals_renderer
    import components.related_analysis.relationship_cards as cards

    monkeypatch.setattr(flow_renderer, "st", fake)
    monkeypatch.setattr(visuals_renderer, "st", fake)
    monkeypatch.setattr(cards, "st", fake)


def test_related_visuals_resolve_labels_and_fallbacks():
    related = related_visuals_for(_entry())

    assert [item.visual_id for item in related] == ["T-07", "T-09", "T-99"]
    assert related[0].label == "Compare road pressure against baseline"
    assert related[1].relationship_type == "threshold"
    assert related[2].title == "T-99"
    assert related[2].has_metadata is False


def test_missing_related_visuals_render_safely(monkeypatch):
    fake = _FakeStreamlit()
    _patch_streamlit(monkeypatch, fake)

    render_related_visuals(_entry(()))
    render_related_visuals(None)

    assert fake.calls == []


def test_related_visual_rendering_is_compact_and_secondary(monkeypatch):
    fake = _FakeStreamlit()
    _patch_streamlit(monkeypatch, fake)

    render_related_visuals(_entry(("T-07", "T-09")))

    rendered = "\n".join(str(call) for call in fake.calls)
    assert "Related visuals: T-07, T-09" in rendered
    assert ("expander", "Related analysis", False) in fake.calls
    assert "Compare road pressure against baseline" in rendered
    assert "Investigate speed-collapse boundary" in rendered


def test_relationship_label_fallback_is_deterministic():
    label = relationship_label("T-05", "A-99")

    assert label.relationship_type == "diagnostic"
    assert label.label == "Investigate why this pattern exists"


def test_analytical_flow_hint_uses_static_progression():
    hint = analytical_flow_hint(_entry(("T-07",)))

    assert hint == "T-03 temporal rhythm -> T-05 road priority -> T-09 speed-collapse threshold"


def test_flow_renderer_is_passive(monkeypatch):
    fake = _FakeStreamlit()
    _patch_streamlit(monkeypatch, fake)

    render_analytical_flow_hint(_entry(("T-07",)))

    assert fake.calls == [
        (
            "caption",
            "Analytical flow: T-03 temporal rhythm -> T-05 road priority -> T-09 speed-collapse threshold",
        )
    ]


def test_related_analysis_has_no_runtime_mutation_imports():
    root = Path(__file__).resolve().parents[1] / "components" / "related_analysis"
    source = "\n".join(path.read_text(encoding="utf-8") for path in root.glob("*.py"))

    assert "filters.transitions" not in source
    assert "dispatch(" not in source
    assert "request_rerun" not in source
    assert "st.session_state[" not in source
