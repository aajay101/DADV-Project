"""Phase 7 — export, accessibility, theme polish, and responsive sizing."""

from __future__ import annotations

from unittest.mock import patch

import plotly.graph_objects as go
import pytest

from config.chart_defaults import resolve_chart_height
from config.theme import get_dashboard_tokens
from config.typography import TYPE_CHART_HERO, TYPE_CHART_SUPPORT
from data_layer.page_bundles import (
    build_traffic_command_bundle,
    build_traffic_lab_bundle,
    build_traffic_patterns_bundle,
    build_traffic_spatial_bundle,
    build_traffic_temporal_bundle,
    build_traffic_threshold_bundle,
)
from filters.state import TRAFFIC_STATE_DEFAULTS
from utils.accessibility_audit import (
    WCAG_AA_NORMAL,
    audit_dashboard_shell,
    chart_accessibility_requirements,
    contrast_ratio,
)
from utils.export import (
    _bundle_chart_slots,
    generate_executive_summary,
    generate_pdf_report,
    resolve_export_figure,
)

def _minimal_png_bytes() -> bytes:
    from io import BytesIO

    from PIL import Image

    buf = BytesIO()
    Image.new("RGB", (8, 8), color=(255, 255, 255)).save(buf, format="PNG")
    return buf.getvalue()

TRAFFIC_BUILDERS = (
    ("p1_command_overview", build_traffic_command_bundle),
    ("p2_temporal_intelligence", build_traffic_temporal_bundle),
    ("p3_spatial_operations", build_traffic_spatial_bundle),
    ("p4_threshold_analytics", build_traffic_threshold_bundle),
    ("p5_hidden_patterns", build_traffic_patterns_bundle),
    ("p6_advanced_lab", build_traffic_lab_bundle),
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
    assert policy["export_includes_filter_metadata"] is False


def test_resolve_export_figure_lazy_builder():
    fig = go.Figure(data=[go.Scatter(x=[1], y=[2])])
    cfg = {"fig": None, "fig_builder": lambda: fig}
    assert resolve_export_figure(cfg) is fig


def test_bundle_slots_include_lazy_secondary(sample_traffic_df):
    state = dict(TRAFFIC_STATE_DEFAULTS)
    with patch("data_layer.page_bundles.load_traffic_clean", return_value=sample_traffic_df):
        with patch("data_layer.page_bundles.get_lab_dataset", return_value=sample_traffic_df):
            bundle = build_traffic_temporal_bundle(state)
    slots = _bundle_chart_slots(bundle)
    assert any(name.startswith("secondary_charts_") for name, _ in slots)


@pytest.mark.parametrize("page_key,builder", TRAFFIC_BUILDERS)
def test_traffic_report_pdf_builds(page_key, builder, sample_traffic_df, monkeypatch):
    from utils import export as export_mod

    state = dict(TRAFFIC_STATE_DEFAULTS)
    monkeypatch.setattr(
        export_mod,
        "export_chart_png",
        lambda *args, **kwargs: _minimal_png_bytes(),
    )
    with patch("data_layer.page_bundles.load_traffic_clean", return_value=sample_traffic_df):
        with patch("data_layer.page_bundles.get_lab_dataset", return_value=sample_traffic_df):
            bundle = builder(state)
    assert not bundle.get("empty"), page_key
    pdf = generate_pdf_report(
        bundle,
        {},
        dashboard="traffic",
        page_title=page_key,
    )
    assert pdf[:4] == b"%PDF"


def test_executive_summary_p1(sample_traffic_df, monkeypatch):
    from utils import export as export_mod

    state = dict(TRAFFIC_STATE_DEFAULTS)
    monkeypatch.setattr(
        export_mod,
        "export_chart_png",
        lambda *args, **kwargs: _minimal_png_bytes(),
    )
    with patch("data_layer.page_bundles.load_traffic_clean", return_value=sample_traffic_df):
        bundle = build_traffic_command_bundle(state)
    pdf = generate_executive_summary(
        bundle,
        {},
        dashboard="traffic",
        page_title="System Status Overview",
    )
    assert pdf[:4] == b"%PDF"


def test_tablet_matrix_height_not_over_compressed():
    desktop = resolve_chart_height("matrix", chart_id="T-11", breakpoint="desktop")
    tablet = resolve_chart_height("matrix", chart_id="T-11", breakpoint="tablet")
    assert tablet >= int(desktop * 0.85)
