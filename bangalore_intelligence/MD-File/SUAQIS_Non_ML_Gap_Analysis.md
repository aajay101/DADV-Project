# SUAQIS · Non-ML Implementation Gap Analysis
## Functionality Not Yet Implemented (Excluding ML Systems)

**Document Type:** Gap Analysis · Implementation Roadmap  
**Status:** Active Development  
**Scope:** All non-ML functionality specified in architecture docs but not yet implemented  
**Companion Documents:** `bangalore_implementation_architecture.md` · `SUAQIS_Visual_UX_Architecture_Blueprint.md` · `SUAQIS_Enterprise_UX_Architecture_Addon.md`  
**Excludes:** ML systems (forecasting, anomaly detection, SHAP explainability) — these are intentionally out of scope

---

# PART 1 — STUB / EMPTY MODULES

---

## 1.1 · `data_layer/transformers.py` — Empty Placeholder

**Architecture reference:** `bangalore_implementation_architecture.md` Part 5.3 — "Each transformation function is independently cached."

**Current state:** Single-line comment: `"Aggregations, pivots, group-bys — Phase 1 placeholder."` No actual implementation.

**What it should contain:** Shared/general-purpose transformation functions that are used by multiple charts or pages across both dashboards. This module was likely intended as a catch-all for transforms that don't belong in the dashboard-specific `traffic_transforms.py` or `aqi_transforms.py` files.

**Estimated scope:**
- Cross-dashboard aggregation utilities (e.g., date bucketing helpers)
- Shared binning functions (used by multiple charts)
- General-purpose rolling window utilities
- Column derivation helpers used across multiple transform modules

**Priority:** Low — both `traffic_transforms.py` and `aqi_transforms.py` have their own complete transform sets. This module is not called anywhere in the codebase.

**Why it matters:** Serves as the single location for transformation utilities that are dashboard-agnostic. Without it, shared transform logic either duplicates across the two specific transform files or gets buried in page bundles.

---

## 1.2 · `utils/altair_helpers.py` — Full Stub

**Architecture reference:** `bangalore_implementation_architecture.md` Part 4.4 — Altair helper utilities

**Current state:** All functions return `None` or empty lists. Stub docstring: `"Phase 2 API stubs."`

| Function | Architecture Spec | Current Status |
|---|---|---|
| `build_ridgeline_base(data, x_col, group_col)` | Returns Altair Chart spec with base ridgeline encoding | Returns `None` |
| `add_aqi_color_scale()` | Returns AQI 6-band color scale for Altair | Returns `None` |
| `build_pairplot_base(data, var_cols, color_col)` | Returns base pairplot Altair spec | Returns `None` |
| `kde_layer(data, col, offset, color)` | Returns KDE layer spec | Returns `None` |

**Impact:** All 30 charts currently use Plotly. If Altair is adopted for specific charts (ridgelines, pairplots), these helpers are required. The codebase already has `utils/analytics_kde.py` with `gaussian_kde_1d()` which is used by `t11_ridgeline.py` and `a03_seasonal_ridgeline.py` — but those charts bypass Altair entirely and render KDEs as Plotly filled areas instead.

**Priority:** Medium — depends on whether Altair rendering is adopted for any of the 4 charts that would benefit from declarative grammar (T-11 ridgeline, A-03 seasonal ridgeline, A-15 pairplot, T-13 radar comparison).

**Why it matters:** Altair's declarative grammar produces cleaner code for multi-layer statistical charts. The architecture spec explicitly calls for Altair on ridgelines and pairplots but currently Plotly is used everywhere.

---

## 1.3 · `utils/validators.py` — Empty Placeholder

**Architecture reference:** `bangalore_implementation_architecture.md` Part 11 — Data validation utilities referenced as anti-pattern prevention

**Current state:** Single-line comment: `"Data validation utilities — Phase 1 placeholder."` No actual implementation.

**What it should contain per architecture spec:**

| Validator | Purpose | Used By |
|---|---|---|
| `validate_traffic_schema(df)` | Verify expected columns and dtypes for traffic dataset | `loaders.py` on data load |
| `validate_aqi_schema(df)` | Verify expected columns and dtypes for AQI dataset | `loaders.py` on data load |
| `validate_date_range(df, start, end)` | Ensure requested filter range is within dataset bounds | `apply_*_filters()` |
| `validate_row_count(df, min_rows)` | Check that filtered result has sufficient rows | Chart render functions |
| `validate_required_columns(df, cols)` | Generic column presence check | All chart modules |
| `check_outlier_range(series, threshold_sigma)` | Flag values outside N-sigma bounds | `cleaners.py` |

