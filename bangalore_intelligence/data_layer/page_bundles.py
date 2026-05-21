"""Page data bundles — orchestration layer (no UI)."""

from config.data_config import COL_AREA, COL_CONGESTION, COL_PM25, COL_ROAD
from dashboards.aqi.charts import (
    a01_crisis_scorecard,
    a02_calendar_heatmap,
    a03_seasonal_ridgeline,
    a04_monthly_variability,
    a05_persistence_series,
    a06_stagnation_hexbin,
    a07_extreme_day_radar,
    a08_temperature_scatter,
    a09_pressure_trigger,
    a10_wind_rescue,
    a11_gust_paradox,
    a12_temp_spread,
    a13_atmospheric_states,
    a14_season_pressure_grid,
    a15_pairplot,
)
from dashboards.traffic.charts import (
    t01_scorecard,
    t02_parallel_coords,
    t03_stream_graph,
    t04_violin_weekly,
    t05_quadrant_scatter,
    t06_burden_treemap,
    t07_mobility_exclusion,
    t08_incident_cliff,
    t09_speed_threshold,
    t10_pt_decoupling,
    t11_ridgeline,
    t12_weather_heatmap,
    t13_compound_radar,
    t14_density_hexbin,
    t15_bubble_matrix,
)
from data_layer.aqi_transforms import (
    compute_aqi_atmospheric_kpis,
    compute_aqi_crisis_kpis,
    compute_aqi_lab_kpis,
    compute_aqi_patterns_kpis,
    compute_aqi_weather_kpis,
    get_aqi_category_profiles,
    get_aqi_category_transition_matrix,
    get_atmospheric_regime_data,
    get_daily_aqi_calendar,
    get_gust_ratio_quintiles,
    get_pairplot_dataset,
    get_persistence_series,
    get_pollutant_correlation_matrix,
    get_season_slp_vv_grid,
    get_seasonal_drift_series,
    get_seasonal_pm25_ridgeline,
    get_slp_season_summary,
    get_slp_vv_scatter,
    get_temp_pm25_scatter,
    get_temp_spread_bands,
    get_temporal_aqi_calendar,
    get_wind_season_summary,
)
from data_layer.loaders import load_aqi_clean, load_traffic_clean
from data_layer.traffic_transforms import (
    compute_traffic_command_kpis,
    compute_traffic_patterns_kpis,
    compute_traffic_spatial_kpis,
    compute_traffic_temporal_kpis,
    compute_traffic_threshold_kpis,
    format_record_count,
    get_area_environmental_burden,
    get_area_summary,
    get_congestion_speed_scatter,
    get_congestion_transition_matrix,
    get_incident_congestion_bands,
    get_monthly_bubble_data,
    get_monthly_stream_data,
    get_parallel_coords_data,
    get_pt_quartile_summary,
    get_radar_normalized_metrics,
    get_road_congestion_distributions,
    get_road_mobility_exclusion,
    get_road_stats,
    get_traffic_volume_congestion,
    get_weather_roadwork_matrix,
    get_weekly_violin_records,
)
from filters.aqi_filters import apply_aqi_filters
from filters.interaction import (
    get_aqi_context,
    get_traffic_context,
    merge_chart_config,
    read_interaction_state,
)
from services.state.detail_content import (
    build_aqi_day_detail,
    build_aqi_regime_detail,
    build_traffic_road_detail,
)
from filters.traffic_filters import apply_traffic_filters


def _traffic_cfg(state: dict, role: str = "hero") -> dict:
    return merge_chart_config({"role": role}, "traffic")


def _aqi_cfg(state: dict, role: str = "hero") -> dict:
    return merge_chart_config({"role": role}, "aqi")


