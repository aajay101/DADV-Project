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
        padding-top: 1rem;
        padding-bottom: 2rem;
    }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    .stSpinner {{ display: none !important; }}

    div[data-testid="stRadio"] > label {{
        font-size: 13px !important;
        font-weight: 500 !important;
    }}

    button:focus-visible,
    [data-testid="stDownloadButton"] button:focus-visible,
    div[data-testid="stRadio"] label:focus-visible {{
        outline: 2px solid {accent} !important;
        outline-offset: 2px !important;
    }}

    .buip-kpi-card svg circle {{
        transition: stroke-dasharray 0.6s ease-out;
    }}
    .buip-nav-card button:focus-visible {{
        outline: 2px solid {accent};
        outline-offset: 2px;
    }}

    @keyframes buip-chart-appear {{
        from {{ opacity: 0.6; }}
        to {{ opacity: 1; }}
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

    .buip-hero {{
        line-height: 1.4;
    }}

    .buip-kpi-card {{
        transition: background 150ms ease, border-color 150ms ease;
    }}
    .buip-kpi-card:hover {{
        background: {surface_2} !important;
        border-color: {border_hover} !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(.buip-kpi-card) {{
        gap: 0.65rem;
        align-items: stretch;
    }}
    div[data-testid="stHorizontalBlock"]:has(.buip-kpi-card) > div {{
        min-width: 0;
    }}

    .buip-section-header {{
        margin-bottom: 0.25rem;
    }}

    .buip-chart-shell {{
        transition: border-color 150ms ease, background 150ms ease;
        animation: buip-chart-appear 0.35s ease-out;
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

    .buip-chart-title {{
        font-family: {FONT_FAMILY};
        line-height: 1.4;
    }}
    .buip-chart-title--hero {{
        font-size: 16px;
        font-weight: 600;
    }}
    .buip-chart-title--support {{
        font-size: 14px;
        font-weight: 500;
    }}
    .buip-selection-pill {{
        display: inline-block;
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: {tokens['severity_warning']};
        background: {tokens['severity_warning']}22;
        border: 1px solid {tokens['severity_warning']}44;
        border-radius: 8px;
        padding: 4px 10px;
        line-height: 1.35;
    }}
    .buip-chart-module {{
        overflow: visible;
    }}
    .buip-chart-module-header {{
        margin-bottom: 0;
    }}
    .buip-chart-plot-wrap {{
        width: 100%;
        max-width: 100%;
        overflow: hidden;
        box-sizing: border-box;
        margin-top: 0;
        margin-bottom: 0.35rem;
        padding-left: 2px;
        padding-right: 2px;
    }}
    .buip-chart-footer {{
        max-width: 100%;
        overflow-wrap: anywhere;
    }}
    .buip-fs-controls-row,
    div[data-testid="stHorizontalBlock"]:has(button[kind="primary"]) {{
        margin-top: 0.15rem;
        margin-bottom: 0.35rem;
    }}
    .buip-chart-plot-wrap--stagger {{
        animation: buip-chart-appear 0.42s ease-out 0.14s both;
    }}
    .buip-chart-plot-wrap .js-plotly-plot,
    .buip-chart-plot-wrap .plotly {{
        max-width: 100% !important;
    }}
    div[data-testid="stPlotlyChart"] {{
        max-width: 100%;
        overflow: hidden;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.buip-chart-title--a01) div[data-testid="stPlotlyChart"] {{
        margin-top: 0 !important;
        padding-top: 0 !important;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.buip-chart-title--a01) .js-plotly-plot {{
        margin-top: 0 !important;
    }}
    /* Targeted plot slots (T-02, T-13, T-03, A-02, A-03, A-05) */
    .buip-plot-slot {{
        display: block;
        height: 0;
        margin: 0;
        padding: 0;
        overflow: hidden;
    }}
    div[data-testid="column"] button {{
        white-space: nowrap !important;
    }}
    div[data-testid="column"]:first-child button {{
        min-width: 4.5rem;
    }}
    [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stPlotlyChart"]) {{
        overflow: hidden;
        max-width: 100%;
    }}
    .buip-zone-investigation-rail {{
        max-width: 100%;
        overflow: hidden;
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
        padding: 14px 12px 12px 12px;
        margin-bottom: 0.5rem;
    }}
    [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] {{
        gap: 0.75rem;
    }}
    details[data-testid="stExpander"] {{
        margin-top: 0.35rem;
        margin-bottom: 0.5rem;
    }}
    details[data-testid="stExpander"] summary {{
        padding-top: 0.55rem;
        padding-bottom: 0.55rem;
        line-height: 1.45;
    }}
    details[data-testid="stExpander"] [data-testid="stExpanderDetails"] {{
        padding-top: 0.65rem;
        padding-bottom: 0.35rem;
    }}
    .buip-zone-command {{
        margin-bottom: 0.5rem;
    }}

    @keyframes buip-filter-progress {{
        0% {{ background-position: 0% 50%; }}
        100% {{ background-position: 200% 50%; }}
    }}
    .buip-filter-strip--updating {{
        opacity: 0.92;
        pointer-events: none;
    }}
    .buip-filter-strip--updating::after {{
        content: "";
        display: block;
        height: 2px;
        margin-top: 6px;
        border-radius: 2px;
        background: linear-gradient(90deg, transparent, {accent}, transparent);
        background-size: 200% 100%;
        animation: buip-filter-progress 1.2s linear infinite;
    }}
    .buip-filter-controls--updating ~ * [data-testid="stDateInput"],
    .buip-filter-controls--updating ~ * [data-testid="stMultiSelect"],
    .buip-filter-strip--updating [data-testid="stDateInput"],
    .buip-filter-strip--updating [data-testid="stMultiSelect"] {{
        opacity: 0.65;
        pointer-events: none;
    }}
    .buip-chart-shell--fullscreen,
    .buip-chart-module.buip-chart-shell--fullscreen {{
        animation: buip-fs-enter 0.35s ease-out;
        margin-bottom: 1.25rem;
    }}
    .buip-chart-plot-wrap--fullscreen {{
        animation: buip-fs-enter 0.35s ease-out;
        margin-top: 0.75rem;
        margin-bottom: 0.75rem;
    }}
    div[data-testid="stPlotlyChart"] {{
        padding-top: 0.15rem;
    }}
    @keyframes buip-fs-enter {{
        from {{ opacity: 0.55; transform: translateY(6px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    @media (max-width: 768px) {{
        .main .block-container {{
            padding-left: 16px;
            padding-right: 16px;
        }}
    }}

    @media (prefers-reduced-motion: reduce) {{
        .buip-skeleton,
        .buip-chart-placeholder,
        .buip-chart-shell {{
            animation: none !important;
        }}
        .buip-filter-strip--updating::after,
        .buip-chart-shell--fullscreen,
        .buip-chart-plot-wrap--fullscreen {{
            animation: none;
            transform: none;
        }}
        .buip-filter-strip--updating::after {{
            background: {accent};
        }}
        .buip-kpi-card svg circle {{
            transition: none !important;
        }}
        .buip-kpi-card,
        .buip-chart-shell,
        .buip-nav-card {{
            transition: none !important;
        }}
        * {{
            transition-duration: 0.01ms !important;
        }}
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
