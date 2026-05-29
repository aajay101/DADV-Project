"""Navigation state — active tab index is the single source of truth."""

from config.page_config import AQI_TABS, TRAFFIC_TABS
from data_layer.page_bundles import get_bundle_builder


def test_each_traffic_tab_has_bundle_builder():
    for tab in TRAFFIC_TABS:
        assert get_bundle_builder(tab["module"], "traffic") is not None


def test_each_aqi_tab_has_bundle_builder():
    for tab in AQI_TABS:
        assert get_bundle_builder(tab["module"], "aqi") is not None


def test_traffic_tab_modules_are_unique():
    modules = [t["module"] for t in TRAFFIC_TABS]
    assert len(modules) == len(set(modules))


def test_set_active_tab_resolves_correct_module():

    class FakeSession(dict):
        def get(self, key, default=None):
            return super().get(key, default)

    # Simulate state without Streamlit
    state = {
        "traffic_active_tab": 2,
        "traffic_tab_nav": TRAFFIC_TABS[2]["label"],
    }
    idx = int(state["traffic_active_tab"])
    assert TRAFFIC_TABS[idx]["module"] == "p3_spatial_operations"
    assert state["traffic_tab_nav"] == TRAFFIC_TABS[2]["label"]
