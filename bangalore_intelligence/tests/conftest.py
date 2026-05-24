"""Shared fixtures for bangalore_intelligence tests."""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if "streamlit" not in sys.modules:
    try:
        import streamlit  # noqa: F401
    except ModuleNotFoundError:
        st = types.ModuleType("streamlit")

        class _CacheWrapper:
            def __init__(self, fn):
                self.fn = fn

            def __call__(self, *args, **kwargs):
                return self.fn(*args, **kwargs)

            def clear(self):
                return None

        def cache_data(**_kwargs):
            def deco(fn):
                return _CacheWrapper(fn)

            return deco

        st.cache_data = cache_data
        st.session_state = {}
        st.cache_resource = cache_data
        st.error = lambda *args, **kwargs: None
        st.warning = lambda *args, **kwargs: None
        st.caption = lambda *args, **kwargs: None
        st.info = lambda *args, **kwargs: None
        st.stop = lambda: None
        sys.modules["streamlit"] = st


@pytest.fixture
def sample_traffic_df() -> pd.DataFrame:
    from data_layer.bootstrap_data import generate_traffic_raw
    from data_layer.cleaners import clean_traffic

    return clean_traffic(generate_traffic_raw(n_rows=120))


@pytest.fixture
def sample_aqi_df() -> pd.DataFrame:
    from data_layer.bootstrap_data import generate_aqi_raw
    from data_layer.cleaners import clean_aqi

    return clean_aqi(generate_aqi_raw(n_days=90))
