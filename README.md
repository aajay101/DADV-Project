<p align="center">
  <img src="assets/banner.png" alt="Bangalore Urban Intelligence Platform" width="100%">
</p>

<h1 align="center">Bangalore Urban Intelligence Platform</h1>

<p align="center">
  <strong>Transforming raw urban data into actionable intelligence for Bangalore's traffic and air quality crises.</strong>
</p>

<p align="center">
  <a href="#project-at-a-glance">Overview</a> ·
  <a href="#screenshots">Screenshots</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#getting-started">Getting Started</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/streamlit-1.28+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/plotly-5.18+-3F4F75?style=flat-square&logo=plotly&logoColor=white" alt="Plotly">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License: MIT">
  <img src="https://img.shields.io/badge/tests-48-passing-brightgreen?style=flat-square" alt="Tests">
</p>

---

## Project at a Glance

| | |
|---|---|
| **Problem** | Urban traffic and air quality analysis exist in disconnected systems. Bangalore's 13 million residents face both crises daily, but no tool connects them. |
| **Solution** | A dual-dashboard analytical platform unifying traffic and AQI intelligence into 30 interactive visualisations with built-in interpretive guidance. |
| **Users** | Urban planners, public health researchers, policy analysts, and citizens seeking evidence-based urban insights. |
| **Scale** | 30 charts · 2 dashboards · 12 pages · 48 tests · 8 zones · 16 roads · 4 years of AQI data |
| **Technology** | Python, Streamlit, Plotly, Pandas, Parquet |
| **Outcome** | Transforms raw urban datasets into a navigable, explainable decision-support interface. |

---

## The Problem

Bangalore's traffic congestion doubles commute times across 8 zones. Its air quality regularly exceeds WHO safety thresholds. These crises are studied separately — traffic data in one tool, pollution data in another — but they are physically connected. The same roads that carry traffic generate the emissions that fill the air.

**No existing tool connects these two views in a single, navigable, analyst-ready interface.**

---

## Why I Built This

While exploring publicly available urban datasets, I noticed that traffic and air quality were almost always analysed independently. A city planner studying congestion and a public health official studying PM2.5 were often looking at the same roads, the same neighbourhoods, and the same seasonal patterns — but through entirely separate tools with no way to cross-reference.

I also wanted to test whether interpretive guidance could make complex visualisations accessible to non-technical users. Most dashboards assume the viewer already knows what to look for. I wanted to explore whether pre-authored explanations — answering "what should I do with this information?" instead of "what am I looking at?" — could change how people interact with analytical data.

The result is a platform that treats explainability as a first-class product concern, not a tooltip afterthought.

---

## Solution Overview

A dual-dashboard analytical platform that unifies Bangalore's traffic and air quality data into **30 interactive visualisations** across **12 analytical pages**, with built-in interpretive guidance so non-technical users can draw meaningful conclusions without training.

- **Traffic Intelligence Dashboard** — 15 charts covering congestion patterns, speed thresholds, road burden, public transport relationships, and multi-dimensional area profiling
- **Air Quality Intelligence Dashboard** — 15 charts covering PM2.5 trends, seasonal patterns, weather correlations, Atmospheric regimes, and pollution persistence
- **Explainability Layer** — Every chart has authored interpretation guidance, misinterpretation warnings, glossary support, and human-impact translations
- **Data Governance** — Automated validation, import locking, schema fingerprinting, and synthetic-data detection ensure data integrity at every stage

---

## System Highlights

| Capability | What It Provides |
|------------|-----------------|
| **Dual Analytical Dashboards** | Separate traffic and AQI workflows with shared visual language |
| **Explainability Engine** | Per-chart interpretation, misinterpretation warnings, glossary, human-impact translations |
| **Data Governance** | Import validation, schema fingerprinting, synthetic-data detection, atomic rollback |
| **Deterministic State Engine** | Redux-inspired reducers with typed actions and invalidation plans |
| **Modular Component Architecture** | 28 reusable UI building blocks parameterised by dashboard identity |
| **Automated Testing** | 48 test modules covering governance, validators, explainability, and chart rendering |
| **Interactive Visualisations** | 30 Plotly charts with hover inspection, linked selection, and fullscreen mode |

---

## Technical Highlights

