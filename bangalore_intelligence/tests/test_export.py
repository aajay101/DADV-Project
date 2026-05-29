from datetime import datetime

import plotly.graph_objects as go

from utils.export import (
    _bundle_chart_slots,
    apply_export_theme,
    build_export_filename,
    chart_code_from_key,
    resolve_export_figure,
)
from utils.annotations import enforce_annotation_limit as ann_limit


def test_build_export_filename_format():
    name = build_export_filename("TRF", "T13", datetime(2026, 5, 21, 18, 30, 0), extension="png")
    assert name.startswith("BUIP_TRF_T13_20260521_")
    assert name.endswith(".png")


def test_apply_export_theme_uses_light_background():
    fig = go.Figure(data=[go.Scatter(x=[1, 2], y=[1, 2])])
    fig.update_layout(paper_bgcolor="#000000")
    themed = apply_export_theme(fig, dashboard="traffic")
    assert themed.layout.paper_bgcolor == "#FFFFFF"
    assert fig.layout.paper_bgcolor == "#000000"


def test_chart_code_from_key():
    assert chart_code_from_key("t13_radar", "T-13") == "T13"


def test_export_chart_png_uses_mock(monkeypatch):
    from utils import export as export_mod

    fig = go.Figure()
    monkeypatch.setattr(export_mod, "figure_to_png_bytes", lambda f: b"fakepng")
    out = export_mod.export_chart_png(fig, "Test Chart", {}, dashboard="traffic")
    assert out == b"fakepng"


def test_resolve_export_figure_prefers_eager_fig():
    fig = go.Figure()
    cfg = {"fig": fig, "fig_builder": lambda: go.Figure()}
    assert resolve_export_figure(cfg) is fig


def test_bundle_slots_lazy_without_eager_fig():
    bundle = {
        "secondary_charts": [
            {"fig": None, "fig_builder": lambda: go.Figure(), "title": "Lazy"},
        ],
    }
    slots = _bundle_chart_slots(bundle)
    assert len(slots) == 1


def test_enforce_annotation_limit():
    anns = [{"_buip_priority": "context"} for _ in range(5)]
    trimmed = ann_limit(anns, max_count=3)
    assert len(trimmed) == 3
