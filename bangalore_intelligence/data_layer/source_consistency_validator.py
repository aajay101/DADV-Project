"""Source consistency checks for governed parquet artifacts."""

from __future__ import annotations

from typing import Any

from data_layer.governance import validate_processed_against_canonical


def validate_source_consistency(dataset: str) -> dict[str, Any]:
    """Validate canonical raw -> processed parity for one dataset."""
    return validate_processed_against_canonical(dataset)


def validate_all_source_consistency() -> dict[str, dict[str, Any]]:
    return {
        "traffic": validate_source_consistency("traffic"),
        "aqi": validate_source_consistency("aqi"),
    }
