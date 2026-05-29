# Dashboard Understandability Improvements

Status: consolidated explainability and understandability summary. This document combines the existing Phase 5A knowledge-map foundation with the new metadata upgrades needed for a more useful future explainability system.

This is still a planning and documentation artifact only. It does not implement UI, reducers, filters, overlays, cache invalidation, chart logic, or runtime AI.

## 1. Current Foundation

The dashboard already has a strong analytical runtime:

- Reducer-governed state transitions.
- Dependency-aware chart invalidation.
- Global filters separated from temporary investigation overlays.
- Overlay-aware and visual-focus-aware chart routing.
- Lazy chart cache governance.
- Runtime observability and recovery tooling.
- Central chart IDs and page bundle metadata.
- Existing titles, subtitles, captions, KPI labels, insight cards, and empty states.

The Phase 5A knowledge map already extracted the core explainability foundation:

- Complete visual inventory for traffic charts `T-01` to `T-15`.
- Complete visual inventory for AQI charts `A-01` to `A-15`.
- Visualization methodology for each chart.
- Analytical terminology definitions.
- Page-level insight extraction.
- KPI semantic extraction.
- Interaction and overlay semantics.
- Empty-state knowledge.
- Future registry structure proposal.
- Streamlit feasibility analysis.
- UX direction for guided analytical storytelling.

## 2. Core Product Direction

The dashboard should evolve from an interactive chart collection into a guided analytical decision-support platform.

The explainability layer should help users understand:

- What they are seeing.
- Why the visualization exists.
- Why that chart type was chosen.
- What the metric or term means.
- What analytical implication the chart suggests.
- How filters affect the view.
- How investigation overlays differ from persistent global filters.
- What users should do next when a result matters.
- What limitations or interpretation risks apply.

The system should not become:

- A documentation dump.
- A generic tooltip layer.
- A tutorial simulator.
- A popup-heavy interface.
- A runtime AI generation system.

It should feel contextual, calm, analytical, and progressively disclosed.

## 3. Existing Visual Knowledge Summary

### Traffic Dashboard

| Area | Key Visuals | What They Help Users Understand |
| --- | --- | --- |
| Network overview | `T-01`, KPIs | Current congestion burden and area-level pressure concentration. |
| Temporal behavior | `T-03`, `T-04`, `T-15` | Monthly rhythm, weekday distribution, and recurring area-month stress. |
| Spatial operations | `T-05`, `T-06`, `T-07` | Road priority, environmental burden, and pedestrian-adjusted road pressure. |
| Threshold analytics | `T-08`, `T-09`, `T-10` | Incident sensitivity, speed collapse, and public transport relationship checks. |
| Pattern discovery | `T-11`, `T-12`, `T-14` | Road distribution skew, weather-roadwork risk, and volume-congestion density. |
| Advanced comparison | `T-02`, `T-13` | Multi-axis area fingerprints and focused stress-profile comparison. |

High-explanation traffic visuals:

- `T-02` Parallel Coordinates Matrix.
- `T-05` Road Management Priority Quadrant.
- `T-09` Speed Collapse Threshold.
- `T-13` Area Stress Profile.

### AQI Dashboard

| Area | Key Visuals | What They Help Users Understand |
| --- | --- | --- |
| PM2.5 burden | `A-01`, KPIs | Mean pollution, category mix, severe days, and WHO guideline context. |
| Temporal persistence | `A-02`, `A-04`, `A-05` | Weekly/monthly pollution clusters and sustained rolling exposure. |
| Seasonal distribution | `A-03` | Winter right-tail behavior and monsoon relief. |
| Atmospheric context | `A-06`, `A-07`, `A-13`, `A-14` | Visibility, pressure, categories, and rule-based atmospheric regimes. |
| Weather relationships | `A-08`, `A-09`, `A-10`, `A-11`, `A-12` | Temperature, pressure, wind, gust, and diurnal spread relationship checks. |
| Advanced exploration | `A-15` | Multivariate weather and PM2.5 pairwise relationships. |