def build_traffic_command_bundle(state: dict) -> dict:
    df = apply_traffic_filters(load_traffic_clean(), state)
    n = len(df)
    if n == 0:
        return {"empty": True, "n": 0}

    area_data = get_area_summary(df)
    band_data = get_incident_congestion_bands(df)
    primary, secondary = compute_traffic_command_kpis(df)
    mean_cong = df[COL_CONGESTION].mean()

    return {
        "empty": False,
        "n": n,
        "record_count": format_record_count(n),
        "primary_kpis": primary,
        "secondary_kpis": secondary,
        "severity_badge": "CRITICAL" if mean_cong >= 90 else "WARNING",
        "hero_chart": {
            "title": "T-01 · Saturation Command Scorecard",
            "subtitle": "Executive system stress · area operational ranking",
            "caption": "Command gauge reflects filtered system congestion; bars rank area saturation severity.",
            "fig": t01_scorecard.render(area_data, _traffic_cfg(state, "hero")),
        },
        "support_chart": {
            "title": "T-08 · First Incident Cliff",
            "subtitle": "Mean congestion by incident band",
            "caption": "Step escalation at 1→2 incidents (+21.5 pts typical) defines operational cliff threshold.",
            "fig": t08_incident_cliff.render(band_data, _traffic_cfg(state, "supporting")),
        },
        "insight": (
            f"System mean congestion {mean_cong:.1f} across {df[COL_AREA].nunique()} areas "
            f"({n:,} records). Capacity saturation and incident cliff patterns confirm chronic overload."
        ),
        "nav_tab": 1,
        "nav_title": "Temporal Intelligence",
        "nav_desc": "Examine congestion evolution and transition dynamics.",
        "linked_controls": False,
    }


def build_traffic_temporal_bundle(state: dict) -> dict:
    df = apply_traffic_filters(load_traffic_clean(), state)
    n = len(df)
    if n == 0:
        return {"empty": True, "n": 0}

    stream = get_monthly_stream_data(df)
    return {
        "empty": False,
        "n": n,
        "record_count": format_record_count(n),
        "primary_kpis": compute_traffic_temporal_kpis(df),
        "secondary_kpis": [],
        "hero_chart": {
            "title": "T-03 · Temporal Stream Intelligence",
            "subtitle": "Monthly congestion pressure by area",
            "caption": "Restrained stacked flow · hover for area isolation.",
            "fig": t03_stream_graph.render(stream, _traffic_cfg(state, "hero")),
        },
        "support_chart": {
            "title": "T-04 · Weekly Violin Distribution",
            "subtitle": "Day-of-week congestion spread",
            "caption": "Violin traces per weekday · boxplot fallback below 30 records per day.",
            "fig": t04_violin_weekly.render(
                get_weekly_violin_records(df),
                {**_traffic_cfg(state, "supporting"), "fallback_box": n < 200},
            ),
        },
        "insight": "Temporal peaks cluster in late-year windows. Weekend relief is marginal relative to weekday baseline congestion.",
        "nav_tab": 2,
        "nav_title": "Spatial Operations",
        "nav_desc": "Map congestion hotspots and mobility pressure.",
        "linked_controls": False,
    }


def build_traffic_spatial_bundle(state: dict) -> dict:
    ctx = get_traffic_context()
    df = apply_traffic_filters(load_traffic_clean(), state)
    n = len(df)
    if n == 0:
        return {"empty": True, "n": 0}

    roads = get_road_stats(df)
    burden = get_area_environmental_burden(df)
    mobility = get_road_mobility_exclusion(df)
    highlight_area = ctx.get("highlight_area")
    highlight_road = ctx.get("highlight_road")
    hero_cfg = _traffic_cfg(state, "hero")
    support_cfg = _traffic_cfg(state, "supporting")
    collapsed_cfg = _traffic_cfg(state, "supporting")
    if highlight_area:
        hero_cfg["highlight_area"] = highlight_area
        support_cfg["highlight_area"] = highlight_area
    if highlight_road:
        hero_cfg["highlight_road"] = highlight_road
        support_cfg["highlight_road"] = highlight_road
        collapsed_cfg["highlight_road"] = highlight_road

    roads_index = {i: r for i, r in enumerate(roads[COL_ROAD].tolist())}

    return {
        "empty": False,
        "n": n,
        "record_count": format_record_count(n),
        "primary_kpis": compute_traffic_spatial_kpis(
            df, highlight_area, highlight_road
        ),
        "secondary_kpis": [],
        "detail_panel": build_traffic_road_detail(df, highlight_road),
        "hero_chart": {
            "chart_id": "T-05",
            "interactive": True,
            "interaction_meta": {"roads_df": roads, "roads_by_index": roads_index},
            "title": "T-05 · Road Management Priority Quadrant",
            "subtitle": "Congestion × capacity operational classification · click a road to investigate",
            "caption": "Quadrant zones classify roads: baseline, constrained flow, capacity margin, critical overload.",
            "fig": t05_quadrant_scatter.render(roads, hero_cfg),
        },
        "support_chart": {
            "chart_id": "T-06",
            "interactive": True,
            "title": "T-06 · Environmental Burden Treemap",
            "subtitle": "Area × road impact hierarchy",
            "caption": "Hierarchical burden reveals which corridors drive environmental impact within the filter scope.",
            "fig": t06_burden_treemap.render(burden, support_cfg),
        },
        "insight": (
            "Quadrant scatter exposes roads in critical overload (high congestion + near-max capacity). "
            "Treemap and mobility penalty views complete the spatial investigation."
        ),
        "nav_tab": 3,
        "nav_title": "Threshold Analytics",
        "nav_desc": "Examine congestion failure boundaries and decoupling effects.",
        "linked_controls": "traffic",
        "collapsed_chart": {
            "chart_id": "T-07",
            "interactive": True,
            "label": "▶ T-07 · ACTIVE MOBILITY EXCLUSION",
            "title": "T-07 · Active Mobility Exclusion",
            "subtitle": "Diverging congestion penalty by road",
            "caption": "Bars show each road's congestion deviation from system baseline (pedestrian pressure included).",
            "fig": t07_mobility_exclusion.render(mobility, collapsed_cfg),
        },
    }


