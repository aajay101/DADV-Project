# User Journey

How three personas navigate the platform to answer real analytical questions and reach evidence-based decisions.

## Journey Overview

```mermaid
graph LR
    Open([Open Dashboard]) --> Choose["Choose Domain<br>Traffic / AQI"]
    Choose --> KPIs["Review KPIs<br>System health at a glance"]
    KPIs --> Filter["Apply Filters<br>Date, area, road, weather"]
    Filter --> Investigate["Investigate Patterns<br>Chart-by-chart exploration"]
    Investigate --> Interpret["Interpret Insights<br>Explainability triggers"]
    Interpret --> Compare["Compare Trends<br>Cross-page analysis"]
    Compare --> Conclude["Draw Conclusions<br>Evidence-based decisions"]
    Conclude --> Act["Support Decision<br>Policy, planning, research"]
    
    style Open fill:#E5383B,color:#fff
    style Choose fill:#4A90D9,color:#fff
    style KPIs fill:#5CB85C,color:#fff
    style Filter fill:#F39C12,color:#000
    style Investigate fill:#9B59B6,color:#fff
    style Interpret fill:#E74C3C,color:#fff
    style Compare fill:#3498DB,color:#fff
    style Conclude fill:#2ECC71,color:#fff
    style Act fill:#1ABC9C,color:#fff
```

---

## Persona 1: Urban Planner

**Question:** *"Which areas need immediate infrastructure investment?"*

```mermaid
sequenceDiagram
    participant U as Urban Planner
    participant T as Traffic Dashboard
    participant C as Charts
    participant E as Explainability

    U->>T: Opens Command Overview
    T->>C: Renders T-01 Scorecard
    C->>U: System congestion gauge + area rankings
    Note over U: "System stress is at 68 — moderate but rising"
    
    U->>T: Applies area filter (focus on 3 zones)
    T->>C: Re-renders with filtered data
    C->>U: Area rankings update to show focused zones
    
    U->>T: Opens Spatial Operations page
    T->>C: Renders T-05 Road Priority Quadrant
    C->>U: Roads classified by congestion vs capacity
    Note over U: "12 roads in Critical Overload quadrant"
    
    U->>E: Clicks explainability trigger on T-05
    E->>U: "Roads in upper-right need both capacity and speed attention"
    
    U->>T: Opens Threshold Analytics
    T->>C: Renders T-09 Speed Collapse
    C->>U: "Congestion becomes irreversible below 25 km/h"
    
    Note over U: Decision: Prioritize 12 roads for signal optimization
```

**Key charts used:** T-01 (Scorecard), T-05 (Quadrant), T-09 (Speed Threshold)
**Decision enabled:** Infrastructure investment prioritization across 8 Bangalore zones

---

## Persona 2: Public Health Researcher

**Question:** *"How bad was air quality this winter, and which areas were most exposed?"*

```mermaid
sequenceDiagram
    participant R as Researcher
    participant A as AQI Dashboard
    participant C as Charts
    participant E as Explainability

    R->>A: Opens Crisis Overview
    A->>C: Renders A-01 Scorecard
    C->>R: PM2.5 burden + category distribution
    Note over R: "42% of days in 'Very Poor' or 'Severe' category"
    
    R->>A: Opens Temporal Patterns
    A->>C: Renders A-02 Calendar Heatmap
    C->>R: 3-year weekly PM2.5 intensity grid
    Note over R: "December-January blocks are consistently dark"
    
    R->>A: Opens Hidden Patterns
    A->>C: Renders A-03 Seasonal Ridgeline
    C->>R: Seasonal PM2.5 distributions
    Note over R: "Winter distribution has a heavy right tail"
    
    R->>E: Checks explainability for A-03
    E->>R: "Heavy-tailed winter indicates recurring acute exposure episodes"
    
    R->>A: Opens Weather Relationships
    A->>C: Renders A-08 Temperature Scatter
    C->>R: Temperature vs PM2.5 relationship
    
    Note over R: Evidence: Winter weeks with low temperature show highest PM2.5
```

**Key charts used:** A-01 (Scorecard), A-02 (Calendar), A-03 (Ridgeline), A-08 (Temperature)
**Decision enabled:** Seasonal health risk assessment and preparedness planning

---

## Persona 3: Policy Analyst

**Question:** *"How do traffic patterns and air quality relate in specific neighborhoods?"*

