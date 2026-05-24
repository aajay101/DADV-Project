"""Viewport measurement and breakpoint rerun policy."""

from components.layout.responsive import get_breakpoint, is_compact, should_collapse_chart
from components.layout.viewport import apply_viewport_measurement


class _FakeSession(dict):
    def get(self, key, default=None):
        return super().get(key, default)

    def pop(self, key, default=None):
        return super().pop(key, default)


def test_apply_viewport_sets_breakpoint_keys(monkeypatch):
    import components.layout.viewport as vp

    state = _FakeSession()
    monkeypatch.setattr(vp, "st", type("S", (), {"session_state": state})())

    width, rerun = apply_viewport_measurement(900)
    assert width == 900
    assert rerun is False
    assert state["viewport_width"] == 900
    assert state["viewport_breakpoint"] == get_breakpoint(900)
    assert state["compact_mode"] == is_compact(900)


def test_apply_viewport_rerun_when_breakpoint_crosses(monkeypatch):
    import components.layout.viewport as vp

    state = _FakeSession(
        {
            "_buip_viewport_measured": 1300,
            "viewport_width": 1300,
            "viewport_breakpoint": "desktop",
        }
    )
    monkeypatch.setattr(vp, "st", type("S", (), {"session_state": state})())

    _, rerun = apply_viewport_measurement(700)
    assert rerun is True
    assert state["viewport_breakpoint"] == "compact"


def test_should_collapse_dense_charts_on_tablet():
    assert should_collapse_chart("t11_ridgeline", width=900) is True
    assert should_collapse_chart("t13_heatmap", width=900) is True
    assert should_collapse_chart("t11_ridgeline", width=1400) is False


def test_viewport_probe_uses_v2_inline_component():
    import components.layout.viewport as vp

    assert hasattr(vp, "_VIEWPORT_PROBE")
    assert vp._VIEWPORT_JS.strip().startswith("export default")
