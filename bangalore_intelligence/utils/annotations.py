"""Plotly annotation factories — tokenized styles and count governance."""

from __future__ import annotations

from typing import Any, Literal

import plotly.graph_objects as go

from config.theme import FONT_FAMILY, get_dashboard_tokens

AnnotationPriority = Literal["threshold", "quadrant", "callout", "context"]

_PRIORITY_RANK = {"threshold": 0, "quadrant": 1, "callout": 2, "context": 3}


def _base_style(dashboard: str = "traffic") -> dict:
    tokens = get_dashboard_tokens(dashboard)
    return {
        "font": dict(
            family=FONT_FAMILY,
            size=11,
            color=tokens["text_primary"],
        ),
        "bgcolor": tokens["surface_2"],
        "bordercolor": tokens["border"],
        "borderwidth": 1,
        "borderpad": 4,
        "opacity": 0.95,
    }


def _merge_annotation(
    base: dict,
    *,
    x: object = None,
    y: object = None,
    text: str = "",
    showarrow: bool = False,
    arrowcolor: str | None = None,
    ax: int = 0,
    ay: int = -24,
    xref: str = "x",
    yref: str = "y",
    priority: AnnotationPriority = "callout",
) -> dict:
    out = {**base, "text": text, "showarrow": showarrow, "xref": xref, "yref": yref}
    if x is not None:
        out["x"] = x
    if y is not None:
        out["y"] = y
    if showarrow:
        out["ax"] = ax
        out["ay"] = ay
        if arrowcolor:
            out["arrowcolor"] = arrowcolor
            out["arrowsize"] = 1
            out["arrowwidth"] = 1.5
    out["_buip_priority"] = priority
    return out


def step_callout(
    x: object,
    y: object,
    delta_text: str,
    color: str,
    dashboard: str = "traffic",
) -> dict:
    """Build styled step-change callout annotation."""
    base = _base_style(dashboard)
    return _merge_annotation(
        base,
        x=x,
        y=y,
        text=delta_text,
        showarrow=True,
        arrowcolor=color,
        ay=-32,
        priority="callout",
    )


def threshold_label(
    y: object,
    label: str,
    side: str = "right",
    dashboard: str = "traffic",
) -> dict:
    xanchor = "left" if side == "right" else "right"
    base = _base_style(dashboard)
    ann = _merge_annotation(
        base,
        y=y,
        text=label,
        xref="paper",
        x=1.0 if side == "right" else 0.0,
        yref="y",
        showarrow=False,
        priority="threshold",
    )
    ann["xanchor"] = xanchor
    return ann


def quadrant_label(x: object, y: object, archetype_text: str, dashboard: str = "traffic") -> dict:
    return _merge_annotation(
        _base_style(dashboard),
        x=x,
        y=y,
        text=archetype_text,
        showarrow=False,
        priority="quadrant",
    )


def regime_annotation(x: object, y: object, regime_name: str, dashboard: str = "traffic") -> dict:
    return _merge_annotation(
        _base_style(dashboard),
        x=x,
        y=y,
        text=regime_name,
        showarrow=True,
        ay=-20,
        arrowcolor=get_dashboard_tokens(dashboard)["accent"],
        priority="context",
    )


def aqi_band_label(y: object, category_name: str, dashboard: str = "aqi") -> dict:
    return _merge_annotation(
        _base_style(dashboard),
        y=y,
        text=category_name,
        xref="paper",
        x=0.02,
        yref="y",
        showarrow=False,
        priority="threshold",
    )


def insight_callout(
    x: object,
    y: object,
    text: str,
    arrow_dir: str = "up",
    dashboard: str = "traffic",
) -> dict:
    ay = -28 if arrow_dir == "up" else 28
    tokens = get_dashboard_tokens(dashboard)
    return _merge_annotation(
        _base_style(dashboard),
        x=x,
        y=y,
        text=text,
        showarrow=True,
        arrowcolor=tokens["severity_warning"],
        ay=ay,
        priority="callout",
    )


def enforce_annotation_limit(annotations: list[dict], max_count: int = 3) -> list[dict]:
    """Return annotations trimmed by governance priority (threshold first)."""
    if len(annotations) <= max_count:
        return [_strip_priority(a) for a in annotations]

    ranked = sorted(
        annotations,
        key=lambda a: _PRIORITY_RANK.get(a.get("_buip_priority", "context"), 9),
    )
    return [_strip_priority(a) for a in ranked[:max_count]]


def _strip_priority(ann: dict) -> dict:
    return {k: v for k, v in ann.items() if k != "_buip_priority"}


def add_annotation_callout(
    fig: go.Figure,
    x: object,
    y: object,
    text: str,
    dashboard: str = "traffic",
) -> go.Figure:
    """Apply a styled callout and return fig."""
    existing = list(fig.layout.annotations or ())
    new_list = enforce_annotation_limit(
        [*[_to_dict(a) for a in existing], insight_callout(x, y, text, dashboard=dashboard)],
    )
    fig.update_layout(annotations=new_list)
    return fig


def add_quadrant_zone_labels(
    fig: go.Figure,
    labels: list[tuple[object, object, str]],
    dashboard: str = "traffic",
) -> go.Figure:
    """Apply up to three quadrant labels."""
    anns = [quadrant_label(x, y, t, dashboard=dashboard) for x, y, t in labels]
    fig.update_layout(annotations=enforce_annotation_limit(anns))
    return fig


def _to_dict(ann: Any) -> dict:
    if isinstance(ann, dict):
        return ann
    return dict(ann) if hasattr(ann, "items") else {"text": str(ann)}
