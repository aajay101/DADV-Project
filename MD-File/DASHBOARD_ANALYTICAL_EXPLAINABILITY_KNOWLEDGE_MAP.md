# Dashboard Analytical Explainability Knowledge Map

Status: Phase 5A semantic extraction complete. This document is the source-grounded knowledge map for a future explainability layer. It does not implement UI, reducers, invalidation, runtime AI, or chart behavior.

## Source Inventory

This extraction is based on the current dashboard codebase:

- `data_layer/page_bundles.py`: page composition, chart titles, subtitles, captions, page insights, record-count context.
- `dashboards/traffic/charts/*`: traffic chart methodology and Plotly visual types.
- `dashboards/aqi/charts/*`: AQI chart methodology and Plotly visual types.
- `data_layer/traffic_transforms.py`: traffic KPI generation, threshold logic, derived analytical tables.
- `data_layer/aqi_transforms.py`: AQI KPI generation, PM2.5 methods, atmospheric regimes, category transitions.
- `filters/performance.py`: chart dependency registry, global filter dependencies, visual-focus dependencies, overlay dependencies, chart-local dependencies.
- `filters/interaction.py`, `filters/interaction_mode.py`, `filters/investigation_scope.py`: chart-click semantics, investigation overlays, global-filter/investigation exclusivity.
- `components/chart_container.py`, `components/kpi_card.py`, `components/metric_strip.py`, `components/page_production.py`, `components/empty_state.py`: presentation surfaces and future explainability insertion points.

## 1. Complete Visual Inventory

All analytical charts depend on dashboard global filters. Overlay awareness and visual-focus awareness are taken from `CHART_DEPENDENCY_REGISTRY`.

### Traffic Visual Registry

| ID | Title | Subtitle | Caption | Visual Type | Builder Source | Dependent Filters | Overlay Aware |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T-01 | Network Congestion And Area Ranking | System congestion gauge and area severity bars | Click an area bar to set chart focus; use Apply as filter to scope all pages. | KPI-style scorecard plus area bar ranking | `dashboards/traffic/charts/t01_scorecard.py::render` | Traffic global filters | No |
| T-02 | Parallel Coordinates Matrix | Eight-axis area performance profile | Area-level z-score profile; open fullscreen for sampled record-level parcoords. | Multi-axis line profile / fullscreen parallel coordinates | `dashboards/traffic/charts/t02_parallel_coords.py::render` | Traffic global filters, visual focus, investigation overlay | Yes |
| T-03 | Monthly Congestion Trend By Area | Network-wide monthly congestion rhythm / Monthly congestion pressure by area | Monthly mean congestion by area in the active filter scope. | Multi-series line chart | `dashboards/traffic/charts/t03_stream_graph.py::render` | Traffic global filters | No |
| T-04 | Weekly Violin Distribution | Day-of-week congestion spread | Violin traces per weekday; boxplot fallback below 30 records per day. | Violin / box distribution chart | `dashboards/traffic/charts/t04_violin_weekly.py::render` | Traffic global filters | No |
| T-05 | Road Management Priority Quadrant | Congestion x capacity classification; click a road to focus charts | Quadrant zones classify roads: baseline, constrained flow, capacity margin, critical overload. | Quadrant scatter plot | `dashboards/traffic/charts/t05_quadrant_scatter.py::render` | Traffic global filters, visual focus, investigation overlay | Yes |
| T-06 | Environmental Burden Treemap | Area x road impact hierarchy | Hierarchical burden reveals which corridors drive environmental impact within the filter scope. | Treemap | `dashboards/traffic/charts/t06_burden_treemap.py::render` | Traffic global filters, visual focus, investigation overlay | Yes |
| T-07 | Pedestrian-Adjusted Road Pressure | Congestion deviation from system baseline by road | Bars show each road's congestion deviation from the filtered-scope baseline, pedestrian exposure included. | Deviation bar chart | `dashboards/traffic/charts/t07_mobility_exclusion.py::render` | Traffic global filters, visual focus, investigation overlay | Yes |
| T-08 | Incident Impact On Congestion | Mean congestion by incident count band | Step change between low and higher incident bands highlights congestion sensitivity to incidents. | Step line with markers | `dashboards/traffic/charts/t08_incident_cliff.py::render` | Traffic global filters | No |
| T-09 | Speed Collapse Threshold | Record-level congestion x speed scatter | Quadrant lines at 30 km/h and congestion 75; critical overload zone annotated. | Threshold scatter plot | `dashboards/traffic/charts/t09_speed_threshold.py::render` | Traffic global filters, visual focus, investigation overlay | Yes |
| T-10 | Public Transport Usage Comparison | Congestion and speed by PT usage quartile | Grouped congestion, speed, and incident means by public transport usage quartile. | Grouped bars plus line | `dashboards/traffic/charts/t10_pt_decoupling.py::render` | Traffic global filters | No |
| T-11 | Road Congestion Distribution Profiles | 4x4 road distribution small multiples | Sixteen histogram panels sorted by median congestion; dotted line marks per-road median. | Small-multiple histograms / distribution profiles | `dashboards/traffic/charts/t11_ridgeline.py::render` | Traffic global filters, visual focus, investigation overlay | Yes |
| T-12 | Weather x Roadwork Heatmap | Operational risk scheduling grid | Mean congestion by weather condition and roadwork activity. | Heatmap | `dashboards/traffic/charts/t12_weather_heatmap.py::render` | Traffic global filters | No |
| T-13 | Area Stress Profile | Focused area stress profile / comparison heatmap or radar | Heatmap default; radar overlay comparison when enabled. | Heatmap or radar chart | `dashboards/traffic/charts/t13_compound_radar.py::render` | Traffic global filters, visual focus, investigation overlay, chart-local controls | Yes |
| T-14 | Traffic Volume And Congestion Density | Record-level volume vs congestion | Hexbin density exposes high-volume corridors operating under sustained congestion. | 2D density heatmap | `dashboards/traffic/charts/t14_density_hexbin.py::render` | Traffic global filters | No |
| T-15 | Area-Month Congestion Heatmap | Temporal area stress comparison | Click a cell to set area and month focus; Apply as filter scopes area globally. | Area-month heatmap | `dashboards/traffic/charts/t15_bubble_matrix.py::render` | Traffic global filters, investigation overlay | Yes |

