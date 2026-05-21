"""Traffic filter application."""

import pandas as pd

from config.data_config import COL_AREA, COL_DATE
from filters.state import TRAFFIC_STATE_DEFAULTS


def apply_traffic_filters(df: pd.DataFrame, state: dict, exclude_date_filter: bool = False) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if not exclude_date_filter:
        start = pd.Timestamp(state.get("traffic_date_start", TRAFFIC_STATE_DEFAULTS["traffic_date_start"]))
        end = pd.Timestamp(state.get("traffic_date_end", TRAFFIC_STATE_DEFAULTS["traffic_date_end"]))
        out = out[(out[COL_DATE] >= start) & (out[COL_DATE] <= end)]
    areas = state.get("traffic_selected_areas") or []
    if areas:
        out = out[out[COL_AREA].isin(areas)]
    return out


def reset_traffic_filters() -> None:
    import streamlit as st

    from filters.interaction import clear_traffic_selection

    for key, value in TRAFFIC_STATE_DEFAULTS.items():
        if key.startswith("traffic_"):
            st.session_state[key] = value
    clear_traffic_selection()
    st.session_state["traffic_filters_active"] = False
    st.cache_data.clear()
