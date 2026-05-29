"""Phase 7 — accessibility, theme polish, and responsive sizing."""

from __future__ import annotations

from config.chart_defaults import resolve_chart_height
from config.theme import get_dashboard_tokens
from config.typography import TYPE_CHART_HERO, TYPE_CHART_SUPPORT
from utils.accessibility_audit import (
    WCAG_AA_NORMAL,
    audit_dashboard_shell,
    chart_accessibility_requirements,
    contrast_ratio,
)


def test_chart_typography_sentence_case():
    assert TYPE_CHART_HERO["transform"] == "none"
    assert TYPE_CHART_SUPPORT["transform"] == "none"


def test_light_theme_tokens_available():
    light = get_dashboard_tokens("traffic", appearance="light")
    dark = get_dashboard_tokens("traffic", appearance="dark")
    assert light["bg"] != dark["bg"]
    assert light["text_primary"] != dark["text_primary"]


def test_traffic_shell_contrast_dark_and_light():
    for appearance in ("dark", "light"):
        report = audit_dashboard_shell("traffic", appearance=appearance)
        assert report["pass"], report["checks"]
        assert report["failure_count"] == 0


def test_contrast_ratio_ordering():
    high = contrast_ratio("#FFFFFF", "#000000")
    low = contrast_ratio("#888888", "#999999")
    assert high > WCAG_AA_NORMAL
    assert low < high


def test_chart_accessibility_policy():
    policy = chart_accessibility_requirements()
    assert policy["require_title"] is True


def test_tablet_matrix_height_not_over_compressed():
    desktop = resolve_chart_height("matrix", chart_id="T-11", breakpoint="desktop")
    tablet = resolve_chart_height("matrix", chart_id="T-11", breakpoint="tablet")
    assert tablet >= int(desktop * 0.85)
