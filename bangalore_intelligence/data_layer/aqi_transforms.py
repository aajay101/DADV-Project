"""AQI derived datasets and KPI aggregations — cached."""

import pandas as pd
import streamlit as st

from config.data_config import (
    AQI_CATEGORIES,
    AQI_PM25_SEVERE,
    AQI_PM25_VERY_POOR,
    AQI_PM25_WHO_ANNUAL,
    COL_AQI_CATEGORY,
    COL_DATE,
    COL_H,
    COL_PM25,
    COL_SEASON,
    COL_SLP,
    COL_T,
    COL_TM,
    COL_V,
    COL_VV,
)


@st.cache_data(show_spinner=False)
def get_aqi_summary_stats(df: pd.DataFrame) -> dict:
    if df.empty:
        return {}
    days_above_120_mask = df[COL_PM25] > AQI_PM25_VERY_POOR
    return {
        "days_above_120_rate": days_above_120_mask.mean() * 100,
        "peak_pm25": df[COL_PM25].max(),
        "annual_mean_pm25": df[COL_PM25].mean(),
        "severe_days": int((df[COL_PM25] > AQI_PM25_SEVERE).sum()),
        "category_counts": df[COL_AQI_CATEGORY].value_counts().to_dict(),
    }


@st.cache_data(show_spinner=False)
def get_daily_aqi_calendar(df: pd.DataFrame) -> pd.DataFrame:
    """Visualization-ready calendar grid rows."""
    if df.empty:
        return pd.DataFrame()
    cal = df[[COL_DATE, COL_PM25, COL_AQI_CATEGORY, "year", "week"]].copy()
    cal["dow"] = cal[COL_DATE].dt.dayofweek
    cal["month"] = cal[COL_DATE].dt.month
    return cal


def compute_aqi_crisis_kpis(df: pd.DataFrame) -> tuple[list[dict], list[dict]]:
    if df.empty:
        return [], []
    stats = get_aqi_summary_stats(df)

    primary = [
        {
            "label": "Days Above 120 ug/m3",
            "value": f"{stats['days_above_120_rate']:.1f}% of days",
            "severity": "critical",
        },
        {
            "label": "Peak PM2.5",
            "value": f"{stats['peak_pm25']:.1f} µg/m³",
            "severity": "critical",
        },
        {
            "label": "Mean PM2.5 in View",
            "value": f"{stats['annual_mean_pm25']:.1f} µg/m³",
            "severity": "warning",
            "note": f"WHO Annual Guideline: {AQI_PM25_WHO_ANNUAL} µg/m³",
        },
        {
            "label": "Severe Days Count",
            "value": f"{stats['severe_days']} days",
            "severity": "critical",
        },
    ]
    secondary = [
        {"label": "WHO Guideline Context", "value": "5 ug/m3 annual", "severity": "warning"},
        {
            "label": "Dominant Category",
            "value": (
                max(counts, key=counts.get)
                if (counts := stats.get("category_counts", {}))
                else "—"
            ),
            "severity": "warning",
        },
        {
            "label": "Seasons Covered",
            "value": str(df[COL_SEASON].nunique()),
            "severity": "neutral",
        },
        {
            "label": "Filtered Days",
            "value": f"{len(df):,}",
            "severity": "neutral",
        },
    ]
    return primary, secondary


POLLUTANT_COLS = [COL_PM25, COL_T, COL_TM, COL_VV, COL_V, COL_SLP, COL_H]