def build_traffic_lab_bundle(state: dict) -> dict:
    ctx = get_traffic_context()
    df = apply_traffic_filters(load_traffic_clean(), state)
    n = len(df)
    if n == 0:
        return {"empty": True, "n": 0}

    parcoords = get_parallel_coords_data(df)
    radar_data = get_radar_normalized_metrics(df)
    hex_data = get_traffic_volume_congestion(df)
    cfg = _traffic_cfg(state, "supporting")
    cfg["fullscreen_key"] = "t02_parcoords"
    radar_cfg = _traffic_cfg(state, "hero")
    radar_cfg["max_overlays"] = 4
    focus = ctx.get("highlight_area") or read_interaction_state("traffic").get("focus_entity")
    if focus:
        radar_cfg["focus_area"] = focus
    from dashboards.traffic.charts.t13_compound_radar import radar_trace_areas

    radar_areas = radar_trace_areas(radar_data, radar_cfg)

    return {
        "empty": False,
        "n": n,
        "record_count": format_record_count(n),
        "primary_kpis": [
            {"label": "Areas Profiled", "value": str(df[COL_AREA].nunique()), "severity": "neutral"},
            {"label": "Radar Overlays", "value": "Max 4", "severity": "neutral"},
            {"label": "Lab Mode", "value": "ACTIVE", "severity": "info"},
            {"label": "Records", "value": f"{n:,}", "severity": "neutral"},
        ],
        "secondary_kpis": [],
        "detail_panel": build_traffic_road_detail(
            df, read_interaction_state("traffic").get("selected_road")
        ),
        "hero_chart": {
            "chart_id": "T-13",
            "interactive": True,
            "interaction_meta": {"radar_areas": radar_areas},
            "title": "T-13 · Compound Stress Radar",
            "subtitle": "Normalized six-axis area stress comparison · click trace to focus",
            "caption": "Top stress areas overlaid on 0–100 scale · focus area emphasized when linked selection is active.",
            "fig": t13_compound_radar.render(radar_data, radar_cfg),
            "fullscreen_key": "t13_radar",
        },
        "support_chart": {
            "chart_id": "T-02",
            "interactive": True,
            "interaction_meta": {"parcoords_areas": parcoords[COL_AREA].tolist()},
            "title": "T-02 · Parallel Coordinates Intelligence",
            "subtitle": "Multivariate area performance matrix · click a line to link focus",
            "caption": "Parallel axes profile congestion, speed, and incidents across areas.",
            "fig": t02_parallel_coords.render(parcoords, cfg),
            "fullscreen_key": "t02_parcoords",
        },
        "insight": (
            "Advanced lab suite: compound stress radar for area comparison, parallel coordinates for "
            "multivariate profiling, and volume–congestion density for record-level structure."
        ),
        "nav_tab": None,
        "linked_controls": "traffic",
        "collapsed_chart": {
            "label": "▶ T-14 · VOLUME–CONGESTION DENSITY",
            "title": "T-14 · Traffic–Congestion Density Hexbin",
            "subtitle": "Record-level volume vs congestion",
            "caption": "Hexbin density exposes high-volume corridors operating under sustained congestion.",
            "fig": t14_density_hexbin.render(hex_data, _traffic_cfg(state, "supporting")),
        },
    }


