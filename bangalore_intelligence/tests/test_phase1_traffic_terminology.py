"""Phase 1 — traffic naming, KPI semantics, and bundle copy governance."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from config.page_config import TRAFFIC_TABS
from data_layer.page_bundles import (
    build_traffic_command_bundle,
    build_traffic_lab_bundle,
    build_traffic_patterns_bundle,
    build_traffic_spatial_bundle,
    build_traffic_temporal_bundle,
    build_traffic_threshold_bundle,
)
from data_layer.traffic_transforms import TRAFFIC_KPI_NOTES, compute_traffic_command_kpis
from filters.state import TRAFFIC_STATE_DEFAULTS

FORBIDDEN_USER_PHRASES = (
    "Saturation Command",
    "Stream Intelligence",
    "Active Mobility Exclusion",
    "First Incident Cliff",
    "Public Transport Decoupling",
    "Congestion Ridgeline",
    "Compound Stress Radar",
    "Command Overview",
    "Temporal Intelligence",
    "Spatial Operations",
    "Threshold Analytics",
    "Hidden Patterns",
    "Advanced Analytics Laboratory",
    "OPERATIONAL FILTER COMMAND",
    "Filtered by investigation",
    "Reset Investigation",
    "Investigation active",
)

EXPECTED_TAB_TITLES = [
    "System Status Overview",
    "Temporal Patterns",
    "Road And Area Diagnostics",
    "Speed And Service Thresholds",
    "Context And Distribution Patterns",
    "Analytical Workspace",
]

BUILDERS = (
    build_traffic_command_bundle,
    build_traffic_temporal_bundle,
    build_traffic_spatial_bundle,
    build_traffic_threshold_bundle,
    build_traffic_patterns_bundle,
    build_traffic_lab_bundle,
)


def _bundle_text(bundle: dict) -> str:
    parts: list[str] = []
    for key in ("nav_title", "nav_desc", "insight", "record_count"):
        val = bundle.get(key)
        if val:
            parts.append(str(val))
    for slot in ("hero_chart", "support_chart", "collapsed_chart"):
        cfg = bundle.get(slot) or {}
        for field in ("title", "subtitle", "caption", "label"):
            if cfg.get(field):
                parts.append(str(cfg[field]))
    for cfg in bundle.get("secondary_charts") or []:
        for field in ("title", "subtitle", "caption", "label"):
            if cfg.get(field):
                parts.append(str(cfg[field]))
    for kpi in bundle.get("primary_kpis", []) + bundle.get("secondary_kpis", []):
        parts.append(str(kpi.get("label", "")))
        parts.append(str(kpi.get("note", "")))
    return " ".join(parts)


@pytest.mark.parametrize("title", EXPECTED_TAB_TITLES)
def test_traffic_tab_titles_modernized(title: str):
    assert title in [t["title"] for t in TRAFFIC_TABS]


def test_traffic_tab_titles_match_phase1_mapping():
    assert [t["title"] for t in TRAFFIC_TABS] == EXPECTED_TAB_TITLES


def test_traffic_bundles_avoid_banned_phrases(sample_traffic_df):
    state = dict(TRAFFIC_STATE_DEFAULTS)
    with patch("data_layer.page_bundles.load_traffic_clean", return_value=sample_traffic_df):
        with patch("data_layer.page_bundles.get_lab_dataset", return_value=sample_traffic_df):
            for builder in BUILDERS:
                bundle = builder(state)
                assert not bundle.get("empty"), builder.__name__
                text = _bundle_text(bundle).lower()
                for phrase in FORBIDDEN_USER_PHRASES:
                    assert phrase.lower() not in text, f"{builder.__name__}: found {phrase!r}"


def test_command_kpis_include_methodology_notes(sample_traffic_df):
    primary, secondary = compute_traffic_command_kpis(sample_traffic_df)
    assert primary and secondary
    for row in primary + secondary:
        assert row.get("note"), f"missing note for {row.get('label')}"
        assert row["label"] in TRAFFIC_KPI_NOTES


def test_command_bundle_exposes_kpi_methodology_flag(sample_traffic_df):
    state = dict(TRAFFIC_STATE_DEFAULTS)
    with patch("data_layer.page_bundles.load_traffic_clean", return_value=sample_traffic_df):
        bundle = build_traffic_command_bundle(state)
    assert bundle.get("kpi_methodology") is True
    assert "Network Congestion And Area Ranking" in bundle["hero_chart"]["title"]