```mermaid
sequenceDiagram
    participant P as Policy Analyst
    participant T as Traffic Dashboard
    participant A as AQI Dashboard
    participant C as Charts

    P->>T: Opens Traffic Dashboard
    T->>C: Renders Command Overview
    C->>P: "System congestion at 72 — high"
    
    P->>T: Filters to Jan-Mar 2023, Whitefield zone
    T->>C: All charts update to focused scope
    C->>P: "Whitefield congestion peaked in February"
    
    P->>A: Switches to AQI Dashboard
    A->>C: Renders Crisis Overview
    C->>P: "PM2.5 burden elevated in same period"
    
    P->>A: Applies same date filter
    A->>C: Temporal charts update
    C->>P: "February PM2.5 spike aligns with traffic peak"
    
    P->>A: Opens Atmospheric Intelligence
    A->>C: Renders A-06 Stagnation Hexbin
    C->>P: "Low wind + high viscosity = pollution trapping"
    
    Note over P: Cross-dashboard finding: Traffic peaks and PM2.5 spikes correlate during atmospheric stagnation events
```

**Key charts used:** T-01 (Traffic Overview), A-01 (AQI Overview), A-06 (Stagnation)
**Decision enabled:** Evidence base for integrated transport-environment policy

---

## Navigation Architecture

Each page is organized around an analytical question. The progression moves from awareness to mastery:

```mermaid
graph TB
    subgraph Traffic["Traffic Intelligence"]
        T1["Command Overview<br>What is the current state?"]
        T2["Temporal Intelligence<br>How has it changed?"]
        T3["Spatial Operations<br>Where is it worst?"]
        T4["Threshold Analytics<br>What are the critical boundaries?"]
        T5["Hidden Patterns<br>What is not immediately visible?"]
        T6["Advanced Lab<br>How do all dimensions relate?"]
    end

    subgraph AQI["Air Quality Intelligence"]
        A1["Crisis Overview<br>What is the current burden?"]
        A2["Temporal Patterns<br>When does pollution peak?"]
        A3["Atmospheric Intelligence<br>What conditions trap pollution?"]
        A4["Weather Relationships<br>How does weather drive AQI?"]
        A5["Hidden Patterns<br>What distributions reveal"]
        A6["Analytical Workspace<br>Multi-variable correlation"]
    end

    T1 --> T2 --> T3 --> T4 --> T5 --> T6
    A1 --> A2 --> A3 --> A4 --> A5 --> A6

    T6 -.->|"switch domain"| A1
    A6 -.->|"switch domain"| T1

    style T1 fill:#E5383B,color:#fff
    style A1 fill:#27AE60,color:#fff
```

---

## Interaction Model

### Global Filters
Filters persist across all charts within a dashboard. Changing the date range, area selection, or weather filter recomputes every chart on the current page.

### Investigation Overlays
Clicking a chart element creates a temporary overlay that highlights related data across other charts. Overlays are cleared with "Clear Focus" — they never modify the underlying filter state.

### Explainability Triggers
Every chart has a "?" trigger that opens structured interpretation: what the chart shows, what patterns matter, what users commonly misunderstand, and what to investigate next.

### Advanced Lab Mode
The Lab page requires explicit entry through a gate component. Lab controls expose analytical parameters (area selection, overlay count, dimension toggles) that production pages hide to reduce cognitive load.

---

## Filter Architecture

```mermaid
graph LR
    subgraph Filters["Global Filter Panel"]
        Date[Date Range]
        Area["Area Selection<br>8 zones"]
        Road["Road Selection<br>16 roads"]
        Weather[Weather Conditions]
        Season[Season]
        Category[AQI Category]
    end

    subgraph State["Session State"]
        Store[(Persistent Filter Store)]
    end

    subgraph Charts["30 Charts"]
        C1[Chart 1] --> C2[Chart 2] --> C3[...]
    end

    Date --> Store
    Area --> Store
    Road --> Store
    Weather --> Store
    Season --> Store
    Category --> Store
    
    Store -->|read| C1

    style Filters fill:#F39C12,color:#000
    style State fill:#9B59B6,color:#fff
    style Charts fill:#5CB85C,color:#fff
```

Filters are application-wide state, not per-chart. When you filter to "Whitefield zone, January 2023," every chart on the page shows the same subset of data. This ensures consistent scope across all visualisations.
