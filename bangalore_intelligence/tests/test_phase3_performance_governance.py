"""Phase 3 performance governance invariants."""

from filters.performance import affected_charts_for_transition
from filters.state import TRAFFIC_STATE_DEFAULTS
from filters.transitions import ChartFocusChanged, GlobalFilterChanged, dispatch


def test_visual_focus_targets_only_visual_dependent_charts():
    affected = affected_charts_for_transition("traffic", ("visual_focus",), ("traffic_selected_area",))

    assert "T-05" in affected
    assert "T-13" in affected
    assert "T-01" not in affected
    assert "T-03" not in affected


def test_chart_focus_clears_only_affected_lazy_chart_caches(monkeypatch):
    fake = {
        **TRAFFIC_STATE_DEFAULTS,
        "buip_lazy_traffic_T-02_page_a": object(),
        "buip_lazy_traffic_T-05_page_a": object(),
        "buip_lazy_traffic_T-03_page_a": object(),
    }
    monkeypatch.setattr("filters.transitions.st.session_state", fake, raising=False)
    monkeypatch.setattr("data_layer.lazy_charts.st.session_state", fake, raising=False)

    result = dispatch(ChartFocusChanged(dashboard="traffic", payload={"chart": "T-01", "selected_area": "MG Road"}))

    assert "T-02" in result.invalidation_plan.affected_charts
    assert "buip_lazy_traffic_T-02_page_a" not in fake
    assert "buip_lazy_traffic_T-05_page_a" not in fake
    assert "buip_lazy_traffic_T-03_page_a" in fake
    assert result.invalidation_plan.data_cache_scope == "none"


def test_global_filter_change_targets_all_dashboard_chart_render_caches(monkeypatch):
    fake = {
        **TRAFFIC_STATE_DEFAULTS,
        "buip_lazy_traffic_T-02_page_a": object(),
        "buip_lazy_traffic_T-03_page_a": object(),
    }
    calls = {"clear": 0}

    class Cache:
        @staticmethod
        def clear():
            calls["clear"] += 1

    monkeypatch.setattr("filters.transitions.st.session_state", fake, raising=False)
    monkeypatch.setattr("data_layer.lazy_charts.st.session_state", fake, raising=False)
    monkeypatch.setattr("filters.transitions.st.cache_data", Cache(), raising=False)

    result = dispatch(GlobalFilterChanged(dashboard="traffic", updates={"traffic_selected_areas": ["MG Road"]}))

    assert "buip_lazy_traffic_T-02_page_a" not in fake
    assert "buip_lazy_traffic_T-03_page_a" not in fake
    assert calls["clear"] == 1
    assert result.invalidation_plan.data_cache_scope == "dashboard"
    assert "filtered_dataset" in result.invalidation_plan.cache_tiers


def test_chart_cache_key_ignores_unrelated_visual_focus(monkeypatch):
    from data_layer.lazy_charts import lazy_cache_key

    fake = dict(TRAFFIC_STATE_DEFAULTS)
    monkeypatch.setattr("data_layer.lazy_charts.st.session_state", fake, raising=False)
    monkeypatch.setattr("filters.performance.st.session_state", fake, raising=False)

    t03_before = lazy_cache_key("traffic", "page", "T-03")
    t05_before = lazy_cache_key("traffic", "page", "T-05")
    fake["traffic_selected_area"] = "MG Road"
    t03_after = lazy_cache_key("traffic", "page", "T-03")
    t05_after = lazy_cache_key("traffic", "page", "T-05")

    assert t03_before == t03_after
    assert t05_before != t05_after


def test_resolve_chart_fig_records_cache_hit_and_miss(monkeypatch):
    from data_layer.lazy_charts import resolve_chart_fig

    fake = dict(TRAFFIC_STATE_DEFAULTS)
    monkeypatch.setattr("data_layer.lazy_charts.st.session_state", fake, raising=False)
    monkeypatch.setattr("filters.performance.st.session_state", fake, raising=False)

    cfg = {"fig": None, "fig_builder": lambda: {"fig": 1}, "chart_id": "T-03"}
    first = resolve_chart_fig(cfg, cache_key="buip_lazy_traffic_T-03_page_x", dashboard="traffic", page_key="page")
    second = resolve_chart_fig(cfg, cache_key="buip_lazy_traffic_T-03_page_x", dashboard="traffic", page_key="page")

    traces = fake["performance_render_traces"]
    assert first == second
    assert traces[-2]["cache_hit"] is False
    assert traces[-1]["cache_hit"] is True
    assert fake["performance_cache_stats"]["T-03"]["hits"] == 1
    assert fake["performance_cache_stats"]["T-03"]["misses"] == 1
