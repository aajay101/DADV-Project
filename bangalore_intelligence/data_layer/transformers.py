"""Shared pure transform helpers — no Streamlit imports."""

from __future__ import annotations

import pandas as pd


def bucket_month(df: pd.DataFrame, date_col: str, out_col: str = "month") -> pd.DataFrame:
    """Add a period-month bucket column from a datetime column."""
    if df.empty or date_col not in df.columns:
        return df.copy()
    out = df.copy()
    out[out_col] = pd.to_datetime(out[date_col], errors="coerce").dt.to_period("M").astype(str)
    return out


def numeric_bin(
    series: pd.Series,
    bins: int = 5,
    labels: list[str] | None = None,
) -> pd.Series:
    """Bin numeric values into categorical labels."""
    if series.empty:
        return series.copy()
    try:
        result = pd.qcut(series.dropna(), q=bins, duplicates="drop")
    except ValueError:
        result = pd.cut(series.dropna(), bins=bins, duplicates="drop")
    if labels:
        cats = result.cat.categories
        mapping = {cats[i]: labels[i] for i in range(min(len(cats), len(labels)))}
        result = result.cat.rename_categories(mapping)
    return result.reindex(series.index)


def grouped_rolling_mean(
    df: pd.DataFrame,
    group_cols: list[str],
    value_col: str,
    window: int,
    date_col: str,
    out_col: str | None = None,
) -> pd.DataFrame:
    """Compute per-group rolling mean ordered by date."""
    out_name = out_col or f"{value_col}_roll_{window}"
    if df.empty or value_col not in df.columns or date_col not in df.columns:
        return df.copy()
    missing_groups = [c for c in group_cols if c not in df.columns]
    if missing_groups:
        return df.copy()
    out = df.sort_values(date_col).copy()
    out[out_name] = (
        out.groupby(group_cols, dropna=False)[value_col]
        .transform(lambda s: s.rolling(window, min_periods=1).mean())
    )
    return out
