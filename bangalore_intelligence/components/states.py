"""Component visual state modifiers — consistent across all UI."""

from typing import Literal

ComponentState = Literal[
    "default",
    "loading",
    "empty",
    "filtered",
    "stale",
    "selected",
    "disabled",
    "fullscreen",
]


def border_for_state(state: ComponentState, tokens: dict) -> str:
    if state == "selected":
        return f"1px solid {tokens['severity_warning']}"
    if state == "stale":
        return f"1px solid {tokens['severity_warning']}55"
    if state == "empty":
        return f"1px dashed {tokens['border']}"
    if state == "disabled":
        return f"1px solid {tokens['border_2']}"
    return f"1px solid {tokens['border']}"


def opacity_for_state(state: ComponentState) -> float:
    if state == "disabled":
        return 0.4
    if state == "stale":
        return 0.92
    return 1.0