**Priority:** Medium — data loading currently trusts the bootstrap/synthetic data generation. If real data is ever integrated, validators are critical for catching schema mismatches.

**Why it matters:** The corrupted-data fallback architecture (Addon Part 4.6) specifies that the platform shows a full-page error on data load failure. Validators are the first line of defense that enables this behavior.

---

## 1.4 · `utils/formatters.py` — Incomplete

**Architecture reference:** `SUAQIS_Visual_UX_Architecture_Blueprint.md` Part 7.1 — `utils/formatters.py` — standard number formats for all tooltips

**Current state:** Only basic numeric formatting implemented:

| Existing Function | Status |
|---|---|
| `fmt_congestion(val)` | ✅ `f"{val:.1f}"` |
| `fmt_speed(val)` | ✅ `f"{val:.1f} km/h"` |
| `fmt_pm25(val)` | ✅ `f"{val:.1f} µg/m³"` |
| `fmt_pct(val)` | ✅ `f"{val:.1f}%"` |
| `fmt_count(val)` | ✅ `f"{int(val):,}"` |

| Missing Function | Architecture Spec | Priority |
|---|---|---|
| `fmt_date(val, format="short")` | "Jan 2022" format for filter strip and chart axes | High |
| `fmt_date_long(val)` | "January 2022" for insight panels | Medium |
| `fmt_date_range(start, end)` | "Jan 2022 – Aug 2024" for filter strip | High |
| `fmt_aqi_category(val)` | "Very Poor" label from numeric PM2.5 | High |
| `fmt_season(val)` | "Winter / Monsoon / Spring / Post-Monsoon" | Medium |
| `fmt_severity(severity)` | "CRITICAL / WARNING / SAFE / NEUTRAL" from semantic label | Medium |
| `fmt_wind_speed(val)` | `f"{val:.1f} m/s"` | Low |
| `fmt_pressure(val)` | `f"{val:.1f} hPa"` | Low |
| `fmt_temperature(val)` | `f"{val:.1f}°C"` | Low |
| `fmt_visibility(val)` | `f"{val:.1f} km"` | Low |
| `fmt_coordinate(lat, lon)` | `f"{lat:.2f}°N, {lon:.2f}°E"` for Bangalore coordinates | Low |
| `fmt_filter_summary(filters)` | Human-readable filter state summary for export footers | High |
| `fmt_model_version(version)` | `"v2.1"` style for ML model metadata (non-ML file but referenced by ML UX) | Low |
| `fmt_confidence_interval(lower, upper)` | `"142–218 µg/m³"` format | Medium |

**Priority:** High for date/category formatters — these are used in `filter_panel.py`, `chart_container.py` captions, and `empty_state.py`. The missing `fmt_date_range` is specifically referenced in the PNG export spec (Addon Part 7.2).

**Why it matters:** The UX blueprint explicitly states: *"No tooltip shows raw float values — all formatting via `utils/formatters.py`."* The current implementation violates this rule by using inline formatting in chart tooltip templates.

---

## 1.5 · `utils/annotations.py` — Minimal Stubs

**Architecture reference:** `bangalore_implementation_architecture.md` Part 4.5 — Annotation architecture; `SUAQIS_Enterprise_UX_Architecture_Addon.md` Part 8 — Microinteraction details

**Current state:** All functions return minimal dicts without full annotation styling configuration:

| Function | Architecture Spec | Current Status |
|---|---|---|
| `step_callout(x, y, delta_text, color)` | Full Plotly `go.layout.Annotation` with positioning, font, arrow | Returns basic dict |
| `threshold_label(y, label, side)` | Threshold line label with position and color | Returns basic dict |
| `quadrant_label(x, y, archetype_text)` | Quadrant zone label (Critical Overload, etc.) | Returns basic dict |
| `regime_annotation(x, y, regime_name)` | Atmospheric regime label | Returns basic dict |
| `aqi_band_label(y, category_name)` | AQI category band label | Returns basic dict |
| `insight_callout(x, y, text, arrow_dir)` | Insight callout with arrow direction | Returns basic dict |

**What is missing:**
- Font family and size specification (Inter, Level 7 caption scale)
- Color application from theme tokens (not hardcoded hex strings)
- Arrow styling (style, width, arrowhead)
- Background box styling for callout annotations
- Z-index / layer ordering
- `add_annotation_callout()` function referenced in UX spec is not present
- `add_quadrant_zone_labels()` helper from Addon Part 8 not present

**Priority:** Medium — annotation styling is currently embedded inline in chart modules. Moving to a centralized annotation factory system enables consistent styling and easier theme updates.

**Why it matters:** The anti-pattern "Annotation Accumulation" (Addon Part 12.2) and "Annotation limits" (Addon Part 9.3) require a centralized annotation system to enforce maximum 3 annotations per chart. Without a factory, annotation count governance is manual.

