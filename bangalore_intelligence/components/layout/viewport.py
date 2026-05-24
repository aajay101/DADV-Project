"""Browser viewport width — inline v2 component writes width into session state."""

from __future__ import annotations

from typing import Any

import streamlit as st
import streamlit.components.v2 as components_v2

from components.layout.responsive import get_breakpoint, is_compact

# Ignore sub-pixel jitter; rerun only when breakpoint class changes
_WIDTH_MATERIAL_DELTA = 40

_VIEWPORT_JS = """
export default function(component) {
  const { setStateValue } = component;

  function measureWidth() {
    try {
      const doc = document.documentElement;
      const body = document.body;
      const w = Math.max(
        doc ? doc.clientWidth : 0,
        body ? body.clientWidth : 0,
        window.innerWidth || 0
      );
      return Math.round(w) || 1280;
    } catch (e) {
      return Math.round(window.innerWidth) || 1280;
    }
  }

  let lastSent = null;
  let debounceTimer = null;

  function publish() {
    const w = measureWidth();
    if (lastSent !== null && Math.abs(w - lastSent) < 24) {
      return;
    }
    lastSent = w;
    setStateValue("width", w);
  }

  function schedulePublish() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(publish, 180);
  }

  publish();
  window.addEventListener("resize", schedulePublish);

  let ro = null;
  if (typeof ResizeObserver !== "undefined") {
    ro = new ResizeObserver(schedulePublish);
    ro.observe(document.documentElement);
  }

  return () => {
    window.removeEventListener("resize", schedulePublish);
    if (ro) {
      ro.disconnect();
    }
  };
}
"""

_VIEWPORT_CSS = """
:host {
  display: block;
  height: 0;
  overflow: hidden;
  margin: 0;
  padding: 0;
}
"""

# Register once per process — avoids v1 file-serving failures on Windows/OneDrive.
_VIEWPORT_PROBE = components_v2.component(
    "buip_viewport_probe",
    js=_VIEWPORT_JS,
    css=_VIEWPORT_CSS,
    isolate_styles=False,
)


def _probe_browser_width() -> int | None:
    """Read width from zero-height inline component (None until JS runs)."""
    result: Any = _VIEWPORT_PROBE(
        key="buip_viewport_probe",
        height=0,
        on_width_change=lambda: None,
    )
    raw = getattr(result, "width", None)
    if raw is None:
        return None
    try:
        w = int(round(float(raw)))
    except (TypeError, ValueError):
        return None
    return w if w > 0 else None


def apply_viewport_measurement(measured: int | None) -> tuple[int, bool]:
    """
    Persist viewport session keys from a measured width.

    Returns (effective_width, should_rerun) where rerun is True only when
    the breakpoint *category* changes (avoids resize churn).
    """
    if measured is None:
        measured = int(st.session_state.get("viewport_width", 1280))

    prev_width = st.session_state.get("_buip_viewport_measured")
    old_bp = st.session_state.get("viewport_breakpoint")
    new_bp = get_breakpoint(measured)

    width_changed_materially = (
        prev_width is None or abs(int(measured) - int(prev_width)) >= _WIDTH_MATERIAL_DELTA
    )

    if width_changed_materially or old_bp != new_bp:
        st.session_state["viewport_width"] = measured
        st.session_state["viewport_breakpoint"] = new_bp
        st.session_state["compact_mode"] = is_compact(measured)
        st.session_state["advanced_lab_disabled_compact"] = is_compact(measured)
        st.session_state["_buip_viewport_measured"] = measured

    should_rerun = (
        prev_width is not None
        and old_bp is not None
        and old_bp != new_bp
        and width_changed_materially
    )
    return measured, should_rerun


def sync_viewport_width() -> int:
    """
    Probe browser width once per run; initialize defaults if JS has not reported yet.
    Reruns at most once when the user crosses a breakpoint boundary.
    """
    if "viewport_width" not in st.session_state:
        st.session_state["viewport_width"] = 1280
        st.session_state["viewport_breakpoint"] = get_breakpoint(1280)
        st.session_state["compact_mode"] = is_compact(1280)
        st.session_state["advanced_lab_disabled_compact"] = is_compact(1280)

    probed = _probe_browser_width()
    effective, should_rerun = apply_viewport_measurement(probed)

    if should_rerun and not st.session_state.get("_buip_viewport_rerun_guard"):
        st.session_state["_buip_viewport_rerun_guard"] = True
        st.rerun()

    st.session_state.pop("_buip_viewport_rerun_guard", None)
    return int(effective)