### AQI Visual Registry

| ID | Title | Subtitle | Caption | Visual Type | Builder Source | Dependent Filters | Overlay Aware |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A-01 | PM2.5 Burden and Category Mix | Filtered PM2.5 burden, category mix, peak, and WHO guideline context | Mean PM2.5 compared with WHO reference; bars show PM2.5-derived category distribution. | Category bar chart | `dashboards/aqi/charts/a01_crisis_scorecard.py::render` | AQI global filters | No |
| A-02 | Weekly PM2.5 Calendar | Weekly PM2.5 intensity grid; click a week to inspect context | Week x year PM2.5 view; selected weeks populate local chart context. | Calendar heatmap | `dashboards/aqi/charts/a02_calendar_heatmap.py::render` | AQI global filters, visual focus, investigation overlay | Yes |
| A-03 | Seasonal PM2.5 Ridgeline | Distribution of daily PM2.5 by season | KDE ridgelines show pollutant distribution shape; winter right-tail vs monsoon relief. | Seasonal ridgeline distribution | `dashboards/aqi/charts/a03_seasonal_ridgeline.py::render` | AQI global filters | No |
| A-04 | Monthly PM2.5 Heatmap | Month x year mean PM2.5 rhythm | Seasonal cycles and elevated-PM2.5 clusters at monthly resolution. | Month-year heatmap | `dashboards/aqi/charts/a04_monthly_variability.py::render` | AQI global filters | No |
| A-05 | Pollution Persistence Series | Daily PM2.5 with 7-day rolling mean | Rolling mean distinct from daily values; elevated band 60-120 ug/m3. | Time-series line chart | `dashboards/aqi/charts/a05_persistence_series.py::render` | AQI global filters | No |
| A-06 | Pressure and Visibility PM2.5 Density | Sea-level pressure x visibility density view | Cell color encodes mean PM2.5 for days with similar pressure and visibility. | 2D density heatmap / seasonal drift lines | `dashboards/aqi/charts/a06_stagnation_hexbin.py::render` | AQI global filters, visual focus, investigation overlay | Yes |
| A-07 | PM2.5 Category Weather Profile | Normalized weather profiles by PM2.5 category | Normalized 0-100 category profiles across six atmospheric axes. | Radar chart | `dashboards/aqi/charts/a07_extreme_day_radar.py::render` | AQI global filters | No |
| A-08 | Minimum Temperature vs PM2.5 | Minimum temperature x PM2.5 x PM2.5 category | Category-colored scatter; sampled for readability above 2,500 points. | Scatter plot / category-transition heatmap fallback | `dashboards/aqi/charts/a08_temperature_scatter.py::render` | AQI global filters | No |
| A-09 | Pressure Band PM2.5 Comparison | Sea-level pressure band x season grouped bars | Grouped means compare PM2.5 across pressure bands and seasons. | Grouped bar chart | `dashboards/aqi/charts/a09_pressure_trigger.py::render` | AQI global filters | No |
| A-10 | Wind Speed Band Comparison | Wind band x season mean PM2.5 | Progressive disclosure; grouped means compare PM2.5 across wind-speed bands. | Grouped bar chart | `dashboards/aqi/charts/a10_wind_rescue.py::render` | AQI global filters | No |
| A-11 | Gust Ratio Quintile Check | Mean PM2.5 by gust-ratio quintile | Quintile means with uncertainty bands for checking gust-ratio relationships. | Bar chart with uncertainty bands | `dashboards/aqi/charts/a11_gust_paradox.py::render` | AQI global filters | No |
| A-12 | Temperature Spread Bands | Diurnal spread vs mean PM2.5 | Progressive disclosure; spread band grouped means. | Bar chart | `dashboards/aqi/charts/a12_temp_spread.py::render` | AQI global filters | No |
| A-13 | Rule-Based Atmospheric Regimes | Regime scatter with rule-based classification; click trace to compare | Rule-based baseline, low-visibility, dispersive, and pressure-regime comparison. | Regime scatter plot | `dashboards/aqi/charts/a13_atmospheric_states.py::render` | AQI global filters, visual focus, investigation overlay | Yes |
| A-14 | Season x Pressure Grid | Mean PM2.5 heatmap (lazy load) | Season x SLP band mean PM2.5 grid. | Heatmap | `dashboards/aqi/charts/a14_season_pressure_grid.py::render` | AQI global filters | No |
| A-15 | Weather Variable Pairplot | 7x7 weather and PM2.5 matrix; click scatter cells to emphasize a factor | Histogram diagonals; category-encoded scatters; correlation fallback below 100 rows. | Pairplot matrix / correlation heatmap fallback | `dashboards/aqi/charts/a15_pairplot.py::render` | AQI global filters, visual focus, investigation overlay, chart-local controls | Yes |