@st.cache_data(show_spinner=False)
def get_pollutant_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Pearson correlation matrix for A-03."""
    if df.empty:
        return pd.DataFrame()
    return df[POLLUTANT_COLS].corr().round(2)


@st.cache_data(show_spinner=False)
def get_temporal_aqi_calendar(df: pd.DataFrame) -> pd.DataFrame:
    """Month × year mean PM2.5 grid for A-04."""
    if df.empty:
        return pd.DataFrame()
    tmp = df.copy()
    tmp["month"] = tmp[COL_DATE].dt.month
    tmp["year"] = tmp[COL_DATE].dt.year
    return (
        tmp.groupby(["year", "month"], as_index=False)
        .agg(mean_pm25=(COL_PM25, "mean"), dominant_category=(COL_AQI_CATEGORY, lambda s: s.mode().iloc[0]))
        .sort_values(["year", "month"])
    )


@st.cache_data(show_spinner=False)
def get_seasonal_drift_series(df: pd.DataFrame) -> pd.DataFrame:
    """Year × season mean PM2.5 for A-06."""
    if df.empty:
        return pd.DataFrame()
    tmp = df.copy()
    tmp["year"] = tmp[COL_DATE].dt.year
    return (
        tmp.groupby([COL_SEASON, "year"], as_index=False)
        .agg(mean_pm25=(COL_PM25, "mean"))
        .sort_values([COL_SEASON, "year"])
    )


@st.cache_data(show_spinner=False)
def get_aqi_category_transition_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Day-to-day AQI category transitions for A-08."""
    if df.empty:
        return pd.DataFrame()
    ordered = df.sort_values(COL_DATE)
    cats = ordered[COL_AQI_CATEGORY].tolist()
    transitions: dict[tuple[str, str], int] = {}
    for i in range(len(cats) - 1):
        key = (cats[i], cats[i + 1])
        transitions[key] = transitions.get(key, 0) + 1
    rows = [{"from_cat": k[0], "to_cat": k[1], "count": v} for k, v in transitions.items()]
    if not rows:
        return pd.DataFrame()
    mat = pd.DataFrame(rows)
    pivot = mat.pivot_table(index="from_cat", columns="to_cat", values="count", fill_value=0)
    for c in AQI_CATEGORIES:
        if c not in pivot.index:
            pivot.loc[c] = 0
        if c not in pivot.columns:
            pivot[c] = 0
    return pivot.loc[AQI_CATEGORIES, AQI_CATEGORIES]


def compute_aqi_patterns_kpis(df: pd.DataFrame) -> list[dict]:
    if df.empty:
        return []
    corr = df[POLLUTANT_COLS].corr()[COL_PM25].drop(COL_PM25).abs().idxmax()
    return [
        {"label": "Strongest Weather Correlation", "value": corr, "severity": "warning"},
        {"label": "Mean PM2.5", "value": f"{df[COL_PM25].mean():.1f} µg/m³", "severity": "warning"},
        {"label": "Seasons", "value": str(df[COL_SEASON].nunique()), "severity": "neutral"},
        {"label": "Days Analyzed", "value": f"{len(df):,}", "severity": "neutral"},
    ]


def compute_aqi_atmospheric_kpis(df: pd.DataFrame, focus_season: str | None = None) -> list[dict]:
    if df.empty:
        return []
    view = df[df[COL_SEASON] == focus_season] if focus_season else df
    trap = ((view[COL_VV] < 1.5) & (view[COL_PM25] > 120)).sum()
    return [
        {"label": "Stagnation Trap Days", "value": str(int(trap)), "severity": "critical"},
        {"label": "Low VV + High PM2.5", "value": f"{trap / max(len(view), 1) * 100:.1f}%", "severity": "critical"},
        {"label": "Mean VV", "value": f"{view[COL_VV].mean():.2f} km", "severity": "neutral"},
        {"label": "Season Focus", "value": focus_season or "All", "severity": "neutral"},
    ]


def compute_aqi_weather_kpis(df: pd.DataFrame) -> list[dict]:
    if df.empty:
        return []
    unstable = int((df[COL_AQI_CATEGORY] != df[COL_AQI_CATEGORY].shift()).sum())
    return [
        {"label": "Category Transitions", "value": str(unstable), "severity": "warning"},
        {"label": "Category Change Rate", "value": f"{unstable / max(len(df), 1) * 100:.1f}%", "severity": "warning"},
        {"label": "Dominant Category", "value": df[COL_AQI_CATEGORY].mode().iloc[0], "severity": "neutral"},
        {"label": "Severe Share", "value": f"{(df[COL_PM25] > 250).mean() * 100:.1f}%", "severity": "critical"},
    ]