def build_traffic_threshold_bundle(state: dict) -> dict:
    df = apply_traffic_filters(load_traffic_clean(), state)
    n = len(df)
    if n == 0:
        return {"empty": True, "n": 0}

    scatter = get_congestion_speed_scatter(df)
    pt = get_pt_quartile_summary(df)
    return {
        "empty": False,
        "n": n,
        "record_count": format_record_count(n),
        "primary_kpis": compute_traffic_threshold_kpis(df),
        "secondary_kpis": [],
        "hero_chart": {
            "title": "T-09 · Speed Collapse Threshold",
            "subtitle": "Record-level congestion × speed scatter",
            "caption": "Quadrant lines at 30 km/h and congestion 75 · critical overload zone annotated.",
            "fig": t09_speed_threshold.render(scatter, _traffic_cfg(state, "hero")),
        },
        "support_chart": {
            "title": "T-10 · Public Transport Decoupling",
            "subtitle": "PT quartile comparison — observational only",
            "caption": "Grouped congestion, speed, and incident means by public transport usage quartile.",
            "fig": t10_pt_decoupling.render(pt, _traffic_cfg(state, "supporting")),
        },
        "insight": "Speed collapse boundary appears near 22–30 km/h. PT usage quartiles show limited observable coupling in this dataset.",
        "nav_tab": 4,
        "nav_title": "Hidden Patterns",
        "nav_desc": "Explore distributional congestion structure.",
        "linked_controls": "traffic",
    }


def build_traffic_patterns_bundle(state: dict) -> dict:
    ctx = get_traffic_context()
    df = apply_traffic_filters(load_traffic_clean(), state)
    n = len(df)
    if n == 0:
        return {"empty": True, "n": 0}

    ridges = get_road_congestion_distributions(df)
    weather = get_weather_roadwork_matrix(df)
    hero_cfg = _traffic_cfg(state, "hero")
    if ctx.get("highlight_area"):
        hero_cfg["highlight_area"] = ctx["highlight_area"]

    return {
        "empty": False,
        "n": n,
        "record_count": format_record_count(n),
        "primary_kpis": compute_traffic_patterns_kpis(df),
        "secondary_kpis": [],
        "hero_chart": {
            "title": "T-11 · Congestion Ridgeline",
            "subtitle": "Top-road distribution stack",
            "caption": "KDE-style ridges sorted by median congestion · up to 16 roads.",
            "fig": t11_ridgeline.render(ridges, hero_cfg),
        },
        "support_chart": {
            "title": "T-12 · Weather × Roadwork Heatmap",
            "subtitle": "Operational risk scheduling grid",
            "caption": "Mean congestion by weather condition and roadwork activity.",
            "fig": t12_weather_heatmap.render(weather, _traffic_cfg(state, "supporting")),
        },
        "insight": "Right-skewed road distributions dominate critical overload corridors. Weather–roadwork intersections elevate mean congestion.",
        "nav_tab": 5,
        "nav_title": "Advanced Analytics Laboratory",
        "nav_desc": "Multi-dimensional area stress profiling.",
        "linked_controls": "traffic",
        "collapsed_chart": {
            "label": "▶ T-15 · AREA × MONTH BUBBLE MATRIX",
            "title": "T-15 · Area × Month Bubble Matrix",
            "subtitle": "Temporal area stress comparison",
            "caption": "Bubble size encodes incidents; color encodes area identity; position shows month × area stress.",
            "fig": t15_bubble_matrix.render(
                get_monthly_bubble_data(df),
                _traffic_cfg(state, "supporting"),
            ),
        },
    }


