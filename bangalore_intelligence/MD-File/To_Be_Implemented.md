# SUAQIS Remaining Implementation Handbook

## 1. Executive Summary
- Critical gaps:
  - Missing interaction/export dependencies in `requirements.txt`: click-event support must be verified against the installed Plotly version before adding `streamlit-plotly-events`; `kaleido` is required for Plotly PNG export and should be version-pinned.
  - Incomplete central formatting layer in `utils/formatters.py`, especially date ranges, AQI category labels, filter summaries, and export-safe strings.
  - Missing validation layer in `utils/validators.py`, leaving loaders, filters, and chart render paths without schema, range, or minimum-row safeguards.
  - Missing viewport width detection, so responsive behavior is mostly delegated to Streamlit rather than governed by SUAQIS breakpoints.
- Medium gaps:
  - Fullscreen chart mode exists only as a visual button in `components/chart_container.py`; it has no state, layout switch, export toolbar, or eligible-chart enforcement.
  - Advanced Lab controls are incomplete: Traffic lacks the return breadcrumb, T-13 lacks the area toggle panel, A-15 lacks category toggles, and Lab mode still uses globally filtered data.
  - Export systems are absent: no `utils/export.py`, no PNG generation, no PDF report flow, and no executive summary export.
  - Loading UX is partially implemented but lacks true staged reveal, filter-strip progress state, and stale-session indicators.
  - Annotation and Altair helper modules remain stubs or minimal factories.
- Low gaps:
  - `data_layer/transformers.py` is still a shared-transform placeholder.
  - Mock/demo content is static rather than derived from real transforms.
  - Stale-cache and long-session notification systems are not implemented.
  - Automated tests are absent.
- Implementation dependencies:
  - Formatters and validators must precede exports, tests, and filter summary rendering.
  - Viewport detection must precede responsive layout enforcement, fullscreen recommendations, and compact Advanced Lab gating.
  - PNG export must precede PDF and executive summary export.
  - Fullscreen state must precede fullscreen toolbar export controls.
  - Test scaffolding should follow the implementation of validators and state transitions.

---

## 2. Implementation Order Roadmap

### Phase 1 — Foundation
- objective:
  - Complete missing low-level contracts required by later UX, export, and validation systems.
- files affected:
  - `bangalore_intelligence/requirements.txt`
  - `bangalore_intelligence/utils/formatters.py`
  - `bangalore_intelligence/utils/validators.py`
  - `bangalore_intelligence/data_layer/loaders.py`
  - `bangalore_intelligence/filters/traffic_filters.py`
  - `bangalore_intelligence/filters/aqi_filters.py`
- systems introduced:
  - Missing package dependencies.
  - Central date, AQI, season, severity, filter-summary, and export metadata formatters.
  - Data schema, date-range, row-count, required-column, and outlier validators.
- architecture dependencies:
  - Preserves central transform architecture.
  - Preserves current loader/filter boundaries.
  - Does not move chart logic into validators or formatters.
- implementation procedure:
  - Verify `streamlit-plotly-events` compatibility against the installed Plotly major version before adding it; the codebase currently allows `plotly>=5.18.0`, while local environments may resolve Plotly 6.x.
  - Add only verified missing packages to `requirements.txt`: click-event support package, `kaleido>=0.2.1,<0.3`, and one PDF engine selected for export phase.
  - Implement formatters as pure functions with no Streamlit imports.
  - Implement validators as pure functions returning validated data or raising typed validation errors.
  - Call validators from loader and filter boundaries, not chart modules.
- validation checklist:
  - Dependency imports are tested after install, especially click-event support and `fig.to_image()`.
  - `fmt_date_range()` matches visible filter strip and export footer expectations.
  - `fmt_aqi_category()` maps PM2.5 values to the existing AQI category tokens.
  - Loader validation catches missing columns before page bundles build charts.
  - Filter validation catches reversed or out-of-bounds date ranges.
- risk if implemented incorrectly:
  - Unverified `streamlit-plotly-events` compatibility can break drilldown behavior under Plotly 6.x.
  - Validator exceptions can break all pages if not converted into existing full-page error states.
  - Inline formatting may persist if chart modules are not migrated incrementally.

### Phase 2 — UX Infrastructure
- objective:
  - Add viewport state, loading progress state, and responsive decision helpers before changing page layouts.
- files affected:
  - `bangalore_intelligence/components/layout/responsive.py`
  - `bangalore_intelligence/utils/css_injector.py`
  - `bangalore_intelligence/components/filter_panel.py`
  - `bangalore_intelligence/filters/state.py`
- systems introduced:
  - `viewport_width` session state.
  - Breakpoint classification helpers.
  - Filter-strip progress state.
  - Compact degradation flags.
- architecture dependencies:
  - Depends on current session state initialization.
  - Uses existing breakpoint constants in `config/layout.py`; the missing layer is browser-width capture and wiring into `components/layout/responsive.py`.
  - Must remain presentation infrastructure, not chart logic.
- implementation procedure:
  - Inject a small viewport-width component once near app startup.
  - Add breakpoint helper functions consumed by page renderer and components.
  - Add filter progress state keys and CSS class hooks.
  - Preserve `get_column_split()` and `get_chart_heights()` as the public responsive API.
- validation checklist:
  - Desktop, laptop, tablet, and compact breakpoints resolve deterministically.
  - Filter strip shows a progress indicator only during rerun/loading state.
  - Compact mode does not create horizontal scroll.
- risk if implemented incorrectly:
  - Updating session state from a component can cause rerun loops.
  - CSS-only responsive behavior can conflict with Streamlit columns unless page logic reads the same breakpoint state.

### Phase 3 — Interaction Systems
- objective:
  - Complete fullscreen, Advanced Lab controls, and Lab-mode state isolation.
- files affected:
  - `bangalore_intelligence/components/chart_container.py`
  - `bangalore_intelligence/dashboards/traffic/pages/p6_advanced_lab.py`
  - `bangalore_intelligence/dashboards/aqi/pages/p6_advanced_lab.py`
  - `bangalore_intelligence/data_layer/page_bundles.py`
  - `bangalore_intelligence/filters/state.py`
  - `bangalore_intelligence/filters/interaction.py`
- systems introduced:
  - Fullscreen state per eligible chart key: `t13_radar`, `t02_parcoords`, `a15_pairplot`, `a02_calendar`.
  - Collapse/exit control.
  - T-13 radar area toggle panel.
  - A-15 AQI category toggle panel.
  - Lab filter suspension using full datasets.
- architecture dependencies:
  - Depends on Phase 2 viewport classification.
  - Depends on existing `chart_container()` and page bundle pattern.
- implementation procedure:
  - Reuse existing `fullscreen_key` metadata already passed through page bundles.
  - Add explicit fullscreen-eligible chart keys.
  - Store fullscreen state under chart-scoped session keys.
  - In fullscreen mode, render only the selected chart plus toolbar.
  - Add Lab breadcrumb parity to Traffic.
  - Build Lab control panels in page/bundle layer; do not put controls in chart render functions.
- validation checklist:
  - `t13_radar`, `t02_parcoords`, `a15_pairplot`, and `a02_calendar` enter/exit fullscreen without losing current page state.
  - Non-eligible charts never show active fullscreen behavior.
  - T-13 overlay limit of 4 is enforced.
  - Lab charts render from full datasets when Lab mode is active.
- risk if implemented incorrectly:
  - Fullscreen can duplicate charts if page-level conditional rendering does not hide normal content.
  - Lab controls can accidentally leak into global filters if they reuse global filter keys.

### Phase 4 — Responsive Architecture
- objective:
  - Convert viewport detection into concrete layout, degradation, and accessibility behavior.