---

# PART 2 — INTERACTION & NAVIGATION

---

## 2.1 · Fullscreen Mode — Not Implemented

**Architecture reference:**
- `SUAQIS_Visual_UX_Architecture_Blueprint.md` Part 8.4 — Fullscreen interaction pattern
- `bangalore_implementation_architecture.md` Part 8.4 — Fullscreen visualization strategy
- `SUAQIS_Enterprise_UX_Architecture_Addon.md` Part 2.3 — Chart container fullscreen state

**Current state:** `chart_container.py` renders a "Fullscreen mount - Phase 5" button with a comment: `"Phase 5 fullscreen enhancement — deferred."` No `session_state` key, no layout switch, no collapse mechanism.

**What needs implementing:**

| Component | Spec Location | Status |
|---|---|---|
| Fullscreen state key in session_state | `"*_fullscreen"` per chart key | Not present |
| Enter fullscreen button | `chart_container(fullscreen_key=...)` renders toggle | Button exists but no handler |
| Fullscreen layout switch | Chart expands to 100% viewport width, 85vh height | Not implemented |
| "← Collapse" exit button | Fixed top-left of fullscreen container | Not implemented |
| Chart-only page render during fullscreen | All other page content hidden via conditional | Not implemented |
| Opacity fade transition | 200ms fade between normal and fullscreen | Not implemented |
| Fullscreen-eligible chart list enforcement | T-13, T-02, A-15, A-02 only | Not enforced |

**Charts that should be fullscreen-eligible:**
- T-13 · Compound Stress Radar (Advanced Lab)
- T-02 · Parallel Coordinates (Advanced Lab)
- A-15 · Full Meteorological Pairplot (Advanced Lab)
- A-02 · Calendar Heatmap (P2 Crisis)

**Priority:** Medium — the button exists as a placeholder, visually indicating intent. Fullscreen is not blocking normal use.

**Why it matters:** The UX spec designates fullscreen as essential for the calendar heatmap (A-02) and pairplot (A-15) where cell/panel sizes are too small at default width for detailed inspection.

---

## 2.2 · Lazy Chart Loading — Not Implemented

**Architecture reference:** `bangalore_implementation_architecture.md` Part 9.2 — Lazy rendering strategy; `SUAQIS_Enterprise_UX_Architecture_Addon.md` Part 3.2 — Progressive rendering and staged chart reveal

**Current state:** `collapsible_section.py` exists with the `content_fn` pattern for lazy rendering, but it is not consistently used. `page_production.py` references lazy loading but the actual mechanism is not wired up. Charts marked as "collapsible" in the architecture (T-12, T-15, A-14) render eagerly.

**What needs implementing:**
- T-12 (Weather × Roadwork heatmap) wrapped in `collapsible_section(default_expanded=False)` — currently renders eagerly
- T-15 (Area × Month bubble matrix) wrapped in `collapsible_section(default_expanded=False)` — currently renders eagerly
- A-14 (Season × Pressure × Visibility grid) wrapped in `collapsible_section(default_expanded=False)` — currently renders eagerly
- T-11 (Ridgeline, 16 distributions) — already collapses at laptop widths but explicit `collapsible_section` wrapping for tablet/compact is not present
- Staged reveal sequence (Addon Part 3.3) — Stage 1–5 progressive rendering with skeleton states is not wired: KPI skeletons appear but hero/supporting chart loading is not staggered

**Priority:** Medium — performance impact is moderate with synthetic data. With real data at scale, eager rendering of 3 complex charts per page would cause visible lag.

**Why it matters:** The staging sequence (`KPI → hero chart → 50ms delay → supporting chart`) creates a progressive reveal that reduces perceived load time. Without it, all charts appear simultaneously after a blank wait.

---

## 2.3 · Viewport / Responsive Detection — Partial

**Architecture reference:** `SUAQIS_Visual_UX_Architecture_Blueprint.md` Part 10.1 — Breakpoint definitions; `SUAQIS_Enterprise_UX_Architecture_Addon.md` Part 1.2–1.6 — Viewport composition per breakpoint

**Current state:** `components/layout/responsive.py` has `get_column_split()` and `get_chart_heights()` functions with some breakpoint-aware logic. However:
- No actual viewport width detection mechanism (JS injection or otherwise)
- Responsive adaptation relies on Streamlit's native column compression, which is not full responsive design
- Laptop breakpoint rules (gauge ring hiding, secondary KPI row collapse) are not implemented
- Tablet breakpoint (single-column collapse) is not enforced
- Compact mode (essential degradation) is not implemented
- T-11 ridgeline auto-collapse at laptop width is not wired
- A-02 calendar heatmap "fullscreen recommended" banner at < 1200px is not implemented

