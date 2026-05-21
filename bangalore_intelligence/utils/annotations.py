"""Annotation factory stubs — return Plotly-compatible dicts in Phase 3+."""


def step_callout(x, y, delta_text, color):
    return {"x": x, "y": y, "text": delta_text, "showarrow": True, "font": {"color": color}}


def threshold_label(y, label, side="right"):
    return {"y": y, "text": label, "showarrow": False}


def quadrant_label(x, y, archetype_text):
    return {"x": x, "y": y, "text": archetype_text, "showarrow": False}


def regime_annotation(x, y, regime_name):
    return {"x": x, "y": y, "text": regime_name, "showarrow": False}


def aqi_band_label(y, category_name):
    return {"y": y, "text": category_name, "showarrow": False}


def insight_callout(x, y, text, arrow_dir="up"):
    return {"x": x, "y": y, "text": text, "showarrow": True}
