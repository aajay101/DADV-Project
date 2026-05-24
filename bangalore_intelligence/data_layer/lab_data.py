"""Advanced Lab dataset scope — full clean data, bypassing global filters."""

from __future__ import annotations

import pandas as pd

from data_layer.loaders import load_aqi_clean, load_traffic_clean
from filters.aqi_filters import apply_aqi_filters
from filters.traffic_filters import apply_traffic_filters


def get_lab_dataset(dashboard: str, state: dict | None = None) -> pd.DataFrame:
    """Return Advanced Lab dataset after global filters, with no silent full-data bypass."""
    if dashboard == "traffic":
        df = load_traffic_clean()
        return apply_traffic_filters(df, state or {}) if state is not None else df
    df = load_aqi_clean()
    return apply_aqi_filters(df, state or {}) if state is not None else df
