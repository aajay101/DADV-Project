# BANGALORE URBAN INTELLIGENCE PLATFORM
## Implementation Architecture Blueprint
### Engineering Organization · Visualization Systems · Dashboard Structure

**Document Type:** Implementation Architecture · Engineering Design  
**Status:** Pre-Implementation · Engineering Planning Phase  
**Scope:** Traffic Intelligence Dashboard + AQI Environmental Intelligence Dashboard  
**Stack:** Streamlit · Plotly · PyDeck · Altair  
**Not Included:** ML systems · APIs · Deployment infrastructure · Live streaming

---

# PART 1 — DASHBOARD ENGINEERING PHILOSOPHY

---

## 1.1 · Governing Engineering Principles

**Principle 1: One Source of Truth Per Concern**  
Every chart configuration, color token, filter state, and layout constant lives in exactly one place. If you find yourself writing the same value twice, it belongs in a shared config or utility module.

**Principle 2: Separation of Data, Logic, and Presentation**  
Raw data → transformation → visualization-ready data → render. These are four distinct layers. Mixing transformation logic inside chart functions is the fastest path to an unmaintainable codebase.

**Principle 3: Reuse Before Rebuild**  
Every new chart should first ask: "Can a base wrapper with different parameters handle this?" If three chart functions share 80% of their configuration code, that 80% is a shared utility function waiting to be extracted.

**Principle 4: Charts Are Configuration, Not Code**  
The ideal chart module is: load data → apply shared config → set chart-specific parameters → return figure. Business logic does not belong inside chart render functions.

**Principle 5: Filters Are Application State, Not Widget State**  
Global filters live in `st.session_state` and are read by every chart that needs them. No chart function directly renders a filter widget. Widgets live in filter components; charts read state.

**Principle 6: Performance Is Architectural, Not an Afterthought**  
Caching strategy, lazy loading, and computation boundaries are decided at architecture time. Adding `@st.cache_data` to a function that recalculates a 8,936-row grouped aggregation 15 times per page load is not a performance strategy — it is cleanup.

---

## 1.2 · Stack Roles

| Tool | Role |
|---|---|
| **Streamlit** | Page routing · Layout containers · State management · Widget rendering · Caching layer |
| **Plotly (Express + Graph Objects)** | All chart rendering · Interactive tooltips · Synchronized axis behaviors · Animation |
| **PyDeck** | Geospatial layer rendering (if map visuals are introduced in future phases) |
| **Altair** | Alternative for statistical charts where declarative grammar is cleaner (ridgelines, pairplots) |
| **Pandas** | All data transformation · Groupby · Aggregation · Derived column computation |

**When to use Altair vs Plotly:**  
Use Altair for visuals that benefit from a declarative layered grammar: ridgeline plots (overlapping KDE), pairplot matrices (grid specification), and interaction-linked multi-panel views. Use Plotly for all other charts — especially those requiring precise tooltip control, animation, and custom trace layering.

---

# PART 2 — FULL PROJECT FOLDER STRUCTURE

---

## 2.1 · Root Structure

```
bangalore_intelligence/
│
├── app.py                          # Entry point — dashboard switcher only
├── requirements.txt
├── .streamlit/
│   └── config.toml                 # Streamlit server config, theme base
│
├── config/                         # All application-wide constants
│   ├── __init__.py
│   ├── theme.py                    # Color tokens, typography, spacing
│   ├── chart_defaults.py           # Shared Plotly layout defaults
│   ├── data_config.py              # Column name constants, dataset paths
│   └── page_config.py              # Page metadata, tab labels, descriptions
│
├── data/
│   ├── raw/
│   │   ├── traffic_raw.csv
│   │   └── aqi_raw.csv
│   ├── processed/
│   │   ├── traffic_clean.parquet   # Cleaned, typed, derived columns added
│   │   └── aqi_clean.parquet
│   └── aggregations/               # Pre-computed expensive groupbys (optional)
│       ├── traffic_area_monthly.parquet
│       ├── traffic_road_stats.parquet
│       └── aqi_monthly_stats.parquet
│
├── dashboards/
│   ├── traffic/                    # Complete Traffic Intelligence Dashboard
│   │   ├── __init__.py
│   │   ├── pages/
│   │   │   ├── p1_command_overview.py
│   │   │   ├── p2_temporal_intelligence.py
│   │   │   ├── p3_spatial_operations.py
│   │   │   ├── p4_threshold_analytics.py
│   │   │   ├── p5_hidden_patterns.py
│   │   │   └── p6_advanced_lab.py
│   │   └── charts/
│   │       ├── t01_scorecard.py
│   │       ├── t02_parallel_coords.py
│   │       ├── t03_stream_graph.py
│   │       ├── t04_violin_weekly.py
│   │       ├── t05_quadrant_scatter.py
│   │       ├── t06_burden_treemap.py
│   │       ├── t07_mobility_exclusion.py
│   │       ├── t08_incident_cliff.py
│   │       ├── t09_speed_threshold.py
│   │       ├── t10_pt_decoupling.py
│   │       ├── t11_ridgeline.py
│   │       ├── t12_weather_heatmap.py
│   │       ├── t13_compound_radar.py
│   │       ├── t14_density_hexbin.py
│   │       └── t15_bubble_matrix.py
│   │
│   └── aqi/                        # Complete AQI Intelligence Dashboard
│       ├── __init__.py
│       ├── pages/
│       │   ├── p1_crisis_overview.py
│       │   ├── p2_temporal_patterns.py
│       │   ├── p3_atmospheric_intelligence.py
│       │   ├── p4_weather_relationships.py
│       │   ├── p5_hidden_patterns.py
│       │   └── p6_advanced_lab.py
│       └── charts/
│           ├── a01_crisis_scorecard.py
│           ├── a02_calendar_heatmap.py
│           ├── a03_seasonal_ridgeline.py
│           ├── a04_monthly_variability.py
│           ├── a05_persistence_series.py
│           ├── a06_stagnation_hexbin.py
│           ├── a07_extreme_day_radar.py
│           ├── a08_temperature_scatter.py
│           ├── a09_pressure_trigger.py
│           ├── a10_wind_rescue.py
│           ├── a11_gust_paradox.py
│           ├── a12_temp_spread.py
│           ├── a13_atmospheric_states.py
│           ├── a14_season_pressure_grid.py
│           └── a15_pairplot.py
│
├── components/                     # Reusable UI building blocks
│   ├── __init__.py
│   ├── kpi_card.py                 # KPI card renderer
│   ├── metric_strip.py             # Horizontal metric row
│   ├── hero_section.py             # Page hero header block
│   ├── insight_panel.py            # "What This Means" collapsible panel
│   ├── filter_panel.py             # Global filter strip component
│   ├── nav_card.py                 # "Investigate Further" navigation card
│   ├── chart_container.py          # Wrapper: title + chart + caption
│   ├── collapsible_section.py      # Expand/collapse section wrapper
│   ├── lab_gate.py                 # Advanced Analytics Lab entry gate
│   ├── lab_header.py               # Lab mode indicator strip
│   └── detail_panel.py             # Dynamic detail panel (road/month drilldown)
│
├── data_layer/                     # All data handling — NO chart logic here
│   ├── __init__.py
│   ├── loaders.py                  # Dataset loading and caching
│   ├── cleaners.py                 # Cleaning, typing, derived column logic
│   ├── transformers.py             # Aggregations, pivots, group-bys
│   ├── traffic_transforms.py       # Traffic-specific derived datasets
│   └── aqi_transforms.py           # AQI-specific derived datasets
│
├── filters/                        # Filter state management
│   ├── __init__.py
│   ├── state.py                    # Session state initialization and helpers
│   ├── traffic_filters.py          # Traffic filter logic and application
│   └── aqi_filters.py              # AQI filter logic and application
│
└── utils/
    ├── __init__.py
    ├── plotly_helpers.py           # Shared Plotly layout builders
    ├── altair_helpers.py           # Shared Altair spec builders
    ├── annotations.py             # Reusable chart annotation builders
    ├── formatters.py              # Number, date, percentage formatting
    └── validators.py              # Data validation utilities
```

---

## 2.2 · Key Structural Decisions

**Why `dashboards/traffic/` and `dashboards/aqi/` are separate top-level directories:**  
The two dashboards share components and data infrastructure but have entirely separate page modules and chart modules. Mixing them in a flat structure creates maintenance confusion when the project grows. Isolation at the dashboard level makes it possible to work on one dashboard without touching the other.

