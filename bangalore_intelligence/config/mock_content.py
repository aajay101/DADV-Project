"""Placeholder analytical mock content — presentation only, no real data."""

TRAFFIC_MOCK = {
    "p1_command_overview": {
        "severity_badge": "CRITICAL",
        "primary_kpis": [
            {"label": "System Congestion Index", "value": "87.3", "severity": "critical", "delta": "▲ 4.2 pts", "delta_positive": False, "gauge_percent": 87},
            {"label": "Capacity Saturation", "value": "64%", "severity": "warning", "gauge_percent": 64},
            {"label": "Active Incidents", "value": "1,247", "severity": "critical"},
            {"label": "Average Speed", "value": "26.4 km/h", "severity": "warning"},
        ],
        "secondary_kpis": [
            {"label": "Pedestrian Exposure", "value": "134 avg", "severity": "neutral"},
            {"label": "Public Transport Usage", "value": "52.3%", "severity": "neutral"},
            {"label": "Signal Compliance", "value": "78.1%", "severity": "neutral"},
            {"label": "Environmental Impact", "value": "128.4", "severity": "warning"},
        ],
        "hero_chart": {"title": "T-01 · Saturation Command Scorecard", "subtitle": "Area-level operational stress matrix", "role": "hero"},
        "support_chart": {"title": "T-08 · First Incident Cliff", "subtitle": "Threshold step at 1→2 incidents", "role": "support"},
        "insight": "Chronic congestion persists across 8 urban areas. Capacity saturation exceeds 50% of monitored roads under current filter context.",
        "nav_tab": 1,
        "nav_title": "Temporal Intelligence",
        "nav_desc": "Examine 32-month congestion trends and weekly velocity patterns.",
    },
    "p2_temporal_intelligence": {
        "primary_kpis": [
            {"label": "Peak Month Congestion", "value": "94.1", "severity": "critical"},
            {"label": "Lowest Month", "value": "61.2", "severity": "safe"},
            {"label": "Trend Direction", "value": "▲ Rising", "severity": "warning", "delta": "Last 6 months", "delta_positive": False},
            {"label": "Volatility Index", "value": "18.4%", "severity": "neutral"},
        ],
        "hero_chart": {"title": "T-03 · Congestion Stream Graph", "subtitle": "32-month area-stacked temporal flow", "role": "hero"},
        "support_chart": {"title": "T-04 · Weekly Violin Distribution", "subtitle": "Day-of-week congestion spread", "role": "support"},
        "insight": "Temporal peaks cluster in Q4 windows. Weekend relief is marginal relative to weekday baseline congestion.",
        "nav_tab": 2,
        "nav_title": "Spatial Operations",
        "nav_desc": "Map congestion to roads and operational zones.",
    },
    "p3_spatial_operations": {
        "primary_kpis": [
            {"label": "Critical Overload Roads", "value": "6", "severity": "critical"},
            {"label": "Worst Area", "value": "Koramangala", "severity": "critical"},
            {"label": "Baseline Roads", "value": "4", "severity": "safe"},
            {"label": "Mean Road Congestion", "value": "82.7", "severity": "warning"},
        ],
        "hero_chart": {"title": "T-05 · Road Priority Quadrant", "subtitle": "Congestion × capacity bubble matrix", "role": "hero"},
        "support_chart": {"title": "T-06 · Environmental Burden Treemap", "subtitle": "Area × road impact hierarchy", "role": "support"},
        "insight": "Spatial overload concentrates in Koramangala and Electronic City corridors. Operational baseline roads remain statistically isolated.",
        "nav_tab": 3,
        "nav_title": "Threshold Analytics",
        "nav_desc": "Examine speed collapse and system failure boundaries.",
    },
    "p4_threshold_analytics": {
        "primary_kpis": [
            {"label": "Speed Collapse Threshold", "value": "~22 km/h", "severity": "warning"},
            {"label": "Congestion at Threshold", "value": "75+", "severity": "critical"},
            {"label": "PT Quartile Spread", "value": "Weak", "severity": "neutral"},
            {"label": "Incident Sensitivity", "value": "+21.5 pts", "severity": "critical"},
        ],
        "hero_chart": {"title": "T-09 · Speed Collapse Threshold", "subtitle": "Record-level congestion × speed scatter", "role": "hero"},
        "support_chart": {"title": "T-10 · Public Transport Decoupling", "subtitle": "Quartile comparison — correlation only", "role": "support"},
        "insight": "Speed collapse boundary appears near 22 km/h. PT usage quartiles show limited observable coupling in this dataset.",
        "nav_tab": 4,
        "nav_title": "Hidden Patterns",
        "nav_desc": "Explore distributional congestion structure.",
    },
    "p5_hidden_patterns": {
        "primary_kpis": [
            {"label": "Skewed Distributions", "value": "11 roads", "severity": "warning"},
            {"label": "Weather Risk Cells", "value": "8 high", "severity": "warning"},
            {"label": "Ridgeline Peaks", "value": ">90", "severity": "critical"},
            {"label": "Pattern Confidence", "value": "Moderate", "severity": "neutral"},
        ],
        "hero_chart": {"title": "T-11 · Congestion Ridgeline", "subtitle": "16-road distribution stack", "role": "hero"},
        "support_chart": {"title": "T-12 · Weather × Roadwork Heatmap", "subtitle": "Operational risk scheduling grid", "role": "support"},
        "insight": "Right-skewed road distributions dominate critical overload quadrant. Weather-roadwork intersections elevate incident probability.",
        "nav_tab": 5,
        "nav_title": "Advanced Analytics Laboratory",
        "nav_desc": "Multi-dimensional area stress profiling.",
    },
    "p6_advanced_lab": {
        "primary_kpis": [
            {"label": "Areas Profiled", "value": "8", "severity": "neutral"},
            {"label": "Stress Dimensions", "value": "6", "severity": "neutral"},
            {"label": "Overlay Limit", "value": "4 max", "severity": "info"},
            {"label": "Lab Mode", "value": "ACTIVE", "severity": "info"},
        ],
        "hero_chart": {"title": "T-13 · Compound Stress Radar", "subtitle": "Normalized multi-metric area overlay", "role": "hero", "fullscreen_key": "t13_radar"},
        "support_chart": {"title": "T-02 · Parallel Coordinates", "subtitle": "Area performance matrix", "role": "support", "fullscreen_key": "t02_parcoords"},
        "insight": "Advanced lab supports high-density comparison. Full analytics render in Phase 3+.",
        "nav_tab": None,
    },
}

