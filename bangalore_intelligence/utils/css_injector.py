"""Global platform CSS — overrides default Streamlit feel."""

import streamlit as st

from config.layout import VIEWPORT_MAX_WIDTH, VIEWPORT_PADDING_X
from config.theme import FONT_FAMILY, get_dashboard_tokens


def inject_platform_css(dashboard: str = "traffic") -> None:
    """Inject once per session; dashboard switches accent variables."""
    if st.session_state.get("_buip_css_injected"):
        return

    tokens = get_dashboard_tokens(dashboard)
    accent = tokens["accent"]
    bg = tokens["bg"]
    surface = tokens["surface"]
    surface_2 = tokens["surface_2"]
    surface_3 = tokens["surface_3"]
    border = tokens["border"]
    border_hover = tokens["border_hover"]
    text_primary = tokens["text_primary"]
    text_muted = tokens["text_muted"]
    shimmer_mid = tokens["surface_4"]

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');

    .stApp {{ background-color: {bg}; }}
    html, body, [class*="css"] {{
        font-family: {FONT_FAMILY} !important;
    }}
    .main .block-container {{
        max-width: {VIEWPORT_MAX_WIDTH}px;
        margin: 0 auto;
        padding-left: {VIEWPORT_PADDING_X}px;
        padding-right: {VIEWPORT_PADDING_X}px;
        padding-top: 0.5rem;
        padding-bottom: 1.25rem;
    }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    .stSpinner {{ display: none !important; }}

    div[data-testid="stRadio"] > label {{
        font-size: 13px !important;
        font-weight: 500 !important;
    }}

    .stDateInput label, .stMultiSelect label {{
        font-size: 12px !important;
        color: {text_muted} !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    @keyframes buip-shimmer {{
        0% {{ background-position: -480px 0; }}
        100% {{ background-position: 480px 0; }}
    }}
    @keyframes buip-pulse {{
        0%, 100% {{ opacity: 0.55; }}
        50% {{ opacity: 0.85; }}
    }}
    .buip-skeleton {{
        background: linear-gradient(90deg, {surface_2} 0%, {shimmer_mid} 42%, {surface_2} 84%);
        background-size: 960px 100%;
        animation: buip-shimmer 1.6s ease-in-out infinite;
        border-radius: 4px;
    }}
    .buip-chart-placeholder {{
        animation: buip-pulse 2.2s ease-in-out infinite;
    }}

    .buip-kpi-card {{
        transition: background 150ms ease, border-color 150ms ease;
    }}
    .buip-kpi-card:hover {{
        background: {surface_2} !important;
        border-color: {border_hover} !important;
    }}

    .buip-chart-shell {{
        transition: border-color 150ms ease, background 150ms ease;
    }}
    .buip-chart-shell--hero {{
        border-width: 1px !important;
        border-color: {border_hover} !important;
        background: {surface_3} !important;
    }}
    .buip-chart-shell--support {{
        background: {surface} !important;
        border-color: {border} !important;
    }}
    .buip-chart-shell:hover {{
        border-color: {border_hover} !important;
    }}

    .buip-nav-card {{
        transition: all 150ms ease;
    }}
    .buip-nav-card:hover {{
        border-color: {accent}66 !important;
        background: {surface_2} !important;
    }}

    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: {surface_2};
        border-color: {border} !important;
        border-radius: 8px;
        padding: 8px 4px 4px 4px;
    }}

    @media (prefers-reduced-motion: reduce) {{
        .buip-skeleton, .buip-chart-placeholder {{ animation: none; }}
        * {{ transition-duration: 0.01ms !important; }}
    }}

    :root {{
        --buip-accent: {accent};
        --buip-bg: {bg};
        --buip-surface: {surface};
        --buip-border: {border};
        --buip-text: {text_primary};
        --buip-muted: {text_muted};
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    st.session_state["_buip_css_injected"] = True


def inject_dashboard_accent(dashboard: str) -> None:
    """Accent and surface refresh when switching dashboards."""
    tokens = get_dashboard_tokens(dashboard)
    shimmer_mid = tokens["surface_4"]
    st.markdown(
        f"""
        <style>
        :root {{
            --buip-accent: {tokens['accent']};
            --buip-bg: {tokens['bg']};
        }}
        .stApp {{ background-color: {tokens['bg']}; }}
        .buip-skeleton {{
            background: linear-gradient(90deg, {tokens['surface_2']} 0%, {shimmer_mid} 42%, {tokens['surface_2']} 84%);
        }}
        .buip-chart-shell--hero {{
            background: {tokens['surface_3']} !important;
            border-color: {tokens['border_hover']} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