**Why `charts/` is inside each dashboard, not shared:**  
T-11 (Traffic Ridgeline) and A-03 (AQI Ridgeline) are both ridgeline plots but have different columns, styling, annotation logic, and insight captions. A shared ridgeline factory with 15 parameters is worse than two clean, readable chart modules. Chart logic is allowed to repeat its *type* if the *content* is fundamentally different.

**Why `components/` is shared across both dashboards:**  
KPI cards, filter panels, chart containers, and collapsible sections look identical across Traffic and AQI. These are pure UI building blocks — they take data and config, they render structure. Dashboard identity (color, labels) is injected via parameters.

**Why `data_layer/` is separate from `filters/`:**  
Data transformation and filter application are different concerns. `data_layer/` handles loading, cleaning, and computing aggregations. `filters/` handles applying user selections to already-computed datasets. Mixing them creates functions that are both expensive to compute and widget-dependent — the worst combination for caching.

---

# PART 3 — MULTI-PAGE DASHBOARD ARCHITECTURE

---

## 3.1 · Application Entry Point

`app.py` has exactly one job: render the primary dashboard switcher and route to the selected dashboard. It contains no chart logic, no data loading, and no filter widgets.

```
app.py responsibilities:
  1. Set global page config (title, icon, layout="wide")
  2. Render the dashboard switcher (Traffic / AQI toggle)
  3. Store selected dashboard in session state
  4. Import and call the selected dashboard's router
  5. Nothing else
```

---

## 3.2 · Page Routing Architecture

Each dashboard has its own internal router. The router reads the selected page from session state and calls the corresponding page module.

**Traffic Dashboard Router (inside `dashboards/traffic/__init__.py`):**

```
traffic_router():
  1. Initialize traffic session state (if first load)
  2. Render tab navigation (Pages 1–6)
  3. Read selected tab from session state
  4. Route to correct page module:
     - Tab 1 → p1_command_overview.render()
     - Tab 2 → p2_temporal_intelligence.render()
     - Tab 3 → p3_spatial_operations.render()
     - Tab 4 → p4_threshold_analytics.render()
     - Tab 5 → p5_hidden_patterns.render()
     - Tab 6 → p6_advanced_lab.render()  [with gate check]
  5. Render global filter strip (above all content)
```

**AQI Dashboard Router (inside `dashboards/aqi/__init__.py`):**  
Identical routing architecture with AQI-specific page modules and filter state.

---

## 3.3 · Page Module Structure

Every page module follows the same internal structure contract:

```python
# Every page module exports one function: render()
# render() has no parameters — it reads everything from session state

def render():
    # 1. Read current filter state from session state
    # 2. Load and filter the required datasets (from data_layer, cached)
    # 3. Render page hero section (from components.hero_section)
    # 4. Render layout containers (st.columns, st.container)
    # 5. Call chart render functions with filtered data
    # 6. Render insight panels if applicable
    # 7. Handle drilldown state (detail panels, dynamic content)
```

**What page modules do NOT contain:**
- Data cleaning or transformation logic
- Raw `st.sidebar` or `st.columns` for filters (filter panel is a component)
- Repeated Plotly layout boilerplate
- Inline CSS strings
- Business logic (mean calculations, derived column formulas)

---

## 3.4 · Tab Navigation Architecture

Navigation tabs are rendered by the dashboard router, not by individual page modules. This ensures the tab bar is always present and consistent regardless of which page is active.

**Tab state management:**

```
session_state["traffic_active_tab"] = 0   # default to Page 1
session_state["aqi_active_tab"] = 0

Tab click → updates session_state["*_active_tab"] → router re-runs → correct page renders
```

**Advanced Lab tab handling:**
The router checks `session_state["*_lab_gate_passed"]` before rendering Page 6. If `False`, the lab gate component renders instead of the page content.

---

## 3.5 · Cross-Dashboard Navigation

When the user switches between Traffic and AQI dashboards:
- The switcher updates `session_state["active_dashboard"]`
- The opposing dashboard's filter state is **preserved** (not cleared)
- The opposing dashboard's active tab is **preserved**
- Only the primary dashboard filter interactions (area click, AQI category click) that directly cross dashboards need to be explicitly mapped

---

# PART 4 — VISUALIZATION SYSTEM ARCHITECTURE

---

## 4.1 · Chart Module Contract

Every chart module (e.g., `t08_incident_cliff.py`) exports exactly one public function: `render(data, config=None)`.

```
render(data, config=None) contract:
  - data: a pre-filtered, pre-aggregated Pandas DataFrame
    (the caller — the page module — is responsible for filtering)
  - config: optional dict for chart-level overrides (height, color_override, etc.)
  - returns: a Plotly Figure object (or Altair Chart object)
  - NEVER calls st.plotly_chart() internally
  - NEVER accesses session_state
  - NEVER loads data
  - NEVER runs a groupby or aggregation (data arrives ready)
```

The **page module** is responsible for: loading data, applying filters, running aggregations, calling chart render functions, and calling `st.plotly_chart(fig)`. The **chart module** is responsible only for: constructing the figure.

This separation means:
- Chart modules are independently testable
- Page modules can swap charts without touching data logic
- Data layer can change without touching chart modules

---

## 4.2 · Base Chart Configuration System

`config/chart_defaults.py` defines a `BASE_LAYOUT` dictionary — the shared Plotly layout applied to every chart as a starting point.

**BASE_LAYOUT covers:**
- `paper_bgcolor` and `plot_bgcolor` (from theme tokens)
- `font` family, size, and color (from typography tokens)
- `margin` defaults (from spacing tokens)
- `hoverlabel` styling (background, font, border)
- `legend` position and styling defaults
- `colorway` (dashboard-specific color sequences)
- `xaxis` and `yaxis` defaults (gridcolor, zeroline, tickfont)

**Usage pattern in chart modules:**

```
Every chart module:
  1. Imports BASE_LAYOUT from config.chart_defaults
  2. Creates a deep copy: layout = deepcopy(BASE_LAYOUT)
  3. Updates only chart-specific overrides
  4. Applies to fig.update_layout(**layout)
```

This means changing the dark background across all 30 charts is a one-line edit in `chart_defaults.py`.

---

## 4.3 · Shared Plotly Helper Utilities (`utils/plotly_helpers.py`)

These are functions that construct Plotly elements that appear in multiple charts:

| Helper Function | Used By |
|---|---|
| `add_threshold_line(fig, y, label, color)` | T-09, A-08, A-09, A-04, A-05 |
| `add_quadrant_lines(fig, x_val, y_val)` | T-05, A-06, A-13 |
| `add_reference_band(fig, y_low, y_high, color, label)` | T-08, T-09, A-05 |
| `build_hover_template(fields, labels)` | All charts |
| `style_axis(axis_dict, title, show_grid)` | All charts |
| `add_annotation_callout(fig, x, y, text)` | T-08, T-09, A-11, A-12 |
| `apply_animation_reveal(fig, n_traces)` | Charts with staggered reveal |
| `build_color_scale(low_color, high_color, n_steps)` | T-06, T-12, A-06, A-14 |

---

## 4.4 · Shared Altair Helper Utilities (`utils/altair_helpers.py`)

| Helper Function | Used By |
|---|---|
| `build_ridgeline_base(data, x_col, group_col)` | T-11, A-03 |
| `add_aqi_color_scale()` | A-02, A-03, A-15 |
| `build_pairplot_base(data, var_cols, color_col)` | A-15 |
| `kde_layer(data, col, offset, color)` | T-11, A-03 |

---

## 4.5 · Annotation Architecture (`utils/annotations.py`)

Annotations are text overlays, callout boxes, and reference labels that appear across many charts. They are never hardcoded inside individual chart modules.

**Annotation types and their factory functions:**

```
StepCallout(x, y, delta_text, color)     → T-08 "+21.5 pts" callout
ThresholdLabel(y, label, side)           → T-09 congestion=75 label
QuadrantLabel(x, y, archetype_text)      → T-05, A-06, A-13 quadrant names
RegimeAnnotation(x, y, regime_name)      → A-13 atmospheric state labels
AQIBandLabel(y, category_name)           → A-04, A-05, A-08 threshold labels
InsightCallout(x, y, text, arrow_dir)    → A-11 "Resuspension Zone" label
```

Every factory function returns a Plotly `go.layout.Annotation` dict — ready to append to `fig.layout.annotations`.

