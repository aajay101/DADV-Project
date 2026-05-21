"""AQI filter application."""

import pandas as pd

from config.data_config import COL_AQI_CATEGORY, COL_DATE, COL_SEASON
from filters.state import AQI_STATE_DEFAULTS


def apply_aqi_filters(df: pd.DataFrame, state: dict, exclude_date_filter: bool = False) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if not exclude_date_filter:
        start = pd.Timestamp(state.get("aqi_date_start", AQI_STATE_DEFAULTS["aqi_date_start"]))
        end = pd.Timestamp(state.get("aqi_date_end", AQI_STATE_DEFAULTS["aqi_date_end"]))
        out = out[(out[COL_DATE] >= start) & (out[COL_DATE] <= end)]
    categories = state.get("aqi_selected_categories") or []
    if categories:
        out = out[out[COL_AQI_CATEGORY].isin(categories)]
    seasons = state.get("aqi_selected_seasons") or []
    if seasons:
        out = out[out[COL_SEASON].isin(seasons)]
    return out


def reset_aqi_filters() -> None:
    import streamlit as st

    from filters.interaction import clear_aqi_selection

    for key, value in AQI_STATE_DEFAULTS.items():
        if key.startswith("aqi_"):
            st.session_state[key] = value
    clear_aqi_selection()
    st.session_state["aqi_filters_active"] = False
    st.cache_data.clear()