- files affected:
  - `bangalore_intelligence/components/page_production.py`
  - `bangalore_intelligence/components/layout/responsive.py`
  - `bangalore_intelligence/components/filter_panel.py`
  - `bangalore_intelligence/components/metric_strip.py`
  - `bangalore_intelligence/utils/css_injector.py`
- systems introduced:
  - Laptop gauge hiding and secondary KPI collapse.
  - Tablet single-column page layout.
  - Compact filter overlay/degradation warning.
  - A-02 fullscreen recommendation banner.
  - T-11 tablet auto-collapse behavior.
- architecture dependencies:
  - Depends on Phase 2 viewport state.
  - Must preserve page bundle pipeline and chart container system.
- implementation procedure:
  - Add breakpoint helpers that return layout modes, not raw width checks scattered across pages.
  - Let `render_production_page()` choose column layout from breakpoint helpers.
  - Move chart-specific responsive exceptions into bundle metadata.
  - Keep CSS media rules aligned with Python breakpoint names.
- validation checklist:
  - 1920px content remains capped at current max width.
  - 1280px has no horizontal scroll and readable KPI values.
  - 1024px renders single-column analytical flow.
  - <768px shows compact degradation guidance and hides Advanced Lab entry.
- risk if implemented incorrectly:
  - Responsive fixes can make desktop density worse.
  - Chart heights can become inconsistent if hardcoded in page modules.

### Phase 5 — Export Systems
- objective:
  - Add self-contained chart, report, and executive export flows.
- files affected:
  - `bangalore_intelligence/utils/export.py`
  - `bangalore_intelligence/utils/formatters.py`
  - `bangalore_intelligence/components/chart_container.py`
  - `bangalore_intelligence/components/filter_panel.py`
  - `bangalore_intelligence/data_layer/page_bundles.py`
  - `bangalore_intelligence/requirements.txt`
- systems introduced:
  - `apply_export_theme()`
  - `export_chart_png()`
  - `generate_pdf_report()`
  - `generate_executive_summary()`
  - Filter-preserving metadata footers.
- architecture dependencies:
  - Depends on Phase 1 formatters.
  - Depends on Phase 3 fullscreen toolbar.
  - Depends on `kaleido`.
- implementation procedure:
  - Implement PNG export first.
  - Use deep copies of Plotly figures before applying light export theme.
  - Add fullscreen toolbar download button for per-chart PNG.
  - Add persistent report export button to filter strip only after PDF generation works.
- validation checklist:
  - Exported PNG is 1200x700 at scale 2 and legible on white background.
  - Filename follows `BUIP_[DashboardCode]_[ChartCode]_[YYYYMMDD]_[HHMMSS].png`.
  - PDF includes cover, summary, chart pages, data notes, and filter metadata.
  - Export does not mutate the on-screen dark-theme figure.
- risk if implemented incorrectly:
  - Export theming can mutate live figures if no deep copy is used.
  - Missing `kaleido` causes runtime export failure after UI is already visible.

### Phase 6 — Accessibility + Governance
- objective:
  - Finish accessibility and production governance behavior that is still partial.
- files affected:
  - `bangalore_intelligence/utils/css_injector.py`
  - `bangalore_intelligence/utils/annotations.py`
  - `bangalore_intelligence/components/chart_container.py`
  - `bangalore_intelligence/components/filter_panel.py`
- systems introduced:
  - Complete reduced-motion CSS coverage.
  - Focus-visible styles across custom HTML blocks.
  - Annotation factories with tokenized styles and count governance.
  - Long-session notification.
- architecture dependencies:
  - Depends on current theme tokens.
  - Must not hardcode color values outside theme/config.
- implementation procedure:
  - Extend existing reduced-motion block to cover chart appear, nav arrows, gauge rings, and progress animations.
  - Centralize annotation dict construction in `utils/annotations.py`.
  - Enforce max 3 visible annotations per chart through helper APIs.
  - Add session-start and notification-dismiss state keys.
- validation checklist:
  - Existing reduced-motion CSS remains in place and is extended to cover chart appear, nav arrows, gauge rings, and progress animations.
  - OS reduced-motion setting disables shimmer and transition effects.
  - Keyboard focus is visible on buttons, tabs, and chart toolbar controls.
  - Annotation factories produce Plotly-compatible dicts with tokenized styling.
  - Long-session banner appears once after the configured threshold and dismisses cleanly.
- risk if implemented incorrectly:
  - Overbroad CSS can disable Plotly interaction affordances.
  - Annotation helpers can become another duplicated styling layer if chart modules keep inline annotation dicts.

### Phase 7 — Testing + Validation
- objective:
  - Add regression tests for data, state, formatting, validators, and chart smoke paths.
- files affected:
  - `bangalore_intelligence/tests/`
  - `bangalore_intelligence/requirements.txt`
  - `bangalore_intelligence/pytest.ini` or `pyproject.toml`
- systems introduced:
  - Loader tests.
  - Formatter tests.
  - Validator tests.
  - Session state tests.
  - Chart smoke tests.
  - Export utility tests.
- architecture dependencies:
  - Depends on Phase 1 validators and formatters.
  - Depends on existing pure chart contract: chart modules return figures and do not render Streamlit directly.
- implementation procedure:
  - Add `pytest` dependency.
  - Test pure functions first.
  - Smoke-test chart render functions with small fixture data.
  - Add state tests after interaction and fullscreen keys are stable.
- validation checklist:
  - Extreme filters do not crash page bundle builders.
  - Cross-dashboard state is preserved on dashboard switch.
  - Empty filtered data returns existing empty-state flags.
  - Export helpers produce bytes and expected filenames.
- risk if implemented incorrectly:
  - Tests that import Streamlit page modules too early can become brittle.
  - Fixtures that duplicate production data shape incorrectly can mask schema bugs.

---

## 3. Detailed Missing Feature Specifications

### Dependency Completion

#### Purpose
The dependency layer exists to make specified interaction and export systems available at runtime. It integrates with click handling, Plotly image export, PDF generation, and automated tests.

#### Current State
`requirements.txt` exists but only includes `streamlit`, `pandas`, `numpy`, `plotly`, and `pyarrow`. Missing dependencies remain for PNG export, PDF export, and tests. Click-event dependency selection is unresolved because `streamlit-plotly-events` must be verified against the installed Plotly version before it is added.

#### Files To Modify
- `bangalore_intelligence/requirements.txt`

#### Required New Files
- None

#### Session State Requirements
- None

#### Data Flow
- Trigger: environment setup or deployment install.
- Processing flow: package resolver installs the required runtime libraries.
- Render/update flow: application imports succeed when interaction/export code paths execute.
- Dependency chain: a verified click-event integration supports drilldown architecture; `kaleido` supports `fig.to_image()`; PDF package supports report export.

#### UI/UX Behavior
- No direct UI. Failure mode appears as disabled or failed interactive/export controls.

#### Backend Logic
- No runtime logic beyond imports and feature availability checks.

#### Implementation Procedure
1. Verify the click-event package against the installed Plotly major version.
2. Add missing packages without removing existing packages.
3. Prefer one PDF engine; do not install both unless a concrete rendering need requires it.
4. Add `pytest` only when Phase 7 test scaffolding begins.
5. Do not add unused future database packages.

#### Code Skeleton
```text
# Verify against installed Plotly before committing this dependency.
streamlit-plotly-events>=0.0.6
kaleido>=0.2.1,<0.3
reportlab>=4.0.0
pytest>=8.0.0
```