---

## 4.6 · Chart Sizing Architecture

Chart heights are not hardcoded inside chart modules. They are managed through a sizing constant system in `config/chart_defaults.py`:

```
CHART_SIZES = {
    "hero_full":      600,   # Full-width hero (T-01 scorecard, A-02 calendar)
    "hero_half":      500,   # Half-width hero (T-05, T-08, A-03, A-08)
    "supporting":     400,   # Supporting / second-row charts
    "compact":        300,   # Compact: bubble matrix, step charts
    "ridgeline":      700,   # Tall ridgelines (T-11: 16 roads, A-03: 4 seasons)
    "pairplot":       800,   # Large pairplot matrix
    "radar":          550,   # Radar/spider charts
    "heatmap_small":  350,   # 5×2 heatmaps, small-multiple grids
}
```

Page modules pass the appropriate size key to the chart container component, which passes the height value to `st.plotly_chart(fig, use_container_width=True, height=h)`.

---

# PART 5 — DATA ORGANIZATION ARCHITECTURE

---

## 5.1 · The Four-Layer Data Model

```
Layer 0: RAW
  data/raw/traffic_raw.csv
  data/raw/aqi_raw.csv
  Never touched after initial load. Source of truth.

Layer 1: CLEANED
  data_layer/cleaners.py → produces cleaned DataFrames
  Actions: type casting, null handling, column renaming, outlier flagging
  Cached on disk as Parquet: data/processed/

Layer 2: TRANSFORMED (DERIVED)
  data_layer/traffic_transforms.py
  data_layer/aqi_transforms.py
  Actions: derived columns, groupbys, pivot tables, aggregations
  Results cached in memory via @st.cache_data

Layer 3: VISUALIZATION-READY
  Page modules apply filter state to Layer 2 outputs
  Result: a small, filtered DataFrame passed directly to a chart render function
  No caching — filtering is fast on small Pandas DataFrames
```

---

## 5.2 · Data Loading Architecture (`data_layer/loaders.py`)

All dataset loading is centralized in `loaders.py`. Every loading function is decorated with `@st.cache_data` and loads from Parquet (not CSV) for performance.

```
load_traffic_clean()    → returns cleaned traffic DataFrame (8,936 rows)
load_aqi_clean()        → returns cleaned AQI DataFrame (1,095 rows)
```

**Cache invalidation strategy:**  
`@st.cache_data(ttl=None)` — no TTL because these are static analytical datasets. Cache persists for the session lifetime. If the underlying data file changes, the Streamlit server must restart to invalidate.

---

## 5.3 · Derived Dataset Architecture (`data_layer/traffic_transforms.py`)

Each transformation function is independently cached. Expensive group-bys are computed once per session.

**Traffic derived datasets:**

| Function | Output | Used By |
|---|---|---|
| `get_area_summary()` | Area-level means: congestion, speed, incidents, capacity, pedestrians | T-02, T-13, Page 1 |
| `get_monthly_area_congestion()` | Monthly × Area congestion pivot | T-03, T-15 |
| `get_weekly_distribution()` | Congestion by day-of-week | T-04 |
| `get_road_stats()` | Road-level: mean, std, % at max cap, mean traffic volume | T-05, T-07, T-11 |
| `get_area_environmental_burden()` | Area × Road environmental impact | T-06 |
| `get_incident_congestion_bands()` | Incident count bands → mean congestion | T-08 |
| `get_congestion_speed_scatter()` | Full record-level congestion × speed × area | T-09 |
| `get_pt_quartile_summary()` | PT usage quartile → congestion, speed, TTI, incidents (weak observable relationship — interpret with caution) | T-10 |
| `get_road_congestion_distributions()` | Road-level full congestion value arrays | T-11 |
| `get_weather_roadwork_matrix()` | Weather × Roadwork → mean incidents, mean congestion | T-12 |
| `get_monthly_bubble_data()` | Month × Area → mean congestion, incidents, % at max | T-15 |
| `get_traffic_volume_congestion()` | Full traffic volume × congestion array | T-14 |

**AQI derived datasets:**

| Function | Output | Used By |
|---|---|---|
| `get_aqi_summary_stats()` | WHO exceedance rate, category distribution, mean PM2.5 | A-01 |
| `get_daily_aqi_calendar()` | Date × PM2.5 × AQI category for all 1,095 days | A-02, A-05 |
| `get_seasonal_pm25_distributions()` | Season → array of PM2.5 values | A-03 |
| `get_monthly_pm25_stats()` | Month → mean ± SD PM2.5 | A-04 |
| `get_slp_vv_scatter()` | SLP × VV × PM2.5 for all days | A-06, A-13 |
| `get_aqi_category_profiles()` | Severe/Average/Good → normalized meteorological vectors | A-07 |
| `get_tm_pm25_scatter()` | Tm × PM2.5 × AQI category for all days | A-08 |
| `get_slp_band_season_summary()` | SLP band × Season → mean PM2.5 | A-09 |
| `get_wind_season_summary()` | Wind speed band × Season → mean PM2.5 | A-10 |
| `get_gust_ratio_quintiles()` | Gust ratio quintile → mean PM2.5 ± CI | A-11 |
| `get_temp_spread_bands()` | Temp spread band → mean PM2.5 + distributions | A-12 |
| `get_atmospheric_regime_data()` | 4-regime classified dataset with PM2.5 | A-13 |
| `get_season_slp_vv_grid()` | Season × SLP band × VV band → mean PM2.5 | A-14 |
| `get_full_met_pairplot_data()` | All meteorological variables + AQI category | A-15 |

---

## 5.4 · Derived Column Registry

All derived columns are computed in `cleaners.py` or `*_transforms.py` and documented in `config/data_config.py`. No chart module ever computes a derived column — it arrives pre-computed in the DataFrame.

**Traffic derived columns (computed in `cleaners.py`):**

| Column Name | Source Formula | Used By |
|---|---|---|
| `day_of_week` | `pd.to_datetime(Date).dt.day_name()` | T-04 |
| `month_year` | `Date.dt.to_period('M')` | T-03, T-15 |
| `at_max_capacity` | `Road_Capacity_Utilization >= 99.5` (bool) | T-05, T-15 |
| `flow_instability_index` | `Congestion_Level.std() / Congestion_Level.mean()` (road-level) | T-05 |
| `environmental_impact` | `(Congestion_Level * 0.6 + Road_Capacity_Utilization * 0.4)` | T-06 |

**AQI derived columns (computed in `cleaners.py`):**

| Column Name | Source Formula | Used By |
|---|---|---|
| `aqi_category` | Binned PM2.5 into 6 WHO/India NAAQS bands | All AQI charts |
| `season` | Month → Winter/Spring/Monsoon/Post-Monsoon | A-03, A-09, A-10, A-14 |
| `temp_spread` | `TM - Tm` | A-12 |
| `gust_ratio` | `VM / V` (with zero-division guard) | A-11 |
| `slp_band` | Binned SLP: Low/Normal/High | A-09, A-13, A-14 |
| `vv_band` | Binned VV: Low/Moderate/High | A-13, A-14 |
| `wind_band` | Binned V: Calm/Moderate/Strong | A-10 |
| `rolling_7d_pm25` | `PM_2_5.rolling(7).mean()` | A-05 |

---

# PART 6 — FILTER & INTERACTION ARCHITECTURE

---

## 6.1 · Session State Schema

All filter and interaction state lives in `st.session_state`. Initialized by `filters/state.py` on first app load.

**Traffic Session State:**

```python
TRAFFIC_STATE_DEFAULTS = {
    # Navigation
    "traffic_active_tab": 0,
    "traffic_lab_gate_passed": False,

    # Global filters
    "traffic_date_start": datetime(2022, 1, 1),
    "traffic_date_end": datetime(2024, 8, 31),
    "traffic_selected_areas": [],           # [] means all areas selected
    "traffic_filters_active": False,

    # Chart interaction state (drilldown)
    "traffic_selected_road": None,          # From T-05 click
    "traffic_selected_area": None,          # From T-02 line click
    "traffic_selected_month": None,         # From T-15 bubble click

    # Cross-chart synchronization
    "traffic_t03_zoom_start": None,
    "traffic_t03_zoom_end": None,
}
```

**AQI Session State:**