PAIRPLOT_VARS = [COL_T, COL_TM, COL_SLP, COL_H, COL_VV, COL_V, COL_PM25]


@st.cache_data(show_spinner=False)
def get_persistence_series(df: pd.DataFrame) -> pd.DataFrame:
    """Daily PM2.5 with rolling average for A-05."""
    if df.empty:
        return pd.DataFrame()
    return df[[COL_DATE, COL_PM25, "rolling_7d_pm25", COL_AQI_CATEGORY]].sort_values(COL_DATE)


@st.cache_data(show_spinner=False)
def get_seasonal_pm25_ridgeline(df: pd.DataFrame) -> pd.DataFrame:
    """Long-format PM2.5 by season for A-03 ridgeline."""
    if df.empty:
        return pd.DataFrame()
    order = ["Winter", "Spring", "Monsoon", "Post-Monsoon"]
    sub = df[[COL_SEASON, COL_PM25]].rename(columns={COL_PM25: "value"})
    sub[COL_SEASON] = pd.Categorical(sub[COL_SEASON], categories=order, ordered=True)
    sub["season_median"] = sub.groupby(COL_SEASON)["value"].transform("median")
    return sub.sort_values(["season_median", COL_SEASON], ascending=[False, True])


@st.cache_data(show_spinner=False)
def get_aqi_category_profiles(df: pd.DataFrame) -> pd.DataFrame:
    """Normalized meteorological profiles by AQI category for A-07 radar."""
    if df.empty:
        return pd.DataFrame()
    metrics = [COL_T, COL_TM, COL_H, COL_VV, COL_V, COL_SLP]
    prof = df.groupby(COL_AQI_CATEGORY)[metrics].mean()
    for col in metrics:
        lo, hi = prof[col].min(), prof[col].max()
        if hi > lo:
            prof[col] = (prof[col] - lo) / (hi - lo) * 100
        else:
            prof[col] = 50.0
    prof = prof.round(1).reset_index()
    prof = prof.set_index(COL_AQI_CATEGORY).reindex(AQI_CATEGORIES).fillna(50.0).reset_index()
    return prof


@st.cache_data(show_spinner=False)
def get_slp_season_summary(df: pd.DataFrame) -> pd.DataFrame:
    """SLP band × season mean PM2.5 for A-09."""
    if df.empty:
        return pd.DataFrame()
    return (
        df.groupby(["slp_band", COL_SEASON], as_index=False)
        .agg(mean_pm25=(COL_PM25, "mean"), record_count=(COL_PM25, "count"))
        .sort_values(["slp_band", COL_SEASON])
    )