def build_aqi_crisis_bundle(state: dict) -> dict:
    df = apply_aqi_filters(load_aqi_clean(), state)
    n = len(df)
    if n == 0:
        return {"empty": True, "n": 0}

    primary, secondary = compute_aqi_crisis_kpis(df)
    chronic_rate = (df[COL_PM25] > 120).mean() * 100

    return {
        "empty": False,
        "n": n,
        "record_count": format_record_count(n),
        "primary_kpis": primary,
        "secondary_kpis": secondary,
        "severity_badge": "SEVERE" if chronic_rate > 50 else "WARNING",
        "hero_chart": {
            "title": "A-01 · Chronic Crisis Scorecard",
            "subtitle": "Executive atmospheric burden · category structure",
            "caption": "Mean PM2.5 gauge vs WHO reference; category bars quantify chronic crisis day distribution.",
            "fig": a01_crisis_scorecard.render(df, _aqi_cfg(state, "hero")),
        },
        "support_chart": {
            "title": "A-05 · Pollution Persistence Series",
            "subtitle": "Daily PM2.5 with 7-day rolling mean",
            "caption": "Rolling mean distinct from daily values · elevated band 60–120 µg/m³.",
            "fig": a05_persistence_series.render(
                get_persistence_series(df),
                _aqi_cfg(state, "supporting"),
            ),
        },
        "insight": (
            f"Chronic crisis rate {chronic_rate:.1f}% of days exceed Very Poor (PM2.5 > 120 µg/m³). "
            f"Filtered mean PM2.5 is {df[COL_PM25].mean():.1f} µg/m³ — the WHO annual guideline is "
            f"5 µg/m³, underscoring persistent atmospheric burden in this view."
        ),
        "insight_severity": "critical",
        "nav_tab": 1,
        "nav_title": "Temporal Patterns",
        "nav_desc": "Calendar and seasonal pollution rhythm analysis.",
        "linked_controls": False,
    }


def build_aqi_temporal_bundle(state: dict) -> dict:
    df = apply_aqi_filters(load_aqi_clean(), state)
    n = len(df)
    if n == 0:
        return {"empty": True, "n": 0}

    cal = get_daily_aqi_calendar(df)
    month_cal = get_temporal_aqi_calendar(df)
    return {
        "empty": False,
        "n": n,
        "record_count": format_record_count(n),
        "primary_kpis": [
            {"label": "Days in View", "value": f"{n:,}", "severity": "neutral"},
            {"label": "Mean PM2.5", "value": f"{df[COL_PM25].mean():.1f} µg/m³", "severity": "warning"},
            {"label": "Peak PM2.5", "value": f"{df[COL_PM25].max():.1f} µg/m³", "severity": "critical"},
            {
                "label": "Severe Share",
                "value": f"{(df[COL_PM25] > 250).mean() * 100:.1f}%",
                "severity": "critical",
            },
        ],
        "secondary_kpis": [],
        "detail_panel": build_aqi_day_detail(df),
        "hero_chart": {
            "chart_id": "A-02",
            "interactive": True,
            "interaction_meta": {"calendar_df": cal},
            "title": "A-02 · 3-Year Calendar Heatmap",
            "subtitle": "Weekly PM2.5 intensity grid · click a week to investigate",
            "caption": "Environmental calendar · week × year resolution.",
            "fig": a02_calendar_heatmap.render(cal, _aqi_cfg(state, "hero")),
            "fullscreen_key": "a02_calendar",
        },
        "support_chart": {
            "title": "A-04 · Temporal AQI Calendar",
            "subtitle": "Month × year mean PM2.5 rhythm",
            "caption": "Seasonal cycles and crisis clusters at monthly resolution.",
            "fig": a04_monthly_variability.render(month_cal, _aqi_cfg(state, "supporting")),
        },
        "insight": "Winter months show persistent high-PM2.5 bands. Monsoon months exhibit partial atmospheric relief.",
        "nav_tab": 2,
        "nav_title": "Atmospheric Intelligence",
        "nav_desc": "Identify seasonal drift and stagnation patterns.",
        "linked_controls": "aqi",
    }