#### Validation Checklist
- Import the selected click-event package successfully under the installed Plotly major version.
- `plotly.graph_objects.Figure().to_image(format="png")` succeeds.
- Selected PDF engine imports successfully.
- Existing app startup remains unchanged.

#### Common Failure Modes
- Installing `kaleido` without a version constraint and not validating export until late.
- Adding `streamlit-plotly-events` blindly in an environment where Plotly 6.x breaks compatibility.
- Adding PDF dependencies before selecting a single PDF implementation path.
- Adding packages to a root-level file instead of `bangalore_intelligence/requirements.txt`.

### Central Formatter Completion

#### Purpose
The formatter layer standardizes all visible numbers, dates, categories, filter summaries, and export metadata. It integrates with filter strip labels, chart captions, tooltips, KPI notes, and export footers.

#### Current State
`utils/formatters.py` already contains five basic numeric formatters: `fmt_congestion()`, `fmt_speed()`, `fmt_pm25()`, `fmt_pct()`, and `fmt_count()`. Date formatting, AQI category mapping, season labels, filter summaries, severity labels, additional meteorological units, coordinates, and confidence intervals are missing.

#### Files To Modify
- `bangalore_intelligence/utils/formatters.py`
- Chart modules that still inline tooltip formatting
- `bangalore_intelligence/components/filter_panel.py`
- `bangalore_intelligence/utils/export.py` after export is introduced

#### Required New Files
- None

#### Session State Requirements
- Reads filter dictionaries or session-derived filter snapshots passed as parameters.
- Must not import or read `st.session_state` directly.

#### Data Flow
- Trigger: component/chart/export needs display text.
- Processing flow: raw scalar/date/filter values enter formatter functions.
- Render/update flow: returned strings are embedded in UI, hover templates, captions, or export footers.
- Dependency chain: export and tests depend on stable formatter outputs.

#### UI/UX Behavior
- Dates display as concise month/year labels in filters and axes.
- AQI category labels match existing category semantics.
- Filter summaries are human-readable and reproduce the active analytical scope.
- Fallback behavior returns `—` for null/invalid display values where appropriate.
- Accessibility: formatted values preserve units and avoid ambiguous abbreviations in export footers.

#### Backend Logic
- Pure functions only.
- Accept `datetime`, `date`, `Timestamp`, strings, or null values defensively.
- No chart rendering and no Streamlit calls.

#### Implementation Procedure
1. Implement date and date-range formatters first.
2. Implement AQI and severity formatters using existing category constants.
3. Implement unit formatters for meteorological values.
4. Implement `fmt_filter_summary(filters)` using a plain dict contract.
5. Replace inline tooltip formatting incrementally chart-by-chart.
6. Add formatter tests before large tooltip migration.

#### Code Skeleton
```python
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping

def fmt_date(val: Any, format: str = "short") -> str:
    """Return a dashboard-safe date label such as 'Jan 2022'."""
    ...

def fmt_date_long(val: Any) -> str:
    """Return a long date label such as 'January 2022'."""
    ...

def fmt_date_range(start: Any, end: Any) -> str:
    """Return 'Jan 2022 - Aug 2024' for visible filter and export labels."""
    ...

def fmt_aqi_category(pm25: float | int | None) -> str:
    """Map PM2.5 value to the platform AQI category label."""
    ...

def fmt_filter_summary(filters: Mapping[str, Any]) -> str:
    """Return a reproducible summary of active date, area, road, category, and season filters."""
    ...
```

#### Validation Checklist
- Null values return safe placeholders.
- Date ranges preserve chronological order and formatting.
- PM2.5 boundary values map to expected categories.
- Filter summary handles all/default filters without noisy output.
- Chart tooltip spot-check shows no raw unformatted floats.

#### Common Failure Modes
- Importing Streamlit inside formatter functions.
- Diverging AQI category thresholds from chart color scales.
- Returning Unicode-only symbols in strings used for filenames.
- Formatting numbers twice, producing strings such as `87.3%%`.

### Data Validator Layer

#### Purpose
Validators protect the data boundary before transforms and charts execute. They integrate with loaders, filter application, empty-state behavior, and future real-data ingestion.

#### Current State
`utils/validators.py` is an empty placeholder. Loaders and filters currently trust bootstrap-generated synthetic data.

#### Files To Modify
- `bangalore_intelligence/utils/validators.py`
- `bangalore_intelligence/data_layer/loaders.py`
- `bangalore_intelligence/filters/traffic_filters.py`
- `bangalore_intelligence/filters/aqi_filters.py`

#### Required New Files
- Optional: `bangalore_intelligence/tests/test_validators.py`

#### Session State Requirements
- None directly.
- Filter functions should pass session-derived dates into validation functions as explicit parameters.

#### Data Flow
- Trigger: data load, cleaning, filter application, or chart bundle construction.
- Processing flow: validators check schema, dtypes, date ranges, row counts, required columns, and outlier bands.
- Render/update flow: validation errors should surface through existing page-level error or empty-state behavior.
- Dependency chain: loaders call schema validators; filters call date validators; chart containers consume low-row or empty-state decisions.

#### UI/UX Behavior
- Invalid data shows a full-page operational error rather than a broken chart stack trace.
- Low-sample filtered views show warnings instead of misleading charts.
- Accessibility: error text must be readable and not rely on color alone.

#### Backend Logic
- Define a typed `ValidationError` or use `ValueError` consistently.
- Keep validation pure and deterministic.
- Do not mutate input DataFrames unless explicitly documented.

#### Implementation Procedure
1. Define expected traffic and AQI schema from `config/data_config.py`.
2. Implement generic column and row-count validators.
3. Implement traffic/AQI schema validators.
4. Add loader calls after cleaned data is loaded.
5. Add date-range validation inside filter application.
6. Add tests for valid, missing-column, wrong-type, and empty-row cases.

#### Code Skeleton
```python
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import pandas as pd

@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    message: str = ""

def validate_required_columns(df: pd.DataFrame, cols: Sequence[str]) -> ValidationResult:
    """Verify that all required columns are present."""
    ...

def validate_traffic_schema(df: pd.DataFrame) -> ValidationResult:
    """Validate traffic dataset columns and critical dtypes."""
    ...

def validate_aqi_schema(df: pd.DataFrame) -> ValidationResult:
    """Validate AQI dataset columns and critical dtypes."""
    ...

def validate_date_range(df: pd.DataFrame, start: Any, end: Any, date_col: str) -> ValidationResult:
    """Validate requested filter range against dataset bounds."""
    ...

def validate_row_count(df: pd.DataFrame, min_rows: int) -> ValidationResult:
    """Return warning/error semantics for low or empty filtered datasets."""
    ...
```

#### Validation Checklist
- Missing column returns a clear message naming the column.
- Empty DataFrames are not treated as schema failures.
- Reversed date range is rejected.
- Single-month and single-road filters produce valid low-sample warnings, not crashes.

#### Common Failure Modes
- Raising exceptions too deep in a chart path.
- Validating after transforms have already dropped required raw columns.
- Hardcoding column names already defined in `config/data_config.py`.

### Viewport Detection and Responsive State

#### Purpose
Viewport detection converts the UX breakpoint spec into application state. It integrates with page layout, KPI density, chart heights, Advanced Lab gating, filter layout, and fullscreen recommendations.

#### Current State
`components/layout/responsive.py` has static helpers but no actual viewport width detection. Layout relies primarily on Streamlit column compression.

#### Files To Modify
- `bangalore_intelligence/components/layout/responsive.py`
- `bangalore_intelligence/components/page_production.py`
- `bangalore_intelligence/components/filter_panel.py`
- `bangalore_intelligence/components/metric_strip.py`
- `bangalore_intelligence/utils/css_injector.py`
- `bangalore_intelligence/app.py`

