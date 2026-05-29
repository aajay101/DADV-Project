"""Page data bundles — orchestration layer (no UI)."""

from config.data_config import (
    AQI_PM25_WHO_ANNUAL,
    COL_AREA,
    COL_AQI_CATEGORY,
    COL_CAPACITY,
    COL_CONGESTION,
    COL_PM25,
    COL_ROAD,
)
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
    get_atmospheric_regime_data,
    get_daily_aqi_calendar,
    get_gust_ratio_quintiles,
    get_pairplot_dataset,
    get_persistence_series,
    get_season_slp_vv_grid,
    get_seasonal_pm25_ridgeline,
    get_slp_season_summary,
    get_slp_vv_scatter,
    get_temp_pm25_scatter,
    get_temp_spread_bands,
    get_temporal_aqi_calendar,
    get_wind_season_summary,
)
from data_layer.lab_data import get_lab_dataset
from data_layer.loaders import load_aqi_clean, load_traffic_clean
from data_layer.traffic_transforms import (
    _attach_kpi_notes,
    compute_traffic_command_kpis,
    compute_traffic_patterns_kpis,
    compute_traffic_spatial_kpis,
    compute_traffic_temporal_kpis,
    compute_traffic_threshold_kpis,
    format_record_count,
    get_area_environmental_burden,
    get_area_summary,
    get_congestion_speed_scatter,
    get_incident_congestion_bands,
    get_monthly_bubble_data,
    get_monthly_stream_data,
    get_parallel_coords_data,
    get_pt_quartile_summary,
    get_radar_normalized_metrics,
    get_area_stress_heatmap,
    get_road_distribution_profiles,
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
from filters.investigation_scope import apply_investigation_overlay_scope
from services.state.detail_content import (
    build_aqi_day_detail,
    build_aqi_regime_detail,
    build_traffic_road_detail,
)
from filters.traffic_filters import apply_traffic_filters
from data_layer.lazy_charts import lazy_fig_builder


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
    stream = get_monthly_stream_data(df)
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
            "chart_id": "T-01",
            "interactive": True,
            "title": "T-01 · Network Congestion And Area Ranking",
            "subtitle": "System congestion gauge and area severity bars",
            "caption": "Click an area bar to set chart focus · use Apply as filter to scope all pages.",
            "fig": t01_scorecard.render(
                area_data,
                {
                    **_traffic_cfg(state, "hero"),
                    "system_congestion": float(mean_cong),
                    "capacity_saturation_rate": float((df[COL_CAPACITY] >= 99.5).mean() * 100),
                },
            ),
        },
        "support_chart": {
            "chart_id": "T-03",
            "title": "T-03 · Monthly Congestion Trend By Area",
            "subtitle": "Network-wide monthly congestion rhythm",
            "caption": "Monthly mean congestion by area in the active filter scope.",
            "fig": t03_stream_graph.render(stream, _traffic_cfg(state, "supporting")),
        },
        "insight": (
            f"Mean congestion {mean_cong:.1f} across {df[COL_AREA].nunique()} areas "
            f"({n:,} filtered records). Area ranking and the monthly trend summarize current network stress."
        ),
        "nav_tab": 1,
        "nav_title": "Temporal Patterns",
        "nav_desc": "Monthly and weekday congestion rhythms.",
        "linked_controls": "traffic",
    }