### Other Explainable Surfaces

| Surface | Source | Meaning |
| --- | --- | --- |
| KPI cards | `components/kpi_card.py`, `components/metric_strip.py`, transform KPI builders | High-level monitoring metrics computed from the current filtered dataset. |
| Insight cards | `components/insight_card.py`, `data_layer/page_bundles.py` | Human-readable page-level interpretation, such as late-year congestion peaks or winter PM2.5 accumulation. |
| Active filter context | `components/page_production.py` | Explains the current record count and active global filters. |
| Investigation chrome | `filters/interaction.py` | Shows temporary chart-click focus and Clear Focus behavior. |
| Empty state panels | `components/empty_state.py`, `components/chart_container.py`, `components/page_production.py` | Communicate filter no-match or chart-unavailable conditions without mutating user selections. |
| Developer runtime panels | `components/runtime_debug.py` | Operational explainability for reducers, dependencies, cache traces, replay, and health. |

## 2. Visualization Methodology Extraction

| Visual | Analytical Purpose | Methodological Reasoning | Communication Purpose |
| --- | --- | --- | --- |
| T-01 | Summarize network congestion and rank areas. | Scorecard plus bars combines system-level severity with area-level attribution. | Show the current operating state and where pressure concentrates. |
| T-02 | Compare multi-metric area performance. | Parallel axes expose tradeoffs across congestion, speed, capacity, incidents, environment, and mobility dimensions. | Reveal area fingerprints rather than a single ranking. |
| T-03 | Track congestion over time by area. | Line charts are appropriate for monthly temporal movement and slope comparison. | Show whether congestion is rising, falling, seasonal, or diverging across areas. |
| T-04 | Show weekday distribution shape. | Violin/box plots reveal spread, median, and heavy-tail behavior better than averages alone. | Distinguish routine congestion from volatile weekday patterns. |
| T-05 | Classify road priority by congestion and capacity. | Quadrant scatter maps two operational risk dimensions at once. | Separate baseline roads from constrained flow, capacity margin, and critical overload. |
| T-06 | Decompose environmental burden by hierarchy. | Treemaps communicate nested contribution and share-of-total burden. | Show which areas and roads dominate environmental impact. |
| T-07 | Compare road pressure relative to baseline. | Deviation bars highlight roads above or below system baseline. | Identify pedestrian-adjusted road pressure outliers. |
| T-08 | Test incident sensitivity. | Step lines by incident band emphasize cliff effects. | Show whether congestion changes sharply as incidents increase. |
| T-09 | Locate speed-collapse conditions. | Threshold scatter uses reference lines to divide normal and critical operating zones. | Show where high congestion and low speed coexist. |
| T-10 | Compare public transport usage bands. | Grouped bars plus line show congestion, speed, and incident changes by quartile. | Check whether higher public transport usage aligns with lower road pressure. |
| T-11 | Profile road-level congestion distributions. | Small multiples reveal each road's distribution shape and median. | Surface skewed or chronically overloaded roads. |
| T-12 | Evaluate weather and roadwork interaction. | Heatmaps communicate two categorical dimensions with a continuous risk value. | Show operational combinations associated with high congestion. |
| T-13 | Compare area stress dimensions. | Heatmap supports compact comparison; radar supports focused multi-axis shape comparison. | Show how selected areas differ across stress factors. |
| T-14 | Inspect volume-congestion density. | 2D density avoids overplotting and reveals clusters. | Identify high-volume corridors under sustained congestion. |
| T-15 | Compare area-month stress. | Matrix heatmap is suited to area x time pressure comparisons. | Expose temporal hotspots and recurring area stress. |
| A-01 | Summarize PM2.5 burden and category mix. | Category bars connect mean pollution burden to severity composition. | Show chronic exposure relative to health-oriented context. |
| A-02 | Locate weekly PM2.5 intensity. | Calendar heatmap preserves time ordering while exposing intensity clusters. | Show persistent polluted weeks and seasonal blocks. |
| A-03 | Compare seasonal distribution shape. | Ridgelines reveal shifts, tails, and relief periods beyond means. | Explain winter accumulation versus monsoon relief. |
| A-04 | Compare month-year pollution rhythm. | Heatmap exposes periodicity and multi-year clusters. | Show seasonal cycles at monthly resolution. |
| A-05 | Separate daily volatility from persistence. | Rolling-mean time series smooths day noise while retaining raw daily values. | Distinguish spikes from sustained pollution episodes. |
| A-06 | Inspect stagnation conditions. | Pressure x visibility density connects meteorological states with PM2.5 burden. | Show where poor visibility and pressure regimes coincide with high pollution. |
| A-07 | Compare weather profiles by PM2.5 category. | Normalized radar axes make category-level atmospheric signatures comparable. | Show which atmospheric variables differ across severity categories. |
| A-08 | Explore temperature and PM2.5 relation. | Scatter supports relationship inspection; fallback heatmap summarizes category transitions. | Show whether low minimum temperature aligns with higher PM2.5 categories. |
| A-09 | Compare pressure-band effects by season. | Grouped bars make categorical band and season comparisons readable. | Show whether pressure regimes vary in PM2.5 burden across seasons. |
| A-10 | Compare wind-band effects by season. | Grouped bars show dispersion-related patterns without implying causality. | Show whether stronger wind bands correspond to lower PM2.5. |
| A-11 | Test gust-ratio relationship. | Quintile bars with uncertainty bands expose monotonic or unstable patterns. | Check whether gustiness is associated with PM2.5 shifts. |
| A-12 | Test diurnal temperature spread. | Banded bars simplify continuous spread into interpretable groups. | Show whether day-night temperature spread aligns with PM2.5 differences. |
| A-13 | Compare atmospheric regimes. | Rule-based scatter reveals clusters by interpretable meteorological labels. | Show baseline, low-visibility, dispersive, and pressure-regime differences. |
| A-14 | Cross-tab season and pressure. | Heatmap is efficient for two categorical dimensions and mean PM2.5. | Show seasonal pressure-pattern hotspots. |
| A-15 | Explore multivariate weather relationships. | Pairplot gives a compact matrix of pairwise relationships and distributions. | Support exploratory comparison among PM2.5 and weather variables. |