**What needs implementing:**

| Breakpoint | Width | Missing Behavior |
|---|---|---|
| Laptop | 1024–1280px | Gauge ring hiding via CSS media query, secondary KPI row collapse, T-11 auto-collapser |
| Tablet | 768–1024px | Single-column layout switch, KPI 2×2 grid, Advanced Lab gate message, A-02 banner |
| Compact | < 768px | All charts in expander, KPI list view, filter overlay, degradation warning banner |
| Ultrawide | ≥ 1920px | 1600px max-width cap confirmed in CSS (already in `css_injector.py`) |

**Implementation approach (per Addon Part 10.1):**

```python
# JS injection via st.components.v1.html() in a startup hook
# Writes viewport width to session_state["viewport_width"]
# Page modules read this value and call get_column_split() / get_chart_heights()
```

**Priority:** Medium — the platform functions at desktop width but degrades gracefully below 1024px.

---

## 2.4 · Advanced Lab Isolation — Partial

**Architecture reference:** `bangalore_implementation_architecture.md` Part 8.1 — Lab page structure; `SUAQIS_Visual_UX_Architecture_Blueprint.md` Part 9.4 — Lab Gate UX

**Current state:** `lab_gate.py` is fully implemented. `lab_header.py` is fully implemented. `p6_advanced_lab.py` pages exist as thin wrappers. However:
- `p6_advanced_lab.py` for traffic does not render the "Return to Dashboard Overview" breadcrumb that AQI's lab has
- The Advanced Lab gate for traffic uses the `is_lab=True` parameter in `render_page()` but the actual gate pass state (`traffic_lab_gate_passed`) is not explicitly handled
- Lab-specific filter controls (area toggles for T-13) — the sidebar-style toggle panel described in the UX spec is not implemented

**What needs implementing:**
- Traffic Advanced Lab breadcrumb: `"← Return to Dashboard Overview [P1 · Command Overview]"`
- T-13 radar area toggle panel in sidebar-style column (`st.columns([4, 1])`) with checkboxes, "Top 3 Stress" / "Baseline 3" quick-select, "Clear All" button, severity ranking list
- A-15 pairplot category toggle filter panel (sidebar-style column, 7 checkboxes)
- Lab mode session state isolation (lab charts use full dataset, global date filter suspended in Lab mode)

**Priority:** Medium — the gate works but the Advanced Lab experience is incomplete. T-13's comparison modes are the most critical gap.

---

# PART 3 — EXPORT / REPORTING

---

## 3.1 · Per-Chart PNG Export — Not Implemented

**Architecture reference:** `SUAQIS_Enterprise_UX_Architecture_Addon.md` Part 7.2 — Per-chart PNG export

**Current state:** No export functionality exists. No `utils/export.py` module. No `st.download_button()` calls in the codebase.

**What needs implementing:**

| Component | Spec |
|---|---|
| `utils/export.py` module | New module |
| `export_chart_png(fig, title, active_filters)` | Adds metadata footer, calls `fig.to_image(format="png", width=1200, height=700, scale=2)`, returns bytes |
| Export filename convention | `BUIP_[DashboardCode]_[ChartCode]_[YYYYMMDD]_[HHMMSS].png` |
| Metadata footer text | `"BUIP · [Dashboard] · Filters: [filter summary] · Generated: [timestamp]"` |
| Download button | Accessible via fullscreen-mode toolbar (not visible by default) |
| `apply_export_theme(fig)` | Light-mode color remapping for print legibility |

**Priority:** Medium — explicitly listed in the UX Production Readiness Final Gate (Addon Part 14.10 item requiring spot-check of 10 random chart tooltips).

**Why it matters:** Analysts need to export self-contained charts for executive briefings and compliance reports. Without this, all sharing requires screen recording or manual screenshots.

---

## 3.2 · PDF Report Export — Not Implemented

**Architecture reference:** `SUAQIS_Enterprise_UX_Architecture_Addon.md` Part 7.3 — PDF report export

**Current state:** No PDF functionality. No `reportlab` or `weasyprint` in any import.

**What needs implementing:**

| Component | Spec |
|---|---|
| `utils/export.py` — `generate_pdf_report()` | Server-side PDF generation entry point |
| Cover page | Platform name, dashboard name, active filter summary, date generated, dataset period |
| Executive summary page | All KPI values, one-sentence interpretation per KPI, severity badge |
| Chart pages (one per chart in export scope) | Chart PNG + title + annotations + insight panel text + filter footer |
| Data notes page | Dataset sources, methodology notes, NAAQS/WHO references |
| Filter state embedding | Every export embeds active filter state in footer and PDF metadata |
| Light-mode chart export | All charts rendered with `apply_export_theme()` before PNG embedding |
| Persistent `⬇ Export Report` button | Right-aligned in filter strip, always visible |