#### Required New Files
- Optional: `bangalore_intelligence/components/layout/viewport.py`

#### Session State Requirements
- `viewport_width`
- `viewport_breakpoint`
- `compact_mode`
- `advanced_lab_disabled_compact`

#### Data Flow
- Trigger: page startup and browser resize.
- Processing flow: browser width is written to session state; responsive helpers classify width.
- Render/update flow: page renderer chooses column split, chart heights, collapsible behavior, and warnings.
- Dependency chain: fullscreen recommendation banners and compact degradation depend on breakpoint state.

#### UI/UX Behavior
- Laptop: hide KPI gauge rings, collapse secondary KPI row, condense filter labels.
- Tablet: single-column chart layout and 2x2 KPI grid.
- Compact: all nonessential charts collapse, filter overlay appears, Advanced Lab is blocked.
- Fallback: unknown width uses desktop-safe defaults.
- Accessibility: compact warning must be text-visible, not color-only.

#### Backend Logic
- Width detection should be isolated from layout policy.
- Breakpoint helpers should return named modes.
- Avoid rerun loops by updating state only when width changes materially.

#### Implementation Procedure
1. Add a viewport helper component or startup hook.
2. Add `get_breakpoint(width)` and `is_compact(width)` helpers.
3. Update `get_column_split()` to accept breakpoint/layout mode.
4. Update `render_production_page()` to use responsive helpers.
5. Add compact/laptop CSS rules aligned with helper names.

#### Code Skeleton
```python
from __future__ import annotations

from typing import Literal

Breakpoint = Literal["compact", "tablet", "laptop", "desktop", "ultrawide"]

def get_breakpoint(width: int | None) -> Breakpoint:
    """Classify viewport width according to SUAQIS breakpoints."""
    ...

def get_column_split(layout: str = "hero_support", width: int | None = None) -> list[int]:
    """Return ratio list after breakpoint-aware layout decisions."""
    ...

def should_collapse_chart(chart_id: str, width: int | None) -> bool:
    """Return whether chart should move behind progressive disclosure."""
    ...
```

#### Validation Checklist
- Breakpoint boundaries at 768, 1024, 1280, and 1920 px behave as specified.
- Compact mode shows no horizontal scroll.
- T-11 collapses at tablet width.
- A-02 shows fullscreen recommendation below 1200 px.
- Advanced Lab is not accessible below 768 px.

#### Common Failure Modes
- Writing viewport state every render and causing rerun churn.
- Splitting breakpoint rules between CSS and Python without a shared naming model.
- Changing chart heights per page instead of through shared helpers.

### Fullscreen Chart Mode

#### Purpose
Fullscreen mode makes dense charts inspectable without redesigning the main page. It integrates with `chart_container()`, session state, viewport rules, and export toolbar controls.

#### Current State
`chart_container.py` already accepts `fullscreen_key` and renders a fullscreen-style `⤢` button for charts whose bundle metadata provides that key. The missing pieces are the button handler, session state, fullscreen rendering branch, collapse button, eligible-key enforcement, and export toolbar.

#### Files To Modify
- `bangalore_intelligence/components/chart_container.py`
- `bangalore_intelligence/components/page_production.py`
- `bangalore_intelligence/filters/state.py`
- `bangalore_intelligence/utils/css_injector.py`

#### Required New Files
- None

#### Session State Requirements
- `fullscreen_chart_key`
- `fullscreen_chart_key`
- Optional derived booleans may be computed from `fullscreen_chart_key`; avoid maintaining multiple independent fullscreen booleans.

#### Data Flow
- Trigger: user clicks fullscreen button.
- Processing flow: chart container validates eligibility and sets fullscreen state.
- Render/update flow: page renderer hides normal content and mounts only selected chart at fullscreen height.
- Dependency chain: export toolbar depends on fullscreen state.

#### UI/UX Behavior
- Eligible chart codes: T-13, T-02, A-15, A-02.
- Eligible `fullscreen_key` values in current bundles: `t13_radar`, `t02_parcoords`, `a15_pairplot`, `a02_calendar`.
- Enter button appears as an icon control with accessible help text.
- Exit button renders as `Return to page` or equivalent collapse control near top-left.
- Fullscreen chart uses 100% available width and approximately 85vh height.
- Fallback: non-eligible charts ignore fullscreen keys.
- Accessibility: button must be keyboard focusable and have descriptive help.

#### Backend Logic
- Store one active fullscreen chart at a time.
- Preserve current filters and Lab control state.
- Do not create a second figure; reuse bundle figure unless export applies a copy.

#### Implementation Procedure
1. Define an eligibility set near `chart_container()` or config.
2. Add fullscreen state helpers.
3. Wire the button to set active fullscreen chart.
4. Add page renderer branch that renders only the active chart.
5. Add exit control.
6. Add export toolbar after PNG export is implemented.

#### Code Skeleton
```python
FULLSCREEN_ELIGIBLE = {"t13_radar", "t02_parcoords", "a15_pairplot", "a02_calendar"}

def is_fullscreen_active(fullscreen_key: str | None) -> bool:
    """Return whether this chart is the active fullscreen mount."""
    ...

def set_fullscreen(fullscreen_key: str, dashboard: str) -> None:
    """Set the single active fullscreen chart key."""
    ...

def clear_fullscreen() -> None:
    """Return page to normal analytical layout."""
    ...
```

#### Validation Checklist
- Enter/exit works for all four eligible charts.
- Normal page content is hidden during fullscreen.
- Selection and filter states remain unchanged after exit.
- Browser resize does not trap user in fullscreen.

#### Common Failure Modes
- Rendering fullscreen chart in addition to normal chart.
- Mutating figure height globally instead of passing fullscreen height at render time.
- Letting multiple fullscreen booleans remain true.

### Advanced Lab Control Panels and Isolation

#### Purpose
Advanced Lab controls isolate dense exploratory workflows from the main dashboard. They integrate with Lab gate state, page bundles, radar overlays, pairplot categories, and responsive gating.

#### Current State
`lab_gate.py` and `lab_header.py` exist. AQI Lab has a return breadcrumb; Traffic Lab does not. T-13 and A-15 lack dedicated sidebar-style toggle panels. Lab bundles still apply global filters.

#### Files To Modify
- `bangalore_intelligence/dashboards/traffic/pages/p6_advanced_lab.py`
- `bangalore_intelligence/dashboards/aqi/pages/p6_advanced_lab.py`
- `bangalore_intelligence/data_layer/page_bundles.py`
- `bangalore_intelligence/filters/state.py`
- `bangalore_intelligence/dashboards/traffic/charts/t13_compound_radar.py`
- `bangalore_intelligence/dashboards/aqi/charts/a15_pairplot.py`

#### Required New Files
- Optional: `bangalore_intelligence/components/lab_controls.py`

#### Session State Requirements
- `traffic_lab_gate_passed`
- `aqi_lab_gate_passed`
- Existing Traffic Lab keys to reuse:
  - `traffic_radar_visible_areas`
  - `traffic_radar_focus_area`
  - `traffic_radar_comparison_mode`
  - `traffic_radar_comparison_n`
- Proposed new AQI Lab keys:
  - `aqi_pairplot_visible_categories`
  - `aqi_pairplot_category_preset`
- Proposed new Lab dataset-scope flags:
  - `traffic_lab_use_full_dataset`
  - `aqi_lab_use_full_dataset`

#### Data Flow
- Trigger: user enters Advanced Lab and toggles control panel options.
- Processing flow: Lab control state is converted into chart config.
- Render/update flow: chart modules receive prefiltered/preconfigured chart-ready data through page bundles.
- Dependency chain: Lab isolation depends on state defaults and loader access to full datasets.