## 3. Analytical Terminology Extraction

| Term | Meaning | Implication | Why It Matters | Appears In |
| --- | --- | --- | --- | --- |
| Active filter scope | The dataset after global filters are applied. | Every KPI and chart is computed from this current analytical subset. | Users must understand that values are conditional on selected filters. | Filter panel, KPI notes, chart captions. |
| Investigation overlay | Temporary chart-click data projection layered after global filters. | Narrows overlay-aware charts without changing top-level filter widgets. | Separates exploratory drilldown from persistent filtering. | T-02, T-05, T-06, T-07, T-09, T-11, T-13, T-15, A-02, A-06, A-13, A-15. |
| Visual focus | Selection state used for highlighting, labels, and breadcrumbs. | Can make related chart traces more prominent. | Helps users follow a clicked entity across charts. | Overlay-aware and visual-focus-aware charts. |
| Clear Focus | Command that removes visual focus and investigation overlay. | Returns charts to baseline view while preserving global filters. | Prevents temporary drilldowns from being mistaken for permanent filters. | Investigation chrome. |
| System Congestion Index | Mean congestion percentage across filtered records. | Higher values indicate heavier overall road network pressure. | Primary traffic health indicator. | Traffic command KPIs. |
| Capacity Saturation Rate | Share of records at or above 99.5 percent road-capacity utilization. | High values imply roads operating near physical or modeled capacity. | Capacity saturation is an operational bottleneck signal. | Traffic command KPIs. |
| Active Incidents | Sum of incident reports in the filtered scope. | More incidents may coincide with elevated congestion. | Incident load helps separate routine congestion from disruption. | Traffic command KPIs, T-08. |
| Average Speed / Mean Speed | Mean observed road speed in km/h. | Lower speed usually signals degraded mobility. | Interprets congestion in real movement terms. | Traffic KPIs, T-09, T-10. |
| Pedestrian Exposure | Mean pedestrian and cyclist count per record. | High exposure makes road pressure more socially sensitive. | Connects vehicle congestion to vulnerable road-user context. | Traffic KPIs, T-07. |
| Public Transport Usage | Mean public transport usage percentage per record. | May indicate modal shift or corridor demand profile. | Helps test whether public transport usage aligns with lower congestion. | Traffic KPIs, T-10. |
| Signal Compliance | Mean traffic signal compliance percentage. | Low compliance may imply operational disorder. | Supports interpretation of congestion beyond volume alone. | Traffic KPIs, T-02. |
| Environmental Impact | Derived environmental impact score per record. | Higher scores imply greater environmental burden. | Links mobility conditions to environmental cost. | Traffic KPIs, T-06. |
| Peak Month Congestion | Highest monthly mean congestion in the filtered period. | Identifies worst temporal window. | Supports seasonal planning and stress diagnosis. | Traffic temporal KPIs, T-03, T-15. |
| Lowest Month | Lowest monthly mean congestion in the filtered period. | Identifies relief period. | Useful baseline for comparing peak burden. | Traffic temporal KPIs. |
| Trend Direction | Difference between recent and earlier monthly mean congestion. | Positive values imply worsening recent congestion. | Helps distinguish static severity from movement. | Traffic temporal KPIs. |
| Volatility Index | Coefficient of variation of monthly mean congestion. | High values indicate unstable congestion across time. | Volatility changes planning risk even when averages are similar. | Traffic temporal KPIs, T-03/T-04 context. |
| Critical Overload Roads | Roads with mean congestion at or above 90 percent. | Indicates chronically overloaded corridors. | Directly supports intervention prioritization. | Traffic spatial KPIs, T-05, T-11. |
| Baseline Roads | Roads with mean congestion below 60 percent. | Indicates lower-pressure comparators. | Helps differentiate normal from elevated road stress. | Traffic spatial KPIs. |
| Threshold Crossings | Count of records with congestion at or above 90 percent. | Shows how often critical congestion occurs. | Frequency matters as much as peak severity. | Traffic threshold KPIs, T-09. |
| Speed collapse | Operating state where low speed and high congestion coincide. | Indicates gridlock-like mobility degradation. | Converts abstract congestion into operational failure. | T-09. |
| Critical overload zone | Scatter quadrant combining high congestion and low speed or high capacity burden. | These points or roads need priority attention. | Gives users a clear risk category. | T-05, T-09. |
| Weather x roadwork risk | Mean congestion for weather and roadwork combinations. | Some operational combinations may elevate congestion. | Supports scheduling and mitigation planning. | T-12. |
| PM2.5 | Fine particulate matter concentration. | Higher PM2.5 indicates worse air quality and greater exposure risk. | Core AQI burden metric in this dashboard. | All AQI pages. |
| Mean PM2.5 in View | Average PM2.5 in the current filtered scope. | Summarizes chronic pollution level. | Central environmental health signal. | AQI crisis KPIs. |
| Peak PM2.5 | Highest PM2.5 value in scope. | Captures acute extremes. | Extreme pollution episodes may require different response than averages. | AQI crisis KPIs. |
| Days Above 120 ug/m3 | Share of days above a high PM2.5 threshold. | Indicates frequency of severe pollution exposure. | Frequency communicates persistence of hazardous conditions. | AQI crisis KPIs, A-05. |
| WHO Guideline Context | Reference comparison against 5 ug/m3 annual PM2.5. | Shows how far observed PM2.5 is from health-oriented reference. | Prevents local averages from seeming normal without context. | AQI crisis KPIs, A-01. |
| Dominant Category | Most common PM2.5-derived category in the filtered data. | Identifies prevailing severity class. | Gives categorical interpretation to numerical PM2.5. | AQI KPIs, A-01, A-08. |
| Category Transitions | Count of changes between AQI categories over time. | Higher values imply unstable air-quality category movement. | Helps users understand volatility and regime switching. | AQI weather KPIs, A-08. |
| Severe Share | Share of records with PM2.5 above severe threshold. | Indicates how much of the period is very polluted. | Provides exposure-frequency context. | AQI weather KPIs. |
| Rolling mean | Smoothed average over a time window, here 7 days. | Reveals sustained pollution independent of daily spikes. | Helps identify persistence. | A-05. |
| Pollution persistence | Sustained elevated PM2.5 over multiple days. | Indicates chronic exposure episodes rather than isolated events. | More actionable for public-health response than a single spike. | A-05. |
| Stagnation trap | Low visibility and high PM2.5 condition. | Suggests trapped pollutants under poor dispersion. | Explains atmospheric conditions associated with severe pollution. | AQI atmospheric KPIs, A-06, A-13. |
| Mean VV | Mean visibility in kilometers. | Lower visibility may coincide with pollution accumulation. | Visibility is an observable atmospheric proxy for particulate burden. | AQI atmospheric KPIs, A-06. |
| Sea-level pressure / SLP | Atmospheric pressure normalized to sea level. | Pressure regimes may align with stagnation or dispersion patterns. | Supports interpretation of meteorological influence. | A-06, A-09, A-14, A-15. |
| Wind band | Grouped wind-speed category. | Stronger winds may correspond with pollutant dispersion. | Supports weather-pattern comparison without implying direct causality. | A-10. |
| Gust ratio | Relationship between gust behavior and average wind behavior. | Can indicate ventilation or turbulent mixing patterns. | Used as a relationship check against PM2.5. | A-11. |
| Diurnal temperature spread | Difference between daily high and low temperature. | May align with atmospheric stability and pollution behavior. | Supports weather-context analysis. | A-12. |
| Rule-based atmospheric regime | Classification created from conditions such as visibility, pressure, and dispersion. | Helps users compare interpretable environmental states. | Useful for explanation, but not a predictive model. | A-13. |
| Pairplot | Matrix of pairwise variable comparisons and distributions. | Exposes multivariate relationships and clusters. | Helps advanced users explore weather-PM2.5 relationships. | A-15. |

