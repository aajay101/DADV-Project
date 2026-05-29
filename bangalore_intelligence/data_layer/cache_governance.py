"""Cache fingerprint diagnostics and invalidation helpers."""

from __future__ import annotations

from typing import Any

import streamlit as st

from data_layer.governance import active_dataset_fingerprint


def current_cache_fingerprint(dashboard: str, filter_state: dict[str, Any]) -> str:
    dataset_fp = active_dataset_fingerprint(dashboard)
    relevant = {
        key: str(value)
        for key, value in sorted(filter_state.items())
        if key.startswith(f"{dashboard}_")
        and any(part in key for part in ("date", "selected", "filter"))
    }
    return f"{dataset_fp}:{hash(tuple(relevant.items()))}"


def cache_diagnostics(dashboard: str) -> dict[str, Any]:
    return {
        "dashboard": dashboard,
        "dataset_fingerprint": active_dataset_fingerprint(dashboard),
        "lazy_cache_keys": [
            key for key in st.session_state.keys()
            if isinstance(key, str) and key.startswith(f"buip_lazy_{dashboard}_")
        ],
    }
