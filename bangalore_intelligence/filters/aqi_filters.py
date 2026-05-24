"""AQI filter application."""

import pandas as pd

from config.data_config import COL_AQI_CATEGORY, COL_DATE, COL_SEASON
from filters.state import AQI_STATE_DEFAULTS
from utils.validators import validate_date_range, validate_filter_date_range


def apply_aqi_filters(df: pd.DataFrame, state: dict, exclude_date_filter: bool = False) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if not exclude_date_filter:
        start = state.get("aqi_date_start", AQI_STATE_DEFAULTS["aqi_date_start"])
        end = state.get("aqi_date_end", AQI_STATE_DEFAULTS["aqi_date_end"])
        if not validate_filter_date_range(start, end).ok:
            return out.iloc[0:0].copy()
        if not validate_date_range(out, start, end, COL_DATE).ok:
            return out.iloc[0:0].copy()
        start_ts = pd.Timestamp(start)
        end_ts = pd.Timestamp(end)
        out = out[(out[COL_DATE] >= start_ts) & (out[COL_DATE] <= end_ts)]
    categories = state.get("aqi_selected_categories") or []
    if categories:
        out = out[out[COL_AQI_CATEGORY].isin(categories)]
    seasons = state.get("aqi_selected_seasons") or []
    if seasons:
        out = out[out[COL_SEASON].isin(seasons)]
    return out


def reset_aqi_filters() -> None:
    from filters.transitions import GlobalFiltersReset, dispatch

    dispatch(GlobalFiltersReset(dashboard="aqi"))
