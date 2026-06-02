"""Production page renderer — uses data bundles, presentation-only layout."""

import streamlit as st

from components.chart_container import chart_container
from components.collapsible_section import collapsible_section
from components.hero_section import hero_section
from components.insight_card import insight_card
from components.lab_controls import render_aqi_lab_controls, render_traffic_lab_controls
from components.lab_header import lab_header
from components.layout.page_zones import (
    command_zone_close,
    command_zone_open,
    context_zone,
    investigation_zone_close,
    investigation_zone_open,
)
from components.layout.responsive import (
    get_column_split,
    should_collapse_chart,
)
from components.metric_strip import metric_strip
from components.interaction_education.empty_state_guidance import render_empty_state_guidance
from components.nav_card import nav_card
from components.section_header import section_header
from config.page_config import AQI_TABS, TRAFFIC_TABS
from components.detail_panel import detail_panel
from config.chart_defaults import chart_size_for
from filters.fullscreen import clear_fullscreen, get_active_fullscreen_key
from filters.interaction import render_investigation_chrome
from data_layer.lazy_charts import lazy_cache_key, resolve_chart_fig
from config.spacing import SECTION_GAP_SM
from utils.formatters import filter_snapshot_from_state
from utils.ui_blocks import render_html_block, render_spacer


def _enrich_chart_slot(slot: dict | None, role: str) -> dict:
    import re

    s = dict(slot or {})
    if not s.get("chart_id"):
        m = re.match(r"^([TA]-\d+)", s.get("title", "") or "")
        if m:
            s["chart_id"] = m.group(1)
    s.setdefault("chart_size", chart_size_for(s.get("chart_id"), role))
    return s


def _interaction_chart_kwargs(cfg: dict, page_key: str) -> dict:
    return {
        "chart_id": cfg.get("chart_id"),
        "chart_size": cfg.get("chart_size"),
        "interactive": bool(cfg.get("interactive")),
        "page_key": page_key,
        "interaction_meta": cfg.get("interaction_meta"),
        "selection_mode": cfg.get("selection_mode", "points"),
        "header_note": cfg.get("header_note"),
    }


def _iter_bundle_chart_slots(bundle: dict) -> list[tuple[str, dict]]:
    slots: list[tuple[str, dict]] = []
    for key in ("hero_chart", "support_chart"):
        cfg = bundle.get(key) or {}
        if cfg:
            slots.append((key, cfg))
    for idx, cfg in enumerate(bundle.get("secondary_charts") or []):
        if cfg:
            slots.append((f"secondary_charts_{idx}", cfg))
    collapsed = bundle.get("collapsed_chart") or {}
    if collapsed:
        slots.append(("collapsed_chart", collapsed))
    return slots


def _find_chart_cfg(bundle: dict, fullscreen_key: str) -> dict | None:
    for _, cfg in _iter_bundle_chart_slots(bundle):
        if cfg.get("fullscreen_key") == fullscreen_key:
            return cfg
    return None


def _render_fullscreen_chart(
    bundle: dict,
    dashboard: str,
    page_key: str,
    fullscreen_key: str,
) -> None:
    raw = _find_chart_cfg(bundle, fullscreen_key)
    if not raw:
        clear_fullscreen()
        st.warning("Fullscreen chart is not available on this page.")
        return
    cfg = _enrich_chart_slot(raw, "hero")

    if fullscreen_key == "t02_parcoords" and dashboard == "traffic":
        from dashboards.traffic.charts import t02_parallel_coords
        from data_layer.loaders import load_traffic_clean
        from data_layer.traffic_transforms import get_parallel_coords_records
        from filters.traffic_filters import apply_traffic_filters

        df = apply_traffic_filters(load_traffic_clean(), dict(st.session_state))
        cfg = dict(cfg)
        cfg["record_level"] = True
        cfg["fig"] = t02_parallel_coords.render(
            get_parallel_coords_records(df),
            {**cfg, "role": "hero"},
        )

    if st.button("← Return to page", key=f"buip_fs_exit_{dashboard}_{page_key}"):
        result = clear_fullscreen()
        from filters.transitions import request_rerun

        request_rerun(result, source=f"fullscreen_page_exit_{dashboard}_{page_key}")

    inv_meta = render_investigation_chrome(bundle, dashboard, page_key)
    filter_snapshot = filter_snapshot_from_state(st.session_state, dashboard)
    fs_fig = resolve_chart_fig(
        cfg,
        cache_key=lazy_cache_key(dashboard, page_key, cfg.get("chart_id"))
        if cfg.get("lazy")
        else None,
        dashboard=dashboard,
        page_key=page_key,
        chart_id=cfg.get("chart_id"),
    )
    chart_container(
        fig=fs_fig,
        title=cfg.get("title", ""),
        subtitle=cfg.get("subtitle"),
        caption=cfg.get("caption"),
        role=cfg.get("role", "hero"),
        dashboard=dashboard,
        fullscreen_key=fullscreen_key,
        record_count=bundle.get("record_count"),
        selection_label=inv_meta.get("selection_label"),
        state="default" if fs_fig is not None else "empty",
        active_filters=filter_snapshot,
        **_interaction_chart_kwargs(cfg, page_key),
    )