```python
AQI_STATE_DEFAULTS = {
    # Navigation
    "aqi_active_tab": 0,
    "aqi_lab_gate_passed": False,

    # Global filters
    "aqi_date_start": datetime(2021, 1, 1),
    "aqi_date_end": datetime(2023, 12, 31),
    "aqi_selected_categories": [],          # [] means all AQI categories
    "aqi_selected_seasons": [],             # [] means all seasons
    "aqi_filters_active": False,

    # Chart interaction state
    "aqi_selected_date": None,              # From A-02 calendar click
    "aqi_selected_month": None,             # From A-04 click
    "aqi_selected_regime": None,            # From A-13 click
    "aqi_selected_season": None,            # From A-03 ridge click
}
```

---

## 6.2 · Filter Panel Component Architecture

The global filter strip (`components/filter_panel.py`) is a single component called at the top of every page render. It reads and writes session state. It never passes filter values as return values — it modifies state directly, which triggers a Streamlit re-run.

**Filter Panel internal structure:**

```
filter_panel(dashboard="traffic"):
  1. Render date range selector → updates state["*_date_start"], state["*_date_end"]
  2. Render area multiselect (Traffic) OR AQI category multiselect (AQI)
  3. Render season filter (AQI only)
  4. Render "Reset All Filters" button → calls reset_filters(dashboard)
  5. Update state["*_filters_active"] = True if any filter is non-default
  6. Render filter-active indicator strip if filters_active is True
```

---

## 6.3 · Filter Application Pattern

Every page module applies filters using the centralized filter utility functions in `filters/traffic_filters.py` or `filters/aqi_filters.py`.

**Pattern:**

```python
# In page module:
df = load_traffic_clean()                              # cached, full dataset
df = apply_traffic_filters(df, st.session_state)       # filter function in filters/

# apply_traffic_filters():
#   - applies date range filter
#   - applies area filter if any areas selected
#   - returns filtered DataFrame
```

**Never:**

```python
# BAD — never do this in a page module
df = df[df["Date"] >= st.session_state["traffic_date_start"]]
df = df[df["Area Name"].isin(st.session_state["traffic_selected_areas"])]
```

The filter logic is centralized. If the filter behavior needs to change (e.g., "date filter should not apply to T-04 violin"), that exception is handled in `apply_traffic_filters()` with an optional `exclude_date_filter` parameter — not by adding an if-statement inside the page module.

---

## 6.4 · Drilldown Interaction Architecture

Plotly in Streamlit does not natively fire events on chart click. Drilldown interactions are implemented using Streamlit's `on_click` pattern with `plotly_events` (streamlit-plotly-events library) or Streamlit's experimental click event support.

**Drilldown flow architecture:**

```
User clicks a road bubble in T-05
  ↓
streamlit_plotly_events() captures click → returns {point_index, curve_number}
  ↓
Page module extracts road name from click data
  ↓
Updates session_state["traffic_selected_road"] = road_name
  ↓
Streamlit re-run triggered
  ↓
Page module reads selected_road from state
  ↓
T-07 (diverging bar) highlights that road
T-06 (treemap) highlights that area
Road Detail Panel populates with that road's stats
```

**Drilldown state clearing:**  
Clicking the same point again, clicking "Reset All Filters," or navigating to a different page clears drilldown state for the relevant drilldown key.

---

## 6.5 · Cross-Chart Synchronization Architecture

Cross-chart synchronization is implemented through **shared session state keys**, not through Plotly's native relayout events. Each chart reads the relevant state keys and applies highlighting, filtering, or emphasis based on current state.

**Cross-chart synchronization map:**

```
State Key                        → Charts That Read It
─────────────────────────────────────────────────────────
traffic_selected_area            → T-03, T-04, T-07, T-11, T-15
traffic_selected_road            → T-06, T-07, Detail Panel
traffic_t03_zoom_start/end       → T-15 (month window sync)
aqi_selected_categories          → A-02, A-05, A-03
aqi_selected_season              → A-04, A-05, A-10
aqi_selected_date                → Month Detail Panel
aqi_selected_regime              → A-14, A-11
```

**Synchronization is applied at the data layer, not the chart layer:**  
When `traffic_selected_area = "Koramangala"`, the page module passes a filtered DataFrame (only Koramangala rows) to T-04. The chart itself does not know a selection occurred — it simply renders whatever data it receives. This keeps chart modules clean.

---

# PART 7 — THEME & COMPONENT ARCHITECTURE

---

## 7.1 · Color Token System (`config/theme.py`)

All colors exist as named constants. Chart modules never use hex strings directly — they import from theme.

**Dashboard Identity Colors:**

```python
# Traffic Dashboard
TRAFFIC_BG           = "#0D1117"    # Page background
TRAFFIC_SURFACE      = "#161B22"    # Card / container surface
TRAFFIC_BORDER       = "#30363D"    # Subtle border
TRAFFIC_CRIMSON      = "#E5383B"    # High severity / crisis
TRAFFIC_AMBER        = "#FFBA08"    # Medium severity / alert
TRAFFIC_TEAL         = "#2EC4B6"    # Low severity / relief
TRAFFIC_TEXT_PRIMARY = "#F0F6FC"
TRAFFIC_TEXT_MUTED   = "#8B949E"

# AQI Dashboard
AQI_BG           = "#0A0F1E"        # Deep navy page background
AQI_SURFACE      = "#111827"        # Card surface
AQI_BORDER       = "#1F2937"        # Subtle border
AQI_NAVY         = "#1E3A5F"        # Atmospheric depth color
AQI_TEXT_PRIMARY = "#E5E7EB"
AQI_TEXT_MUTED   = "#6B7280"

# AQI Category Color Scale
AQI_COLOR_GOOD         = "#00B050"   # Green
AQI_COLOR_SATISFACTORY = "#92D050"   # Light green
AQI_COLOR_MODERATE     = "#FFFF00"   # Yellow
AQI_COLOR_POOR         = "#FF7C00"   # Orange
AQI_COLOR_VERY_POOR    = "#FF0000"   # Red
AQI_COLOR_SEVERE       = "#7030A0"   # Near-black purple
```

**Shared Design Tokens:**

```python
FONT_FAMILY  = "'Inter', 'Segoe UI', sans-serif"
FONT_MONO    = "'JetBrains Mono', 'Fira Code', monospace"

FONT_SIZE_KPI      = 36
FONT_SIZE_HEADING  = 20
FONT_SIZE_LABEL    = 13
FONT_SIZE_CAPTION  = 11

SPACING_XS  = 4
SPACING_SM  = 8
SPACING_MD  = 16
SPACING_LG  = 24
SPACING_XL  = 40
```

---

## 7.2 · Streamlit Global Theme (`.streamlit/config.toml`)

```toml
[theme]
base = "dark"
primaryColor = "#E5383B"           # Traffic: crimson / overridden per dashboard
backgroundColor = "#0D1117"
secondaryBackgroundColor = "#161B22"
textColor = "#F0F6FC"
font = "sans serif"
```

The config.toml handles Streamlit's native widget styling. Chart styling is handled by `chart_defaults.py`. Component styling is handled by targeted `st.markdown()` with `unsafe_allow_html=True` using structured inline styles derived from theme tokens — never raw CSS files.

---

## 7.3 · Reusable Component Architecture

Each component in `components/` follows the same contract:
- Takes content and configuration parameters
- Reads theme tokens internally (never from caller)
- Returns nothing — it renders directly via `st.markdown()` / `st.plotly_chart()` / `st.columns()`
- Has no side effects on session state (filter_panel.py is the only exception)

---

### KPI Card Component (`components/kpi_card.py`)

```
kpi_card(
    label: str,
    value: str,
    delta: str = None,
    delta_positive: bool = None,
    gauge_percent: float = None,
    severity: str = "neutral",     # "critical" | "warning" | "safe" | "neutral"
    size: str = "normal"           # "normal" | "large" | "compact"
)
```

Renders a dark-background card containing:
- Metric label (muted text, small)
- Metric value (large, bold, severity-colored)
- Optional delta (with ▲/▼ indicator and color)
- Optional animated radial gauge ring (SVG-based, fills clockwise)

**Severity → Color mapping** is handled internally using theme tokens — caller only specifies semantic severity, not hex codes.

---

### Metric Strip Component (`components/metric_strip.py`)

```
metric_strip(metrics: list[dict])
# metrics = [{"label": str, "value": str, "severity": str}, ...]
```

Renders a horizontal row of compact KPI cards. Used for supporting metrics below hero charts. Internally calls `kpi_card()` in compact size for each metric in the list.

