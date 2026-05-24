"""Centralized theme tokens — colors, typography, spacing, radius, elevation."""

from typing import Literal

DashboardId = Literal["traffic", "aqi"]
AppearanceId = Literal["dark", "light"]

# ── Traffic: operational urgency ─────────────────────────────────────────────
TRAFFIC_BG = "#0D1117"
TRAFFIC_SURFACE = "#161B22"
TRAFFIC_SURFACE_1 = TRAFFIC_SURFACE
TRAFFIC_SURFACE_2 = "#1C2128"
TRAFFIC_SURFACE_3 = "#21262D"
TRAFFIC_SURFACE_4 = "#2D333B"
TRAFFIC_BORDER = "#30363D"
TRAFFIC_BORDER_1 = TRAFFIC_BORDER
TRAFFIC_BORDER_2 = "#21262D"
TRAFFIC_BORDER_HOVER = "#484F58"
TRAFFIC_CRIMSON = "#E5383B"
TRAFFIC_AMBER = "#FFBA08"
TRAFFIC_TEAL = "#2EC4B6"
TRAFFIC_SLATE = "#58A6FF"
TRAFFIC_TEXT_PRIMARY = "#F0F6FC"
TRAFFIC_TEXT_MUTED = "#8B949E"

# ── AQI: atmospheric analytical ──────────────────────────────────────────────
AQI_BG = "#0A0F1E"
AQI_SURFACE = "#111827"
AQI_SURFACE_1 = AQI_SURFACE
AQI_SURFACE_2 = "#1A2333"
AQI_SURFACE_3 = "#1F2D42"
AQI_SURFACE_4 = "#243344"
AQI_BORDER = "#1F2937"
AQI_BORDER_1 = AQI_BORDER
AQI_BORDER_2 = "#162032"
AQI_BORDER_HOVER = "#374151"
AQI_NAVY = "#1E3A5F"
AQI_CYAN = "#38BDF8"
AQI_STEEL = "#64748B"
AQI_MUTED_GREEN = "#34D399"
AQI_TEXT_PRIMARY = "#E5E7EB"
AQI_TEXT_MUTED = "#6B7280"

# ── AQI category scale — muted scientific palette (Phase 3.5) ───────────────
AQI_COLOR_GOOD = "#3D7A5C"
AQI_COLOR_SATISFACTORY = "#5A8F72"
AQI_COLOR_MODERATE = "#8A7B4E"
AQI_COLOR_POOR = "#B07A45"
AQI_COLOR_VERY_POOR = "#A85A5A"
AQI_COLOR_SEVERE = "#6E5A82"

AQI_SCALE_COLORS = [
    AQI_COLOR_GOOD,
    AQI_COLOR_SATISFACTORY,
    AQI_COLOR_MODERATE,
    AQI_COLOR_POOR,
    AQI_COLOR_VERY_POOR,
    AQI_COLOR_SEVERE,
]

# ── Shared typography families ───────────────────────────────────────────────
FONT_FAMILY = "'Inter', 'Segoe UI', sans-serif"
FONT_MONO = "'JetBrains Mono', 'Fira Code', monospace"

# ── Spacing scale ────────────────────────────────────────────────────────────
SPACING_XS = 4
SPACING_SM = 8
SPACING_MD = 16
SPACING_LG = 24
SPACING_XL = 40
SPACING_2XL = 64

GAP_TIGHT = SPACING_SM
GAP_DEFAULT = SPACING_MD
GAP_SECTION = SPACING_LG
GAP_ZONE = SPACING_XL
GAP_PAGE_SECTION = 32

# ── Border radius scale ──────────────────────────────────────────────────────
RADIUS_SM = 4
RADIUS_MD = 6
RADIUS_LG = 8
RADIUS_XL = 12
RADIUS_XL = 12

# ── Elevation (dark theme: borders + surface lift, no box-shadow) ────────────
ELEVATION_0 = "none"
ELEVATION_1 = f"1px solid {TRAFFIC_BORDER_1}"
ELEVATION_2 = f"1px solid {TRAFFIC_BORDER_HOVER}"

# ── Severity semantic palette ──────────────────────────────────────────────────
SEVERITY_CRITICAL = "critical"
SEVERITY_WARNING = "warning"
SEVERITY_SAFE = "safe"
SEVERITY_NEUTRAL = "neutral"
SEVERITY_INFO = "info"


def get_severity_colors(dashboard: DashboardId) -> dict[str, str]:
    tokens = get_dashboard_tokens(dashboard)
    return {
        SEVERITY_CRITICAL: tokens["severity_critical"],
        SEVERITY_WARNING: tokens["severity_warning"],
        SEVERITY_SAFE: tokens["severity_safe"],
        SEVERITY_NEUTRAL: tokens["text_primary"],
        SEVERITY_INFO: tokens["accent_secondary"],
        "info": tokens["accent_secondary"],
    }