def build_aqi_atmospheric_bundle(state: dict) -> dict:
    ctx = get_aqi_context()
    df = apply_aqi_filters(load_aqi_clean(), state)
    n = len(df)
    if n == 0:
        return {"empty": True, "n": 0}

    hex_data = get_slp_vv_scatter(df)
    profiles = get_aqi_category_profiles(df)
    hero_cfg = _aqi_cfg(state, "hero")
    if ctx.get("highlight_season"):
        hero_cfg["highlight_season"] = ctx["highlight_season"]
    return {
        "empty": False,
        "n": n,
        "record_count": format_record_count(n),
        "primary_kpis": compute_aqi_atmospheric_kpis(df, ctx.get("highlight_season")),
        "secondary_kpis": [],
        "hero_chart": {
            "title": "A-06 · Stagnation Hexbin",
            "subtitle": "SLP × VV density trap zone",
            "caption": "Cell color encodes mean PM2.5 · stagnation trap quadrant visible at low VV.",
            "fig": a06_stagnation_hexbin.render(hex_data, hero_cfg),
        },
        "support_chart": {
            "title": "A-07 · Extreme Day Radar",
            "subtitle": "Good / Moderate / Severe meteorological profiles",
            "caption": "Normalized 0–100 category profiles across six atmospheric axes.",
            "fig": a07_extreme_day_radar.render(profiles, _aqi_cfg(state, "supporting")),
        },
        "insight": "Seasonal drift reveals winter accumulation vs monsoon partial recovery. Link season focus to contextualize KPIs.",
        "nav_tab": 3,
        "nav_title": "Weather Relationships",
        "nav_desc": "Category transitions and meteorological drivers.",
        "linked_controls": "aqi",
    }


def build_aqi_patterns_bundle(state: dict) -> dict:
    df = apply_aqi_filters(load_aqi_clean(), state)
    n = len(df)
    if n == 0:
        return {"empty": True, "n": 0}

    ridge = get_seasonal_pm25_ridgeline(df)
    gust = get_gust_ratio_quintiles(df)
    return {
        "empty": False,
        "n": n,
        "record_count": format_record_count(n),
        "primary_kpis": compute_aqi_patterns_kpis(df),
        "secondary_kpis": [],
        "hero_chart": {
            "title": "A-03 · Seasonal PM2.5 Ridgeline",
            "subtitle": "Atmospheric density by season",
            "caption": "KDE ridgelines show pollutant distribution shape — winter right-tail vs monsoon relief.",
            "fig": a03_seasonal_ridgeline.render(ridge, _aqi_cfg(state, "hero")),
        },
        "support_chart": {
            "title": "A-11 · Gust Ratio Paradox",
            "subtitle": "Quintile PM2.5 with CI bands",
            "caption": "Mid-quintile resuspension visible in gust ratio structure.",
            "fig": a11_gust_paradox.render(gust, _aqi_cfg(state, "supporting")),
        },
        "insight": "Winter ridgelines show heaviest right tails. Gust ratio paradox visible in mid-quintile resuspension zone.",
        "collapsed_chart": {
            "title": "A-12 · Temperature Spread Bands",
            "subtitle": "Diurnal spread vs mean PM2.5",
            "caption": "Progressive disclosure · spread band grouped means.",
            "fig": a12_temp_spread.render(
                get_temp_spread_bands(df),
                _aqi_cfg(state, "supporting"),
            ),
        },
        "nav_tab": 5,
        "nav_title": "Advanced Analytics Laboratory",
        "nav_desc": "High-density multivariate analysis environment.",
        "linked_controls": "aqi",
    }


def build_aqi_weather_bundle(state: dict) -> dict:
    df = apply_aqi_filters(load_aqi_clean(), state)
    n = len(df)
    if n == 0:
        return {"empty": True, "n": 0}

    temp_scatter = get_temp_pm25_scatter(df)
    pressure = get_slp_season_summary(df)
    return {
        "empty": False,
        "n": n,
        "record_count": format_record_count(n),
        "primary_kpis": compute_aqi_weather_kpis(df),
        "secondary_kpis": [],
        "hero_chart": {
            "title": "A-08 · Minimum Temperature Scatter",
            "subtitle": "Tm × PM2.5 × AQI category",
            "caption": "Category-colored scatter · sampled for readability above 2,500 points.",
            "fig": a08_temperature_scatter.render(temp_scatter, _aqi_cfg(state, "hero")),
        },
        "support_chart": {
            "title": "A-09 · Pressure Universal Trigger",
            "subtitle": "SLP band × season grouped bars",
            "caption": "Pressure bands amplify PM2.5 consistently across seasons in filtered view.",
            "fig": a09_pressure_trigger.render(pressure, _aqi_cfg(state, "supporting")),
        },
        "insight": "Pressure bands and minimum temperature show consistent amplification patterns across seasons.",
        "collapsed_chart": {
            "title": "A-10 · Wind Rescue (Winter)",
            "subtitle": "Wind band × season",
            "caption": "Progressive disclosure · wind rescue limited in winter cells.",
            "fig": a10_wind_rescue.render(
                get_wind_season_summary(df),
                _aqi_cfg(state, "supporting"),
            ),
        },
        "nav_tab": 4,
        "nav_title": "Hidden Patterns",
        "nav_desc": "Statistical variability and seasonal structure.",
        "linked_controls": "aqi",
    }