AQI_MOCK = {
    "p1_crisis_overview": {
        "severity_badge": "SEVERE",
        "primary_kpis": [
            {"label": "Chronic Crisis Rate", "value": "68.4%", "severity": "critical"},
            {"label": "Peak PM2.5", "value": "389.2 µg/m³", "severity": "critical"},
            {"label": "Annual Mean PM2.5", "value": "142.7 µg/m³", "severity": "warning"},
            {"label": "Severe Days", "value": "124", "severity": "critical"},
        ],
        "secondary_kpis": [
            {"label": "WHO Exceedance", "value": "Daily", "severity": "warning"},
            {"label": "Winter Burden", "value": "Highest", "severity": "critical"},
            {"label": "Monsoon Relief", "value": "Moderate", "severity": "safe"},
            {"label": "Persistence Index", "value": "High", "severity": "warning"},
        ],
        "hero_chart": {"title": "A-01 · Chronic Crisis Scorecard", "subtitle": "Cumulative atmospheric burden indicators", "role": "hero"},
        "support_chart": {"title": "A-05 · Pollution Persistence Series", "subtitle": "Daily PM2.5 with 7-day rolling mean", "role": "support"},
        "insight": "PM2.5 chronic burden far exceeds WHO annual guideline (5 µg/m³). Winter stagnation drives sustained Severe classifications.",
        "nav_tab": 1,
        "nav_title": "Temporal Patterns",
        "nav_desc": "Calendar and monthly pollution rhythm analysis.",
    },
    "p2_temporal_patterns": {
        "primary_kpis": [
            {"label": "Worst Month", "value": "Nov 2022", "severity": "critical"},
            {"label": "Best Month", "value": "Aug 2021", "severity": "safe"},
            {"label": "Calendar Severe Days", "value": "412", "severity": "critical"},
            {"label": "Monthly Variability", "value": "±48.2", "severity": "warning"},
        ],
        "hero_chart": {"title": "A-02 · 3-Year Calendar Heatmap", "subtitle": "1,095-day PM2.5 grid", "role": "hero", "fullscreen_key": "a02_calendar"},
        "support_chart": {"title": "A-04 · Monthly PM2.5 Variability", "subtitle": "Mean ± SD by month", "role": "support"},
        "insight": "Winter months show persistent red-to-purple calendar bands. Monsoon months exhibit partial atmospheric relief.",
        "nav_tab": 2,
        "nav_title": "Atmospheric Intelligence",
        "nav_desc": "Identify stagnation and trap conditions.",
    },
    "p3_atmospheric_intelligence": {
        "primary_kpis": [
            {"label": "Stagnation Trap Days", "value": "287", "severity": "critical"},
            {"label": "Low VV + High PM2.5", "value": "41%", "severity": "critical"},
            {"label": "Regime Classes", "value": "4", "severity": "neutral"},
            {"label": "Dispersion Index", "value": "Low", "severity": "warning"},
        ],
        "hero_chart": {"title": "A-06 · Stagnation Hexbin", "subtitle": "VV × PM2.5 density trap zone", "role": "hero"},
        "support_chart": {"title": "A-07 · Extreme Day Radar", "subtitle": "Severe / Average / Good profiles", "role": "support"},
        "insight": "Low visibility and low dispersion correlate with highest PM2.5 concentrations in the stagnation trap quadrant.",
        "nav_tab": 3,
        "nav_title": "Weather Relationships",
        "nav_desc": "Meteorological drivers of pollution amplification.",
    },
    "p4_weather_relationships": {
        "primary_kpis": [
            {"label": "Temp Correlation", "value": "Strong", "severity": "warning"},
            {"label": "Pressure Trigger", "value": "Universal", "severity": "critical"},
            {"label": "Wind Rescue (Winter)", "value": "Limited", "severity": "warning"},
            {"label": "Gust Paradox", "value": "Observed", "severity": "neutral"},
        ],
        "hero_chart": {"title": "A-08 · Minimum Temperature Scatter", "subtitle": "Tm × PM2.5 × AQI category", "role": "hero"},
        "support_chart": {"title": "A-09 · Pressure Universal Trigger", "subtitle": "SLP band × season grouped bars", "role": "support"},
        "insight": "Pressure bands and minimum temperature show consistent amplification patterns across seasons in filtered view.",
        "nav_tab": 4,
        "nav_title": "Hidden Patterns",
        "nav_desc": "Statistical variability and seasonal structure.",
    },
    "p5_hidden_patterns": {
        "primary_kpis": [
            {"label": "Seasonal Skew", "value": "Winter", "severity": "critical"},
            {"label": "Gust Ratio Peak", "value": "Q4", "severity": "warning"},
            {"label": "Temp Spread Inversion", "value": "Detected", "severity": "warning"},
            {"label": "Variability Tier", "value": "High", "severity": "neutral"},
        ],
        "hero_chart": {"title": "A-03 · Seasonal Ridgeline", "subtitle": "4-season PM2.5 distributions", "role": "hero"},
        "support_chart": {"title": "A-11 · Gust Ratio Paradox", "subtitle": "Quintile PM2.5 with CI bands", "role": "support"},
        "insight": "Winter ridgelines show heaviest right tails. Gust ratio paradox visible in mid-quintile resuspension zone.",
        "nav_tab": 5,
        "nav_title": "Advanced Analytics Laboratory",
        "nav_desc": "Full meteorological co-factor matrix.",
    },
    "p6_advanced_lab": {
        "primary_kpis": [
            {"label": "Met Variables", "value": "7", "severity": "neutral"},
            {"label": "Pairplot Panels", "value": "36", "severity": "neutral"},
            {"label": "Category Encoding", "value": "6-band", "severity": "info"},
            {"label": "Lab Mode", "value": "ACTIVE", "severity": "info"},
        ],
        "hero_chart": {"title": "A-15 · Full Meteorological Pairplot", "subtitle": "6×6 co-factor matrix", "role": "hero", "fullscreen_key": "a15_pairplot"},
        "support_chart": {"title": "A-13 · Four Atmospheric States", "subtitle": "Regime scatter with insets", "role": "support"},
        "insight": "Advanced lab hosts extreme-density visuals. Pairplot and regime charts activate in Phase 3+.",
        "nav_tab": None,
    },
}


def get_page_mock(dashboard: str, page_key: str) -> dict:
    catalog = TRAFFIC_MOCK if dashboard == "traffic" else AQI_MOCK
    return catalog.get(page_key, {})
