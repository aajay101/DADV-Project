# SUAQIS · SMART URBAN AIR QUALITY + INTELLIGENCE SYSTEM
## Enterprise UX Architecture Addon
### Production Refinement Layer · Advanced Implementation Guidance · Visual Systems Expansion

**Document Type:** UX Architecture Addon · Production Enhancement Specification  
**Status:** Implementation Precision Layer · Companion to Pre-Implementation Blueprint  
**Scope:** Traffic Intelligence Dashboard + AQI Environmental Intelligence Dashboard  
**Additive To:** `SUAQIS_Visual_UX_Architecture_Blueprint.md` · `bangalore_implementation_architecture.md`  
**Does Not Replace:** Any existing architecture specification, component contract, or engineering blueprint  
**Purpose:** Eliminate remaining implementation ambiguity · Add production-grade UX systems not yet specified

---

> **Document Role:** This addon operates as a production-readiness expansion layer above the existing UX blueprint. Every section in this document *adds* specification that was either absent or underdefined in prior documents. Where existing architecture has already defined a behavior, this document deepens, qualifies, or edge-cases it — it does not contradict it. The existing blueprint, engineering architecture, and this addon document form a three-layer specification stack: engineering architecture → visual UX blueprint → this production enhancement addon.

---

# PART 1 — PAGE WIREFRAME + VIEWPORT COMPOSITION ADDON

---

## 1.1 · Viewport Composition Philosophy

The existing UX blueprint defines the three-zone page model (Command / Investigation / Context) and the column ratio system. What it leaves underdefined is *how these zones deform and recompose across viewport widths*, and *exactly how charts are positioned relative to one another within the Investigation Zone*.

The implementation AI must never need to guess:

- Whether the hero chart sits left or top relative to its supporting chart
- What happens to the KPI strip at 1024px vs 1440px vs 1920px
- Which chart breaks to a second row and which collapses into an expander at each breakpoint
- How far the sticky filter strip sits from the viewport top edge

This section closes all of those gaps.

---

## 1.2 · Desktop Viewport Composition (1440px–1920px)

The primary target viewport. All page architecture definitions in the existing blueprint assume this range.

**Standard Page Wireframe — Desktop (Illustrative for P1 Traffic / P1 AQI):**

```
┌────────────────────────────────────────────────────────────────────────────┐
│ ████ FILTER STRIP (sticky, z-index: 100)                        [Active ×] │ ← 48px / #21262D bg
│  Date Range: Jan 2022 – Aug 2024  |  Area: All  |  Road: All  |  Reset All │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  COMMAND OVERVIEW · TRAFFIC INTELLIGENCE              [CRITICAL] severity  │ ← Hero section: 88px
│  "What is the system-wide congestion and capacity status?"                 │
│                                                                            │
├─────────┬─────────┬─────────┬─────────┬─────────────────────────────────  ┤
│  KPI 1  │  KPI 2  │  KPI 3  │  KPI 4  │         (secondary KPI row)       │ ← KPI strip: 96px
│  87.3   │  64%    │ 1,247   │ 26.4    │  134avg  52.3%   78.1%   128.4    │
│ [gauge] │ [gauge] │ [gauge] │ [gauge] │  (no gauges on secondary row)     │
├─────────┴─────────┴─────────┴─────────┴─────────────────────────────────  ┤
│                                                                            │ ← Spacer: 24px
├────────────────────────────────────────────┬───────────────────────────────┤
│                                            │                               │
│  T-01 · SATURATION COMMAND SCORECARD       │  T-08 · INCIDENT CLIFF        │
│  [HERO CHART — ratio: 3]                   │  [SECONDARY — ratio: 2]       │
│                                            │                               │
│  ████████████████████████████████████████  │  ████████████████████████     │
│  ████████████████████████████████████████  │  ████████████████████████     │
│  ████████████████████████████████████████  │  ████████████████████████     │
│  ████████████████████████████████████████  │  ████████████████████████     │
│  ████████████████████████████████████████  │  ████████████████████████     │
│  [height: 460px]                           │  [height: 340px]              │
│  Caption: one-line insight                 │  Caption: one-line insight    │
│                                            │                               │
├────────────────────────────────────────────┴───────────────────────────────┤
│                                                                            │ ← Spacer: 32px
├─────────────────────────────────────────────────────────────────────────  ─┤
│  ▶ WHAT THIS MEANS  (collapsed by default)                                 │ ← insight_panel: 40px collapsed
├────────────────────────────────────────────────────────────────────────────┤
│  → Investigate Further: Temporal Patterns  [nav_card]                      │ ← nav_card: 64px
└────────────────────────────────────────────────────────────────────────────┘
```

**Chart Positioning Rules at Desktop:**

| Situation | Column Arrangement | Hero Height | Secondary Height |
|---|---|---|---|
| Hero + one supporting chart | `st.columns([3, 2])` | 460px | 340px |
| Hero + two supporting charts stacked | `st.columns([3, 2])` with secondary column containing two charts | 460px | 160px each |
| Full-width single hero (scorecards, calendar) | `st.columns([1])` | 500px | — |
| Side-by-side equals (P4: T-09 + T-10) | `st.columns([1, 1])` | 400px | 400px |
| Radar with toggle panel (T-13, A-15) | `st.columns([4, 1])` | 460px | Control panel only |

---

## 1.3 · Ultrawide Viewport Adaptation (1920px–2560px)

At ultrawide resolutions, the default Streamlit `st.layout="wide"` container reaches its natural width ceiling. Without explicit composition rules, charts become uncomfortably wide at these resolutions — scatter points spread apart, bar charts develop awkward spacing, and reading flow breaks.

**Ultrawide Behavior:**

The platform does **not** expand to fill ultrawide viewports infinitely. Instead:

```python
# In inject_platform_css():
.main .block-container {
    max-width: 1600px;
    margin: 0 auto;
    padding-left: 40px;
    padding-right: 40px;
}
```

This centers the platform content at a maximum of 1600px, with generous side margins that acknowledge the wider viewport without distorting the chart composition.

**Why 1600px cap:** Plotly charts rendered much wider than 1200px begin to lose spatial density — distributions in ridgeline charts separate too far, heatmap cells become rectangles, and scatter plots develop empty center areas. The 1600px cap preserves chart density at the level of analytical utility.

**Ultrawide Wireframe (centered, max 1600px):**

```
┌────────────────────────────[viewport 2560px]───────────────────────────────┐
│   [empty margin]   ┌──────────────[1600px]──────────────┐   [margin]       │
│                    │  FILTER STRIP                       │                  │
│                    │  HERO SECTION                       │                  │
│                    │  KPI STRIP ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │                  │
│                    │  HERO CHART (3)  |  SECONDARY (2)  │                  │
│                    │  INSIGHT + NAV                      │                  │
│                    └─────────────────────────────────────┘                  │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 1.4 · Laptop Viewport Composition (1024px–1440px)

This is the most operationally important breakpoint — analysts reviewing dashboards on 13–15 inch laptops in briefing rooms, field offices, or transit. The architecture must function completely at this size without horizontal scroll.

**Layout Adjustments at Laptop Width:**

```
┌─────────────────────────────────────────────────────────────────────┐
│ FILTER STRIP (condensed — labels hidden, icons only at < 1200px)    │ ← 40px
│  [📅]  [📍]  [🛣]  [↺]                                              │
├─────────────────────────────────────────────────────────────────────┤
│  HERO SECTION (reduced — subtitle collapses to one line)            │ ← 72px
├──────────────┬──────────────┬──────────────┬────────────────────────┤
│  KPI 1       │  KPI 2       │  KPI 3       │  KPI 4                 │ ← 80px (4-column strip preserved)
│  (no gauge)  │  (no gauge)  │  (no gauge)  │  (no gauge)            │
│  Secondary KPI row collapses to 2-column below primary row          │
├──────────────┴──────────────┴──────────────┴────────────────────────┤
│  HERO CHART (full width — secondary chart moves to below)           │ ← 400px
├─────────────────────────────────────────────────────────────────────┤
│  SECONDARY CHART (full width below hero)                            │ ← 300px
├─────────────────────────────────────────────────────────────────────┤
│  ▶ WHAT THIS MEANS (collapsed)                                      │
│  → Investigate Further  [nav_card]                                  │
└─────────────────────────────────────────────────────────────────────┘
```

**Critical laptop breakpoint rules:**

- `st.columns([3, 2])` splits are **preserved** — Streamlit handles responsive column compression natively
- Gauge rings on KPI cards are **hidden** at viewport < 1200px: `@media (max-width: 1200px) { .gauge-ring { display: none; } }`
- Secondary KPI row collapses under the primary row (4 primary + 4 secondary becomes two sequential full-width rows)
- A-02 calendar heatmap renders a persistent banner at this width: `"⚠ Calendar detail is best viewed at 1440px+. Tap 'Fullscreen' to expand."`
- T-11 ridgeline (16 distributions, very wide) is automatically collapsed into an expander with the label: `"Road Distribution Analysis (16 roads) — expand for full view"`

---

## 1.5 · Tablet Viewport Composition (768px–1024px)

Tablet is a constrained reading context. Multi-column chart layouts become unusable at this width. The dashboard shifts to a single-column, scrollable reading mode.

**Tablet-specific behaviors:**

- All `st.columns([3, 2])` and `st.columns([1, 1])` splits collapse to single-column sequential rendering
- Hero chart renders full-width at 380px height
- Supporting charts render full-width at 300px height, below the hero
- KPI strip collapses to a 2×2 grid (not a single row) — 4 primary KPI cards in a 2-column arrangement
- Secondary KPI row collapses behind a `▶ View All Metrics` expander
- Insight panels remain collapsed — the analyst must choose to expand
- Navigation cards are reduced to text link style (no description)
- Advanced Lab (Tab 06) renders a blocking message: `"Advanced Laboratory requires a desktop viewport (1024px minimum). Please switch to a larger screen."`

**Tablet KPI Layout:**

```
┌─────────────────────────┬──────────────────────────┐
│  KPI 1: 87.3            │  KPI 2: 64%              │
│  System Congestion      │  Capacity Saturation     │
├─────────────────────────┼──────────────────────────┤
│  KPI 3: 1,247           │  KPI 4: 26.4 km/h        │
│  Active Incidents       │  Average Speed           │
└─────────────────────────┴──────────────────────────┘
▶ View 4 Additional Metrics
```

---

## 1.6 · Compact Screen Adaptation (< 768px)

The platform is not designed for mobile. However, rather than delivering a broken experience, it delivers a graceful degradation mode.

**Compact screen behavior:**

- All charts collapse behind `st.expander()` wrappers with descriptive labels
- KPI cards render in a vertical list (single column) — value + label + severity badge only, no gauge
- Filter panel collapses to a sidebar button: `☰ Filters` — tapping opens a full-page filter overlay
- A persistent warning banner at the top: `"BUIP is optimized for desktop use. Some features are unavailable at this screen size."`
- No attempt is made to force chart rendering at < 320px column width — charts that would render unreadably are replaced with tabular summaries

---

## 1.7 · Sticky Analytical Regions

The filter strip is the primary sticky element. Its behavior is specifically defined to avoid visual conflict with the chart reading zone.

**Filter strip sticky implementation:**

```css
.filter-strip {
    position: sticky;
    top: 0;
    z-index: 100;
    background: #21262D;        /* TRAFFIC_SURFACE_3 */
    border-bottom: 1px solid #30363D;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    transition: box-shadow 0.2s ease;
}