def build_aqi_lab_bundle(state: dict) -> dict:
    df = apply_aqi_filters(load_aqi_clean(), state)
    n = len(df)
    if n == 0:
        return {"empty": True, "n": 0}

    pairplot = get_pairplot_dataset(df)
    regimes = get_atmospheric_regime_data(df)
    grid = get_season_slp_vv_grid(df)
    cfg = _aqi_cfg(state, "hero")
    cfg["fullscreen_key"] = "a15_pairplot"
    regime_order = regimes["regime"].unique().tolist() if "regime" in regimes.columns else []

    return {
        "empty": False,
        "n": n,
        "record_count": format_record_count(n),
        "primary_kpis": compute_aqi_lab_kpis(df),
        "secondary_kpis": [],
        "detail_panel": build_aqi_regime_detail() or build_aqi_day_detail(df),
        "hero_chart": {
            "chart_id": "A-15",
            "interactive": True,
            "selection_mode": ("points",),
            "title": "A-15 · Full Meteorological Pairplot",
            "subtitle": "7×7 co-factor matrix · click scatter cells to emphasize a factor",
            "caption": "Histogram diagonals · category-encoded scatters · correlation fallback below 100 rows.",
            "fig": a15_pairplot.render(pairplot, cfg),
            "fullscreen_key": "a15_pairplot",
        },
        "support_chart": {
            "chart_id": "A-13",
            "interactive": True,
            "interaction_meta": {"regime_order": regime_order},
            "title": "A-13 · Four Atmospheric States",
            "subtitle": "Regime scatter with classification · click trace to compare",
            "caption": "Stagnation trap, dispersive relief, pressure lock, and baseline regimes.",
            "fig": a13_atmospheric_states.render(regimes, _aqi_cfg(state, "supporting")),
        },
        "insight": "Pairplot exposes multivariate co-factors. Atmospheric regime scatter isolates stagnation trap days.",
        "nav_tab": None,
        "linked_controls": "aqi",
        "collapsed_chart": {
            "title": "A-14 · Season × Pressure Grid",
            "subtitle": "Mean PM2.5 heatmap (lazy load)",
            "caption": "Season × SLP band mean PM2.5 grid.",
            "fig": a14_season_pressure_grid.render(grid, _aqi_cfg(state, "supporting")),
        },
    }


def get_bundle_builder(page_key: str, dashboard: str):
    traffic = {
        "p1_command_overview": build_traffic_command_bundle,
        "p2_temporal_intelligence": build_traffic_temporal_bundle,
        "p3_spatial_operations": build_traffic_spatial_bundle,
        "p4_threshold_analytics": build_traffic_threshold_bundle,
        "p5_hidden_patterns": build_traffic_patterns_bundle,
        "p6_advanced_lab": build_traffic_lab_bundle,
    }
    aqi = {
        "p1_crisis_overview": build_aqi_crisis_bundle,
        "p2_temporal_patterns": build_aqi_temporal_bundle,
        "p3_atmospheric_intelligence": build_aqi_atmospheric_bundle,
        "p4_weather_relationships": build_aqi_weather_bundle,
        "p5_hidden_patterns": build_aqi_patterns_bundle,
        "p6_advanced_lab": build_aqi_lab_bundle,
    }
    catalog = traffic if dashboard == "traffic" else aqi
    return catalog.get(page_key)