def build_traffic_temporal_bundle(state: dict) -> dict:
    df = apply_traffic_filters(load_traffic_clean(), state)
    n = len(df)
    if n == 0:
        return {"empty": True, "n": 0}

    stream = get_monthly_stream_data(df)
    t15_df = apply_investigation_overlay_scope(df, "traffic", "T-15", state)
    return {
        "empty": False,
        "n": n,
        "record_count": format_record_count(n),
        "primary_kpis": compute_traffic_temporal_kpis(df),
        "secondary_kpis": [],
        "hero_chart": {
            "chart_id": "T-03",
            "title": "T-03 · Monthly Congestion Trend By Area",
            "subtitle": "Monthly congestion pressure by area",
            "caption": "Monthly mean congestion by area · hover to isolate a corridor.",
            "fig": t03_stream_graph.render(stream, _traffic_cfg(state, "hero")),
        },
        "support_chart": {
            "chart_id": "T-04",
            "title": "T-04 · Weekly Violin Distribution",
            "subtitle": "Day-of-week congestion spread",
            "caption": "Violin traces per weekday · boxplot fallback below 30 records per day.",
            "fig": t04_violin_weekly.render(
                get_weekly_violin_records(df),
                {**_traffic_cfg(state, "supporting"), "fallback_box": n < 200},
            ),
        },
        "secondary_charts": [
            {
                "chart_id": "T-15",
                "interactive": True,
                "title": "T-15 · Area-Month Congestion Heatmap",
                "subtitle": "Temporal area stress comparison",
                "caption": "Click a cell to set area and month focus · Apply as filter scopes area globally.",
                **lazy_fig_builder(
                    lambda d=t15_df, s=state: t15_bubble_matrix.render(
                        get_monthly_bubble_data(d),
                        _traffic_cfg(s, "supporting"),
                    )
                ),
            }
        ],
        "insight": "Temporal peaks cluster in late-year windows. Weekend relief is marginal relative to weekday baseline congestion.",
        "nav_tab": 2,
        "nav_title": "Road And Area Diagnostics",
        "nav_desc": "Compare roads and areas on congestion and capacity.",
        "linked_controls": "traffic",
    }


def build_traffic_spatial_bundle(state: dict) -> dict:
    ctx = get_traffic_context()
    df = apply_traffic_filters(load_traffic_clean(), state)
    n = len(df)
    if n == 0:
        return {"empty": True, "n": 0}

    t05_df = apply_investigation_overlay_scope(df, "traffic", "T-05", state)
    t06_df = apply_investigation_overlay_scope(df, "traffic", "T-06", state)
    t07_df = apply_investigation_overlay_scope(df, "traffic", "T-07", state)
    roads = get_road_stats(t05_df)
    burden = get_area_environmental_burden(t06_df)
    mobility = get_road_mobility_exclusion(t07_df)
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
            "subtitle": "Congestion × capacity classification · click a road to focus charts",
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
            "Treemap and pedestrian-adjusted pressure views complete the spatial diagnostic."
        ),
        "nav_tab": 3,
        "nav_title": "Speed And Service Thresholds",
        "nav_desc": "Speed decline and service threshold boundaries.",
        "linked_controls": "traffic",
        "secondary_charts": [
            {
                "chart_id": "T-07",
                "interactive": True,
                "title": "T-07 · Pedestrian-Adjusted Road Pressure",
                "subtitle": "Congestion deviation from system baseline by road",
                "caption": "Bars show each road's congestion deviation from the filtered-scope baseline (pedestrian exposure included).",
                "fig": t07_mobility_exclusion.render(mobility, collapsed_cfg),
            }
        ],
    }


