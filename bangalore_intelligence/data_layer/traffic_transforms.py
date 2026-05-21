"""Traffic derived datasets and KPI aggregations — cached."""

import numpy as np
import pandas as pd
import streamlit as st

from config.data_config import (
    COL_AREA,
    COL_CAPACITY,
    COL_CONGESTION,
    COL_DATE,
    COL_INCIDENTS,
    COL_PEDESTRIAN,
    COL_PT_USAGE,
    COL_ROAD,
    COL_ROADWORK,
    COL_SIGNAL,
    COL_SPEED,
    COL_TRAFFIC_VOL,
    COL_WEATHER,
    CONGESTION_STATE_BOUNDS,
    CONGESTION_STATES,
    TRAFFIC_AREA_COORDS,
    TRAFFIC_CAPACITY_CRITICAL_PCT,
    TRAFFIC_CONGESTION_CRITICAL,
    TRAFFIC_CONGESTION_WARNING,
    TRAFFIC_INCIDENTS_CRITICAL,
    TRAFFIC_SPEED_CRITICAL,
    TRAFFIC_SPEED_WARNING,
)


def _congestion_state(series: pd.Series) -> pd.Series:
    return pd.cut(
        series,
        bins=CONGESTION_STATE_BOUNDS,
        labels=CONGESTION_STATES,
        include_lowest=True,
    ).astype(str)


@st.cache_data(show_spinner=False)
def get_area_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(COL_AREA, as_index=False)
        .agg(
            mean_congestion=(COL_CONGESTION, "mean"),
            mean_speed=(COL_SPEED, "mean"),
            total_incidents=(COL_INCIDENTS, "sum"),
            mean_capacity=(COL_CAPACITY, "mean"),
            mean_pedestrian=(COL_PEDESTRIAN, "mean"),
            mean_pt_usage=(COL_PT_USAGE, "mean"),
            mean_signal=(COL_SIGNAL, "mean"),
            record_count=(COL_CONGESTION, "count"),
        )
        .round(1)
    )


@st.cache_data(show_spinner=False)
def get_incident_congestion_bands(df: pd.DataFrame) -> pd.DataFrame:
    capped = df.copy()
    capped["incident_band"] = capped[COL_INCIDENTS].clip(0, 5)
    return (
        capped.groupby("incident_band", as_index=False)
        .agg(mean_congestion=(COL_CONGESTION, "mean"), record_count=(COL_CONGESTION, "count"))
        .sort_values("incident_band")
    )


def compute_traffic_command_kpis(df: pd.DataFrame) -> list[dict]:
    """Build KPI card configs from filtered traffic data."""
    if df.empty:
        return []

    mean_cong = df[COL_CONGESTION].mean()
    cap_pct = (df[COL_CAPACITY] >= 99.5).mean() * 100
    incidents = int(df[COL_INCIDENTS].sum())
    mean_speed = df[COL_SPEED].mean()

    def sev_cong(v):
        if v >= TRAFFIC_CONGESTION_CRITICAL:
            return "critical"
        if v >= TRAFFIC_CONGESTION_WARNING:
            return "warning"
        return "safe"

    def sev_cap(p):
        if p >= TRAFFIC_CAPACITY_CRITICAL_PCT:
            return "critical"
        if p >= 25:
            return "warning"
        return "safe"

    def sev_inc(n):
        if n >= TRAFFIC_INCIDENTS_CRITICAL:
            return "critical"
        if n >= 200:
            return "warning"
        return "neutral"

    def sev_spd(v):
        if v <= TRAFFIC_SPEED_CRITICAL:
            return "critical"
        if v <= TRAFFIC_SPEED_WARNING:
            return "warning"
        return "safe"

    primary = [
        {
            "label": "System Congestion Index",
            "value": f"{mean_cong:.1f}",
            "severity": sev_cong(mean_cong),
            "gauge_percent": float(mean_cong),
        },
        {
            "label": "Capacity Saturation Rate",
            "value": f"{cap_pct:.1f}%",
            "severity": sev_cap(cap_pct),
            "gauge_percent": float(cap_pct),
        },
        {
            "label": "Active Incidents",
            "value": f"{incidents:,}",
            "severity": sev_inc(incidents),
        },
        {
            "label": "Average Speed",
            "value": f"{mean_speed:.1f} km/h",
            "severity": sev_spd(mean_speed),
        },
    ]
    secondary = [
        {
            "label": "Pedestrian Exposure",
            "value": f"{df[COL_PEDESTRIAN].mean():.0f} avg",
            "severity": "neutral",
        },
        {
            "label": "Public Transport Usage",
            "value": f"{df[COL_PT_USAGE].mean():.1f}%",
            "severity": "neutral",
        },
        {
            "label": "Signal Compliance",
            "value": f"{df[COL_SIGNAL].mean():.1f}%",
            "severity": "warning" if df[COL_SIGNAL].mean() < 70 else "neutral",
        },
        {
            "label": "Environmental Impact",
            "value": f"{df['environmental_impact'].mean():.1f}",
            "severity": "warning" if df["environmental_impact"].mean() > 140 else "neutral",
        },
    ]
    return primary, secondary


