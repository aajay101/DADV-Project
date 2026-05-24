"""HTML render sanitization — regression guards for Streamlit leakage."""

from utils.html_styles import pill_badge, styled_div
from utils.ui_blocks import (
    escape_text,
    sanitize_html_fragment,
)


def test_escape_text_prevents_tag_injection():
    raw = '<script>alert(1)</script> & "quotes"'
    out = escape_text(raw)
    assert "<script>" not in out
    assert "&lt;script&gt;" in out


def test_sanitize_collapses_multiline_style_attributes():
    fragment = """
    <div style="
        margin-bottom:24px;
        padding:8px;
    ">Label</div>
    """
    safe = sanitize_html_fragment(fragment)
    assert "\n" not in safe
    assert 'style="margin-bottom:24px;padding:8px;"' in safe or "margin-bottom:24px" in safe


def test_sanitize_strips_leading_orphan_close_tags():
    leaked = "</div></span><p>Showing: Indiranagar</p>"
    safe = sanitize_html_fragment(leaked)
    assert not safe.startswith("</div>")
    assert "Showing: Indiranagar" in safe


def test_pill_badge_single_line():
    html = pill_badge("Showing: Koramangala", "#11223344", "#ff0", "#333")
    assert "\n" not in html
    assert html.startswith("<span")


def test_styled_div_escapes_content():
    html = styled_div('</div><span style="color:red">', "color:#fff;")
    assert "&lt;/div&gt;" in html