High-explanation AQI visuals:

- `A-06` Pressure and Visibility PM2.5 Density.
- `A-13` Rule-Based Atmospheric Regimes.
- `A-15` Weather Variable Pairplot.

## 4. Existing Interaction Semantics To Preserve

The explainability layer must clearly explain and preserve these rules:

- Global filters are persistent dataset-scope controls.
- Global filters combine naturally through dataframe filtering.
- Investigation overlays are temporary chart-click drilldowns.
- Investigation overlays do not mutate persistent global filter widgets.
- `global_filter_mode` and `investigation_mode` cannot coexist.
- Chart clicks in global-filter mode are cosmetic-only.
- Clear Focus clears visual focus and investigation overlays while preserving global filters.
- Empty datasets are valid analytical results and must not auto-clear filters.

This distinction is one of the most important user education targets:

```text
Global filters = persistent dataset scope.
Investigation overlay = temporary clicked-context scope.
Visual focus = highlighting and selection memory.
```

## 5. New Metadata Upgrades

The future explainability registry should add the following fields.

| Upgrade | Field | Purpose |
| --- | --- | --- |
| Explanation complexity | `complexity_level` | Prevent every explanation from being equally dense. |
| Common misinterpretations | `misinterpretation_warning` | Prevent causal overreach, overlay confusion, and threshold misuse. |
| Why users should care | `decision_relevance` | Connect descriptive analytics to decision-support value. |
| Confidence and limits | `limitations` | Explain sampling, sparse data, fallback charts, and descriptive-only methods. |
| Term graph | `related_terms` | Support semantic navigation between concepts. |
| User type targeting | `audience` | Tune explanations for general, analyst, operations, or developer users. |
| When to use this visual | `when_to_use` | Tell users which analytical question a chart answers. |
| Related visuals | `related_visuals` | Create guided exploration paths across charts. |
| Rollout priority | `priority` | Focus authoring effort on the charts that need explanations most. |
| Empty-state variants | `empty_state_variants` | Tailor no-data messages to the actual situation. |

## 6. Proposed Registry Fields

Future `ExplainabilityEntry` records should include:

```python
ExplainabilityEntry(
    surface_id="T-05",
    dashboard="traffic",
    surface_type="chart",
    title="Road Management Priority Quadrant",
    complexity_level="intermediate",
    priority="high",
    audience=["operations", "analyst"],
    what_this_shows="Roads positioned by congestion and capacity pressure.",
    why_this_visualization="A quadrant scatter exposes two operational risk dimensions at once.",
    when_to_use="Use this chart to prioritize roads for operational attention.",
    interpretation_guide=[
        "Upper-right points indicate critical overload.",
        "Lower-left points indicate baseline roads.",
    ],
    decision_relevance="Roads with high congestion and high capacity pressure may require corridor-level intervention.",
    misinterpretation_warning="Quadrant position is descriptive; it does not prove the root cause of road stress.",
    limitations=[
        "Sparse road records can make quadrant placement less stable.",
        "Capacity and congestion are summarized from the active filtered scope.",
    ],
    key_terms=["congestion", "capacity saturation", "critical overload"],
    related_terms=["speed collapse", "threshold crossings", "baseline roads"],
    related_visuals=["T-07", "T-09", "T-11"],
    filter_impact="Global filters narrow the dataset before this chart is built.",
    overlay_behavior="Investigation overlay can focus related charts by road or area.",
    interaction_help="Click a road to activate temporary investigation focus when no global filters are active.",
    empty_state_variants=["no_rows_from_filters", "no_overlay_match", "chart_unavailable"],
    source_refs=[
        "data_layer/page_bundles.py",
        "dashboards/traffic/charts/t05_quadrant_scatter.py",
        "filters/performance.py",
    ],
)
```

