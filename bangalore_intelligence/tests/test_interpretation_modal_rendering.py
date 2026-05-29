from contextlib import nullcontext

from components.explainability import explainability_trigger
from bangalore_intelligence.explainability.interpretation import mode_selector
from bangalore_intelligence.explainability.interpretation import modal as interpretation_modal
from bangalore_intelligence.explainability.interpretation import modal_layout, modal_sections
from bangalore_intelligence.explainability.interpretation.reading_modes import READING_MODE_ANALYTICAL
from bangalore_intelligence.explainability.registry_loader import load_explainability_registry


class _Column:
    def __init__(self, calls, label):
        self.calls = calls
        self.label = label

    def __enter__(self):
        self.calls.append(("column_enter", self.label))
        return self

    def __exit__(self, exc_type, exc, tb):
        self.calls.append(("column_exit", self.label))
        return False


class _FakeStreamlit:
    def __init__(self, *, click=True, dialog=True, selected_mode=None):
        self.calls = []
        self._click = click
        self._selected_mode = selected_mode
        if dialog:
            self.dialog = self._dialog

    def markdown(self, text, **kwargs):
        self.calls.append(("markdown", text, kwargs))

    def caption(self, text):
        self.calls.append(("caption", text))

    def button(self, label, **kwargs):
        self.calls.append(("button", label, kwargs))
        return self._click

    def segmented_control(self, label, options, default=None, **kwargs):
        self.calls.append(("segmented_control", label, options, default, kwargs))
        return self._selected_mode or default

    def columns(self, spec, gap=None, **kwargs):
        self.calls.append(("columns", spec, gap, kwargs))
        count = spec if isinstance(spec, int) else len(spec)
        return [_Column(self.calls, f"col_{idx}") for idx in range(count)]

    def container(self, **kwargs):
        self.calls.append(("container", kwargs))
        return nullcontext()

    def info(self, text):
        self.calls.append(("info", text))

    def plotly_chart(self, *args, **kwargs):
        self.calls.append(("plotly_chart", args, kwargs))

    def expander(self, label, expanded=False):
        self.calls.append(("expander", label, expanded))
        return nullcontext()

    def _dialog(self, title, **kwargs):
        self.calls.append(("dialog", title, kwargs))

        def decorator(func):
            def wrapped():
                self.calls.append(("dialog_body", title))
                return func()

            return wrapped

        return decorator


def _patch_streamlit(monkeypatch, fake):
    for module in (
        explainability_trigger,
        interpretation_modal,
        modal_layout,
        modal_sections,
        mode_selector,
    ):
        monkeypatch.setattr(module, "st", fake)


def test_deep_trigger_opens_large_interpretation_dialog(monkeypatch):
    fake = _FakeStreamlit(click=True, dialog=True)
    _patch_streamlit(monkeypatch, fake)
    entry = load_explainability_registry()["T-05"]

    explainability_trigger.render_explainability_trigger(entry, fig=None)

    rendered = "\n".join(str(call) for call in fake.calls)
    assert "Understand This Analysis" in rendered
    assert "dialog" in rendered
    assert "Road Management Priority Quadrant" in rendered
    assert "Explore This Analysis" in rendered
    assert "Situation Understanding" in rendered
    assert "Guardrail" in rendered
    assert "Next Step" in rendered
    assert "Optional Deeper Understanding" in rendered
    assert "Key Insight" in rendered
    assert "Reading mode" in rendered
    assert "suaqis_editorial_navigation" in rendered
    assert "suaqis_editorial_chart_card" in rendered
    assert "suaqis_editorial_t_05_01_blue" in rendered
    assert "What to notice first" in rendered


