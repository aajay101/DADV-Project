"""Aggregation parity checks for governed dashboard outputs."""

from __future__ import annotations

from typing import Any

import pandas as pd

from config.data_config import COL_CAPACITY, COL_CONGESTION


def traffic_command_kpi_truth(df: pd.DataFrame) -> dict[str, float]:
    return {
        "system_congestion": float(df[COL_CONGESTION].mean()),
        "capacity_saturation_rate": float((df[COL_CAPACITY] >= 99.5).mean() * 100),
    }


def validate_t01_config_parity(df: pd.DataFrame, chart_config: dict[str, Any]) -> dict[str, Any]:
    truth = traffic_command_kpi_truth(df)
    diffs = {
        key: abs(float(chart_config.get(key, float("nan"))) - expected)
        for key, expected in truth.items()
    }
    ok = all(diff <= 1e-9 for diff in diffs.values())
    return {"ok": ok, "expected": truth, "differences": diffs}


def validate_sampling_metadata(data: pd.DataFrame) -> dict[str, Any]:
    sampling = getattr(data, "attrs", {}).get("sampling", {})
    if not sampling:
        return {"ok": True, "sampled": False}
    required = {"sampled", "method", "sample_size", "source_rows"}
    return {
        "ok": required.issubset(sampling),
        "sampled": bool(sampling.get("sampled")),
        "metadata": sampling,
    }
