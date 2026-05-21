# SUAQIS · SMART URBAN AIR QUALITY + INTELLIGENCE SYSTEM
## Visual UX Architecture Blueprint
### Enterprise Design Specification · Interaction Systems · Analytical Experience Design

**Document Type:** Visual UX Architecture · Product Design Specification  
**Status:** Design Engineering Phase · Pre-Implementation Reference  
**Scope:** Traffic Intelligence Dashboard + AQI Environmental Intelligence Dashboard  
**Target Stack:** Streamlit · Plotly · Altair · Custom CSS Injection  
**Companion Document:** `bangalore_implementation_architecture.md` (Engineering Architecture — preserved in full)  
**Not Included:** Backend refactoring · Folder structure changes · Streamlit replacement  

---

> **Architecture Relationship:** This document is a design layer specification that sits entirely above the engineering architecture. It defines *how* the existing 80-module, 30-chart platform looks, feels, moves, and communicates. Nothing in this document contradicts or replaces the engineering blueprint. Every visual behavior defined here maps to existing components, pages, and chart modules.

---

# PART 1 — ENTERPRISE VISUAL DESIGN PHILOSOPHY

---

## 1.1 · Platform Identity Declaration

The Bangalore Urban Intelligence Platform is not a data visualization project. It is an **operational intelligence environment** — a system that transforms raw traffic telemetry and atmospheric sensor readings into analyst-grade situational awareness.

The visual identity must reflect that purpose without compromise.

This means the platform looks and feels like:
- A mission-critical monitoring environment used by infrastructure planners
- An intelligence briefing tool for urban mobility and environmental operations teams
- A Bloomberg Terminal-class analytical system applied to civic infrastructure

It does **not** look like:
- A university capstone project
- A Kaggle competition notebook rendered as a web app
- A default Streamlit dark theme with charts dropped into `st.columns(3)`
- An aesthetics-first dashboard where color and animation outweigh readability

**Design Target Reference Systems:**
- Grafana (operational clarity, metric hierarchy, dense information without noise)
- Datadog (enterprise dark theme, signal-first typography, sidebar governance)
- Bloomberg Terminal (information density without clutter, restrained color logic)
- Palantir Gotham (analytical narrative, drilldown discipline, spatial data layers)
- Tableau Server Enterprise (layout consistency, chart-to-insight sequencing)

The platform serves two datasets with different analytical purposes: the Bangalore Traffic Dataset (8,936 rows, 16 columns including congestion levels, incident counts, pedestrian volumes, weather conditions, roadwork activity, and modal split across 8 areas and 16 roads) and the AQI Environmental Dataset (1,095 rows, 9 meteorological and PM2.5 columns across 3 years). The visual language must support both domains while maintaining a unified platform identity.

---

## 1.2 · The "High Signal / Low Noise" Mandate

Every visual decision must be evaluated against a single test:

> **Does this element help the analyst understand faster, or does it exist for other reasons?**

If the answer is "other reasons" — decoration, convention, novelty — it does not belong in this platform.

**High Signal elements earn their place:**
- A severity-coded KPI value earns its crimson because it alerts before the chart context can
- A reference line on the speed-collapse threshold scatter (T-09) earns its annotation because it defines a critical behavioral boundary in the congestion data
- A seasonal color band on the AQI ridgeline (A-03) earns its encoding because it separates the monsoon-driven PM2.5 relief from winter stagnation accumulation

**Noise elements are removed without negotiation:**
- Decorative gradients on chart backgrounds that add visual interest but reduce readability
- Animated chart reveals that delay information delivery by more than 300ms
- Drop shadows on already-dark-background cards that add depth without adding information
- Legend items for axis values that are already labeled on the axis
- Chart borders that repeat container structure the spacing already establishes

**Implementation Rule:** Any CSS property, Plotly layout attribute, or Streamlit component styling that cannot be justified by analytical communication is removed. The platform's visual restraint is a feature, not a limitation.

---

## 1.3 · The Two-Dashboard Identity System

The Traffic and AQI dashboards share a platform identity but carry distinct domain personalities.

**Traffic Dashboard Visual Personality: Operational Urgency**
The traffic data reveals a city under chronic congestion pressure. 100% capacity utilization rates appear across multiple roads. Incident-to-congestion relationships show threshold effects. The visual system must communicate *operational stress* — through the crimson severity palette, through the dense but readable KPI scorecard, through the way congestion levels are encoded not as neutral data but as severity gradations.

**AQI Dashboard Visual Personality: Atmospheric Weight**
The PM2.5 data shows a city living under persistent atmospheric burden. Values in the 200+ µg/m³ range — classified as Severe under India NAAQS standards — appear regularly in winter months. The visual system must communicate *chronic environmental pressure* — through the deep navy palette, through the way the calendar heatmap (A-02) shows year-scale pollution persistence, through color encoding that maps WHO classification bands to intuitive severity gradations.

**Shared Platform DNA:**
Both dashboards use the same structural skeleton: dark backgrounds, Inter-family typography, consistent spacing tokens, identical component contracts. The shared components (`kpi_card`, `chart_container`, `hero_section`, `filter_panel`) read `dashboard="traffic"` or `dashboard="aqi"` and apply the correct identity palette — but the underlying structure is identical. This ensures that analysts who work across both dashboards never need to relearn the interface.

---

## 1.4 · Analytical Readability as the Primary UX Metric

Enterprise analytical dashboards fail at readability in three predictable ways:

1. **Visual overload** — too many charts rendered simultaneously, forcing the analyst's attention to scatter rather than sequence
2. **Color noise** — too many hues, inconsistent severity encoding, decorative color that competes with data-encoded color
3. **Context starvation** — charts that display patterns without communicating what the pattern means operationally

The 6-page architecture in the existing engineering blueprint (3 main charts per page, Advanced Lab isolation for dense visuals) already solves problem 1. The color token system in `config/theme.py` already establishes the foundation for solving problem 2. This UX document's primary task is formalizing and deepening both systems, and directly solving problem 3 through the storytelling and hierarchy specifications in Parts 7 and 9.

---

# PART 2 — VISUAL HIERARCHY SYSTEM

---

## 2.1 · The Focal Zone Architecture

Every page in both dashboards is organized into three distinct visual zones. The analyst's eye must travel through these zones in sequence — not because we force it, but because the visual weight hierarchy makes it the path of least resistance.

**Zone 1: The Command Zone (Top 30% of viewport)**
This is where the analyst gets their answer before they dig.
- Contains: page hero section + KPI scorecard row or hero chart title + filter active status indicator
- Visual treatment: highest contrast, largest typography, severity-coded values
- Implementation: `hero_section()` component + `metric_strip()` component + `filter_panel()` component
- Behavior: Always visible without scrolling. The analyst should be able to identify the operational status of the page within 3 seconds of landing.

**Zone 2: The Investigation Zone (Middle 50% of viewport)**
This is where the analyst validates, explores, and discovers.
- Contains: primary and secondary charts (the 2–3 main analytical charts per page)
- Visual treatment: full-width hero chart, supported by a secondary chart in a subordinate column
- Implementation: `chart_container()` wrappers inside `st.columns()` with appropriate ratios
- Behavior: The hero chart occupies the dominant visual position. Supporting charts are visually lighter — smaller, lower contrast titles, thinner borders.

**Zone 3: The Context Zone (Lower 20% of viewport)**
This is where the analyst receives interpretation and navigation.
- Contains: `insight_panel()` ("What This Means"), `nav_card()` ("Investigate Further"), optional collapsible secondary content
- Visual treatment: lower contrast, reduced typography size, muted border emphasis
- Implementation: `insight_panel()` with `collapsible=True` default state open; `nav_card()` with subdued border
- Behavior: Collapsed by default on first load (reduces cognitive overhead). Analysts who want interpretation expand it. Analysts who already understand the data skip it.

---

## 2.2 · Hero Chart Dominance Protocol

The engineering architecture specifies 2–3 charts per page. Of those, one must dominate.

**What "dominance" means visually:**
- The hero chart occupies at minimum 60% of the Investigation Zone's horizontal width
- The hero chart renders at 420–480px height (vs. 300–360px for supporting charts)
- The hero chart title uses the Section Header type scale (16px, weight 600)
- Supporting chart titles use the Chart Title type scale (13px, weight 500)
- The hero chart is the first chart rendered in the DOM — it never appears below a supporting chart in the reading flow

**Per-page hero chart assignments:**

| Dashboard | Page | Hero Chart | Supporting Charts |
|---|---|---|---|
| Traffic | P1 · Command Overview | T-01 Saturation Scorecard | T-08 Incident Cliff |
| Traffic | P2 · Temporal Intelligence | T-03 Stream Graph | T-04 Violin Weekly |
| Traffic | P3 · Spatial Operations | T-05 Quadrant Scatter | T-06 Treemap / T-07 Diverging Bar |
| Traffic | P4 · Threshold Analytics | T-09 Speed Threshold | T-10 PT Decoupling |
| Traffic | P5 · Hidden Patterns | T-11 Ridgeline | T-12 Weather Heatmap (collapsed) |
| Traffic | P6 · Advanced Lab | T-13 Radar | T-02 Parallel Coords / T-14 Hexbin |
| AQI | P1 · Crisis Overview | A-01 Crisis Scorecard | A-05 Persistence Series |
| AQI | P2 · Temporal Patterns | A-02 Calendar Heatmap | A-04 Monthly Variability |
| AQI | P3 · Atmospheric Intelligence | A-06 Stagnation Hexbin | A-07 Extreme Day Radar |
| AQI | P4 · Weather Relationships | A-08 Temp Scatter | A-09 Pressure Trigger / A-10 Wind Rescue |
| AQI | P5 · Hidden Patterns | A-03 Seasonal Ridgeline | A-11 Gust Paradox / A-12 Temp Spread |
| AQI | P6 · Advanced Lab | A-15 Pairplot | A-13 Atm. States / A-14 Season Grid |

---

## 2.3 · Visual Weight Rules

Visual weight is the perceived importance of a UI element — determined by size, contrast, color, and position. These rules govern how the dashboard assigns visual weight:

**Rule 1: Severity Color = Highest Weight**
Any element colored with a severity token (TRAFFIC_CRIMSON, AQI Severe purple) automatically becomes the highest-weight element in its zone. Use severity color only for data that warrants analyst attention. Never use severity color for decoration.

**Rule 2: Position = Implicit Priority**
Top-left renders first. The reading eye defaults to top-left → right → down. Hero charts always occupy the top-left or full-width position. Supporting charts always appear to the right or below.

**Rule 3: Size Establishes Hierarchy**
A 420px-height chart outranks a 300px-height chart in the same row without requiring any other visual differentiation. Do not fight this natural hierarchy by giving supporting charts excessive visual decoration.

