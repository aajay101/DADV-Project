"""Reusable loading skeleton states."""

from __future__ import annotations

from collections.abc import Callable

from config.theme import RADIUS_MD, SPACING_SM, SPACING_XS, get_dashboard_tokens
from utils.ui_blocks import render_html_block

CHART_SKELETON_TYPES = frozenset(
    {"bar", "heatmap", "scatter", "radar", "pairplot", "line", "default"}
)

_LAYOUT_TO_SKELETON: dict[str, str] = {
    "radar": "radar",
    "parcoords": "radar",
    "pairplot": "pairplot",
    "ridgeline": "line",
    "heatmap_small": "heatmap",
    "matrix": "scatter",
    "scatter_dense": "scatter",
    "compact": "bar",
    "default": "default",
}


def resolve_skeleton_type(chart_type: str | None) -> str:
    """Map plotly layout type or explicit skeleton key to a skeleton variant."""
    if not chart_type:
        return "default"
    key = chart_type.lower()
    if key in CHART_SKELETON_TYPES:
        return key
    return _LAYOUT_TO_SKELETON.get(key, "default")


def _skeleton_shell(height: int, dashboard: str, inner: str) -> str:
    tokens = get_dashboard_tokens(dashboard)
    return f"""
    <div class="buip-chart-skeleton buip-chart-skeleton--typed" data-skeleton-type
        style="position:relative;height:{height}px;background:{tokens['surface_2']};
        border-radius:{RADIUS_MD}px;overflow:hidden;border:1px solid {tokens['border']};">
        {inner}
    </div>
    """


def _bar_skeleton_inner() -> str:
    return """
        <div class="buip-skeleton" style="position:absolute;bottom:24px;left:5%;width:90%;height:12px;"></div>
        <div class="buip-skeleton" style="position:absolute;left:40px;top:8%;width:12px;height:80%;"></div>
        <div class="buip-skeleton" style="position:absolute;bottom:40px;left:12%;width:10%;height:55%;"></div>
        <div class="buip-skeleton" style="position:absolute;bottom:40px;left:28%;width:10%;height:72%;"></div>
        <div class="buip-skeleton" style="position:absolute;bottom:40px;left:44%;width:10%;height:38%;"></div>
        <div class="buip-skeleton" style="position:absolute;bottom:40px;left:60%;width:10%;height:64%;"></div>
    """


def _heatmap_skeleton_inner() -> str:
    return """
        <div class="buip-skeleton" style="position:absolute;inset:32px 24px 48px 56px;
            display:grid;grid-template-columns:repeat(6,1fr);grid-template-rows:repeat(4,1fr);gap:4px;">
            <div class="buip-skeleton" style="height:100%;opacity:0.35;"></div>
            <div class="buip-skeleton" style="height:100%;opacity:0.55;"></div>
            <div class="buip-skeleton" style="height:100%;opacity:0.75;"></div>
            <div class="buip-skeleton" style="height:100%;opacity:0.45;"></div>
            <div class="buip-skeleton" style="height:100%;opacity:0.65;"></div>
            <div class="buip-skeleton" style="height:100%;opacity:0.5;"></div>
        </div>
    """


def _scatter_skeleton_inner() -> str:
    return """
        <div class="buip-skeleton" style="position:absolute;left:12%;top:22%;width:8px;height:8px;border-radius:50%;"></div>
        <div class="buip-skeleton" style="position:absolute;left:28%;top:45%;width:10px;height:10px;border-radius:50%;"></div>
        <div class="buip-skeleton" style="position:absolute;left:52%;top:30%;width:9px;height:9px;border-radius:50%;"></div>
        <div class="buip-skeleton" style="position:absolute;left:68%;top:58%;width:11px;height:11px;border-radius:50%;"></div>
        <div class="buip-skeleton" style="position:absolute;left:78%;top:38%;width:8px;height:8px;border-radius:50%;"></div>
        <div class="buip-skeleton" style="position:absolute;bottom:32px;left:8%;width:84%;height:1px;opacity:0.5;"></div>
        <div class="buip-skeleton" style="position:absolute;left:48px;top:12%;width:1px;height:76%;opacity:0.5;"></div>
    """