def test_dynamic_context_adds_concentration_aware_insert(monkeypatch):
    import plotly.graph_objects as go

    fake = _FakeStreamlit(click=True, dialog=True)
    _patch_streamlit(monkeypatch, fake)
    entry = load_explainability_registry()["T-05"]
    fig = go.Figure(go.Bar(y=[12, 14, 88, 92]))

    interpretation_modal.render_interpretation_modal(entry, fig=fig)

    rendered = "\n".join(str(call) for call in fake.calls)
    assert "Current view" in rendered
    assert "Main focus" in rendered
    assert "Localized interpretation matters most" in rendered
    assert "Suppress broad-system framing" in rendered
    assert "Why next" in rendered
    assert "local detail matters more than broad averages next" in rendered
    assert "Open question" in rendered
    assert "Analytical gap" not in rendered
    assert "Depth control" not in rendered
    assert "concentrated rather than evenly spread" in rendered
    assert "same issue stays localized" in rendered


def test_dynamic_priority_elevates_weak_relationship_uncertainty(monkeypatch):
    import plotly.graph_objects as go

    fake = _FakeStreamlit(click=True, dialog=True)
    _patch_streamlit(monkeypatch, fake)
    entry = load_explainability_registry()["A-15"]
    fig = go.Figure(go.Scatter(x=[1, 2, 3, 4, 5, 6], y=[4, 1, 5, 2, 6, 3], mode="markers"))

    interpretation_modal.render_interpretation_modal(entry, fig=fig)

    rendered = "\n".join(str(call) for call in fake.calls)
    assert "Weak or noisy relationships should control the reading" in rendered
    assert "Read carefully" in rendered
    assert "validate the relationship before treating it as meaningful" in rendered
    assert "validation matters more than deeper interpretation" in rendered
    assert "Leave aside for now" in rendered
    assert "Suppress detailed relationship interpretation" in rendered


def test_dynamic_context_adds_relationship_strength_insert(monkeypatch):
    import plotly.graph_objects as go

    fake = _FakeStreamlit(click=True, dialog=True)
    _patch_streamlit(monkeypatch, fake)
    entry = load_explainability_registry()["A-15"]
    fig = go.Figure(go.Scatter(x=[1, 2, 3, 4, 5, 6], y=[2, 4, 6, 8, 10, 12], mode="markers"))

    interpretation_modal.render_interpretation_modal(entry, fig=fig)

    rendered = "\n".join(str(call) for call in fake.calls)
    assert "Current view" in rendered
    assert "tightly linked enough to deserve focused follow-up" in rendered


def test_modal_uses_progressive_disclosure_for_deeper_sections(monkeypatch):
    fake = _FakeStreamlit(click=True, dialog=True, selected_mode=READING_MODE_ANALYTICAL)
    _patch_streamlit(monkeypatch, fake)
    entry = load_explainability_registry()["T-09"]

    interpretation_modal.render_interpretation_modal(entry, fig=None)

    rendered = "\n".join(str(call) for call in fake.calls)
    assert entry.semantic_migration_status == "migrated"
    assert "Analyst Detail" in rendered
    assert "Optional Deeper Understanding" in rendered
    assert "Understand this visualization" in rendered
    assert "Guardrail" in rendered


def test_analytical_mode_expands_metric_and_component_details(monkeypatch):
    fake = _FakeStreamlit(click=True, dialog=True, selected_mode=READING_MODE_ANALYTICAL)
    _patch_streamlit(monkeypatch, fake)
    entry = load_explainability_registry()["A-15"]

    interpretation_modal.render_interpretation_modal(entry, fig=None)

    rendered = "\n".join(str(call) for call in fake.calls)
    assert "Optional Relationship Interpretation Lab" in rendered
    assert "How to read this safely" in rendered
    assert "PM2.5 relationship cell" in rendered
    assert "Diagonal distribution" in rendered
    assert "Analyst Detail" in rendered


def test_modal_uses_top_anchored_story_flow(monkeypatch):
    fake = _FakeStreamlit(click=True, dialog=True)
    _patch_streamlit(monkeypatch, fake)
    entry = load_explainability_registry()["A-05"]

    interpretation_modal.render_interpretation_modal(entry, fig=None)

    rendered = "\n".join(str(call) for call in fake.calls)
    assert "suaqis_editorial_modal" in rendered
    assert "suaqis_editorial_a_05_01_blue" in rendered
    assert "Situation Understanding" in rendered
    assert "Guardrail" in rendered
    assert "Next Step" in rendered
    assert "Optional Deeper Understanding" in rendered
    assert "Verdict" not in rendered
    assert "Significance" not in rendered
    assert "Focus Point" not in rendered
    assert "Human Impact" not in rendered
    assert "Pattern Consequence" not in rendered
    assert "Use this as lived context, not a prediction." not in rendered