@st.cache_data(show_spinner=False)
def get_wind_season_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Wind band × season mean PM2.5 for A-10."""
    if df.empty:
        return pd.DataFrame()
    return (
        df.groupby(["wind_band", COL_SEASON], as_index=False)
        .agg(mean_pm25=(COL_PM25, "mean"), record_count=(COL_PM25, "count"))
        .sort_values(["wind_band", COL_SEASON])
    )


@st.cache_data(show_spinner=False)
def get_gust_ratio_quintiles(df: pd.DataFrame) -> pd.DataFrame:
    """Gust ratio quintile PM2.5 for A-11."""
    if df.empty:
        return pd.DataFrame()
    tmp = df.copy()
    tmp["gust_quintile"] = pd.qcut(
        tmp["gust_ratio"].rank(method="first"),
        q=5,
        labels=[f"Q{i}" for i in range(1, 6)],
        duplicates="drop",
    )
    agg = (
        tmp.groupby("gust_quintile", as_index=False)
        .agg(
            mean_pm25=(COL_PM25, "mean"),
            std_pm25=(COL_PM25, "std"),
            record_count=(COL_PM25, "count"),
        )
    )
    agg["ci_low"] = agg["mean_pm25"] - agg["std_pm25"].fillna(0)
    agg["ci_high"] = agg["mean_pm25"] + agg["std_pm25"].fillna(0)
    return agg


@st.cache_data(show_spinner=False)
def get_temp_spread_bands(df: pd.DataFrame) -> pd.DataFrame:
    """Temperature spread band summaries for A-12."""
    if df.empty:
        return pd.DataFrame()
    tmp = df.copy()
    tmp["spread_band"] = pd.cut(
        tmp["temp_spread"],
        bins=[-1, 5, 10, 15, 100],
        labels=["≤5°C", "5–10°C", "10–15°C", ">15°C"],
    )
    return (
        tmp.groupby("spread_band", as_index=False)
        .agg(
            mean_pm25=(COL_PM25, "mean"),
            median_pm25=(COL_PM25, "median"),
            record_count=(COL_PM25, "count"),
        )
        .sort_values("spread_band")
    )


@st.cache_data(show_spinner=False)
def get_atmospheric_regime_data(df: pd.DataFrame) -> pd.DataFrame:
    """VV vs PM2.5 with atmospheric regime labels for A-13."""
    if df.empty:
        return pd.DataFrame()
    tmp = df[[COL_VV, COL_PM25, COL_SLP, COL_H, COL_SEASON]].copy()
    tmp["regime"] = "Baseline"
    tmp.loc[(tmp[COL_VV] < 1.5) & (tmp[COL_PM25] > 120), "regime"] = "Stagnation Trap"
    tmp.loc[(tmp[COL_VV] >= 3) & (tmp[COL_PM25] < 90), "regime"] = "Dispersive Relief"
    tmp.loc[(tmp[COL_SLP] < 1005) & (tmp[COL_PM25] > 150), "regime"] = "Pressure Lock"
    return tmp


@st.cache_data(show_spinner=False)
def get_season_slp_vv_grid(df: pd.DataFrame) -> pd.DataFrame:
    """Season × SLP band mean PM2.5 for A-14."""
    if df.empty:
        return pd.DataFrame()
    return (
        df.groupby([COL_SEASON, "slp_band"], as_index=False)
        .agg(mean_pm25=(COL_PM25, "mean"), record_count=(COL_PM25, "count"))
        .sort_values([COL_SEASON, "slp_band"])
    )


@st.cache_data(show_spinner=False)
def get_pairplot_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Meteorological columns + category for A-15."""
    if df.empty:
        return pd.DataFrame()
    cols = PAIRPLOT_VARS + [COL_AQI_CATEGORY]
    return df[cols].dropna().reset_index(drop=True)


@st.cache_data(show_spinner=False)
def get_slp_vv_scatter(df: pd.DataFrame) -> pd.DataFrame:
    """SLP × VV × PM2.5 for A-06 hexbin when used as stagnation view."""
    if df.empty:
        return pd.DataFrame()
    return df[[COL_SLP, COL_VV, COL_PM25, COL_SEASON]].dropna().reset_index(drop=True)


@st.cache_data(show_spinner=False)
def get_temp_pm25_scatter(df: pd.DataFrame, max_points: int = 2500) -> pd.DataFrame:
    """Minimum temperature vs PM2.5 for A-08 scatter."""
    if df.empty:
        return pd.DataFrame()
    out = df[[COL_TM, COL_PM25, COL_AQI_CATEGORY]].dropna()
    if len(out) > max_points:
        out = out.sample(max_points, random_state=42)
    return out.reset_index(drop=True)


def compute_aqi_lab_kpis(df: pd.DataFrame) -> list[dict]:
    if df.empty:
        return []
    return [
        {"label": "Met Variables", "value": str(len(PAIRPLOT_VARS)), "severity": "neutral"},
        {"label": "Days", "value": f"{len(df):,}", "severity": "neutral"},
        {"label": "Categories", "value": str(df[COL_AQI_CATEGORY].nunique()), "severity": "neutral"},
        {"label": "Exploration Mode", "value": "Active", "severity": "info"},
    ]
