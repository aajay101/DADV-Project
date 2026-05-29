"""Traffic filter application."""

import pandas as pd

from config.data_config import COL_AREA, COL_DATE, COL_ROAD, COL_ROADWORK, COL_WEATHER
from filters.state import TRAFFIC_STATE_DEFAULTS
from utils.validators import validate_date_range, validate_filter_date_range


def apply_traffic_filters(df: pd.DataFrame, state: dict, exclude_date_filter: bool = False) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if not exclude_date_filter:
        start = state.get("traffic_date_start", TRAFFIC_STATE_DEFAULTS["traffic_date_start"])
        end = state.get("traffic_date_end", TRAFFIC_STATE_DEFAULTS["traffic_date_end"])
        if not validate_filter_date_range(start, end).ok:
            return out.iloc[0:0].copy()
        if not validate_date_range(out, start, end, COL_DATE).ok:
            return out.iloc[0:0].copy()
        start_ts = pd.Timestamp(start)
        end_ts = pd.Timestamp(end)
        out = out[(out[COL_DATE] >= start_ts) & (out[COL_DATE] <= end_ts)]

    areas = state.get("traffic_selected_areas") or []
    if areas:
        out = out[out[COL_AREA].isin(areas)]

    weather = state.get("traffic_selected_weather") or []
    if weather:
        out = out[out[COL_WEATHER].isin(weather)]

    roadwork = state.get("traffic_selected_roadwork", TRAFFIC_STATE_DEFAULTS["traffic_selected_roadwork"])
    if roadwork and roadwork != "Both":
        out = out[out[COL_ROADWORK] == roadwork]

    roads = state.get("traffic_selected_roads") or []
    if roads:
        out = out[out[COL_ROAD].isin(roads)]

    return out


def reset_traffic_filters() -> None:
    from filters.transitions import GlobalFiltersReset, dispatch

    dispatch(GlobalFiltersReset(dashboard="traffic"))