#### UI/UX Behavior
- Traffic Lab breadcrumb returns to P1 and resets Lab gate state.
- T-13 area panel supports checkboxes, `Top 3 Stress`, `Baseline 3`, and `Clear All`.
- A-15 category panel supports AQI category checkboxes.
- Overlay limit is 4 with inline warning on fifth selection.
- Compact breakpoint blocks Advanced Lab with a clear message.
- Accessibility: control groups require labels and keyboard-operable buttons.

#### Backend Logic
- Lab state keys must be separate from global filter keys. Do not reuse `traffic_selected_areas`, `aqi_selected_categories`, or `aqi_selected_seasons` for Lab controls.
- Lab bundles should intentionally bypass global date/category filters unless explicitly specified.
- Chart modules remain pure and receive config only.

#### Implementation Procedure
1. Add Traffic breadcrumb parity.
2. Add Lab-specific state defaults.
3. Add reusable Lab control component if both dashboards share patterns.
4. Update Lab bundle builders to use full loaded datasets.
5. Convert control state into chart config.
6. Enforce overlay/category limits before rendering figures.

#### Code Skeleton
```python
def render_traffic_lab_controls(available_areas: list[str], dashboard: str = "traffic") -> list[str]:
    """Render T-13 area overlay controls and return selected areas."""
    ...

def render_aqi_lab_controls(categories: list[str], dashboard: str = "aqi") -> list[str]:
    """Render A-15 category controls and return selected categories."""
    ...

def get_lab_dataset(dashboard: str):
    """Return full clean dataset for Advanced Lab, bypassing global filters."""
    ...
```

#### Validation Checklist
- Traffic breadcrumb works like AQI breadcrumb.
- T-13 never renders more than 4 overlays.
- Quick-select buttons update selections deterministically.
- Global dashboard filters do not shrink Lab datasets.
- Returning from Lab preserves non-Lab dashboard state.

#### Common Failure Modes
- Reusing `traffic_selected_areas` for Lab controls.
- Applying global date filters before Lab chart generation.
- Putting checkbox logic in chart modules.

### Lazy Rendering and Staged Reveal

#### Purpose
Lazy rendering and staged reveal reduce perceived load time and prevent heavy secondary charts from rendering before the analyst asks for them.

#### Current State
`collapsible_section()` exists and `page_production.py` wraps one collapsed chart, but collapsed figures are still built in `data_layer/page_bundles.py` before the expander opens. T-12 remains an eager support chart on Traffic P5. Staged reveal is not implemented.

#### Files To Modify
- `bangalore_intelligence/components/page_production.py`
- `bangalore_intelligence/components/collapsible_section.py`
- `bangalore_intelligence/data_layer/page_bundles.py`
- `bangalore_intelligence/components/loading_state.py`

#### Required New Files
- None

#### Session State Requirements
- `page_stage`
- `chart_reveal_stage`
- `expanded_sections`
- Existing per-section collapse keys

#### Data Flow
- Trigger: page load, filter rerun, or expander open.
- Processing flow: bundle metadata delays heavy figure construction until `content_fn`.
- Render/update flow: KPI skeletons render first, hero chart next, supporting charts last.
- Dependency chain: viewport state may force additional charts into collapsed mode.

#### UI/UX Behavior
- Initial load sequence: filters and KPI skeletons, KPI data, hero chart, short delay, support/collapsed content.
- T-12 should move behind collapse when P5 density requires it at laptop/tablet widths.
- Collapsed sections should not compute hidden figures.
- Reduced-motion setting disables shimmer and reveal animation.

#### Backend Logic
- Bundle entries for lazy charts should carry callables or descriptors, not prebuilt figures.
- Page renderer invokes lazy chart factory only when expanded.
- Caching remains in transform layer, not page UI.

#### Implementation Procedure
1. Replace collapsed `fig` values with `fig_factory` callables or chart descriptors.
2. Update `page_production.py` to call factory inside `content_fn`.
3. Add staged render state for first page load only.
4. Add chart-type skeleton variants only where visual fidelity matters.
5. Keep chart modules pure.

#### Code Skeleton
```python
from collections.abc import Callable

ChartFactory = Callable[[], object]

def build_lazy_chart_config(title: str, factory: ChartFactory, **metadata) -> dict:
    """Store deferred chart construction metadata for collapsed/progressive rendering."""
    ...

def render_lazy_chart(cfg: dict, page_key: str, dashboard: str) -> None:
    """Build and render a chart only after its section is visible."""
    ...
```

#### Validation Checklist
- Collapsed T-15 and A-14 do not build figures until expanded.
- T-12 does not exceed eager chart density rules at responsive breakpoints.
- Cold load shows meaningful skeleton state.
- Filter rerun does not replay decorative chart reveal.

#### Common Failure Modes
- Calling `fig_factory()` while constructing the bundle.
- Introducing `time.sleep()` without a rerun-safe state transition.
- Losing chart interaction metadata when deferring chart creation.

### Filter Strip Progress Bar

#### Purpose
The filter progress bar replaces hidden Streamlit spinner behavior during filter reruns. It integrates with `filter_panel()`, CSS injection, and loading-state governance.

#### Current State
The default Streamlit spinner is hidden. `filter_panel.py` has a static active-filter bar but no animated rerun progress bar or widget disable behavior.

#### Files To Modify
- `bangalore_intelligence/components/filter_panel.py`
- `bangalore_intelligence/utils/css_injector.py`
- `bangalore_intelligence/filters/state.py`

#### Required New Files
- None

#### Session State Requirements
- `traffic_filter_updating`
- `aqi_filter_updating`
- `last_filter_change_at`

#### Data Flow
- Trigger: filter widget value changes.
- Processing flow: update flag set before rerun; cleared after filter state sync.
- Render/update flow: filter strip bottom border becomes animated progress bar; widgets are visually disabled.
- Dependency chain: uses existing active-filter computation.

#### UI/UX Behavior
- 2px animated bar appears only while a rerun/filter update is active.
- Filter controls reduce opacity and ignore double-clicks during update.
- Cold-cache loads may still use inline loader where appropriate.
- Reduced-motion disables sweep animation but keeps static progress indicator.

#### Backend Logic
- Avoid permanent disabled state after exceptions.
- Do not block Streamlit rerender with long sleeps.

#### Implementation Procedure
1. Add CSS classes for updating filter strip.
2. Add state flags with safe default `False`.
3. Set updating flag on widget change callbacks.
4. Clear flag after `_sync_filters_active()`.
5. Add reduced-motion CSS override.

#### Code Skeleton
```python
def mark_filter_updating(prefix: str) -> None:
    """Mark filter controls as updating for the next rerun cycle."""
    ...

def clear_filter_updating(prefix: str) -> None:
    """Clear rerun progress state after filter values have synchronized."""
    ...
```

#### Validation Checklist
- Progress bar appears on filter changes.
- Reset All shows same progress treatment.
- Flag clears after rerun.
- Reduced-motion users see non-animated progress.

#### Common Failure Modes
- Progress state never clears.
- Active-filter bar and progress bar visually conflict.
- Widget callbacks mutate unrelated dashboard state.

### Stale Cache and Long Session Notices

#### Purpose
These systems communicate data freshness and extended review-session risk. They integrate with loaders, filter strip, KPI cards, and export prompts.

#### Current State
No stale-data detection, refresh affordance, session duration tracking, or long-session notification exists. The keys below are proposed additions, not current state.

