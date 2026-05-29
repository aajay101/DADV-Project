"""Dataset paths, column registry, and schema constants."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DATA_AGG_DIR = PROJECT_ROOT / "data" / "aggregations"
DATA_METADATA_DIR = PROJECT_ROOT / "data" / "metadata"
DATA_ARCHIVE_DIR = PROJECT_ROOT / "data" / "archive"
IMPORT_PROFILE_PATH = DATA_METADATA_DIR / "import_profile.json"
IMPORT_HISTORY_DIR = DATA_METADATA_DIR / "import_history"
IMPORT_LOCK_PATH = DATA_METADATA_DIR / ".import.lock"

# Phase 4 — operational governance
IMPORT_LOCK_STALE_SECONDS = 3600
ARCHIVE_SNAPSHOT_RETENTION = 10
TRAFFIC_ARCHIVE_PREFIX = "traffic_raw_"
AQI_ARCHIVE_PREFIX = "aqi_raw_"

DATA_SCHEMA_VERSION = "1.0.0"
SUPPORTED_SCHEMA_VERSIONS = frozenset({DATA_SCHEMA_VERSION})

# Bootstrap / legacy CSV paths (unchanged for current loaders)
TRAFFIC_RAW_PATH = DATA_RAW_DIR / "traffic_raw.csv"
AQI_RAW_PATH = DATA_RAW_DIR / "aqi_raw.csv"

# Governed canonical raw parquet targets (Phase 1+ ingestion; not used by loaders until later phases)
TRAFFIC_CANONICAL_RAW_PARQUET = DATA_RAW_DIR / "traffic_canonical_raw.parquet"
AQI_CANONICAL_RAW_PARQUET = DATA_RAW_DIR / "aqi_canonical_raw.parquet"

TRAFFIC_CLEAN_PATH = DATA_PROCESSED_DIR / "traffic_clean.parquet"
AQI_CLEAN_PATH = DATA_PROCESSED_DIR / "aqi_clean.parquet"

# Import staging (Phase 3) — temp artifacts; loaders must not read these directly
DATA_TEMP_DIR = PROJECT_ROOT / "data" / ".import_temp"
TRAFFIC_CANONICAL_RAW_TMP = DATA_TEMP_DIR / "traffic_canonical_raw.tmp.parquet"
AQI_CANONICAL_RAW_TMP = DATA_TEMP_DIR / "aqi_canonical_raw.tmp.parquet"
TRAFFIC_CLEAN_TMP = DATA_TEMP_DIR / "traffic_clean.tmp.parquet"
AQI_CLEAN_TMP = DATA_TEMP_DIR / "aqi_clean.tmp.parquet"
TRAFFIC_CLEAN_BACKUP = DATA_PROCESSED_DIR / "traffic_clean.parquet.bak"
AQI_CLEAN_BACKUP = DATA_PROCESSED_DIR / "aqi_clean.parquet.bak"

MIN_PROCESSED_TRAFFIC_ROWS = 10
MIN_PROCESSED_AQI_ROWS = 30

# Phase 0 — governed runtime traffic contract (repository canonical truth).
# Derived from data/raw/traffic_raw.csv after import normalization + duplicate governance.
# Dashboard refactor phases must use these values, not external guide assumptions.
TRAFFIC_RUNTIME_SOURCE_CSV_ROWS = 8936
TRAFFIC_RUNTIME_CANONICAL_ROWS = 8579
TRAFFIC_RUNTIME_PROCESSED_ROWS = 8579
TRAFFIC_RUNTIME_DATE_MIN = "2022-01-01"
TRAFFIC_RUNTIME_DATE_MAX = "2024-08-17"
TRAFFIC_RUNTIME_AREAS = frozenset(
    {
        "Brigade Road",
        "Electronic City",
        "Indiranagar",
        "Koramangala",
        "MG Road",
        "Marathahalli",
        "Silk Board",
        "Whitefield",
    }
)
TRAFFIC_RUNTIME_ROAD_COUNT = 16
TRAFFIC_RUNTIME_ROAD_PREFIX = "Road_"
TRAFFIC_RUNTIME_MEAN_CONGESTION = 70.96
TRAFFIC_RUNTIME_MEAN_SPEED = 20.23
TRAFFIC_RUNTIME_SPEED_MIN = 8.0
TRAFFIC_RUNTIME_SPEED_MAX = 40.8
TRAFFIC_RUNTIME_VOLUME_MIN = 501.0
TRAFFIC_RUNTIME_VOLUME_MAX = 4996.0
TRAFFIC_RUNTIME_MEAN_CAPACITY = 75.96
TRAFFIC_RUNTIME_INCIDENT_SUM_PROCESSED = 7452
TRAFFIC_RUNTIME_DUPLICATE_ROWS_COLLAPSED = 357
TRAFFIC_RUNTIME_DUPLICATE_GROUPS_AGGREGATED = 339
TRAFFIC_RUNTIME_KPI_TOLERANCE = 0.2

# Optional real-source fields preserved in canonical raw traffic (not derived in import layer)
COL_TRAVEL_TIME_INDEX = "Travel_Time_Index"
COL_ENVIRONMENTAL_IMPACT_SOURCE = "Environmental_Impact"
COL_PARKING_USAGE = "Parking_Usage"

# Traffic columns
COL_DATE = "Date"
COL_AREA = "Area Name"
COL_ROAD = "Road Name"
COL_CONGESTION = "Congestion_Level"
COL_SPEED = "Average_Speed"
COL_INCIDENTS = "Incident_Reports"
COL_CAPACITY = "Road_Capacity_Utilization"
COL_PEDESTRIAN = "Pedestrian_and_Cyclist_Count"
COL_PT_USAGE = "Public_Transport_Usage"
COL_SIGNAL = "Traffic_Signal_Compliance"
COL_TRAFFIC_VOL = "Traffic_Volume"
COL_WEATHER = "Weather_Condition"
COL_ROADWORK = "Roadwork_Activity"

TRAFFIC_AREAS = [
    "Indiranagar",
    "Koramangala",
    "Whitefield",
    "Electronic City",
    "Marathahalli",
    "Silk Board",
    "MG Road",
    "Brigade Road",
]

# Bangalore area centroids for spatial charts (lat, lon)
TRAFFIC_AREA_COORDS: dict[str, tuple[float, float]] = {
    "Indiranagar": (12.9784, 77.6408),
    "Koramangala": (12.9352, 77.6245),
    "Whitefield": (12.9698, 77.7500),
    "Electronic City": (12.8456, 77.6603),
    "Marathahalli": (12.9591, 77.6974),
    "Silk Board": (12.9172, 77.6221),
    "MG Road": (12.9750, 77.6063),
    "Brigade Road": (12.9716, 77.6070),
}

CONGESTION_STATES = ["Low", "Moderate", "Elevated", "Critical"]
CONGESTION_STATE_BOUNDS = [0, 60, 75, 90, 100]

# AQI columns
COL_PM25 = "PM_2_5"
COL_T = "T"
COL_TM = "Tm"
COL_TM_MAX = "TM"
COL_SLP = "SLP"
COL_H = "H"
COL_VV = "VV"
COL_V = "V"
COL_VM = "VM"
COL_AQI_CATEGORY = "aqi_category"
COL_SEASON = "season"

# Raw ingestion governance (Phase 2+)
RAW_DUPLICATE_TOLERANCE = 0
UNKNOWN_CATEGORY_WARNING_RATIO = 0.01
UNKNOWN_CATEGORY_ERROR_RATIO = 0.05
INCIDENT_NULL_FILL_MAX_RATIO = 0.02

TRAFFIC_RAW_REQUIRED_COLUMNS = [
    COL_DATE,
    COL_AREA,
    COL_ROAD,
    COL_CONGESTION,
    COL_SPEED,
    COL_INCIDENTS,
    COL_CAPACITY,
    COL_PEDESTRIAN,
    COL_PT_USAGE,
    COL_SIGNAL,
    COL_TRAFFIC_VOL,
    COL_WEATHER,
    COL_ROADWORK,
]

AQI_RAW_REQUIRED_COLUMNS = [
    COL_DATE,
    COL_PM25,
    COL_T,
    COL_TM,
    COL_TM_MAX,
    COL_SLP,
    COL_H,
    COL_VV,
    COL_V,
    COL_VM,
]

TRAFFIC_DUPLICATE_KEY = [COL_DATE, COL_AREA, COL_ROAD]
AQI_DUPLICATE_KEY = [COL_DATE]

# Traffic duplicate governance (Phase 2+): multiple rows per daily road key are aggregated
# before raw validation — source has no intraday timestamp but repeated measurements per day.
TRAFFIC_DUPLICATE_GOVERNANCE_POLICY = "aggregate_daily_canonical"
TRAFFIC_DUPLICATE_AGG_MEAN_COLUMNS = [
    COL_CONGESTION,
    COL_SPEED,
    COL_CAPACITY,
    COL_PEDESTRIAN,
    COL_PT_USAGE,
    COL_SIGNAL,
    COL_TRAFFIC_VOL,
    COL_TRAVEL_TIME_INDEX,
    COL_ENVIRONMENTAL_IMPACT_SOURCE,
    COL_PARKING_USAGE,
]
TRAFFIC_DUPLICATE_AGG_MAX_COLUMNS = [COL_INCIDENTS]
TRAFFIC_DUPLICATE_AGG_MODE_COLUMNS = [COL_WEATHER, COL_ROADWORK]

WEATHER_CONDITION_ENUM = ("Clear", "Rain", "Cloudy", "Haze")
ROADWORK_ACTIVITY_ENUM = ("None", "Minor", "Major")

TRAFFIC_ROADS = [f"{TRAFFIC_RUNTIME_ROAD_PREFIX}{i}" for i in range(1, TRAFFIC_RUNTIME_ROAD_COUNT + 1)]
TRAFFIC_WEATHER_OPTIONS = list(WEATHER_CONDITION_ENUM)
TRAFFIC_ROADWORK_FILTER_OPTIONS = ("Both", *ROADWORK_ACTIVITY_ENUM)

WEATHER_CATEGORY_ALIASES: dict[str, str] = {
    "clear": "Clear",
    "rain": "Rain",
    "cloudy": "Cloudy",
    "haze": "Haze",
    "fog": "Haze",
}

ROADWORK_CATEGORY_ALIASES: dict[str, str] = {
    "none": "None",
    "minor": "Minor",
    "major": "Major",
    "no": "None",
}

TRAFFIC_RAW_CATEGORY_COLUMNS: dict[str, tuple[str, ...]] = {
    COL_WEATHER: WEATHER_CONDITION_ENUM,
    COL_ROADWORK: ROADWORK_ACTIVITY_ENUM,
}

TRAFFIC_SEMANTIC_RANGES: dict[str, tuple[float, float]] = {
    COL_CONGESTION: (0.0, 100.0),
    COL_SPEED: (0.0, 120.0),
    COL_INCIDENTS: (0.0, 50.0),
    COL_CAPACITY: (0.0, 100.0),
    COL_PEDESTRIAN: (0.0, 10_000.0),
    COL_PT_USAGE: (0.0, 100.0),
    COL_SIGNAL: (0.0, 100.0),
    COL_TRAFFIC_VOL: (0.0, 50_000.0),
}

AQI_SEMANTIC_RANGES: dict[str, tuple[float, float]] = {
    COL_PM25: (0.0, 600.0),
    COL_T: (-5.0, 50.0),
    COL_TM: (-10.0, 45.0),
    COL_TM_MAX: (-5.0, 55.0),
    COL_SLP: (950.0, 1040.0),
    COL_H: (0.0, 100.0),
    COL_VV: (0.0, 20.0),
    COL_V: (0.0, 30.0),
    COL_VM: (0.0, 60.0),
}

# Source header aliases → canonical names (real CSV intake)
TRAFFIC_SOURCE_COLUMN_ALIASES: dict[str, str] = {
    "date": COL_DATE,
    "area name": COL_AREA,
    "road name": COL_ROAD,
    "road/intersection name": COL_ROAD,
    "road intersection name": COL_ROAD,
    "congestion_level": COL_CONGESTION,
    "congestion level": COL_CONGESTION,
    "average_speed": COL_SPEED,
    "average speed": COL_SPEED,
    "incident_reports": COL_INCIDENTS,
    "incident reports": COL_INCIDENTS,
    "road_capacity_utilization": COL_CAPACITY,
    "road capacity utilization": COL_CAPACITY,
    "pedestrian_and_cyclist_count": COL_PEDESTRIAN,
    "pedestrian and cyclist count": COL_PEDESTRIAN,
    "public_transport_usage": COL_PT_USAGE,
    "public transport usage": COL_PT_USAGE,
    "traffic_signal_compliance": COL_SIGNAL,
    "traffic signal compliance": COL_SIGNAL,
    "traffic_volume": COL_TRAFFIC_VOL,
    "traffic volume": COL_TRAFFIC_VOL,
    "weather_condition": COL_WEATHER,
    "weather condition": COL_WEATHER,
    "weather conditions": COL_WEATHER,
    "roadwork_activity": COL_ROADWORK,
    "roadwork activity": COL_ROADWORK,
    "roadwork and construction activity": COL_ROADWORK,
    "travel time index": COL_TRAVEL_TIME_INDEX,
    "travel_time_index": COL_TRAVEL_TIME_INDEX,
    "environmental impact": COL_ENVIRONMENTAL_IMPACT_SOURCE,
    "environmental_impact": COL_ENVIRONMENTAL_IMPACT_SOURCE,
    "parking usage": COL_PARKING_USAGE,
    "parking_usage": COL_PARKING_USAGE,
}

AQI_PM25_SOURCE_ALIASES = ("PM 2.5", "PM2.5", "PM2.5 ", "PM_2_5", "pm 2.5", "pm2.5")

AQI_SOURCE_COLUMN_ALIASES: dict[str, str] = {
    "pm 2.5": COL_PM25,
    "pm2.5": COL_PM25,
    "pm_2_5": COL_PM25,
    "date": COL_DATE,
    "t": COL_T,
    "tm": COL_TM,
    "tm_max": COL_TM_MAX,
    "tm max": COL_TM_MAX,
    "tm (min)": COL_TM,
    "slp": COL_SLP,
    "h": COL_H,
    "humidity": COL_H,
    "vv": COL_VV,
    "visibility": COL_VV,
    "v": COL_V,
    "wind": COL_V,
    "vm": COL_VM,
    "gust": COL_VM,
}

TRAFFIC_RAW_NUMERIC_COLUMNS = [
    COL_CONGESTION,
    COL_SPEED,
    COL_INCIDENTS,
    COL_CAPACITY,
    COL_PEDESTRIAN,
    COL_PT_USAGE,
    COL_SIGNAL,
    COL_TRAFFIC_VOL,
    COL_TRAVEL_TIME_INDEX,
    COL_ENVIRONMENTAL_IMPACT_SOURCE,
    COL_PARKING_USAGE,
]

AQI_RAW_NUMERIC_COLUMNS = [
    COL_PM25,
    COL_T,
    COL_TM,
    COL_TM_MAX,
    COL_SLP,
    COL_H,
    COL_VV,
    COL_V,
    COL_VM,
]

AQI_CATEGORIES = [
    "Good",
    "Satisfactory",
    "Moderate",
    "Poor",
    "Very Poor",
    "Severe",
]

TRAFFIC_DERIVED_COLUMNS = [
    "day_of_week",
    "month_year",
    "at_max_capacity",
    "environmental_impact",
]

AQI_DERIVED_COLUMNS = [
    "aqi_category",
    "season",
    "temp_spread",
    "gust_ratio",
    "slp_band",
    "vv_band",
    "wind_band",
    "rolling_7d_pm25",
    "year",
    "week",
]

# Operational thresholds
TRAFFIC_CONGESTION_CRITICAL = 90
TRAFFIC_CONGESTION_WARNING = 60
TRAFFIC_CAPACITY_CRITICAL_PCT = 50
TRAFFIC_INCIDENTS_CRITICAL = 500
TRAFFIC_SPEED_WARNING = 30
TRAFFIC_SPEED_CRITICAL = 20

AQI_PM25_WHO_ANNUAL = 5
AQI_PM25_VERY_POOR = 120
AQI_PM25_SEVERE = 250

# Session / cache governance
STALE_THRESHOLD_SECONDS = 3600
LONG_SESSION_THRESHOLD_SECONDS = 90 * 60
STATIC_DATASET_MODE = True

# Real-data loader policy (Phase 0 governance lockdown)
# Production runtime is governed-only: canonical raw parquet is the source of truth,
# processed parquet is the dashboard-serving artifact, and legacy CSV is import input only.
RUNTIME_ENV = "prod"
ALLOW_SYNTHETIC_BOOTSTRAP = False
ALLOW_DEV_SYNTHETIC_BOOTSTRAP = False
REQUIRE_GOVERNED_DATA = True
GOVERNED_MANIFEST_FILENAME = "governed_dataset_manifest.json"
