"""p6_advanced_lab — T-02 investigative · staged radar mount."""

from components.page_runtime import render_page


def render() -> None:
    render_page("traffic", "p6_advanced_lab", is_lab=True)