def test_migrated_simple_mode_hides_visualization_taxonomy(monkeypatch):
    fake = _FakeStreamlit(click=True, dialog=True)
    _patch_streamlit(monkeypatch, fake)
    entry = load_explainability_registry()["T-01"]

    interpretation_modal.render_interpretation_modal(entry, fig=None)

    rendered = "\n".join(str(call) for call in fake.calls)
    assert "Situation Understanding" in rendered
    assert "Understand this visualization" in rendered
    assert "Analyst Detail" not in rendered
    assert "Visualization Anatomy" not in rendered
    assert "Plain-English terms" not in rendered
    assert "Meaning" not in rendered
    assert "Attention" not in rendered
    assert "Lived meaning" not in rendered
    assert "So what" not in rendered


def test_migrated_analytical_mode_keeps_deeper_learning_optional(monkeypatch):
    fake = _FakeStreamlit(click=True, dialog=True, selected_mode=READING_MODE_ANALYTICAL)
    _patch_streamlit(monkeypatch, fake)
    entry = load_explainability_registry()["A-05"]

    interpretation_modal.render_interpretation_modal(entry, fig=None)

    rendered = "\n".join(str(call) for call in fake.calls)
    assert "Situation Understanding" in rendered
    assert "Understand this visualization" in rendered
    assert "Visual cues" in rendered
    assert "Terms used here" in rendered
    assert "Analyst Detail" in rendered


def test_t13_uses_special_cognition_focus_flow(monkeypatch):
    fake = _FakeStreamlit(click=True, dialog=True)
    _patch_streamlit(monkeypatch, fake)
    entry = load_explainability_registry()["T-13"]

    interpretation_modal.render_interpretation_modal(entry, fig=None)

    rendered = "\n".join(str(call) for call in fake.calls)
    assert entry.semantic_migration_status == "migrated"
    assert "Main Situation" in rendered
    assert "First Focus Path" in rendered
    assert "Optional Relationship Lab" in rendered
    assert "Optional Deeper Understanding" not in rendered
    assert "You are seeing heatmap mode" in rendered
    assert "strongest stress factor" in rendered
    assert "Ignore secondary stress factors" in rendered


def test_t02_uses_profile_special_cognition_flow(monkeypatch):
    fake = _FakeStreamlit(click=True, dialog=True)
    _patch_streamlit(monkeypatch, fake)
    entry = load_explainability_registry()["T-02"]

    interpretation_modal.render_interpretation_modal(entry, fig=None)

    rendered = "\n".join(str(call) for call in fake.calls)
    assert entry.semantic_migration_status == "migrated"
    assert "Main Profile Situation" in rendered
    assert "First Focus Path" in rendered
    assert "Practical Follow-Up" in rendered
    assert "Optional Profile Interpretation Lab" in rendered
    assert "Optional Deeper Understanding" not in rendered
    assert "Start with one area line" in rendered
    assert "Ignore crossings at first" in rendered
    assert "congestion, speed, and capacity pressure" in rendered


def test_t13_special_cognition_detects_radar_mode(monkeypatch):
    import plotly.graph_objects as go

    fake = _FakeStreamlit(click=True, dialog=True)
    _patch_streamlit(monkeypatch, fake)
    entry = load_explainability_registry()["T-13"]
    fig = go.Figure(go.Scatterpolar(r=[40, 70, 40], theta=["A", "B", "A"]))

    interpretation_modal.render_interpretation_modal(entry, fig=fig)

    rendered = "\n".join(str(call) for call in fake.calls)
    assert "You are seeing radar comparison mode" in rendered
    assert "largest outward spike" in rendered


