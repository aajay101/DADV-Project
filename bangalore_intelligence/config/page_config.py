"""Page metadata, tab labels, and dashboard routing configuration."""

DASHBOARD_OPTIONS = {
    "traffic": "Traffic Intelligence",
    "aqi": "AQI Environmental Intelligence",
}

TRAFFIC_TABS = [
    {
        "index": 0,
        "label": "01 · Overview",
        "module": "p1_command_overview",
        "title": "Command Overview",
        "subtitle": "P1 of 6 · System-wide congestion and capacity status",
        "is_lab": False,
    },
    {
        "index": 1,
        "label": "02 · Temporal",
        "module": "p2_temporal_intelligence",
        "title": "Temporal Intelligence",
        "subtitle": "P2 of 6 · When congestion patterns emerge across time",
        "is_lab": False,
    },
    {
        "index": 2,
        "label": "03 · Spatial",
        "module": "p3_spatial_operations",
        "title": "Spatial Operations",
        "subtitle": "P3 of 6 · Road-level and area-level operations",
        "is_lab": False,
    },
    {
        "index": 3,
        "label": "04 · Threshold",
        "module": "p4_threshold_analytics",
        "title": "Threshold Analytics",
        "subtitle": "P4 of 6 · Congestion threshold and failure boundaries",
        "is_lab": False,
    },
    {
        "index": 4,
        "label": "05 · Patterns",
        "module": "p5_hidden_patterns",
        "title": "Hidden Patterns",
        "subtitle": "P5 of 6 · Distributional and operational pattern analysis",
        "is_lab": False,
    },
    {
        "index": 5,
        "label": "06 · Lab ⚗",
        "module": "p6_advanced_lab",
        "title": "Advanced Analytics Laboratory",
        "subtitle": "P6 of 6 · High-density multi-variable analysis",
        "is_lab": True,
    },
]

AQI_TABS = [
    {
        "index": 0,
        "label": "01 · Crisis",
        "module": "p1_crisis_overview",
        "title": "Crisis Overview",
        "subtitle": "P1 of 6 · Chronic pollution burden and severity",
        "is_lab": False,
    },
    {
        "index": 1,
        "label": "02 · Calendar",
        "module": "p2_temporal_patterns",
        "title": "Temporal Patterns",
        "subtitle": "P2 of 6 · Calendar and monthly pollution rhythms",
        "is_lab": False,
    },
    {
        "index": 2,
        "label": "03 · Atmosphere",
        "module": "p3_atmospheric_intelligence",
        "title": "Atmospheric Intelligence",
        "subtitle": "P3 of 6 · Atmospheric conditions that trap pollution",
        "is_lab": False,
    },
    {
        "index": 3,
        "label": "04 · Weather",
        "module": "p4_weather_relationships",
        "title": "Weather Relationships",
        "subtitle": "P4 of 6 · Meteorological drivers of pollution",
        "is_lab": False,
    },
    {
        "index": 4,
        "label": "05 · Patterns",
        "module": "p5_hidden_patterns",
        "title": "Hidden Patterns",
        "subtitle": "P5 of 6 · Statistical structure of variability",
        "is_lab": False,
    },
    {
        "index": 5,
        "label": "06 · Lab ⚗",
        "module": "p6_advanced_lab",
        "title": "Advanced Analytics Laboratory",
        "subtitle": "P6 of 6 · Full meteorological co-factor analysis",
        "is_lab": True,
    },
]