## 4. Insight Extraction

### Traffic Insights

- Command overview: system congestion and area ranking communicate whether the current filtered scope is broadly stressed or concentrated in a few areas.
- Temporal page: late-year or monthly peaks identify when congestion pressure intensifies; weekday distributions reveal whether pressure is routine or volatile.
- Spatial page: road priority quadrants identify corridors that combine congestion with capacity stress; environmental treemaps show where burden is concentrated.
- Advanced profile page: area stress profiles expose multi-dimensional imbalance rather than single-metric rankings.
- Threshold page: speed-collapse and incident-band charts show operational breaking points: low speed under high congestion and congestion sensitivity to incident bands.
- Pattern page: road distribution profiles reveal chronic overload and skew; weather-roadwork heatmaps reveal operational combinations associated with higher mean congestion.
- Density view: volume-congestion density identifies high-volume records operating under sustained congestion, which are candidate corridors for deeper investigation.

### AQI Insights

- Crisis overview: PM2.5 burden is interpreted relative to category mix, severe-day frequency, peak exposure, and WHO guideline context.
- Temporal page: weekly, monthly, and rolling PM2.5 views distinguish seasonal structure, sustained pollution, and acute spikes.
- Atmospheric page: pressure, visibility, seasonal drift, and normalized category profiles communicate atmospheric conditions associated with pollution accumulation or relief.
- Pattern page: ridgelines emphasize winter right tails and monsoon relief; gust-ratio checks support relationship exploration.
- Weather comparison page: temperature, pressure, wind, and spread views compare PM2.5 against weather indicators without claiming causality.
- Lab page: pairplot and regime scatter support exploratory diagnosis of multivariate relationships and rule-based atmospheric categories.

## 5. Interaction Semantics Extraction

- Global filters are persistent dataset-scope filters. They should combine naturally and are applied before page bundles and chart transforms are built.
- Global filters include traffic dimensions such as date, area, weather, road, and roadwork, and AQI dimensions such as date, AQI category, and season.
- Chart clicks dispatch `ChartFocusChanged` and may create visual focus plus an investigation overlay when interaction mode allows it.
- In baseline mode, chart clicks can activate temporary investigation overlays for overlay-aware charts.
- In global-filter mode, chart-click drilldown overlays are blocked; chart click behavior is cosmetic only. This prevents simultaneous global and temporary analytical authority.
- Investigation overlays are temporary analytical projections. They are applied after global filters and before chart-specific transforms.
- Clear Focus dispatches `FocusCleared`, clearing visual focus and investigation overlay while preserving global filters.
- Reset All dispatches `GlobalFiltersReset`, restoring global filters, visual focus, and investigation overlay to baseline.
- Empty datasets are valid analytical outcomes. The dashboard should preserve user selections and render empty-state messaging rather than silently clearing filters.