- Deterministic reducer architecture for predictable state management
- Fingerprint-based cache invalidation with SHA-256 schema verification
- Atomic import pipeline with file locking and automatic rollback
- Static explainability metadata engine with semantic style validation
- Modular component system with dashboard-agnostic rendering
- WCAG contrast auditing for accessibility compliance

---

## Design Principles

1. **Explainability over decoration.** Every chart earns its place by helping a user reach a conclusion. If a chart cannot answer a decision question, it is removed.

2. **No business logic in chart code.** Transforms compute data. Charts render it. This separation makes both layers independently testable and replaceable.

3. **Govern every data boundary.** Fingerprint validation, schema checks, and synthetic-data detection exist because every data handoff is a potential failure point.

4. **Deterministic state.** Every filter interaction dispatches a typed action, produces a predictable state, and declares exactly which caches are invalidated.

5. **Plain language, always.** Explainability text is written for a non-technical decision-maker, not a data scientist. Jargon is avoided; metrics are translated to human impact.

---

## Live Demo

> **[Explore the Bangalore Urban Intelligence Platform →](https://your-app-url.streamlit.app)**
>
> *Deployed on Streamlit Community Cloud. No installation required.*

---

## Screenshots

<p align="center">
  <em>Add your dashboard screenshots to the <code>assets/screenshots/</code> directory.</em>
</p>

<table>
  <tr>
    <td align="center" width="50%">
      <img src="assets/screenshots/traffic_overview.png" alt="Traffic Command Overview" width="100%">
      <br>
      <strong>Traffic Command Overview</strong><br>
      <em>Identify high-volume, low-speed corridors that need capacity intervention</em>
    </td>
    <td align="center" width="50%">
      <img src="assets/screenshots/aqi_overview.png" alt="AQI Crisis Overview" width="100%">
      <br>
      <strong>AQI Crisis Overview</strong><br>
      <em>Assess current pollution severity and which zones exceed safe thresholds</em>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <img src="assets/screenshots/traffic_quadrant.png" alt="Road Priority Quadrant" width="100%">
      <br>
      <strong>Road Priority Quadrant</strong><br>
      <em>Rank roads by congestion severity to prioritise infrastructure spend</em>
    </td>
    <td align="center" width="50%">
      <img src="assets/screenshots/aqi_calendar.png" alt="AQI Calendar Heatmap" width="100%">
      <br>
      <strong>3-Year AQI Calendar</strong><br>
      <em>Spot seasonal pollution peaks to plan public health advisories</em>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <img src="assets/screenshots/filter_panel.png" alt="Global Filter Panel" width="100%">
      <br>
      <strong>Global Filter Panel</strong><br>
      <em>Scope any view to specific zones, date ranges, or road types</em>
    </td>
    <td align="center" width="50%">
      <img src="assets/screenshots/advanced_lab.png" alt="Advanced Analytical Lab" width="100%">
      <br>
      <strong>Advanced Analytical Lab</strong><br>
      <em>Cross-correlate traffic and AQI dimensions with stress profiling</em>
    </td>
  </tr>
</table>

### Demo GIF

> *Add a 20–30 second screen recording showing: dashboard launch → filter interaction → chart exploration → explainability trigger → dashboard switching → Advanced Lab.*

---

## Key Metrics

<table>
  <tr>
    <td align="center"><strong>30</strong><br>Analytical Visualisations</td>
    <td align="center"><strong>2</strong><br>Analytical Dashboards</td>
    <td align="center"><strong>12</strong><br>Dashboard Pages</td>
    <td align="center"><strong>48</strong><br>Automated Tests</td>
  </tr>
  <tr>
    <td align="center"><strong>8</strong><br>Bangalore Zones</td>
    <td align="center"><strong>16</strong><br>Road Segments</td>
    <td align="center"><strong>4</strong><br>Years of Data</td>
    <td align="center"><strong>28</strong><br>UI Components</td>
  </tr>
</table>

---

## User Journey

The platform is designed for three user personas with distinct analytical needs:

```mermaid
graph LR
    Open([Open Dashboard]) --> Choose[Choose Domain<br/>Traffic | AQI]
    Choose --> KPIs[Review KPIs<br/>System health at a glance]
    KPIs --> Filter[Apply Filters<br/>Date, area, road, weather]
    Filter --> Investigate[Investigate Patterns<br/>Chart-by-chart exploration]
    Investigate --> Interpret[Interpret Insights<br/>Explainability triggers]
    Interpret --> Conclude[Draw Conclusions<br/>Evidence-based decisions]
    
    style Open fill:#E5383B,color:#fff
    style Choose fill:#4A90D9,color:#fff
    style KPIs fill:#5CB85C,color:#fff
    style Filter fill:#F39C12,color:#000
    style Investigate fill:#9B59B6,color:#fff
    style Interpret fill:#E74C3C,color:#fff
    style Conclude fill:#2ECC71,color:#fff
```

### The Urban Planner
> *"Which areas need immediate infrastructure investment?"*

Opens the **Traffic Command Overview** → Reviews system congestion gauge and area rankings → Filters to focus on underperforming zones → Uses the **Road Priority Quadrant** to classify roads by congestion vs. capacity → Identifies roads in "Critical Overload" → Checks the **Speed Collapse Threshold** to understand at what speed congestion becomes irreversible → Prioritizes roads for signal optimization.

### The Public Health Researcher
> *"How bad was air quality this winter?"*

Opens the **AQI Crisis Overview** → Reviews PM2.5 burden and category distribution → Uses the **3-Year Calendar Heatmap** to identify recurring pollution weeks → Opens the **Seasonal Ridgeline** to compare winter vs. monsoon distributions → Checks **Weather Relationships** for temperature-pressure correlations → Concludes which seasonal windows carry the highest health risk.

### The Policy Analyst
> *"How do traffic and air quality relate in specific neighborhoods?"*

Applies filters in the **Traffic Dashboard** for a specific zone and date range → Notes congestion patterns → Switches to the **AQI Dashboard** with the same filters → Compares pollution trends against traffic trends → Uses **Atmospheric Intelligence** to check whether stagnation events coincide with high-traffic periods → Builds evidence for integrated transport-environment policy.

> **[Detailed persona flows and sequence diagrams →](docs/diagrams/user_journey.md)**

---

## Questions This Platform Helps Answer

Every feature maps to a specific analytical decision:

| Question | Feature | Decision Enabled |
|----------|---------|-----------------|
| *"How stressed is the traffic network?"* | Network Congestion Scorecard (T-01) | System-wide assessment |
| *"Which roads should we fix first?"* | Road Priority Quadrant (T-05) | Infrastructure investment prioritization |
| *"At what point does congestion become irreversible?"* | Speed Collapse Threshold (T-09) | Speed management policy |
| *"How do areas compare across all dimensions?"* | Compound Radar Profile (T-13) | Multi-factor area assessment |
| *"How bad is PM2.5 right now?"* | Crisis Scorecard (A-01) | Public health alert level |
| *"When were the worst pollution weeks?"* | 3-Year Calendar Heatmap (A-02) | Seasonal preparedness planning |
| *"How does weather drive pollution?"* | Temperature-Pressure Scatter (A-08) | Meteorological risk factors |
| *"What conditions trap pollution?"* | Atmospheric Regimes (A-13) | Stagnation event response |
| *"What does this chart mean for my decision?"* | Explainability Triggers | Informed interpretation |

---

## Architecture

The platform follows a strict **four-layer separation** with unidirectional data flow. No chart function touches raw data. No filter function touches chart rendering.

### Runtime Architecture

```mermaid
graph TB
    subgraph UI["🖥️ User Interface"]
        User([👤 User]) --> App[Streamlit App]
        App --> Router[Dashboard Router<br/>Traffic | AQI]
        Router --> Pages[Page Router<br/>6 pages per dashboard]
    end

    subgraph Presentation["🎨 Presentation"]
        Pages --> Components[28 Reusable Components]
        Components --> Charts[30 Chart Modules]
        Components --> Explainability[Explainability Engine]
    end

    subgraph State["⚙️ State Management"]
        App --> SessionState[Session State]
        SessionState --> Reducers[Deterministic Reducers]
        Reducers --> Performance[Cache Invalidation]
    end

    subgraph Data["📊 Data Layer"]
        Pages --> Bundles[12 Page Bundle Builders]
        Bundles --> Transforms[Data Transforms]
        Transforms --> Loaders[Cached Loaders]
        Loaders --> Governance[Data Governance]
        Governance --> Storage[(Processed Parquets)]
    end

    style User fill:#E5383B,color:#fff
    style Charts fill:#5CB85C,color:#fff
    style Explainability fill:#9B59B6,color:#fff
    style Reducers fill:#F39C12,color:#000
    style Governance fill:#E67E22,color:#fff
    style Storage fill:#3498DB,color:#fff
```

> **[Detailed architecture diagrams →](docs/diagrams/system_architecture.md)**

### Repository Layout

```
bangalore_intelligence/
├── app.py              # Entry point — governance check, dashboard switching
├── config/             # Theme tokens, data schema, chart sizing, page definitions
├── dashboards/         # 30 chart modules + 12 page modules across 2 dashboards
├── components/         # 28 reusable UI building blocks
├── data_layer/         # Page bundles, transforms, governance, import pipeline
├── explainability/     # Chart interpretation metadata and validation engine
├── filters/            # Session state, deterministic reducers, interaction management
├── services/           # Chart click handlers and drilldown content builders
├── utils/              # CSS injection, formatters, validators, Plotly helpers
├── tests/              # 48 test modules
├── scripts/            # CLI for real data import
└── data/               # Raw CSVs, processed parquets, governance metadata
```

### Data Pipeline

```mermaid
flowchart LR
    CSV[Raw CSVs] --> Import[Import Pipeline]
    Import --> Parquet[Clean Parquet]
    Parquet --> Load[Cached Loaders]
    Load --> Transform[Data Transforms]
    Transform --> Bundle[Page Bundles]
    Bundle --> Chart[Chart Modules]
    Chart --> Figure[Plotly Figure]
    Figure --> Dashboard[Streamlit Dashboard]
    
    style CSV fill:#f0ad4e,color:#000
    style Dashboard fill:#5cb85c,color:#fff
```

1. **Raw CSVs** are imported through a validated pipeline that normalizes columns, detects duplicates, and writes canonical parquet files
2. **Clean parquets** are loaded with `st.cache_data` and fingerprinted against a governance manifest — cache invalidates on hash mismatch
3. **Transforms** compute chart-ready datasets: temporal KPIs, spatial aggregates, stress heatmaps, ridgeline distributions, weather profiles
4. **Page bundles** assemble transforms into structured dictionaries with hero charts, support charts, KPIs, insights, and navigation metadata
5. **Chart modules** receive clean DataFrames and return Plotly `Figure` objects — zero business logic, only visualization code

> **[Full pipeline details →](docs/diagrams/data_pipeline.md)**

---

## Engineering Decisions

### Deterministic State Management

Streamlit's `session_state` is write-only — no mechanism to trace why state changed or which charts are affected. I implemented a **reducer pattern** inspired by Redux: every state change is dispatched as a typed action, a pure reducer computes the new state, and an invalidation plan declares which cached data is stale. This makes state changes predictable and debuggable.

### Data Governance: Defense in Depth

Real-world data imports can fail mid-way, contain duplicates, or arrive with unexpected schemas. The governance system operates at three levels: **import governance** (file locking, atomic rollback), **runtime governance** (startup schema verification), and **load-time governance** (fingerprint validation on every cache hit). Every check was motivated by a specific failure mode I encountered during development.

### Explainability Without Runtime AI

Calling an LLM for every chart interpretation would add latency, cost, and unpredictability. Instead, every chart's interpretation is **pre-authored by a human** and validated against semantic style rules that enforce plain language, reject overconfident claims, and prevent chart-first narration. The `ExplainabilityEntry` dataclass has 30+ fields covering metrics, components, glossary, patterns, and human impact — all validated at startup.

### Fingerprint-Based Cache Invalidation

Data transforms are expensive — some recompute grouped aggregations across 8,936 records. Simple caching would never refresh. Each dataset has a SHA-256 fingerprint computed from file content and schema. On load, the fingerprint is compared against the governance manifest. Mismatches trigger revalidation. The `performance.py` module tracks a dependency graph of 30 charts and their cache tiers.

---

## Product Decisions

### Why Two Dashboards Instead of One

A unified dashboard would force users to mentally switch between "road congestion" and "air quality" on every page. Separating them lets users stay in one analytical context. The shared component layer ensures visual consistency without coupling the workflows.

### Why Six Pages Per Dashboard

Each page is organized around an analytical question, not a chart type:

1. **Overview** — "What is the current state?"
2. **Temporal** — "How has this changed over time?"
3. **Spatial/Atmospheric** — "Where or under what conditions?"
4. **Threshold/Correlation** — "What are the critical boundaries?"
5. **Hidden Patterns** — "What is not immediately visible?"
6. **Advanced Lab** — "How do all dimensions relate?"

This progression guides users from awareness to deep investigation without overwhelming them.

### Why an Advanced Lab Gate

The compound radar (T-13) and pairplot matrix (A-15) are high-dimensional tools that require more context than standard charts. The Lab gate asks users to explicitly enter advanced mode, preventing overwhelm while preserving analytical depth for power users.

---

## Technology Choices

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | **Streamlit** | Fastest path from Python data to interactive web app. Native caching, session state, and widgets eliminate a custom backend. |
| Visualization | **Plotly** | Interactive tooltips, synchronized selections, custom trace layering. Every chart supports hover inspection without additional wiring. |
| Data format | **Parquet** | Columnar storage with type preservation. The traffic dataset is 693KB as CSV but reads as typed parquet with zero parsing overhead. |
| State management | **Custom reducers** | Streamlit's session_state is write-only. Deterministic reducers make state changes traceable and reproducible. |
| Caching | **`st.cache_data` + fingerprinting** | Expensive transforms are cached with file-hash-based invalidation to ensure consistency with source data. |
| Explainability | **Static metadata** | Pre-authored, validated interpretation ensures quality without runtime AI latency or cost. |
| Testing | **Pytest with Streamlit stubs** | 48 test modules covering governance, validators, explainability integrity, and chart rendering. |

---

## Datasets

The platform processes two real-world datasets:

- **Traffic**: 8,936 records across 16 roads in 8 Bangalore zones (Jan 2022 – Aug 2024), capturing congestion, speed, capacity, incidents, roadwork, pedestrian activity, and public transport usage
- **Air Quality**: Daily PM2.5 readings with meteorological data (2021–2024), including temperature, pressure, wind speed, humidity, and AQI category classifications

Both pass through a validated pipeline with schema enforcement, duplicate detection, and atomic import operations.

> **[Full pipeline diagram →](docs/diagrams/data_pipeline.md)**

---

## Getting Started

```bash
# Clone the repository
git clone https://github.com/aajay101/DADV-Project.git
cd DADV-Project/bangalore_intelligence

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1    # Windows
# source .venv/bin/activate    # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

The application includes synthetic bootstrap data, so it renders immediately without importing real datasets.

### Importing Real Data

```bash
# Preview what would be imported (safe — no changes made)
python scripts/import_real_data.py --dry-run

# Apply the import
python scripts/import_real_data.py --apply --traffic path/to/traffic.csv --aqi path/to/aqi.csv
```

---

## Product Roadmap

| Phase | Status | Scope |
|-------|--------|-------|
| **Phase 1** | ✅ Complete | Dual-dashboard platform with 30 charts, filters, explainability, governance, and tests |
| **Phase 2** | Planned | Real-time data ingestion from Bangalore traffic APIs and CPCB air quality stations |
| **Phase 3** | Planned | Predictive analytics — PM2.5 forecasting with confidence intervals, congestion early warning |
| **Phase 4** | Planned | Decision support — automated anomaly detection, intervention impact modeling |
| **Phase 5** | Vision | Full urban intelligence platform — multi-city, multi-modal transport, policy simulation |

---

## What I Learned

Building this project taught me three things I did not expect:

1. **The hardest product decision was knowing what to leave out.** Early versions had 45 charts. Cutting 15 was harder than building them, because each one felt justified in isolation. The real question was not "is this chart useful?" but "does this chart help the user reach a conclusion faster?" That discipline — cutting features to improve the product — is the most important thing I learned.

2. **Explainability is a product problem, not a technical one.** The explainability layer started as "let's add tooltips." It became a product exercise when I realized the tooltips were telling users what the chart *shows* instead of what it *means for their decision*. Rewriting every interpretation to answer "so what should I do?" instead of "what am I looking at?" was the single biggest UX improvement.

3. **Data governance is invisible until it fails.** The import pipeline, fingerprint validation, and synthetic data detection all feel like over-engineering — until you deploy to a new environment and the data format has changed. Every governance check was motivated by a specific failure I encountered during development.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  Built to understand how data becomes decisions, and how products make that translation effortless.
</p>