---

### Hero Section Component (`components/hero_section.py`)

```
hero_section(
    title: str,
    subtitle: str = None,
    severity_badge: str = None,     # e.g., "CRITICAL" — renders colored badge
    dashboard: str = "traffic"      # controls color identity
)
```

Renders the page title block: dashboard identity strip, page title, optional subtitle, optional severity badge. This is the topmost element on every page, below the global filter strip.

---

### Chart Container Component (`components/chart_container.py`)

```
chart_container(
    fig,                            # Plotly Figure or Altair Chart
    title: str,
    caption: str = None,
    height: int = None,             # from CHART_SIZES constant if not provided
    fullscreen_key: str = None,     # if provided, renders fullscreen toggle button
    use_container_width: bool = True
)
```

Wraps every chart render with:
- Chart title (styled label above the chart)
- `st.plotly_chart()` or `st.altair_chart()` call
- Optional caption line below the chart (finding summary)
- Optional fullscreen toggle (used in Advanced Lab)

**This is the only place `st.plotly_chart()` is called.** Page modules never call it directly.

---

### Collapsible Section Component (`components/collapsible_section.py`)

```
collapsible_section(
    label: str,
    key: str,                       # unique session state key for expand state
    default_expanded: bool = False,
    content_fn: callable            # function that renders the content
)
```

Uses `st.expander()` internally. The `content_fn` is called only when the section is expanded — this enables lazy rendering of expensive charts.

---

### Insight Panel Component (`components/insight_panel.py`)

```
insight_panel(
    heading: str,
    body: str,
    severity: str = "neutral",
    collapsible: bool = True,
    key: str = None
)
```

Renders the "What This Means" panel that appears below CRITICAL charts. If `collapsible=True`, it uses `st.expander()` collapsed by default. Contains plain-English interpretation of the chart's core finding. Text is passed as a parameter from the page module — never hardcoded inside the component.

---

### Advanced Lab Gate Component (`components/lab_gate.py`)

```
lab_gate(
    dashboard: str,                 # "traffic" or "aqi"
    page_content_fn: callable       # the actual page render function
)
```

**Logic:**
1. Checks `session_state["*_lab_gate_passed"]`
2. If `False`: renders the gate card overlay — title, explanation text, two buttons
3. "Enter Lab" button: sets `session_state["*_lab_gate_passed"] = True` → re-run → `page_content_fn()` is called
4. "← Go Back" button: sets `session_state["*_active_tab"] = 0` → re-run → navigates to Page 1
5. If `True`: calls `page_content_fn()` directly

---

### Detail Panel Component (`components/detail_panel.py`)

```
detail_panel(
    title: str,
    metrics: list[dict],
    notes: str = None,
    visible: bool = True
)
```

Renders the dynamic drilldown detail panel (Road Detail Panel for Traffic, Month Detail Panel for AQI). `visible` controls whether the panel renders at all — page modules pass `visible = (session_state["traffic_selected_road"] is not None)`.

---

# PART 8 — ADVANCED ANALYTICS ARCHITECTURE

---

## 8.1 · Advanced Lab Page Structure

Both `p6_advanced_lab.py` page modules follow a modified structure:

```python
def render():
    # 1. Lab gate check handled by lab_gate component (called by router)
    # 2. Render lab header strip (lab_header component)
    # 3. Render "← Return to Dashboard" breadcrumb
    # 4. Render local filter controls (Lab has its own filter row — area/AQI category toggles)
    # 5. Load and prepare data (no global date filter applied in Lab — full dataset used)
    # 6. Render primary advanced visualization (radar or pairplot)
    # 7. Render interpretation panel
```

---

## 8.2 · Radar Chart Architecture (T-13, A-07)

**T-13 · Compound Stress Radar — Engineering Notes:**

Data preparation (`get_area_summary()` → normalize each of 6 metrics to 0–100 scale where 100 = worst):
- Normalization mapping is defined once in `data_layer/traffic_transforms.py`
- 8 areas × 6 normalized metrics → 8×6 matrix
- Each area becomes one `go.Scatterpolar` trace

Interactive toggle design:
- Each area has a corresponding `st.checkbox()` in a sidebar-style column
- Checking/unchecking updates `session_state["traffic_radar_visible_areas"]`
- The chart render function receives only the visible areas' data

**Readability and Comparison Safeguards:**

*Overlay limit:* Maximum 4 polygon overlays rendered simultaneously. When the user attempts to enable a 5th area, a warning renders inline ("Limit reached — deselect an area to compare another"). This prevents illegible polygon stacking across all 8 areas.

*Comparison modes:* The Lab control panel exposes two quick-select modes alongside individual checkboxes:
- **Top-N mode** — auto-selects the N highest-stress areas (ranked by composite normalized score); default N = 3
- **Bottom-N mode** — auto-selects the N lowest-stress areas; useful for baseline contrast

*Focus-area selection:* A "Focus Area" radio below the checkboxes pins one area as the primary trace (rendered at full opacity, thicker stroke). All other visible areas render as secondary context.

*Visibility toggles:* Each checkbox row includes a visibility-only toggle (eye icon) that dims a trace without removing it from the overlay count. Dimmed traces render at 15% opacity — present but non-dominant.

*Inactive overlay fading:* When a focus area is selected, non-focus visible traces automatically reduce to 20% opacity. Hovering a non-focus trace temporarily raises it to 60% opacity for inspection.

Session state additions for safeguard behavior:
```python
"traffic_radar_visible_areas": [],        # active area list (max 4)
"traffic_radar_focus_area": None,         # pinned primary trace
"traffic_radar_dimmed_areas": [],         # visibility-toggled (eye-off) areas
"traffic_radar_comparison_mode": None,    # "top_n" | "bottom_n" | None
"traffic_radar_comparison_n": 3,          # N value for top/bottom modes
```

**A-07 · Extreme Day Radar — Engineering Notes:**
- 3 traces (Severe / Average / Good) always rendered
- AQI category filter from global state controls which categories are shown
- 6 meteorological axes normalized so that larger = worse (requires reversal for temperature and visibility)

---

## 8.3 · Pairplot Architecture (A-15)

The 6×6 pairplot is the most performance-sensitive chart in the platform.

**Implementation approach — Altair over Plotly:**  
Use Altair's `Chart.encode()` with `mark_circle()` for scatter panels and `mark_area()` for diagonal KDE panels. Altair's declarative grammar handles the grid layout natively with `repeat()` or `facet()`.

**Performance mitigations for A-15:**
- Data passed is the full 1,095-row AQI dataset — small enough that sampling is unnecessary
- Diagonal KDE panels are pre-computed as binned histograms (not real KDE), reducing render time
- AQI category toggle filters the dataset before passing to chart — fewer points per toggle
- Fullscreen toggle via `chart_container(fullscreen_key="a15_pairplot")` expands the chart to use full page width

**Altair pairplot implementation structure:**

```
build_pairplot(data, variables, color_col):
  1. Define variable list: [T, Tm, SLP, H, VV, V, PM_2_5]
  2. Build base selection: AQI category color encoding
  3. Build scatter spec for off-diagonal cells
  4. Build KDE/histogram spec for diagonal cells
  5. Compose with altair.concat() in a 6×6 grid
  6. Apply shared color scale (AQI_COLOR_* tokens)
  7. Return Altair Chart object
```

---

## 8.4 · Fullscreen Visualization Strategy

The fullscreen toggle in `chart_container()` works by:

1. Storing expand state in `session_state["*_fullscreen"]` (bool)
2. When `True`: the chart renders inside a full-width `st.container()` that consumes the entire page column (all other page content is hidden via conditional rendering)
3. A "← Collapse" button restores normal layout

**Affected charts (fullscreen-eligible):**  
T-13 · Radar, T-02 · Parallel Coordinates, A-15 · Pairplot, A-02 · Calendar Heatmap

---

## 8.5 · Parallel Coordinates Architecture (T-02)

T-02 is the most interaction-rich chart in the Traffic dashboard.

**Implementation with `go.Parcoords`:**
- 5 axes, 8 area-colored lines
- `constraintrange` attribute enables native Plotly axis brushing (filter by dragging on an axis)
- Brushed constraint ranges are captured via `plotly_events` and stored in session state
- When constraints are active, T-02 is considered a "local filter" source — it filters only the Area Insight Sidebar, not the global area filter

**UX Readability Safeguards:**