These fields are presentation-layer metadata only. They must not affect reducers, invalidation, cache keys, chart computation, overlay rules, or filter behavior.

## 7. Complexity Levels

| Level | Meaning | Examples | UX Behavior Later |
| --- | --- | --- | --- |
| `basic` | Direct metric, ranking, grouped bar, or simple trend. | `T-01`, `T-03`, `A-01`, `A-05` | Short default explanation. |
| `intermediate` | Requires comparison, thresholds, distributions, or multi-factor interpretation. | `T-05`, `T-09`, `T-12`, `A-06`, `A-09` | Structured explanation with warning and decision relevance. |
| `advanced` | Multivariate, matrix, regime, radar, pairplot, or expert exploratory view. | `T-02`, `T-13`, `A-13`, `A-15` | Collapse deeper methodology by default; provide richer optional detail. |

Why this matters:

- Beginner users should not be forced through dense statistical explanation.
- Complex charts should not be explained with shallow generic copy.
- The UI can progressively disclose methodology and limitations based on chart complexity.

## 8. Priority Levels

| Priority | Meaning | Initial Chart Targets |
| --- | --- | --- |
| `high` | Needs strong explanation before rollout because it is complex, risky to misread, or central to decisions. | `T-02`, `T-05`, `T-09`, `T-13`, `A-06`, `A-13`, `A-15` |
| `medium` | Useful explanation, but not as urgent. | `T-03`, `T-04`, `T-06`, `T-07`, `T-08`, `T-11`, `T-12`, `T-14`, `T-15`, `A-02`, `A-03`, `A-04`, `A-05`, `A-07`, `A-08`, `A-11`, `A-14` |
| `low` | Simple enough for shorter copy or later enrichment. | `T-01`, `T-10`, `A-01`, `A-09`, `A-10`, `A-12` |

Priority should guide authoring and rollout effort. It should not imply analytical importance alone; it reflects how much explanation is needed for safe interpretation.

## 9. Common Misinterpretation Warnings

| Context | Warning |
| --- | --- |
| Weather relationships | A weather variable associated with lower or higher PM2.5 does not prove that variable alone caused the pollution change. |
| Correlation and pairplots | Pairwise correlation is descriptive and can hide confounding factors, seasonal structure, and nonlinear behavior. |
| Investigation overlay | A temporary investigation overlay does not change the dashboard's persistent global filter scope. |
| Global filters | Empty results from compound filters are valid; the system should not automatically clear selections. |
| Threshold charts | Crossing a threshold identifies risk conditions, not a complete causal diagnosis. |
| Volatility index | High volatility means instability across time, not necessarily consistently high congestion. |
| Radar charts | Larger radar area suggests broader stress but should not be treated as a predictive score. |
| Atmospheric regimes | Rule-based regimes are descriptive labels, not machine-learning predictions. |
| Sparse categories | Small record counts can make category means or comparisons unstable. |
| Sampled scatter plots | Sampling improves readability but may hide rare points. |

## 10. Decision Relevance

| Analytical Area | Decision Relevance |
| --- | --- |
| Persistent congestion growth | May indicate infrastructure strain requiring corridor-level intervention. |
| Critical overload roads | Helps operations teams identify roads needing priority attention. |
| Speed collapse | Reveals conditions where mobility degrades from slow traffic into operational failure. |
| Weather-roadwork congestion | Supports scheduling and mitigation planning around risky operational combinations. |
| Environmental burden | Connects traffic pressure to environmental impact and corridor-level externalities. |
| PM2.5 persistence | Indicates recurring exposure windows, not just isolated pollution spikes. |
| Stagnation traps | May signal recurring public-health exposure periods under poor dispersion conditions. |
| Seasonal PM2.5 behavior | Helps separate structural seasonal risk from short-term anomalies. |
| Atmospheric regimes | Gives analysts a structured way to compare weather-condition groups. |
| Pairplot exploration | Helps analysts decide which weather-PM2.5 relationships deserve deeper study. |

