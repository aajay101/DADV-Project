from pathlib import Path

from components.interaction_education.empty_state_guidance import empty_state_message, render_empty_state_guidance
from components.interaction_education.filter_scope_explanations import filter_scope_hint
from components.interaction_education.focus_behavior_help import clear_focus_hint, render_clear_focus_hint
from components.interaction_education.interaction_hints import render_hint
from components.interaction_education.interaction_mode_help import cosmetic_click_hint
from components.interaction_education.overlay_explanations import overlay_hint, render_overlay_hint
from components.interaction_education.semantics_utils import interaction_semantics_snapshot
from filters.state import AQI_STATE_DEFAULTS, TRAFFIC_STATE_DEFAULTS


class _FakeStreamlit:
    def __init__(self):
        self.calls = []

    def caption(self, text):
        self.calls.append(("caption", text))


def test_interaction_semantics_observation_does_not_mutate_state():
    state = {**TRAFFIC_STATE_DEFAULTS, "traffic_selected_areas": ["Whitefield"]}
    before = dict(state)

    snapshot = interaction_semantics_snapshot(state, "traffic")
    hint = filter_scope_hint(state, "traffic")

    assert snapshot["mode"] == "global_filter_mode"
    assert hint is not None
    assert state == before


def test_filter_scope_hint_explains_persistent_global_filters():
    state = {**TRAFFIC_STATE_DEFAULTS, "traffic_selected_weather": ["Rain"]}

    hint = filter_scope_hint(state, "traffic")

    assert hint is not None
    assert hint.code == "global_filter_scope_active"
    assert "active analytical dataset" in hint.message


def test_overlay_hint_explains_temporary_investigation_context():
    state = {
        **AQI_STATE_DEFAULTS,
        "aqi_investigation_scope": {
            **AQI_STATE_DEFAULTS["aqi_investigation_scope"],
            "category": "Severe",
        },
    }

    hint = overlay_hint(state, "aqi")

    assert hint is not None
    assert hint.code == "investigation_overlay_active"
    assert "does not rewrite global filters" in hint.detail


def test_cosmetic_click_hint_only_appears_in_global_filter_mode():
    baseline = dict(TRAFFIC_STATE_DEFAULTS)
    filtered = {**TRAFFIC_STATE_DEFAULTS, "traffic_selected_roads": ["Old Airport Road"]}

    assert cosmetic_click_hint(baseline, "traffic") is None
    hint = cosmetic_click_hint(filtered, "traffic")

    assert hint is not None
    assert hint.code == "chart_click_cosmetic_global_filter_mode"
    assert "chart clicks remain contextual only" in hint.message


def test_clear_focus_hint_explains_filter_preservation():
    hint = clear_focus_hint()

    assert hint.code == "clear_focus_preserves_filters"
    assert "preserving persistent filters" in hint.message


def test_empty_state_semantic_distinctions():
    assert empty_state_message("valid_empty_result").code == "valid_empty_result"
    assert empty_state_message("overlay_empty_result").code == "overlay_empty_result"
    assert empty_state_message("chart_unavailable").code == "chart_unavailable"
    assert empty_state_message("lazy_not_hydrated").code == "lazy_not_hydrated"
    assert empty_state_message("dataset_unavailable").code == "dataset_unavailable"
    assert empty_state_message("unknown").code == "valid_empty_result"


def test_rendering_hints_is_passive(monkeypatch):
    import components.interaction_education.empty_state_guidance as empty_state_guidance
    import components.interaction_education.focus_behavior_help as focus_behavior_help
    import components.interaction_education.interaction_hints as interaction_hints
    import components.interaction_education.overlay_explanations as overlay_explanations

    fake = _FakeStreamlit()
    monkeypatch.setattr(interaction_hints, "st", fake)

    render_hint(clear_focus_hint())
    render_empty_state_guidance("overlay_empty_result")
    render_clear_focus_hint()
    render_overlay_hint(
        {
            **TRAFFIC_STATE_DEFAULTS,
            "traffic_investigation_scope": {
                **TRAFFIC_STATE_DEFAULTS["traffic_investigation_scope"],
                "area": "Whitefield",
            },
        },
        "traffic",
    )

    assert empty_state_guidance.render_hint is render_hint
    assert focus_behavior_help.render_hint is render_hint
    assert overlay_explanations.render_hint is render_hint
    assert len(fake.calls) == 4
    assert all(call[0] == "caption" for call in fake.calls)


def test_safe_behavior_with_missing_state():
    assert interaction_semantics_snapshot({}, "traffic")["mode"] == "global_filter_mode"
    assert overlay_hint({}, "traffic") is None


def test_interaction_education_layer_has_no_runtime_mutation_imports():
    root = Path(__file__).resolve().parents[1] / "components" / "interaction_education"
    source = "\n".join(path.read_text(encoding="utf-8") for path in root.glob("*.py"))

    assert "filters.transitions" not in source
    assert "dispatch(" not in source
    assert "request_rerun" not in source
    assert "st.session_state[" not in source
