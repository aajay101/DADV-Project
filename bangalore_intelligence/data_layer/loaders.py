"""Dataset loading and caching."""

import pandas as pd
import streamlit as st

from config.data_config import AQI_CLEAN_PATH, AQI_RAW_PATH, TRAFFIC_CLEAN_PATH, TRAFFIC_RAW_PATH
from data_layer.bootstrap_data import ensure_raw_datasets
from data_layer.cleaners import clean_aqi, clean_traffic


@st.cache_data(show_spinner=False)
def load_traffic_clean() -> pd.DataFrame:
    ensure_raw_datasets()
    if TRAFFIC_CLEAN_PATH.exists() and TRAFFIC_CLEAN_PATH.stat().st_size > 100:
        df = pd.read_parquet(TRAFFIC_CLEAN_PATH)
    else:
        df = pd.read_csv(TRAFFIC_RAW_PATH)
        df = clean_traffic(df)
        TRAFFIC_CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(TRAFFIC_CLEAN_PATH, index=False)
    return df


@st.cache_data(show_spinner=False)
def load_aqi_clean() -> pd.DataFrame:
    ensure_raw_datasets()
    if AQI_CLEAN_PATH.exists() and AQI_CLEAN_PATH.stat().st_size > 100:
        df = pd.read_parquet(AQI_CLEAN_PATH)
    else:
        df = pd.read_csv(AQI_RAW_PATH)
        df = clean_aqi(df)
        AQI_CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(AQI_CLEAN_PATH, index=False)
    return df