#### Files To Modify
- `bangalore_intelligence/config/data_config.py`
- `bangalore_intelligence/data_layer/loaders.py`
- `bangalore_intelligence/components/filter_panel.py`
- `bangalore_intelligence/components/kpi_card.py`
- `bangalore_intelligence/filters/state.py`

#### Required New Files
- Optional: `bangalore_intelligence/utils/session_health.py`

#### Session State Requirements
- Proposed app/session keys:
  - `session_start_time`
  - `long_session_notice_dismissed`
- Proposed loader freshness keys:
  - `traffic_data_loaded_at`
  - `aqi_data_loaded_at`
  - `traffic_data_stale`
  - `aqi_data_stale`

#### Data Flow
- Trigger: app startup, data load, or elapsed time threshold.
- Processing flow: timestamps are compared with configured thresholds.
- Render/update flow: filter strip refresh control, KPI stale badges, and long-session banner render conditionally.
- Dependency chain: PDF export provides action for long-session summary.

#### UI/UX Behavior
- Stale indicator appears without blocking analysis.
- Refresh button clears/reloads cached data.
- Long-session notice appears once after the configured threshold and can be dismissed.
- Fallback: static datasets may keep stale detection disabled by default.
- Accessibility: notice text is explicit and includes actionable buttons.

#### Backend Logic
- Use configurable thresholds.
- Cache clearing must target relevant loader functions only.
- Do not auto-refresh while user is interacting.

#### Implementation Procedure
1. Add `STALE_THRESHOLD_SECONDS` to data config.
2. Add a configurable long-session threshold, defaulting to 90 minutes unless product review selects a different value.
3. Store data-loaded timestamps in loader boundary.
4. Add `check_data_freshness()` helper.
5. Render stale badge and refresh button in filter strip.
6. Add long-session state initialized at app startup.
7. Wire Export Summary button after PDF export exists.

#### Code Skeleton
```python
def check_data_freshness(loaded_at: float | None, threshold_seconds: int) -> bool:
    """Return True when cached data should be marked stale."""
    ...

def should_show_long_session_notice(now: float, start: float | None, dismissed: bool) -> bool:
    """Return whether the 90-minute review-session notice should render."""
    ...
```

#### Validation Checklist
- Stale badge appears only after threshold.
- Refresh reloads data and clears stale state.
- Long-session notice appears once and dismisses persistently.
- Static dataset mode does not nag users unnecessarily.

#### Common Failure Modes
- Clearing all Streamlit cache and invalidating unrelated expensive transforms.
- Showing stale badges on every KPI without a single filter-strip explanation.
- Long-session notice reappearing after dismissal.

### Export System

#### Purpose
Exports produce self-contained, filter-preserving artifacts for analyst briefings and executive reporting. They integrate with formatters, fullscreen toolbar, page bundles, and Plotly figures.

#### Current State
No `utils/export.py` exists. No PNG export, PDF export, executive summary export, export button, or export theme is implemented.

#### Files To Modify
- `bangalore_intelligence/components/chart_container.py`
- `bangalore_intelligence/components/filter_panel.py`
- `bangalore_intelligence/data_layer/page_bundles.py`
- `bangalore_intelligence/utils/formatters.py`
- `bangalore_intelligence/requirements.txt`

#### Required New Files
- `bangalore_intelligence/utils/export.py`

#### Session State Requirements
- `export_in_progress`
- `last_export_status`
- `selected_export_chart`
- `executive_export_hero_chart`

#### Data Flow
- Trigger: user clicks PNG, Report, or Executive export.
- Processing flow: copy current figure, apply export theme, add metadata footer, render bytes.
- Render/update flow: `st.download_button()` exposes generated bytes with canonical filename.
- Dependency chain: PNG export precedes PDF export; PDF precedes executive summary export.

#### UI/UX Behavior
- PNG button appears in fullscreen toolbar, not every chart by default.
- Report button appears in filter strip after PDF generation is ready.
- Export uses light-mode chart theme for print readability.
- Fallback: export errors show inline non-blocking error text.
- Accessibility: download buttons have descriptive labels.

#### Backend Logic
- Deep-copy figures before export theme changes.
- Embed active filters and generated timestamp in every artifact.
- Keep export utilities independent from Streamlit except button placement in components.

#### Implementation Procedure
1. Implement `apply_export_theme(fig)`.
2. Implement `build_export_filename()`.
3. Implement `export_chart_png()`.
4. Add fullscreen toolbar download button.
5. Implement PDF report with cover, KPI summary, chart pages, and data notes.
6. Implement one-page executive summary only after report export works.

#### Code Skeleton
```python
from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

import plotly.graph_objects as go

def apply_export_theme(fig: go.Figure) -> go.Figure:
    """Return a light-background copy of fig suitable for print/PDF export."""
    ...

def build_export_filename(
    dashboard_code: str,
    chart_code: str,
    generated_at: datetime | None = None,
    extension: str = "png",
) -> str:
    """Return BUIP filename with dashboard, chart, date, and time."""
    ...

def export_chart_png(fig: go.Figure, title: str, active_filters: Mapping[str, Any]) -> bytes:
    """Render a Plotly figure as PNG bytes with export-safe theme and metadata."""
    ...

def generate_pdf_report(bundle: Mapping[str, Any], active_filters: Mapping[str, Any]) -> bytes:
    """Generate a dashboard report PDF from current page/chart bundle metadata."""
    ...
```

#### Validation Checklist
- Exported chart has white paper background and legible axes.
- Footer includes dashboard, filters, and timestamp.
- Filename is stable and filesystem-safe.
- Live chart style is unchanged after export.
- PDF pages include required sections.

#### Common Failure Modes
- Mutating on-screen figure during export.
- Attempting PDF generation before `kaleido` PNG path works.
- Missing filter summary because export reads session state directly instead of receiving a snapshot.

### Annotation Factory Completion

#### Purpose
Annotation factories centralize callout styling and prevent annotation bloat. They integrate with Plotly chart modules, theme tokens, governance limits, and export preservation.

#### Current State
`utils/annotations.py` returns minimal Plotly-compatible dicts. It lacks tokenized styling, arrow configuration, background boxes, annotation count governance, `add_annotation_callout()`, and `add_quadrant_zone_labels()`.

#### Files To Modify
- `bangalore_intelligence/utils/annotations.py`
- Chart modules with inline annotations
- `bangalore_intelligence/utils/plotly_helpers.py`

#### Required New Files
- None

#### Session State Requirements
- None

#### Data Flow
- Trigger: chart module needs threshold, quadrant, regime, AQI band, or insight annotation.
- Processing flow: chart passes coordinates and semantic type to annotation factory.
- Render/update flow: factory returns Plotly annotation dicts or applies them to figures through helper.
- Dependency chain: export preserves Plotly annotations automatically.

#### UI/UX Behavior
- Font, background, border, and arrow style are consistent across dashboards.
- Maximum three visible annotations per chart.
- Fallback: over-limit annotations are dropped or downgraded based on priority.
- Accessibility: annotation text must be concise and not the only source of semantic meaning.

#### Backend Logic
- Factories accept dashboard/theme context.
- Do not import chart modules.
- Keep output as Plotly-compatible dictionaries.

#### Implementation Procedure
1. Define base annotation style helper.
2. Add dashboard token support.
3. Implement missing helper functions.
4. Migrate chart modules incrementally.
5. Add annotation count guard.

#### Code Skeleton
```python
from __future__ import annotations

from typing import Literal

import plotly.graph_objects as go

AnnotationPriority = Literal["threshold", "quadrant", "callout", "context"]

def step_callout(x: object, y: object, delta_text: str, color: str, dashboard: str = "traffic") -> dict:
    """Build styled step-change callout annotation."""
    ...

def add_annotation_callout(fig: go.Figure, x: object, y: object, text: str, dashboard: str = "traffic") -> go.Figure:
    """Apply a styled callout to fig and return fig."""
    ...

def enforce_annotation_limit(annotations: list[dict], max_count: int = 3) -> list[dict]:
    """Return annotations trimmed according to governance priority."""
    ...
```

