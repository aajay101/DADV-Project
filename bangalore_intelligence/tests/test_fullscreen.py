from filters.fullscreen import FULLSCREEN_ELIGIBLE, is_fullscreen_eligible


def test_fullscreen_eligible_keys():
    assert "t13_radar" in FULLSCREEN_ELIGIBLE
    assert is_fullscreen_eligible("a02_calendar")
    assert not is_fullscreen_eligible("t01_scorecard")