def _radar_skeleton_inner() -> str:
    return """
        <div class="buip-skeleton" style="position:absolute;left:50%;top:50%;width:42%;height:42%;
            transform:translate(-50%,-50%);border-radius:50%;border:2px dashed rgba(255,255,255,0.08);"></div>
        <div class="buip-skeleton" style="position:absolute;left:50%;top:50%;width:28%;height:28%;
            transform:translate(-50%,-50%);border-radius:50%;opacity:0.5;"></div>
        <div class="buip-skeleton" style="position:absolute;left:50%;top:18%;width:2px;height:34%;transform:translateX(-50%);"></div>
        <div class="buip-skeleton" style="position:absolute;left:50%;bottom:18%;width:2px;height:34%;transform:translateX(-50%);"></div>
        <div class="buip-skeleton" style="position:absolute;top:50%;left:18%;width:34%;height:2px;transform:translateY(-50%);"></div>
        <div class="buip-skeleton" style="position:absolute;top:50%;right:18%;width:34%;height:2px;transform:translateY(-50%);"></div>
    """


def _pairplot_skeleton_inner() -> str:
    return """
        <div class="buip-skeleton" style="position:absolute;inset:28px 20px 36px 48px;
            display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(3,1fr);gap:6px;">
            <div class="buip-skeleton" style="border-radius:4px;opacity:0.4;"></div>
            <div class="buip-skeleton" style="border-radius:4px;opacity:0.55;"></div>
            <div class="buip-skeleton" style="border-radius:4px;opacity:0.45;"></div>
            <div class="buip-skeleton" style="border-radius:4px;opacity:0.5;"></div>
            <div class="buip-skeleton" style="border-radius:4px;opacity:0.7;"></div>
            <div class="buip-skeleton" style="border-radius:4px;opacity:0.42;"></div>
        </div>
    """


def _line_skeleton_inner() -> str:
    return """
        <div class="buip-skeleton" style="position:absolute;bottom:36px;left:8%;width:84%;height:2px;opacity:0.35;"></div>
        <div class="buip-skeleton" style="position:absolute;bottom:48px;left:10%;width:76%;height:48px;border-radius:40px 40px 0 0;opacity:0.45;"></div>
        <div class="buip-skeleton" style="position:absolute;bottom:52px;left:18%;width:68%;height:36px;border-radius:36px 36px 0 0;opacity:0.35;"></div>
        <div class="buip-skeleton" style="position:absolute;bottom:56px;left:26%;width:58%;height:28px;border-radius:28px 28px 0 0;opacity:0.3;"></div>
    """


_SKELETON_BUILDERS: dict[str, Callable[[], str]] = {
    "bar": _bar_skeleton_inner,
    "default": _bar_skeleton_inner,
    "heatmap": _heatmap_skeleton_inner,
    "scatter": _scatter_skeleton_inner,
    "radar": _radar_skeleton_inner,
    "pairplot": _pairplot_skeleton_inner,
    "line": _line_skeleton_inner,
}


def chart_skeleton_html(
    height: int = 460,
    dashboard: str = "traffic",
    chart_type: str = "default",
) -> str:
    """Return skeleton markup for tests and optional direct rendering."""
    sk_type = resolve_skeleton_type(chart_type)
    inner = _SKELETON_BUILDERS.get(sk_type, _bar_skeleton_inner)()
    return _skeleton_shell(height, dashboard, inner).replace(
        "data-skeleton-type",
        f'data-skeleton-type="{sk_type}"',
    )


def kpi_skeleton(dashboard: str = "traffic") -> None:
    tokens = get_dashboard_tokens(dashboard)
    html = f"""
    <div class="buip-skeleton" style="width:60%;height:36px;margin-bottom:{SPACING_SM}px;
         background:{tokens['surface_2']};"></div>
    <div class="buip-skeleton" style="width:80%;height:12px;margin-bottom:{SPACING_XS}px;"></div>
    <div class="buip-skeleton" style="width:40%;height:10px;"></div>
    """
    render_html_block(html)


def chart_skeleton(
    height: int = 460,
    dashboard: str = "traffic",
    chart_type: str = "default",
) -> None:
    render_html_block(chart_skeleton_html(height, dashboard, chart_type))


def inline_loader(label: str = "Calculating…", dashboard: str = "traffic") -> None:
    tokens = get_dashboard_tokens(dashboard)
    html = f"""
    <p class="buip-inline-loader" style="color:{tokens['text_muted']};font-size:12px;margin:{SPACING_SM}px 0;">
        {label}
    </p>
    """
    render_html_block(html)