def test_a13_uses_atmospheric_special_cognition_flow(monkeypatch):
    fake = _FakeStreamlit(click=True, dialog=True)
    _patch_streamlit(monkeypatch, fake)
    entry = load_explainability_registry()["A-13"]

    interpretation_modal.render_interpretation_modal(entry, fig=None)

    rendered = "\n".join(str(call) for call in fake.calls)
    assert entry.semantic_migration_status == "migrated"
    assert "Main Atmospheric Situation" in rendered
    assert "Dominant Condition Focus" in rendered
    assert "Practical Follow-Up" in rendered
    assert "Optional Environmental Interpretation Lab" in rendered
    assert "Optional Deeper Understanding" not in rendered
    assert "high PM2.5 appears with low visibility" in rendered
    assert "Ignore secondary environmental interactions" in rendered
    assert "regime labels as exact predictions" in rendered


def test_a15_uses_pairplot_special_cognition_flow(monkeypatch):
    fake = _FakeStreamlit(click=True, dialog=True)
    _patch_streamlit(monkeypatch, fake)
    entry = load_explainability_registry()["A-15"]

    interpretation_modal.render_interpretation_modal(entry, fig=None)

    rendered = "\n".join(str(call) for call in fake.calls)
    assert entry.semantic_migration_status == "migrated"
    assert "Main Relationship Situation" in rendered
    assert "First Relationship Focus" in rendered
    assert "Practical Follow-Up" in rendered
    assert "Optional Relationship Interpretation Lab" in rendered
    assert "Optional Deeper Understanding" not in rendered
    assert "Start with one PM2.5 relationship" in rendered
    assert "Ignore diagonal distributions" in rendered
    assert "not treat every matrix cell as important" in rendered


def test_related_investigations_render_relationship_context(monkeypatch):
    fake = _FakeStreamlit(click=True, dialog=True)
    _patch_streamlit(monkeypatch, fake)
    entry = load_explainability_registry()["T-05"]

    interpretation_modal.render_interpretation_modal(entry, fig=None)

    rendered = "\n".join(str(call) for call in fake.calls)
    assert "Investigate speed-collapse boundary" in rendered
    assert "Road Congestion Distribution Profiles" in rendered
    assert "suaqis_editorial_t_05_03_related_1" in rendered
    assert "&lt;article" not in rendered
    assert "<article" not in rendered


def test_modal_uses_native_rendering_pipeline_for_content(monkeypatch):
    fake = _FakeStreamlit(click=True, dialog=True, selected_mode=READING_MODE_ANALYTICAL)
    _patch_streamlit(monkeypatch, fake)
    entry = load_explainability_registry()["A-15"]

    interpretation_modal.render_interpretation_modal(entry, fig=None)

    unsafe_markdown = [call[1] for call in fake.calls if call[0] == "markdown" and call[2].get("unsafe_allow_html")]
    assert unsafe_markdown
    assert all(text.strip().startswith("<style>") for text in unsafe_markdown)
    rendered = "\n".join(str(call) for call in fake.calls)
    assert "<div" not in rendered
    assert "<article" not in rendered
    assert "suaqis-editorial-anatomy-row" not in rendered


def test_modal_falls_back_to_editorial_container_when_dialog_is_unavailable(monkeypatch):
    fake = _FakeStreamlit(click=True, dialog=False)
    _patch_streamlit(monkeypatch, fake)
    entry = load_explainability_registry()["A-05"]

    interpretation_modal.render_interpretation_modal(entry, fig=None)

    rendered = "\n".join(str(call) for call in fake.calls)
    assert "suaqis_editorial_fallback_a_05" in rendered
    assert not any(call[0] == "expander" for call in fake.calls)


def test_trigger_does_not_open_modal_until_user_clicks(monkeypatch):
    fake = _FakeStreamlit(click=False, dialog=True)
    _patch_streamlit(monkeypatch, fake)
    entry = load_explainability_registry()["A-06"]

    explainability_trigger.render_explainability_trigger(entry, fig=None)

    assert any(call[0] == "button" for call in fake.calls)
    assert not any(call[0] == "dialog" for call in fake.calls)