def build_traffic_lab_bundle(state: dict) -> dict:
    ctx = get_traffic_context()
    df = get_lab_dataset("traffic", state)
    n = len(df)
    if n == 0:
        return {"empty": True, "n": 0}

    from data_layer.traffic_transforms import PARALLEL_AREA_DIMENSIONS

    t02_df = apply_investigation_overlay_scope(df, "traffic", "T-02", state)
    t13_df = apply_investigation_overlay_scope(df, "traffic", "T-13", state)
    parcoords = get_parallel_coords_data(t02_df)
    radar_data = get_radar_normalized_metrics(t13_df)
    heatmap_data = get_area_stress_heatmap(t13_df)
    t13_view = state.get("traffic_lab_t13_view", "heatmap")
    cfg = _traffic_cfg(state, "supporting")
    cfg["fullscreen_key"] = "t02_parcoords"
    radar_cfg = _traffic_cfg(state, "hero")
    radar_cfg["max_overlays"] = 4
    radar_cfg["view"] = t13_view
    visible = state.get("traffic_radar_visible_areas") or []
    if visible:
        radar_cfg["visible_areas"] = visible[:4]
    focus = ctx.get("highlight_area") or read_interaction_state("traffic").get("focus_entity")
    if focus:
        radar_cfg["focus_area"] = focus
    from dashboards.traffic.charts.t13_compound_radar import radar_trace_areas

    radar_areas = radar_trace_areas(radar_data, radar_cfg)
    t13_subtitle = (
        "Normalized area × metric heatmap"
        if t13_view != "radar"
        else "Radar overlay comparison · click trace to focus"
    )
    if focus:
        t13_subtitle = f"Focus: {focus} · {t13_subtitle}"

    if t13_view == "radar":
        t13_fig = t13_compound_radar.render_radar(radar_data, radar_cfg)
        t13_meta = {"radar_areas": radar_areas}
    else:
        t13_fig = t13_compound_radar.render_heatmap(heatmap_data, radar_cfg)
        t13_meta = {"heatmap_areas": heatmap_data.get("areas", [])}

    area_rank = get_area_summary(df).sort_values("mean_congestion", ascending=False)
    top_stress = area_rank[COL_AREA].head(3).tolist()
    baseline = area_rank[COL_AREA].tail(3).tolist()

    return {
        "empty": False,
        "n": n,
        "record_count": format_record_count(n),
        "primary_kpis": _attach_kpi_notes(
            [
                {"label": "Areas Profiled", "value": str(df[COL_AREA].nunique()), "severity": "neutral"},
                {"label": "Radar Overlays", "value": "Max 4", "severity": "neutral"},
                {"label": "Exploration Mode", "value": "Active", "severity": "info"},
                {"label": "Records", "value": f"{n:,}", "severity": "neutral"},
            ]
        ),
        "secondary_kpis": [],
        "detail_panel": build_traffic_road_detail(
            df, read_interaction_state("traffic").get("selected_road")
        ),
        "hero_chart": {
            "chart_id": "T-13",
            "interactive": True,
            "interaction_meta": t13_meta,
            "title": "T-13 · Area Stress Profile",
            "subtitle": t13_subtitle,
            "caption": (
                "Six stress dimensions per area (0–100 normalized) · toggle radar view in lab controls."
                if t13_view != "radar"
                else "Top stress areas on 0–100 scale · focus area emphasized when linked selection is active."
            ),
            "fig": t13_fig,
            "fullscreen_key": "t13_radar",
        },
        "support_chart": {
            "chart_id": "T-02",
            "interactive": True,
            "interaction_meta": {"parcoords_areas": parcoords[COL_AREA].tolist()},
            "title": "T-02 · Parallel Coordinates Matrix",
            "subtitle": "Eight-axis area performance profile",
            "caption": "Area-level z-score profile · open fullscreen for sampled record-level parcoords.",
            "fig": t02_parallel_coords.render(
                parcoords,
                {**cfg, "dimensions": PARALLEL_AREA_DIMENSIONS},
            ),
            "fullscreen_key": "t02_parcoords",
        },
        "secondary_charts": [
            {
                "chart_id": "T-14",
                "title": "T-14 · Traffic Volume And Congestion Density",
                "subtitle": "Record-level volume vs congestion",
                "caption": "Hexbin density exposes high-volume corridors operating under sustained congestion.",
                **lazy_fig_builder(
                    lambda d=df, s=state: t14_density_hexbin.render(
                        get_traffic_volume_congestion(d),
                        _traffic_cfg(s, "supporting"),
                    )
                ),
            }
        ],
        "insight": (
            "Analytical workspace: area stress profiles, parallel coordinates for multivariate comparison, "
            "and volume–congestion density for record-level structure."
        ),
        "nav_tab": None,
        "linked_controls": "traffic",
        "is_lab": True,
        "lab_meta": {
            "available_areas": sorted(df[COL_AREA].dropna().unique().tolist()),
            "top_stress_areas": top_stress,
            "baseline_areas": baseline,
        },
    }