*Hover isolation:* On line hover, the hovered area's line raises to full opacity and increases stroke weight. All other lines reduce to 10% opacity for the duration of the hover.

*Focus highlighting:* If `traffic_selected_area` is set in session state (from a cross-chart click), that area's line is pre-highlighted at full opacity on render. All other lines render at 35% opacity as passive context.

*Default axis visibility:* On initial render, show 3 axes only (Congestion Level, Speed, Incident Reports — highest operational relevance). The remaining 2 axes (Capacity Utilization, Pedestrian Count) are present but collapsed behind a "Show More Axes" toggle. This reduces initial visual density without removing data.

*Opacity fading for brushed state:* When a `constraintrange` brush is active on any axis, lines falling outside the brushed range reduce to 8% opacity. Lines within range remain at full opacity.

**Tablet adaptation:**
On tablet widths, the parallel coordinates chart drops from 5 axes to 3 (Congestion, Speed, Incidents — the most operationally relevant). A "Show More Axes" button adds the remaining two.

---

# PART 9 — PERFORMANCE OPTIMIZATION STRATEGY

---

## 9.1 · Caching Strategy

**Three levels of caching:**

```
Level 1: @st.cache_data — Data Loading
  load_traffic_clean()        → 8,936 rows · loads once per session
  load_aqi_clean()            → 1,095 rows · loads once per session
  TTL: None (static datasets)

Level 2: @st.cache_data — Expensive Transformations
  get_area_summary()          → 8×6 aggregation matrix · cache_data
  get_road_stats()            → 16×5 road-level stats · cache_data
  get_monthly_area_congestion() → 32×8 pivot · cache_data
  get_daily_aqi_calendar()    → 1,095 row preprocessed · cache_data
  get_full_met_pairplot_data() → 1,095×7 normalized · cache_data
  TTL: None (static datasets)

Level 3: No cache — Filter Application
  apply_traffic_filters(df, state)  → fast Pandas boolean masking · no cache
  apply_aqi_filters(df, state)      → fast Pandas boolean masking · no cache
  (Caching filter results would cause stale-state bugs)
```

**Cache invalidation note:**  
Because all datasets are static and session-lifetime cached, the only way to refresh data is a server restart. This is correct behavior for an analytical dashboard — not a live system.

---

## 9.2 · Lazy Rendering Strategy

**Collapsible sections (T-12, T-15 on Traffic; A-14 on AQI) use the `content_fn` pattern:**

```python
collapsible_section(
    label="OPERATIONAL RISK SCHEDULING · Weather × Roadwork",
    key="t12_expand",
    default_expanded=False,
    content_fn=lambda: chart_container(render_t12(filtered_data), ...)
)
```

Because `content_fn` is a lambda, `render_t12()` is never called until the section is expanded. This prevents the 5×2 heatmap from computing on every page load.

**Advanced Lab (Page 6) lazy loading:**  
The Advanced Lab page is never rendered until the user navigates to Tab 6 AND passes the gate. Streamlit's page routing ensures that importing a page module does not execute its `render()` function. The pairplot and radar are never computed during Pages 1–5 navigation.

---

## 9.3 · Chart-Specific Performance Notes

| Chart | Risk | Mitigation |
|---|---|---|
| T-02 · Parallel Coordinates | Slow with many traces | 8 traces only — manageable. Pre-aggregate to area level before passing. |
| T-11 · Ridgeline (16 roads) | KDE computation on 16 distributions | Pre-compute KDE arrays in `get_road_congestion_distributions()`; pass arrays to chart, not raw data |
| T-14 · Hexbin | Point density computation | Use Plotly `histogram2d` (server-side binning) rather than computing bins in Python |
| A-02 · Calendar Heatmap | 1,095 individual cells | Pre-compute the calendar grid structure in `get_daily_aqi_calendar()`; chart receives a pre-shaped DataFrame |
| A-06 · Stagnation Hexbin | Same as T-14 | Same mitigation: `histogram2d` |
| A-15 · Pairplot | 36 sub-panels, 1,095 points each | Altair renders client-side; pre-normalize all columns; diagonal panels use histogram bins not KDE |
| A-13 · Atmospheric States | Inset charts inside main chart | Insets are separate `st.plotly_chart()` calls placed in a sub-column, not literally inside the Plotly figure |

---

## 9.4 · Visualization Complexity Classification

All 30 dashboard visualizations are classified by rendering complexity. This classification drives lazy loading decisions, rendering priority, and optimization focus — not visual design.

**Classification tiers:**

| Tier | Definition |
|---|---|
| **Simple** | Static or near-static; minimal trace count; no interaction dependencies; fast render unconditionally |
| **Moderate** | Multi-trace or multi-facet; light aggregation; interaction-aware but low re-render cost |
| **Heavy** | Large trace counts, polygon overlays, or dense point clouds; benefits from lazy loading and cache hits |
| **Extreme** | Multi-panel grids, client-side rendering, or full-dataset scatter at axis scale; must be isolated in Advanced Lab or collapsed by default |

**Traffic Dashboard classifications:**

| Chart | Tier | Rationale |
|---|---|---|
| T-01 · Saturation Scorecard | Simple | KPI cards + gauge rings; no chart figure |
| T-02 · Parallel Coordinates | Heavy | 8 area lines × 5 axes; hover isolation adds re-render cost; fullscreen-eligible |
| T-03 · Stream Graph | Moderate | 8 stacked area traces; 32-month axis; animation on load |
| T-04 · Violin Weekly | Moderate | 7 violin traces; day-level distribution; no interaction dependencies |
| T-05 · Quadrant Scatter | Moderate | 16 road bubbles; click drilldown; quadrant annotations |
| T-06 · Burden Treemap | Moderate | ~50 cells (8 areas × roads); color-scaled; click-driven highlight |
| T-07 · Mobility Exclusion | Simple | 16-bar diverging chart; pre-aggregated; no interaction cost |
| T-08 · Incident Cliff | Simple | 6 step bars; 2 annotations; static once rendered |
| T-09 · Speed Threshold | Moderate | 8,936 scatter points; color by area; threshold line overlay |
| T-10 · PT Decoupling | Simple | 4 quartile bars × 4 metrics; grouped bar; lightweight |
| T-11 · Ridgeline | Heavy | 16 KDE distributions; Altair rendering; tall chart; pre-computation required |
| T-12 · Weather Heatmap | Moderate | 5×2 cell grid; color-scaled; collapsible (lazy) |
| T-13 · Compound Radar | Heavy | Up to 4 polygon overlays; opacity management; comparison modes; Advanced Lab only |
| T-14 · Density Hexbin | Heavy | 8,936 raw points → histogram2d binning; server-side but dense |
| T-15 · Bubble Matrix | Moderate | ~256 bubbles (32 months × 8 areas); collapsible (lazy) |

**AQI Dashboard classifications:**

| Chart | Tier | Rationale |
|---|---|---|
| A-01 · Crisis Scorecard | Simple | KPI cards only |
| A-02 · Calendar Heatmap | Heavy | 1,095 individual cells; date grid construction; fullscreen-eligible |
| A-03 · Seasonal Ridgeline | Moderate | 4 KDE distributions; Altair; seasonal color encoding |
| A-04 · Monthly Variability | Simple | 12 bar + error bar traces; static |
| A-05 · Persistence Series | Moderate | Time series + rolling average; threshold band; 1,095 points |
| A-06 · Stagnation Hexbin | Heavy | 1,095 scatter points → histogram2d; same pattern as T-14 |
| A-07 · Extreme Day Radar | Simple | 3 traces only; fixed axes; no overlay management needed |
| A-08 · Temperature Scatter | Moderate | 1,095 scatter points; AQI color encoding; threshold line |
| A-09 · Pressure Trigger | Moderate | Grouped bars × 4 seasons; pre-aggregated |
| A-10 · Wind Rescue | Simple | Grouped bars; 3 wind bands × 4 seasons; pre-aggregated |
| A-11 · Gust Paradox | Simple | 5 quintile bars + CI error bars; annotation callout |
| A-12 · Temp Spread | Simple | 4 band bars + distribution overlay; annotation |
| A-13 · Atmospheric States | Heavy | Scatter + 4 quadrant zones + inset sub-charts; complex layout |
| A-14 · Season × Pressure Grid | Moderate | 3×4 faceted heatmap grid; collapsible (lazy) |
| A-15 · Full Met Pairplot | Extreme | 36 sub-panels; 1,095 points per panel; Altair client-side; Advanced Lab only |

