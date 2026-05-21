"""Dataset paths, column registry, and schema constants."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DATA_AGG_DIR = PROJECT_ROOT / "data" / "aggregations"

TRAFFIC_RAW_PATH = DATA_RAW_DIR / "traffic_raw.csv"
AQI_RAW_PATH = DATA_RAW_DIR / "aqi_raw.csv"
TRAFFIC_CLEAN_PATH = DATA_PROCESSED_DIR / "traffic_clean.parquet"
AQI_CLEAN_PATH = DATA_PROCESSED_DIR / "aqi_clean.parquet"

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
