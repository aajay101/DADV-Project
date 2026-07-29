# Publication Assets

Design specifications, screenshot plans, and publication checklist for the Bangalore Urban Intelligence Platform.

---

## Deliverable 1: Repository Banner

**File:** `assets/banner.png`
**Size:** 1280 x 320 px (GitHub recommended banner ratio)

### Design Specification

```
Background:     #0D1117 (GitHub dark) or #161B22 (slightly lighter)
Left zone:      Project title + tagline
Right zone:     Minimal abstract illustration
```

### Layout

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│   BANGALORE URBAN                 ╭─────────╮                    │
│   INTELLIGENCE PLATFORM          │  ┌─┐ ┌─┐ │                    │
│                                  │  │ │ │ │ │  ← abstract bar   │
│   Traffic · Air Quality ·        │  │ │ │ │ │    chart suggesting│
│   Decision Support               │  └─┘ └─┘ │    data analysis   │
│                                  ╰─────────╯                    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Typography

- **Title:** Inter or GitHub Sans, bold, 28–32px, white (#FFFFFF)
- **Tagline:** Inter regular, 16–18px, muted (#8B949E)
- **Tracking:** Slight letter-spacing on title for modern feel

### Illustration (Right Side)

- 3–4 vertical bars of varying heights in accent colours:
  - `#E5383B` (red — traffic)
  - `#27AE60` (green — AQI)
  - `#3498DB` (blue — analytics)
  - `#F39C12` (amber — insights)
- Bars should be slightly rounded, semi-transparent, overlapping
- No realistic charts — abstract and clean

### colours Palette

| Element | Hex | Use |
|---------|-----|-----|
| Background | `#0D1117` | Primary background |
| Title | `#FFFFFF` | Project name |
| Tagline | `#8B949E` | Subtitle text |
| Traffic accent | `#E5383B` | Bar 1, highlights |
| AQI accent | `#27AE60` | Bar 2 |
| Analytics accent | `#3498DB` | Bar 3 |
| Insights accent | `#F39C12` | Bar 4 |

### Generation Prompt (for AI image tools)

```
Dark GitHub repository banner, 1280x320, minimalist, modern tech aesthetic.
Left side: white text "BANGALORE URBAN INTELLIGENCE PLATFORM" with subtitle
"Traffic · Air Quality · Decision Support" in muted grey.
Right side: abstract vertical bar chart with 4 rounded bars in red, green,
blue, and amber on dark background #0D1117. Clean, no clutter, suitable
for a professional open-source project. Flat design, no gradients.
```

---

## Deliverable 2: Social Preview (Open Graph)

**File:** `assets/social-preview.png`
**Size:** 1280 x 640 px

### Design Specification

```
Background:     #0D1117
Layout:         Title left, visual right
```

### Layout

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│   ┌─────────────────────────┐    ┌──────────────────────────┐   │
│   │                         │    │                          │   │
│   │   🚗  🌿               │    │   Mini dashboard mockup  │   │
│   │                         │    │   showing 2x2 chart grid │   │
│   │   Bangalore Urban       │    │   with coloured accents  │   │
│   │   Intelligence          │    │                          │   │
│   │   Platform              │    │   ┌──────┐ ┌──────┐     │   │
│   │                         │    │   │ ████ │ │ ▓▓▓▓ │     │   │
│   │   Dual-dashboard        │    │   │ ████ │ │ ▓▓▓▓ │     │   │
│   │   analytical platform   │    │   └──────┘ └──────┘     │   │
│   │   for traffic and       │    │   ┌──────┐ ┌──────┐     │   │
│   │   air quality           │    │   │ ░░░░ │ │ ◆◆◆◆ │     │   │
│   │                         │    │   │ ░░░░ │ │ ◆◆◆◆ │     │   │
│   │   30 charts · 2         │    │   └──────┘ └──────┘     │   │
│   │   dashboards · 48 tests │    │                          │   │
│   │                         │    │                          │   │
│   └─────────────────────────┘    └──────────────────────────┘   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Typography

- **Title:** Bold, 36–40px, white
- **Subtitle:** Regular, 18–20px, `#8B949E`
- **Metrics:** Regular, 14–16px, `#58A6FF` (GitHub link blue)

### Visual (Right Side)

- Simplified 2x2 grid of abstract chart thumbnails
- Each thumbnail is a rounded rectangle with a subtle border (`#30363D`)
- Inside each: abstract shapes suggesting chart types
  - Top-left: vertical bars (traffic overview)
  - Top-right: heatmap grid (AQI calendar)
  - Bottom-left: scatter dots (correlation)
  - Bottom-right: line chart (trends)
- Colours from the project palette

### Generation Prompt

```
Dark social preview image for GitHub, 1280x640. Left side: white title
"Bangalore Urban Intelligence Platform" with subtitle "Dual-dashboard
analytical platform for traffic and air quality" and metrics
"30 charts · 2 dashboards · 48 tests". Right side: simplified 2x2 grid
of abstract chart thumbnails (bar chart, heatmap, scatter, line) in
red, green, blue, amber on dark background #0D1117. Professional,
modern, clean. Flat design.
```

---

## Deliverable 3: Screenshot Plan

### Screenshot 1: `traffic_overview.png`

| Field | Value |
|-------|-------|
| **Page** | Traffic Intelligence → Command Overview (T-01) |
| **Purpose** | Show the traffic scorecard with system congestion gauge and area rankings |
| **Visible UI** | T-01 Network Congestion Scorecard (hero), 2–3 support charts below, KPI strip at top |
| **Filters** | Date range: Jan 2023 – Dec 2023 (full year), Area: All zones |
| **Insight visible** | System congestion gauge showing ~68, area ranking bars with Silk Board and Marathahalli in red |
| **Crop** | Full viewport, 1440px wide |
| **Resolution** | 2880 x 1800 (2x for retina) |
| **Format** | PNG |

### Screenshot 2: `aqi_overview.png`

| Field | Value |
|-------|-------|
| **Page** | AQI Intelligence → Crisis Overview (A-01) |
| **Purpose** | Show the AQI crisis scorecard with PM2.5 burden and category distribution |
| **Visible UI** | A-01 Crisis Scorecard (hero), category distribution chart, KPI strip |
| **Filters** | Date range: Oct 2023 – Mar 2024 (winter peak), Area: All zones |
| **Insight visible** | PM2.5 burden gauge in red/orange, "Very Poor" and "Severe" categories dominant |
| **Crop** | Full viewport, 1440px wide |
| **Resolution** | 2880 x 1800 |
| **Format** | PNG |

### Screenshot 3: `traffic_quadrant.png`

| Field | Value |
|-------|-------|
| **Page** | Traffic Intelligence → Spatial Operations (T-05) |
| **Purpose** | Show the Road Priority Quadrant classifying roads by congestion vs capacity |
| **Visible UI** | T-05 Quadrant Scatter (full width), axis labels, quadrant labels |
| **Filters** | Date range: Jun 2023 – Aug 2023, Area: All zones |
| **Insight visible** | Roads in "Critical Overload" quadrant (upper-right) clearly separated |
| **Crop** | Focus on the quadrant chart, slight padding |
| **Resolution** | 2880 x 1800 |
| **Format** | PNG |

### Screenshot 4: `aqi_calendar.png`

| Field | Value |
|-------|-------|
| **Page** | AQI Intelligence → Temporal Patterns (A-02) |
| **Purpose** | Show the 3-Year Calendar Heatmap with seasonal pollution patterns |
| **Visible UI** | A-02 Calendar Heatmap (full width), colour legend, year labels |
| **Filters** | Date range: Jan 2022 – Dec 2024 (full dataset), Area: All zones |
| **Insight visible** | December–January blocks consistently dark (high PM2.5), monsoon months lighter |
| **Crop** | Full calendar heatmap with legend |
| **Resolution** | 2880 x 1800 |
| **Format** | PNG |

### Screenshot 5: `filter_panel.png`

| Field | Value |
|-------|-------|
| **Page** | Any dashboard page (e.g., Traffic Command Overview) |
| **Purpose** | Show the global filter panel with active filters applied |
| **Visible UI** | Filter panel expanded with date range, area selection, road selection, weather filter |
| **Filters** | Date: Mar 2023, Area: Koramangala + Whitefield, Weather: Clear |
| **Insight visible** | Filter pills showing active selections, charts in background responding to filters |
| **Crop** | Left sidebar filter panel + portion of main content showing chart response |
| **Resolution** | 2880 x 1800 |
| **Format** | PNG |

### Screenshot 6: `advanced_lab.png`

| Field | Value |
|-------|-------|
| **Page** | Traffic Intelligence → Advanced Lab (T-13) or AQI → Advanced Lab (A-15) |
| **Purpose** | Show the compound radar profile or pairplot matrix |
| **Visible UI** | T-13 Compound Radar (full width) with multi-axis overlay, or A-15 Pairplot matrix |
| **Filters** | Date range: Jan 2023 – Dec 2023, Area: 3 zones selected |
| **Insight visible** | Radar showing zone comparison across 6+ dimensions, or pairplot showing cross-correlations |
| **Crop** | Full chart area with lab controls visible |
| **Resolution** | 2880 x 1800 |
| **Format** | PNG |

---

## Deliverable 4: Demo GIF Storyboard

**Duration:** 20–30 seconds
**Resolution:** 1440 x 900 (or 1280 x 720 for smaller file)
**Format:** GIF or MP4 (MP4 preferred for GitHub)

### Sequence

| Time | Action | What Shows | Duration |
|------|--------|------------|----------|
| 0:00–0:02 | App launch | Streamlit loading → dashboard appears | 2 sec |
| 0:02–0:05 | Traffic Overview | T-01 Scorecard fills screen, KPI strip visible, system congestion gauge at ~68 | 3 sec |
| 0:05–0:08 | Apply filters | Mouse moves to filter panel, selects "Koramangala" area, charts update smoothly | 3 sec |
| 0:08–0:12 | Chart interaction | Click on T-05 Quadrant scatter point, investigation overlay appears, detail panel shows road info | 4 sec |
| 0:12–0:16 | Explainability | Click "?" trigger on T-09 Speed Threshold, interpretation panel slides open with plain-language explanation | 4 sec |
| 0:16–0:20 | Dashboard switching | Click "Air Quality" tab, dashboard transitions to AQI Crisis Overview, A-01 Scorecard loads | 4 sec |
| 0:20–0:26 | Advanced Lab | Navigate to AQI Advanced Lab, A-15 Pairplot matrix renders with correlations | 6 sec |
| 0:26–0:30 | Branding hold | Final frame: dashboard visible, fade to dark with project title | 4 sec |

### Recording Tips

- Use [LICEcap](https://www.cockos.com/licecap/) or [ScreenToGif](https://www.screentogif.com/) for GIF
- Use [OBS Studio](https://obsproject.com/) for MP4 (preferred)
- Set browser to 1440x900 before recording
- Clear browser cache before recording for clean load
- Use dark mode in Streamlit
- Record at 30fps for smooth animation
- Keep file under 5MB for GitHub (use MP4 if GIF is too large)

### Post-Production

- Trim any loading spinners or blank frames
- Speed up filter application slightly (1.5x) if slow
- Add subtle fade transitions between sections
- Ensure text is readable at GitHub's max display width

---

## Deliverable 7: GitHub Description

### One-Line Elevator Pitch

```
Dual-dashboard analytical platform unifying Bangalore's traffic and air quality data into 30 interactive visualisations with built-in interpretive guidance.
```

### Short Description (120 chars)

```
Bangalore Urban Intelligence Platform — 30 interactive charts unifying traffic and air quality analytics with explainability.
```

### Medium Description (350 chars)

```
A dual-dashboard analytical platform that transforms raw Bangalore traffic and air quality data into 30 interactive visualisations across 12 pages. Features deterministic state management, data governance with fingerprint-based cache invalidation, and a pre-authored explainability engine that interprets every chart for non-technical decision-makers. Built with Streamlit, Plotly, and Pandas.
```

### Full Description (for GitHub About)

```
Bangalore Urban Intelligence Platform

A dual-dashboard analytical platform unifying traffic and air quality intelligence for Bangalore's 13 million residents.

30 interactive visualisations · 12 analytical pages · 48 automated tests

Features:
- Traffic Intelligence Dashboard — congestion patterns, speed thresholds, road burden, multi-dimensional profiling
- Air Quality Intelligence Dashboard — PM2.5 trends, seasonal patterns, weather correlations, atmospheric regimes
- Explainability Engine — per-chart interpretation, misinterpretation warnings, glossary, human-impact translations
- Data Governance — import validation, schema fingerprinting, synthetic-data detection, atomic rollback
- Deterministic State Engine — Redux-inspired reducers with typed actions and invalidation plans

Built with Python, Streamlit, Plotly, and Pandas.
```

---

## Deliverable 8: GitHub Topics

### Primary Topics (high discoverability)

```
streamlit
plotly
python
dashboard
data-visualization
urban-analytics
```

### Secondary Topics (niche discoverability)

```
traffic-analysis
air-quality
interactive-dashboard
analytics
product-design
data-engineering
```

### Tertiary Topics (contextual)

```
bangalore
india
urban-planning
public-health
environmental-data
decision-support
explainable-ai
data-governance
```

### Recommended Set (15 max for GitHub)

```
streamlit
plotly
python
dashboard
data-visualization
urban-analytics
traffic-analysis
air-quality
interactive-dashboard
analytics
data-engineering
product-design
bangalore
decision-support
data-governance
```

---

## Deliverable 9: Repository Organisation Review

### Current Structure

```
DADV-Project/
├── assets/                    # Banner, screenshots (empty)
├── bangalore_intelligence/    # Application code
├── docs/diagrams/             # Architecture diagrams
├── MD-File/                   # Legacy design documents
├── .gitignore
├── README.md
├── LICENSE                    # ✅ Created
└── CONTRIBUTING.md            # ✅ Created
```

### Recommendations

| Item | Action | Priority |
|------|--------|----------|
| `MD-File/` folder | Rename to `docs/design-docs/` or leave as-is (not user-facing) | Low |
| `assets/screenshots/` | Populate with real screenshots before publishing | High |
| `assets/banner.png` | Create using design spec above | High |
| `.gitignore` | Verify `bangalore_intelligence/data/` paths are covered | Medium |
| `requirements.txt` | Pin exact versions for reproducibility | Low |
| `.github/` | Add issue template and PR template | Low |

### Badge Ordering (in README)

Current order is correct:
1. Python version
2. Streamlit version
3. Plotly version
4. License
5. Tests

No changes needed.

### Release Preparation

- Tag initial release as `v1.0.0`
- Write release notes summarising the platform
- Attach screenshots to the release

### GitHub Settings

| Setting | Recommendation |
|---------|---------------|
| **Branch protection** | Require PR reviews for `main` |
| **Issue templates** | Bug report + Feature request |
| **PR template** | Checklist: tests pass, docs updated |
| **Discussions** | Enable for Q&A |
| **Wiki** | Disable (README is sufficient) |
| **Pages** | Enable from `main` branch if hosting docs |

---

## Deliverable 10: Final Publication Checklist

### Pre-Publication

- [ ] `assets/banner.png` created and placed
- [ ] `assets/screenshots/traffic_overview.png` captured
- [ ] `assets/screenshots/aqi_overview.png` captured
- [ ] `assets/screenshots/traffic_quadrant.png` captured
- [ ] `assets/screenshots/aqi_calendar.png` captured
- [ ] `assets/screenshots/filter_panel.png` captured
- [ ] `assets/screenshots/advanced_lab.png` captured
- [ ] Demo GIF recorded and placed
- [ ] `LICENSE` file present
- [ ] `CONTRIBUTING.md` present
- [ ] Streamlit deployment live and URL updated in README
- [ ] Placeholder URL `your-app-url.streamlit.app` replaced with real URL

### GitHub Configuration

- [ ] Repository description set (short)
- [ ] Website URL set (Streamlit deployment)
- [ ] Topics added (15 recommended topics)
- [ ] Social preview image uploaded
- [ ] README renders correctly on mobile
- [ ] All badges render correctly
- [ ] All Mermaid diagrams render correctly
- [ ] All relative links work
- [ ] All image paths resolve

### Code Quality

- [ ] All 48 tests pass (`pytest bangalore_intelligence/tests/ -v`)
- [ ] No hardcoded paths or secrets
- [ ] `.gitignore` covers all generated files
- [ ] No `__pycache__` directories committed
- [ ] No `.env` files committed

### Final Review

- [ ] README reads well in 90 seconds
- [ ] Screenshots are high-resolution and清晰
- [ ] Demo GIF is smooth and under 5MB
- [ ] No broken links anywhere
- [ ] No typos in public-facing text
- [ ] License file has correct year and name
- [ ] Repository feels indistinguishable from a mature open-source project

### Post-Publication

- [ ] Pin repository on GitHub profile
- [ ] Share on LinkedIn with project summary
- [ ] Add to portfolio website
- [ ] Create GitHub release with notes
- [ ] Monitor issues and respond promptly