def format_record_count(n: int) -> str:
    return f"n = {n:,} records"


@st.cache_data(show_spinner=False)
def get_parallel_coords_data(df: pd.DataFrame) -> pd.DataFrame:
    """Area-level multivariate summary for T-02."""
    return get_area_summary(df)


@st.cache_data(show_spinner=False)
def get_monthly_stream_data(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly mean congestion by area for T-03."""
    if df.empty:
        return pd.DataFrame()
    tmp = df.copy()
    tmp["month"] = tmp[COL_DATE].dt.to_period("M").astype(str)
    return (
        tmp.groupby(["month", COL_AREA], as_index=False)
        .agg(mean_congestion=(COL_CONGESTION, "mean"))
        .sort_values("month")
    )


@st.cache_data(show_spinner=False)
def get_area_hotspot_map(df: pd.DataFrame) -> pd.DataFrame:
    """Area centroids with congestion and incident intensity for T-05."""
    if df.empty:
        return pd.DataFrame()
    agg = (
        df.groupby(COL_AREA, as_index=False)
        .agg(
            mean_congestion=(COL_CONGESTION, "mean"),
            total_incidents=(COL_INCIDENTS, "sum"),
            mean_speed=(COL_SPEED, "mean"),
            record_count=(COL_CONGESTION, "count"),
        )
    )
    agg["lat"] = agg[COL_AREA].map(lambda a: TRAFFIC_AREA_COORDS.get(a, (12.97, 77.59))[0])
    agg["lon"] = agg[COL_AREA].map(lambda a: TRAFFIC_AREA_COORDS.get(a, (12.97, 77.59))[1])
    agg["pressure_index"] = (agg["mean_congestion"] * 0.7 + agg["total_incidents"] * 0.03).round(1)
    return agg


@st.cache_data(show_spinner=False)
def get_road_mobility_exclusion(df: pd.DataFrame) -> pd.DataFrame:
    """Per-road active mobility penalty vs system baseline (T-07 diverging bar)."""
    stats = get_road_stats(df)
    if stats.empty:
        return stats
    baseline = float(df[COL_CONGESTION].mean())
    stats = stats.copy()
    stats["exclusion_delta"] = (stats["mean_congestion"] - baseline).round(1)
    if COL_PEDESTRIAN in df.columns:
        ped = (
            df.groupby([COL_AREA, COL_ROAD], as_index=False)[COL_PEDESTRIAN]
            .mean()
            .rename(columns={COL_PEDESTRIAN: "mean_pedestrian"})
        )
        stats = stats.merge(ped, on=[COL_AREA, COL_ROAD], how="left")
        stats["exclusion_delta"] = (
            stats["mean_congestion"]
            - baseline
            + stats["mean_pedestrian"].fillna(0) * 0.04
        ).round(1)
    return stats.sort_values("exclusion_delta", ascending=True)


@st.cache_data(show_spinner=False)
def get_congestion_transition_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Daily area mean congestion state transitions for T-07."""
    if df.empty:
        return pd.DataFrame()
    daily = (
        df.groupby([COL_DATE, COL_AREA], as_index=False)
        .agg(mean_congestion=(COL_CONGESTION, "mean"))
        .sort_values([COL_AREA, COL_DATE])
    )
    daily["state"] = _congestion_state(daily["mean_congestion"])
    transitions: dict[tuple[str, str], int] = {}
    for _, grp in daily.groupby(COL_AREA):
        states = grp["state"].tolist()
        for i in range(len(states) - 1):
            key = (states[i], states[i + 1])
            transitions[key] = transitions.get(key, 0) + 1
    rows = [
        {"from_state": k[0], "to_state": k[1], "count": v}
        for k, v in transitions.items()
    ]
    if not rows:
        return pd.DataFrame()
    mat = pd.DataFrame(rows)
    pivot = mat.pivot_table(index="from_state", columns="to_state", values="count", fill_value=0)
    for s in CONGESTION_STATES:
        if s not in pivot.index:
            pivot.loc[s] = 0
        if s not in pivot.columns:
            pivot[s] = 0
    return pivot.loc[CONGESTION_STATES, CONGESTION_STATES]


def compute_traffic_temporal_kpis(df: pd.DataFrame) -> list[dict]:
    if df.empty:
        return []
    monthly = df.copy()
    monthly["month"] = monthly[COL_DATE].dt.to_period("M")
    by_month = monthly.groupby("month")[COL_CONGESTION].mean()
    peak = by_month.max()
    low = by_month.min()
    trend = by_month.iloc[-6:].mean() - by_month.iloc[:6].mean() if len(by_month) >= 12 else 0
    vol = by_month.std() / by_month.mean() * 100 if by_month.mean() else 0
    return [
        {"label": "Peak Month Congestion", "value": f"{peak:.1f}", "severity": "critical"},
        {"label": "Lowest Month", "value": f"{low:.1f}", "severity": "safe"},
        {
            "label": "Trend Direction",
            "value": "▲ Rising" if trend > 2 else ("▼ Easing" if trend < -2 else "→ Stable"),
            "severity": "warning" if trend > 2 else "neutral",
        },
        {"label": "Volatility Index", "value": f"{vol:.1f}%", "severity": "neutral"},
    ]


def compute_traffic_spatial_kpis(
    df: pd.DataFrame,
    focus_area: str | None = None,
    focus_road: str | None = None,
) -> list[dict]:
    if df.empty:
        return []
    if focus_road:
        stats = get_road_stats(df)
        row = stats[stats[COL_ROAD] == focus_road]
        if not row.empty:
            r = row.iloc[0]
            return [
                {"label": "Investigation", "value": focus_road, "severity": "warning", "filtered": True},
                {"label": "Congestion", "value": f"{r['mean_congestion']:.1f}", "severity": "critical"},
                {"label": "Capacity", "value": f"{r['mean_capacity']:.1f}%", "severity": "warning"},
                {"label": "Area", "value": str(r[COL_AREA]), "severity": "neutral"},
            ]
    view = df[df[COL_AREA] == focus_area] if focus_area else df
    road = view.groupby(COL_ROAD)[COL_CONGESTION].mean()
    critical = int((road >= 90).sum())
    baseline = int((road < 60).sum())
    worst_area = view.groupby(COL_AREA)[COL_CONGESTION].mean().idxmax() if not focus_area else focus_area
    return [
        {"label": "Critical Overload Roads", "value": str(critical), "severity": "critical"},
        {"label": "Focus Area" if focus_area else "Worst Area", "value": str(worst_area), "severity": "critical"},
        {"label": "Baseline Roads", "value": str(baseline), "severity": "safe"},
        {"label": "Mean Road Congestion", "value": f"{road.mean():.1f}", "severity": "warning"},
    ]


def _normalize_series_to_stress(series: pd.Series, higher_is_worse: bool = True) -> pd.Series:
    """Scale values to 0–100 stress index (100 = worst in sample)."""
    if series.empty or series.nunique() <= 1:
        return pd.Series(50.0, index=series.index)
    lo, hi = series.min(), series.max()
    if hi == lo:
        return pd.Series(50.0, index=series.index)
    norm = (series - lo) / (hi - lo) * 100
    return norm if higher_is_worse else (100 - norm)


@st.cache_data(show_spinner=False)
def get_weekly_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Day-of-week congestion distribution for T-04 violin/box."""
    if df.empty:
        return pd.DataFrame()
    return (
        df.groupby("day_of_week", as_index=False)
        .agg(
            mean_congestion=(COL_CONGESTION, "mean"),
            median_congestion=(COL_CONGESTION, "median"),
            q25=(COL_CONGESTION, lambda s: s.quantile(0.25)),
            q75=(COL_CONGESTION, lambda s: s.quantile(0.75)),
            record_count=(COL_CONGESTION, "count"),
        )
        .assign(
            day_of_week=lambda d: pd.Categorical(
                d["day_of_week"],
                categories=[
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ],
                ordered=True,
            )
        )
        .sort_values("day_of_week")
    )


@st.cache_data(show_spinner=False)
def get_weekly_violin_records(df: pd.DataFrame) -> pd.DataFrame:
    """Record-level day-of-week congestion for T-04 violin."""
    if df.empty:
        return pd.DataFrame()
    order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    out = df[["day_of_week", COL_CONGESTION]].dropna()
    out["day_of_week"] = pd.Categorical(out["day_of_week"], categories=order, ordered=True)
    return out.sort_values("day_of_week")


@st.cache_data(show_spinner=False)
def get_road_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Road-level operational metrics for T-05 scatter and T-11."""
    if df.empty:
        return pd.DataFrame()
    stats = (
        df.groupby([COL_AREA, COL_ROAD], as_index=False)
        .agg(
            mean_congestion=(COL_CONGESTION, "mean"),
            std_congestion=(COL_CONGESTION, "std"),
            mean_speed=(COL_SPEED, "mean"),
            mean_capacity=(COL_CAPACITY, "mean"),
            total_incidents=(COL_INCIDENTS, "sum"),
            mean_traffic_vol=(COL_TRAFFIC_VOL, "mean"),
            pct_at_max_capacity=("at_max_capacity", "mean"),
            record_count=(COL_CONGESTION, "count"),
        )
        .round(2)
    )
    stats["flow_instability_index"] = (
        stats["std_congestion"] / stats["mean_congestion"].replace(0, np.nan)
    ).fillna(0).round(2)
    return stats


@st.cache_data(show_spinner=False)
def get_area_environmental_burden(df: pd.DataFrame) -> pd.DataFrame:
    """Hierarchical area × road environmental burden for T-06 treemap."""
    if df.empty:
        return pd.DataFrame()
    return (
        df.groupby([COL_AREA, COL_ROAD], as_index=False)
        .agg(
            environmental_impact=("environmental_impact", "mean"),
            mean_congestion=(COL_CONGESTION, "mean"),
            record_count=(COL_CONGESTION, "count"),
        )
        .sort_values("environmental_impact", ascending=False)
    )


@st.cache_data(show_spinner=False)
def get_congestion_speed_scatter(df: pd.DataFrame, max_points: int = 2500) -> pd.DataFrame:
    """Record-level congestion vs speed for T-09 (sampled if large)."""
    if df.empty:
        return pd.DataFrame()
    cols = [COL_AREA, COL_ROAD, COL_CONGESTION, COL_SPEED, COL_INCIDENTS]
    out = df[cols].dropna()
    if len(out) > max_points:
        out = out.sample(max_points, random_state=42)
    return out.reset_index(drop=True)


@st.cache_data(show_spinner=False)
def get_pt_quartile_summary(df: pd.DataFrame) -> pd.DataFrame:
    """PT usage quartile vs congestion outcomes for T-10."""
    if df.empty:
        return pd.DataFrame()
    tmp = df.copy()
    tmp["pt_quartile"] = pd.qcut(
        tmp[COL_PT_USAGE].rank(method="first"),
        q=4,
        labels=["Q1 (Low PT)", "Q2", "Q3", "Q4 (High PT)"],
    )
    return (
        tmp.groupby("pt_quartile", as_index=False)
        .agg(
            mean_congestion=(COL_CONGESTION, "mean"),
            mean_speed=(COL_SPEED, "mean"),
            mean_incidents=(COL_INCIDENTS, "mean"),
            mean_capacity=(COL_CAPACITY, "mean"),
            record_count=(COL_CONGESTION, "count"),
        )
        .sort_values("pt_quartile")
    )


@st.cache_data(show_spinner=False)
def get_road_congestion_distributions(df: pd.DataFrame) -> pd.DataFrame:
    """Long-format road congestion values for T-11 ridgeline."""
    if df.empty:
        return pd.DataFrame()
    roads = (
        df.groupby(COL_ROAD)[COL_CONGESTION]
        .mean()
        .sort_values(ascending=False)
        .head(16)
        .index
    )
    sub = df[df[COL_ROAD].isin(roads)][[COL_ROAD, COL_AREA, COL_CONGESTION]]
    sub = sub.rename(columns={COL_CONGESTION: "value"})
    sub["median_cong"] = sub.groupby(COL_ROAD)["value"].transform("median")
    return sub.sort_values(["median_cong", COL_ROAD], ascending=[False, True])


@st.cache_data(show_spinner=False)
def get_weather_roadwork_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Weather × roadwork mean congestion and incidents for T-12."""
    if df.empty:
        return pd.DataFrame()
    return (
        df.groupby([COL_WEATHER, COL_ROADWORK], as_index=False)
        .agg(
            mean_congestion=(COL_CONGESTION, "mean"),
            mean_incidents=(COL_INCIDENTS, "mean"),
            record_count=(COL_CONGESTION, "count"),
        )
        .sort_values([COL_WEATHER, COL_ROADWORK])
    )


@st.cache_data(show_spinner=False)
def get_monthly_bubble_data(df: pd.DataFrame) -> pd.DataFrame:
    """Month × area aggregates for T-15 bubble matrix."""
    if df.empty:
        return pd.DataFrame()
    tmp = df.copy()
    tmp["month"] = tmp[COL_DATE].dt.to_period("M").astype(str)
    agg = (
        tmp.groupby(["month", COL_AREA], as_index=False)
        .agg(
            mean_congestion=(COL_CONGESTION, "mean"),
            total_incidents=(COL_INCIDENTS, "sum"),
            pct_at_max_capacity=("at_max_capacity", "mean"),
            record_count=(COL_CONGESTION, "count"),
        )
    )
    agg["pct_at_max_capacity"] = (agg["pct_at_max_capacity"] * 100).round(1)
    return agg


@st.cache_data(show_spinner=False)
def get_traffic_volume_congestion(df: pd.DataFrame, max_points: int = 3000) -> pd.DataFrame:
    """Traffic volume vs congestion for T-14 hexbin."""
    if df.empty:
        return pd.DataFrame()
    out = df[[COL_TRAFFIC_VOL, COL_CONGESTION, COL_AREA]].dropna()
    if len(out) > max_points:
        out = out.sample(max_points, random_state=42)
    return out.reset_index(drop=True)


RADAR_METRIC_SPECS = [
    ("mean_congestion", True),
    ("total_incidents", True),
    ("mean_capacity", True),
    ("mean_speed", False),
    ("mean_pedestrian", True),
    ("mean_signal", False),
]


@st.cache_data(show_spinner=False)
def get_radar_normalized_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Area-level 0–100 normalized radar axes for T-13."""
    base = get_area_summary(df)
    if base.empty:
        return pd.DataFrame()
    rows = []
    for _, row in base.iterrows():
        entry = {COL_AREA: row[COL_AREA]}
        for col, higher_worse in RADAR_METRIC_SPECS:
            if col not in row:
                continue
            entry[col] = float(
                _normalize_series_to_stress(
                    base.set_index(COL_AREA)[col], higher_is_worse=higher_worse
                ).loc[row[COL_AREA]]
            )
        rows.append(entry)
    return pd.DataFrame(rows)


def compute_traffic_threshold_kpis(df: pd.DataFrame) -> list[dict]:
    if df.empty:
        return []
    below_30 = (df[COL_SPEED] < 30).mean() * 100
    above_75 = (df[COL_CONGESTION] >= 75).mean() * 100
    return [
        {"label": "Speed < 30 km/h Share", "value": f"{below_30:.1f}%", "severity": "critical"},
        {"label": "Congestion ≥ 75 Share", "value": f"{above_75:.1f}%", "severity": "warning"},
        {"label": "Mean Speed", "value": f"{df[COL_SPEED].mean():.1f} km/h", "severity": "warning"},
        {"label": "Threshold Crossings", "value": f"{int((df[COL_CONGESTION] >= 90).sum()):,}", "severity": "critical"},
    ]


def compute_traffic_patterns_kpis(df: pd.DataFrame) -> list[dict]:
    if df.empty:
        return []
    roads = df[COL_ROAD].nunique()
    skew_roads = int((df.groupby(COL_ROAD)[COL_CONGESTION].mean() >= 85).sum())
    return [
        {"label": "Roads Profiled", "value": str(roads), "severity": "neutral"},
        {"label": "High-Skew Roads", "value": str(skew_roads), "severity": "critical"},
        {"label": "Mean Congestion", "value": f"{df[COL_CONGESTION].mean():.1f}", "severity": "warning"},
        {"label": "Weather Regimes", "value": str(df[COL_WEATHER].nunique()), "severity": "neutral"},
    ]