**Implementation dependencies:**
- `reportlab` or `weasyprint` needs to be added to `requirements.txt`
- PNG export must be working first (3.1)
- Filter summary formatter must be working (`fmt_filter_summary`)

**Priority:** Low-Medium — not required for core functionality. Listed as Phase 7 in the original roadmap.

---

## 3.3 · Executive Summary Export — Not Implemented

**Architecture reference:** `SUAQIS_Enterprise_UX_Architecture_Addon.md` Part 7.4 — Executive summary export mode

**Current state:** No separate export path for non-technical stakeholders.

**What needs implementing:**
- One-page light-background export for city officials and department heads
- Three headline findings — one sentence each (analytically written, not chart titles)
- Three KPI values with severity assessment
- One hero chart (analyst-selected at export time)
- White background / black text for print readability
- Simplified filename: `BUIP_[Dashboard]_Executive_[YYYYMMDD].pdf`

**Priority:** Low — depends on PDF export (3.2) being complete first.

---

# PART 4 — LOADING / FALLBACK UX

---

## 4.1 · Skeleton Loader System — Partial

**Architecture reference:** `SUAQIS_Enterprise_UX_Architecture_Addon.md` Part 3.2 — Skeleton loader system; Part 3.3 — Progressive rendering

**Current state:** `components/loading_state.py` has `kpi_skeleton()`, `chart_skeleton()`, and `inline_loader()` implemented with shimmer CSS animation. These are used in `chart_container.py` during loading state. However:
- The staged reveal sequence (Stage 1: filter + hero + KPI skeletons → Stage 2: KPI data → Stage 3: hero chart → Stage 4: 50ms delay → supporting chart) is not wired in page modules
- KPI skeleton shimmer is not integrated into `kpi_card()` component — `kpi_card()` does not accept a `loading` parameter
- Chart skeleton does not render the simulated axis lines and bar shapes (it renders a generic placeholder block instead of the chart-accurate skeleton described in Addon Part 3.2)
- The shimmer CSS animation is defined in `css_injector.py` but the `.skeleton` class usage is not consistently applied across all skeleton instances

**What needs implementing:**
- `kpi_card(loading=True)` parameter — renders KPI skeleton instead of value when `loading=True`
- Chart-accurate skeleton shapes per chart type (bar chart skeleton vs. stream graph skeleton vs. scatter skeleton)
- Progressive rendering sequence in `page_production.py` — currently all charts render simultaneously once data resolves
- `prefers-reduced-motion` override for skeleton animation (static block instead of shimmer)

**Priority:** Medium — skeleton loaders exist and are functional but the staged reveal is the missing piece for progressive perceived performance.

---

## 4.2 · Filter Strip Progress Bar — Not Implemented

**Architecture reference:** `SUAQIS_Enterprise_UX_Architecture_Addon.md` Part 3.4 — Streamlit rerender mitigation; Part 3.5 — Loading hierarchy and spinner governance

**Current state:** No animated progress bar on the filter strip during re-runs. Default Streamlit spinner is hidden via CSS but no replacement exists.

**What needs implementing:**

| Component | Spec |
|---|---|
| Filter strip progress bar | 2px animated gradient bar replaces bottom border of filter strip during re-runs |
| Animation | 2s linear infinite slide — `transparent → TRAFFIC_SLATE → transparent` |
| Spinner governance | `st.spinner()` used only for initial cold-cache load; filter strip progress bar used for all subsequent interactions |
| Loading state filter disable | During re-run, filter widgets get `pointer-events: none; opacity: 0.7` to prevent double-clicks |

**Priority:** Low-Medium — improves perceived performance but not blocking. The UX Addon specifies this as a "production polish" feature.

---

## 4.3 · Stale-Cache Handling — Not Implemented

**Architecture reference:** `SUAQIS_Enterprise_UX_Architecture_Addon.md` Part 4.5 — Stale-cache handling

**Current state:** No stale data detection or indicator system. `@st.cache_data` decorators use `ttl=None` (session lifetime) which is correct for static datasets but means no stale detection would ever fire anyway.

**What needs implementing:**
- `check_data_freshness(df)` utility function that compares dataset timestamp to `STALE_THRESHOLD_SECONDS`
- Stale data indicator in filter strip: `⟳ Refresh` button appears when data is stale
- Per-KPI stale corner badge: `"⟳ Stale"` in top-right corner of KPI card (CSS-styled)
- Non-blocking banner below hero section: `"ⓘ Displaying data from [HH:MM]. Refresh to load latest."`
- "Refresh" action: re-runs `load_traffic_clean()` / `load_aqi_clean()` to re-populate cache
- Configuration: `STALE_THRESHOLD_SECONDS` constant (default 300 = 5 minutes) in `config/data_config.py`