def build_traffic_threshold_bundle(state: dict) -> dict:
    df = apply_traffic_filters(load_traffic_clean(), state)
    n = len(df)
    if n == 0:
        return {"empty": True, "n": 0}

    t09_df = apply_investigation_overlay_scope(df, "traffic", "T-09", state)
    scatter = get_congestion_speed_scatter(t09_df)
    pt = get_pt_quartile_summary(df)
    return {
        "empty": False,
        "n": n,
        "record_count": format_record_count(n),
        "primary_kpis": compute_traffic_threshold_kpis(df),
        "secondary_kpis": [],
        "hero_chart": {
            "chart_id": "T-09",
            "title": "T-09 · Speed Collapse Threshold",
            "subtitle": "Record-level congestion × speed scatter",
            "caption": "Quadrant lines at 30 km/h and congestion 75 · critical overload zone annotated.",
            "fig": t09_speed_threshold.render(scatter, _traffic_cfg(state, "hero")),
        },
        "support_chart": {
            "chart_id": "T-10",
            "title": "T-10 · Public Transport Usage Comparison",
            "subtitle": "Congestion and speed by PT usage quartile",
            "caption": "Grouped congestion, speed, and incident means by public transport usage quartile.",
            "fig": t10_pt_decoupling.render(pt, _traffic_cfg(state, "supporting")),
        },
        "insight": "Speed collapse boundary appears near 22–30 km/h. PT usage quartiles show limited observable coupling in this dataset.",
        "nav_tab": 4,
        "nav_title": "Context And Distribution Patterns",
        "nav_desc": "Congestion distributions across roads, weather, and incidents.",
        "linked_controls": "traffic",
    }


def build_traffic_patterns_bundle(state: dict) -> dict:
    ctx = get_traffic_context()
    df = apply_traffic_filters(load_traffic_clean(), state)
    n = len(df)
    if n == 0:
        return {"empty": True, "n": 0}

    t11_df = apply_investigation_overlay_scope(df, "traffic", "T-11", state)
    profiles = get_road_distribution_profiles(t11_df)
    band_data = get_incident_congestion_bands(df)
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
            "chart_id": "T-11",
            "title": "T-11 · Road Congestion Distribution Profiles",
            "subtitle": "4×4 road distribution small multiples",
            "caption": "Sixteen histogram panels sorted by median congestion · dotted line marks per-road median.",
            "fig": t11_ridgeline.render(profiles, hero_cfg),
        },
        "support_chart": {
            "chart_id": "T-12",
            "title": "T-12 · Weather × Roadwork Heatmap",
            "subtitle": "Operational risk scheduling grid",
            "caption": "Mean congestion by weather condition and roadwork activity.",
            **lazy_fig_builder(
                lambda d=df, s=state: t12_weather_heatmap.render(
                    get_weather_roadwork_matrix(d),
                    _traffic_cfg(s, "supporting"),
                )
            ),
        },
        "secondary_charts": [
            {
                "chart_id": "T-08",
                "title": "T-08 · Incident Impact On Congestion",
                "subtitle": "Mean congestion by incident count band",
                "caption": "Step change between low and higher incident bands highlights congestion sensitivity to incidents.",
                "fig": t08_incident_cliff.render(band_data, _traffic_cfg(state, "supporting")),
            }
        ],
        "insight": "Right-skewed road distributions dominate critical overload corridors. Weather–roadwork intersections elevate mean congestion.",
        "nav_tab": 5,
        "nav_title": "Analytical Workspace",
        "nav_desc": "Dense multi-metric comparison (inherits global filters).",
        "linked_controls": "traffic",
    }


