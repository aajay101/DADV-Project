"""Generate synthetic CSV bootstrap data when raw files are absent (dev/CI fallback only).

Dashboards prefer governed parquet from `import_real_data.py --apply`. See MD-File/REAL_DATA_OPERATION.md.
"""

from datetime import datetime

import numpy as np
import pandas as pd

from config.data_config import (
    ALLOW_DEV_SYNTHETIC_BOOTSTRAP,
    AQI_RAW_PATH,
    COL_AREA,
    COL_CAPACITY,
    COL_CONGESTION,
    COL_DATE,
    COL_H,
    COL_INCIDENTS,
    COL_PEDESTRIAN,
    COL_PM25,
    COL_PT_USAGE,
    COL_ROAD,
    COL_ROADWORK,
    COL_SIGNAL,
    COL_SLP,
    COL_SPEED,
    COL_T,
    COL_TM,
    COL_TM_MAX,
    COL_TRAFFIC_VOL,
    COL_V,
    COL_VM,
    COL_VV,
    COL_WEATHER,
    TRAFFIC_AREAS,
    TRAFFIC_RAW_PATH,
)
from data_layer.governance import SyntheticDataDetectedError, is_production_runtime


def _pm25_to_category(pm25: float) -> str:
    if pm25 <= 30:
        return "Good"
    if pm25 <= 60:
        return "Satisfactory"
    if pm25 <= 90:
        return "Moderate"
    if pm25 <= 120:
        return "Poor"
    if pm25 <= 250:
        return "Very Poor"
    return "Severe"


def generate_traffic_raw(n_rows: int = 8936) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    roads = [f"Road_{i+1}" for i in range(16)]
    start = datetime(2022, 1, 1)
    dates = pd.date_range(start, periods=32 * 30, freq="D")
    records = []
    for _ in range(n_rows):
        area = rng.choice(TRAFFIC_AREAS)
        road = rng.choice(roads)
        date = rng.choice(dates)
        base_cong = 70 + (5 if area == "Koramangala" else 0) + (3 if area == "Electronic City" else 0)
        congestion = float(np.clip(rng.normal(base_cong, 12), 35, 99))
        capacity = float(np.clip(rng.normal(congestion + 5, 8), 50, 100))
        lam = max(0.1, 0.8 + (congestion - 70) / 25)
        incidents = int(np.clip(rng.poisson(lam), 0, 6))
        speed = float(np.clip(45 - congestion * 0.35 + rng.normal(0, 4), 8, 55))
        records.append(
            {
                COL_DATE: date,
                COL_AREA: area,
                COL_ROAD: road,
                COL_CONGESTION: round(congestion, 1),
                COL_SPEED: round(speed, 1),
                COL_INCIDENTS: incidents,
                COL_CAPACITY: round(capacity, 1),
                COL_PEDESTRIAN: int(rng.integers(50, 250)),
                COL_PT_USAGE: round(float(rng.uniform(30, 75)), 1),
                COL_SIGNAL: round(float(rng.uniform(60, 95)), 1),
                COL_TRAFFIC_VOL: int(rng.integers(500, 5000)),
                COL_WEATHER: rng.choice(["Clear", "Rain", "Cloudy", "Haze"]),
                COL_ROADWORK: rng.choice(["None", "Minor", "Major"]),
            }
        )
    return pd.DataFrame(records)


def generate_aqi_raw(n_days: int = 1095) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    start = datetime(2021, 1, 1)
    dates = pd.date_range(start, periods=n_days, freq="D")
    records = []
    for date in dates:
        month = date.month
        seasonal = 40 + (35 if month in (11, 12, 1, 2) else 0) - (15 if month in (6, 7, 8, 9) else 0)
        pm25 = float(np.clip(rng.normal(seasonal, 25), 8, 420))
        tm = float(np.clip(rng.normal(18 + (2 if month <= 3 else -2), 4), 8, 32))
        tmax = tm + float(rng.uniform(4, 12))
        records.append(
            {
                COL_DATE: date,
                COL_PM25: round(pm25, 1),
                COL_T: round(tmax, 1),
                COL_TM: round(tm, 1),
                COL_TM_MAX: round(tmax, 1),
                COL_SLP: round(float(rng.normal(1010, 8)), 1),
                COL_H: round(float(rng.uniform(35, 95)), 1),
                COL_VV: round(float(np.clip(rng.normal(2.5, 1.5), 0.2, 8)), 2),
                COL_V: round(float(np.clip(rng.normal(2.0, 1.2), 0.1, 12)), 2),
                COL_VM: round(float(np.clip(rng.normal(4.0, 2.0), 0.5, 20)), 2),
            }
        )
    return pd.DataFrame(records)


def ensure_raw_datasets() -> None:
    """Write raw CSV files if explicitly allowed for development bootstrap."""
    if is_production_runtime() or not ALLOW_DEV_SYNTHETIC_BOOTSTRAP:
        raise SyntheticDataDetectedError(
            "Synthetic raw dataset bootstrap is disabled by Phase 0 governance. "
            "Use governed canonical parquet produced by scripts/import_real_data.py --apply."
        )
    TRAFFIC_RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not TRAFFIC_RAW_PATH.exists() or TRAFFIC_RAW_PATH.stat().st_size < 10:
        generate_traffic_raw().to_csv(TRAFFIC_RAW_PATH, index=False)
    if not AQI_RAW_PATH.exists() or AQI_RAW_PATH.stat().st_size < 10:
        generate_aqi_raw().to_csv(AQI_RAW_PATH, index=False)


if __name__ == "__main__":
    ensure_raw_datasets()
    print("Bootstrap complete")
