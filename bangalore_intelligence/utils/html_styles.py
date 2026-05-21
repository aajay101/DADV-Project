"""Centralized HTML/CSS builders from theme tokens — triple-quoted fragments only."""

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
    class_attr = f' class="{class_name}"' if class_name else ""
    html = f"""
    <div{class_attr} style="{style}">
        {content}
    </div>
    """
    return html.strip()


def styled_div(content: str, style: str, class_name: str = "") -> str:
    """Block element with inline styles."""
    return wrap_div(content, style, class_name)


def styled_p(content: str, style: str) -> str:
    html = f"""
    <p style="{style}">
        {content}
    </p>
    """
    return html.strip()


def styled_span(content: str, style: str) -> str:
    html = f"""
    <span style="{style}">
        {content}
    </span>
    """
    return html.strip()


def spacer(px: int) -> str:
    html = f"""
    <div style="height:{px}px;"></div>
    """
    return html.strip()


def pill_badge(text: str, bg: str, color: str, border: str | None = None) -> str:
    border_line = f"border:1px solid {border};" if border else ""
    html = f"""
    <span style="
        display:inline-block;
        padding:{SPACING_XS}px {SPACING_MD}px;
        font-size:10px;
        font-weight:600;
        letter-spacing:0.06em;
        text-transform:uppercase;
        border-radius:{RADIUS_LG}px;
        background:{bg};
        color:{color};
        {border_line}
    ">{text}</span>
    """
    return html.strip()


def left_accent_bar(color: str) -> str:
    return f"border-left:3px solid {color};"


def chart_shell_classes(role: str) -> str:
    base = "buip-chart-shell"
    if role == "hero":
        return f"{base} buip-chart-shell--hero"
    return f"{base} buip-chart-shell--support"