#### Validation Checklist
- Annotations render with theme font and colors.
- No chart exceeds 3 visible annotations.
- Exported charts preserve annotations.
- Existing chart meanings remain unchanged after migration.

#### Common Failure Modes
- Hardcoding hex colors in annotation helpers.
- Applying annotation dicts with invalid Plotly keys.
- Removing analytically required threshold annotations while enforcing limits.

### Altair Helper Completion

#### Purpose
Altair helpers support declarative ridgeline and pairplot implementations if the project adopts Altair for dense statistical charts.

#### Current State
`utils/altair_helpers.py` is a full stub with `None` or empty-list returns. Current charts use Plotly, so this should remain an evaluation backlog item unless Altair is intentionally adopted for T-11, A-03, A-15, or T-13 alternatives.

#### Files To Modify
- `bangalore_intelligence/utils/altair_helpers.py`
- Any chart module intentionally migrated to Altair

#### Required New Files
- None

#### Session State Requirements
- None

#### Data Flow
- Trigger: chart module requests an Altair base spec.
- Processing flow: helper builds reusable chart/layer specification.
- Render/update flow: page renderer would need Altair rendering support if used.
- Dependency chain: depends on `altair` package if retained in requirements.

#### UI/UX Behavior
- Altair charts must match current theme tokens and tooltip formatters.
- Fallback: keep Plotly implementation when Altair does not provide clear maintainability improvement.

#### Backend Logic
- Use existing `utils/analytics_kde.py` for KDE data when needed.
- Do not duplicate transform logic in Altair helper.

#### Implementation Procedure
1. Decide whether each candidate chart remains Plotly.
2. Implement only helpers needed by adopted Altair charts.
3. Keep helper API thin and chart-specific config in chart modules.
4. Validate visual parity before replacing existing Plotly charts.

#### Code Skeleton
```python
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

def build_ridgeline_base(data: Any, x_col: str, group_col: str):
    """Return an Altair ridgeline base chart specification."""
    ...

def add_aqi_color_scale():
    """Return AQI category color scale aligned with theme/category tokens."""
    ...

def build_pairplot_base(data: Any, var_cols: Sequence[str], color_col: str):
    """Return an Altair pairplot base specification."""
    ...
```

#### Validation Checklist
- Altair output renders in Streamlit.
- Theme colors match existing Plotly charts.
- Tooltips use centralized formatter output.
- Dense chart remains readable at target viewport widths.

#### Common Failure Modes
- Rebuilding existing working Plotly charts without a concrete benefit.
- Putting KDE computation inside Altair helper instead of transform/KDE utilities.
- Creating a second theme system for Altair.

### Shared Transform Utilities

#### Purpose
`data_layer/transformers.py` should host dashboard-agnostic transform helpers shared by traffic and AQI modules, preventing duplicated date bucketing, binning, rolling windows, and derived-column helpers.

#### Current State
`data_layer/transformers.py` contains only a placeholder comment. Existing dashboard-specific transform modules are functional.

#### Files To Modify
- `bangalore_intelligence/data_layer/transformers.py`
- `bangalore_intelligence/data_layer/traffic_transforms.py`
- `bangalore_intelligence/data_layer/aqi_transforms.py`

#### Required New Files
- Optional: tests for shared transform helpers

#### Session State Requirements
- None

#### Data Flow
- Trigger: traffic or AQI transform module needs a shared helper.
- Processing flow: dashboard-specific transform calls shared pure utility.
- Render/update flow: page bundles consume existing transform outputs unchanged.
- Dependency chain: must preserve cached transform boundaries.

#### UI/UX Behavior
- No direct UI.
- Indirectly ensures consistent buckets and rolling windows across dashboards.

#### Backend Logic
- Functions must be pure and accept DataFrames/Series explicitly.
- Shared helpers should not know dashboard page or chart IDs.
- Cache at expensive public transform functions, not every tiny helper.

#### Implementation Procedure
1. Identify actual duplicated logic before adding helpers.
2. Move only dashboard-agnostic utilities.
3. Preserve public transform function signatures.
4. Add tests for edge cases such as empty frames and missing dates.

#### Code Skeleton
```python
from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

def add_month_bucket(df: pd.DataFrame, date_col: str, output_col: str = "month") -> pd.DataFrame:
    """Return a copy with a normalized month bucket column."""
    ...

def bin_numeric_series(series: pd.Series, bins: Sequence[float], labels: Sequence[str]) -> pd.Series:
    """Return categorical bins for a numeric series."""
    ...

def rolling_mean(df: pd.DataFrame, value_col: str, window: int, group_cols: Sequence[str] | None = None) -> pd.Series:
    """Return rolling mean with optional group boundaries."""
    ...
```

#### Validation Checklist
- Existing page bundles produce identical shapes after refactor.
- Cache hits remain effective.
- Shared helpers handle empty input without crashing.

#### Common Failure Modes
- Moving chart-specific logic into shared utilities.
- Changing public transform output columns.
- Over-caching helper functions and creating stale intermediate state.

### Mock Data Upgrade

#### Purpose
The mock/demo path should present internally consistent dashboard content without bypassing current architecture. It integrates with `page_template.py`, `config/mock_content.py`, and transform outputs.

#### Current State
`config/mock_content.py` uses static strings. Mock KPI and insight values are not guaranteed to align with real transforms.

#### Files To Modify
- `bangalore_intelligence/config/mock_content.py`
- `bangalore_intelligence/components/page_template.py`

#### Required New Files
- None

#### Session State Requirements
- Optional: `demo_mode`

#### Data Flow
- Trigger: demo/presentation page rendering.
- Processing flow: mock generator derives stable mock values from real transform schemas or sampled fixture data.
- Render/update flow: page template receives content shaped like production bundles.
- Dependency chain: should mirror page bundle contracts.

#### UI/UX Behavior
- Demo values should be coherent across KPI, chart titles, and insight text.
- Fallback: if data is unavailable, static content can remain as last resort.

#### Backend Logic
- Do not duplicate production bundle logic.
- Keep mock values deterministic for repeatable demos.

#### Implementation Procedure
1. Define a bundle-like mock contract.
2. Generate mock KPIs from transform outputs or stable fixtures.
3. Generate insight text from the same values.
4. Keep static strings only for page titles and descriptions.

#### Code Skeleton
```python
def get_page_mock(page_key: str, dashboard: str) -> dict:
    """Return presentation-mode content matching production bundle shape."""
    ...

def build_mock_kpis(seed_data: dict) -> list[dict]:
    """Build internally consistent KPI card inputs for demo mode."""
    ...
```

#### Validation Checklist
- KPI values referenced in insight text match rendered KPI cards.
- Mock bundle shape matches production bundle expectations.
- Demo mode does not affect production data paths.

#### Common Failure Modes
- Creating a second page-rendering pipeline.
- Letting mock content drift from actual page bundle keys.
- Using random values that change on every rerun.

### Production Test Suite

#### Purpose
Tests protect the remaining architecture while interaction, export, and responsive systems are added. They integrate with validators, formatters, loaders, state helpers, transforms, and chart render contracts.

#### Current State
No `tests/` directory exists. Manual quality gates are specified in the UX docs, but automated tests are absent.

#### Files To Modify
- `bangalore_intelligence/requirements.txt`