**Implementation guidance by tier:**

- **Simple** — render eagerly on page load; no special handling required
- **Moderate** — render eagerly; ensure transform function is cached; no lazy loading needed
- **Heavy** — wrap in `collapsible_section` with `default_expanded=False` unless it is the page's primary hero chart; verify cache hit before every render
- **Extreme** — Advanced Lab placement mandatory; fullscreen toggle required; never render outside Tab 6

---

## 9.5 · Conditional Rendering for Drilldown Content

Detail panels and dynamic content are conditionally rendered based on session state — they produce no DOM content (and trigger no computation) when their display condition is False.

```python
# In page module — never render empty containers
if st.session_state.get("traffic_selected_road"):
    detail_panel(
        title=st.session_state["traffic_selected_road"],
        metrics=get_road_detail(st.session_state["traffic_selected_road"]),
        visible=True
    )
# No else clause — nothing renders if no road selected
```

---

## 9.6 · Streamlit Re-run Minimization

Every filter widget interaction triggers a full Streamlit re-run. Performance depends on cache hits covering all expensive operations. Strategy to minimize re-run cost:

- All groupby/aggregation functions are cached → re-run cost is dominated by chart figure construction
- Chart figure construction is fast for all 30 charts with pre-aggregated data (< 200ms per chart)
- `use_container_width=True` on all charts avoids layout recalculation
- `st.container()` and `st.columns()` are pre-defined at page module level — not inside chart functions

---

# PART 10 — IMPLEMENTATION ROADMAP

---

## Phase 1 · Dashboard Shell + Navigation (Days 1–2)

**Objective:** Running skeleton with full navigation — no real charts, no real data.

**Deliverables:**
- `app.py` with dashboard switcher
- Traffic and AQI dashboard routers with 6-tab navigation each
- All 12 page modules (`p1_*.py` through `p6_*.py` for both dashboards) with empty `render()` functions
- Session state initialization for both dashboards (`filters/state.py`)
- Tab navigation rendering (active tab highlighting, Lab tab visual distinction)
- Advanced Lab gate mechanism (lab_gate component — functional but with placeholder content)

**Dependencies:** None — this is the foundation.

**Risks:**
- Streamlit's native tab component (`st.tabs`) is the right choice here — do not build custom tab routing with radio buttons if `st.tabs` meets the navigation needs
- Session state schema must be finalized before Phase 2 begins — changing state key names later breaks all consumers

**Priority:**  
1. app.py switcher  
2. Traffic router + 6 empty pages  
3. AQI router + 6 empty pages  
4. Session state init  
5. Lab gate component  

---

## Phase 2 · Theme + Reusable Layout System (Days 3–4)

**Objective:** All reusable components built and tested with placeholder content.

**Deliverables:**
- `config/theme.py` — complete color token system
- `config/chart_defaults.py` — BASE_LAYOUT and CHART_SIZES
- All components in `components/` — functional with placeholder data
- `utils/plotly_helpers.py` — all shared helper functions
- `utils/altair_helpers.py` — ridgeline and pairplot base specs
- `utils/annotations.py` — all annotation factory functions
- Global filter strip rendering (non-functional filters — widgets render, state updates, but no data yet)

**Dependencies:** Phase 1 complete. Session state schema finalized.

**Risks:**
- Component API design decisions made here are hard to reverse — spend extra time on `kpi_card`, `chart_container`, and `collapsible_section` APIs before proceeding
- `unsafe_allow_html=True` usage in Streamlit for styled components — test rendering carefully across browsers

**Priority:**  
1. theme.py + chart_defaults.py  
2. chart_container component  
3. kpi_card component  
4. filter_panel component (renders widgets + updates state)  
5. hero_section, collapsible_section  
6. plotly_helpers utilities  

---

## Phase 3 · Data Layer + Core Visualizations (Days 5–10)

**Objective:** All CRITICAL-priority charts rendering with real data on their correct pages.

**Sub-phases:**

**Phase 3A: Data Layer (Days 5–6)**
- `data_layer/loaders.py` — load and cache both datasets from Parquet
- `data_layer/cleaners.py` — all cleaning and derived column computation
- `data_layer/traffic_transforms.py` — all 12 traffic aggregation functions
- `data_layer/aqi_transforms.py` — all 14 AQI aggregation functions
- Verify all derived columns against blueprint specifications

**Phase 3B: Traffic CRITICAL Charts (Days 7–8) — implement in priority order:**
1. T-01 · Saturation Command Scorecard
2. T-08 · First Incident Cliff
3. T-11 · Congestion Distribution Ridgeline
4. T-09 · Speed Collapse Threshold
5. T-02 · Urban Area Performance Matrix
6. T-10 · Public Transport Decoupling *(insight panel: frame as weak or limited observable correlation between PT usage quartiles and congestion outcomes within this dataset — avoid causal or policy-failure language)*
7. T-03 · 32-Month Congestion Stream Graph
8. T-05 · Road Management Priority Quadrant

**Phase 3C: AQI CRITICAL Charts (Days 9–10) — implement in priority order:**
1. A-01 · Chronic Crisis Scorecard
2. A-02 · 3-Year Calendar Heatmap
3. A-06 · Atmospheric Stagnation Trap
4. A-07 · Extreme Day Radar
5. A-03 · Seasonal Ridgeline
6. A-08 · Minimum Temperature Scatter
7. A-05 · Pollution Persistence Series
8. A-09 · Pressure Universal Trigger
9. A-13 · Four Atmospheric States
10. A-04 · Monthly PM2.5 Variability

**Dependencies:** Phase 2 complete. Data files available.

**Risks:**
- T-03 Stream Graph is the most technically complex Traffic chart — reserve extra time
- A-02 Calendar Heatmap requires careful date grid construction — pre-compute grid in data layer
- A-03 Ridgeline with Altair requires careful KDE layer composition — test on real data before integrating

---

## Phase 4 · HIGH/MEDIUM Priority Charts (Days 11–13)

**Objective:** All remaining charts implemented across both dashboards.

**Traffic HIGH/MEDIUM charts:**
- T-04 · 7-Day Violin (HIGH)
- T-06 · Environmental Burden Treemap (HIGH)
- T-07 · Active Mobility Exclusion Diverging Bar (HIGH)
- T-12 · Weather × Roadwork Heatmap (HIGH — collapsible)
- T-13 · Compound Stress Radar (HIGH — Advanced Lab)
- T-15 · Area × Month Bubble Matrix (HIGH — collapsible)
- T-14 · Traffic-Congestion Density Hexbin (MEDIUM)

**AQI HIGH/MEDIUM charts:**
- A-10 · Wind Cannot Rescue Winter (HIGH)
- A-11 · Gust Ratio Paradox (HIGH)
- A-12 · Temperature Spread Inversion (HIGH)
- A-14 · Season × Pressure × Visibility Grid (HIGH)
- A-15 · Full Meteorological Pairplot (MEDIUM — Advanced Lab)

**Dependencies:** Phase 3 data layer complete. All data transforms available.

---

## Phase 5 · Interaction + Filtering (Days 14–16)

**Objective:** All cross-chart synchronization, drilldown behaviors, and filter propagation functional.

**Deliverables:**
- `streamlit_plotly_events` integration for click capture on T-05, A-02, A-13
- Full drilldown state propagation per interaction architecture (Part 6)
- Cross-chart synchronization per cross-filter maps (Part 6)
- Filter active indicator strip
- Detail panels (Road Detail Panel, Month Detail Panel) — dynamic content
- Advanced Lab fullscreen toggle
- Collapsible section expand/collapse state persistence
- "Investigate Further" navigation cards on Page 1 of both dashboards

**Dependencies:** All charts from Phases 3 and 4 complete.

**Risks:**
- `streamlit_plotly_events` adds a library dependency — evaluate stability
- Cross-chart sync via session state causes full page re-runs on every interaction — profile render time under interactions after implementation

---

## Phase 6 · Performance Optimization + Polish (Days 17–20)

**Objective:** Platform feels fast, premium, and production-ready.

**Performance tasks:**
- Profile all page renders under filter interactions — identify slow chart functions
- Verify all expensive transform functions hit cache on re-run
- Implement lazy rendering for collapsible sections (content_fn pattern)
- Confirm Advanced Lab page never renders outside Tab 6
- Optimize A-15 pairplot render time (switch from real KDE to histogram bins on diagonals if needed)
- Remove any `@st.cache_data` functions that are incorrectly cached (filter-dependent functions)

