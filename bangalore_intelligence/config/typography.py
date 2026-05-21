"""Typography hierarchy tokens — single source for all text roles."""

from config.theme import FONT_FAMILY, FONT_MONO

TYPE_HERO_TITLE = {
    "family": FONT_FAMILY,
    "size": "20px",
    "weight": "700",
    "letter_spacing": "-0.02em",
    "line_height": "1.25",
    "transform": "none",
}

TYPE_SECTION_TITLE = {
    "family": FONT_FAMILY,
    "size": "16px",
    "weight": "600",
    "letter_spacing": "0.05em",
    "line_height": "1.4",
    "transform": "uppercase",
}

TYPE_SUBSECTION_TITLE = {
    "family": FONT_FAMILY,
    "size": "13px",
    "weight": "500",
    "letter_spacing": "0.04em",
    "line_height": "1.45",
    "transform": "uppercase",
}

TYPE_KPI_VALUE = {
    "family": FONT_MONO,
    "size": "32px",
    "weight": "700",
    "letter_spacing": "-0.02em",
    "line_height": "1.1",
    "transform": "none",
}

TYPE_KPI_VALUE_LARGE = {
    **TYPE_KPI_VALUE,
    "size": "40px",
    "weight": "800",
}

TYPE_KPI_VALUE_COMPACT = {
    **TYPE_KPI_VALUE,
    "size": "24px",
}

TYPE_KPI_LABEL = {
    "family": FONT_FAMILY,
    "size": "12px",
    "weight": "600",
    "letter_spacing": "0.04em",
    "line_height": "1.45",
    "transform": "uppercase",
}

TYPE_BODY = {
    "family": FONT_FAMILY,
    "size": "14px",
    "weight": "400",
    "letter_spacing": "0",
    "line_height": "1.65",
    "transform": "none",
}

TYPE_MUTED = {
    "family": FONT_FAMILY,
    "size": "14px",
    "weight": "400",
    "letter_spacing": "0",
    "line_height": "1.65",
    "transform": "none",
}

TYPE_CAPTION = {
    "family": FONT_FAMILY,
    "size": "13px",
    "weight": "400",
    "letter_spacing": "0.02em",
    "line_height": "1.55",
    "transform": "none",
}

TYPE_ALERT = {
    "family": FONT_FAMILY,
    "size": "13px",
    "weight": "600",
    "letter_spacing": "0.03em",
    "line_height": "1.45",
    "transform": "none",
}

TYPE_CHART_HERO = TYPE_SECTION_TITLE
TYPE_CHART_SUPPORT = TYPE_SUBSECTION_TITLE


def css_from_type(scale: dict, color: str, extra: str = "") -> str:
    """Build inline CSS from a type scale entry."""
    transform = scale.get("transform", "none")
    transform_css = f"text-transform:{transform};" if transform != "none" else ""
    extra_css = extra.strip()
    if extra_css and not extra_css.endswith(";"):
        extra_css += ";"
    return (
        f"font-family:{scale['family']};"
        f"font-size:{scale['size']};"
        f"font-weight:{scale['weight']};"
        f"letter-spacing:{scale['letter_spacing']};"
        f"line-height:{scale['line_height']};"
        f"color:{color};"
        f"{transform_css}"
        f"{extra_css}"
    )