## 6. KPI Semantic Extraction

### Traffic KPI Families

| KPI | Meaning | Why It Matters | Interpretation Guidance |
| --- | --- | --- | --- |
| System Congestion Index | Mean congestion percentage across filtered records. | Primary traffic severity summary. | Higher values mean broader network pressure in the selected scope. |
| Capacity Saturation Rate | Share of records near full road-capacity utilization. | Capacity pressure indicates infrastructure bottlenecks. | High saturation means roads are operating with little headroom. |
| Active Incidents | Sum of incident reports in the filtered scope. | Incidents may explain abnormal congestion. | Compare with congestion to distinguish disruption from routine load. |
| Average Speed / Mean Speed | Mean observed speed in km/h. | Converts congestion into travel-performance terms. | Declining speed under high congestion suggests mobility breakdown. |
| Pedestrian Exposure | Mean pedestrian and cyclist count per record. | Congestion has higher social impact where vulnerable users are exposed. | High exposure roads need more cautious interpretation than vehicle-only pressure. |
| Public Transport Usage | Mean public transport usage percentage. | Indicates mobility mix in the filtered scope. | Compare quartiles to see whether PT usage aligns with congestion or speed changes. |
| Signal Compliance | Mean traffic signal compliance percentage. | Compliance affects operational flow and safety. | Low compliance may amplify congestion or incident risk. |
| Environmental Impact | Mean derived environmental impact score. | Connects traffic stress to environmental burden. | High impact highlights corridors where mobility pressure has broader cost. |
| Peak Month Congestion | Highest monthly mean congestion. | Identifies the worst time window. | Use with trend charts to find recurring peaks. |
| Trend Direction | Recent monthly mean minus earlier monthly mean. | Captures movement, not just level. | Positive trend suggests worsening recent conditions. |
| Volatility Index | Coefficient of variation of monthly congestion. | Measures instability. | High volatility means averages may hide unpredictable peaks. |
| Critical Overload Roads | Roads with mean congestion at or above 90 percent. | Identifies intervention candidates. | More roads in this state means stress is distributed, not isolated. |
| Threshold Crossings | Count of records with congestion at or above 90 percent. | Measures frequency of critical stress. | Frequent crossings imply repeated operational failure. |

### AQI KPI Families

| KPI | Meaning | Why It Matters | Interpretation Guidance |
| --- | --- | --- | --- |
| Days Above 120 ug/m3 | Percentage of days above a high PM2.5 threshold. | Frequency of high exposure is more informative than isolated peaks. | Higher percentages imply persistent environmental burden. |
| Peak PM2.5 | Maximum PM2.5 in the filtered scope. | Captures acute exposure extremes. | Interpret with rolling mean to distinguish spike from sustained crisis. |
| Mean PM2.5 in View | Average PM2.5 in the filtered scope. | Core chronic pollution indicator. | Compare with WHO guideline context and category mix. |
| Severe Days Count | Count of severe PM2.5 days. | Communicates duration of hazardous conditions. | A high count suggests repeated high-risk exposure windows. |
| WHO Guideline Context | Reference value of 5 ug/m3 annual PM2.5. | Gives health-oriented scale to local values. | Values far above this reference should not be normalized as acceptable. |
| Dominant Category | Most frequent PM2.5 category. | Converts numeric PM2.5 into severity language. | Helps nontechnical users understand prevailing air quality. |
| Strongest Weather Correlation | Weather variable with highest absolute PM2.5 correlation in scope. | Guides exploratory attention. | It is correlational only, not causal evidence. |
| Stagnation Trap Days | Days with low visibility and high PM2.5. | Identifies poor-dispersion pollution episodes. | More trap days imply atmospheric accumulation risk. |
| Low VV + High PM2.5 | Share of focused records with low visibility and high PM2.5. | Measures how often poor visibility aligns with severe pollution. | Use with pressure and season views to contextualize conditions. |
| Category Transitions | Count of AQI category changes over time. | Measures category instability. | More transitions imply volatile air-quality classification. |
| Severe Share | Share of records above severe PM2.5 threshold. | Measures exposure prevalence. | High severe share indicates broad severe pollution, not just a peak. |

## 7. Empty-State Knowledge Extraction

| Empty State | Source | Why It Occurs | User Guidance | State Preservation Rule |
| --- | --- | --- | --- | --- |
| No data matches filters | `components/chart_container.py` | Compound global filters, date range, or overlay scope produce zero rows for a chart. | Adjust date range or scope filters if the empty result was not intended. | Preserve all global filter selections and overlay state until the user changes them. |
| No records match current filter selection | `components/page_production.py` | Page bundle receives no rows after global filtering. | Review active filters or reset filters to restore records. | Do not auto-clear filters. Empty result is valid analytical feedback. |
| Chart unavailable | `components/chart_container.py` | Chart builder returned `None`, lazy builder failed safely, or required data is unavailable. | Treat as chart-level unavailable state, not a reason to reset filters. | Preserve state; recovery is chart-cache scoped where applicable. |
| No data to export | `components/filter_panel.py`, `components/session_notice.py` | Export requested when bundle has no exportable rows. | Adjust filters or restore data before exporting. | Do not alter analytical state. |
| Bootstrap/reload unavailable | `components/page_runtime.py` | Raw or processed datasets are missing or stale. | Restore datasets or reset filters, then reload. | Dataset lifecycle issue, not analytical selection cleanup. |

