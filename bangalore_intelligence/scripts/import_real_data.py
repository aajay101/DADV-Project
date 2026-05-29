#!/usr/bin/env python3
"""
Real-data import CLI — dry-run (default) or governed --apply writes.

See MD-File/REAL_DATA_OPERATION.md for operational workflow and loader tiers.

Usage (from bangalore_intelligence/):
  python scripts/import_real_data.py
  python scripts/import_real_data.py --dry-run
  python scripts/import_real_data.py --apply
  python scripts/import_real_data.py --apply --traffic-source data/raw/traffic_raw.csv --aqi-source data/raw/aqi_raw.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure package root is importable when invoked as a script
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from config.data_config import AQI_RAW_PATH, DATA_SCHEMA_VERSION, TRAFFIC_RAW_PATH  # noqa: E402
from data_layer.real_data_import import (  # noqa: E402
    format_apply_summary,
    format_dry_run_summary,
    run_dry_run_import,
    run_real_import,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bangalore Intelligence real-data import")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Normalize and validate in memory without writing files (default).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Run governed import: canonical raw + processed parquet after validation.",
    )
    parser.add_argument(
        "--traffic-source",
        type=Path,
        default=TRAFFIC_RAW_PATH,
        help="Path to traffic source CSV",
    )
    parser.add_argument(
        "--aqi-source",
        type=Path,
        default=AQI_RAW_PATH,
        help="Path to AQI source CSV",
    )
    args = parser.parse_args(argv)

    if args.apply and args.dry_run:
        print("Use either --dry-run or --apply, not both.", file=sys.stderr)
        return 2

    if not args.traffic_source.exists():
        print(f"Traffic source not found: {args.traffic_source}", file=sys.stderr)
        return 1
    if not args.aqi_source.exists():
        print(f"AQI source not found: {args.aqi_source}", file=sys.stderr)
        return 1

    if args.apply:
        result = run_real_import(args.traffic_source, args.aqi_source)
        print(format_apply_summary(result))
        print(f"\nSchema version constant: {DATA_SCHEMA_VERSION}")
        if not result.success and result.profile.error and "already in progress" in result.profile.error:
            return 4
        return 0 if result.success else 3

    result = run_dry_run_import(args.traffic_source, args.aqi_source)
    print(format_dry_run_summary(result))
    print(f"\nSchema version constant: {DATA_SCHEMA_VERSION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
