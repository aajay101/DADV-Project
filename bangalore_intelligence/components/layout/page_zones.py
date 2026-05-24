"""Command / Investigation / Context zone markers — self-contained HTML only."""

from config.theme import GAP_PAGE_SECTION, GAP_ZONE, SPACING_MD, SPACING_SM, get_dashboard_tokens
from utils.html_styles import join_styles
from utils.ui_blocks import render_html_block


def command_zone_open(dashboard: str = "traffic") -> None:
    tokens = get_dashboard_tokens(dashboard)
    style = join_styles(
        f"margin-bottom:{GAP_ZONE}px",
        f"padding-bottom:{SPACING_MD}px",
        f"border-bottom:1px solid {tokens['border']}",
    )
    render_html_block(f'<div class="buip-zone-command" style="{style}"></div>')


def command_zone_close() -> None:
    pass


def investigation_zone_open(dashboard: str = "traffic") -> None:
    tokens = get_dashboard_tokens(dashboard)
    style = join_styles(
        "height:2px",
        f"background:linear-gradient(90deg,{tokens['accent']}33 0%,{tokens['border']} 72%,{tokens['border']} 100%)",
        f"margin:{SPACING_MD + 4}px 0 {SPACING_SM + 4}px 0",
        "border-radius:2px",
    )
    render_html_block(f'<div class="buip-zone-investigation-rail" style="{style}"></div>')


def investigation_zone_close() -> None:
    pass


def context_zone(dashboard: str = "traffic") -> None:
    tokens = get_dashboard_tokens(dashboard)
    style = join_styles(
        f"margin-top:{GAP_PAGE_SECTION}px",
        f"padding-top:{SPACING_MD + 4}px",
        f"border-top:1px solid {tokens['border_2']}",
    )
    render_html_block(f'<div class="buip-zone-context" style="{style}"></div>')