.filter-strip.scrolled {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}
```

The `scrolled` class is toggled via a small JS injection:

```javascript
// Inject via st.components.v1.html() in inject_platform_css()
window.addEventListener('scroll', function() {
    const strip = document.querySelector('.filter-strip');
    if (strip) {
        strip.classList.toggle('scrolled', window.scrollY > 10);
    }
});
```

**Why backdrop-filter blur:** When the analyst scrolls, page content slides under the filter strip. Without blur, the overlapping chart content creates visual conflict. The blur creates a frosted-glass separation that clarifies the spatial hierarchy: filter strip = chrome layer, chart = content layer.

**What is NOT sticky:** KPI cards, hero section, navigation cards. Only the filter strip achieves sticky behavior. Making additional elements sticky creates competing fixed layers that consume viewport height.

---

## 1.8 · Scroll Segmentation and Reading Flow

Each page is segmented into explicit scroll positions. The analyst's reading experience is a vertical journey through defined content zones:

```
Scroll Position 0–100px:    Command Zone (KPI strip visible, filter strip docked)
Scroll Position 100–600px:  Investigation Zone (hero chart in view)
Scroll Position 600–1000px: Supporting chart and beginning of context zone
Scroll Position 1000px+:    Context Zone (insight panel, nav card)
```

**Scroll segmentation implementation:** Explicit `st.markdown("<div style='margin-top: {SPACING}px'></div>")` spacers are placed between each zone. These are not decorative — they establish the visual pauses that signal zone transitions to the analyst. The spacing values are:

- Between Command Zone and Investigation Zone: `SPACING_XL` (40px)
- Between hero chart and supporting chart (when stacked): `SPACING_LG` (24px)  
- Between Investigation Zone and Context Zone: `SPACING_2XL` (64px)

---

# PART 2 — COMPONENT STATE SYSTEM ADDON

---

## 2.1 · State System Architecture

The existing UX blueprint defines hover states for several components. It does not define the complete multi-state model for every component type — which creates implementation drift as developers invent their own loading, error, and disabled treatments.

This section defines the canonical state set for every interactive component. The implementation must match these specifications exactly. Any state not defined here defaults to the component's normal state.

**Canonical State Set:**

| State | Trigger | Visual Signal |
|---|---|---|
| `default` | Component rendered, no interaction | Base appearance |
| `hover` | Mouse over element | Surface lift + border brightening |
| `active` | Mouse button held | Scale compression (0.98) |
| `selected` | User clicked or drilldown applied | Border accent + badge |
| `focused` | Keyboard focus reached element | Focus ring |
| `loading` | Data computation in progress | Shimmer / skeleton |
| `disabled` | Interaction blocked (e.g., Advanced Lab gate) | 40% opacity, cursor not-allowed |
| `filtered` | Data is filtered and showing subset | Badge indicator |
| `stale` | Cached data may be outdated | Muted border + warning label |
| `error` | Computation or render failure | Error banner |
| `empty` | Zero rows match current filters | Empty state panel |

---

## 2.2 · KPI Card — Complete State Specification

```
DEFAULT STATE:
  background:     SURFACE_1 (#161B22)
  border:         1px solid BORDER_1 (#30363D)
  border-radius:  8px
  opacity:        1.0
  value-color:    [severity-determined: CRITICAL/WARNING/SAFE/NEUTRAL]
  transition:     all 150ms ease

HOVER STATE:
  background:     SURFACE_2 (#1C2128)
  border:         1px solid #484F58
  cursor:         default (KPI cards are not clickable unless explicitly drilldown-capable)
  transition:     background 150ms ease, border-color 150ms ease

ACTIVE STATE (drilldown-capable KPI cards only):
  transform:      scale(0.98)
  transition:     transform 60ms ease
  cursor:         pointer

SELECTED STATE (after drilldown click):
  border:         1px solid TRAFFIC_AMBER (or AQI_CYAN for AQI)
  border-left:    3px solid TRAFFIC_AMBER
  background:     rgba(TRAFFIC_AMBER, 0.05) tint
  badge:          "Active Filter" pill, 10px, amber background, 6px right of title

FOCUSED STATE (keyboard navigation):
  outline:        2px solid TRAFFIC_SLATE (#58A6FF)
  outline-offset: 2px
  
LOADING STATE:
  Replace value area with shimmer block: 60px × 20px
  Replace label with shimmer block: 100px × 12px
  Gauge ring: pulsing opacity 0.3→0.7→0.3, 1.2s infinite
  (See Part 3 for shimmer system specification)

DISABLED STATE:
  opacity:        0.4
  cursor:         not-allowed
  pointer-events: none
  
FILTERED STATE (data subset active):
  Visual: identical to DEFAULT
  Badge: "(Filtered)" appended to subtitle in TEXT_MUTED

STALE-DATA STATE (cache age > configurable threshold, default 5min):
  border:         1px solid #FFBA08 at 30% opacity
  Corner badge:   "⟳ Stale" — 9px, TEXT_MUTED, top-right corner of card

ERROR STATE:
  background:     rgba(229, 56, 59, 0.05)   /* TRAFFIC_CRIMSON tint */
  border:         1px solid rgba(229, 56, 59, 0.3)
  value:          "—" (em dash) in TEXT_MUTED
  subtitle:       "Data unavailable" in TEXT_MUTED, 11px

EMPTY STATE:
  value:          "0" in TEXT_MUTED (never blank — always show the zero explicitly)
  badge:          "No data for filters" in SURFACE_3 pill below subtitle
```

---

## 2.3 · Chart Container — Complete State Specification

```
DEFAULT STATE:
  background:     SURFACE_1
  border:         none (charts rely on spatial separation, not borders)
  border-radius:  8px
  padding:        16px

HOVER STATE (on the container, not the chart internals):
  No container-level hover behavior — chart hover is handled by Plotly internally
  Exception: chart title area shows a subtle "⤢ Fullscreen" icon on far right, fading in

LOADING STATE:
  Chart area replaced with skeleton (see Part 3)
  Title area: visible (title loads first, content loads second — reduces perceived load time)
  Caption: visible as TEXT_MUTED placeholder: "Calculating..."

SELECTED/DRILLDOWN-ACTIVE STATE:
  border:         1px solid rgba(TRAFFIC_AMBER, 0.4)
  title:          Selection badge appended (e.g., "Koramangala" pill in amber)
  
STALE-DATA STATE:
  title:          Append small "⟳" icon in TEXT_MUTED with tooltip: "Data may be stale"

ERROR STATE:
  Chart area replaced with error panel (see Part 4)
  Title: unchanged (so analyst can identify which chart failed)

EMPTY STATE:
  Chart area replaced with empty panel (see Part 4)
  Title: unchanged with "(No Data)" suffix in TEXT_MUTED

FULLSCREEN STATE:
  Container expands to fill viewport
  background:     BG (#0D1117 / #0A0F1E) — full page takeover
  "× Exit Fullscreen" button: top-right, always visible
  Chart re-renders at fullscreen dimensions via session_state flag
  All other page content: hidden (display: none) during fullscreen
```

---

## 2.4 · Filter Panel — Complete State Specification

```
DEFAULT STATE (no filters applied):
  Filter strip: shows all widgets at full opacity
  "Reset All" button: TEXT_MUTED, opacity 0.5 (no active filters to reset)
  Active filter count badge: hidden

ACTIVE FILTERED STATE (one or more non-default filters):
  Filter strip: unchanged
  "Reset All" button: TEXT_PRIMARY, opacity 1.0, hover: TRAFFIC_CRIMSON
  Active filter count badge: appears — e.g., "2 filters active" — amber pill, left of Reset button

HOVER (individual filter widget):
  Do not override Streamlit's native widget hover behavior
  Exception: the "Reset All" button uses custom hover: background TRAFFIC_CRIMSON at 15% opacity

LOADING STATE (during filter-triggered re-run):
  A thin progress bar replaces the filter strip's bottom border:
  height:         2px
  background:     animated gradient from transparent → TRAFFIC_SLATE → transparent
  animation:      2s linear infinite slide
  This signals that a re-run is in progress without obscuring any filter controls.

DISABLED STATE (during chart computation):
  Filter widgets: pointer-events: none (cannot click a new filter during active re-run)
  Opacity:        0.7 (slightly dimmed to signal not-yet-interactive)
  Duration:       disabled for the duration of the re-run only
```

---

## 2.5 · Navigation Card — Complete State Specification

```
DEFAULT STATE:
  background:     SURFACE_1
  border:         1px solid BORDER_2 (#21262D)
  border-radius:  8px
  padding:        16px 20px
  arrow icon:     → in TEXT_MUTED

HOVER STATE:
  background:     SURFACE_2
  border:         1px solid rgba(TRAFFIC_CRIMSON, 0.4)   [Traffic] 
                  1px solid rgba(AQI_CYAN, 0.4)          [AQI]
  border-left:    3px solid TRAFFIC_CRIMSON              [Traffic]
                  3px solid AQI_CYAN                     [AQI]
  arrow icon:     → moves 4px right (CSS: transform: translateX(4px), transition 150ms)
  cursor:         pointer
  transition:     all 150ms ease

ACTIVE STATE:
  transform:      translateY(1px) — subtle press-down feeling
  transition:     transform 60ms ease

DISABLED STATE (appears on P6 Advanced Lab gate):
  opacity:        0.35
  cursor:         not-allowed
  pointer-events: none
  border:         1px solid BORDER_2 unchanged
```

---

## 2.6 · Collapsible Section — Complete State Specification

```
COLLAPSED DEFAULT STATE:
  Header:         background SURFACE_3, full-width, 44px height
  Chevron icon:   ▶ (pointing right), TEXT_MUTED
  Title:          TEXT_MUTED, 13px weight 500 uppercase
  Content:        hidden (height: 0, overflow: hidden)

HOVER STATE (header):
  Header:         background SURFACE_2
  Chevron:        TEXT_PRIMARY
  cursor:         pointer
  transition:     background 100ms ease

EXPANDED STATE:
  Chevron:        ▼ (pointing down), TEXT_PRIMARY
  Title:          TEXT_PRIMARY
  Content:        visible, animation: max-height 0→content-height, 200ms ease-out
  Header:         background SURFACE_2 (stays elevated when open)

LOADING STATE (content inside is loading):
  Chevron:        animated spinner replaces chevron temporarily
  Content area:   skeleton placeholders (see Part 3)
```

---

## 2.7 · Tab Navigation — Complete State Specification

```
ACTIVE TAB:
  color:          TEXT_PRIMARY (#F0F6FC)
  border-bottom:  2px solid TRAFFIC_CRIMSON [Traffic] / AQI_CYAN [AQI]
  font-weight:    600
  background:     transparent

INACTIVE TAB (default):
  color:          TEXT_MUTED
  border-bottom:  none
  font-weight:    400
  cursor:         pointer

INACTIVE TAB HOVER:
  color:          TEXT_PRIMARY (not secondary-active color — only the active tab gets the accent)
  border-bottom:  1px solid BORDER_1
  transition:     color 100ms ease, border 100ms ease

DISABLED TAB (e.g., Advanced Lab gate):
  color:          TEXT_MUTED at 50% opacity
  cursor:         not-allowed
  tooltip:        "Advanced Lab — enable in Settings or visit after completing P1–P5"
```

---

## 2.8 · Drilldown Panel — Complete State Specification

The drilldown panel is the detail panel that renders below or beside a chart when a user selects an element (e.g., clicking an area in T-05 Quadrant Scatter reveals the Area Detail Panel).

```
HIDDEN STATE (no selection):
  display:        none — does not occupy vertical space

APPEARING STATE (selection just made):
  animation:      slide down from 0px → full height, 200ms ease-out
  opacity:        0 → 1, 150ms ease
  
VISIBLE DEFAULT STATE:
  background:     SURFACE_2
  border-left:    3px solid [selection color — area color for traffic, AQI category for AQI]
  border-radius:  0 8px 8px 0
  padding:        16px 20px
  Title:          "Detail: [Selection Name]" — TEXT_PRIMARY, 14px weight 600
  Content:        Analytical breakdown rows

CLEAR CONTROL:
  Position:       top-right of panel
  Label:          "× Clear Selection"
  Color:          TEXT_MUTED
  Hover:          TRAFFIC_CRIMSON, cursor pointer
  Click behavior: clears session_state drilldown key → panel animates out

DISMISSING STATE (× clicked):
  animation:      slide up to 0px, 180ms ease-in + opacity 1 → 0
  After animation: display: none
```

---

# PART 3 — LOADING + PERCEIVED PERFORMANCE UX ADDON

---

## 3.1 · Loading UX Philosophy

Streamlit's fundamental execution model is: every interaction triggers a full Python re-run. This means that from the browser's perspective, *all* content is periodically replaced. Without a deliberate loading UX, this creates a jarring experience: charts disappear and reappear, KPI values flash, the entire page blinks.

The goal is not to eliminate this re-run behavior — it is a core Streamlit characteristic. The goal is to *layer perceived-performance UX* on top of it so that the analyst never feels like the platform is unresponsive or unstable.

**Three-tier loading strategy:**

1. **Instant feedback** (< 50ms): CSS `:active` states, button press compression — handled entirely in CSS, no Python involvement
2. **Progress signaling** (50ms–800ms): Thin animated progress bar on filter strip, spinner governance — signals the re-run is active
3. **Placeholder architecture** (800ms+): Skeleton loaders replace chart areas during data-heavy re-runs — prevents blank containers

---

## 3.2 · Skeleton Loader System

Skeleton loaders are layout-accurate placeholder blocks that mirror the shape of the content they stand in for. They use the shimmer animation system defined below.

**Shimmer animation (single CSS definition, applied platform-wide):**

```css
@keyframes shimmer {
    0%   { background-position: -400px 0; }
    100% { background-position: 400px 0; }
}

.skeleton {
    background: linear-gradient(
        90deg,
        #1C2128 0%,           /* SURFACE_2 — base */
        #2D333B 40%,           /* SURFACE_4 — shimmer peak */
        #1C2128 80%            /* SURFACE_2 — return */
    );
    background-size: 800px 100%;
    animation: shimmer 1.4s ease-in-out infinite;
    border-radius: 4px;
}
```

**KPI Card skeleton layout:**

```html
<!-- Replaces kpi_card() content during loading -->
<div class="kpi-skeleton">
  <div class="skeleton" style="width:60%; height:36px; margin-bottom:8px;"></div>   <!-- Value -->
  <div class="skeleton" style="width:80%; height:12px; margin-bottom:4px;"></div>   <!-- Label -->
  <div class="skeleton" style="width:40%; height:10px;"></div>                      <!-- Sublabel -->
</div>
```

**Chart container skeleton layout:**

```html
<!-- Replaces chart render area during loading — matches hero chart height (460px) -->
<div class="chart-skeleton" style="height: 460px;">
  <!-- X-axis skeleton (bottom) -->
  <div class="skeleton" style="position:absolute; bottom:24px; width:90%; height:12px; left:5%;"></div>
  <!-- Y-axis skeleton (left) -->
  <div class="skeleton" style="position:absolute; left:40px; height:80%; width:12px; top:5%;"></div>
  <!-- Simulated chart body — 3 irregular bars suggest chart content -->
  <div class="skeleton" style="position:absolute; bottom:40px; left:10%; width:12%; height:55%;"></div>
  <div class="skeleton" style="position:absolute; bottom:40px; left:26%; width:12%; height:75%;"></div>
  <div class="skeleton" style="position:absolute; bottom:40px; left:42%; width:12%; height:40%;"></div>
  <!-- etc. — use 6–8 bars for bar charts, 3 flowing bands for stream charts -->
</div>
```

**The chart title is never skeletonized.** Titles load immediately (they are static markdown, not data-dependent). Only the chart body area shows a skeleton. This means the analyst can see which chart is loading even before the data arrives.

---

## 3.3 · Progressive Rendering and Staged Chart Reveal

When multiple charts load on a page, they should not all appear simultaneously after a long blank wait. They should appear in priority order, creating a progressive reveal that matches the visual hierarchy.

**Staged reveal sequence:**

```
Stage 1 (immediate): Filter strip + Hero section + KPI skeletons  →  0ms delay
Stage 2 (fast):       KPI cards with data                          →  After @st.cache_data resolves (typically < 200ms)
Stage 3 (normal):     Hero chart                                    →  After chart-specific aggregation resolves
Stage 4 (delayed):    Supporting chart                              →  50ms after hero chart appears
Stage 5 (deferred):   Collapsible sections remain collapsed         →  Only load if expanded
```

**Implementation approach:**

Use `@st.cache_data` with `ttl=300` (5 minutes) on all aggregation functions. Load KPI metrics from a separate, faster aggregation path than chart data:

```python
# Separate caching tiers:
@st.cache_data(ttl=300)
def load_kpi_metrics(df, filters) -> dict:
    # Fast: scalar aggregations only — returns in <50ms
    ...

@st.cache_data(ttl=300)  
def load_chart_data_hero(df, filters) -> pd.DataFrame:
    # Moderate: grouped aggregation for hero chart
    ...

@st.cache_data(ttl=300)
def load_chart_data_supporting(df, filters) -> pd.DataFrame:
    # Can be slightly slower — analyst sees KPI + hero first
    ...
```

By rendering `load_kpi_metrics()` first (fast), the Command Zone fills with real data immediately while the Investigation Zone's skeleton loaders continue shimmering.

---

## 3.4 · Streamlit Rerender Mitigation

Streamlit's re-run behavior creates three specific UX failure modes that require explicit mitigation:

**Failure 1: Full-page flash on filter change**

*Problem:* When the analyst adjusts a date filter, all components disappear and rerender simultaneously, creating a disorienting visual blank period.

*Mitigation:* Use `st.empty()` placeholder containers for chart regions. On re-run, fill these containers with skeleton loaders *first*, then replace with chart content when computation completes. The visual effect: charts fade from skeleton → real content, rather than blank → real content.

```python
# Page module pattern:
chart_slot = st.empty()

with chart_slot.container():
    render_chart_skeleton(height=460)   # immediate: shows skeleton

# After data loads:
fig = load_and_render_hero_chart(...)
with chart_slot.container():
    chart_container(fig, title="T-01 · Saturation Command Scorecard", ...)
```

**Failure 2: Spinner covering the entire viewport**

*Problem:* Streamlit's default spinner appears as a full-page overlay, blocking all content visibility during re-runs.

*Mitigation:* Replace the default spinner with a thin top-of-page progress bar:

```css
/* Hide default Streamlit spinner */
.stSpinner { display: none !important; }

/* Show only the filter-strip progress bar during re-runs */
```

Use `st.spinner()` contexts only for operations exceeding 2 seconds (e.g., first-load data parsing). For standard filter-triggered re-runs, the filter strip progress bar is sufficient feedback.

**Failure 3: KPI values flickering between zero and real values**

*Problem:* During re-runs, KPI card values briefly render as "0" or empty before real data loads, creating false severity readings.

*Mitigation:* KPI skeleton loaders are shown during the computation period. Never render a "0" value from a partially-computed metric. The `kpi_card()` component accepts an explicit `loading=True` parameter that renders the skeleton state instead of a value.

---

## 3.5 · Loading Hierarchy and Spinner Governance

**Spinner governance rules — when spinners are permitted:**

| Situation | Appropriate Feedback | NOT Appropriate |
|---|---|---|
| Initial page load (cold cache, data parse) | `st.spinner("Loading platform data...")` full-page | No feedback at all |
| Filter change (warm cache) | Filter strip progress bar only | Full-page spinner |
| Drilldown click | CSS `:active` pulse + filter strip progress bar | Any spinner |
| Advanced Lab first load (large computation) | `st.spinner()` inside the chart container only | Full-page overlay |
| Export generation | Modal spinner inside export dialog only | Page-level spinner |

**Rule:** The full-page spinner (`st.spinner()` wrapping the entire page render) is used **only** on initial cold-cache load. Every subsequent interaction uses localized feedback mechanisms.

---

# PART 4 — EMPTY / ERROR / NO-DATA UX ADDON

---

## 4.1 · Analytical Fallback Architecture Philosophy

A dashboard that shows blank charts or broken containers is not a minor aesthetic problem — it is an analytical trust failure. The analyst cannot distinguish between "no data" and "something is wrong." This ambiguity destroys confidence in the platform.

Every possible fallback state must communicate three things:
1. **What happened:** A plain-language description of the condition
2. **Why it happened:** Operational context (too-narrow filter, data unavailable for period)
3. **What to do next:** A specific actionable recovery path

---

## 4.2 · No-Data Chart Behavior

When the current filter combination returns zero rows, charts do not render. Instead, a structured empty state panel occupies the chart's normal height:

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│           📊  (icon, TEXT_MUTED, 32px)              │
│                                                     │
│      No data matches the current filters            │
│      (TEXT_PRIMARY, 14px, weight 500)               │
│                                                     │
│   The selected date range and area filters          │
│   return 0 records from the traffic dataset.        │
│   (TEXT_MUTED, 13px, line-height 1.6)               │
│                                                     │
│   [ ← Reset Filters ]   [ View All Data ]           │
│    (TRAFFIC_SLATE, 12px)  (TRAFFIC_SLATE, 12px)     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Implementation:**

```python
def chart_container(fig, title, caption="", height=460, ...):
    if fig is None:
        render_empty_state(
            title=title,
            height=height,
            message="No data matches the current filters.",
            context="Adjust the date range or area filter to include more records.",
            actions=[("Reset Filters", "reset_all_filters"), 
                     ("View All Data", "clear_and_reload")]
        )
        return
    # ... normal chart rendering
```

**Empty state icons by chart type:**

| Chart Type | Empty State Icon |
|---|---|
| KPI scorecard cards | — (em dash) with "(No data)" below in TEXT_MUTED |
| Time series / stream | `📈` muted |
| Scatter / hexbin | `⬡` muted (hexagon outline) |
| Bar / violin | `▬` muted |
| Calendar heatmap | `📅` muted |
| Radar / pairplot | `🕸` muted |

---

## 4.3 · Invalid Filter Handling

Some filter combinations are logically impossible or produce analytically meaningless results (e.g., a date range of a single day for a chart designed to show 30-day rolling averages).

**Invalid filter detection rules:**

| Condition | Detection Logic | UX Response |
|---|---|---|
| Date range < 7 days (for rolling-average charts) | `(end_date - start_date).days < 7` | Warning banner below filter strip: "⚠ Rolling average charts require 7+ days. Showing raw values." |
| Single area selected for multi-area comparison charts | `len(selected_areas) == 1` | Chart renders with note: "Multi-area comparison requires 2+ areas. Only one area selected." |
| Road filter and Area filter conflict | Road not in selected Area | Warning: "Selected road is outside the selected area. Showing road data only." |
| Date range outside dataset bounds | `start_date < dataset_min` | Filter silently clamped to dataset bounds + note: "Date range adjusted to available data (Jan 2022 – Aug 2024)" |

**Warning banner anatomy:**

```css
.filter-warning {
    background: rgba(255, 186, 8, 0.1);   /* TRAFFIC_AMBER tint */
    border-left: 3px solid #FFBA08;
    padding: 8px 16px;
    font-size: 12px;
    color: #FFBA08;
    margin-bottom: 8px;
}
```

---

## 4.4 · Partial-Data Fallback

Some charts have minimum data requirements. When data is available but insufficient for a specific visualization technique, the chart degrades gracefully to a simpler form:

| Chart | Minimum Data | Fallback If Under Minimum |
|---|---|---|
| T-04 Violin (weekly distribution) | 30 rows per day-of-week | Boxplot instead of violin |
| T-11 Ridgeline (16 distributions) | 50 rows per road | Bar chart of means (simpler, always works) |
| A-02 Calendar Heatmap | 90 days of data | Monthly bar chart of average PM2.5 |
| A-15 Pairplot | 100 rows minimum | Correlation matrix table (tabular fallback) |
| T-13 Radar overlay | 1 area selected | Radar renders with single polygon + note: "Select 2+ areas to compare" |

**Fallback notification:** When a degraded fallback renders, a small `ℹ` badge appears in the chart title area. Hovering the badge shows: `"Full visualization requires [N] rows. Showing simplified view for [current row count] rows."` — SURFACE_3 tooltip, TEXT_MUTED.

---

## 4.5 · Stale-Cache Handling

When `@st.cache_data` TTL has expired and data has not yet been refreshed, or when the raw data file has been updated since the last cache population:

**Stale data indicator:**

```python
def check_data_freshness(df: pd.DataFrame) -> bool:
    """Returns True if data is fresh, False if stale."""
    cache_timestamp = st.session_state.get("data_load_time")
    if cache_timestamp is None:
        return True
    return (datetime.now() - cache_timestamp).seconds < STALE_THRESHOLD_SECONDS  # default: 300
```

When `check_data_freshness()` returns False:

- Filter strip gains a `⟳ Refresh` button on the right side (always visible when stale)
- Each KPI card gains the stale-data corner badge (see Part 2.2)
- A non-blocking banner appears below the hero section: `"ⓘ Displaying data from [HH:MM]. Refresh to load latest."`

The platform **does not** automatically refresh stale data — automatic refreshes are jarring and can interrupt the analyst's review. The analyst initiates the refresh.

---

## 4.6 · Corrupted-Data Fallback

If `load_clean_data()` raises an exception, or if data validation fails (missing required columns, dtype mismatches, out-of-range values), the platform renders a full-page error state instead of a partially-broken dashboard:

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  BANGALORE URBAN INTELLIGENCE PLATFORM                              │
│                                                                     │
│  ⚠  Data Load Error                                                │
│     (TRAFFIC_CRIMSON, 20px weight 600)                              │
│                                                                     │
│  The platform could not load the traffic dataset.                   │
│  The data file may be missing, corrupted, or in an unexpected       │
│  format.                                                            │
│                                                                     │
│  Technical detail: [error message, TEXT_MUTED, monospace, 11px]    │
│                                                                     │
│  Expected file: data/processed/traffic_clean.parquet               │
│  Expected columns: Date, Area_Name, Road_Name, [13 more...]        │
│                                                                     │
│  Recovery: Verify the data file exists and re-run the              │
│  preprocessing pipeline. See README.md for data setup.             │
│                                                                     │
│  [ View Setup Documentation ]   [ Report Issue ]                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Critical rule:** The platform never renders a partially-loaded state where some KPI cards show real values and others show errors. Either the data loads completely and all components render, or the platform shows the full-page error state. Partial success is more dangerous than total failure because it creates false analytical confidence.

---

## 4.7 · Low-Sample-Size Warning UX

The traffic dataset contains 8,936 rows across 16 roads. Heavily filtered views (single road + short date range) can yield as few as 50–100 rows. Statistical conclusions from such subsets require explicit analyst caution.

**Sample size indicator:**

Every chart renders a row count indicator in its bottom-right corner — always visible, not only on hover:

```
Format: "Datapoints = 1,247"
Position: bottom-right corner of chart_container
Font: 10px, TEXT_MUTED, opacity 0.8
Color: TEXT_MUTED (neutral always - even at very low datapoint counts)
```

**Low-sample warning trigger (Datapoints < 200):**

When the filtered row count drops below 200, the row count indicator changes treatment:

```
"Datapoints = 84 warning"
Color: TRAFFIC_AMBER
Tooltip: "Small sample. Statistical patterns may not be representative."
```

Below 50 rows, a warning banner replaces the chart:

```
"Insufficient data for visualization (Datapoints = [count]).
   Select a wider date range or remove road/area filters."
```

---

## 4.8 · Reset-Filter Recovery Flows

Every fallback state includes a clearly-labeled recovery action. The recovery logic must clear only the minimal filters needed — not blunt "reset everything" behavior that erases deliberate analyst configuration.

**Recovery action hierarchy:**

1. `"Remove Date Filter"` — clears only the date range, preserves area/road filters
2. `"Remove Area Filter"` — clears only area selection, preserves date/road
3. `"Remove Road Filter"` — clears only road selection
4. `"Reset All Filters"` — full reset to defaults (last resort, always available)

**Implementation:**

```python
def recovery_action_buttons(active_filters: list[str]) -> None:
    """
    Render targeted recovery buttons based on which filters are active.
    Prioritizes least-destructive recovery first.
    """
    cols = st.columns(len(active_filters) + 1)
    for i, filter_key in enumerate(active_filters):
        with cols[i]:
            if st.button(f"Remove {filter_key.replace('_', ' ').title()}"):
                del st.session_state[filter_key]
                st.rerun()
    with cols[-1]:
        if st.button("Reset All"):
            clear_all_filters()
            st.rerun()
```

---

# PART 5 — ML EXPERIENCE + PREDICTION UX ADDON

---

## 5.1 · ML UX Philosophy: Trustworthy Intelligence, Not Magic

The platform's current architecture is descriptive and diagnostic — it reveals what happened. Future ML layers will add predictive and prescriptive capabilities. This section defines the UX framework that governs how those ML outputs are displayed when they are added.

The fundamental principle: **ML outputs are advisory, not authoritative.** The UX must communicate this consistently. An analyst must never mistake a model prediction for a measured fact. The visual language for ML-derived content is deliberately differentiated from the language of observational data.

**Two forbidden ML UX patterns:**

1. **Confidence theater:** Displaying a prediction with 94.7% confidence as if high confidence means accuracy. Confidence intervals must always communicate the *range* of plausible outcomes, not just a false-precision point estimate.
2. **Black-box urgency:** Showing a "HIGH RISK" ML alert with no explanation of what features drove it. Every high-severity ML output must include an accessible explanation path.

---

## 5.2 · Forecasting UX

When time-series forecasting is added (e.g., next-7-days congestion forecast, next-week AQI forecast), it overlays on existing temporal charts (T-03 Stream Graph, A-05 Persistence Series).

**Forecast overlay visual specification:**

```
Observed historical data:
  Line style:     solid, full opacity (matches existing chart encoding)
  
Forecast range (confidence interval):
  Style:          shaded band (not a line) from lower to upper bound
  Fill color:     [Identity accent color] at 15% opacity
  Band label:     "80% Confidence Interval" — 10px, TEXT_MUTED, positioned on band
  
Forecast centerline (point estimate):
  Line style:     dashed, 1.5px, [Identity accent color] at 70% opacity
  Marker:         None (dashed line already distinguishes from observed)
  
Forecast/observed boundary:
  Vertical line:  1px, BORDER_1 dashed
  Label:          "Forecast →" — 10px, TEXT_MUTED, positioned above line
```

**Hover behavior on forecast elements:**

When hovering a point within the forecast band:

```
Tooltip fields:
  Date: [YYYY-MM-DD]
  Forecast Value: [point estimate, formatted]
  80% CI: [lower bound] – [upper bound]
  Model: [model name/version, e.g., "SARIMA v2.1"]
  Training data: [last training date]
```

**Forecast accuracy decay indicator:**

As the forecast extends further into the future, the confidence band widens. Additionally, a visual "reliability fade" is applied: the centerline opacity reduces from 70% at Day 1 to 30% at Day 7. This visually communicates that near-term forecasts are more reliable than far-term ones — without requiring any text explanation.

---

## 5.3 · Prediction Panel Architecture

When ML model outputs are surfaced as standalone insights (not overlaid on existing charts), they render in a dedicated **Prediction Panel** component — visually distinct from observational insight panels.

**Prediction panel visual treatment:**

```
┌─────────────────────────────────────────────────────────────────────┐
│ ◈  ML PREDICTION                                         [i] Info   │  ← Header: SURFACE_2 bg, left border: TRAFFIC_SLATE
│                                                                     │
│  Congestion Level Forecast — Tomorrow, Wednesday 21 May             │
│  (TEXT_PRIMARY, 14px weight 600)                                    │
│                                                                     │
│  ████████████████████░░░░░░   HIGH PROBABILITY                      │  ← Confidence bar
│  Koramangala · Electronic City · Whitefield                         │
│  (TEXT_MUTED, 12px — "top affected areas per model")               │
│                                                                     │
│  ▶ Why this prediction?  (expandable SHAP explanation row)          │
│                                                                     │
│  Model: Gradient Boost Ensemble  |  Trained: 2024-08-01            │  ← Footer metadata
│  (TEXT_MUTED, 10px monospace)                                       │
└─────────────────────────────────────────────────────────────────────┘
```

**Differentiating signals:** The left border of prediction panels is `TRAFFIC_SLATE` (#58A6FF), not TRAFFIC_CRIMSON. This deliberately distinguishes prediction panels from severity-coded operational content. Severity crimson = measured fact requiring attention. Slate blue = model-derived insight, advisory in nature.

---

## 5.4 · SHAP Explainability Systems

When SHAP (SHapley Additive exPlanations) values are available for a model prediction, the `▶ Why this prediction?` control reveals a compact SHAP waterfall visualization:

**SHAP waterfall layout (inside expandable section):**

```
Base rate: 62.3 congestion index
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Incident Reports:       +12.4 ████████████████ [CRIMSON]
Time of Day (Peak):     +8.7  ████████████     [CRIMSON]
Road Capacity:          +5.2  ███████          [CRIMSON]
Weather (Rain):         +3.1  ████             [AMBER]
Public Transport:       -2.8        █████      [TEAL]
Signal Compliance:      -1.4        ███        [TEAL]

                        = 87.3 congestion index
                           ▲ 25.0 above base rate
```

**SHAP waterfall styling:**

- Positive contributions (pushing prediction up): TRAFFIC_CRIMSON bars
- Negative contributions (pulling prediction down): TRAFFIC_TEAL bars
- Base rate horizontal line: BORDER_1
- Final value: TEXT_PRIMARY + severity badge
- Feature names: TEXT_MUTED, 12px
- Value amounts: monospace, 12px, TEXT_PRIMARY

**Analyst guidance rule:** Below the SHAP waterfall, a single sentence is rendered in TEXT_MUTED at 11px: `"Feature contributions show relative model influence — not causal relationships."` This preempts misinterpretation of SHAP values as causal claims.

---

## 5.5 · Anomaly Investigation UX

When an anomaly detection layer is active, anomalous data points are flagged within existing charts rather than surfaced in a separate anomaly view.

**In-chart anomaly flagging:**

- Anomalous data points receive an additional marker layer: hollow circle outline, 2px, TRAFFIC_AMBER
- On hover: standard tooltip + additional field: `"⚠ Anomaly Score: [score]"` in amber
- The flagging is always opt-in, not default — a toggle in the filter strip: `"Show Anomaly Flags ☐"`

**Anomaly investigation panel (triggered by clicking a flagged point):**

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚠ ANOMALY DETECTED                                 [× Dismiss] │
│  Koramangala · 2023-11-14 · 17:30                               │
├─────────────────────────────────────────────────────────────────┤
│  Observed value:       PM2.5 = 387.4 µg/m³                      │
│  Expected range:       142–218 µg/m³ (±2σ for this period)      │
│  Anomaly severity:     ████████████  EXTREME                    │
├─────────────────────────────────────────────────────────────────┤
│  Possible contributing factors:                                  │
│   · Atmospheric pressure: 1008 hPa (stagnation-prone range)    │
│   · Wind speed: 0.3 m/s (near-zero — minimal dispersion)       │
│   · Visibility: 0.8 km (below stagnation threshold of 1.0)     │
├─────────────────────────────────────────────────────────────────┤
│  [ View Surrounding Period ]   [ Compare to Similar Events ]    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5.6 · Model Health and Reliability Indicators

When ML models are deployed, their operational health must be surfaced without cluttering the primary analytical view.

**Model health location:** The platform's header area includes a compact model health badge, visible only when ML features are active:

```
TRAFFIC INTELLIGENCE  |  [◉ Models: Healthy]   ← Top-right of hero section
                                                  ◉ = TRAFFIC_TEAL when healthy
                                                  ◉ = TRAFFIC_AMBER when degraded
                                                  ◉ = TRAFFIC_CRIMSON when stale/failed
```

Clicking the badge opens a Model Health Panel:

```
Model           | Version | Last Trained   | Accuracy    | Status
Congestion FC   | v2.1    | 2024-08-01     | MAPE: 8.3%  | ● Healthy
AQI Forecast    | v1.4    | 2024-07-15     | RMSE: 24.1  | ● Healthy
Anomaly Det.    | v3.0    | 2024-06-20     | F1: 0.84    | ⚠ Degraded
```

**Degraded model behavior in charts:** When a model's status is DEGRADED, its outputs are rendered at 50% opacity with a `"Model performance degraded — use outputs with caution"` tooltip. The prediction panel header acquires an AMBER left border instead of SLATE.

**Stale model behavior:** When a model has not been retrained in > 90 days (configurable), outputs are rendered with the same stale-data treatment as stale observational data: a `⟳` corner badge and amber border.

---

# PART 6 — ACCESSIBILITY + READABILITY ADDON

---

## 6.1 · Contrast and Color Accessibility Governance

**Minimum contrast requirements (WCAG 2.1 AA as baseline, enterprise AA+ as target):**

| Element Type | Minimum Contrast Ratio | Target |
|---|---|---|
| Body text (TEXT_MUTED on SURFACE_1) | 4.5:1 | 5.5:1 |
| Chart axis labels (TEXT_MUTED on SURFACE_1) | 3.0:1 (large text exception) | 4.0:1 |
| KPI values (severity colors on SURFACE_1) | 4.5:1 | 7:1 |
| Filter widget labels | 4.5:1 | 5.0:1 |
| Navigation card text | 4.5:1 | 5.5:1 |
| Focus ring (TRAFFIC_SLATE on BG) | 3.0:1 | 4.5:1 |

**Verification requirement:** All contrast values must be verified using the WCAG contrast algorithm against the actual token values defined in `config/theme.py`. Not verified against approximations.

---

## 6.2 · Colorblind-Safe Chart Encoding

The traffic area palette (8 colors) and AQI severity scale (6 colors) both include colors that can be confused by analysts with red-green colorblindness (the most common form, affecting ~8% of males).

**Colorblind safety rules:**

1. **Never rely on color alone** for encoding categorical distinctions in charts with more than 4 categories. Supplement with labels, patterns, or shape encoding.

2. **T-03 Stream Graph (8-area encoding):** Each stream area is labeled directly at the right edge with its area name — the label, not the color, is the primary identifier. Color serves as a visual grouping aid, not the sole encoding.

3. **AQI severity scale:** The scale runs Good (green) → Severe (purple). The green-to-yellow transition is the most problematic for red-green colorblindness. Supplement AQI category encoding in the calendar heatmap (A-02) with a visible category label on hover tooltip. Consider adding a light diagonal hatching pattern to "Good" cells to distinguish them from "Satisfactory" without relying solely on hue shift.

4. **T-05 Quadrant Scatter:** Quadrant labels (Critical Overload, Operational Baseline, etc.) appear as permanent text annotations, not only on hover. Color supports the quadrant labeling but is never the sole differentiator.

5. **TRAFFIC_AMBER (#FFBA08) and TRAFFIC_TEAL (#2EC4B6):** This warning/safe pairing is distinguishable by all major colorblindness types due to the strong difference in both hue and lightness. Preferred over red/green pairings for severity vs. safe-state distinction.

---

## 6.3 · Readable Font Minimums

**Absolute font size floors:**

| Context | Minimum Font Size | Rationale |
|---|---|---|
| Chart axis tick labels | 10px | Below this, labels are unreadable without zooming |
| Tooltip text | 11px | Tooltips are small — 10px is too tight for multi-line content |
| KPI sublabels | 11px | Must be scannable across the metric strip |
| Caption / chart annotation text | 11px (regular) / 9px (extreme space constraint only) | 9px only for axis value markers on dense heatmaps |
| Navigation card body | 12px | Not reading-speed content, but must be decipherable at a glance |
| Insight panel body | 13px | This is primary interpretation text — must be comfortable at reading speed |
| KPI values | 24px minimum (compact) | KPI values that cannot be read instantly defeat their purpose |

**Line height minimums for multi-line text:**

- Insight panel body: 1.6 line-height — comfortable sustained reading
- Tooltip multi-line: 1.4 line-height — compact but clear
- Chart annotations: 1.3 line-height — tight, but annotations are usually 1–2 lines

---

## 6.4 · Reduced-Motion Behavior

Some analysts use operating system or browser reduced-motion settings (relevant for vestibular disorders and motion sensitivity). All CSS animations must respect this setting:

```css
@media (prefers-reduced-motion: reduce) {
    .skeleton { animation: none; background: #2D333B; }           /* Static skeleton, no shimmer */
    * { transition-duration: 0.01ms !important; }                 /* Kill all transitions */
    .chart-appear { animation: none; opacity: 1; }               /* Skip chart reveal animations */
    .nav-card-arrow { transform: none !important; }               /* No arrow movement */
    .kpi-gauge circle { transition: none; }                       /* No gauge fill animation */
}
```

**Reduced-motion behavior intent:** The platform must be *fully functional* in reduced-motion mode. No interaction should require animation to communicate its state change. Color, border, and content changes are sufficient fallbacks for all animation-dependent states.

---

## 6.5 · Keyboard Navigation Considerations

The platform's primary interaction model is mouse-based (Plotly charts, Streamlit widgets). However, critical navigation paths must be keyboard-accessible:

**Tab order sequence (per page):**

1. Filter strip controls (left to right)
2. "Reset All" button
3. KPI cards (left to right, if drilldown-capable)
4. Chart fullscreen toggles
5. Collapsible section headers
6. "What This Means" expander
7. "Investigate Further" nav card
8. Page tab navigation

**Focus ring specification:**

```css
:focus-visible {
    outline: 2px solid #58A6FF;    /* TRAFFIC_SLATE */
    outline-offset: 2px;
    border-radius: 4px;            /* Matches component border-radius */
}

:focus:not(:focus-visible) {
    outline: none;                 /* Suppress focus ring on mouse click */
}
```

**Plotly chart keyboard access:** Plotly's built-in keyboard navigation (arrow key point selection, Enter to drill down) is preserved. Do not override Plotly's native `tabIndex` handling on `st.plotly_chart()` renders.

---

## 6.6 · Cognitive Load Safeguards

**Information density limits:**

- No page renders more than 4 KPI cards in the primary row (8 is the theoretical maximum including secondary row — 4+4)
- No chart displays more than 8 simultaneous categorical series without hover-isolation dimming
- No tooltip shows more than 6 data fields
- No collapsible section header uses more than 6 words
- No page-level annotation appears without a minimum of 48px spatial separation from adjacent annotations

**Long-session UX protections:**

After an extended session (> 90 minutes of uninterrupted use — tracked via `st.session_state["session_start_time"]`):

```
A non-blocking notification bar appears below the filter strip:
"You've been reviewing this dashboard for 90+ minutes. Refresh data before final decisions."
[Dismiss]
```

This is shown once per session and dismissed permanently when the analyst clicks Dismiss. It does not interrupt the workflow — it is informational, not blocking.

**Visual fatigue reduction:** Dark theme, muted typography, and the low-saturation surface architecture are themselves cognitive load safeguards. The explicit rule: resist pressure to add more visual variety to "liven up" the dashboard. Every additional color, animation, or component adds cognitive weight. The current architecture is calibrated.

---

# PART 8 — ENTERPRISE MICROINTERACTION ADDON

---

## 8.1 · Microinteraction Philosophy

Microinteractions are the platform's conversational layer — the tiny responses the interface gives to analyst actions that confirm: *I heard you, here's what happened, here's what's happening now.*

The BUIP is an operational intelligence tool. Its microinteractions must feel like a precision instrument — responsive, deliberate, proportional. Every animation must earn its existence by communicating something that static visual states cannot communicate alone.

**The operational interaction standard:** If an animation makes the platform feel *snappier* or *clearer* without calling attention to itself, it belongs. If an analyst notices the animation itself (rather than the information it delivers), it does not belong.

---

## 8.2 · Hover Precision Systems

**Hover intent delay:** Hover effects on chart containers and KPI cards are delayed by 80ms. This prevents accidental hover states from firing when the analyst is moving the mouse across the interface to reach a target elsewhere. 80ms is above the threshold of accidental hover (< 50ms) but below the threshold of noticeable delay (> 150ms).

```css
.kpi-card, .chart-container, .nav-card {
    transition-delay: 80ms;    /* hover intent delay */
    transition-property: background, border-color, transform;
    transition-duration: 150ms;
    transition-timing-function: ease;
}

/* Remove delay on mouse leave — unhover should be immediate */
.kpi-card:not(:hover), .chart-container:not(:hover) {
    transition-delay: 0ms;
}
```

---

## 8.3 · Selection Emphasis and Focus Hierarchy

When a drilldown selection is active, the entire page shifts to communicate the selection hierarchy visually — not just the selected element.

**Selection emphasis cascade:**

1. **Selected element:** Full opacity (1.0), selection border, selection badge — elevated
2. **Sibling elements (same chart):** Reduced to 30% opacity — clearly secondary
3. **Other charts on same page:** Unchanged opacity but acquire a subtle golden filter badge: `"Filtered by: [selection]"` — acknowledging the cross-chart influence without reducing their readability
4. **KPI strip:** Values update to reflect the filtered subset + a persistent "Selection Active" badge appears in the filter strip

This cascade ensures the analyst always knows: *this selection is affecting everything I see, not just the chart I clicked.*

---

## 8.4 · Focus Transitions

When the analyst tabs to a new interactive element (keyboard navigation), the focus transition is distinct from the hover transition — it must be immediately noticeable without a mouse event:

```css
:focus-visible {
    outline: 2px solid #58A6FF;
    outline-offset: 2px;
    /* Subtle background pulse — one time only, not repeating */
    animation: focus-pulse 0.4s ease-out forwards;
}

@keyframes focus-pulse {
    0%   { box-shadow: 0 0 0 0 rgba(88, 166, 255, 0.4); }
    100% { box-shadow: 0 0 0 6px rgba(88, 166, 255, 0); }
}
```

The pulse fires once (not infinitely) — it announces focus, then settles into the steady outline state.

---

## 8.5 · Interaction Feedback Timing Standards

Every discrete interaction class has a defined timing budget:

| Interaction | Feedback Type | Timing | Max Duration |
|---|---|---|---|
| Button press | CSS scale compress (0.98) | 60ms ease | 60ms |
| Hover enter | Background/border change | 150ms ease | 150ms |
| Hover leave | Return to default | 100ms ease | 100ms (faster exit than enter) |
| Tab focus | Focus ring + pulse | 400ms (pulse), steady thereafter | 400ms |
| Drilldown selection | Scale compress + re-render | 60ms + re-run time | 60ms (visual) |
| Filter change | Progress bar on filter strip | 2s animated sweep | Until re-run completes |
| Chart appear (first load) | Fade in from skeleton | 300ms ease | 300ms |
| Collapsible expand | Height 0 → content, opacity 0 → 1 | 200ms ease-out | 200ms |
| Collapsible collapse | Height → 0, opacity → 0 | 150ms ease-in | 150ms (collapse faster than expand) |
| Tooltip appear | Opacity 0 → 1 | 100ms | 100ms |
| Tooltip dismiss | Opacity 1 → 0 | 60ms | 60ms |

**The collapse-faster-than-expand rule:** When the analyst collapses a section, they have made a deliberate decision to move on. Slow collapse animations feel like the interface is resisting the decision. Collapse at 150ms; expand at 200ms.

---

## 8.6 · Motion Restraint System

**The animation budget:** Each page has a conceptual "animation budget" — the total perceptible motion that should occur during normal use. The budget is consumed by:

- Chart skeleton shimmer (continuous — always consuming budget)
- Hover state transitions (intermittent)
- Collapse/expand (occasional)
- Drilldown transitions (infrequent)

**Budget rules:**

1. No more than 3 simultaneous animated elements at any given moment
2. Skeleton shimmer is the only *continuous* animation — all others are triggered
3. When a re-run is in progress (filter strip progress bar active), suppress all other hover-triggered animations — do not layer two active motion signals simultaneously
4. Victory/completion animations are prohibited — no confetti, no "success!" bounce. Operational intelligence platforms confirm success through data accuracy, not visual celebration.

---

## 8.7 · Contextual Interaction Feedback

Beyond transitions, the platform uses *contextual copy* as a microinteraction layer — small text changes that confirm the analyst's action was received:

| Interaction | Before | After |
|---|---|---|
| Click "Reset All Filters" | "Reset All" | "✓ Filters Reset" (1.5s, then returns to "Reset All") |
| Export PNG | "⬇ PNG" | "✓ Downloaded" (1.5s, then returns) |
| Click drilldown on chart | Normal state | "Selection Active" badge appears in filter strip |
| Open Advanced Lab for first time | "Advanced Lab" tab | `lab_gate()` modal renders |

These text confirmations are rendered via `st.session_state` flags and `time.sleep(1.5)` with `st.rerun()`. They are brief (1.5s), non-blocking, and require no modal or toast library.

---

# PART 9 — UX GOVERNANCE + IMPLEMENTATION SAFETY ADDON

---

## 9.1 · Governance Philosophy

The visual and interaction quality of an enterprise analytics platform degrades through entropy, not catastrophe. No single implementation decision breaks the platform — it is the accumulation of small shortcuts, extra charts, inconsistent spacing values, and "just one more color" decisions that transforms a precision analytical instrument into a cluttered, distracting tool.

This section defines the governance systems that prevent that entropy. These are not aspirational guidelines — they are implementation safety rules. Any implementation that violates a rule in this section must be corrected before the page is considered complete.

---

## 9.2 · Forbidden UI Patterns

The following patterns are explicitly prohibited. Their presence in any page module, component, or CSS file is grounds for implementation rejection:

**Layout prohibitions:**

- `st.columns([1, 1, 1])` for charts (3-column chart grids are never permitted)
- Fixed pixel values in column definitions (`st.columns([400, 600])` is forbidden — use ratio-based splits only)
- More than 2 charts rendered eagerly (outside expanders) on a single page
- Any chart rendering inside a `st.sidebar()`

**Visual prohibitions:**

- `box-shadow` on any element with a dark background (creates visual artifacts)
- `border-radius > 12px` on any container (excessive rounding breaks the operational aesthetic)
- Gradient fills as chart backgrounds
- Any color not defined in `config/theme.py` used in any component, chart, or CSS injection
- `opacity: 0` as a visibility toggle without accompanying `pointer-events: none` (creates invisible clickable regions)

**Typography prohibitions:**

- Any font not in the approved Inter + JetBrains Mono stack
- `font-size < 10px` for any visible text
- `font-weight > 800` (weight 800 is used only for CRITICAL KPI values — nothing else gets this weight)
- `text-transform: uppercase` on body text or chart captions (uppercase is reserved for section headers and chart titles only)

**Interaction prohibitions:**

- `st.session_state` reads or writes inside chart render functions (charts receive pre-computed data only)
- `time.sleep()` calls without a paired `st.rerun()` (creates unresponsive states)
- Custom spinner implementations that overlay the entire page (filter strip progress bar only)
- `st.balloons()` or any Streamlit celebration effect

---

## 9.3 · Anti-Clutter and Anti-Bloat Rules

**Chart count limits:**

| Page Type | Maximum Charts (eager + lazy combined) | Maximum Charts Eagerly Rendered |
|---|---|---|
| Standard analytical page (P1–P5) | 4 charts maximum | 2 charts maximum |
| Advanced Lab (P6) | 4 charts maximum | 1 chart maximum (others behind expanders) |
| Any single page | Never exceed 4 | Never exceed 2 |

**Annotation limits:**

| Chart Type | Maximum Visible Annotations Simultaneously |
|---|---|
| Any chart | 3 annotations (callout boxes, labels, reference line labels combined) |
| Reference lines | 2 per chart maximum (e.g., mean line + threshold line — not 4 threshold lines) |
| Drilldown-active annotation (selection active) | 1 per chart (the selection badge only) |

**KPI strip limits:**

- Primary row: maximum 4 KPI cards
- Secondary row: maximum 4 KPI cards
- Total per page: 8 KPI cards maximum — never exceed this

**Color limits per chart:**

| Data Dimension | Maximum Colors |
|---|---|
| Single-metric charts (no categories) | 1 data color + optional severity gradient |
| Categorical (areas, roads) | 8 maximum (the defined area palette) — always use the canonical palette |
| Combined encoding (area × severity) | Use area color for hue + severity for saturation/opacity — not separate color dimensions |

---

## 9.4 · Spacing Consistency Enforcement

**The zero-tolerance spacing rule:** No margin, padding, gap, or spacing value may appear as a hardcoded pixel value in any page module or component. Every spacing value must reference a token from `config/theme.py`.

**Spacing token audit procedure:**

```bash
# Search for spacing violations in codebase:
grep -rn "margin.*px\|padding.*px\|gap.*px" dashboards/ --include="*.py" \
  | grep -v "SPACING_"
# Any result from this command is a violation requiring correction.
```

**Permitted spacing patterns:**

```python
# Correct:
st.markdown(f"<div style='margin-top: {SPACING_LG}px'></div>", unsafe_allow_html=True)

# Forbidden:
st.markdown("<div style='margin-top: 24px'></div>", unsafe_allow_html=True)
```

---

## 9.5 · Interaction Consistency Standards

**Hover consistency mandate:** If element type X shows a hover border brightening on Page 1, it must show the same hover border brightening on all pages. Hover behaviors are defined by component, not by page. The component owns its state specification.

**Navigation consistency mandate:** Every page that is not Page 1 must have a `nav_card()` pointing to the next page in the analytical narrative. No page is a dead end.

**Drilldown consistency mandate:** If a chart type supports drilldown (e.g., area click in T-05 Quadrant Scatter), all charts of that type across the platform support drilldown with the same interaction pattern. There are no charts in the same category where some are drilldown-capable and others are not — without explicit architectural justification.

---

## 9.6 · UX Review Checklist (Implementation Completion Gate)

This checklist must be completed for every page before it is considered implementation-complete. A page that cannot pass this checklist is not ready for review.

**Visual Integrity:**
- [ ] All colors verified against `config/theme.py` token definitions — no hex values outside theme
- [ ] All spacing values reference tokens — no hardcoded pixel values in page modules
- [ ] Maximum 2 charts rendered eagerly — all others behind `st.expander()`
- [ ] No `box-shadow` declarations in injected CSS
- [ ] No font size below 10px on any visible element

**Component Correctness:**
- [ ] Every chart wrapped in `chart_container()` — no bare `st.plotly_chart()` calls
- [ ] Every chart has a `caption` parameter with a one-line analytical insight
- [ ] Every KPI card has correct `severity` parameter (CRITICAL/WARNING/SAFE/NEUTRAL)
- [ ] Every page has `hero_section()` with a subtitle framing the analytical question
- [ ] Every page (except P6) has a `nav_card()` pointing to the next page

**State Completeness:**
- [ ] Loading state (skeleton) defined and tested for all KPI cards and hero chart
- [ ] Empty state tested: set filters to return zero rows — verify empty state panel renders
- [ ] Error state tested: verify `load_clean_data()` error shows full-page error state
- [ ] Drilldown selection: verify selection badge renders, `× Clear` button clears state correctly
- [ ] Low-sample warning: tested with filtered row count < 200

**Interaction Quality:**
- [ ] Filter strip progress bar visible during re-run (test with artificial `time.sleep(1)`)
- [ ] `× Clear` drilldown control functions on all drilldown-capable charts
- [ ] Collapsible sections are collapsed by default
- [ ] Insight panel is collapsed by default
- [ ] Hover state visible on KPI cards (manual mouse test)

**Accessibility:**
- [ ] All text contrast ratios verified (use browser devtools accessibility checker)
- [ ] Focus ring visible on Tab-key navigation through page controls
- [ ] Reduced-motion: test with OS reduced-motion setting — verify no animation failures
- [ ] Font sizes floor verified — no text below 10px

**Export Readiness:**
- [ ] PNG export from chart fullscreen mode produces correctly labeled output with filter footer
- [ ] PDF export includes this page's charts (if page is in export scope)
- [ ] Dark-mode export color remapping applied — charts legible on white background

---

## 9.7 · Enterprise Quality Gates

**Gate 1 — Visual Consistency Review**  
Reviewer opens all 12 pages in sequence. Screenshots every page. Compares KPI strip heights, hero section heights, and chart proportions for uniformity. Any page where the hero section is visually larger or smaller than others requires investigation.

**Gate 2 — Filter State Stress Test**  
Reviewer applies the most extreme valid filter combination (single road, single month, single area). Verifies: no blank charts, no broken layouts, appropriate empty/low-sample states, row count indicator shows correct n.

**Gate 3 — Navigation Flow Test**  
Reviewer begins at P1 of each dashboard and navigates exclusively via `nav_card()` through all 6 pages. Verifies no dead ends, no broken navigation targets, no pages without a nav card.

**Gate 4 — Cross-Dashboard Switch Test**  
Reviewer applies filters on Traffic Dashboard, switches to AQI Dashboard, switches back to Traffic Dashboard. Verifies Traffic filters were preserved during the round trip.

**Gate 5 — Responsive Breakpoint Test**  
Reviewer tests at exactly 1280px width (laptop), 1024px width (minimum tablet), and 1920px (desktop). Verifies: no horizontal scroll at any tested width, KPI strips readable at all widths, charts not deformed.

**Gate 6 — Advanced Lab Isolation Test**  
Reviewer navigates directly to Tab 06 (Advanced Lab) without visiting P1–P5. Verifies: lab gate renders correctly on first visit, T-13 radar and A-15 pairplot render correctly with full data, no errors from missing drilldown state.

---

## 9.8 · Preventing "Just One More Chart" Syndrome

The most insidious threat to dashboard quality is incremental scope creep — each individually defensible addition that collectively degrades the analytical experience.

**Pre-addition evaluation questions (must be answered YES for all four before any new chart is added):**

1. **Does this chart answer a question the existing charts cannot answer?** (Not "this chart also shows X" — "this chart *only* shows X")
2. **Has the page budget been consulted?** (The receiving page must have a chart slot available — maximum 4 charts per page including new addition)
3. **Does this chart have a defined hero-or-supporting role?** (New charts cannot be added as "bonus context" — they must have a place in the visual hierarchy)
4. **Has a chart been removed or promoted to Advanced Lab to make room?** (Net chart count at the platform level should not exceed 30 without architectural review)

**The Advanced Lab redirect rule:** If a proposed new chart is exploratory, multi-dimensional, or high-density — it belongs in the Advanced Lab (Tab 06), not in P1–P5. The Advanced Lab exists precisely to absorb analytical complexity without contaminating the operational clarity of the main pages.

---

*Document: SUAQIS Enterprise UX Architecture Addon*  
*Platform: Bangalore Urban Intelligence Platform — Traffic + AQI Dashboards*  
*Document Role: Production Refinement Layer · Implementation Precision Guide · Enterprise UX Expansion*  
*Additive To: SUAQIS_Visual_UX_Architecture_Blueprint.md · bangalore_implementation_architecture.md*  
*Status: Production Enhancement Specification · Implementation Ready*  
*Sections Covered: 9 Parts · Viewport Composition · Component States · Loading UX · Fallback Architecture · ML Experience · Accessibility · Export Systems · Microinteractions · UX Governance*  
*Replaces: Nothing. Extends: Everything.*
