from pathlib import Path

from filters.state import (
    clear_filter_updating,
    is_filter_updating,
)
from filters.transitions import GlobalFilterChanged, dispatch


class _FakeSession(dict):
    def get(self, key, default=None):
        return super().get(key, default)


def test_filter_updating_lifecycle(monkeypatch):
    fake = _FakeSession()
    monkeypatch.setattr("filters.state.st.session_state", fake, raising=False)
    monkeypatch.setattr("filters.transitions.st.session_state", fake, raising=False)

    dispatch(GlobalFilterChanged(dashboard="traffic", updates={}))
    assert is_filter_updating("traffic") is True
    assert is_filter_updating("aqi") is False

    clear_filter_updating("traffic")
    assert is_filter_updating("traffic") is False


def test_filter_updating_does_not_lock_filter_widgets_or_recovery_buttons():
    source = (
        Path(__file__).resolve().parents[1]
        / "components"
        / "filter_panel.py"
    ).read_text(encoding="utf-8")

    assert 'controls_disabled = interaction_mode == "investigation_mode"' in source
    assert "controls_disabled = filter_updating or interaction_mode" not in source

    clear_start = source.index('"Clear Global Filters"')
    reset_start = source.index('"Reset All"')
    clear_block = source[clear_start:reset_start]
    reset_block = source[reset_start:source.index("request_filter_reset", reset_start)]

    assert "disabled=filter_updating" not in clear_block
    assert "disabled=filter_updating" not in reset_block
