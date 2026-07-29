# System Architecture

How every module in the Bangalore Urban Intelligence Platform connects and why each boundary exists.

```mermaid
graph TB
    subgraph UI["🖥️ User Interface"]
        User([👤 User]) --> App[Streamlit App<br/>app.py]
        App --> Router[Dashboard Router<br/>traffic_router / aqi_router]
        Router --> Pages[Page Router<br/>6 pages per dashboard]
    end

    subgraph Presentation["🎨 Presentation Layer"]
        Pages --> Components[28 Reusable Components<br/>KPI cards, filters, chart containers, lab controls]
        Components --> Charts[30 Chart Modules<br/>DataFrame → Plotly Figure]
        Components --> Explainability[Explainability Engine<br/>Per-chart interpretation + style validation]
    end

    subgraph State["⚙️ State Management"]
        App --> SessionState[Session State<br/>Filter values, active tab, interactions]
        SessionState --> Reducers[Deterministic Reducers<br/>Typed actions → new state → invalidation plan]
        Reducers --> Performance[Performance Tracker<br/>Cache tiers, render traces, dependency graph]
        Performance --> Observability[Observability<br/>Runtime telemetry, health monitoring]
    end

    subgraph Data["📊 Data Layer"]
        Pages --> Bundles[12 Page Bundle Builders<br/>Structured page data packages]
        Bundles --> Transforms[Traffic Transforms + AQI Transforms<br/>KPI computation, chart-ready datasets]
        Transforms --> Loaders[Cached Loaders<br/>st.cache_data + SHA-256 fingerprint]
        Loaders --> Governance[Data Governance<br/>Startup checks, schema validation, synthetic detection]
        Governance --> Storage[(Processed Parquets<br/>Validated, typed, derived columns)]
    end

    subgraph Import["📥 Import Pipeline"]
        CLI[CLI: import_real_data.py] --> Normalize[Column Normalization]
        Normalize --> Validate[Schema Validation]
        Validate --> Dedup[Duplicate Detection]
        Dedup --> Lock[File-based Locking]
        Lock --> Write[Atomic Write to Parquet]
    end

    style User fill:#E5383B,color:#fff
    style Charts fill:#5CB85C,color:#fff
    style Explainability fill:#9B59B6,color:#fff
    style Reducers fill:#F39C12,color:#000
    style Governance fill:#E67E22,color:#fff
    style Storage fill:#3498DB,color:#fff
    style CLI fill:#95A5A6,color:#fff
```

## Module Responsibilities

| Module | What It Does |
|--------|-------------|
| **app.py** | Entry point. Runs startup governance checks, initializes state, switches between dashboards. |
| **config/** | Color tokens, data schema, chart sizing, page definitions. |
| **dashboards/** | Dashboard routing and 30 chart modules (Traffic T-01–T-15, AQI A-01–A-15). |
| **components/** | 28 reusable UI building blocks shared across both dashboards. |
| **data_layer/** | Data loading, transforms, page bundle assembly, import pipeline with governance. |
| **explainability/** | Static metadata for every chart: interpretation, glossary, misinterpretation warnings. |
| **filters/** | Session state, deterministic reducers, chart dependency tracking, interaction management. |
| **services/** | Performance tracking, cache management, export, drilldown detail content builders. |
| **utils/** | CSS injection, formatting, Plotly theming, data validation, accessibility auditing. |
| **tests/** | 48 test modules covering governance, validators, explainability, and chart rendering. |

## Dependency Rules

Every dependency points inward toward the data layer:

- **Charts** depend on Bundles, never on raw data
- **Components** are read-only UI building blocks
- **Filters** modify session state, never chart rendering
- **Governance** validates at every boundary (import, load, runtime)