## 8. Overlay And Investigation Knowledge Extraction

- Global filters are canonical dataset authority. They are persistent, widget-backed, and should combine through normal dataframe filtering.
- Investigation overlays are temporary drilldown authority. They are activated by chart interactions only when no global filters are active.
- Visual focus is the UI memory of what the user clicked. It powers breadcrumbs, highlighting, and selection labels.
- Overlay-aware traffic charts: T-02, T-05, T-06, T-07, T-09, T-11, T-13, T-15.
- Overlay-aware AQI charts: A-02, A-06, A-13, A-15.
- Visual-focus-aware traffic charts: T-02, T-05, T-06, T-07, T-09, T-11, T-13.
- Visual-focus-aware AQI charts: A-02, A-06, A-13, A-15.
- Clear Focus restores the baseline investigation view by clearing temporary visual focus and overlay state.
- Reset All restores baseline interaction mode by clearing global filters, visual focus, and investigation overlay.
- Future explainability must clearly separate "I filtered the dataset" from "I temporarily investigated a clicked chart element."

## 9. User Interpretation Guidance

| Visual | How To Read It |
| --- | --- |
| T-01 | Read the scorecard as overall network pressure and the bars as where that pressure is concentrated. |
| T-02 | Look for lines that remain high across many axes; those areas have broad multi-factor stress. |
| T-03 | Steeper upward slopes indicate worsening monthly congestion; diverging lines indicate unequal area trajectories. |
| T-04 | Wider shapes show more variability; long upper tails show occasional severe congestion. |
| T-05 | Points in the critical overload quadrant combine high congestion and capacity pressure. |
| T-06 | Larger blocks contribute more total environmental burden; nested blocks show area-road responsibility. |
| T-07 | Positive bars are above baseline pressure; larger positive deviations deserve closer inspection. |
| T-08 | A sharp step between incident bands indicates congestion sensitivity to incidents. |
| T-09 | Points above congestion threshold and below speed threshold indicate speed-collapse risk. |
| T-10 | Compare quartiles to see whether public transport usage bands align with congestion or speed differences. |
| T-11 | Roads with right-skewed distributions and high medians are chronically stressed. |
| T-12 | Darker cells indicate higher mean congestion for a weather-roadwork combination. |
| T-13 | In heatmap mode, compare color intensity across dimensions; in radar mode, larger shapes mean broader stress. |
| T-14 | Dense high-volume/high-congestion regions represent sustained corridor load. |
| T-15 | Darker area-month cells identify when and where congestion pressure concentrates. |
| A-01 | Read category mix with mean PM2.5 and WHO context to understand chronic burden. |
| A-02 | Darker weeks identify persistent PM2.5 periods; blocks reveal seasonal or year-specific episodes. |
| A-03 | Right-shifted or right-tailed seasons indicate more high-PM2.5 days. |
| A-04 | Darker month-year cells indicate recurring seasonal PM2.5 hotspots. |
| A-05 | Daily spikes show acute events; rolling mean shows sustained exposure. |
| A-06 | High PM2.5 cells under low visibility or pressure bands suggest stagnation-like conditions. |
| A-07 | Compare radar shapes to see which weather dimensions differ by PM2.5 category. |
| A-08 | Upward PM2.5 patterns at lower temperatures may indicate temperature-linked pollution behavior, but not causality. |
| A-09 | Higher bars in pressure bands suggest pressure regimes associated with greater PM2.5 in that season. |
| A-10 | Lower PM2.5 under stronger wind bands may indicate dispersion, but should be interpreted cautiously. |
| A-11 | Monotonic quintile movement suggests a relationship worth investigating; wide uncertainty reduces confidence. |
| A-12 | Larger bar differences across temperature-spread bands suggest atmospheric stability associations. |
| A-13 | Regime clusters show how rule-based atmospheric conditions separate pollution patterns. |
| A-14 | Dark season-pressure cells identify combined meteorological conditions associated with higher PM2.5. |
| A-15 | Use diagonal histograms for distribution and off-diagonal scatter cells for pairwise relationships. |

## 10. Explainability Readiness Audit

### Already Strong

- Most charts have meaningful titles, subtitles, and captions in `page_bundles.py`.
- Traffic KPI notes are centralized in `TRAFFIC_KPI_NOTES`.
- Chart dependencies are already centralized in `CHART_DEPENDENCY_REGISTRY`.
- Overlay semantics are mature and can be explained consistently.
- Empty-state rendering is already presentation-only and can carry explanatory copy.

### Needs Manual Authoring

- AQI KPI methodology is less centralized than traffic KPI notes. Future work should add an AQI KPI definition catalog before UI rollout.
- Some captions describe interaction or chart mechanics but not analytical implication.
- Advanced visuals such as T-02, T-13, A-15, and A-13 need richer explanations because they require statistical or multivariate interpretation.
- Terms such as "volatility index", "stagnation trap", "gust ratio", "capacity saturation", and "rule-based regime" need user-friendly term cards.

### Potentially Vague Labels

- "Environmental Impact" needs a visible definition of the derived score.
- "Trend Direction" should explain the recent-vs-earlier heuristic.
- "Strongest Weather Correlation" should explicitly warn that correlation is not causation.
- "Category Transitions" should clarify whether transitions are chronological day-to-day category changes.
- "Lab Mode" should explain that the analytical workspace inherits global filters unless local lab controls change display scope.

