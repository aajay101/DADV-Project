"""Command / Investigation / Context zone markers — self-contained HTML only."""

from config.theme import GAP_ZONE, RADIUS_LG, SPACING_MD, SPACING_SM, get_dashboard_tokens
from utils.ui_blocks import render_html_block


def command_zone_open(dashboard: str = "traffic") -> None:
    tokens = get_dashboard_tokens(dashboard)
    render_html_block(
        f"""
        <div class="buip-zone-command" style="
            margin-bottom:{GAP_ZONE}px;
            padding-bottom:{SPACING_MD}px;
            border-bottom:1px solid {tokens['border']};
        "></div>
        """
    )


def command_zone_close() -> None:
    pass


def investigation_zone_open(dashboard: str = "traffic") -> None:
    tokens = get_dashboard_tokens(dashboard)
    render_html_block(
        f"""
        <div class="buip-zone-investigation-rail" style="
            height:2px;
            background:linear-gradient(90deg,{tokens['accent']}55 0%,{tokens['border']} 100%);
            margin:{SPACING_MD}px 0 {SPACING_SM}px 0;
            border-radius:2px;
        "></div>
        """
    )


def investigation_zone_close() -> None:
    pass


def context_zone(dashboard: str = "traffic") -> None:
    tokens = get_dashboard_tokens(dashboard)
    render_html_block(
        f"""
        <div class="buip-zone-context" style="
            margin-top:{GAP_ZONE}px;
            padding-top:{SPACING_MD}px;
            border-top:1px solid {tokens['border_2']};
        "></div>
        """
    )
