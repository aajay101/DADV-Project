"""
Traffic duplicate-key governance — import boundary only.

When multiple source rows share (Date, Area, Road) with differing metrics, the source
lacks intraday timestamps. Canonical policy aggregates to one daily row per key before
raw duplicate validation runs.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from config.data_config import (
    COL_CAPACITY,
    COL_CONGESTION,
    COL_PT_USAGE,
    COL_ROADWORK,
    COL_SIGNAL,
    COL_SPEED,
    COL_TRAFFIC_VOL,
    TRAFFIC_DUPLICATE_AGG_MAX_COLUMNS,
    TRAFFIC_DUPLICATE_AGG_MEAN_COLUMNS,
    TRAFFIC_DUPLICATE_AGG_MODE_COLUMNS,
    TRAFFIC_DUPLICATE_GOVERNANCE_POLICY,
    TRAFFIC_DUPLICATE_KEY,
)

_ROADWORK_SEVERITY = {"None": 0, "Minor": 1, "Major": 2}


def _mode_or_first(series: pd.Series) -> Any:
    cleaned = series.dropna()
    if cleaned.empty:
        return np.nan
    modes = cleaned.mode()
    return modes.iloc[0] if not modes.empty else cleaned.iloc[0]


def _roadwork_mode(series: pd.Series) -> Any:
    cleaned = series.dropna().astype(str).str.strip()
    if cleaned.empty:
        return np.nan
    modes = cleaned.mode()
    if len(modes) == 1:
        return modes.iloc[0]
    ranked = sorted(
        cleaned.unique(),
        key=lambda v: _ROADWORK_SEVERITY.get(v, -1),
        reverse=True,
    )
    return ranked[0]


def _build_aggregation_spec(columns: list[str]) -> dict[str, Any]:
    spec: dict[str, Any] = {}
    for col in TRAFFIC_DUPLICATE_AGG_MEAN_COLUMNS:
        if col in columns:
            spec[col] = "mean"
    for col in TRAFFIC_DUPLICATE_AGG_MAX_COLUMNS:
        if col in columns:
            spec[col] = "max"
    for col in TRAFFIC_DUPLICATE_AGG_MODE_COLUMNS:
        if col not in columns:
            continue
        if col == COL_ROADWORK:
            spec[col] = _roadwork_mode
        else:
            spec[col] = _mode_or_first
    return spec


def govern_traffic_duplicate_keys(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Enforce canonical daily uniqueness for traffic raw keys.

    1. Drop exact duplicate rows (all columns identical).
    2. Aggregate remaining partial duplicate groups to one row per (Date, Area, Road).
    """
    key = list(TRAFFIC_DUPLICATE_KEY)
    stats: dict[str, Any] = {
        "policy": TRAFFIC_DUPLICATE_GOVERNANCE_POLICY,
        "duplicate_key_columns": key,
        "rows_before": int(len(df)),
        "duplicate_key_rows_before": 0,
        "duplicate_groups_before": 0,
        "exact_duplicates_removed": 0,
        "partial_groups_aggregated": 0,
        "rows_collapsed_by_aggregation": 0,
        "rows_after": 0,
    }

    if df.empty or not all(c in df.columns for c in key):
        stats["rows_after"] = int(len(df))
        return df.copy(), stats

    work = df.copy()
    dup_mask = work.duplicated(subset=key, keep=False)
    stats["duplicate_key_rows_before"] = int(dup_mask.sum())
    stats["duplicate_groups_before"] = (
        int(work.loc[dup_mask].groupby(key, dropna=False).ngroups) if dup_mask.any() else 0
    )

    before_exact = len(work)
    work = work.drop_duplicates(keep="first")
    stats["exact_duplicates_removed"] = before_exact - len(work)

    dup_mask = work.duplicated(subset=key, keep=False)
    if not dup_mask.any():
        stats["rows_after"] = int(len(work))
        return work.reset_index(drop=True), stats

    unique = work.loc[~dup_mask].copy()
    multi = work.loc[dup_mask].copy()
    stats["partial_groups_aggregated"] = int(multi.groupby(key, dropna=False).ngroups)
    stats["rows_collapsed_by_aggregation"] = int(len(multi) - stats["partial_groups_aggregated"])

    agg_spec = _build_aggregation_spec(list(multi.columns))
    if not agg_spec:
        raise ValueError("No aggregation columns resolved for traffic duplicate groups")

    aggregated = multi.groupby(key, dropna=False).agg(agg_spec).reset_index()

    for col in TRAFFIC_DUPLICATE_AGG_MEAN_COLUMNS:
        if col in aggregated.columns:
            if col in (COL_CONGESTION, COL_SPEED, COL_CAPACITY, COL_SIGNAL, COL_PT_USAGE):
                aggregated[col] = aggregated[col].round(1)
            elif col == COL_TRAFFIC_VOL:
                aggregated[col] = aggregated[col].round(0)

    out = pd.concat([unique, aggregated], ignore_index=True)
    out = out.sort_values(key).reset_index(drop=True)
    stats["rows_after"] = int(len(out))
    return out, stats