**Polish tasks:**
- Consistent chart title styling across all 30 charts
- Consistent hover tooltip formatting (number formatting via formatters.py)
- Consistent caption text below all CRITICAL charts (insight panel component)
- Staggered animation reveal on initial page load for hero charts (T-01, A-01)
- Filter reset behavior tested for all state keys
- Tablet layout adaptation (2-column → 1-column collapse)
- Mobile navigation (bottom tab bar) if in scope

**Final review checklist:**
- All 30 charts render with correct data
- All cross-chart interactions function per architecture spec
- No chart function directly accesses session state
- No page module directly calls groupby or aggregation
- No color hex string appears outside theme.py
- No Plotly layout property appears outside chart_defaults.py or chart modules
- All expensive transforms are cached

---

# PART 11 — ENGINEERING ANTI-PATTERNS TO AVOID

---

## Anti-Pattern 1: The Monolithic app.py

**What it looks like:**  
A single `app.py` containing all 30 chart functions, all data loading, all filter widgets, and all layout logic — 2,000+ lines, untestable, unreadable.

**Prevention:**  
`app.py` has exactly 15 lines: page config, dashboard switcher, and a routing call. Everything else lives in its dedicated module.

---

## Anti-Pattern 2: Repeated Plotly Layout Boilerplate

**What it looks like:**  
```python
# In t03_stream_graph.py:
fig.update_layout(paper_bgcolor="#0D1117", plot_bgcolor="#161B22", font_family="Inter", ...)

# In t04_violin_weekly.py:
fig.update_layout(paper_bgcolor="#0D1117", plot_bgcolor="#161B22", font_family="Inter", ...)
```

**Prevention:**  
`BASE_LAYOUT` in `chart_defaults.py`. Every chart does `layout = deepcopy(BASE_LAYOUT)` then sets only chart-specific overrides. Changing the background color is one line.

---

## Anti-Pattern 3: Filters Inside Chart Functions

**What it looks like:**  
```python
def render_t03(df):
    selected_areas = st.session_state.get("traffic_selected_areas", [])
    if selected_areas:
        df = df[df["Area Name"].isin(selected_areas)]
    fig = go.Figure(...)
```

**Prevention:**  
Chart functions receive pre-filtered data. They never touch session state. Filtering happens in the page module before calling the chart function. The chart is a pure data-to-figure transformer.

---

## Anti-Pattern 4: Aggregations Inside Chart Functions

**What it looks like:**  
```python
def render_t08(df):
    grouped = df.groupby("Incident Reports")["Congestion Level"].mean().reset_index()
    # This runs every render, every filter interaction, uncached
```

**Prevention:**  
`get_incident_congestion_bands()` in `traffic_transforms.py` is decorated with `@st.cache_data`. The chart receives the already-aggregated 6-row DataFrame. The groupby runs once per session.

---

## Anti-Pattern 5: Inline Style Strings

**What it looks like:**  
```python
st.markdown('<div style="background:#0D1117; border-radius:12px; padding:16px">', unsafe_allow_html=True)
```

**Prevention:**  
Components are responsible for their own styling using theme token imports. The `kpi_card()` component internally constructs its div — the caller never writes HTML or hex strings. If a hex color appears in a page module, it is a bug.

---

## Anti-Pattern 6: Uncached Expensive Operations

**What it looks like:**  
```python
# In p2_temporal_intelligence.py — runs on every re-run
df_pivot = load_traffic_clean().groupby(["month_year", "Area Name"])["Congestion Level"].mean().unstack()
```

**Prevention:**  
This exact groupby lives in `get_monthly_area_congestion()` in `traffic_transforms.py` decorated with `@st.cache_data`. The page module calls the function — it hits cache on every re-run except the first.

---

## Anti-Pattern 7: Dashboard Clutter (All Charts on One Page)

**What it looks like:**  
A single page rendering all 15 traffic charts in a vertical scroll. Users drown in charts. "Investigative" feel is lost. Page load time multiplies.

**Prevention:**  
6-page architecture. Maximum 3 main charts per page. Collapsible sections for secondary content. Advanced Lab isolation for dense visuals. Every page has a single analytical question it answers.

---

## Anti-Pattern 8: Filter State Chaos

**What it looks like:**  
- Widget A creates a filter variable in local scope
- Widget B in a different module also creates a filter variable
- They conflict on re-run
- Chart C uses one, Chart D uses the other
- The user applies a filter and half the charts respond

**Prevention:**  
Session state schema in `filters/state.py` is the single source of truth. Every filter widget writes to a specific, named session state key. Every chart reads from those specific keys via `apply_*_filters()`. No filter variable ever lives in local scope across a re-run boundary.

---

## Anti-Pattern 9: Inconsistent Chart Containers

**What it looks like:**  
- Some charts have titles, some don't
- Some have captions, some don't
- Some use `st.plotly_chart(fig, use_container_width=True)`, some use `st.plotly_chart(fig, height=400)`
- Visual rhythm is broken

**Prevention:**  
All charts go through `chart_container()`. Titles, heights, captions, fullscreen toggles are managed uniformly. Direct `st.plotly_chart()` calls outside of `chart_container()` are forbidden by convention.

---

## Anti-Pattern 10: Mixing Dashboard Identities

**What it looks like:**  
AQI charts accidentally use traffic crimson. Traffic chart uses AQI navy background. Components use hardcoded colors instead of theme tokens.

**Prevention:**  
Every component and chart module receives `dashboard="traffic"` or `dashboard="aqi"` as a parameter (or reads it from session state). Color selection is a single `if dashboard == "traffic" else ...` branch that maps to theme tokens — never to raw hex strings.

---

# PART 12 — FINAL RECOMMENDED DASHBOARD BLUEPRINT

---

## 12.1 · Module Dependency Map

```
app.py
  └── dashboards/traffic/__init__.py (router)
  │     ├── filters/state.py              (init + read)
  │     ├── filters/traffic_filters.py    (apply)
  │     ├── components/filter_panel.py    (render)
  │     └── dashboards/traffic/pages/
  │           └── p*.py (render)
  │                 ├── data_layer/loaders.py
  │                 ├── data_layer/traffic_transforms.py
  │                 ├── components/*.py
  │                 └── dashboards/traffic/charts/t*.py (render → Figure)
  │                       ├── config/theme.py
  │                       ├── config/chart_defaults.py
  │                       └── utils/plotly_helpers.py
  │
  └── dashboards/aqi/__init__.py (router)
        └── [identical structure, aqi namespace]
```

---

## 12.2 · File Count Summary

| Directory | File Count | Purpose |
|---|---|---|
| `config/` | 4 files | App-wide constants and tokens |
| `data/` | 7 files (2 raw CSV, 2 processed Parquet, 3 aggregation Parquet) | Data storage |
| `dashboards/traffic/pages/` | 6 files | Traffic page modules |
| `dashboards/traffic/charts/` | 15 files | Traffic chart modules |
| `dashboards/aqi/pages/` | 6 files | AQI page modules |
| `dashboards/aqi/charts/` | 15 files | AQI chart modules |
| `components/` | 11 files | Reusable UI components |
| `data_layer/` | 5 files | Data loading and transformation |
| `filters/` | 3 files | Filter state management |
| `utils/` | 5 files | Shared utilities |
| **Root** | **3 files** | **app.py, requirements.txt, config.toml** |
| **Total** | **~80 files** | **Organized, maintainable, scalable** |

---

## 12.3 · The Single Most Important Principle

The architecture is designed around one non-negotiable rule:

> **A chart function receives data. A chart function returns a figure. Nothing else.**

Every complication that exists in analytics dashboards — unmaintainable app.py files, duplicate styling, filter chaos, slow re-renders, broken cross-chart sync — traces back to violating this principle. Chart functions that load their own data, apply their own filters, write their own state, and call their own `st.plotly_chart()` are the root cause of unmaintainable analytics code.

Keep chart functions as pure transformations. Put everything else in its correct layer. The 80-file structure above exists to enforce this discipline at scale.

---

*Bangalore Urban Intelligence Platform · Implementation Architecture Blueprint*  
*Traffic Dashboard: 15 visuals · AQI Dashboard: 15 visuals · Total: 30*  
*Engineering Document Version: 1.0 Final · Pre-Implementation*  
*Stack: Streamlit + Plotly + Altair · Architecture Phase: Complete*
