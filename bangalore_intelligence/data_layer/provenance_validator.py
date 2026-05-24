"""Provenance registry and manifest validation utilities."""

from __future__ import annotations

from typing import Any

from data_layer.governance import (
    active_dataset_fingerprint,
    build_governed_manifest,
    provenance_summary,
    validate_manifest_current,
    write_governed_manifest,
)


def build_source_fingerprint_registry() -> dict[str, Any]:
    manifest = build_governed_manifest()
    return {
        dataset: {
            "active_fingerprint": active_dataset_fingerprint(dataset),
            "canonical_file_sha256": payload["canonical"]["file_sha256"],
            "processed_file_sha256": payload["processed"]["file_sha256"],
            "row_count": payload["processed"]["row_count"],
            "date_range": payload["processed"].get("date_range"),
        }
        for dataset, payload in manifest["datasets"].items()
    }


def validate_provenance_manifest() -> dict[str, Any]:
    return validate_manifest_current()


def refresh_provenance_manifest() -> dict[str, Any]:
    return write_governed_manifest()


def runtime_source_disclosure(dataset: str) -> dict[str, Any]:
    return provenance_summary(dataset)