#### Required New Files
- `bangalore_intelligence/tests/test_formatters.py`
- `bangalore_intelligence/tests/test_validators.py`
- `bangalore_intelligence/tests/test_loaders.py`
- `bangalore_intelligence/tests/test_filters.py`
- `bangalore_intelligence/tests/test_page_bundles.py`
- `bangalore_intelligence/tests/test_chart_smoke.py`
- Optional: `bangalore_intelligence/pytest.ini`

#### Session State Requirements
- Tests should initialize or monkeypatch session state keys when needed.

#### Data Flow
- Trigger: developer runs `pytest`.
- Processing flow: fixtures create minimal valid data; tests exercise pure utilities and bundle/chart contracts.
- Render/update flow: chart tests assert figures return without Streamlit rendering.
- Dependency chain: relies on validators and formatters being implemented first.

#### UI/UX Behavior
- No direct UI.
- Protects UX rules such as state preservation, empty-state handling, and formatted labels.

#### Backend Logic
- Keep tests focused on pure functions where possible.
- Avoid snapshotting entire Plotly specs unless testing a narrow contract.

#### Implementation Procedure
1. Add pytest dependency.
2. Add formatter and validator tests first.
3. Add loader and filter tests using existing data files.
4. Add page bundle tests for empty/extreme filters.
5. Add smoke tests for representative chart modules.
6. Add export tests after export utilities exist.

#### Code Skeleton
```python
def test_fmt_date_range_outputs_month_year_range():
    ...

def test_validate_required_columns_reports_missing_column():
    ...

def test_extreme_traffic_filter_returns_empty_or_valid_bundle():
    ...

def test_t01_render_returns_plotly_figure(sample_traffic_area_summary):
    ...
```

#### Validation Checklist
- Tests run from `bangalore_intelligence` root.
- No tests require live browser access.
- Chart modules remain pure data-to-figure functions.
- Extreme filter tests cover zero-row and low-row cases.

#### Common Failure Modes
- Importing Streamlit app/router in unit tests and triggering page rendering.
- Asserting brittle full Plotly JSON structures.
- Using production cache state across tests without clearing it.

---

## 4. Cross-System Dependency Graph

- Foundation dependency chain:
  - `requirements.txt` missing packages -> interaction/export imports.
  - `utils/formatters.py` -> filter strip summaries -> export metadata -> PDF reports.
  - `utils/validators.py` -> loaders/filters -> page bundle reliability -> automated tests.
- UX dependency chain:
  - viewport detection -> responsive layout -> compact Advanced Lab gating -> fullscreen recommendation banners.
  - filter progress state -> loading hierarchy -> reduced-motion behavior.
- Interaction dependency chain:
  - fullscreen state -> fullscreen chart render branch -> fullscreen export toolbar -> per-chart PNG export.
  - Lab-specific state -> T-13/A-15 control panels -> Lab data isolation -> Lab validation tests.
- Export dependency chain:
  - `kaleido` + `apply_export_theme()` -> PNG bytes -> PDF chart pages -> executive summary.
  - `fmt_filter_summary()` -> PNG footer -> PDF metadata -> report reproducibility.
- Parallelizable work:
  - Formatters and validators can be implemented in parallel.
  - Annotation factory completion can proceed while viewport detection is implemented.
  - Test scaffolding can begin after formatter/validator signatures stabilize.
  - Mock data upgrade can proceed independently after production bundle shape is understood.
- Should never be implemented simultaneously:
  - Fullscreen page-render branching and page responsive branching in the same files without sequencing; both alter `page_production.py`.
  - Export theming and chart theme refactors at the same time; this risks mutating live chart style.
  - Lab global-filter suspension and global filter refactoring at the same time; this risks state leakage.
  - Shared transform refactors and chart bundle rewrites at the same time; this risks changing output schemas invisibly.

---

## 5. Technical Debt Warnings

- Architectural risks:
  - `page_production.py` is now a high-leverage integration point. Fullscreen, responsive layout, staged reveal, and lazy rendering all touch it; changes must be sequenced.
  - `data_layer/page_bundles.py` currently constructs figures eagerly, including collapsed chart figures. True lazy loading requires changing bundle shape carefully.
- State explosion risks:
  - Lab, fullscreen, export, stale-cache, long-session, and responsive keys can clutter `st.session_state`. Prefix all new keys by dashboard and concern.
  - Do not reuse global filter keys for Lab controls.
- Rerender bottlenecks:
  - Viewport detection can cause rerun loops if it writes width state every render.
  - Lazy sections are not truly lazy if chart factories are invoked while building bundles.
- Duplicated logic risks:
  - Formatter functions must replace inline tooltip formatting gradually; partial adoption can leave inconsistent labels.
  - Annotation helpers must replace inline dicts; otherwise a second styling system is created.
- Styling inconsistency risks:
  - Export light-theme overrides must live only in export utilities and must not alter dashboard theme tokens.
  - Responsive CSS rules must align with Python breakpoint helpers.
- Cache invalidation risks:
  - Stale-cache refresh must target loader caches, not every cached transform globally.
  - Shared transform helpers should not be over-cached independently of their public transform functions.

---

## 6. Production Readiness Checklist

- responsiveness:
  - [ ] Viewport width is available as session state.
  - [ ] Laptop, tablet, compact, desktop, and ultrawide layouts match breakpoint rules.
  - [ ] No horizontal scroll at 1280px, 1024px, or compact width.
  - [ ] Advanced Lab is blocked below compact threshold.
- fullscreen behavior:
  - [ ] T-13, T-02, A-15, and A-02 enter and exit fullscreen.
  - [ ] Normal page content is hidden while fullscreen is active.
  - [ ] Fullscreen state does not erase filters, selections, or Lab controls.
  - [ ] Non-eligible charts do not activate fullscreen behavior.
- export systems:
  - [ ] PNG export produces light-theme, filter-preserving images.
  - [ ] PDF report includes cover, KPI summary, chart pages, data notes, and metadata.
  - [ ] Executive summary export produces one-page stakeholder report.
  - [ ] Export does not mutate live on-screen chart figures.
- loading systems:
  - [ ] Filter-strip progress bar appears during filter reruns.
  - [ ] Hidden collapsed charts do not build figures until expanded.
  - [ ] Staged reveal does not replay unnecessarily after filter changes.
  - [ ] Reduced-motion disables shimmer and animated progress.
- accessibility:
  - [ ] Focus-visible styles are present on buttons, tabs, filters, and toolbar controls.
  - [ ] Reduced-motion CSS covers skeletons, chart appearance, nav arrows, gauge rings, and progress bars.
  - [ ] Error, stale, compact, and long-session notices include text, not color-only signals.
- interaction consistency:
  - [ ] T-13 Lab controls enforce max 4 overlays.
  - [ ] A-15 category controls are separate from global AQI filters.
  - [ ] Drilldown and selection states remain clearable.
  - [ ] Traffic and AQI dashboard filter states survive dashboard switching.
- state persistence:
  - [ ] New session keys are initialized in one place.
  - [ ] Export, fullscreen, Lab, stale-cache, and viewport keys are dashboard-scoped.
  - [ ] Dismissed notices do not reappear in the same session.
- testing coverage:
  - [ ] Formatter tests cover nulls, date ranges, PM2.5 category boundaries, and filter summaries.
  - [ ] Validator tests cover schemas, date ranges, low-row states, and missing columns.
  - [ ] Loader tests verify schemas and nonzero data.
  - [ ] Page bundle tests cover empty and extreme filters.
  - [ ] Chart smoke tests confirm representative chart modules return figures without Streamlit rendering.
  - [ ] Export tests confirm bytes and filenames for PNG/PDF utilities.
