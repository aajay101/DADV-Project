"""Centralized HTML/CSS builders from theme tokens — single-line, escaped content."""

from utils.ui_blocks import escape_text
from config.theme import RADIUS_LG, SPACING_MD, SPACING_XS


def join_styles(*chunks: str) -> str:
    """Merge inline CSS fragments with guaranteed semicolon separation."""
    parts: list[str] = []
    for chunk in chunks:
        if not chunk or not str(chunk).strip():
            continue
        parts.append(str(chunk).strip().rstrip(";") + ";")
    return "".join(parts)


def wrap_div(content: str, style: str, class_name: str = "") -> str:
    class_attr = f' class="{escape_text(class_name)}"' if class_name else ""
    return (
        f'<div{class_attr} style="{join_styles(style)}">{escape_text(content)}</div>'
    )


def styled_div(content: str, style: str, class_name: str = "") -> str:
    return wrap_div(content, style, class_name)


def styled_p(content: str, style: str) -> str:
    return f'<p style="{join_styles(style)}">{escape_text(content)}</p>'


def styled_span(content: str, style: str) -> str:
    return f'<span style="{join_styles(style)}">{escape_text(content)}</span>'


def spacer(px: int) -> str:
    """HTML string for embedding in composed blocks (prefer render_spacer for standalone gaps)."""
    return f'<div style="height:{max(0, int(px))}px;" aria-hidden="true"></div>'


def pill_badge(
    text: str,
    bg: str,
    color: str,
    border: str | None = None,
    *,
    inline_gap: int | None = None,
) -> str:
    border_line = f"border:1px solid {border};" if border else ""
    margin = f"margin-left:{inline_gap}px;" if inline_gap else ""
    style = join_styles(
        "display:inline-block",
        "vertical-align:middle",
        f"padding:{SPACING_XS + 2}px {SPACING_MD}px",
        "font-size:10px",
        "font-weight:600",
        "letter-spacing:0.06em",
        "text-transform:uppercase",
        "line-height:1.35",
        f"border-radius:{RADIUS_LG}px",
        f"background:{bg}",
        f"color:{color}",
        "white-space:nowrap",
        border_line,
        margin,
    )
    return f'<span style="{style}">{escape_text(text)}</span>'


def left_accent_bar(color: str) -> str:
    return f"border-left:3px solid {color};"


def chart_shell_classes(role: str) -> str:
    base = "buip-chart-shell"
    if role == "hero":
        return f"{base} buip-chart-shell--hero"
    return f"{base} buip-chart-shell--support"
