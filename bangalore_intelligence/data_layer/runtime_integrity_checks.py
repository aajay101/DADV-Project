"""Runtime governance checks for dashboard startup and diagnostics."""

from __future__ import annotations

from typing import Any

from data_layer.governance import (
    assert_synthetic_runtime_disabled,
    run_startup_governance_checks,
)
from data_layer.provenance_validator import build_source_fingerprint_registry
from data_layer.source_consistency_validator import validate_all_source_consistency


def run_runtime_integrity_checks() -> dict[str, Any]:
    """Run all non-visual integrity checks used by production startup/tests."""
    assert_synthetic_runtime_disabled()
    manifest = run_startup_governance_checks()
    return {
        "manifest": manifest,
        "source_consistency": validate_all_source_consistency(),
        "fingerprint_registry": build_source_fingerprint_registry(),
        "status": "PASS",
    }
