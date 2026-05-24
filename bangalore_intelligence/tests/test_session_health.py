import time

from utils.session_health import check_data_freshness, should_show_long_session_notice


def test_stale_disabled_in_static_mode():
    assert check_data_freshness(time.time() - 99999, 60) is False


def test_long_session_notice_threshold():
    start = time.time() - (91 * 60)
    assert should_show_long_session_notice(time.time(), start, dismissed=False) is True
    assert should_show_long_session_notice(time.time(), start, dismissed=True) is False