def build_aqi_crisis_bundle(state: dict) -> dict:
    df = apply_aqi_filters(load_aqi_clean(), state)
    n = len(df)
    if n == 0:
        return {"empty": True, "n": 0}

    primary, secondary = compute_aqi_crisis_kpis(df)
    days_above_120_rate = (df[COL_PM25] > 120).mean() * 100

    return {
        "empty": False,
        "n": n,
        "record_count": format_record_count(n),
        "primary_kpis": primary,
        "secondary_kpis": secondary,
        "severity_badge": "SEVERE" if days_above_120_rate > 50 else "WARNING",
        "hero_chart": {
            "chart_id": "A-01",
            "title": "A-01 · PM2.5 Burden and Category Mix",
            "subtitle": (
                "Filtered PM2.5 burden and category structure · "
                f"{days_above_120_rate:.1f}% days >120 µg/m³ · "
                f"peak {df[COL_PM25].max():.1f} µg/m³ · WHO guideline {AQI_PM25_WHO_ANNUAL} µg/m³"
            ),
            "caption": "Mean PM2.5 compared with WHO reference; bars show PM2.5-derived category distribution.",
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
            f"{days_above_120_rate:.1f}% of days exceed Very Poor (PM2.5 > 120 µg/m³). "
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

    a02_df = apply_investigation_overlay_scope(df, "aqi", "A-02", state)
    cal = get_daily_aqi_calendar(a02_df)
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
            "title": "A-02 · Weekly PM2.5 Calendar",
            "subtitle": "Weekly PM2.5 intensity grid · click a week to inspect context",
            "caption": "Week × year PM2.5 view; selected weeks populate local chart context.",
            "fig": a02_calendar_heatmap.render(cal, _aqi_cfg(state, "hero")),
            "fullscreen_key": "a02_calendar",
        },
        "support_chart": {
            "title": "A-04 · Monthly PM2.5 Heatmap",
            "subtitle": "Month × year mean PM2.5 rhythm",
            "caption": "Seasonal cycles and elevated-PM2.5 clusters at monthly resolution.",
            "fig": a04_monthly_variability.render(month_cal, _aqi_cfg(state, "supporting")),
        },
        "insight": "Winter months show persistent high-PM2.5 bands. Monsoon months exhibit partial atmospheric relief.",
        "nav_tab": 2,
        "nav_title": "Atmospheric Conditions",
        "nav_desc": "Compare pressure and visibility conditions with PM2.5.",
        "linked_controls": "aqi",
    }


def build_aqi_atmospheric_bundle(state: dict) -> dict:
    ctx = get_aqi_context()
    df = apply_aqi_filters(load_aqi_clean(), state)
    n = len(df)
    if n == 0:
        return {"empty": True, "n": 0}

    a06_df = apply_investigation_overlay_scope(df, "aqi", "A-06", state)
    hex_data = get_slp_vv_scatter(a06_df)
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
            "title": "A-06 · Pressure and Visibility PM2.5 Density",
            "subtitle": "Sea-level pressure × visibility density view",
            "caption": "Cell color encodes mean PM2.5 for days with similar pressure and visibility.",
            "fig": a06_stagnation_hexbin.render(hex_data, hero_cfg),
        },
        "support_chart": {
            "title": "A-07 · PM2.5 Category Weather Profile",
            "subtitle": "Normalized weather profiles by PM2.5 category",
            "caption": "Normalized 0–100 category profiles across six atmospheric axes.",
            "fig": a07_extreme_day_radar.render(profiles, _aqi_cfg(state, "supporting")),
        },
        "insight": "Seasonal drift reveals winter accumulation vs monsoon partial recovery. Link season focus to contextualize KPIs.",
        "nav_tab": 3,
        "nav_title": "Weather Indicators",
        "nav_desc": "Compare PM2.5 with temperature, pressure, and wind indicators.",
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
            "subtitle": "Distribution of daily PM2.5 by season",
            "caption": "KDE ridgelines show pollutant distribution shape — winter right-tail vs monsoon relief.",
            "fig": a03_seasonal_ridgeline.render(ridge, _aqi_cfg(state, "hero")),
        },
        "support_chart": {
            "title": "A-11 · Gust Ratio Quintile Check",
            "subtitle": "Mean PM2.5 by gust-ratio quintile",
            "caption": "Quintile means with uncertainty bands for checking gust-ratio relationships.",
            "fig": a11_gust_paradox.render(gust, _aqi_cfg(state, "supporting")),
        },
        "insight": "Winter ridgelines show heavier right tails. Gust-ratio bands provide a relationship check for the active filter scope.",
        "collapsed_chart": {
            "chart_id": "A-12",
            "title": "A-12 · Temperature Spread Bands",
            "subtitle": "Diurnal spread vs mean PM2.5",
            "caption": "Progressive disclosure · spread band grouped means.",
            **lazy_fig_builder(
                lambda d=df, s=state: a12_temp_spread.render(
                    get_temp_spread_bands(d),
                    _aqi_cfg(s, "supporting"),
                )
            ),
        },
        "nav_tab": 5,
        "nav_title": "Analytical Workspace",
        "nav_desc": "High-density weather and PM2.5 exploration environment.",
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
            "title": "A-08 · Minimum Temperature vs PM2.5",
            "subtitle": "Minimum temperature × PM2.5 × PM2.5 category",
            "caption": "Category-colored scatter; sampled for readability above 2,500 points.",
            "fig": a08_temperature_scatter.render(temp_scatter, _aqi_cfg(state, "hero")),
        },
        "support_chart": {
            "title": "A-09 · Pressure Band PM2.5 Comparison",
            "subtitle": "Sea-level pressure band × season grouped bars",
            "caption": "Grouped means compare PM2.5 across pressure bands and seasons.",
            "fig": a09_pressure_trigger.render(pressure, _aqi_cfg(state, "supporting")),
        },
        "insight": "Minimum temperature, pressure, and wind views compare PM2.5 against weather indicators without implying causality.",
        "collapsed_chart": {
            "chart_id": "A-10",
            "title": "A-10 · Wind Speed Band Comparison",
            "subtitle": "Wind band × season mean PM2.5",
            "caption": "Progressive disclosure · grouped means compare PM2.5 across wind-speed bands.",
            **lazy_fig_builder(
                lambda d=df, s=state: a10_wind_rescue.render(
                    get_wind_season_summary(d),
                    _aqi_cfg(s, "supporting"),
                )
            ),
        },
        "nav_tab": 4,
        "nav_title": "Distribution and Variability",
        "nav_desc": "Seasonal distributions and variability checks.",
        "linked_controls": "aqi",
    }


