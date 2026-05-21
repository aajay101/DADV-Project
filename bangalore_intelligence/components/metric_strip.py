"""Horizontal KPI metric row — primary and secondary tiers."""

import streamlit as st

from components.kpi_card import kpi_card


def metric_strip(
    metrics: list[dict],
    dashboard: str = "traffic",
    tier: str = "primary",
    loading: bool = False,
) -> None:
    if not metrics:
        return

    size = "normal" if tier == "primary" else "compact"
    cols = st.columns(len(metrics))
    for col, metric in zip(cols, metrics):
        with col:
            kpi_card(
                label=metric.get("label", ""),
                value=metric.get("value", "—"),
                delta=metric.get("delta"),
                delta_positive=metric.get("delta_positive"),
                gauge_percent=metric.get("gauge_percent"),
                severity=metric.get("severity", "neutral"),
                size=size,
                dashboard=dashboard,
                icon=metric.get("icon"),
                note=metric.get("note"),
                loading=loading,
                filtered_note=metric.get("filtered", False),
            )