**Rule 4: Whitespace as Emphasis**
An element surrounded by generous whitespace appears more important than a densely-packed element. The hero section has `SPACING_XL` (40px) padding above and below. Chart rows have `SPACING_LG` (24px) gaps. KPI cards have `SPACING_MD` (16px) internal padding. Reducing spacing anywhere reduces the implied importance of the surrounding content.

**Rule 5: Muted Color = Low Weight**
`TRAFFIC_TEXT_MUTED` (#8B949E) and `AQI_TEXT_MUTED` (#6B7280) are reserved for non-critical information: chart captions, axis labels, sidebar secondary text, insight panel body text. These colors should never be used for KPI values or chart data encodings.

---

## 2.4 · Alert Severity Visibility System

The traffic and AQI datasets both contain severity gradations that require distinct visual encoding. The following rules govern severity visibility across all components and charts:

**Traffic Severity Encoding:**

| Severity Level | Data Condition | Color Token | Visual Behavior |
|---|---|---|---|
| CRITICAL | Congestion ≥ 90 · Capacity ≥ 95 · Incidents ≥ 3 | TRAFFIC_CRIMSON (#E5383B) | KPI value text + left-border accent on card |
| WARNING | Congestion 60–90 · Capacity 75–95 | TRAFFIC_AMBER (#FFBA08) | KPI value text + warning-state card background tint |
| SAFE | Congestion < 60 · Speed > 35 km/h | TRAFFIC_TEAL (#2EC4B6) | KPI value text only — no special card treatment |
| NEUTRAL | Non-severity metrics (pedestrian count, PT usage) | TRAFFIC_TEXT_PRIMARY (#F0F6FC) | Default white text — no severity encoding |

**AQI Severity Encoding:**

| AQI Category | PM2.5 Range (µg/m³) | Color Token | Background Opacity |
|---|---|---|---|
| Good | 0–30 | AQI_COLOR_GOOD (#00B050) | 8% tint on card background |
| Satisfactory | 31–60 | AQI_COLOR_SATISFACTORY (#92D050) | 8% tint |
| Moderate | 61–90 | AQI_COLOR_MODERATE (#FFFF00) | 8% tint |
| Poor | 91–120 | AQI_COLOR_POOR (#FF7C00) | 10% tint |
| Very Poor | 121–250 | AQI_COLOR_VERY_POOR (#FF0000) | 12% tint |
| Severe | > 250 | AQI_COLOR_SEVERE (#7030A0) | 15% tint + left-border accent |

**Saturation Governance:** Severity colors appear in KPI values, chart data encodings, and status badge elements. They never appear as full-coverage background fills — only as text color, thin left-border accents (3px), or low-opacity card background tints. This preserves legibility and prevents the dashboard from appearing to scream at the analyst.

---

# PART 3 — ENTERPRISE LAYOUT ARCHITECTURE

---

## 3.1 · Page Grid System

The dashboard uses a fluid column grid built on Streamlit's native `st.columns()`. The grid is not a fixed-pixel system — it is a ratio-based system that scales with the browser window while maintaining proportional relationships.

**Standard Page Layout (st.layout="wide"):**

```
┌─────────────────────────────────────────────────────────────────┐
│  FILTER STRIP                                          [Active] │  ← 48px height
├─────────────────────────────────────────────────────────────────┤
│  HERO SECTION — Page Title + Severity Badge                     │  ← 72–96px height
├─────────────────────────────────────────────────────────────────┤
│  KPI / METRIC STRIP — 4–5 cards horizontal                      │  ← 88px height
├─────────────────────────────────────────────────────────────────┤
│  SPACER                                                         │  ← 24px
├──────────────────────────────────────────┬──────────────────────┤
│  HERO CHART CONTAINER                    │  SECONDARY CHART     │
│  [ratio: 0.60]                           │  [ratio: 0.40]       │  ← 440–480px height
│  Title (16px / weight 600)               │  Title (13px / 500)  │
│  Chart                                   │  Chart               │
│  Caption                                 │  Caption             │
├──────────────────────────────────────────┴──────────────────────┤
│  SPACER                                                         │  ← 24px
├─────────────────────────────────────────────────────────────────┤
│  [COLLAPSIBLE] SECONDARY CHART OR INSIGHT PANEL                 │  ← Variable height
├─────────────────────────────────────────────────────────────────┤
│  [COLLAPSIBLE] "WHAT THIS MEANS" — insight_panel()              │  ← 120–200px expanded
├─────────────────────────────────────────────────────────────────┤
│  "INVESTIGATE FURTHER" — nav_card()                             │  ← 64px
└─────────────────────────────────────────────────────────────────┘
```

**Column Ratio Reference:**

| Page Layout Type | Column Split | Use Case |
|---|---|---|
| Hero-dominant split | `st.columns([3, 2])` | Primary hero + supporting chart |
| Equal comparison | `st.columns([1, 1])` | Side-by-side equivalents (P4: T-09 + T-10) |
| Single hero full-width | `st.columns([1])` | Scorecards, calendar heatmap (A-02), ridgelines |
| Wide hero + narrow sidebar | `st.columns([4, 1])` | Radar with area toggle panel (T-13) |
| Three supporting | `st.columns([1, 1, 1])` | KPI metric strip only — never for charts |

---

## 3.2 · Spacing Token Application

The spacing token system from `config/theme.py` governs all margins, padding, and gap values. No hardcoded pixel values appear in page modules or component HTML.

| Token | Value | Usage |
|---|---|---|
| `SPACING_XS` | 4px | Internal label gaps, badge padding |
| `SPACING_SM` | 8px | Icon-to-text gap, compact card internal margin |
| `SPACING_MD` | 16px | Card internal padding, between-chart captions |
| `SPACING_LG` | 24px | Between chart rows, section breaks |
| `SPACING_XL` | 40px | Hero section padding above/below, major section separators |
| `SPACING_2XL` | 64px | Between Investigation Zone and Context Zone |

**Implementation in Streamlit:** Spacing between elements is achieved through a combination of `st.write("")` spacers (for controlled empty lines), `st.markdown("<div style='margin-top:Npx'></div>", unsafe_allow_html=True)` for precise spacing, and the `SPACING_*` token values inserted into component HTML strings via f-string formatting.

---

## 3.3 · Responsive Layout Strategy

Streamlit does not offer native responsive CSS. The following adaptation strategy achieves responsive-like behavior through conditional column configurations based on viewport signals.

**Desktop (≥ 1280px): Full enterprise layout**
- All column splits as specified above
- Full KPI card row (4–5 cards)
- Hero + supporting split (3:2 or similar)
- Sidebar filter visible

**Laptop (1024–1280px): Condensed layout**
- Hero chart promoted to full-width where possible
- Supporting chart moves below hero (1:1 stacked) rather than side-by-side
- KPI cards reduce to 3 per visible row (remaining cards stack in second row)
- Implementation: `st.columns([1, 1])` instead of `st.columns([3, 2])`

**Tablet (768–1024px): Single-column critical path**
- All chart pairs stack vertically (single-column layout for charts)
- KPI strip collapses to 2-card visible + "show more" expander
- Parallel coordinates (T-02) drops to 3 axes (Congestion, Speed, Incidents)
- Sidebar collapses and moves to a top horizontal filter strip
- Implementation guidance: Detect via `st.session_state["viewport_width"]` if using custom JS injection, or default to conservative layout as the safe option

**Compact (< 768px): Essential mode**
- Full-width single column only
- Hero chart only on each page (supporting charts hidden behind expanders)
- Metric strip shows 2 primary KPIs only
- Advanced Lab not accessible (display "Visit on a larger screen" gate)

---

## 3.4 · Maximum Chart Density Per Viewport

To prevent visual overload, strict density limits apply per page render:

| Rule | Value |
|---|---|
| Maximum charts rendered without scroll | 2 (hero + 1 supporting) |
| Maximum charts total per page (including collapsible) | 4 |
| Maximum KPI cards in metric strip | 5 |
| Maximum KPI cards in full scorecard section (T-01, A-01) | 8 |
| Maximum overlapping traces in any single chart | 8 (T-03 stream graph limit) |
| Maximum radar polygon overlays simultaneously | 4 (enforced in T-13) |
| Maximum pairplot variables | 7 (A-15: T, Tm, SLP, H, VV, V, PM2.5) |

---

# PART 4 — ADVANCED TYPOGRAPHY SYSTEM

---

## 4.1 · Typography Hierarchy

The platform uses a 7-level type hierarchy. Each level has a specific semantic role. No level may be used for a different semantic purpose — doing so breaks the visual hierarchy and forces the analyst to re-learn importance cues on each page.

**Level 1 — Platform Title (app.py switcher)**

```css
font-family: 'Inter', 'Segoe UI', sans-serif;
font-size: 24px;
font-weight: 700;
letter-spacing: -0.02em;
color: TRAFFIC_TEXT_PRIMARY / AQI_TEXT_PRIMARY;
```
Used exclusively for the dashboard name in the app-level switcher bar. Appears once per session.

**Level 2 — Page Title (hero_section)**

```css
font-size: 20px;
font-weight: 600;
letter-spacing: -0.01em;
color: TRAFFIC_TEXT_PRIMARY;
line-height: 1.2;
```
Used in `hero_section()` for the page's analytical title (e.g., "Command Overview · Traffic Intelligence"). Appears once per page.

**Level 3 — Section Header (chart_container title — hero charts)**

```css
font-size: 16px;
font-weight: 600;
letter-spacing: 0;
color: TRAFFIC_TEXT_PRIMARY;
text-transform: uppercase;
letter-spacing: 0.05em;
```
Used for the title above hero charts. Uppercase + wider letter-spacing distinguishes section-level headers from inline labels. The uppercase treatment communicates "this is a named analytical module" rather than "this is a descriptive label."

**Level 4 — Chart Title (chart_container title — supporting charts)**

```css
font-size: 13px;
font-weight: 500;
letter-spacing: 0.03em;
color: TRAFFIC_TEXT_MUTED;
text-transform: uppercase;
```
Supporting charts use muted color + slightly smaller scale. This visual de-emphasis communicates "supporting context" without hiding the title entirely.

**Level 5 — KPI Value**

```css
font-size: 32px (normal) / 24px (compact) / 40px (large);
font-weight: 700;
font-variant-numeric: tabular-nums;  /* critical for aligned numeric comparison */
letter-spacing: -0.02em;
color: [severity-token] OR TRAFFIC_TEXT_PRIMARY;
font-family: 'JetBrains Mono', 'Fira Code', monospace; /* for numeric KPIs */
```
KPI values use monospace to ensure digit columns align when multiple KPI cards are viewed together. The tabular-nums feature is essential for scan-reading metric strips. Font weight 700 ensures values pop against the dark surface.

**Level 6 — Body / Annotation**

```css
font-size: 13px;
font-weight: 400;
line-height: 1.6;
color: TRAFFIC_TEXT_MUTED;
```
Used for insight panel body text, chart captions, annotation text in Plotly charts, sidebar explanatory text. Line-height 1.6 ensures readability of multi-line interpretation text.

**Level 7 — Caption / Label**

```css
font-size: 11px;
font-weight: 400;
letter-spacing: 0.02em;
color: TRAFFIC_TEXT_MUTED;
opacity: 0.8;
```
Used for chart axis tick labels, legend text, filter widget labels, metadata (data range shown, last updated). Never use for anything the analyst needs to read during primary analysis.

---

## 4.2 · KPI Typography Behavior

KPI values require special typographic handling because they communicate severity through both color and scale:

**Normal state:** 32px monospace, weight 700, color TRAFFIC_TEXT_PRIMARY
**Warning state:** 32px monospace, weight 700, color TRAFFIC_AMBER, optional subtle pulsing animation (see Part 13)
**Critical state:** 36px monospace, weight 800, color TRAFFIC_CRIMSON — the size increase to 36px adds visual urgency beyond color alone
**Safe/positive state:** 32px monospace, weight 700, color TRAFFIC_TEAL

**Delta indicators (trend arrows):**
- Positive delta: ▲ prefix + TRAFFIC_TEAL + 12px font-size
- Negative delta (bad): ▼ prefix + TRAFFIC_CRIMSON + 12px font-size  
- Negative delta (good — e.g., PM2.5 decreased): ▼ prefix + TRAFFIC_TEAL — the semantic is determined by `delta_positive` parameter in `kpi_card()`, not by direction alone

**Truncation rules:**
- KPI values are never truncated — the number format is adjusted instead (e.g., "1,234,567" becomes "1.2M")
- Chart titles truncate at 48 characters with ellipsis at desktop, 36 characters at tablet
- Caption text truncates to 2 lines maximum (CSS: `-webkit-line-clamp: 2`) unless inside an expanded insight panel

---

## 4.3 · Plotly Internal Typography

Plotly charts have their own internal typography system managed through `BASE_LAYOUT` in `config/chart_defaults.py`. All Plotly text elements must respect the platform's type hierarchy:

```python
BASE_LAYOUT = {
    "font": {
        "family": "'Inter', 'Segoe UI', sans-serif",
        "size": 12,
        "color": "#8B949E"  # TRAFFIC_TEXT_MUTED — default for axis labels
    },
    "title": {
        "font": {"size": 14, "color": "#F0F6FC", "weight": 600}
        # Note: chart titles are rendered outside Plotly via chart_container — 
        # the fig.update_layout(title=...) is NOT used. 
        # chart_container() renders the title via st.markdown, not inside the figure.
    },
    "hoverlabel": {
        "font": {"family": "'JetBrains Mono', monospace", "size": 12},
        "bgcolor": "#161B22",
        "bordercolor": "#30363D"
    }
}
```

**Why chart titles live outside Plotly:** Plotly's internal title system offers poor vertical spacing control and inconsistent cross-chart behavior. By rendering all chart titles via `chart_container()` using `st.markdown()`, we gain: pixel-perfect spacing, consistent type scale regardless of chart type, the ability to add badges or severity indicators next to the title, and alignment with the platform's CSS type scale rather than Plotly's internal font system.

---

# PART 5 — ENTERPRISE COLOR SYSTEM

---

## 5.1 · Color System Architecture

The color system operates on three layers:

**Layer 1 — Surface Architecture (backgrounds, containers, borders)**
These colors define the spatial depth of the platform. They never encode data.

```python
# Traffic Dashboard surfaces
TRAFFIC_BG           = "#0D1117"    # Page background — the deepest layer
TRAFFIC_SURFACE_1    = "#161B22"    # Primary cards, chart containers
TRAFFIC_SURFACE_2    = "#1C2128"    # Hover state backgrounds, nested containers
TRAFFIC_SURFACE_3    = "#21262D"    # Input backgrounds, collapsed section headers
TRAFFIC_BORDER_1     = "#30363D"    # Visible borders — card edges
TRAFFIC_BORDER_2     = "#21262D"    # Subtle borders — section separators

# AQI Dashboard surfaces
AQI_BG           = "#0A0F1E"        # Deep navy page background
AQI_SURFACE_1    = "#111827"        # Primary cards
AQI_SURFACE_2    = "#1A2333"        # Hover state backgrounds
AQI_SURFACE_3    = "#1F2D42"        # Input backgrounds
AQI_BORDER_1     = "#1F2937"        # Visible borders
AQI_BORDER_2     = "#162032"        # Subtle section separators
```

**Layer 2 — Identity Accent Colors (operational brand tones)**
These colors establish the dashboard's visual personality. They appear in: hero section decorative elements, active tab indicators, focus-state borders, severity badge backgrounds, and as the dominant hue in multi-series charts.

```python
# Traffic: Crimson operational identity
TRAFFIC_CRIMSON      = "#E5383B"    # Primary identity — critical severity, accent
TRAFFIC_AMBER        = "#FFBA08"    # Warning severity — alert state
TRAFFIC_TEAL         = "#2EC4B6"    # Positive/relief — low severity, safe state
TRAFFIC_SLATE        = "#58A6FF"    # Neutral accent — date ranges, info badges

# AQI: Atmospheric navy identity  
AQI_NAVY             = "#1E3A5F"    # Primary identity — atmospheric depth
AQI_CYAN             = "#38BDF8"    # Highlight — wind/relief indicators
AQI_STEEL            = "#64748B"    # Neutral metric text
```

**Layer 3 — Data Encoding Colors (for charts only)**
These colors encode data. They never appear in UI chrome. They are governed by strict allocation rules to prevent cross-chart confusion.

```python
# Traffic: Area palette (8 areas = 8 colors)
# These appear in T-02, T-03, T-04, T-05, T-09, T-11, T-13, T-15
TRAFFIC_AREA_COLORS = [
    "#58A6FF",  # Indiranagar — steel blue
    "#E5383B",  # Koramangala — crimson
    "#2EC4B6",  # Whitefield — teal
    "#FFBA08",  # Electronic City — amber
    "#8B5CF6",  # Marathahalli — violet
    "#10B981",  # Silk Board — emerald
    "#F97316",  # MG Road — tangerine
    "#EC4899",  # Brigade Road — rose
]

# AQI: PM2.5 severity gradient
AQI_SCALE_COLORS = ["#00B050", "#92D050", "#FFFF00", "#FF7C00", "#FF0000", "#7030A0"]
```

---

## 5.2 · Color Governance Rules

**Rule 1: One Encoding Per Color**
Each color in the data encoding palette encodes exactly one dimension. TRAFFIC_CRIMSON encodes: (a) critical severity in KPIs, (b) Koramangala area in multi-area charts. It never encodes anything else — no "emphasis for the analyst's attention," no decorative use on chart backgrounds.

**Rule 2: Saturation Ceiling**
No data encoding color should appear at 100% saturation on dark backgrounds unless it represents a critical alert state. TRAFFIC_AMBER (#FFBA08) at full saturation on a dark background creates strong visual tension — appropriate for a warning-state KPI, not appropriate for a chart bar in a grouped bar chart that represents neutral data.

For neutral data series in grouped bars (T-10, A-09, A-10), use area colors at 70–80% opacity: `rgba(88, 166, 255, 0.75)` instead of `#58A6FF`. This reduces saturation noise while preserving color identity.

**Rule 3: The 3-Color Maximum for Single Charts**
Any single chart may use a maximum of 3 distinct categorical colors without a legend. At 4+ colors, a legend is required. At 8 colors (T-02, T-03), hover-isolation behavior becomes mandatory (all traces dim to 15% opacity on hover except the focused trace).

**Rule 4: AQI Category Colors Are Fixed**
The 6 AQI category colors (Good through Severe) are WHO/NAAQS-standard. They are never changed for aesthetic reasons. An analyst who understands the AQI color scale should be able to decode any AQI chart in this platform without a legend. Consistency is critical.

**Rule 5: Gray Is Muted, Not Neutral**
The muted text colors (`TRAFFIC_TEXT_MUTED`, `AQI_TEXT_MUTED`) are gray. They communicate "this is supporting information." Never use gray as a data encoding color — it reads as "this data is less important" rather than as a neutral category. Use a desaturated hue instead.

---

## 5.3 · The Surface Layering System

The dark theme achieves depth through layered surface tones, not through shadows (shadows on dark backgrounds create visual artifacts and reduce clarity):

```
Depth Layer 0 — Page Background:     #0D1117 (Traffic) / #0A0F1E (AQI)
Depth Layer 1 — Primary Card:        #161B22 / #111827
Depth Layer 2 — Nested Content:      #1C2128 / #1A2333
Depth Layer 3 — Input/Control:       #21262D / #1F2D42
Depth Layer 4 — Hover State:         #2D333B / #243344
```

Charts are rendered on SURFACE_1 backgrounds. Filter panel sits at SURFACE_3 (input level). Page background is BG (deepest level). This creates a natural spatial hierarchy where interactive elements appear "elevated" relative to static content.

**Border Governance:** Use `BORDER_1` only for cards that contain critical operational content. Use `BORDER_2` (subtler, near-invisible) for section separators and chart internal borders. Charts should have no explicit container border unless the chart is a KPI scorecard card — the chart's own axis and content create implicit boundaries.

---

# PART 6 — KPI + METRIC UX SYSTEM

---

## 6.1 · KPI Architecture Philosophy

The Bangalore traffic dataset contains 8,936 rows across 16 roads and 8 areas, spanning 32 months. The AQI dataset contains 1,095 daily readings across 3 years. Neither analyst wants to read these rows. They want the answers:

- **Traffic:** How bad is congestion right now (given the filtered view)? Which areas are worst? What's the incident picture?
- **AQI:** What is the chronic pollution burden? How many Severe days occurred? When was the worst period?

The KPI scorecard (T-01 for Traffic, A-01 for AQI) must answer these questions in the Command Zone — before the analyst scrolls to any chart.

---

## 6.2 · T-01 · Saturation Command Scorecard — UX Specification

**Layout:** Full-width card grid — 4 primary KPI cards in top row, 4 secondary KPI cards in bottom row (or 4+4 in a 2-row metric strip depending on viewport).

**Primary KPI Cards (top row — maximum operational urgency):**

| KPI | Derived From | Severity Logic | Display Format |
|---|---|---|---|
| System Congestion Index | Mean `Congestion_Level` across all filtered rows | ≥90: CRITICAL · 60–90: WARNING · <60: SAFE | "87.3" (one decimal) |
| Capacity Saturation Rate | % roads with `Road_Capacity_Utilization ≥ 99.5` | ≥50%: CRITICAL · 25–50%: WARNING | "64%" |
| Active Incidents | Sum of `Incident_Reports` over filtered date range | ≥ 500: CRITICAL · 200–500: WARNING | "1,247" |
| Average Speed | Mean `Average_Speed` across filtered rows | ≤ 20 km/h: CRITICAL · 20–30: WARNING | "26.4 km/h" |

**Secondary KPI Cards (bottom row — supporting operational context):**

| KPI | Derived From | Severity | Display |
|---|---|---|---|
| Pedestrian & Cyclist Exposure | Mean `Pedestrian_and_Cyclist_Count` | Neutral (higher = more exposure) | "134 avg" |
| Public Transport Usage | Mean `Public_Transport_Usage` | Neutral | "52.3%" |
| Signal Compliance Rate | Mean `Traffic_Signal_Compliance` | <70%: WARNING | "78.1%" |
| Environmental Impact Index | Mean `Environmental_Impact` | >140: WARNING | "128.4" |

**Gauge Ring Behavior (SVG-based in kpi_card component):**
The gauge ring renders only on primary KPI cards. It fills clockwise from 0 to the KPI's percentage value. Fill color matches the severity state: crimson for CRITICAL, amber for WARNING, teal for SAFE.

Implementation in `kpi_card.py`:
```python
# SVG gauge ring — 32px radius, 4px stroke width
# Circumference = 2 * π * 32 ≈ 201px
# Fill amount = (gauge_percent / 100) * 201 via stroke-dasharray
svg_gauge = f"""
<svg width="80" height="80" viewBox="0 0 80 80">
  <circle cx="40" cy="40" r="32" fill="none" 
          stroke="{TRAFFIC_BORDER_1}" stroke-width="4"/>
  <circle cx="40" cy="40" r="32" fill="none"
          stroke="{severity_color}" stroke-width="4"
          stroke-dasharray="{fill_amount} 201"
          stroke-linecap="round"
          transform="rotate(-90 40 40)"
          style="transition: stroke-dasharray 0.6s ease-out;"/>
</svg>
"""
```

---

## 6.3 · A-01 · Chronic Crisis Scorecard — UX Specification

AQI KPIs communicate cumulative atmospheric burden, not instantaneous operational stress. The design reflects this difference.

**Primary KPI Cards:**

| KPI | Derived From | Display |
|---|---|---|
| Chronic Crisis Rate | % days with PM2.5 > 120 (Very Poor + Severe) | "68.4% of days" — color: AQI_COLOR_VERY_POOR |
| Peak Pollution Index | Maximum PM2.5 in filtered range | "389.2 µg/m³" — color: AQI_COLOR_SEVERE |
| Annual Mean PM2.5 | Mean PM2.5 over filtered period | "142.7 µg/m³" — WHO guideline annotation below: "WHO: 5 µg/m³" |
| Severe Days Count | Count of days PM2.5 > 250 | "124 days" — color: AQI_COLOR_SEVERE |

The WHO guideline annotation below the Annual Mean PM2.5 card is a permanent micro-annotation: `"WHO Annual Guideline: 5 µg/m³"` in Level 7 caption type, TRAFFIC_TEXT_MUTED color. This contextualizes the value without a tooltip — the gap between 142.7 and 5.0 is the analytical story of this entire dashboard.

---

## 6.4 · Metric Strip Hover Behavior

Each KPI card in the metric strip supports hover interaction:

- **Hover state:** SURFACE_2 background transition (150ms ease), BORDER_1 border brightens from #30363D to #484F58
- **Hover tooltip:** Shows the metric definition, data range used, and N (row count) for the filtered dataset
- **No click behavior on metric strip cards** — they are read-only summary elements, not drilldown triggers

Implementation in `metric_strip.py`:
```python
card_hover_style = f"""
<style>
.metric-card:hover {{
    background-color: {TRAFFIC_SURFACE_2};
    border-color: #484F58;
    transition: all 0.15s ease;
    cursor: default;
}}
</style>
"""
```

---

# PART 7 — CHART UX + VISUALIZATION REFINEMENT

---

## 7.1 · Universal Chart Standards

These standards apply to all 30 charts across both dashboards before any chart-specific guidance.

**Axis Simplification Protocol:**
- Remove all gridlines from Y-axis by default. Add a single, extremely subtle horizontal grid at `gridcolor="#21262D"` (nearly matches background) for charts where value reading requires vertical reference (bar charts, scatter plots).
- Remove all X-axis gridlines universally. Temporal x-axes use tick marks only.
- Zero line: render only when negative values are possible (T-07 diverging bar, delta indicators). Otherwise `zeroline=False`.
- Axis titles: Use sparingly. If the chart title already communicates the axis content ("Congestion Level Distribution by Day of Week" implies the Y-axis), suppress `yaxis_title`. Only include axis titles when the unit is critical (e.g., "PM2.5 µg/m³" — the unit matters analytically).

**Tooltip Design Standard:**
All Plotly tooltips use the `hoverlabel` standard from `BASE_LAYOUT`:
- Background: `TRAFFIC_SURFACE_1` (#161B22) — dark but distinct from chart background
- Border: `TRAFFIC_BORDER_1` (#30363D)
- Font: JetBrains Mono 12px for numeric values, Inter 12px for label text
- Number formatting: via `utils/formatters.py` — never raw Python float representation

```python
# utils/formatters.py — standard number formats
def fmt_congestion(val): return f"{val:.1f}"
def fmt_speed(val): return f"{val:.1f} km/h"
def fmt_pm25(val): return f"{val:.1f} µg/m³"
def fmt_pct(val): return f"{val:.1f}%"
def fmt_count(val): return f"{int(val):,}"
```

**Legend Governance:**
- Legends render only when 3+ series are present in a single chart
- Legend position: bottom-center (`legend=dict(orientation="h", yanchor="bottom", y=-0.15)`)
- Legend font: Level 7 caption scale
- Legend items are never repeated across the page — if 3 charts on the same page share the same series encoding (e.g., area colors in T-03, T-04, T-09), only the hero chart renders the legend; supporting charts suppress it with a footnote: "See legend above"

---

## 7.2 · T-03 · Stream Graph — Chart-Specific UX

The 32-month congestion stream graph is the temporal hero chart for the Traffic Temporal Intelligence page. 8 area stacked streams across 32 months.

**Readability safeguards:**
- Area label annotation appears at the rightmost data point of each stream, using `add_annotation` in `utils/annotations.py` — not a legend. Label font: Level 7 (11px), color: matching area color at 90% opacity
- Streams are ordered by mean congestion contribution: Koramangala (highest) stacked first from baseline, Brigade Road (lowest) stacked last at top
- X-axis: monthly tick marks, labeled every 6 months (format: "Jan 2022", "Jul 2022", etc.)
- Hover: Hovering any stream highlights that stream to full opacity; all others reduce to 20% opacity; tooltip shows: Area Name, Month, Mean Congestion, Contribution %

**Animation on initial load:**
Streams reveal from left to right over 800ms using Plotly's `frame` animation. Each frame adds one month of data. Animation plays once on page load, does not loop. If the analyst has applied a filter, animation is suppressed (instant render).

---

## 7.3 · T-05 · Quadrant Scatter — Chart-Specific UX

16 road bubbles plotted on Congestion Level (Y) vs. Road Capacity Utilization (X). Bubble size encodes `flow_instability_index`.

**Quadrant annotation system:**
Four quadrants are labeled using `QuadrantLabel()` from `utils/annotations.py`:
- Top-right: "CRITICAL OVERLOAD" — font color TRAFFIC_CRIMSON, 11px
- Top-left: "CONSTRAINED FLOW" — TRAFFIC_AMBER
- Bottom-right: "CAPACITY MARGIN" — TRAFFIC_TEAL
- Bottom-left: "OPERATIONAL BASELINE" — TRAFFIC_TEXT_MUTED

**Drilldown interaction:**
- Click on a road bubble → `streamlit_plotly_events` captures click → `session_state["traffic_selected_road"]` updates → T-06 treemap highlights the clicked road's area → T-07 diverging bar scrolls to highlight the clicked road → Road Detail Panel renders below the chart
- Selected road bubble: border radius increases (Plotly `marker.line.width` from 0 to 2), marker opacity increases to 1.0
- Unselected bubbles when one is selected: opacity reduces to 0.35

**Road Detail Panel (below T-05, conditional render):**
When `session_state["traffic_selected_road"]` is set, `detail_panel()` renders with:
- Road name as panel title
- Metric row: Mean Congestion | Mean Speed | Capacity Util | Total Incidents
- "at_max_capacity" badge if Road_Capacity_Utilization ≥ 99.5 for >80% of rows
- Sparkline (small 200×60px chart) showing congestion over time for that road

---

## 7.4 · T-11 · Congestion Distribution Ridgeline — Chart-Specific UX

16 KDE distributions stacked vertically with vertical offset, Altair implementation, one distribution per road.

**Readability Protocol:**
- Distributions are sorted by median congestion, high-to-low (top distribution = most congested road)
- Each distribution is filled with the road's area color at 40% opacity; stroke at 100% opacity
- Y-axis labels: road names, right-aligned, font size 10px — compact to accommodate 16 labels
- X-axis: 0–100 congestion scale, tick marks at 0, 25, 50, 75, 100
- Peak annotation: A vertical dashed line at the distribution peak, labeled with the peak value. Only for the top 3 and bottom 2 distributions (reducing annotation clutter on the middle roads)

**Hover behavior (Altair):**
Use Altair's `selection_single()` with `on='mouseover'`. Hovering a distribution: fills with 70% opacity (from 40%), all other distributions reduce to 20% opacity. Tooltip shows: Road name, Area, Median congestion, 90th percentile congestion.

**Key insight annotation:**
A persistent annotation renders below the chart: `"Roads in Critical Overload quadrant show strongly right-skewed distributions. Roads near Operational Baseline show tight, left-concentrated distributions."` — Level 7 caption, TRAFFIC_TEXT_MUTED. This is the chart's `caption` parameter in `chart_container()`.

---

## 7.5 · T-13 · Compound Stress Radar — Chart-Specific UX

Multi-polygon radar in Advanced Lab. Maximum 4 overlays. 6 normalized axes.

**Axis labeling:**
Axis labels render at 110% of the radar's outer radius, using `go.Scatterpolar` trace annotations:
- Axis label text: full metric name (e.g., "Congestion Level", "Incident Rate")
- Value annotations at radial positions: 0, 50, 100 marks on each axis, rendered as faint dotted arc lines
- Axis labels at 12px Level 7 scale — compact but readable at the chart's standard 440px height

**Polygon interaction:**
- Focus area (from radio button in sidebar column): renders at `opacity=0.8`, `line.width=2`, fill visible
- Non-focus visible areas: render at `opacity=0.25`, `line.width=1`, fill at `opacity=0.1`
- Hover a polygon: raises it to `opacity=0.9` temporarily; tooltip shows all 6 normalized scores

**The area toggle panel (sidebar-style column at right of chart):**
Uses `st.columns([4, 1])` split. The right column contains:
- 8 checkboxes (one per area), styled as compact toggles
- "Top 3 Stress" and "Baseline 3" quick-select buttons
- "Clear All" link-style button
- A compact severity ranking list: areas listed in descending order of composite stress score

---

## 7.6 · A-02 · 3-Year Calendar Heatmap — Chart-Specific UX

1,095 individual day cells arranged in a 3-year calendar grid. Cells colored by AQI category.

**Grid layout:**
- 3 rows (years: 2021, 2022, 2023) × 53 columns (weeks)
- Each cell: approximately 12×12px at standard viewport
- Weekday labels: Mon–Sun on left Y-axis, 7px font (smallest readable)
- Month labels: above each month start column, 10px font

**Color encoding:**
Each cell uses the AQI category color scale. Good days are visually rare (green islands). The persistent red-to-purple pattern in winter months (November–February) communicates chronic crisis without any annotation — the pattern is the insight.

**Critical contextual annotation:**
A thin horizontal band annotation highlights the WHO daily PM2.5 guideline (15 µg/m³). Since most days exceed this threshold, the annotation renders as a footnote below the chart: `"All colored cells except 'Good' exceed WHO daily PM2.5 guideline of 15 µg/m³."` — permanent, Level 7 caption.

**Click interaction:**
Clicking a calendar cell → `session_state["aqi_selected_date"]` sets to that date → Month Detail Panel renders below the chart with that date's full meteorological readings.

**Fullscreen mode:**
At standard width, individual day cells may be small. The fullscreen toggle expands the chart to full page width, cells enlarge to approximately 18×18px. Fullscreen is recommended for detailed day-level inspection.

---

## 7.7 · A-15 · Full Meteorological Pairplot — Chart-Specific UX

6×6 Altair scatter matrix. 7 variables: T, Tm, SLP, H, VV, V, PM2.5.

**Diagonal panel treatment:**
Diagonal panels render KDE-approximated histograms (binned, not true KDE for performance). Fill color matches the AQI category distribution for that variable. This means the diagonal histograms encode the shape of the data distribution — the heavily right-skewed PM2.5 diagonal panel communicates the chronic high-burden distribution immediately.

**Off-diagonal panel behavior:**
- Default: all points rendered at 30% opacity, colored by AQI category (6-color scale)
- On AQI category hover/click: points from that category raise to 80% opacity; others reduce to 10%
- This Altair selection behavior is implemented with `alt.selection_point(fields=['aqi_category'], bind='legend')`

**Size calibration:**
At standard dashboard width (st.layout="wide"), the pairplot renders at 800×800px total. Individual panels are approximately 115×115px — the minimum size where scatter point patterns remain interpretable. Fullscreen expands to 1100×1100px.

**Variable ordering:**
Variables are ordered by data type: meteorological drivers first (SLP → T → Tm → H → VV → V), then outcome last (PM2.5). This ensures all meteorological correlations with PM2.5 read from left-to-right in the final column, and all correlations read bottom-up in the final row — following the analyst's natural hypothesis direction.

---

## 7.8 · A-06 · Atmospheric Stagnation Hexbin — Chart-Specific UX

VV (visibility/atmospheric dispersion proxy) vs PM2.5 density hexbin chart. 1,095 points binned.

**Hexbin color scale:**
Use a single-hue scale from SURFACE_1 (low density) to AQI_COLOR_SEVERE (high density). This keeps the chart visually cohesive with the platform's AQI severity identity. Avoid multi-hue rainbow scales — they introduce false categorical boundaries in a continuous density distribution.

**Critical insight annotation:**
The bottom-left corner of the hexbin contains the highest PM2.5 + lowest VV concentration — the "stagnation trap" zone. A rectangular annotation box marks this zone: dashed border in TRAFFIC_AMBER, label: "STAGNATION TRAP — Low Dispersion × High PM2.5". This annotation uses `add_annotation_callout()` from `utils/annotations.py`.

**Quadrant reference lines:**
Horizontal line at PM2.5 = 120 µg/m³ (Very Poor threshold) and vertical line at VV = 1.0 (low visibility threshold), both via `add_quadrant_lines()` from `utils/plotly_helpers.py`. Line color: TRAFFIC_BORDER_1 at 60% opacity — present but not dominant.

---

# PART 8 — INTERACTION DESIGN SYSTEM

---

## 8.1 · Hover State Specification

Hover states communicate interactability without requiring the analyst to attempt a click. Every interactive element has a defined hover treatment:

**Chart data elements (Plotly):**

| Element Type | Default State | Hover State | Transition |
|---|---|---|---|
| Scatter points | `opacity=0.75`, `marker.line.width=0` | `opacity=1.0`, `marker.line.width=1.5` | Plotly native (instant) |
| Bar chart bars | `opacity=0.85` | `opacity=1.0`, slight brightness increase via `marker.color` | Plotly native (instant) |
| Stream area | `opacity=0.6` | `opacity=0.9` for hovered stream, all others → 0.2 | Plotly native |
| Radar polygon | Per focus rules above | `opacity=0.9` | 150ms CSS ease |
| Calendar cell | `opacity=0.85` | `opacity=1.0`, `cursor:pointer` | Plotly native |
| Hexbin cell | `opacity=0.7` | `opacity=1.0` | Plotly native |

**Streamlit UI elements:**

| Element | Default | Hover | Transition |
|---|---|---|---|
| KPI card | `background: SURFACE_1`, `border: BORDER_1` | `background: SURFACE_2`, `border: #484F58` | 150ms ease |
| Nav card | `background: SURFACE_1`, `border: BORDER_2` | `background: SURFACE_2`, `border: TRAFFIC_CRIMSON at 50%` | 150ms ease |
| Collapsible section header | `background: SURFACE_3` | `background: SURFACE_2`, `cursor: pointer` | 100ms ease |
| Tab (active) | `border-bottom: 2px solid TRAFFIC_CRIMSON` | No change — already active | — |
| Tab (inactive) | `color: TEXT_MUTED` | `color: TEXT_PRIMARY`, `border-bottom: 1px solid BORDER_1` | 100ms ease |
| Filter widget | Streamlit default | Streamlit default — do not override widget hover | — |

---

## 8.2 · Click States and Drilldown Transitions

**Click state feedback:**
The analyst must receive immediate visual feedback when a click is registered — before the Streamlit re-run completes (which may take 300–800ms depending on cache state). This is achieved through a CSS `:active` pseudo-class pulse:

```css
.chart-drilldown-target:active {
    transform: scale(0.98);
    transition: transform 0.05s ease;
}
```

This micro-scale reduction on click gives immediate tactile feedback without waiting for the Streamlit re-run.

**Post-drilldown visual state:**
After drilldown completes (re-run finishes):
- The clicked element remains visually distinguished: selected scatter point maintains `marker.line.width=2, opacity=1.0`
- All non-selected elements in the same chart reduce opacity to 0.35
- A "Selection active" indicator badge renders near the chart title: small pill badge reading "Showing: [selection name]" in SURFACE_3 background, TRAFFIC_AMBER border, 10px font
- A "× Clear" button appears inline next to the badge — clicking it clears the drilldown state key in session_state and triggers a re-run

---

## 8.3 · Cross-Chart Highlighting Protocol

When `session_state["traffic_selected_area"]` is set (from clicking a line in T-02 or a cell in other area-indexed charts), every chart that uses area color encoding responds:

- Charts that **contain** the selected area: render that area at full opacity, all others at 20% opacity
- Charts that **do not** use area encoding (T-08 incident cliff, T-10 PT decoupling): no change — they are immune to the area selection
- The filter strip: renders an additional "Focus: [Area Name]" badge next to the Reset button

This is implemented at the data level (page module passes filtered/highlighted data to charts) rather than at the Plotly level (no JavaScript callbacks). The page module checks `session_state["traffic_selected_area"]`:

```python
selected_area = st.session_state.get("traffic_selected_area")
if selected_area:
    # For charts with multi-area traces:
    # primary_data = filtered to selected_area only → passed to chart at full weight
    # secondary_data = all other areas → passed with opacity_override=0.2
```

---

## 8.4 · Fullscreen Interaction Pattern

Fullscreen-eligible charts: T-02 (Parallel Coordinates), T-13 (Radar), A-02 (Calendar Heatmap), A-15 (Pairplot).

**Entering fullscreen:**
1. Analyst clicks the ⊞ icon rendered by `chart_container(fullscreen_key="t13_radar")`
2. `session_state["t13_radar_fullscreen"] = True` is set
3. Streamlit re-run triggers
4. Page module detects fullscreen state:
   ```python
   if st.session_state.get("t13_radar_fullscreen"):
       # Render ONLY the fullscreen chart — all other page content is hidden via st.empty()
       st.columns([1])[0].write(chart_container(fig, fullscreen_mode=True))
   ```
5. Fullscreen chart renders at 100% viewport width, 85% viewport height (CSS: `height: 85vh`)
6. A fixed "← Collapse" button renders in the top-left corner of the fullscreen container

**Exiting fullscreen:**
Clicking "← Collapse" → `session_state["t13_radar_fullscreen"] = False` → re-run → normal layout restores.

The transition between normal and fullscreen uses a 200ms CSS opacity fade: the outgoing layout fades to opacity 0, the fullscreen container fades in from opacity 0. This prevents the jarring layout jump that a direct render swap creates.

---

## 8.5 · Interaction Anti-Patterns to Prevent

| Anti-Pattern | Problem | Prevention |
|---|---|---|
| Click fires but nothing visually changes for 800ms | Analyst double-clicks thinking the first click failed | CSS `:active` pulse gives immediate feedback |
| Drilldown selection has no visible "exit" path | Analyst cannot clear the selection without refreshing the page | "× Clear" badge always present when drilldown state is active |
| Multiple selection states active simultaneously | T-05 road selected + T-02 area selected simultaneously creates contradictory chart states | Selection hierarchy enforced: road selection clears area selection; area selection does not clear road selection |
| Filter interaction re-renders all charts including off-screen ones | Visible lag on filter change | Only charts in the current active tab are rendered; other tab content is not in the DOM |
| Hover tooltip appears outside the viewport on edge charts | Tooltip is not readable | All Plotly hover labels use `hovermode="closest"` and `hoverlabel.namelength=-1` to prevent clipping |

---

# PART 9 — DASHBOARD STORYTELLING + NAVIGATION UX

---

## 9.1 · Analytical Storytelling Philosophy

Each of the 12 pages (6 per dashboard) is a **chapter in an analytical investigation.** The pages are not independently useful — they are progressively deeper examinations of the same underlying questions.

**Traffic Dashboard Analytical Arc:**
```
P1 · Command Overview:     "How bad is the overall congestion crisis?"
P2 · Temporal Intelligence: "When does it happen — patterns across time?"
P3 · Spatial Operations:    "Where does it happen — which roads and areas?"
P4 · Threshold Analytics:   "At what point does congestion become system failure?"
P5 · Hidden Patterns:       "What distributional patterns explain the crisis?"
P6 · Advanced Lab:          "Multi-dimensional profiling of every area and road"
```

**AQI Dashboard Analytical Arc:**
```
P1 · Crisis Overview:         "How severe and persistent is the pollution burden?"
P2 · Temporal Patterns:       "When is it worst — calendar and monthly patterns?"
P3 · Atmospheric Intelligence:"What atmospheric conditions trap pollution?"
P4 · Weather Relationships:   "Which meteorological drivers amplify pollution?"
P5 · Hidden Patterns:         "Statistical structure of pollution variability"
P6 · Advanced Lab:            "Full meteorological co-factor analysis"
```

Each page knows its place in the arc. The hero section subtitle communicates this: `"P3 of 6 · Spatial Investigation Layer"`. Analysts are never uncertain about where they are in the investigation.

---

## 9.2 · Page-Level Attention Path Design

For each page, the analyst's eye path is designed to deliver insight in this sequence:

**Sequence 1: Status → 2: Pattern → 3: Interpretation → 4: Next Step**

**P1 (Command Overview) eye path:**
1. Hero section: Dashboard name + page title (anchors context)
2. Metric strip: Severity-colored KPIs deliver the top-line answer in < 3 seconds
3. Hero chart (T-01 scorecard with gauges): Validates and elaborates the metric strip numbers
4. Supporting chart (T-08 incident cliff): Adds context to the incident KPI — the step function reveals threshold effects
5. Insight panel (collapsed by default): "What This Means" — quantifies the crisis
6. Nav card: "Investigate when this happens → Temporal Intelligence"

**P3 (Spatial Operations) eye path:**
1. Hero section: "Spatial Operations · Road-Level Intelligence"
2. Metric strip: Worst-performing area badge + overall capacity metric
3. Hero chart (T-05 Quadrant Scatter): Immediately reveals the critical-overload vs operational-baseline road distribution — the pattern is visible in < 5 seconds
4. Below: T-06 treemap in left column (area-level aggregation) + T-07 diverging bar in right column (active mobility penalty)
5. If road selected via T-05 click: Road Detail Panel renders between T-05 and T-06/T-07
6. Insight panel: "Critical Overload Roads: N roads with Congestion > 90 and Capacity > 95%"
7. Nav card: "Examine congestion threshold effects → Threshold Analytics"

---

## 9.3 · Navigation Flow Architecture

**Primary Navigation: Tab Bar**
The 6-tab navigation bar is the primary navigation instrument. It renders above all page content, below the filter strip. Tab labels use abbreviated but explicit names:

```
Traffic Dashboard tabs:
[01 · Overview] [02 · Temporal] [03 · Spatial] [04 · Threshold] [05 · Patterns] [06 · Lab ⚗]

AQI Dashboard tabs:
[01 · Crisis] [02 · Calendar] [03 · Atmosphere] [04 · Weather] [05 · Patterns] [06 · Lab ⚗]
```

**Active tab indicator:**
- Active tab: `border-bottom: 2px solid TRAFFIC_CRIMSON`, font-weight 600, `color: TEXT_PRIMARY`
- Inactive tabs: no border, font-weight 400, `color: TEXT_MUTED`
- Lab tab (Tab 06): distinct treatment — subtle ⚗ icon prefix, slightly muted background (`SURFACE_2` instead of transparent background of other tabs), communicates "this is a different kind of content"

**Secondary Navigation: "Investigate Further" Nav Cards**
Nav cards appear at the bottom of every page except the Advanced Lab. They provide a single recommended next-step destination:

```python
nav_card(
    label="INVESTIGATE FURTHER",
    destination_title="Temporal Intelligence",
    destination_description="Examine the 32-month congestion trend and weekly velocity patterns",
    tab_index=1,   # Tab 02
    dashboard="traffic"
)
```

Nav card styling:
- Full-width card, `SURFACE_1` background, `BORDER_2` border
- Arrow icon (→) on right side, colored with dashboard identity accent
- Hover: border brightens to BORDER_1, background to SURFACE_2
- Click: updates `session_state["traffic_active_tab"]` to target tab index → triggers re-run → correct page renders

**Tertiary Navigation: Breadcrumb in Advanced Lab**
The Advanced Lab page is the only page with a breadcrumb. Because it requires a gate pass, users may forget how they got there. The breadcrumb renders as:
```
← Return to Dashboard Overview   [P1 · Command Overview]
```
This renders as a plain link-style button: `color: TRAFFIC_SLATE`, `font-size: 13px`, `cursor: pointer`. Clicking returns to Tab 01 and clears the lab gate state.

---

## 9.4 · The Lab Gate UX

The Advanced Lab gate is a deliberate friction point — it communicates "this section has higher cognitive load." The gate is not a security barrier; it is an expectation-setter.

**Gate visual design:**
Full-width card, centered content:
- Icon: ⚗ (laboratory flask), 48px, TRAFFIC_TEXT_MUTED color
- Title: "Advanced Analytics Laboratory" — Level 2 type scale
- Subtitle: "High-density multi-variable analysis. Recommended for experienced data analysts." — Level 6 body
- Two buttons:
  - "Enter Lab" — primary button, TRAFFIC_CRIMSON background on hover
  - "← Back to Overview" — ghost button, TEXT_MUTED border

The gate is not shown on the second visit to Tab 06 within the same session (lab gate state persists in session_state). Repeat analysts are not re-gated.

---

# PART 10 — RESPONSIVE + ADAPTIVE DESIGN SYSTEM

---

## 10.1 · Breakpoint Definitions

The platform targets these viewport widths, ordered from largest to smallest:

| Breakpoint | Width | Layout Mode | Charts Per Row |
|---|---|---|---|
| Ultrawide | ≥ 1920px | Enterprise full-density | 3 (hero + 2 supporting) |
| Desktop | 1280–1920px | Standard enterprise layout | 2 (hero + 1 supporting) |
| Laptop | 1024–1280px | Condensed layout | 2 (equal-weight columns) |
| Tablet | 768–1024px | Single-column critical path | 1 (stacked) |
| Compact | < 768px | Essential mode | 1 (hero only per page) |

**Implementation Approach:**
Streamlit does not provide JavaScript-accessible viewport width natively. However, the `st.columns()` system responds to the actual rendered width. The column ratios defined in Part 3 naturally adapt:
- `st.columns([3, 2])` at 1280px renders a wide hero + narrower support
- `st.columns([3, 2])` at 900px renders approximately equal columns — acceptable for laptop mode
- At true tablet widths, switch to `st.columns([1])` via a stored viewport constant

**Streamlit custom component approach for responsive detection:**
Inject a one-time JavaScript snippet via `st.components.v1.html()` to write viewport width to session state:
```javascript
// Called once on first load
const vw = window.innerWidth;
window.parent.postMessage({type: 'viewport', width: vw}, '*');
// Streamlit receives via component callback mechanism
```
This allows the page module to choose column configurations: `cols = [3,2] if vw >= 1024 else [1]`.

---

## 10.2 · Chart Resizing Rules by Breakpoint

| Chart | Desktop Height | Laptop Height | Tablet Height | Compact Height |
|---|---|---|---|---|
| T-01 / A-01 KPI Scorecard | 180px (cards, no fixed height) | Same | Same | 2 cards visible |
| T-03 Stream Graph | 420px | 360px | 300px | 260px |
| T-05 Quadrant Scatter | 460px | 400px | 360px | 300px |
| T-11 Ridgeline (16 distributions) | 520px | 480px | 420px | Hidden (collapsed) |
| T-13 Radar | 500px | 460px | 420px | Hidden (lab not available) |
| A-02 Calendar Heatmap | 320px | 280px | 240px | Fullscreen recommended banner |
| A-15 Pairplot | 800px | 700px | Hidden (lab not available) | Hidden |
| All other charts | 360px | 320px | 280px | 240px |

---

## 10.3 · What Visual Complexity Reduces First

When screen size decreases, visual complexity reduces in this priority order:

1. **First to reduce:** Annotations and callout labels. At tablet width, annotation text font reduces from 11px to 9px, then disappears at compact.
2. **Second to reduce:** Secondary supporting charts collapse into `st.expander()` by default.
3. **Third to reduce:** Legend items compress to icon-only (color dot without text).
4. **Fourth to reduce:** Axis labels reduce to every-other-tick marks.
5. **Fifth to reduce:** KPI strip reduces from 4–5 cards to 2 primary cards.
6. **Never reduced:** The hero chart itself (resized, not hidden). KPI values (never truncated). Severity color encoding (always maintained regardless of size).

---

# PART 11 — STREAMLIT UX ENHANCEMENT STRATEGY

---

## 11.1 · Overriding Default Streamlit Feel

A default Streamlit dark app looks like this: gray sidebar, generic st.metric() cards, default font size, standard padding, blue accent color everywhere, and visible Streamlit branding. None of these characteristics are appropriate for an enterprise intelligence platform.

The following CSS injection strategy — delivered through a single `utils/css_injector.py` module — overrides the most impactful default behaviors:

```python
# utils/css_injector.py
# Called once at the top of every page render

def inject_platform_css(dashboard: str = "traffic"):
    from config.theme import (
        TRAFFIC_BG, TRAFFIC_SURFACE_1, TRAFFIC_BORDER_1,
        TRAFFIC_TEXT_PRIMARY, TRAFFIC_TEXT_MUTED, TRAFFIC_CRIMSON
    )
    
    css = f"""
    <style>
    /* ── Global Layout ── */
    .stApp {{
        background-color: {TRAFFIC_BG};
    }}
    
    /* ── Remove default Streamlit header padding ── */
    .block-container {{
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }}
    
    /* ── Typography override ── */
    html, body, [class*="css"] {{
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
    }}
    
    /* ── Tab styling ── */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {TRAFFIC_BG};
        border-bottom: 1px solid {TRAFFIC_BORDER_1};
        gap: 0px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        color: {TRAFFIC_TEXT_MUTED};
        border-radius: 0;
        font-size: 13px;
        font-weight: 400;
        padding: 8px 16px;
        border-bottom: 2px solid transparent;
    }}
    .stTabs [aria-selected="true"] {{
        color: {TRAFFIC_TEXT_PRIMARY};
        font-weight: 600;
        border-bottom: 2px solid {TRAFFIC_CRIMSON};
        background-color: transparent;
    }}
    
    /* ── Expander styling ── */
    .streamlit-expanderHeader {{
        background-color: {TRAFFIC_SURFACE_1};
        border: 1px solid {TRAFFIC_BORDER_1};
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        color: {TRAFFIC_TEXT_MUTED};
    }}
    
    /* ── Sidebar refinement ── */
    .css-1d391kg {{
        background-color: {TRAFFIC_SURFACE_1};
        border-right: 1px solid {TRAFFIC_BORDER_1};
    }}
    
    /* ── Remove Streamlit menu and footer ── */
    #MainMenu, footer, header {{
        visibility: hidden;
    }}
    
    /* ── Button refinement ── */
    .stButton > button {{
        background-color: {TRAFFIC_SURFACE_1};
        border: 1px solid {TRAFFIC_BORDER_1};
        color: {TRAFFIC_TEXT_PRIMARY};
        border-radius: 6px;
        font-size: 13px;
        transition: all 0.15s ease;
    }}
    .stButton > button:hover {{
        border-color: {TRAFFIC_CRIMSON};
        background-color: {TRAFFIC_SURFACE_1};
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
```

This module is called at the top of `app.py` before any routing logic. It applies globally to all pages.

---

## 11.2 · Enterprise Container Architecture

Streamlit's default rendering places all content in a single column with generous padding. Enterprise dashboards require tighter container control. The following container patterns are used throughout:

**Hero Section Container:**
```python
# components/hero_section.py — renders this HTML structure
st.markdown(f"""
<div style="
    background: linear-gradient(90deg, {TRAFFIC_SURFACE_1} 0%, {TRAFFIC_BG} 100%);
    border-left: 3px solid {TRAFFIC_CRIMSON};
    padding: {SPACING_MD}px {SPACING_LG}px;
    margin-bottom: {SPACING_LG}px;
    border-radius: 0 6px 6px 0;
">
    <div style="font-size:11px; font-weight:600; letter-spacing:0.1em; 
                color:{TRAFFIC_TEXT_MUTED}; text-transform:uppercase; margin-bottom:4px;">
        BANGALORE URBAN INTELLIGENCE · TRAFFIC DASHBOARD
    </div>
    <div style="font-size:20px; font-weight:600; color:{TRAFFIC_TEXT_PRIMARY}; 
                letter-spacing:-0.01em;">
        {title}
    </div>
    {f'<div style="...{subtitle_styles}">{subtitle}</div>' if subtitle else ''}
</div>
""", unsafe_allow_html=True)
```

The left border accent in TRAFFIC_CRIMSON / AQI_NAVY is the platform's most consistent visual motif — it appears on hero sections, critical insight panels, and detail panel headers. It creates a continuous vertical line of identity through the page.

**Chart Container:**
```python
# components/chart_container.py
st.markdown(f"""
<div style="
    background-color: {TRAFFIC_SURFACE_1};
    border: 1px solid {TRAFFIC_BORDER_1};
    border-radius: 8px;
    padding: {SPACING_MD}px;
    margin-bottom: {SPACING_LG}px;
">
    <div style="font-size:13px; font-weight:500; letter-spacing:0.05em; 
                text-transform:uppercase; color:{TRAFFIC_TEXT_MUTED};
                margin-bottom:{SPACING_SM}px;">
        {title}
    </div>
""", unsafe_allow_html=True)

# Render the actual chart via st.plotly_chart() or st.altair_chart()
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

if caption:
    st.markdown(f"""
    <div style="font-size:11px; color:{TRAFFIC_TEXT_MUTED}; 
                margin-top:{SPACING_SM}px; opacity:0.8;">
        {caption}
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
```

Note: `config={"displayModeBar": False}` removes Plotly's default mode bar (the camera/zoom toolbar). The enterprise platform should not expose raw chart controls. Where zoom is needed, implement it via custom Streamlit buttons that adjust axis range programmatically.

---

## 11.3 · Filter Panel UX Refinement

The default Streamlit filter widgets (`st.selectbox`, `st.date_input`, `st.multiselect`) look generic. The filter panel must feel like an enterprise control strip.

**Filter strip layout:**
The filter panel renders as a horizontal strip above the hero section, styled as:
```
┌──────────────────────────────────────────────────────────────────┐
│ 📅 Jan 2022 → Aug 2024    🏙 All Areas ▾    [⟳ Reset]  [●ACTIVE]│
└──────────────────────────────────────────────────────────────────┘
```

- Background: `SURFACE_3` (#21262D) — slightly lighter than page background, creating a "control shelf" effect
- Border-bottom: `BORDER_1` — separates the filter shelf from page content
- Font: 13px, TEXT_MUTED by default, TEXT_PRIMARY when a filter is actively set
- "ACTIVE" badge: only renders when `session_state["*_filters_active"] = True` — pill badge, TRAFFIC_AMBER background, "FILTERS ACTIVE" text, 10px font

**Filter active visual communication:**
When a filter is active, a subtle tint renders below the filter strip: a 2px-high bar in TRAFFIC_AMBER at 60% opacity, spanning the full page width. This persistent indicator ensures the analyst never forgets that they are looking at a filtered view.

---

## 11.4 · Sidebar UX

The sidebar is used exclusively in the Advanced Lab for chart control panels (the area toggle panel for T-13). It is not used on Pages 1–5.

**Sidebar styling in Advanced Lab:**
- The sidebar width is constrained to 240px (`[data-testid="stSidebar"] { width: 240px; }`)
- Sidebar header: platform identity strip in SURFACE_1, consistent with main content
- Sidebar body: SURFACE_1 background, no internal padding override
- Sidebar widgets (checkboxes, radio buttons): styled via the global CSS injection to use platform border and text colors
- Sidebar footer: version and dataset info in Level 7 typography

---

# PART 12 — VISUAL DENSITY GOVERNANCE

---

## 12.1 · Density Governance Rules

Visual density is the amount of information per unit of screen space. Higher density is not better — optimal density for an analytical platform matches the analyst's cognitive processing capacity.

| Governance Rule | Limit | Reason |
|---|---|---|
| Charts per page (eager-rendered) | 2 | Beyond 2, analyst attention fragments |
| Charts per page (including collapsible) | 4 | Maximum for session-length analytical tasks |
| Annotation callouts per chart | 3 | More than 3 callouts become visual noise |
| Tooltip fields per hover | 6 | Beyond 6, tooltips require reading not scanning |
| Radar polygon overlays | 4 | Beyond 4, polygon intersections are unreadable |
| Pairplot variables | 7 | Beyond 7, panel cells are too small to read |
| KPI cards in metric strip | 5 | Beyond 5, the strip requires horizontal scrolling |
| Area traces in T-02 parallel coords | 8 | Fixed by dataset (8 areas) — manageable |
| AQI calendar heatmap — year span | 3 | More years at standard cell size = unreadable |
| Stream graph area traces | 8 | Fixed by dataset — manageable with hover-isolation |
| Hexbin cells (T-14, A-06) | 30×30 max | Finer binning defeats density readability |

---

## 12.2 · Anti-Density Patterns to Prevent

**Pattern 1: Annotation Accumulation**
Over-annotated charts develop "callout soup" where no single annotation is noticed because all compete equally for attention. Maximum 3 annotations per chart. Priority hierarchy: threshold lines > quadrant labels > specific point callouts. If all 3 are needed, threshold lines render as lines (no text box), quadrant labels render at reduced opacity (30%), and only the most critical point gets a callout box.

**Pattern 2: Legend Proliferation**
Charts that have the same area color encoding do not each need a legend. The stream graph (T-03) renders the legend for the area color palette once; T-04, T-05, and T-09 on other pages reference the same color palette but suppress repeated legends with a footnote caption: `"Area colors: see Stream Graph legend (P2)"`.

**Pattern 3: Heatmap Saturation**
T-12 (weather × roadwork heatmap) and A-14 (season × pressure grid) use color-scaled cells. Default Plotly heatmap color scales (Viridis, RdYlGn) introduce too many hues across too small a value range. Use a **3-step diverging scale** for T-12: TRAFFIC_TEAL (low congestion risk) → neutral mid-tone → TRAFFIC_CRIMSON (high congestion risk). A-14 uses the AQI 6-band color scale mapped to PM2.5 value ranges.

**Pattern 4: Parallel Coordinates Overload**
T-02 with all 5 axes visible and all 8 area lines fully rendered at full opacity is nearly unreadable on load. The architecture already specifies 3 default axes and 35% opacity for non-focused lines. Add to this: on the initial render (no user interaction yet), all 8 lines render at 40% opacity. The chart's reading instruction — "Hover an area line to isolate it" — renders as a persistent caption below the chart: 11px, TEXT_MUTED. This is not a tooltip — it is always visible.

---

## 12.3 · Ridgeline Density Management

T-11 (16 road distributions) and A-03 (4 seasonal distributions) require different density treatments:

**T-11 (16 distributions):** High density, high analytical value
- Use minimal row height per distribution: 28px per distribution × 16 = 448px total chart height
- Distribution fill opacity: 30% (reduces visual weight of each individual distribution, making the pattern of all 16 more readable than if each were rendered at full opacity)
- The 3 most congested and 2 least congested roads are labeled; the middle 11 have Y-axis labels only

**A-03 (4 seasonal distributions):** Low density, high readability
- Each distribution renders with 50% fill opacity — more visual presence per distribution, appropriate for only 4 layers
- Season labels render inside the distribution peaks (not on Y-axis): "Monsoon", "Winter", "Spring", "Post-Monsoon" at peak density point
- Color: use the 4 seasonal colors (not AQI severity colors) to encode seasonality: Winter = #60A5FA (cool blue), Monsoon = #34D399 (monsoon green), Spring = #FBBF24 (warm amber), Post-Monsoon = #A78BFA (violet)

---

# PART 13 — MOTION + ANIMATION SYSTEM

---

## 13.1 · Animation Philosophy

The platform's animation system follows a single governing principle: **animation must communicate information, not entertain.**

Every animated element must answer: *what does this movement help the analyst understand?*

Animation is appropriate when:
- It reveals temporal sequence (T-03 stream graph left-to-right reveal shows time progression)
- It communicates loading/computational state (loading spinners prevent "is it broken?" anxiety)
- It provides interaction feedback (hover opacity transitions confirm that an element is responding)
- It smooths state transitions (filter-active transitions prevent jarring layout jumps)

Animation is inappropriate when:
- It delays information delivery (a 1-second chart entrance animation makes the analyst wait 1 second for every chart)
- It creates visual noise (background animations during chart reading)
- It is purely decorative (animated gradient on the page background)
- It conflicts with analytical concentration (the analyst is trying to read data; anything moving outside the chart they're reading competes for attention)

---

## 13.2 · Animation Specification

**Chart reveal animation (hero charts only):**
- Timing: 600–800ms ease-out
- Behavior: Y-axis values animate from 0 to actual values (bars grow upward; scatter points materialize from center outward; stream areas fill from baseline upward)
- Implementation: Plotly's native `animation_frame` parameter or `transition` config
- Trigger: First render only. If the analyst changes a filter, charts re-render instantly (no animation) — the analyst is seeking precise values, not a reveal experience

**Tab transition:**
- Timing: 150ms opacity fade between tabs
- Behavior: Outgoing tab content fades to opacity 0; incoming tab content fades from opacity 0 to 1
- Implementation: CSS `transition: opacity 0.15s ease` on `.block-container`
- Note: This is subtle and barely perceptible — its purpose is eliminating jarring layout snaps, not creating a visible effect

**KPI severity state transitions:**
- When a filter change causes a KPI value to cross a severity threshold (e.g., congestion moves from WARNING to CRITICAL), the KPI value color transitions from AMBER to CRIMSON over 300ms
- Implementation: `transition: color 0.3s ease` on KPI value element
- Note: The color change itself communicates the severity shift; the animation gives the analyst's eye time to register it

**Hover state transitions:**
- Chart element opacity changes: instant (Plotly native)
- Card background/border changes: 150ms ease (CSS transition)
- Tab state changes: 100ms ease (CSS transition)
- Gauge ring fill (on initial load): 600ms ease-out (SVG stroke-dasharray transition)

**Loading transitions:**
When a page re-renders due to a filter change, Streamlit shows a spinner overlay. Override the default spinner with a minimal platform-styled loader:

```python
# In utils/css_injector.py — already applied globally
"""
.stSpinner > div {
    border-color: TRAFFIC_CRIMSON transparent transparent transparent;
}
"""
```

---

## 13.3 · What Shall Not Animate

| Element | Prohibition Reason |
|---|---|
| Chart data points after initial render | Distracting during analysis |
| Page background | Impossible to read charts against moving backgrounds |
| KPI values during filter application | Values changing during update create false impressions |
| Collapsible section expand/collapse | Streamlit's native expander handles this; do not override |
| Navigation tab hover states | Beyond 100ms transition — would feel sluggish |
| Drilldown detail panel appearance | Panel should appear instantly; transition delay is unacceptable for operational tools |

---

# PART 14 — FINAL ENTERPRISE UX CHECKLIST

---

## 14.1 · Visual Consistency Checklist

**Color System:**
- [ ] All chart data encodings use colors from `config/theme.py` — no hex strings in chart modules
- [ ] No chart uses more than 3 colors without a legend
- [ ] Severity color (CRIMSON, AMBER, TEAL) appears only where data-driven severity justifies it
- [ ] Traffic charts and AQI charts never share a color token that carries different semantic meaning
- [ ] AQI category colors match WHO/NAAQS standard — never modified for aesthetic preference

**Typography:**
- [ ] All chart titles render via `chart_container()` — never via `fig.update_layout(title=...)`
- [ ] Hero chart titles use Level 3 type scale (uppercase, 16px, 600 weight)
- [ ] Supporting chart titles use Level 4 type scale (uppercase, 13px, 500 weight, muted color)
- [ ] KPI values use monospace font with tabular-nums
- [ ] No font size below 10px appears anywhere in the rendered platform
- [ ] No truncation occurs on KPI values — values are formatted to fit their available space

**Spacing:**
- [ ] All spacing values derive from `SPACING_*` tokens — no hardcoded pixel values in components
- [ ] Consistent `SPACING_LG` (24px) gap between all chart rows
- [ ] `SPACING_XL` (40px) padding around hero section
- [ ] Chart containers have identical internal padding across all pages

---

## 14.2 · Readability Checklist

**Chart Readability:**
- [ ] Every chart has a caption (`chart_container(caption=...)`) with a one-line insight summary
- [ ] No chart has more than 3 annotation callouts visible simultaneously
- [ ] Tooltip fields are formatted via `utils/formatters.py` — no raw float values
- [ ] Axis labels are simplified: unnecessary axis titles suppressed, tick frequency reduced
- [ ] Legend positions are consistent (bottom-center) across all charts that use legends
- [ ] Radar polygon overlays limited to 4 maximum (enforced in T-13 session state logic)

**Dashboard Readability:**
- [ ] The top 30% of each page (Command Zone) is readable without scrolling at 1280px width
- [ ] Maximum 2 charts are eagerly rendered (no scroll required) on each page
- [ ] Insight panels are collapsible and collapsed by default (do not force interpretation on the analyst)
- [ ] Filter active state is permanently visible when filters are applied

---

## 14.3 · Navigation Quality Checklist

- [ ] Every page has a "Investigate Further" nav card pointing to the logically next page
- [ ] Active tab is visually distinct from inactive tabs on every page render
- [ ] The Advanced Lab gate appears on every first visit to Tab 06 within a session
- [ ] The breadcrumb "← Return to Overview" appears in the Advanced Lab on every render
- [ ] Drilldown selections show a "× Clear" control to enable selection clearing
- [ ] Clearing a drilldown selection returns all charts to their unselected default state
- [ ] The filter "Reset All" button clears ALL session state filter keys, not just displayed widgets
- [ ] Dashboard switcher (Traffic ↔ AQI) preserves the filter state of the non-active dashboard

---

## 14.4 · Responsiveness Checklist

- [ ] Charts rendered at `use_container_width=True` on all pages
- [ ] Chart heights are defined as constants in `CHART_SIZES` (config/chart_defaults.py) — not hardcoded per chart
- [ ] Column splits use ratio-based `st.columns()` — no fixed-pixel column widths
- [ ] The T-11 ridgeline (16 distributions) collapses at tablet widths (hidden behind expander)
- [ ] A-02 calendar heatmap renders a "fullscreen recommended" banner at compact widths
- [ ] The Advanced Lab is not accessible below 768px viewport width

---

## 14.5 · Interaction Quality Checklist

- [ ] All drilldown-capable chart elements show `cursor: pointer` on hover
- [ ] Click feedback (CSS `:active` pulse) is implemented on all drilldown elements
- [ ] Cross-chart highlighting (selected area → all area-encoded charts respond) is tested for all 5 area-synced charts
- [ ] Filter changes cause a consistent, complete re-render — no chart shows stale data
- [ ] No chart function accesses `st.session_state` (architectural rule enforced)
- [ ] Drilldown states clear correctly when navigating between pages
- [ ] The radar overlay limit (4 maximum) is enforced with an inline warning on the 5th selection attempt

---

## 14.6 · Chart Density Checklist

- [ ] Maximum 2 charts eagerly render on each page (others behind collapsible sections)
- [ ] T-12 (weather heatmap) is collapsed by default (`default_expanded=False`)
- [ ] T-15 (bubble matrix) is collapsed by default
- [ ] A-14 (season × pressure grid) is collapsed by default
- [ ] T-13 radar (Advanced Lab) and A-15 pairplot (Advanced Lab) are isolated in Tab 06 only
- [ ] T-02 parallel coordinates renders with 3 default axes (not 5) on initial load
- [ ] T-11 ridgeline (16 distributions) does not label the middle 11 roads (only top 3 + bottom 2)

---

## 14.7 · Enterprise Polish Checklist

- [ ] Streamlit default header, footer, and menu are hidden via CSS injection
- [ ] Platform name and dashboard name appear in `st.set_page_config(page_title=...)` — browser tab shows "Traffic Intelligence | BUIP" or "AQI Intelligence | BUIP"
- [ ] Custom spinner animation replaces default Streamlit spinner
- [ ] Chart mode bars are hidden via `config={"displayModeBar": False}` in all `st.plotly_chart()` calls
- [ ] All insight panel text is written as analytical interpretation — not placeholder text
- [ ] Every KPI card shows the filtered N (row count) in its hover tooltip
- [ ] The platform renders without horizontal scroll at 1280px viewport width

---

## 14.8 · Storytelling Quality Checklist

- [ ] Every page hero section subtitle communicates the page's analytical question (not just a label)
- [ ] Every page has a single hero chart that answers the page's primary analytical question
- [ ] Every page's `insight_panel()` text quantifies the key finding — uses actual data values, not generic phrasing
- [ ] The "Investigate Further" nav card on each page provides a specific analytical reason to continue
- [ ] The 6-page analytical arc for each dashboard follows a coherent investigative narrative (from summary → temporal → spatial → threshold → distributional → multi-dimensional)
- [ ] The AQI scorecard (A-01) includes the WHO annual guideline annotation on the PM2.5 mean KPI card

---

## 14.9 · Analytical Clarity Checklist

- [ ] T-08 (Incident Cliff) clearly labels the step function thresholds — the "+21.5 congestion point" callout at the 1→2 incident boundary
- [ ] A-06 (Stagnation Hexbin) clearly identifies and labels the stagnation trap zone
- [ ] A-07 (Extreme Day Radar) uses reversed axis normalization for temperature and visibility (larger value = worse outcome) — and this inversion is noted in the chart caption
- [ ] T-05 (Quadrant Scatter) includes the four quadrant archetype labels at render — not only on hover
- [ ] A-05 (Persistence Series) renders the rolling 7-day average as a distinct trace from the daily PM2.5 values — both are labeled in the chart
- [ ] T-10 (PT Decoupling) insight panel explicitly frames the pattern as correlation-only, not causal — the text avoids policy-failure language per the engineering architecture spec

---

## 14.10 · Production-Readiness Final Gate

Before considering the platform production-ready, confirm:

- [ ] `inject_platform_css()` is called at the top of `app.py` before any routing — CSS applies to all pages
- [ ] `config/chart_defaults.py` `BASE_LAYOUT` has been tested: changing `paper_bgcolor` there changes all 30 charts simultaneously
- [ ] `utils/formatters.py` functions are used consistently — spot-check 10 random chart tooltips
- [ ] The dataset date range displayed in the filter strip matches the actual data range (Traffic: Jan 2022–Aug 2024; AQI: 2021–2023)
- [ ] Advanced Lab pages (T-13 and A-15) have been tested in isolation: they render correctly with full data and do not depend on any drilldown state set on Pages 1–5
- [ ] The platform has been reviewed on both a 1920px desktop monitor and a 13-inch laptop (approximately 1280px) — both layouts are acceptable
- [ ] No `st.write()` debugging output appears on any page
- [ ] The cross-dashboard switcher has been tested: switching Traffic → AQI → Traffic restores the Traffic filter state correctly

---

*Document: SUAQIS Visual UX Architecture Blueprint*  
*Platform: Bangalore Urban Intelligence Platform — Traffic + AQI Dashboards*  
*Scope: Visual Design · UX Architecture · Interaction Systems · Enterprise Experience*  
*Status: Design Engineering Specification · Pre-Implementation*  
*Companion: bangalore_implementation_architecture.md (Engineering Architecture — unchanged)*  
*Total Charts Covered: 30 (T-01 through T-15 · A-01 through A-15)*  
*Total Pages Covered: 12 (6 Traffic · 6 AQI)*  
*Total Components Referenced: 11 (kpi_card · metric_strip · hero_section · insight_panel · filter_panel · nav_card · chart_container · collapsible_section · lab_gate · lab_header · detail_panel)*
