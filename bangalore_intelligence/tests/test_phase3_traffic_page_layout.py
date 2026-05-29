"""Phase 3 — traffic page chart placement across six tabs."""

from __future__ import annotations

import re
from unittest.mock import patch

import pytest

from data_layer.page_bundles import (
    build_traffic_command_bundle,
    build_traffic_lab_bundle,
    build_traffic_patterns_bundle,
    build_traffic_spatial_bundle,
    build_traffic_temporal_bundle,
    build_traffic_threshold_bundle,
)
from filters.state import TRAFFIC_STATE_DEFAULTS

_CHART_ID = re.compile(r"^(T-\d+)")


def _slot_id(slot: dict | None) -> str | None:
    if not slot:
        return None
    if slot.get("chart_id"):
        return slot["chart_id"]
    match = _CHART_ID.match(slot.get("title", "") or "")
    return match.group(1) if match else None


def _bundle_chart_ids(bundle: dict) -> set[str]:
    ids: set[str] = set()
    for key in ("hero_chart", "support_chart"):
        cid = _slot_id(bundle.get(key))
        if cid:
            ids.add(cid)
    for slot in bundle.get("secondary_charts") or []:
        cid = _slot_id(slot)
        if cid:
            ids.add(cid)
    cid = _slot_id(bundle.get("collapsed_chart"))
    if cid:
        ids.add(cid)
    return ids


@pytest.fixture
def traffic_state():
    return dict(TRAFFIC_STATE_DEFAULTS)


def test_p1_overview_t01_hero_t03_support_no_t08(sample_traffic_df, traffic_state):
    with patch("data_layer.page_bundles.load_traffic_clean", return_value=sample_traffic_df):
        bundle = build_traffic_command_bundle(traffic_state)
    ids = _bundle_chart_ids(bundle)
    assert ids == {"T-01", "T-03"}
    assert bundle.get("collapsed_chart") is None


def test_p2_temporal_t03_t04_t15(sample_traffic_df, traffic_state):
    with patch("data_layer.page_bundles.load_traffic_clean", return_value=sample_traffic_df):
        bundle = build_traffic_temporal_bundle(traffic_state)
    ids = _bundle_chart_ids(bundle)
    assert ids == {"T-03", "T-04", "T-15"}
    secondary = bundle["secondary_charts"][0]
    assert secondary.get("lazy") is True
    assert secondary.get("fig") is None


def test_p3_spatial_t05_t06_t07(sample_traffic_df, traffic_state):
    with patch("data_layer.page_bundles.load_traffic_clean", return_value=sample_traffic_df):
        bundle = build_traffic_spatial_bundle(traffic_state)
    ids = _bundle_chart_ids(bundle)
    assert ids == {"T-05", "T-06", "T-07"}
    assert bundle.get("collapsed_chart") is None
    assert bundle["secondary_charts"][0]["fig"] is not None


def test_p4_threshold_t09_t10(sample_traffic_df, traffic_state):
    with patch("data_layer.page_bundles.load_traffic_clean", return_value=sample_traffic_df):
        bundle = build_traffic_threshold_bundle(traffic_state)
    assert _bundle_chart_ids(bundle) == {"T-09", "T-10"}


def test_p5_patterns_t11_t12_t08(sample_traffic_df, traffic_state):
    with patch("data_layer.page_bundles.load_traffic_clean", return_value=sample_traffic_df):
        bundle = build_traffic_patterns_bundle(traffic_state)
    ids = _bundle_chart_ids(bundle)
    assert ids == {"T-11", "T-12", "T-08"}
    assert bundle.get("collapsed_chart") is None
    assert bundle["secondary_charts"][0]["fig"] is not None


def test_p6_lab_t13_t02_t14(sample_traffic_df, traffic_state):
    with patch("data_layer.page_bundles.load_traffic_clean", return_value=sample_traffic_df):
        with patch("data_layer.page_bundles.get_lab_dataset", return_value=sample_traffic_df):
            bundle = build_traffic_lab_bundle(traffic_state)
    ids = _bundle_chart_ids(bundle)
    assert ids == {"T-02", "T-13", "T-14"}
    assert bundle.get("collapsed_chart") is None
    secondary = bundle["secondary_charts"][0]
    assert secondary.get("lazy") is True


def test_all_traffic_charts_accounted_across_pages(sample_traffic_df, traffic_state):
    builders = (
        build_traffic_command_bundle,
        build_traffic_temporal_bundle,
        build_traffic_spatial_bundle,
        build_traffic_threshold_bundle,
        build_traffic_patterns_bundle,
        build_traffic_lab_bundle,
    )
    all_ids: set[str] = set()
    with patch("data_layer.page_bundles.load_traffic_clean", return_value=sample_traffic_df):
        with patch("data_layer.page_bundles.get_lab_dataset", return_value=sample_traffic_df):
            for builder in builders:
                bundle = builder(traffic_state)
                assert not bundle.get("empty")
                all_ids |= _bundle_chart_ids(bundle)
    expected = {f"T-{i:02d}" for i in range(1, 16)}
    assert all_ids == expected
