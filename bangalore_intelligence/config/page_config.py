"""Page metadata, tab labels, and dashboard routing configuration."""

DASHBOARD_OPTIONS = {
    "traffic": "Traffic Intelligence",
    "aqi": "Air Quality and Weather Analysis",
}

TRAFFIC_TABS = [
    {
        "index": 0,
        "label": "01 · Overview",
        "module": "p1_command_overview",
        "title": "System Status Overview",
        "subtitle": "P1 of 6 · Current network congestion, capacity pressure, and area ranking",
        "is_lab": False,
    },
    {
        "index": 1,
        "label": "02 · Time",
        "module": "p2_temporal_intelligence",
        "title": "Temporal Patterns",
        "subtitle": "P2 of 6 · Monthly and weekday congestion rhythms by area",
        "is_lab": False,
    },
    {
        "index": 2,
        "label": "03 · Areas",
        "module": "p3_spatial_operations",
        "title": "Road And Area Diagnostics",
        "subtitle": "P3 of 6 · Road and area stress compared on congestion and capacity",
        "is_lab": False,
    },
    {
        "index": 3,
        "label": "04 · Limits",
        "module": "p4_threshold_analytics",
        "title": "Speed And Service Thresholds",
        "subtitle": "P4 of 6 · Speed decline and service threshold boundaries",
        "is_lab": False,
    },
    {
        "index": 4,
        "label": "05 · Patterns",
        "module": "p5_hidden_patterns",
        "title": "Context And Distribution Patterns",
        "subtitle": "P5 of 6 · Congestion distributions across roads, weather, and incidents",
        "is_lab": False,
    },
    {
        "index": 5,
        "label": "06 · Lab ⚗",
        "module": "p6_advanced_lab",
        "title": "Analytical Workspace",
        "subtitle": "P6 of 6 · Dense multi-metric comparison workspace",
        "is_lab": True,
    },
]

AQI_TABS = [
    {
        "index": 0,
        "label": "01 · Burden",
        "module": "p1_crisis_overview",
        "title": "Air Quality Burden Overview",
        "subtitle": "P1 of 6 · PM2.5 burden, category mix, and persistence",
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
        "title": "Atmospheric Conditions",
        "subtitle": "P3 of 6 · Pressure and visibility conditions associated with PM2.5",
        "is_lab": False,
    },
    {
        "index": 3,
        "label": "04 · Weather",
        "module": "p4_weather_relationships",
        "title": "Weather Indicators",
        "subtitle": "P4 of 6 · Weather indicators compared with PM2.5",
        "is_lab": False,
    },
    {
        "index": 4,
        "label": "05 · Patterns",
        "module": "p5_hidden_patterns",
        "title": "Distribution and Variability",
        "subtitle": "P5 of 6 · Seasonal distributions and variability checks",
        "is_lab": False,
    },
    {
        "index": 5,
        "label": "06 · Lab ⚗",
        "module": "p6_advanced_lab",
        "title": "Analytical Workspace",
        "subtitle": "P6 of 6 · High-density weather and PM2.5 exploration",
        "is_lab": True,
    },
]