## 11. Term Graph And Related Terms

Terms should not remain isolated definitions. The future registry should support cross-linking.

| Term | Related Terms |
| --- | --- |
| Active filter scope | global filters, compound filtering, empty state |
| Investigation overlay | visual focus, Clear Focus, overlay-aware chart |
| Visual focus | investigation overlay, selected chart context, chart click |
| System Congestion Index | mean congestion, peak month congestion, volatility index |
| Capacity Saturation Rate | critical overload, road priority quadrant, speed collapse |
| Active Incidents | incident impact, threshold crossings, congestion sensitivity |
| Speed collapse | congestion threshold, mean speed, critical overload |
| Critical overload zone | capacity saturation, speed collapse, baseline roads |
| Volatility Index | trend direction, monthly congestion, temporal instability |
| PM2.5 | AQI category, severe share, WHO guideline context |
| Pollution persistence | rolling mean, severe days, PM2.5 burden |
| Stagnation trap | low visibility, PM2.5, pressure regime |
| Sea-level pressure | pressure band, atmospheric regime, season-pressure grid |
| Wind band | dispersion, gust ratio, PM2.5 relationship |
| Rule-based atmospheric regime | stagnation trap, dispersive regime, low visibility |
| Pairplot | correlation, scatter matrix, multivariate relationship |

## 12. Audience Targeting

| Audience | Explanation Style |
| --- | --- |
| `general` | Plain-language explanation, minimal jargon, practical interpretation. |
| `operations` | Focus on intervention, scheduling, thresholds, hotspots, and risk. |
| `analyst` | Include methodology, limitations, correlation cautions, and related visuals. |
| `developer` | Explain state semantics, overlays, dependency routing, and runtime behavior. |

Suggested chart audiences:

- `T-01`, `A-01`: `general`, `operations`.
- `T-05`, `T-09`, `T-12`: `operations`, `analyst`.
- `T-02`, `T-13`, `A-13`, `A-15`: `analyst`.
- Runtime/debug surfaces: `developer`.

## 13. When To Use This Visual

| Visual Group | When To Use |
| --- | --- |
| KPI cards | Use for a quick read of current filtered-state severity. |
| Ranking bars | Use to identify where pressure is concentrated. |
| Time-series lines | Use to compare temporal movement and trend direction. |
| Heatmaps | Use to find dense clusters, repeated hotspots, or two-dimensional risk combinations. |
| Scatter thresholds | Use to identify records or roads crossing operational risk boundaries. |
| Quadrants | Use to classify entities across two decision dimensions. |
| Treemaps | Use to understand contribution and hierarchy. |
| Distribution charts | Use to compare spread, tails, and consistency. |
| Radar charts | Use to compare multi-axis profiles for a small number of entities. |
| Pairplots | Use for exploratory multivariate relationship discovery. |
| Regime scatter | Use to compare interpretable atmospheric condition groups. |

## 14. Related Visual Navigation

Future popovers should guide users toward related analysis rather than leaving each chart isolated.

| Starting Visual | Related Visuals | Guided Flow |
| --- | --- | --- |
| `T-01` | `T-03`, `T-05`, `T-15` | From system pressure to temporal and spatial diagnosis. |
| `T-02` | `T-13`, `T-05`, `T-07` | From multi-axis area profile to road and stress details. |
| `T-03` | `T-04`, `T-15` | From monthly trend to distribution and area-month hotspot. |
| `T-05` | `T-07`, `T-09`, `T-11` | From road priority to pedestrian pressure, speed collapse, and distribution profile. |
| `T-09` | `T-05`, `T-08`, `T-10` | From speed-collapse risk to road priority, incident impact, and PT usage. |
| `T-12` | `T-08`, `T-03` | From weather-roadwork risk to incidents and temporal rhythm. |
| `T-13` | `T-02`, `T-15` | From area stress profile to multi-axis fingerprints and temporal heatmap. |
| `A-01` | `A-05`, `A-02`, `A-04` | From PM2.5 burden to persistence and temporal clusters. |
| `A-05` | `A-02`, `A-03`, `A-04` | From daily persistence to weekly, seasonal, and monthly structure. |
| `A-06` | `A-13`, `A-14`, `A-07` | From pressure-visibility density to regimes, season-pressure grid, and category profiles. |
| `A-08` | `A-09`, `A-10`, `A-12` | From temperature relationship to pressure, wind, and spread comparisons. |
| `A-13` | `A-06`, `A-14`, `A-15` | From regimes to meteorological density, grid context, and multivariate exploration. |
| `A-15` | `A-06`, `A-08`, `A-13` | From pairwise exploration to focused weather and regime views. |