**Note:** For the current static dataset architecture, this feature is not immediately useful since data doesn't change. It becomes critical if real-time data ingestion is added.

**Priority:** Low — explicitly designed for dynamic data scenarios.

---

## 4.4 · Long-Session Notification — Not Implemented

**Architecture reference:** `SUAQIS_Enterprise_UX_Architecture_Addon.md` Part 6.6 — Cognitive load safeguards

**Current state:** No session duration tracking or notification system.

**What needs implementing:**
- `st.session_state["session_start_time"]` set on initial app load
- After 90 minutes of uninterrupted use: non-blocking notification bar below filter strip: `"You've been reviewing this dashboard for 90+ minutes. Consider exporting a report summary before continuing."`
- `[Export Summary] [Dismiss]` buttons — Export Summary triggers PDF export flow (3.2), Dismiss sets a session state flag to suppress future notifications
- Notification shown only once per session

**Priority:** Low — quality-of-life feature.

---

# PART 5 — COMPONENT COMPLETION

---

## 5.1 · `page_template.py` Mock Data Upgrade

**Architecture reference:** `SUAQIS_Visual_UX_Architecture_Blueprint.md` Part 14.7 — Enterprise polish checklist; `bangalore_implementation_architecture.md` Part 3.3 — Page module structure

**Current state:** `config/mock_content.py` has hardcoded static strings for KPI values, chart titles, and insights. `page_template.py` renders via `render_analytical_page()` using these mocks. This serves as a presentation layer for showing the dashboard structure without running the full data pipeline.

**What needs implementing:**
- Dynamic mock data generation (per-page mock data derived from actual transforms rather than static strings)
- Mock KPI values that are internally consistent with each other
- Mock insight text that references the same mock KPI values
- `get_page_mock()` currently returns catalog entries — should return actual computed mock aggregations

**Priority:** Low — used for presentation/demo mode. Not production-critical.

---

## 5.2 · Cross-Dashboard State Preservation — Partial Bug

**Architecture reference:** `bangalore_implementation_architecture.md` Part 3.5 — Cross-dashboard navigation

**Current state:** `filters/state.py` and `filters/interaction.py` implement state preservation for both dashboards. However, the `app.py` switcher stores `active_dashboard` but there is no explicit test or validation that filter state is preserved when switching Traffic ↔ AQI ↔ Traffic.

**What needs validating/implementing:**
- Explicit test: switch from Traffic (with active area filter) to AQI to Traffic — verify area filter is preserved
- `active_dashboard` state key preservation during round-trip
- Opposing dashboard's active tab preservation (should remain at whatever tab was active before switching)

**Priority:** Medium — critical UX behavior if implemented incorrectly. Currently not tested.

---

## 5.3 · Reduced-Motion Accessibility — Partial

**Architecture reference:** `SUAQIS_Enterprise_UX_Architecture_Addon.md` Part 6.4 — Reduced-motion behavior

**Current state:** `css_injector.py` defines the shimmer keyframes animation. No `@media (prefers-reduced-motion: reduce)` media query exists.

**What needs implementing:**
```css
@media (prefers-reduced-motion: reduce) {
    .skeleton { animation: none; background: #2D333B; }
    * { transition-duration: 0.01ms !important; }
    .chart-appear { animation: none; opacity: 1; }
    .nav-card-arrow { transform: none !important; }
    .kpi-gauge circle { transition: none; }
}
```

**Priority:** Low — accessibility feature that does not affect functionality for default settings.

---

# PART 6 — CONFIGURATION & PROJECT SETUP

---

## 6.1 · `requirements.txt` — Missing

**Architecture reference:** `bangalore_implementation_architecture.md` Part 2.1 — Root structure lists `requirements.txt`

**Current state:** No `requirements.txt` in the project root or anywhere in `bangalore_intelligence/`.

**What needs implementing:**

| Package | Purpose | Status |
|---|---|---|
| `streamlit` | Application framework | Present via .venv |
| `plotly` | Primary charting | Present via .venv |
| `pandas` | Data manipulation | Present via .venv |
| `numpy` | KDE computation, numeric ops | Present via .venv |
| `altair` | Statistical charts (if adopted) | Present via .venv |
| `streamlit-plotly-events` | Chart click events for drilldown | **Missing** — needed for T-05, A-02 click handlers |
| `kaleido` | PNG export from Plotly (`fig.to_image()`) | **Missing** — needed for PNG export |
| `reportlab` or `weasyprint` | PDF generation | **Missing** — needed for PDF export |
| `psycopg2-binary` | (Future) database connection | Not needed now |

