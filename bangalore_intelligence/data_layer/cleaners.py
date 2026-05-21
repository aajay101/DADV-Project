"""Cleaning, typing, and derived column computation."""

import numpy as np
import pandas as pd

from config.data_config import (
    COL_AQI_CATEGORY,
    COL_CONGESTION,
    COL_CAPACITY,
    COL_DATE,
    COL_PM25,
    COL_SEASON,
    COL_SLP,
    COL_TM,
    COL_TM_MAX,
    COL_V,
    COL_VM,
    COL_VV,
)


def _pm25_to_category(series: pd.Series) -> pd.Series:
    return pd.cut(
        series,
        bins=[-np.inf, 30, 60, 90, 120, 250, np.inf],
        labels=["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"],
    ).astype(str)


def _month_to_season(month: int) -> str:
    if month in (12, 1, 2):
        return "Winter"
    if month in (3, 4, 5):
        return "Spring"
    if month in (6, 7, 8, 9):
        return "Monsoon"
    return "Post-Monsoon"


def clean_traffic(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out[COL_DATE] = pd.to_datetime(out[COL_DATE])
    out["day_of_week"] = out[COL_DATE].dt.day_name()
    out["month_year"] = out[COL_DATE].dt.to_period("M").astype(str)
    out["at_max_capacity"] = out[COL_CAPACITY] >= 99.5
    out["environmental_impact"] = (out[COL_CONGESTION] * 0.6 + out[COL_CAPACITY] * 0.4).round(1)
    return out.sort_values(COL_DATE).reset_index(drop=True)


def clean_aqi(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out[COL_DATE] = pd.to_datetime(out[COL_DATE])
    out[COL_AQI_CATEGORY] = _pm25_to_category(out[COL_PM25])
    out[COL_SEASON] = out[COL_DATE].dt.month.map(_month_to_season)
    out["temp_spread"] = (out[COL_TM_MAX] - out[COL_TM]).round(1)
    out["gust_ratio"] = np.where(out[COL_V] > 0, (out[COL_VM] / out[COL_V]).round(2), 0.0)
    out["slp_band"] = pd.cut(
        out[COL_SLP],
        bins=[-np.inf, 1005, 1015, np.inf],
        labels=["Low", "Normal", "High"],
    ).astype(str)
    out["vv_band"] = pd.cut(
        out[COL_VV],
        bins=[-np.inf, 1.0, 3.0, np.inf],
        labels=["Low", "Moderate", "High"],
    ).astype(str)
    out["wind_band"] = pd.cut(
        out[COL_V],
        bins=[-np.inf, 1.5, 4.0, np.inf],
        labels=["Calm", "Moderate", "Strong"],
    ).astype(str)
    out["rolling_7d_pm25"] = out[COL_PM25].rolling(7, min_periods=1).mean().round(1)
    out["year"] = out[COL_DATE].dt.year
    out["week"] = out[COL_DATE].dt.isocalendar().week.astype(int)
    return out.sort_values(COL_DATE).reset_index(drop=True)
