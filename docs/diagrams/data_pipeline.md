# Data Pipeline

How raw CSVs become interactive visualisations, with every data handoff validated.

```mermaid
flowchart TB
    subgraph Sources["📁 Data Sources"]
        TrafficCSV[Traffic Raw CSV<br/>8,936 records · 16 roads · 8 zones]
        AQICSV[AQI Raw CSV<br/>Daily PM2.5 · meteorological data]
    end

    subgraph Import["🔄 Import Pipeline"]
        CLI[import_real_data.py<br/>--dry-run / --apply]
        Normalize[Column Normalization<br/>Alias mapping, type coercion]
        Validate[Schema Validation<br/>Required columns, date ranges]
        Dedup[Duplicate Detection<br/>Road-level key governance]
        Lock[File-based Locking<br/>Mutual exclusion]
    end

    subgraph Governance["🛡️ Governance"]
        Backup[Atomic Backup<br/>Previous state preserved]
        Rollback[Rollback on Failure<br/>Automatic restore]
    end

    subgraph Storage["💾 Processed Storage"]
        Parquet[(Clean Parquets<br/>Typed, derived columns)]
        Manifest[(Governance Manifest<br/>SHA-256 fingerprints)]
    end

    subgraph Loading["📥 Cached Loading"]
        Loader[st.cache_data<br/>with fingerprint check]
        Fallback[Fallback Chain<br/>Processed → Canonical → Bootstrap]
    end

    subgraph Transforms["📊 Transforms"]
        TrafficKPI[Traffic Transforms<br/>15 chart datasets + KPIs]
        AQIKPI[AQI Transforms<br/>15 chart datasets + KPIs]
    end

    subgraph Bundles["📦 Page Bundles"]
        Bundles12[12 Bundle Builders<br/>Hero + Support charts, KPIs, Insights]
    end

    subgraph Rendering["🖥️ Rendering"]
        ChartModules[30 Chart Modules<br/>DataFrame → Plotly Figure]
        Dashboard[Streamlit Dashboard<br/>Interactive, Filterable, Explainable]
    end

    TrafficCSV --> CLI
    AQICSV --> CLI
    CLI --> Normalize --> Validate --> Dedup --> Lock
    Lock --> Backup --> Parquet
    Lock -.->|failure| Rollback
    Parquet --> Loader
    Manifest --> Loader
    Loader --> Fallback
    Fallback --> TrafficKPI
    Fallback --> AQIKPI
    TrafficKPI --> Bundles12
    AQIKPI --> Bundles12
    Bundles12 --> ChartModules --> Dashboard

    style Sources fill:#f0ad4e,color:#000
    style Import fill:#5BC0DE,color:#fff
    style Governance fill:#E67E22,color:#fff
    style Storage fill:#3498DB,color:#fff
    style Loading fill:#9B59B6,color:#fff
    style Transforms fill:#5CB85C,color:#fff
    style Bundles fill:#F39C12,color:#000
    style Rendering fill:#2ECC71,color:#fff
```

## Stage 1: Import

Raw CSVs are normalized, validated, and deduplicated before writing canonical parquet files. The CLI supports `--dry-run` for safe preview and `--apply` for execution. File-based locking prevents concurrent imports. Atomic backup ensures failed imports never corrupt working data.

## Stage 2: Loading

`data_layer/loaders.py` resolves data through a priority chain: processed parquet → canonical raw parquet → synthetic bootstrap. Each load is fingerprinted against the governance manifest. Fingerprint mismatches trigger cache invalidation.

## Stage 3: Transforms

Transform functions compute chart-ready datasets from clean parquets. Each function produces exactly the DataFrame shape its chart expects. No chart function performs aggregation — all computation happens here.

## Stage 4: Bundles

Page bundle builders assemble transforms into structured dictionaries containing hero chart, support charts, KPI values, insight text, and navigation metadata. Each of the 12 pages has its own builder.

## Stage 5: Rendering

Chart modules receive clean DataFrames and return Plotly `Figure` objects. They contain zero business logic — only visualisation code. Chart containers handle titles, loading skeletons, fullscreen, and captions.

## Cache Invalidation

```mermaid
flowchart LR
    Trigger[Cache Invalidation] --> Type{Trigger Type}
    Type -->|File hash change| Fingerprint[Fingerprint Mismatch → Revalidate]
    Type -->|Filter change| Filter[Filter Update → Reapply filters only]
    Type -->|Import event| Import[Import Complete → Clear dashboard caches]
    
    style Trigger fill:#E74C3C,color:#fff
    style Fingerprint fill:#E67E22,color:#fff
    style Filter fill:#F39C12,color:#000
    style Import fill:#9B59B6,color:#fff
```

The `performance.py` module tracks a dependency graph mapping each chart to its transforms and caches. When a filter changes, only affected caches are invalidated — not the entire data layer.