**Priority:** High — `streamlit-plotly-events` is required for the drilldown interaction architecture. The codebase currently uses a Plotly selection integration in `chart_container.py` but `streamlit_plotly_events` is the specified library that must be installed.

---

## 6.2 · `.streamlit/config.toml` — Missing

**Architecture reference:** `bangalore_implementation_architecture.md` Part 7.2 — Streamlit global theme

**Current state:** No `.streamlit/` directory exists. The Streamlit theme is set via `st.set_page_config()` and CSS injection (`utils/css_injector.py`).

**What needs implementing:**
```toml
# bangalore_intelligence/.streamlit/config.toml
[theme]
base = "dark"
primaryColor = "#E5383B"
backgroundColor = "#0D1117"
secondaryBackgroundColor = "#161B22"
textColor = "#F0F6FC"
font = "sans serif"

[server]
headless = true
```

**Priority:** Medium — the CSS injection approach currently handles most styling. The config.toml is the canonical Streamlit theme source but is not critical since CSS overrides take precedence.

---

## 6.3 · `pytest` / Test Suite — Missing

**Architecture reference:** `bangalore_implementation_architecture.md` — No test directory listed in folder structure; `SUAQIS_Enterprise_UX_Architecture_Addon.md` Part 9.6 — Quality gates require manual testing

**Current state:** No test files exist anywhere in the project.

**What needs implementing (per UX Addon quality gates):**

| Test Area | Test Cases |
|---|---|
| Data loading | `test_load_traffic_clean()`, `test_load_aqi_clean()` — verify schema, row counts |
| Transformers | `test_traffic_transforms()` — verify each transform function output shape |
| Formatters | `test_fmt_date_range()`, `test_fmt_aqi_category()` — verify output format |
| Validators | `test_validate_traffic_schema()`, `test_check_outlier_range()` |
| KPI card severity | `test_kpi_severity_color()` — verify CRITICAL → CRIMSON, WARNING → AMBER |
| Session state | `test_state_defaults()`, `test_filter_reset()` |
| Chart rendering | `test_t01_render()` — smoke test, figure returned, no exceptions |
| Drilldown state | `test_clear_selection()` — verify selection clearing |
| Filter stress test | `test_extreme_filters()` — single road, single month, verify no crash |

**Priority:** Medium — the UX quality gates require manual testing. Automated tests would reduce regression risk during ongoing development.

---

# PART 7 — INFRASTRUCTURE & DEPLOYMENT

---

## 7.1 · Data Persistence — Real Data Integration Path

**Architecture reference:** `bangalore_implementation_architecture.md` Part 5.1 — Four-layer data model; `SUAQIS_Enterprise_UX_Architecture_Addon.md` Part 4.6 — Corrupted-data fallback

**Current state:** `data_layer/bootstrap_data.py` generates synthetic data on every run. No real Bangalore traffic or AQI data sources. No API clients. No web scraping.

**What exists for real data integration:**
- `data_layer/loaders.py` is properly structured for loading from parquet — just needs different source paths
- `data_layer/cleaners.py` has full cleaning logic — would need extension for real column names
- `utils/validators.py` is the placeholder that would enable real data validation
- `bootstrap_data.py` `ensure_raw_datasets()` could be replaced with a real data fetch function

**Real data sources to consider (for future phases):**
- Bangalore traffic: Bangalore Traffic Police开放数据, ITS Bangalore, BBMP data portals
- AQI: CPCB (Central Pollution Control Board) daily data, SAFAR (IMD), Twitter/X data feeds
- Static data: Bangalore Open Data Portal, Karnataka State Data Center

**Priority:** Low (university project context) — synthetic data is appropriate for a DADV project demonstration.

---

# PART 8 — SUMMARY TABLE

---

## 8.1 · Complete Gap List by Priority

