from types import SimpleNamespace

from bangalore_intelligence.explainability.models import ExplainabilityEntry
from components import kpi_card as kpi_card_module
from components.explainability import explainability_renderer, explainability_sections, explainability_trigger
from components.explainability.explainability_renderer import render_explainability
from components.explainability.explainability_trigger import render_explainability_trigger
from components.related_analysis import analytical_flow_renderer, related_visuals_renderer, relationship_cards


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
    def __init__(self, *, popover=True):
        self.calls = []
        if popover:
            self.popover = self._popover

    def markdown(self, text, **kwargs):
        self.calls.append(("markdown", text, kwargs))

    def caption(self, text):
        self.calls.append(("caption", text))

    def warning(self, text, icon=None):
        self.calls.append(("warning", text, icon))

    def button(self, label, **kwargs):
        self.calls.append(("button", label, kwargs))
        return False

    def expander(self, label, expanded=False):
        return _Block(self.calls, "expander", label, expanded)

    def _popover(self, label, help=None):
        return _Block(self.calls, "popover", label, help)


def _entry(complexity_level="intermediate") -> ExplainabilityEntry:
    return ExplainabilityEntry(
        surface_id="T-05",
        dashboard="traffic",
        surface_type="chart",
        title="Road Management Priority Quadrant",
        complexity_level=complexity_level,
        priority="high",
        what_this_shows="Roads positioned by congestion and capacity pressure.",
        why_this_visualization="Quadrant scatter compares two risk dimensions.",
        when_to_use="Use it for road priority review.",
        decision_relevance="It supports intervention prioritization.",
        misinterpretation_warning="It is descriptive, not causal proof.",
        related_visuals=("T-07", "T-09"),
        limitations=("Sparse records reduce stability.",),
    )


def _kpi_entry(complexity_level="intermediate") -> ExplainabilityEntry:
    return ExplainabilityEntry(
        surface_id="kpi.mean_pm25",
        dashboard="aqi",
        surface_type="kpi",
        title="Mean PM2.5",
        complexity_level=complexity_level,
        priority="medium",
        what_this_shows="Average PM2.5 in the active scope.",
        why_this_visualization="A KPI summarizes current burden.",
        when_to_use="Use it for quick severity review.",
        decision_relevance="High averages indicate sustained exposure.",
        misinterpretation_warning="A mean can hide daily spikes.",
        related_visuals=(),
        limitations=("Averages hide distribution shape.",),
    )


def _patch_streamlit(monkeypatch, fake):
    monkeypatch.setattr(explainability_renderer, "st", fake)
    monkeypatch.setattr(explainability_sections, "st", fake)
    monkeypatch.setattr(explainability_trigger, "st", fake)
    monkeypatch.setattr(analytical_flow_renderer, "st", fake)
    monkeypatch.setattr(related_visuals_renderer, "st", fake)
    monkeypatch.setattr(relationship_cards, "st", fake)


def test_missing_explainability_renders_nothing(monkeypatch):
    fake = _FakeStreamlit()
    _patch_streamlit(monkeypatch, fake)

    render_explainability(None)
    render_explainability_trigger(None)

    assert fake.calls == []


def test_basic_rendering_is_compact(monkeypatch):
    fake = _FakeStreamlit()
    _patch_streamlit(monkeypatch, fake)

    render_explainability(_entry("basic"))

    rendered = "\n".join(str(call) for call in fake.calls)
    assert "What this shows" in rendered
    assert "When to use this visual" in rendered
    assert "Why this visualization exists" not in rendered
    assert "Why it matters" not in rendered


def test_intermediate_rendering_shows_limitations_without_collapsing(monkeypatch):
    fake = _FakeStreamlit()
    _patch_streamlit(monkeypatch, fake)

    render_explainability(_entry("intermediate"))

    rendered = "\n".join(str(call) for call in fake.calls)
    assert "Why this visualization exists" in rendered
    assert "Why it matters" in rendered
    assert "Sparse records reduce stability." in rendered
    assert not any(call[0] == "expander" and call[1] == "Limitations" for call in fake.calls)


def test_advanced_rendering_collapses_limitations(monkeypatch):
    fake = _FakeStreamlit()
    _patch_streamlit(monkeypatch, fake)

    render_explainability(_entry("advanced"))

    assert ("expander", "Limitations", False) in fake.calls


def test_related_visuals_are_display_only(monkeypatch):
    fake = _FakeStreamlit()
    _patch_streamlit(monkeypatch, fake)

    render_explainability(_entry())

    assert any("Related visuals: T-07, T-09" in str(call) for call in fake.calls)


def test_trigger_uses_popover_when_available(monkeypatch):
    fake = _FakeStreamlit(popover=True)
    _patch_streamlit(monkeypatch, fake)

    render_explainability_trigger(_kpi_entry())

    assert any(call[0] == "popover" for call in fake.calls)


def test_trigger_falls_back_to_expander(monkeypatch):
    fake = _FakeStreamlit(popover=False)
    _patch_streamlit(monkeypatch, fake)

    render_explainability_trigger(_kpi_entry())

    assert any(call[0] == "expander" and call[1] == "Understand This Analysis" for call in fake.calls)


def test_chart_trigger_without_deep_interpretation_does_not_use_old_popover(monkeypatch):
    fake = _FakeStreamlit(popover=True)
    _patch_streamlit(monkeypatch, fake)

    render_explainability_trigger(_entry())

    assert fake.calls == []


def test_renderer_does_not_mutate_entry(monkeypatch):
    fake = _FakeStreamlit()
    _patch_streamlit(monkeypatch, fake)
    entry = _entry()
    before = SimpleNamespace(related_visuals=entry.related_visuals, limitations=entry.limitations)

    render_explainability(entry)

    assert entry.related_visuals == before.related_visuals
    assert entry.limitations == before.limitations


def test_kpi_card_hides_missing_explainability(monkeypatch):
    calls = []
    monkeypatch.setattr(kpi_card_module, "render_html_block", lambda _html: None)
    monkeypatch.setattr(kpi_card_module, "kpi_entry", lambda _surface_id: None)
    monkeypatch.setattr(kpi_card_module, "render_explainability_trigger", lambda entry, label="Explain": calls.append(entry))

    kpi_card_module.kpi_card("Mean PM2.5", "120", explainability_id="missing")

    assert calls == [None]


def test_kpi_card_can_render_kpi_explainability(monkeypatch):
    calls = []
    entry = ExplainabilityEntry(
        surface_id="kpi.mean_pm25",
        dashboard="aqi",
        surface_type="kpi",
        title="Mean PM2.5",
        complexity_level="basic",
        priority="medium",
        what_this_shows="Average PM2.5 in the active scope.",
        why_this_visualization="A KPI summarizes current burden.",
        when_to_use="Use it for quick severity review.",
        decision_relevance="High averages indicate sustained exposure.",
        misinterpretation_warning="A mean can hide daily spikes.",
        related_visuals=(),
        limitations=("Averages hide distribution shape.",),
    )
    monkeypatch.setattr(kpi_card_module, "render_html_block", lambda _html: None)
    monkeypatch.setattr(kpi_card_module, "kpi_entry", lambda _surface_id: entry)
    monkeypatch.setattr(
        kpi_card_module,
        "render_explainability_trigger",
        lambda entry_arg, label="Explain": calls.append((entry_arg, label)),
    )

    kpi_card_module.kpi_card("Mean PM2.5", "120", explainability_id="kpi.mean_pm25")

    assert calls == [(entry, "Explain KPI")]