TRAFFIC_LIGHT = {
    "dashboard": "traffic",
    "bg": "#F4F6F8",
    "surface": "#FFFFFF",
    "surface_2": "#F0F2F5",
    "surface_3": "#E8EBEF",
    "surface_4": "#DEE3EA",
    "border": "#CBD2D9",
    "border_2": "#E5E7EB",
    "border_hover": "#94A3B8",
    "accent": "#C92A2A",
    "accent_secondary": "#1D4ED8",
    "accent_gradient_start": "#FFFFFF",
    "accent_gradient_end": "#F4F6F8",
    "severity_critical": "#B42318",
    "severity_warning": "#B54708",
    "severity_safe": "#0F766E",
    "text_primary": "#111827",
    "text_muted": "#4B5563",
    "filter_shelf": "#FFFFFF",
    "identity_label": "Traffic intelligence",
    "platform_tagline": "Operational urban mobility analytics",
    "lab_atmosphere": "#E8EBEF",
}

AQI_LIGHT = {
    "dashboard": "aqi",
    "bg": "#F8FAFC",
    "surface": "#FFFFFF",
    "surface_2": "#F1F5F9",
    "surface_3": "#E2E8F0",
    "surface_4": "#CBD5E1",
    "border": "#CBD5E1",
    "border_2": "#E2E8F0",
    "border_hover": "#94A3B8",
    "accent": "#0284C7",
    "accent_secondary": "#059669",
    "accent_gradient_start": "#FFFFFF",
    "accent_gradient_end": "#F8FAFC",
    "severity_critical": "#6E5A82",
    "severity_warning": "#B07A45",
    "severity_safe": "#3D7A5C",
    "text_primary": "#0F172A",
    "text_muted": "#475569",
    "filter_shelf": "#FFFFFF",
    "identity_label": "AQI environmental intelligence",
    "platform_tagline": "Atmospheric environmental analytics",
    "lab_atmosphere": "#E2E8F0",
}


def get_dashboard_tokens(dashboard: DashboardId, appearance: AppearanceId = "dark") -> dict:
    """Full token bundle for a dashboard identity (dark default, optional light)."""
    if appearance == "light":
        base = TRAFFIC_LIGHT if dashboard == "traffic" else AQI_LIGHT
        return dict(base)
    if dashboard == "aqi":
        return {
            "dashboard": "aqi",
            "bg": AQI_BG,
            "surface": AQI_SURFACE_1,
            "surface_2": AQI_SURFACE_2,
            "surface_3": AQI_SURFACE_3,
            "surface_4": AQI_SURFACE_4,
            "border": AQI_BORDER_1,
            "border_2": AQI_BORDER_2,
            "border_hover": AQI_BORDER_HOVER,
            "accent": AQI_CYAN,
            "accent_secondary": AQI_MUTED_GREEN,
            "accent_gradient_start": AQI_NAVY,
            "accent_gradient_end": AQI_BG,
            "severity_critical": AQI_COLOR_SEVERE,
            "severity_warning": AQI_COLOR_POOR,
            "severity_safe": AQI_MUTED_GREEN,
            "text_primary": AQI_TEXT_PRIMARY,
            "text_muted": AQI_TEXT_MUTED,
            "filter_shelf": AQI_SURFACE_3,
            "identity_label": "AQI environmental intelligence",
            "platform_tagline": "Atmospheric environmental analytics",
            "lab_atmosphere": AQI_NAVY,
        }
    return {
        "dashboard": "traffic",
        "bg": TRAFFIC_BG,
        "surface": TRAFFIC_SURFACE_1,
        "surface_2": TRAFFIC_SURFACE_2,
        "surface_3": TRAFFIC_SURFACE_3,
        "surface_4": TRAFFIC_SURFACE_4,
        "border": TRAFFIC_BORDER_1,
        "border_2": TRAFFIC_BORDER_2,
        "border_hover": TRAFFIC_BORDER_HOVER,
        "accent": TRAFFIC_CRIMSON,
        "accent_secondary": TRAFFIC_SLATE,
        "accent_gradient_start": TRAFFIC_SURFACE_1,
        "accent_gradient_end": TRAFFIC_BG,
        "severity_critical": TRAFFIC_CRIMSON,
        "severity_warning": TRAFFIC_AMBER,
        "severity_safe": TRAFFIC_TEAL,
        "text_primary": TRAFFIC_TEXT_PRIMARY,
        "text_muted": TRAFFIC_TEXT_MUTED,
        "filter_shelf": TRAFFIC_SURFACE_3,
        "identity_label": "Traffic intelligence",
        "platform_tagline": "Operational urban mobility analytics",
        "lab_atmosphere": TRAFFIC_SURFACE_2,
    }