def build_aqi_lab_bundle(state: dict) -> dict:
    df = get_lab_dataset("aqi", state)
    n = len(df)
    if n == 0:
        return {"empty": True, "n": 0}

    a15_df = apply_investigation_overlay_scope(df, "aqi", "A-15", state)
    a13_df = apply_investigation_overlay_scope(df, "aqi", "A-13", state)
    pairplot = get_pairplot_dataset(a15_df)
    regimes = get_atmospheric_regime_data(a13_df)
    cfg = _aqi_cfg(state, "hero")
    cfg["fullscreen_key"] = "a15_pairplot"
    visible_cats = state.get("aqi_pairplot_visible_categories") or []
    if visible_cats:
        cfg["visible_categories"] = visible_cats
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
            "title": "A-15 · Weather Variable Pairplot",
            "subtitle": "7×7 weather and PM2.5 matrix · click scatter cells to emphasize a factor",
            "caption": "Histogram diagonals · category-encoded scatters · correlation fallback below 100 rows.",
            "fig": a15_pairplot.render(pairplot, cfg),
            "fullscreen_key": "a15_pairplot",
        },
        "support_chart": {
            "chart_id": "A-13",
            "interactive": True,
            "interaction_meta": {"regime_order": regime_order},
            "title": "A-13 · Rule-Based Atmospheric Regimes",
            "subtitle": "Regime scatter with rule-based classification · click trace to compare",
            "caption": "Rule-based baseline, low-visibility, dispersive, and pressure-regime comparison.",
            "fig": a13_atmospheric_states.render(regimes, _aqi_cfg(state, "supporting")),
        },
        "insight": "Pairplot and regime scatter support exploratory PM2.5 and weather comparison; regime labels are rule-based, not predictive.",
        "nav_tab": None,
        "linked_controls": "aqi",
        "is_lab": True,
        "lab_meta": {"categories": list(df[COL_AQI_CATEGORY].dropna().unique()) if COL_AQI_CATEGORY in df.columns else []},
        "collapsed_chart": {
            "chart_id": "A-14",
            "title": "A-14 · Season × Pressure Grid",
            "subtitle": "Mean PM2.5 heatmap (lazy load)",
            "caption": "Season × SLP band mean PM2.5 grid.",
            **lazy_fig_builder(
                lambda d=df, s=state: a14_season_pressure_grid.render(
                    get_season_slp_vv_grid(d),
                    _aqi_cfg(s, "supporting"),
                )
            ),
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