def render_production_page(
    dashboard: str,
    page_key: str,
    bundle: dict,
    is_lab: bool = False,
) -> None:
    tabs = TRAFFIC_TABS if dashboard == "traffic" else AQI_TABS
    tab = next((t for t in tabs if t["module"] == page_key), tabs[0])

    filter_snapshot = filter_snapshot_from_state(st.session_state, dashboard)

    active_fs = get_active_fullscreen_key(dashboard)
    if active_fs:
        _render_fullscreen_chart(bundle, dashboard, page_key, active_fs)
        return

    if is_lab:
        lab_header(dashboard=dashboard)
        lab_meta = bundle.get("lab_meta") or {}
        if dashboard == "traffic":
            render_traffic_lab_controls(
                lab_meta.get("available_areas", []),
                lab_meta.get("top_stress_areas", []),
                lab_meta.get("baseline_areas", []),
            )
        else:
            render_aqi_lab_controls(lab_meta.get("categories"))

    if bundle.get("empty"):
        st.warning("No records match the current filter selection. Adjust filters to restore analytics.")
        render_empty_state_guidance("valid_empty_result")
        return

    prefix = "traffic" if dashboard == "traffic" else "aqi"
    data_stale = bool(st.session_state.get(f"{prefix}_data_stale", False))

    command_zone_open(dashboard)
    hero_section(
        title=tab["title"],
        subtitle=tab["subtitle"],
        severity_badge=bundle.get("severity_badge"),
        dashboard=dashboard,
    )
    metric_strip(
        bundle.get("primary_kpis", []),
        dashboard=dashboard,
        tier="primary",
        data_stale=data_stale,
    )
    if bundle.get("secondary_kpis"):
        metric_strip(
            bundle.get("secondary_kpis", []),
            dashboard=dashboard,
            tier="secondary",
            data_stale=data_stale,
        )
    command_zone_close()

    investigation_zone_open(dashboard)
    with st.container(border=True):
        render_html_block(
            '<span class="buip-analytical-modules-panel-marker" aria-hidden="true"></span>'
        )
        section_header(
            "Analytical Modules",
            zone="investigation",
            dashboard=dashboard,
        )

        hero_cfg = _enrich_chart_slot(bundle.get("hero_chart"), "hero")
        support_cfg = _enrich_chart_slot(bundle.get("support_chart"), "supporting")
        hero_col, support_col = st.columns(get_column_split("hero_support"))

        def _fig_for_slot(slot: dict, role: str) -> object | None:
            cid = slot.get("chart_id")
            cache = (
                lazy_cache_key(dashboard, page_key, cid)
                if slot.get("lazy") and cid
                else None
            )
            return resolve_chart_fig(
                slot,
                cache_key=cache,
                dashboard=dashboard,
                page_key=page_key,
                chart_id=cid,
            )

        inv_meta = render_investigation_chrome(bundle, dashboard, page_key)
        render_spacer(SECTION_GAP_SM)
        sel = inv_meta.get("selection_label")
        hero_fig_resolved = _fig_for_slot(hero_cfg, "hero")
        if hero_fig_resolved is not None:
            hero_state = "default"
        elif hero_cfg.get("lazy"):
            hero_state = "loading"
        else:
            hero_state = "empty"
        chart_kw = _interaction_chart_kwargs

        collapse_hero = (
            page_key == "p5_hidden_patterns"
            and dashboard == "traffic"
            and hero_cfg.get("chart_id") == "T-11"
            and should_collapse_chart("t11_ridgeline")
        )

        def _render_hero_chart():
            chart_container(
                fig=_fig_for_slot(hero_cfg, "hero"),
                title=hero_cfg.get("title", ""),
                subtitle=hero_cfg.get("subtitle"),
                caption=hero_cfg.get("caption"),
                role="hero",
                dashboard=dashboard,
                fullscreen_key=hero_cfg.get("fullscreen_key"),
                record_count=bundle.get("record_count"),
                selection_label=sel,
                state=hero_state,
                active_filters=filter_snapshot,
                **chart_kw(hero_cfg, page_key),
            )

        with hero_col:
            if collapse_hero:
                collapsible_section(
                    label="▶ T-11 · Congestion distribution matrix (tablet layout)",
                    key=f"{page_key}_hero_collapsed",
                    default_expanded=False,
                    content_fn=_render_hero_chart,
                    dashboard=dashboard,
                )
            else:
                _render_hero_chart()

        collapse_support = (
            is_lab
            and support_cfg.get("chart_id") == "T-02"
            and should_collapse_chart("t02_parcoords")
        )

        def _render_support_chart():
            support_fig = _fig_for_slot(support_cfg, "supporting")
            chart_container(
                fig=support_fig,
                title=support_cfg.get("title", ""),
                subtitle=support_cfg.get("subtitle"),
                caption=support_cfg.get("caption"),
                role="supporting",
                dashboard=dashboard,
                fullscreen_key=support_cfg.get("fullscreen_key"),
                record_count=bundle.get("record_count"),
                selection_label=sel,
                state="default" if support_fig is not None else "empty",
                active_filters=filter_snapshot,
                reveal_stagger=True,
                **chart_kw(support_cfg, page_key),
            )

        with support_col:
            if collapse_support:
                collapsible_section(
                    label="▶ T-02 · Area Traffic Profile (tablet layout)",
                    key=f"{page_key}_support_collapsed",
                    default_expanded=False,
                    content_fn=_render_support_chart,
                    dashboard=dashboard,
                )
            else:
                _render_support_chart()

        secondary_slots = [
            _enrich_chart_slot(slot, "supporting")
            for slot in (bundle.get("secondary_charts") or [])
        ]
        if secondary_slots:
            st.divider()
            section_header(
                "Extended Analysis",
                zone="investigation",
                dashboard=dashboard,
            )
            sec_cols = st.columns(len(secondary_slots) if len(secondary_slots) < 3 else [1, 1])
            for idx, sec_cfg in enumerate(secondary_slots):
                col = sec_cols[idx % len(sec_cols)]

                def _render_secondary(cfg=sec_cfg, column=col):
                    with column:
                        sec_fig = _fig_for_slot(cfg, "supporting")
                        sec_state = (
                            "loading"
                            if cfg.get("lazy") and sec_fig is None
                            else ("default" if sec_fig is not None else "empty")
                        )
                        chart_container(
                            fig=sec_fig,
                            title=sec_cfg.get("title", ""),
                            subtitle=sec_cfg.get("subtitle"),
                            caption=sec_cfg.get("caption"),
                            role="supporting",
                            dashboard=dashboard,
                            fullscreen_key=sec_cfg.get("fullscreen_key"),
                            record_count=bundle.get("record_count"),
                            selection_label=sel,
                            state=sec_state,
                            active_filters=filter_snapshot,
                            reveal_stagger=True,
                            **chart_kw(sec_cfg, page_key),
                        )

                _render_secondary()

        detail = bundle.get("detail_panel")
        if detail:
            detail_panel(
                title=detail.get("title", "Selection"),
                metrics=detail.get("metrics", []),
                notes=detail.get("notes"),
                visible=True,
                dashboard=detail.get("dashboard", dashboard),
                state="selected",
            )

        collapsed_cfg = _enrich_chart_slot(bundle.get("collapsed_chart") or {}, "supporting")

        def _render_collapsed():
            collapsed_fig = _fig_for_slot(collapsed_cfg, "supporting")
            chart_container(
                fig=collapsed_fig,
                title=collapsed_cfg.get("title", "Secondary analytical module"),
                subtitle=collapsed_cfg.get("subtitle"),
                caption=collapsed_cfg.get("caption"),
                role="supporting",
                dashboard=dashboard,
                fullscreen_key=collapsed_cfg.get("fullscreen_key"),
                record_count=bundle.get("record_count"),
                selection_label=sel,
                state="default" if collapsed_fig is not None else "empty",
                active_filters=filter_snapshot,
                **_interaction_chart_kwargs(collapsed_cfg, page_key),
            )

        if collapsed_cfg.get("fig_builder") or collapsed_cfg.get("fig") or collapsed_cfg.get("title"):
            collapsible_section(
                label=collapsed_cfg.get("label", "▶ SECONDARY MODULE · Progressive disclosure"),
                key=f"{page_key}_collapsed",
                default_expanded=False,
                content_fn=_render_collapsed,
                dashboard=dashboard,
            )
    investigation_zone_close()

    context_zone(dashboard)
    insight_card(
        heading="What This Means" if dashboard == "aqi" else "Operational Interpretation",
        body=bundle.get("insight", ""),
        severity=bundle.get("insight_severity", "neutral"),
        collapsible=True,
        default_expanded=False,
        dashboard=dashboard,
    )

    nav_tab = bundle.get("nav_tab")
    if nav_tab is not None:
        nav_card(
            label="Continue analysis" if dashboard == "aqi" else "Investigate further",
            destination_title=bundle.get("nav_title", ""),
            destination_description=bundle.get("nav_desc", ""),
            tab_index=nav_tab,
            dashboard=dashboard,
        )
