"""Reusable loading skeleton states."""

from config.theme import RADIUS_MD, SPACING_SM, SPACING_XS, get_dashboard_tokens
from utils.ui_blocks import render_html_block


def kpi_skeleton(dashboard: str = "traffic") -> None:
    tokens = get_dashboard_tokens(dashboard)
    html = f"""
    <div class="buip-skeleton" style="width:60%;height:36px;margin-bottom:{SPACING_SM}px;
         background:{tokens['surface_2']};"></div>
    <div class="buip-skeleton" style="width:80%;height:12px;margin-bottom:{SPACING_XS}px;"></div>
    <div class="buip-skeleton" style="width:40%;height:10px;"></div>
    """
    render_html_block(html)


def chart_skeleton(height: int = 460, dashboard: str = "traffic") -> None:
    tokens = get_dashboard_tokens(dashboard)
    html = f"""
    <div class="buip-chart-skeleton" style="
        position:relative;height:{height}px;background:{tokens['surface_2']};
        border-radius:{RADIUS_MD}px;overflow:hidden;border:1px solid {tokens['border']};
    ">
        <div class="buip-skeleton" style="position:absolute;bottom:24px;left:5%;width:90%;height:12px;"></div>
        <div class="buip-skeleton" style="position:absolute;left:40px;top:8%;width:12px;height:80%;"></div>
        <div class="buip-skeleton" style="position:absolute;bottom:40px;left:12%;width:10%;height:55%;"></div>
        <div class="buip-skeleton" style="position:absolute;bottom:40px;left:28%;width:10%;height:72%;"></div>
        <div class="buip-skeleton" style="position:absolute;bottom:40px;left:44%;width:10%;height:38%;"></div>
    </div>
    """
    render_html_block(html)


def inline_loader(label: str = "Calculating…", dashboard: str = "traffic") -> None:
    tokens = get_dashboard_tokens(dashboard)
    html = f"""
    <p class="buip-inline-loader" style="color:{tokens['text_muted']};font-size:12px;margin:{SPACING_SM}px 0;">
        {label}
    </p>
    """
    render_html_block(html)