### Simplification Candidates

- "Pedestrian-Adjusted Road Pressure" can be explained as "road congestion relative to baseline, with exposure context."
- "Pressure and Visibility PM2.5 Density" can be simplified as "where weather conditions and pollution levels cluster."
- "Rule-Based Atmospheric Regimes" can be simplified as "interpretable weather-condition groups, not a prediction model."
- "Volatility Index" can be simplified as "how unstable congestion is across months."

## 11. Future Registry Structure Proposal

Do not implement this yet. A future registry could live in a presentation-only module such as `explainability/registry.py` or `components/explainability/registry.py`.

Suggested schema:

```python
ExplainabilityEntry(
    surface_id="T-05",
    dashboard="traffic",
    surface_type="chart",
    title="Road Management Priority Quadrant",
    what_this_shows="Roads positioned by congestion and capacity pressure.",
    why_this_visualization="A quadrant scatter exposes two operational risk dimensions at once.",
    interpretation_guide=[
        "Upper-right points indicate critical overload.",
        "Lower-left points indicate baseline roads.",
    ],
    analytical_implication="Roads in high congestion and high capacity pressure require priority attention.",
    key_terms=["congestion", "capacity saturation", "critical overload"],
    interaction_help="Click a road to activate temporary investigation focus when no global filters are active.",
    filter_impact="Global filters narrow the dataset before this chart is built.",
    overlay_behavior="Investigation overlay can focus related charts by road or area.",
    source_refs=[
        "data_layer/page_bundles.py",
        "dashboards/traffic/charts/t05_quadrant_scatter.py",
        "filters/performance.py",
    ],
)
```

Recommended fields:

- `surface_id`
- `dashboard`
- `surface_type`
- `title`
- `what_this_shows`
- `why_this_visualization`
- `methodology`
- `interpretation_guide`
- `analytical_implication`
- `key_terms`
- `related_kpis`
- `filter_impact`
- `overlay_behavior`
- `interaction_help`
- `empty_state_meaning`
- `source_refs`
- `readiness_status`

## 12. Codebase Integration Points

Future explainability UI should be inserted only at presentation boundaries:

- `components/chart_container.py::chart_container()`: chart-header info trigger, caption-adjacent explanation, chart-level popover.
- `components/kpi_card.py::kpi_card()`: KPI definition popover and threshold explanation.
- `components/metric_strip.py::metric_strip()`: pass metric labels or explanation IDs into KPI cards.
- `components/page_production.py::render_production_page()`: page-level analytical guide, insight-card explanations, active-filter context help.
- `components/empty_state.py::empty_state()`: empty-state explanation and suggested user actions.
- `filters/interaction.py::render_investigation_chrome()`: explanation of temporary overlays and Clear Focus.
- `components/filter_panel.py::filter_panel()`: explanation of persistent global filters and compound filtering.
- `components/runtime_debug.py::render_transition_debug_panel()`: developer-only runtime explainability can remain separate from user-facing explainability.

Avoid these integration points:

- Reducers in `filters/transitions.py`.
- Invalidation and dependency routing in `filters/performance.py`.
- Data filtering functions in `filters/traffic_filters.py` and `filters/aqi_filters.py`.
- Lazy chart cache logic in `data_layer/lazy_charts.py`.
- Dataset loaders and governance modules.

## 13. Streamlit Feasibility Analysis

The UX vision is feasible in Streamlit with presentation-layer constraints.

Native or near-native fits:

- `st.popover` for compact contextual explanations.
- `st.expander` for page-level "how to read this" panels.
- `st.dialog` for deeper methodology views when a chart is complex.
- Markdown rendering for term definitions and interpretation guidance.
- Existing custom HTML/CSS helpers for polished cards and empty-state copy.
- Existing chart container structure for consistent placement.

Needs custom styling:

- Premium icon buttons in chart headers.
- Subtle hover/focus states around explanation triggers.
- Compact term chips or glossary links.
- Motion quality beyond Streamlit defaults.
- Consistent popover width, typography, and spacing.

Should be avoided:

- Hover-only explanations as the only access path, because Streamlit hover behavior is limited and mobile-unfriendly.
- Popover spam on every small label.
- Runtime AI generation in the dashboard path.
- Explanation controls that trigger reruns with analytical side effects.
- Explanations inside reducers, cache layers, or data transforms.

Recommended Streamlit interaction model:

- Use explicit info/help triggers for charts and KPIs.
- Keep explanations collapsed by default.
- Prefer short structured sections: What this shows, Why this visual, How to read it, Interactions, Terms.
- Use dialog only for advanced visuals such as T-02, T-13, A-13, and A-15.

## 14. UX Design Direction

The explainability layer should feel like embedded analytical guidance, not documentation pasted into the app.

Design principles:

- Progressive disclosure: show help only when the user asks or when the state genuinely needs explanation.
- Contextual specificity: each explanation must refer to the exact chart, metric, filter state, or overlay behavior.
- Analytical storytelling: explain what the visual means and how to reason with it, not just which chart type it is.
- Quiet confidence: compact controls, restrained styling, clear typography, no decorative overload.
- State respect: never clear filters, rerun analytical transitions, or mutate overlays just because help was opened.
- Reusable semantics: terms such as PM2.5, volatility, capacity saturation, and investigation overlay should have one canonical definition.

The final product direction is a guided analytical decision-support system. The runtime already governs state, dependencies, overlays, and observability; the next layer should help users understand what those analytics mean and how to think with the data.