## 15. Empty-State Explanation Variants

Future empty-state messages should be tailored to the actual reason no visual is shown.

| Variant | Meaning | User Message Intent | Suggested Action | State Rule |
| --- | --- | --- | --- | --- |
| `no_rows_from_filters` | Global filters produce zero matching rows. | Your selected filters are valid, but no records match them together. | Adjust or reset filters if this was not intended. | Preserve filters. |
| `no_overlay_match` | Temporary investigation overlay has no matching chart records. | The clicked context has no data for this chart. | Clear Focus or inspect another related chart. | Preserve global filters and overlay until user clears focus. |
| `chart_unavailable` | Chart builder cannot produce a figure. | This chart cannot currently render from the available data. | Keep current scope; inspect another chart or reload if persistent. | Do not mutate analytical state. |
| `lazy_chart_not_hydrated` | Lazy chart has not loaded or failed safely. | The chart is deferred or recovered from a builder failure. | Retry, switch chart, or use recovery tooling in developer mode. | Recovery should remain chart-cache scoped. |
| `dataset_unavailable` | Governed dataset is missing, stale, or not loaded. | The issue is data availability, not user filter intent. | Restore/import governed datasets, then reload. | Do not clear filters as a workaround. |
| `export_no_data` | Export requested with no exportable rows. | There is currently no data to export for this scope. | Adjust filters or restore data before exporting. | Do not alter filters. |

## 16. Implementation Principles For Later

When this becomes code, the explainability layer should:

- Live in presentation-only registry/components.
- Use chart IDs and KPI labels as lookup keys.
- Use `st.popover`, `st.expander`, or `st.dialog` depending on complexity.
- Keep advanced methodology collapsed by default.
- Surface warnings for correlation, thresholds, overlays, sampling, and sparse data.
- Support related visual navigation.
- Support term cross-linking.
- Support audience-specific detail levels.
- Never trigger analytical transitions just because help is opened.
- Never mutate filters, overlays, reducers, caches, or chart data.

Safe future integration points:

- `components/chart_container.py::chart_container()`
- `components/kpi_card.py::kpi_card()`
- `components/metric_strip.py::metric_strip()`
- `components/page_production.py::render_production_page()`
- `components/empty_state.py::empty_state()`
- `filters/interaction.py::render_investigation_chrome()`
- `components/filter_panel.py::filter_panel()`

Avoid implementing explainability inside:

- Reducers.
- Invalidation logic.
- Lazy chart cache logic.
- Data loaders.
- Chart transforms.
- Global filter synchronization.

## 17. Final Summary

The current dashboard already has the technical maturity needed for explainability: stable state governance, chart IDs, overlay semantics, dependency routing, captions, KPIs, and empty states.

The next maturity step is not more runtime architecture. It is user understanding.

The improved explainability system should add:

- Complexity-aware explanations.
- Common misinterpretation warnings.
- Decision relevance.
- Confidence and limitation notes.
- Term relationships.
- Audience targeting.
- When-to-use guidance.
- Related visual navigation.
- Explainability priority levels.
- Empty-state variants.

Together, these turn the explainability layer from simple chart help into a guided analytical understanding system.
