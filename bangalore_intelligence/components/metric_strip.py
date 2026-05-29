"""Horizontal KPI metric row — primary and secondary tiers."""

import streamlit as st

from components.kpi_card import kpi_card
from components.layout.responsive import should_collapse_secondary_kpis, should_hide_kpi_gauges
from config.spacing import KPI_STRIP_AFTER_SECONDARY, KPI_STRIP_BOTTOM
from utils.ui_blocks import render_spacer


def metric_strip(
    metrics: list[dict],
    dashboard: str = "traffic",
    tier: str = "primary",
    loading: bool = False,
    data_stale: bool = False,
) -> None:
    if not metrics:
        return
    if tier == "secondary" and should_collapse_secondary_kpis():
        return

    size = "normal" if tier == "primary" else "compact"
    hide_gauges = should_hide_kpi_gauges()
    kpi_state = "stale" if data_stale else "default"
    cols = st.columns(len(metrics), gap="small")
    for col, metric in zip(cols, metrics):
        with col:
            kpi_card(
                label=metric.get("label", ""),
                value=metric.get("value", "—"),
                delta=metric.get("delta"),
                delta_positive=metric.get("delta_positive"),
                gauge_percent=None if hide_gauges else metric.get("gauge_percent"),
                severity=metric.get("severity", "neutral"),
                size=size,
                dashboard=dashboard,
                icon=metric.get("icon"),
                note=metric.get("note"),
                loading=loading,
                filtered_note=metric.get("filtered", False),
                state=kpi_state,
                explainability_id=metric.get("explainability_id") or metric.get("id") or metric.get("label"),
            )
    bottom = KPI_STRIP_BOTTOM if tier == "primary" else KPI_STRIP_AFTER_SECONDARY
    render_spacer(bottom)
