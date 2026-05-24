"""Dashboard shell accessibility checks — contrast and caption policy."""

from __future__ import annotations

from typing import Any

from config.theme import get_dashboard_tokens

WCAG_AA_NORMAL = 4.5
WCAG_AA_LARGE = 3.0


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    color = hex_color.strip().lstrip("#")
    if len(color) == 3:
        color = "".join(ch * 2 for ch in color)
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def _relative_luminance(hex_color: str) -> float:
    r, g, b = _hex_to_rgb(hex_color)

    def channel(c: int) -> float:
        s = c / 255.0
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(foreground: str, background: str) -> float:
    l1 = _relative_luminance(foreground)
    l2 = _relative_luminance(background)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def audit_token_pairs(
    pairs: list[tuple[str, str, str, float]],
    tokens: dict[str, str],
) -> list[dict[str, Any]]:
    """Return contrast results for foreground/background token pairs."""
    results: list[dict[str, Any]] = []
    for fg_key, bg_key, label, required in pairs:
        fg = tokens[fg_key]
        bg = tokens[bg_key]
        ratio = contrast_ratio(fg, bg)
        results.append(
            {
                "label": label,
                "foreground": fg_key,
                "background": bg_key,
                "ratio": round(ratio, 2),
                "required": required,
                "pass": ratio >= required,
            }
        )
    return results


def audit_dashboard_shell(dashboard: str = "traffic", *, appearance: str = "dark") -> dict[str, Any]:
    """WCAG-style contrast audit for primary dashboard chrome tokens."""
    tokens = get_dashboard_tokens(dashboard, appearance=appearance)
    pairs = [
        ("text_primary", "bg", "Primary text on page background", WCAG_AA_NORMAL),
        ("text_primary", "surface_2", "Primary text on elevated surface", WCAG_AA_NORMAL),
        ("text_muted", "surface_2", "Muted text on elevated surface", WCAG_AA_NORMAL),
        ("text_muted", "bg", "Muted text on page background", WCAG_AA_NORMAL),
        ("severity_critical", "surface_2", "Critical severity on surface", WCAG_AA_LARGE),
        ("severity_warning", "surface_2", "Warning severity on surface", WCAG_AA_LARGE),
        ("accent", "bg", "Accent on background", WCAG_AA_LARGE),
    ]
    checks = audit_token_pairs(pairs, tokens)
    failures = [c for c in checks if not c["pass"]]
    return {
        "dashboard": dashboard,
        "appearance": appearance,
        "checks": checks,
        "pass": len(failures) == 0,
        "failure_count": len(failures),
    }


def chart_accessibility_requirements() -> dict[str, Any]:
    """Policy for chart slots rendered via chart_container."""
    return {
        "require_title": True,
        "require_caption_or_subtitle": True,
        "keyboard_focusable_controls": [
            "plotly_chart with on_select",
            "fullscreen_button",
        ],
        "export_includes_filter_metadata": False,
    }