| # | Item | Module | Priority | Estimated Effort |
|---|---|---|---|---|
| 1 | `streamlit-plotly-events` dependency | `requirements.txt` | **High** | 1 package |
| 2 | `kaleido` dependency | `requirements.txt` | **High** | 1 package |
| 3 | Date / AQI category formatters | `utils/formatters.py` | **High** | ~8 functions |
| 4 | `fmt_filter_summary` for exports | `utils/formatters.py` | **High** | 1 function |
| 5 | Viewport width JS detection | New or `utils/` | **High** | ~20 lines |
| 6 | T-13 radar area toggle panel | `dashboards/traffic/pages/p6_advanced_lab.py` | **High** | ~40 lines |
| 7 | KPI card `loading=True` parameter | `components/kpi_card.py` | **Medium** | ~15 lines |
| 8 | Chart-accurate skeleton shapes | `components/loading_state.py` | **Medium** | ~30 lines |
| 9 | Staged chart reveal sequence | `page_production.py` | **Medium** | ~20 lines |
| 10 | T-12, T-15, A-14 collapsible wrapping | Respective page modules | **Medium** | 3 wrappers |
| 11 | Tablet/Compact responsive layout | `components/layout/responsive.py` | **Medium** | ~60 lines |
| 12 | Advanced Lab sidebar filter panels | Respective page modules | **Medium** | ~80 lines |
| 13 | Cross-dashboard state preservation test | `filters/interaction.py` | **Medium** | Test + validation |
| 14 | `utils/validators.py` implementation | `utils/validators.py` | **Medium** | ~40 lines |
| 15 | Fullscreen mode (T-13, A-15, A-02, T-02) | `components/chart_container.py` | **Medium** | ~60 lines |
| 16 | Filter strip progress bar | `components/filter_panel.py` | **Medium** | ~20 lines |
| 17 | Annotation factory completion | `utils/annotations.py` | **Medium** | ~50 lines |
| 18 | PNG export | `utils/export.py` | **Medium** | ~50 lines |
| 19 | `data_layer/transformers.py` completion | `data_layer/transformers.py` | **Low** | If needed |
| 20 | PDF export | `utils/export.py` | **Low** | ~100 lines |
| 21 | Executive summary export | `utils/export.py` | **Low** | ~40 lines |
| 22 | Altair helpers completion | `utils/altair_helpers.py` | **Low** | If Altair is adopted |
| 23 | Reduced-motion CSS | `utils/css_injector.py` | **Low** | ~10 lines |
| 24 | Stale-cache handling | `filters/state.py` | **Low** | If dynamic data added |
| 25 | Long-session notification | `components/filter_panel.py` | **Low** | ~20 lines |
| 26 | Mock data upgrade | `config/mock_content.py` | **Low** | Refactor |
| 27 | `.streamlit/config.toml` | `.streamlit/config.toml` | **Low** | ~10 lines |
| 28 | `requirements.txt` creation | `requirements.txt` | **High** | ~12 lines |
| 29 | Test suite | `tests/` | **Medium** | ~20 test functions |

---

## 8.2 · Quick Wins (Under 1 Hour Each)

1. **Create `requirements.txt`** — List all .venv packages + streamlit-plotly-events + kaleido. Immediate developer experience improvement.
2. **Add `fmt_date_range()` to `utils/formatters.py`** — Used in filter strip and export footer. 5 lines.
3. **Add `fmt_aqi_category()` to `utils/formatters.py`** — Converts PM2.5 numeric to "Very Poor" label. 5 lines.
4. **Add `loading=True` parameter to `kpi_card()`** — Enables KPI skeleton. 10 lines.
5. **Add viewport width JS detection** — Single `st.components.v1.html()` injection. 15 lines.
6. **Wrap T-12 in `collapsible_section()`** — Lazy load weather heatmap. 5 lines.

---

## 8.3 · What's Already Great (No Action Needed)

- **All 30 chart modules** — Fully implemented with real synthetic data
- **All 12 page modules** — Working with production bundle pipeline
- **Theme system** — Complete color token system in `config/theme.py`
- **KPI card component** — SVG gauge ring, severity coloring, delta indicator
- **Filter panel** — Sticky filter strip with date range, area/category multiselect, Reset All
- **Tab navigation** — Themed tab strip with active state
- **Lab gate** — Functional gate with session state persistence
- **Data layer** — Full transform pipeline with 55+ cached functions
- **Interactive drilldown** — Full selection → detail panel system via `filters/interaction.py` and `services/state/chart_handlers.py`
- **Chart container** — Universal wrapper with title, caption, state-aware borders
- **CSS injection** — Comprehensive dark theme override of Streamlit defaults
- **Bootstrap data generation** — Realistic synthetic data for both datasets
- **Gaussian KDE** — `utils/analytics_kde.py` working for ridgeline charts
- **Plotly engine** — Theme application, color scales, severity mapping

---

*Document: SUAQIS Non-ML Implementation Gap Analysis*  
*Platform: Bangalore Urban Intelligence Platform*  
*Purpose: Identify all non-ML architecture-specified functionality not yet implemented*  
*Scope: ~25 items across stub modules, interaction, export, loading UX, components, config, and infrastructure*  
*Companion: bangalore_implementation_architecture.md · SUAQIS_Visual_UX_Architecture_Blueprint.md · SUAQIS_Enterprise_UX_Architecture_Addon.md*