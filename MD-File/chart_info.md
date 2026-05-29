# SUAQIS Chart Interpretation Audit

Status: documentation-only semantic and visualization audit. This file explains the implemented SUAQIS dashboard visuals for a future human-centered interpretation system. It does not describe a new feature, change dashboard behavior, or introduce runtime AI.

Source basis: chart builders in `dashboards/traffic/charts/*` and `dashboards/aqi/charts/*`, page metadata in `data_layer/page_bundles.py`, transform logic in `data_layer/traffic_transforms.py` and `data_layer/aqi_transforms.py`, and interaction metadata from the dashboard filter and overlay system.

Audience assumption: mixed audience, including non-technical users, students, analysts, executives, and government officials. Explanations should use simple, educational language with enough analytical depth for decision support.

## Shared Interpretation Rules

Global filters narrow the dataset before charts are calculated. When a user changes date, area, road, season, weather, or AQI filters, chart values change because the underlying records in scope changed.

Investigation overlays are temporary chart-click focus states. They can highlight or narrow overlay-aware charts, but they are not the same as global filters. They should be explained as temporary investigation context, not permanent dashboard state.

Empty charts are valid analytical outcomes. A blank or unavailable chart may mean the current filter or overlay scope has no matching records, not that the dashboard should reset user choices.

Most visuals are observational. They show patterns and relationships in the available data. They do not prove causality, identify exact root causes, or predict the future unless explicitly stated.

## Traffic Dashboard

### T-01 - Network Congestion And Area Ranking

**Visualization Type**

KPI-style bullet gauge plus horizontal area ranking bars. The gauge summarizes overall network congestion on a 0-100 scale, while the bars show which areas contribute the highest mean congestion. This combination works because users need both the big picture and the location of pressure. A single number would hide where congestion is concentrated, and a bar chart alone would not clearly say whether the whole system is healthy or stressed.

**Main Analytical Goal**

This chart helps users answer: "How stressed is the traffic network right now, and which areas are driving that stress?" It exists as the traffic overview because it turns many traffic records into an immediate operating picture. After seeing it, users should know whether congestion is broadly serious or mostly concentrated in a few locations.

**Variables / Metrics Used**

- System Congestion Index: the average congestion percentage across the current filtered records. Higher values mean heavier traffic pressure; values near or above the warning zone suggest the network is under strain.
- Capacity Saturation Rate: the share of records where road capacity is almost fully used. High saturation means roads have little spare room and small disruptions may cause bigger delays.
- Area mean congestion: the average congestion for each area. Higher bars identify areas with worse pressure.
- Peak stress area: the area with the highest pressure in the current scope. It points attention to the strongest contributor.

**Visual Components**

- Bullet gauge: shows system congestion from low to high on a fixed 0-100 scale.
- Colored gauge bands: lower values are calmer, middle values show caution, and high values show severe pressure.
- Diamond marker: marks the current System Congestion Index.
- Vertical threshold line near 75: helps users see when congestion moves into a concerning range.
- Area bars: rank areas by mean congestion.
- Dashed line near 90: marks critical overload territory for area-level congestion.
- Annotation text: reports capacity saturation and peak stress so users do not need to infer them from the visual alone.

**What Patterns Matter**

High overall gauge value plus many long area bars means congestion is network-wide. A moderate gauge with one or two very long bars means the problem is concentrated. If the top area is far above the others, users should treat the network stress as geographically uneven.

**Real-World Meaning**

This chart helps traffic planners and public users understand whether mobility is generally degraded. High congestion can mean longer travel times, less reliable commutes, more fuel use, and greater pressure on roads.

**Likely Intended User Interpretation**

Users are supposed to read this as the command-center summary: "Is the traffic system strained, and where should I look first?"

**Potential User Confusion**

Users may think the gauge is a live real-time traffic signal. It is actually calculated from the current dataset and filters. Users may also assume the top area is the only problem, even when the gauge indicates broad system stress.

**Glossary Terms Needed**

- Congestion index: a 0-100 style measure of how crowded or slow the road network is.
- Capacity saturation: how often roads are close to their usable limit.
- Peak stress: the area with the highest observed pressure.
- Filter scope: the records currently included after filters are applied.

**What This Chart Does NOT Explain**

It does not explain the exact cause of congestion. It does not prove whether congestion is caused by incidents, roadwork, weather, demand, or road design. It does not predict future congestion.

### T-02 - Parallel Coordinates Matrix

**Visualization Type**

Parallel coordinates / multi-axis profile chart. Each area is drawn as a line across several normalized traffic dimensions. This type was chosen because the question is not about one metric; it is about how areas behave across many metrics at once. Separate bar charts would make it harder to see the overall area "fingerprint."

**Main Analytical Goal**

This chart helps users understand whether an area is stressed in one way or across many dimensions. It answers: "Which areas have broad multi-factor traffic problems, and which only stand out on one measure?"

**Variables / Metrics Used**

- Congestion: how crowded the road system is.
- Speed: how quickly vehicles are moving. Low speed is usually bad.
- Capacity utilization: how close roads are to their capacity.
- Incident intensity: how often incidents appear in the records.
- Environmental impact: a derived score representing environmental burden associated with traffic conditions.
- Mobility and pedestrian exposure dimensions: help connect vehicle pressure to human exposure.
- Normalized z-score/profile values: convert different metrics onto comparable scales so one unit type does not dominate the chart.

**Visual Components**

- Vertical axes: each axis is one traffic dimension.
- Lines crossing axes: each line represents an area profile.
- High or low positions on each axis: show whether an area is above or below the system pattern for that metric.
- Highlight opacity: selected focus areas can appear stronger while others fade.
- Fullscreen record-level version: allows deeper inspection of sampled record-level profiles.

**What Patterns Matter**

Lines that stay high across many axes indicate broad stress. Lines that spike on only one axis indicate a more specific issue. Crossing lines show tradeoffs, such as an area with high congestion but not the highest incident burden.

**Real-World Meaning**

Traffic problems are rarely one-dimensional. This chart helps decision-makers avoid treating all congested areas the same. One area may need capacity attention, while another may need incident management or pedestrian safety review.

**Likely Intended User Interpretation**

Users should look for area fingerprints: which areas are consistently stressed, which have mixed performance, and which are comparatively stable.

**Potential User Confusion**

Parallel coordinates are unfamiliar to many people. Users may not know that each line is an area and each vertical axis is a different measure. Normalized values can also confuse users because they are not raw percentages.

**Glossary Terms Needed**

- Parallel coordinates: a chart where one line crosses many metric axes to show a multi-metric profile.
- Normalized value: a transformed value used to compare different kinds of measurements fairly.
- Area profile: the pattern an area makes across several traffic measures.
- Z-score: a way to describe whether a value is above or below the usual level.

**What This Chart Does NOT Explain**

It does not say why an area is stressed. It does not prove that one metric caused another. It should not be used as a precise ranking unless users understand the axes and normalization.

### T-03 - Monthly Congestion Trend By Area

**Visualization Type**

Multi-series line chart with markers. A line chart fits because congestion changes over time and users need to see movement, slope, and repeated monthly behavior. A table would make trends harder to spot.

**Main Analytical Goal**

This chart helps users understand whether congestion is rising, falling, seasonal, or different across areas. It answers: "How does monthly congestion change over time, and do areas behave differently?"

**Variables / Metrics Used**

- Month: the time period being compared.
- Area: the location group represented by each line.
- Mean congestion: average congestion in that area and month. Higher values mean heavier pressure.

**Visual Components**

- X-axis: calendar month.
- Y-axis: mean congestion percentage.
- Colored lines: one line per area.
- Markers: monthly values along each line.
- Legend: identifies which color belongs to each area.

**What Patterns Matter**

Upward slopes suggest worsening congestion. Downward slopes suggest relief. Repeated peaks in the same months may indicate seasonal or operational cycles. Lines that diverge show inequality between areas.

**Real-World Meaning**

Monthly congestion patterns support planning. If congestion regularly rises late in the year or in specific months, city teams can prepare roadwork, enforcement, public transport support, or communication earlier.

**Likely Intended User Interpretation**

Users should compare both the level and direction of each area. The most important question is not only "which area is highest?" but also "which area is getting worse?"

**Potential User Confusion**

Users may overreact to a single monthly spike. A spike may be temporary, especially if the line returns to normal. Users may also compare areas without checking whether filters changed the active scope.

**Glossary Terms Needed**

- Mean congestion: average congestion across records.
- Trend: the direction of movement over time.
- Seasonal pattern: a pattern that repeats during certain parts of the year.

**What This Chart Does NOT Explain**

It does not identify exact causes of monthly changes. It does not prove seasonality by itself. It does not show daily or hourly variation inside each month.

### T-04 - Weekly Violin Distribution

**Visualization Type**

Violin chart with box-style distribution features, with a boxplot fallback when records are too few. A violin chart was chosen because averages alone can hide whether congestion is stable or highly variable. It shows the shape and spread of congestion for each weekday.

**Main Analytical Goal**

This chart helps users understand whether certain weekdays are consistently congested or simply have occasional extreme congestion. It answers: "Which days have routine pressure, and which days have unstable or heavy-tail congestion?"

**Variables / Metrics Used**

- Day of week: the weekday category.
- Congestion: record-level congestion values for each weekday.
- Median and distribution spread: show typical and unusual values.

**Visual Components**

- X-axis: weekday.
- Y-axis: congestion percentage.
- Violin shape: wider parts mean more records at that congestion level.
- Box/median indicators: show central tendency.
- Upper tails: show occasional severe congestion.

**What Patterns Matter**

Wide shapes mean congestion varies a lot. Tall upper tails mean occasional severe events. A weekday with a high median is routinely stressful. A weekday with low median but long upper tail is usually manageable but sometimes severe.

**Real-World Meaning**

This chart helps users distinguish routine weekly pressure from occasional disruption. That matters for staffing, enforcement, public messaging, and roadwork scheduling.

**Likely Intended User Interpretation**

Users should look beyond the average and ask whether congestion is predictable or unstable on each day.

**Potential User Confusion**

Many people do not know how to read a violin chart. They may think width means congestion size, when it actually means more observations at that level. The fallback boxplot also changes the visual form when data is limited.

**Glossary Terms Needed**

- Violin chart: a distribution chart where width shows how common values are.
- Median: the middle value.
- Distribution: the full spread of values, not just the average.
- Tail: the extreme high or low end of a distribution.

**What This Chart Does NOT Explain**

It does not identify why a weekday is volatile. It does not show exact event causes. It does not prove that a weekday itself causes congestion.

### T-05 - Road Management Priority Quadrant

**Visualization Type**

Quadrant scatter plot. Roads are positioned by congestion and capacity pressure, with reference lines and colored zones. This was chosen because road priority depends on two dimensions at once. A single ranked list would hide whether a road is congested, capacity-constrained, or both.

**Main Analytical Goal**

This chart helps users identify roads that deserve management attention. It answers: "Which roads combine high congestion and high capacity pressure?"

**Variables / Metrics Used**

- Mean congestion: average congestion for a road. Higher is worse.
- Mean capacity utilization: how much road capacity is being used. Higher means less spare capacity.
- Flow instability index: used as point size to show unstable or variable road behavior.
- Mean speed: supporting context for mobility quality.
- Incident count: supporting context for disruption.

**Visual Components**

- X-axis: mean capacity utilization.
- Y-axis: mean congestion.
- Dots: roads.
- Dot size: instability or variation in flow.
- Dot color: road priority category.
- Vertical and horizontal threshold lines: divide the chart into management zones.
- Zone labels: identify baseline, constrained flow, capacity margin, and critical overload.
- Hover details: show road, area, speed, incidents, and capacity context.

**What Patterns Matter**

Dots in the high-congestion and high-capacity zone are the most concerning. Large dots indicate instability. Dots near thresholds are important because small changes could push them into a worse zone.

**Real-World Meaning**

This chart supports road prioritization. Roads in critical overload may need signal review, demand management, enforcement, capacity planning, or incident mitigation.

**Likely Intended User Interpretation**

Users should focus on roads in or near critical overload, then inspect related charts to understand whether the issue is speed collapse, distribution, environmental burden, or area stress.

**Potential User Confusion**

Users may think the quadrant labels are official road classifications. They are analytical categories created from dashboard thresholds. Users may also assume every point is equally important, even though size and location both matter.

**Glossary Terms Needed**

- Quadrant: a chart divided into four zones by reference lines.
- Capacity utilization: how much of a road's usable capacity is being used.
- Critical overload: a condition where congestion and capacity pressure are both high.
- Flow instability: how much road performance varies or becomes unpredictable.

**What This Chart Does NOT Explain**

It does not identify the cause of overload. It does not tell which intervention will work. It does not prove that capacity alone caused congestion.

### T-06 - Environmental Burden Treemap

**Visualization Type**

Hierarchical treemap. Areas contain roads, and block size represents environmental impact. This chart type was chosen because the analysis is about contribution and hierarchy: which areas and roads account for the largest share of burden.

**Main Analytical Goal**

This chart helps users understand where traffic-related environmental burden is concentrated. It answers: "Which roads and areas contribute most to environmental impact in the current scope?"

**Variables / Metrics Used**

- Environmental impact: a derived burden score connected to traffic conditions. Higher values mean greater environmental cost.
- Area: top-level location group.
- Road: nested location inside area.
- Mean congestion: used for severity coloring.

**Visual Components**

- Large rectangles: areas or roads with larger total burden.
- Nested structure: roads sit inside areas to show responsibility within location groups.
- Color intensity: congestion severity.
- Hover values: show burden and congestion context.
- Focus opacity: selected road or area can be visually emphasized while others fade.

**What Patterns Matter**

Large dark blocks are the most important. A large area with one dominant road suggests a specific corridor problem. Many medium blocks inside one area suggest distributed burden.

**Real-World Meaning**

Traffic pressure has environmental consequences. This chart helps users identify where congestion may be linked to higher emissions, exposure, or local environmental stress.

**Likely Intended User Interpretation**

Users should find the largest and most severe blocks, then investigate whether those corridors also show speed collapse, chronic congestion distribution, or pedestrian exposure.

**Potential User Confusion**

Treemaps can be difficult because area size, hierarchy, and color all encode meaning. Users may not know whether size or color matters more. "Environmental impact" also needs a clear definition.

**Glossary Terms Needed**

- Treemap: a chart where rectangle size shows contribution to a total.
- Environmental impact: a derived score representing traffic-related environmental burden.
- Hierarchy: parent-child grouping, such as area -> road.
- Severity color: color used to show how serious a value is.

**What This Chart Does NOT Explain**

It does not measure exact emissions directly unless the underlying score is designed to do so. It does not identify pollution sources outside traffic. It does not prove health impact by itself.

### T-07 - Pedestrian-Adjusted Road Pressure

**Visualization Type**

Diverging horizontal bar chart. Bars show whether each road is above or below the current system baseline. This works because the chart is about deviation, not just raw ranking. A normal bar chart would make it harder to see which roads are worse than the baseline.

**Main Analytical Goal**

This chart helps users understand which roads carry unusually high pressure compared with the current traffic system. It answers: "Which roads are above the baseline, especially where pedestrian exposure matters?"

**Variables / Metrics Used**

- Exclusion delta / congestion deviation: how far a road's congestion is above or below the filtered-scope baseline.
- Road: the corridor being compared.
- Pedestrian and cyclist exposure: context showing why pressure on some roads may be more socially sensitive.
- System baseline: average congestion level in the current filtered scope.

**Visual Components**

- X-axis: deviation from baseline.
- Y-axis: roads.
- Horizontal bars: each road's pressure difference.
- Zero reference line: separates below-baseline from above-baseline roads.
- Bar colors: positive stress, mild stress, or lower-than-baseline condition.
- Optional focus highlight: emphasizes selected roads or areas.

**What Patterns Matter**

Large positive bars deserve attention because they are much worse than the system baseline. Negative bars are comparatively less pressured. A cluster of positive bars in one area may suggest area-level stress.

**Real-World Meaning**

Road pressure matters more when many pedestrians or cyclists are exposed. This chart helps users think beyond vehicles and consider where traffic stress affects vulnerable road users.

**Likely Intended User Interpretation**

Users should identify roads that are not just congested, but unusually congested compared with the current context.

**Potential User Confusion**

Users may interpret negative bars as "good roads" in an absolute sense. They only mean below the current baseline. If filters change, the baseline changes too.

**Glossary Terms Needed**

- Baseline: the comparison level for the current filtered dataset.
- Deviation: how far a value is above or below the baseline.
- Pedestrian exposure: how much walking and cycling activity may be affected.

**What This Chart Does NOT Explain**

It does not prove pedestrian danger. It does not show crash risk directly. It does not explain why a road is above baseline.

### T-08 - Incident Impact On Congestion

**Visualization Type**

Step line with markers. A step chart was chosen because the x-axis is incident count bands, not continuous time. It helps users see whether congestion jumps when incidents move from low to higher bands.

**Main Analytical Goal**

This chart helps users understand how congestion changes across incident levels. It answers: "Does congestion rise sharply when incident counts increase?"

**Variables / Metrics Used**

- Incident count band: grouped number of incidents.
- Mean congestion: average congestion within each incident band.
- Step delta: change between low and higher incident bands.

**Visual Components**

- X-axis: incident count band.
- Y-axis: mean congestion.
- Step line: shows changes between bands as jumps rather than smooth trends.
- Markers: observed band means.
- Threshold line around 75: marks concerning congestion.
- Annotation: highlights the first major change when incident bands increase.

**What Patterns Matter**

A sharp step upward means congestion is sensitive to incidents. A flat line means incident count bands do not strongly separate congestion levels in the current data. A high baseline even with low incidents suggests routine congestion may be the main issue.

**Real-World Meaning**

Incident-sensitive roads may need faster incident response, enforcement, or temporary traffic management. If congestion stays high even without incidents, structural road pressure may be more important.

**Likely Intended User Interpretation**

Users should read this as an incident sensitivity check, not as proof that incidents caused every congestion increase.

**Potential User Confusion**

Users may assume incidents cause congestion because the chart compares them. The chart is observational and grouped. Other conditions may also differ across bands.

**Glossary Terms Needed**

- Incident band: a grouped range of incident counts.
- Step change: a jump from one category to another.
- Sensitivity: how strongly one measure changes when another condition changes.

**What This Chart Does NOT Explain**

It does not prove incidents caused congestion. It does not show incident type, location precision, or response time. It does not identify which incidents mattered most.

### T-09 - Speed Collapse Threshold

**Visualization Type**

Threshold scatter plot. Each point places a traffic record by speed and congestion. Reference lines mark speed and congestion thresholds. This works because speed collapse is a combined condition: high congestion and low speed together.

**Main Analytical Goal**

This chart helps users find conditions where traffic is not only crowded but also slow enough to indicate mobility breakdown. It answers: "Where do high congestion and low speed happen together?"

**Variables / Metrics Used**

- Speed: vehicle speed, usually in km/h. Lower values are worse for mobility.
- Congestion: traffic pressure percentage. Higher values are worse.
- Area: used for color/grouping and focus context.
- Threshold values: around 30 km/h for low speed and 75 for high congestion.

**Visual Components**

- X-axis: speed.
- Y-axis: congestion.
- Dots: traffic records.
- Colors: area or severity grouping.
- Vertical speed threshold line: marks low-speed risk.
- Horizontal congestion threshold line: marks high-congestion risk.
- Critical overload annotation: labels the high-congestion, low-speed zone.
- Sampling annotation: may appear when large data is sampled for readability.

**What Patterns Matter**

Points in the critical zone are the most serious. Dense clusters in that zone suggest repeated speed collapse. Points with high congestion but moderate speed may be congested but still moving. Points with low speed but low congestion may have different causes.

**Real-World Meaning**

Speed collapse affects travel time, emergency response, bus reliability, fuel consumption, and public frustration. It turns abstract congestion into a practical mobility problem.

**Likely Intended User Interpretation**

Users should look for how often and where traffic crosses into the low-speed/high-congestion zone.

**Potential User Confusion**

Users may assume every dot is a road. It is record-level data, so many dots can come from repeated observations. Users may also treat thresholds as absolute laws rather than practical analytical reference lines.

**Glossary Terms Needed**

- Speed collapse: a state where roads are congested and vehicles are moving slowly.
- Threshold: a reference value used to separate normal from concerning conditions.
- Scatter plot: a chart where each dot shows one observation using two measurements.

**What This Chart Does NOT Explain**

It does not say why speed collapsed. It does not identify exact bottlenecks. It does not predict future collapse.

### T-10 - Public Transport Usage Comparison

**Visualization Type**

Grouped bars plus line on a secondary axis. Bars compare congestion and speed by public transport usage quartile, while a line shows incidents. This mixed design works because users need to compare several outcomes across the same usage groups.

**Main Analytical Goal**

This chart helps users inspect whether public transport usage bands align with different traffic outcomes. It answers: "Do areas or records with higher public transport usage show different congestion, speed, or incident levels?"

**Variables / Metrics Used**

- Public transport usage quartile: records grouped from lower to higher public transport usage.
- Mean congestion: average traffic pressure in each quartile.
- Mean speed: average travel speed in each quartile.
- Mean incidents: average incident count in each quartile.

**Visual Components**

- X-axis: public transport usage quartile.
- Left Y-axis: congestion and speed bars.
- Right Y-axis: incident line.
- Grouped bars: allow side-by-side comparison of congestion and speed.
- Line with markers: shows incident levels without adding another bar group.
- Legend: separates metrics.

**What Patterns Matter**

If higher public transport usage aligns with lower congestion or higher speed, that suggests a relationship worth exploring. If incidents rise in high-usage quartiles, those corridors may be busy or complex. Mixed patterns require caution.

**Real-World Meaning**

This chart helps explore whether public transport context relates to road pressure. It can inform mobility planning, but it should not be treated as proof that public transport caused the differences.

**Likely Intended User Interpretation**

Users should compare quartiles and ask whether traffic outcomes improve, worsen, or stay similar as public transport usage changes.

**Potential User Confusion**

The secondary axis can confuse users because incidents are scaled differently from congestion and speed. Quartiles also need explanation.

**Glossary Terms Needed**

- Quartile: one of four groups created by sorting values from low to high.
- Public transport usage: the share or level of public transport use in the records.
- Secondary axis: a second Y-axis used for a metric with a different scale.

**What This Chart Does NOT Explain**

It does not prove that public transport usage reduces or increases congestion. It does not account for all corridor differences, land use, demand, or service quality.

### T-11 - Road Congestion Distribution Profiles

**Visualization Type**

Small-multiple histogram grid. Each panel shows the congestion distribution for one road, sorted by median congestion. This was chosen because many roads must be compared without hiding their distribution shapes.

**Main Analytical Goal**

This chart helps users understand whether road congestion is occasional, frequent, skewed, or chronic. It answers: "Which roads repeatedly operate at high congestion instead of only spiking sometimes?"

**Variables / Metrics Used**

- Road: one panel per road, up to sixteen roads.
- Congestion: record-level congestion values.
- Median congestion: dotted line per road showing the typical middle value.
- Area: used for coloring and focus context.

**Visual Components**

- 4x4 panel grid: compact comparison across roads.
- Histogram bars: show how often congestion falls into ranges.
- Dotted median line: marks each road's typical congestion level.
- Panel titles: identify roads.
- Shared congestion scale: helps compare roads fairly.
- Annotation: explains panel count and median marker.

**What Patterns Matter**

Roads with high medians and right-heavy distributions are chronically stressed. Roads with low medians but long right tails have occasional severe events. Roads with narrow distributions are more predictable.

**Real-World Meaning**

This chart helps separate one-time congestion from repeated corridor problems. Chronic roads may need structural review, while spiky roads may need incident or event management.

**Likely Intended User Interpretation**

Users should compare distribution shape, not just the highest value.

**Potential User Confusion**

Small multiples can feel dense. Users may not know that each mini-chart uses the same congestion scale. They may also mistake a high bar count for high congestion unless they read the x-axis.

**Glossary Terms Needed**

- Histogram: a chart showing how often values fall into ranges.
- Median: the middle value.
- Right-skewed: many values are lower, but some extend far into high values.
- Chronic congestion: congestion that appears repeatedly, not just once.

**What This Chart Does NOT Explain**

It does not identify exact causes of road-level distributions. It does not show time order. It does not explain whether high congestion occurred during specific incidents or periods.

### T-12 - Weather x Roadwork Heatmap

**Visualization Type**

Categorical heatmap. Weather conditions and roadwork status form a grid, and color shows mean congestion. This chart type works because the question involves two categorical conditions at the same time.

**Main Analytical Goal**

This chart helps users understand which weather and roadwork combinations are associated with higher congestion. It answers: "Which operational conditions are most risky for traffic flow?"

**Variables / Metrics Used**

- Weather condition: categorical weather state.
- Roadwork activity/status: whether or how roadwork is present.
- Mean congestion: average congestion for each weather-roadwork combination.
- Incident context: available in transform output as supporting context.

**Visual Components**

- X-axis: roadwork status.
- Y-axis: weather condition.
- Cell color: mean congestion.
- Color scale: darker/hotter colors indicate higher congestion.
- Hover text: shows the exact combination and congestion value.

**What Patterns Matter**

Dark cells identify high-risk combinations. A whole dark row suggests one weather condition is broadly difficult. A dark column suggests roadwork status matters across weather types. Isolated dark cells suggest specific operational combinations.

**Real-World Meaning**

This chart supports roadwork scheduling and traffic operations. If certain weather-roadwork combinations are repeatedly stressful, agencies may avoid work during those conditions or prepare mitigation.

**Likely Intended User Interpretation**

Users should look for combinations that create high average congestion and treat them as planning risk signals.

**Potential User Confusion**

Users may think weather or roadwork caused the congestion. The chart only shows association. Sparse combinations may be less reliable if there are few records.

**Glossary Terms Needed**

- Heatmap: a grid where color represents a value.
- Roadwork status: whether road construction or maintenance is active.
- Operational risk: a condition that may make traffic harder to manage.

**What This Chart Does NOT Explain**

It does not prove causality. It does not show exact roadwork locations or severity. It does not include all possible weather impacts.

### T-13 - Area Stress Profile

**Visualization Type**

Heatmap by default, with radar chart mode for focused comparison. The heatmap is good for scanning many areas across many stress dimensions. Radar mode is useful when comparing the shape of a few area profiles.

**Main Analytical Goal**

This chart helps users understand how areas differ across multiple traffic stress factors. It answers: "Is an area stressed because of congestion, speed, incidents, capacity, environment, or a combination?"

**Variables / Metrics Used**

- Normalized stress index: converts each metric to a 0-100 comparison scale.
- Area: each row or radar shape.
- Stress dimensions: congestion, speed pressure, capacity, incidents, environmental impact, and related traffic indicators.
- Raw metric values: displayed as text/hover context where available.

**Visual Components**

- Heatmap rows: areas.
- Heatmap columns: stress dimensions.
- Cell color: normalized stress level.
- Cell labels: raw values or readable metric values.
- Radar axes: stress dimensions arranged around a circle.
- Radar shapes: area profiles across dimensions.
- Focus highlighting: selected area can be emphasized.

**What Patterns Matter**

Dark rows across many columns indicate broad stress. Dark cells in only one column indicate a specific issue. Radar shapes that expand widely show broad stress; narrow shapes show lower overall pressure.

**Real-World Meaning**

Area stress is multidimensional. This chart helps city teams decide whether an area needs broad intervention or a targeted response, such as incident control, capacity planning, or environmental review.

**Likely Intended User Interpretation**

Users should identify the type of stress, not only the most stressed area.

**Potential User Confusion**

Normalized values may be mistaken for raw percentages. Radar charts can exaggerate visual area, so users should compare axis values carefully.

**Glossary Terms Needed**

- Stress profile: a multi-metric picture of how an area is performing.
- Normalized index: a converted score used for fair comparison.
- Radar chart: a chart where each axis is a metric and shapes show profiles.

**What This Chart Does NOT Explain**

It does not prove which stress factor caused another. It does not replace detailed engineering analysis. It does not show exact street-level interventions.

### T-14 - Traffic Volume And Congestion Density

**Visualization Type**

2D density heatmap / histogram. Traffic volume and congestion form the axes, and color shows where records are concentrated. This works better than a raw scatter plot when there are many records because it reduces overplotting.

**Main Analytical Goal**

This chart helps users see whether high traffic volume commonly occurs with high congestion. It answers: "Where do many records cluster in the volume-congestion relationship?"

**Variables / Metrics Used**

- Traffic volume: amount of observed traffic activity.
- Congestion: traffic pressure percentage.
- Density/count: how many records fall into each volume-congestion bin.

**Visual Components**

- X-axis: traffic volume.
- Y-axis: congestion.
- Colored density cells: more intense cells mean more records in that region.
- Color scale: highlights common combinations.
- Sampling annotation: may appear when the chart uses a sample for readability.

**What Patterns Matter**

Dense high-volume/high-congestion regions indicate sustained corridor load. High-volume/low-congestion regions may show roads handling demand well. Low-volume/high-congestion clusters may suggest localized bottlenecks or incidents.

**Real-World Meaning**

The chart helps distinguish demand-related pressure from other congestion patterns. It can guide deeper investigation into corridors where high demand regularly turns into high congestion.

**Likely Intended User Interpretation**

Users should focus on clusters, not isolated cells. The key question is where congestion repeatedly occurs under volume pressure.

**Potential User Confusion**

Users may think color means congestion severity, but it primarily represents density/count of records in a bin. The axes still show the actual volume and congestion relationship.

**Glossary Terms Needed**

- Density: how many observations are concentrated in an area of the chart.
- Bin: a grouped range of values.
- Overplotting: when too many dots overlap and become hard to read.

**What This Chart Does NOT Explain**

It does not show individual roads unless filters narrow the data. It does not prove that traffic volume alone caused congestion. It does not show time sequence.

### T-15 - Area-Month Congestion Heatmap

**Visualization Type**

Area-by-month heatmap. This type was chosen because users need to compare two dimensions at once: where congestion happens and when it happens.

**Main Analytical Goal**

This chart helps users find recurring temporal hotspots. It answers: "Which areas are congested in which months?"

**Variables / Metrics Used**

- Area: location group.
- Month: time period.
- Mean congestion: average area-month congestion.
- Incidents: supporting hover context.

**Visual Components**

- X-axis: month.
- Y-axis: area.
- Cell color: mean congestion.
- Colorbar: congestion percentage.
- Hover details: area, month, congestion, and incident count.
- Clickable cells: can set temporary focus or support filtering behavior depending on interaction mode.

**What Patterns Matter**

Dark blocks show area-month stress. Repeated dark cells across a row mean an area is persistently stressed. Repeated dark cells down a column mean many areas are stressed in the same month.

**Real-World Meaning**

This chart supports seasonal and area-specific planning. It helps users see whether congestion is a recurring monthly issue or a localized temporary issue.

**Likely Intended User Interpretation**

Users should identify where and when congestion concentrates, then use related charts to inspect causes or road-level details.

**Potential User Confusion**

Users may assume clicking a cell always filters the whole dashboard. Depending on mode, it may create temporary focus rather than a global filter.

**Glossary Terms Needed**

- Heatmap: a grid where color represents a value.
- Area-month: one area during one month.
- Temporary focus: a click-based context that highlights or scopes some charts without changing global filters.

**What This Chart Does NOT Explain**

It does not show daily variation within a month. It does not prove why a month is high. It does not predict future month congestion.

## AQI Dashboard

### A-01 - PM2.5 Burden and Category Mix

**Visualization Type**

Categorical bar chart. Each bar counts days in an AQI category. This works because the chart is about how often each air-quality severity category occurs. A line chart would be worse because the goal is category mix, not time order.

**Main Analytical Goal**

This chart helps users understand the overall pollution burden in plain severity categories. It answers: "How often is air quality good, moderate, poor, very poor, or severe in the current scope?"

**Variables / Metrics Used**

- AQI category: human-readable pollution severity group.
- Day count: number of days or records in each category.
- PM2.5 context: category values are derived from PM2.5 thresholds.

**Visual Components**

- X-axis: AQI categories from cleaner to more polluted.
- Y-axis: day count.
- Bars: frequency of each category.
- Category colors: familiar severity coloring from cleaner to more dangerous.
- Hover text: category and day count.

**What Patterns Matter**

Tall bars in Poor, Very Poor, or Severe categories indicate frequent unhealthy air. A distribution concentrated in Good or Satisfactory categories suggests cleaner conditions. A wide mix across categories suggests unstable air quality.

**Real-World Meaning**

People understand categories more easily than raw PM2.5 numbers. This chart tells users whether residents are mostly experiencing acceptable air or repeated unhealthy exposure.

**Likely Intended User Interpretation**

Users should read this as the AQI overview: how serious is the pollution burden in everyday terms?

**Potential User Confusion**

Users may not know how PM2.5 maps to AQI categories. They may also think category counts are independent of the selected filters, when filters directly change the category mix.

**Glossary Terms Needed**

- PM2.5: tiny airborne particles that can affect breathing and health.
- AQI category: a label that groups pollution levels into severity bands.
- Day count: how many days fall into a category.

**What This Chart Does NOT Explain**

It does not identify pollution sources. It does not show exact daily timing. It does not prove health outcomes for individuals.

### A-02 - Weekly PM2.5 Calendar

**Visualization Type**

Weekly calendar heatmap. Weeks are shown across the x-axis and years on the y-axis, with color representing PM2.5 severity. This works because users need to see pollution persistence and timing across years.

**Main Analytical Goal**

This chart helps users locate polluted weeks and repeated seasonal blocks. It answers: "When during the year does PM2.5 become high, and does that pattern repeat across years?"

**Variables / Metrics Used**

- Week of year: weekly time unit.
- Year: yearly comparison.
- Mean PM2.5: average pollution level for each week.
- Highlighted week/year: optional temporary focus from chart interaction.

**Visual Components**

- X-axis: week number.
- Y-axis: year.
- Cell color: PM2.5 severity using AQI-style colors.
- Colorbar: PM2.5 value scale.
- Highlight opacity: selected week can remain strong while others fade.
- Empty dark cells: missing or unavailable week values.

**What Patterns Matter**

Long bands of high-color cells show persistent pollution episodes. Repeated high weeks across years suggest seasonal pollution behavior. Isolated high cells suggest short episodes.

**Real-World Meaning**

Weekly persistence matters because health risk increases when poor air lasts for many days. This chart helps users see exposure duration, not just isolated peaks.

**Likely Intended User Interpretation**

Users should identify polluted blocks and compare whether they repeat across years.

**Potential User Confusion**

Week numbers are less intuitive than month names. Users may also need help understanding that color represents PM2.5, not record count.

**Glossary Terms Needed**

- Calendar heatmap: a time grid where color shows intensity.
- PM2.5: fine particulate pollution.
- Persistence: pollution staying high over a period, not just one day.

**What This Chart Does NOT Explain**

It does not explain the source of weekly pollution. It does not show hourly variation. It does not prove a seasonal cause by itself.

### A-03 - Seasonal PM2.5 Ridgeline

**Visualization Type**

Seasonal ridgeline density chart. Each season has a filled distribution shape showing where daily PM2.5 values commonly fall. This works because it shows distribution shape, not just seasonal average.

**Main Analytical Goal**

This chart helps users understand how pollution differs by season. It answers: "Which seasons have cleaner air, which have high-pollution tails, and how spread out are PM2.5 values?"

**Variables / Metrics Used**

- Season: Winter, Spring, Monsoon, Post-Monsoon.
- Daily PM2.5 values: pollution measurements by day.
- Density: where values are most common within each season.

**Visual Components**

- X-axis: PM2.5 level.
- Y-axis: season labels.
- Filled ridgeline shapes: seasonal distribution of PM2.5.
- Shape width/height: where values are more common.
- Annotation: points users toward winter accumulation and monsoon relief.

**What Patterns Matter**

A season shifted to the right has higher PM2.5. A long right tail means occasional severe pollution. A narrow shape means values are consistent; a wide shape means conditions vary.

**Real-World Meaning**

Seasonal pollution patterns help users understand when residents may face higher exposure risk and when atmospheric conditions may provide relief.

**Likely Intended User Interpretation**

Users should compare seasonal shapes and notice whether winter or post-monsoon periods carry more high-pollution days.

**Potential User Confusion**

Ridgeline charts are uncommon. Users may not know that the shape shows how common PM2.5 values are, not a time trend.

**Glossary Terms Needed**

- Ridgeline chart: stacked distribution shapes used to compare groups.
- Density: how common values are in a range.
- Right tail: the high-value end of a distribution.
- Monsoon relief: lower pollution associated with rain or atmospheric mixing during monsoon periods.

**What This Chart Does NOT Explain**

It does not identify exact pollution sources. It does not show daily sequence inside a season. It does not prove why a season is polluted.

### A-04 - Monthly PM2.5 Heatmap

**Visualization Type**

Month-by-year heatmap. This type was chosen because it shows seasonal and multi-year rhythm in one compact grid.

**Main Analytical Goal**

This chart helps users understand when pollution is high at monthly scale. It answers: "Which months and years had higher mean PM2.5?"

**Variables / Metrics Used**

- Month: calendar month.
- Year: comparison year.
- Mean PM2.5: average pollution for each month-year cell.

**Visual Components**

- X-axis: month names.
- Y-axis: year.
- Cell color: mean PM2.5 severity.
- Colorbar: PM2.5 scale.
- Hover details: exact month, year, and PM2.5 value.

**What Patterns Matter**

Dark clusters in the same months across years suggest recurring seasonal pollution. Dark cells isolated to one year may indicate a specific year episode. Lighter monsoon months may show seasonal relief.

**Real-World Meaning**

Monthly patterns help public agencies prepare seasonal responses and help the public understand when air quality risk is more likely.

**Likely Intended User Interpretation**

Users should identify recurring high-PM2.5 months and compare whether pollution burden is improving or worsening across years.

**Potential User Confusion**

Monthly averages hide daily spikes. Users may think a moderate month means every day was moderate, which may not be true.

**Glossary Terms Needed**

- Mean PM2.5: average fine-particle pollution level.
- Heatmap: a color-coded grid.
- Seasonal cycle: repeated pattern across parts of the year.

**What This Chart Does NOT Explain**

It does not show daily persistence. It does not identify pollution sources. It does not show weather drivers directly.

### A-05 - Pollution Persistence Series

**Visualization Type**

Time-series line chart with raw daily PM2.5 and a 7-day rolling mean. A line chart was chosen because pollution changes day by day and users need to see spikes, persistence, and longer movement.

**Main Analytical Goal**

This chart helps users understand whether pollution is brief or sustained. It answers: "Does PM2.5 spike for a day, or does it stay high for many days?"

**Variables / Metrics Used**

- Date: daily time axis.
- Daily PM2.5: observed fine-particle pollution for each day.
- 7-day rolling mean: smoothed average that reduces daily noise.
- Elevated band 60-120 ug/m3: a visible caution range.
- Severe threshold 250 ug/m3: high-risk reference line.

**Visual Components**

- X-axis: date.
- Y-axis: PM2.5.
- Thin daily line: raw daily pollution movement.
- Thicker rolling mean line: sustained trend over about a week.
- Shaded band: elevated pollution range.
- Dotted severe line: very high pollution reference.
- Legend: separates daily values from rolling mean.

**What Patterns Matter**

Sharp spikes show acute pollution days. A rolling mean that stays high shows sustained exposure. Repeated waves suggest recurring pollution episodes. A rolling line that remains elevated after spikes means pollution did not quickly return to normal.

**Real-World Meaning**

Sustained pollution is important for public health because repeated exposure can matter more than a single bad day. This chart helps users understand duration and persistence.

**Likely Intended User Interpretation**

Users should compare daily volatility with the smoother trend and ask whether pollution is temporary or persistent.

**Potential User Confusion**

Users may not understand rolling mean. They may also focus only on the highest spike and miss sustained moderate-to-high pollution.

**Glossary Terms Needed**

- Rolling mean: an average over recent days that smooths noisy daily changes.
- PM2.5: tiny pollution particles in the air.
- Severe threshold: a reference level for very unhealthy pollution.
- Persistence: pollution remaining high over time.

**What This Chart Does NOT Explain**

It does not identify pollution sources. It does not prove why pollution stayed high. It does not predict future air quality.

### A-06 - Pressure and Visibility PM2.5 Density

**Visualization Type**

2D density heatmap or seasonal drift line chart depending on the dataset passed to the renderer. The main density view uses sea-level pressure and vertical visibility as axes, with color showing average PM2.5. This works because stagnation-like pollution often depends on weather conditions occurring together.

**Main Analytical Goal**

This chart helps users understand atmospheric context for pollution. It answers: "Under which pressure and visibility conditions does PM2.5 tend to be higher?"

**Variables / Metrics Used**

- Sea-level pressure: atmospheric pressure adjusted to sea level.
- Vertical visibility: how clearly air allows vertical visibility; lower visibility can indicate haze or pollution.
- PM2.5: pollution level averaged in each pressure-visibility cell.
- Season/year drift: alternate view showing seasonal mean PM2.5 over years.

**Visual Components**

- X-axis: sea-level pressure.
- Y-axis: vertical visibility.
- Cell color: average PM2.5 for similar conditions.
- Color scale: darker/cooler to warmer/severe PM2.5.
- Alternate lines: seasons over year when seasonal drift data is used.
- Highlight opacity: can emphasize selected season.

**What Patterns Matter**

High PM2.5 cells under low visibility or certain pressure bands suggest stagnation-like conditions. Seasonal lines rising over years suggest worsening seasonal burden; falling lines suggest relief.

**Real-World Meaning**

Air pollution is influenced by atmospheric conditions. This chart helps users see when weather may trap or disperse pollution, without claiming weather is the only cause.

**Likely Intended User Interpretation**

Users should connect high PM2.5 with weather context and then inspect regime or season-pressure charts for more explanation.

**Potential User Confusion**

Sea-level pressure and vertical visibility are technical terms. Users may also assume weather conditions directly caused PM2.5, even though the chart shows association.

**Glossary Terms Needed**

- Sea-level pressure: air pressure normalized so different elevations can be compared.
- Vertical visibility: how far upward through the air visibility remains clear.
- Stagnation: weather conditions where pollution can become trapped.
- Density heatmap: a grid summarizing many observations.

**What This Chart Does NOT Explain**

It does not identify pollution source. It does not prove atmospheric causality. It does not include every weather variable or emissions factor.

### A-07 - PM2.5 Category Weather Profile

**Visualization Type**

Radar chart comparing normalized weather profiles for Good, Moderate, and Severe PM2.5 categories. This was chosen because the goal is to compare the shape of multiple weather conditions across categories.

**Main Analytical Goal**

This chart helps users understand how weather conditions differ across pollution severity categories. It answers: "What weather profile tends to appear with cleaner or more polluted air?"

**Variables / Metrics Used**

- Temperature: weather warmth measure.
- Minimum temperature: low temperature context.
- Humidity: moisture in the air.
- Visibility: clarity of the air.
- Wind: ventilation or movement of air.
- Sea-level pressure: pressure regime context.
- Normalized 0-100 values: used so different weather units can be compared on one radar.

**Visual Components**

- Circular axes: weather variables.
- Filled shapes: category weather profiles.
- Colors: PM2.5 category severity.
- Radial scale 0-100: normalized metric strength.
- Legend: identifies Good, Moderate, and Severe profiles.

**What Patterns Matter**

Large differences between shapes show weather variables that separate pollution categories. If Severe has lower visibility and different pressure profile, that may suggest stagnation context. Overlapping shapes suggest categories are not strongly separated by those metrics.

**Real-World Meaning**

The chart helps people understand that air quality is connected to weather context, not only emissions. It supports cautious interpretation of atmospheric conditions.

**Likely Intended User Interpretation**

Users should compare category shapes and ask which weather factors look different between cleaner and more polluted conditions.

**Potential User Confusion**

Radar charts can look dramatic even when differences are small. Normalized values are not raw units, so users need explanation.

**Glossary Terms Needed**

- Radar chart: a circular chart comparing several variables at once.
- Normalized value: a converted value on a shared 0-100 scale.
- Visibility: how clear the air is.
- Humidity: moisture level in the air.

**What This Chart Does NOT Explain**

It does not prove weather caused pollution. It does not show exact PM2.5 values. It does not include all possible atmospheric factors.

### A-08 - Minimum Temperature vs PM2.5

**Visualization Type**

Category-colored scatter plot, with a category-transition heatmap fallback when transition-style data is passed. The scatter was chosen because users need to inspect a relationship between a continuous weather variable and pollution.

**Main Analytical Goal**

This chart helps users understand whether lower minimum temperatures align with higher PM2.5 categories. It answers: "Do colder minimum temperatures appear with more polluted days?"

**Variables / Metrics Used**

- Minimum temperature: the lowest temperature for the day or record.
- PM2.5: fine-particle pollution level.
- AQI category: pollution severity group used for point color.
- Category transitions: fallback matrix showing movement from one AQI category to another.

**Visual Components**

- X-axis: minimum temperature.
- Y-axis: PM2.5.
- Dots: observations.
- Dot colors: AQI category.
- Legend: maps colors to categories.
- Transition heatmap fallback: from-category and to-category axes with counts in cells.

**What Patterns Matter**

If high PM2.5 points cluster at lower temperatures, users may infer a temperature-linked pattern worth investigating. Mixed clouds mean temperature alone is not enough. In transition mode, large off-diagonal counts mean category instability.

**Real-World Meaning**

Temperature can be part of pollution context, especially during seasons where cooler conditions may coincide with accumulation. This chart helps users see that relationship without overstating it.

**Likely Intended User Interpretation**

Users should treat the pattern as an exploratory relationship, not a proof of cause.

**Potential User Confusion**

Scatter plots can look noisy. Users may see a loose cluster and assume causation. Category colors also need a clear legend.

**Glossary Terms Needed**

- Minimum temperature: the lowest temperature in the period.
- Scatter plot: a chart where each dot is one observation.
- AQI category: pollution severity label.
- Category transition: movement from one air-quality category to another over time.

**What This Chart Does NOT Explain**

It does not prove cold weather causes pollution. It does not account for emissions, wind, humidity, or pressure by itself. It does not identify pollution sources.

### A-09 - Pressure Band PM2.5 Comparison

**Visualization Type**

Grouped bar chart by sea-level pressure band and season. This works because users need to compare mean PM2.5 across pressure categories while keeping seasonal context visible.

**Main Analytical Goal**

This chart helps users understand whether PM2.5 differs across pressure regimes and seasons. It answers: "Are some pressure bands associated with higher pollution in certain seasons?"

**Variables / Metrics Used**

- Sea-level pressure band: grouped pressure range.
- Season: seasonal category.
- Mean PM2.5: average pollution in that pressure-season group.

**Visual Components**

- X-axis: pressure band.
- Y-axis: mean PM2.5.
- Grouped bars: seasonal comparison within each pressure band.
- Colors: season.
- Legend: identifies seasons.

**What Patterns Matter**

Tall bars in certain pressure bands show higher pollution associations. Seasonal differences within the same band show whether pressure matters differently across the year.

**Real-World Meaning**

Pressure regimes can be part of pollution accumulation or dispersion context. This chart helps users connect weather patterns to pollution burden.

**Likely Intended User Interpretation**

Users should compare seasons within each pressure band and pressure bands within each season.

**Potential User Confusion**

Pressure bands are technical. Users may also interpret bar differences as causal proof rather than association.

**Glossary Terms Needed**

- Sea-level pressure: atmospheric pressure adjusted for comparison.
- Pressure band: a grouped pressure range.
- Mean PM2.5: average fine-particle pollution.

**What This Chart Does NOT Explain**

It does not prove pressure caused PM2.5 changes. It does not show daily timing or emissions. It does not explain why pressure differs.

### A-10 - Wind Speed Band Comparison

**Visualization Type**

Grouped bar chart by wind speed band and season. It is appropriate because the chart compares PM2.5 averages across categorical wind ranges while preserving seasonal differences.

**Main Analytical Goal**

This chart helps users inspect whether stronger or weaker wind bands align with different pollution levels. It answers: "Does PM2.5 tend to be lower when wind is stronger?"

**Variables / Metrics Used**

- Wind speed band: grouped wind-speed range.
- Season: seasonal category.
- Mean PM2.5: average pollution in each wind-season group.

**Visual Components**

- X-axis: wind speed band.
- Y-axis: mean PM2.5.
- Grouped bars: seasonal comparison.
- Colors and legend: season identity.

**What Patterns Matter**

Lower PM2.5 in stronger wind bands may suggest dispersion. High PM2.5 even with wind suggests other factors may dominate. Seasonal differences show that wind context may not behave the same all year.

**Real-World Meaning**

Wind can help disperse pollution. This chart gives users a simple way to see whether the dataset reflects that idea.

**Likely Intended User Interpretation**

Users should interpret wind as one environmental factor, not the entire pollution explanation.

**Potential User Confusion**

Users may think wind alone controls pollution. They may also need help understanding wind bands as grouped ranges.

**Glossary Terms Needed**

- Wind band: a grouped range of wind speeds.
- Dispersion: pollution spreading out or being carried away by air movement.
- Mean PM2.5: average particle pollution.

**What This Chart Does NOT Explain**

It does not prove wind caused lower pollution. It does not show wind direction. It does not include emissions sources or local terrain effects.

### A-11 - Gust Ratio Quintile Check

**Visualization Type**

Bar chart with uncertainty/error bands. Gust ratio is grouped into quintiles, and each bar shows mean PM2.5. Error bands show uncertainty around the mean.

**Main Analytical Goal**

This chart helps users test whether gustiness has a meaningful relationship with PM2.5. It answers: "Do days with different gust-ratio levels show different average pollution?"

**Variables / Metrics Used**

- Gust ratio quintile: five groups from lower to higher gust ratio.
- Mean PM2.5: average pollution in each quintile.
- Confidence interval: uncertainty range around the mean.

**Visual Components**

- X-axis: gust ratio quintile.
- Y-axis: mean PM2.5.
- Bars: average pollution for each quintile.
- Error bars: uncertainty range.
- Hover text: mean PM2.5.

**What Patterns Matter**

A steady increase or decrease across quintiles suggests a relationship worth investigating. Wide error bars mean results are less certain. Overlapping error bars mean differences may not be meaningful.

**Real-World Meaning**

Gustiness may relate to ventilation or mixing. This chart helps users check whether that weather behavior aligns with pollution differences.

**Likely Intended User Interpretation**

Users should look for a clear pattern and also check uncertainty before drawing conclusions.

**Potential User Confusion**

Quintiles and confidence intervals are technical. Users may ignore error bars and overstate small differences.

**Glossary Terms Needed**

- Gust ratio: a measure comparing gust behavior with normal wind.
- Quintile: one of five equal-sized groups after sorting values.
- Confidence interval: a range showing uncertainty around an estimate.

**What This Chart Does NOT Explain**

It does not prove gustiness caused pollution changes. It does not show wind direction or local airflow. It does not prove a relationship if error ranges are wide.

### A-12 - Temperature Spread Bands

**Visualization Type**

Bar chart comparing PM2.5 across diurnal temperature spread bands. This works because the question is whether grouped temperature-spread conditions correspond to different pollution averages.

**Main Analytical Goal**

This chart helps users understand whether day-night temperature difference is associated with PM2.5 levels. It answers: "Do days with larger or smaller temperature spread show different pollution?"

**Variables / Metrics Used**

- Diurnal temperature spread: difference between daily high and low temperature.
- Spread band: grouped range of temperature spread.
- Mean PM2.5: average pollution for each band.
- Median PM2.5: supporting typical value in hover text.

**Visual Components**

- X-axis: temperature spread band.
- Y-axis: mean PM2.5.
- Bars: average pollution per band.
- Hover text: mean and median PM2.5.

**What Patterns Matter**

Large differences between bars suggest temperature spread may matter. Similar bars suggest little separation. Mean and median differences may reveal skewed values.

**Real-World Meaning**

Temperature spread can relate to atmospheric stability. This chart helps users explore whether stability-like conditions align with pollution burden.

**Likely Intended User Interpretation**

Users should treat this as a weather-context comparison, not a causal finding.

**Potential User Confusion**

Diurnal spread is not an everyday term. Users may also assume a high bar means every day in that band was polluted.

**Glossary Terms Needed**

- Diurnal temperature spread: the difference between the day's high and low temperature.
- Mean: average value.
- Median: middle value.
- Atmospheric stability: conditions where air mixing may be limited.

**What This Chart Does NOT Explain**

It does not prove temperature spread caused pollution. It does not show daily sequence. It does not include emissions or wind direction.

### A-13 - Rule-Based Atmospheric Regimes

**Visualization Type**

Regime-colored scatter plot. Each point is placed by vertical visibility and PM2.5, and colored by a rule-based atmospheric regime. This works because users need to compare interpretable weather-pollution groups.

**Main Analytical Goal**

This chart helps users understand how different rule-based atmospheric states relate to pollution. It answers: "Which weather-condition groups are associated with higher or lower PM2.5?"

**Variables / Metrics Used**

- Vertical visibility: air clarity measure.
- PM2.5: pollution level.
- Regime label: rule-based category such as Baseline, Stagnation Trap, Dispersive Relief, or Pressure Lock.
- Focus regime: optional selected regime highlight.

**Visual Components**

- X-axis: vertical visibility.
- Y-axis: PM2.5.
- Dots: observations.
- Colors: atmospheric regime.
- Legend: regime names.
- Highlight styling: selected regime points become clearer while others fade.

**What Patterns Matter**

Regime clusters with high PM2.5 are important. Stagnation Trap points with low visibility and high PM2.5 suggest trapped pollution conditions. Dispersive Relief points with lower PM2.5 may suggest cleaner ventilation context.

**Real-World Meaning**

Rule-based regimes make weather-pollution relationships easier to understand. They turn technical measurements into interpretable environmental states.

**Likely Intended User Interpretation**

Users should compare regimes and ask which conditions are most associated with polluted air.

**Potential User Confusion**

Users may think regimes are predictions or official classifications. They are rule-based analytical labels, not an AI model.

**Glossary Terms Needed**

- Atmospheric regime: a named group of weather conditions.
- Stagnation trap: conditions where pollution may remain trapped near the surface.
- Dispersive relief: conditions where air movement may help reduce pollution.
- Pressure lock: pressure conditions associated with pollution accumulation.

**What This Chart Does NOT Explain**

It does not prove regimes caused pollution. It does not identify emission sources. It does not predict future regime changes.

### A-14 - Season x Pressure Grid

**Visualization Type**

Season-by-pressure heatmap. This is appropriate because it compares two categorical dimensions and one continuous pollution value in a compact grid.

**Main Analytical Goal**

This chart helps users understand how season and pressure band combine with PM2.5. It answers: "Which season-pressure combinations have the highest pollution?"

**Variables / Metrics Used**

- Season: seasonal category.
- SLP band: grouped sea-level pressure range.
- Mean PM2.5: average pollution for each season-pressure cell.

**Visual Components**

- X-axis: pressure band.
- Y-axis: season.
- Cell color: mean PM2.5.
- Hover details: season, pressure band, and PM2.5.

**What Patterns Matter**

Dark cells show high-pollution combinations. A dark row indicates a season with high pollution across pressure bands. A dark column indicates a pressure band that is high across seasons.

**Real-World Meaning**

This chart helps explain when atmospheric pressure and season align with pollution burden. It supports seasonal preparedness and environmental interpretation.

**Likely Intended User Interpretation**

Users should identify the most concerning season-pressure combinations and compare them with A-06 and A-13.

**Potential User Confusion**

SLP is technical. Users may also interpret a dark cell as proof of cause rather than a summarized association.

**Glossary Terms Needed**

- SLP: sea-level pressure.
- Pressure band: grouped pressure range.
- Heatmap: grid where color shows value.

**What This Chart Does NOT Explain**

It does not show daily variation inside each cell. It does not prove pressure caused pollution. It does not include wind, visibility, or emissions directly.

### A-15 - Weather Variable Pairplot

**Visualization Type**

Multivariate pairplot matrix with density plots on the diagonal and scatter plots off the diagonal. If there are too few rows, it falls back to a correlation heatmap. This was chosen because the chart is for broad exploratory comparison among many weather variables and PM2.5.

**Main Analytical Goal**

This chart helps advanced users explore many pairwise relationships at once. It answers: "Which weather variables appear related to PM2.5 or to each other?"

**Variables / Metrics Used**

- Temperature.
- Minimum temperature.
- Sea-level pressure.
- Humidity.
- Vertical visibility.
- Wind.
- PM2.5.
- AQI category: used for scatter point color when available.
- Correlation: fallback measure showing strength and direction of linear relationships.

**Visual Components**

- Matrix layout: each row and column is a variable.
- Diagonal cells: distribution of each variable.
- Off-diagonal cells: scatter plots comparing two variables.
- Point colors: AQI category.
- Small points: many observations sampled for readability.
- Correlation heatmap fallback: colored cells with correlation numbers when scatter matrix is not suitable.

**What Patterns Matter**

Clear diagonal distribution shapes show how each variable behaves. Sloped scatter clouds suggest relationships. Category colors clustering in certain regions show where high or low pollution conditions appear. Strong positive or negative correlations in fallback view indicate relationships worth investigating.

**Real-World Meaning**

Air quality is influenced by many interacting weather conditions. This chart gives analysts a broad map for deeper investigation, helping them decide which relationships deserve more focused charts.

**Likely Intended User Interpretation**

Users should treat this as an exploratory lab view. It helps find questions, not final answers.

**Potential User Confusion**

Pairplots are complex and can overwhelm non-technical users. Correlation is often misunderstood as causation. Small panels may be hard to read without explanation.

**Glossary Terms Needed**

- Pairplot: a matrix comparing many variables two at a time.
- Correlation: a number showing how strongly two variables move together.
- Distribution: the spread of values for one variable.
- Scatter plot: dots showing paired values.
- Sampling: showing a subset of records to keep the chart readable.

**What This Chart Does NOT Explain**

It does not prove causality. It does not identify pollution sources. It does not provide a final model or prediction. It does not replace focused domain analysis.

## KPI Cards and Metric Strips

### Traffic KPI Cards

**Visualization Type**

Compact KPI cards and metric strips. These are summary tiles that show one metric at a time, often with short supporting notes. They work because users need fast orientation before reading detailed charts.

**Main Analytical Goal**

Traffic KPI cards answer: "What is the current traffic condition in the filtered scope?" They provide high-level monitoring before users inspect chart-level detail.

**Variables / Metrics Used**

- System Congestion Index: average traffic pressure. High values mean the network is more congested.
- Capacity Saturation Rate: share of near-full-capacity records. High values mean little operational headroom.
- Active Incidents: total incidents in scope. High values may indicate disruption or risk.
- Average Speed / Mean Speed: average vehicle speed. Low values indicate poorer mobility.
- Pedestrian Exposure: pedestrian and cyclist activity context. High values mean road stress may affect more vulnerable users.
- Public Transport Usage: public transport usage level. Helps compare road pressure with mobility mix.
- Signal Compliance: signal-following behavior. Low compliance may indicate operational disorder.
- Environmental Impact: derived burden connected to traffic stress. High values mean broader cost.
- Peak Month Congestion: worst monthly congestion.
- Trend Direction: recent movement compared with earlier months.
- Volatility Index: how unstable congestion is across time.
- Critical Overload Roads: number of roads above severe congestion thresholds.
- Threshold Crossings: how often records cross critical congestion levels.

**Visual Components**

- Numeric value: main KPI result.
- Label: tells users what metric is shown.
- Supporting note: explains the meaning or caution.
- Delta or context text where present: helps compare against baseline or previous period.
- Styling: compact display keeps KPIs secondary to charts but useful for orientation.

**What Patterns Matter**

High congestion plus low speed is more serious than high congestion alone. High capacity saturation suggests fragility. High volatility means averages may hide unstable conditions. Many critical overload roads means stress is distributed rather than isolated.

**Real-World Meaning**

KPI cards translate detailed traffic data into operational signals for planning, monitoring, and communication.

**Likely Intended User Interpretation**

Users should use KPIs as the first diagnostic layer, then open charts to understand where and why values are high.

**Potential User Confusion**

Users may treat KPIs as absolute citywide truth even when filters are active. They may also misunderstand derived metrics like environmental impact or volatility.

**Glossary Terms Needed**

- KPI: a key performance indicator, or summary metric.
- Saturation: being close to capacity.
- Volatility: how unstable a value is over time.
- Threshold crossing: an observation passing a warning limit.
- Compliance: how closely behavior follows rules or signals.

**What These Cards Do NOT Explain**

They do not show distribution, location detail, or cause. They summarize conditions and should be paired with charts for interpretation.

### AQI KPI Cards

**Visualization Type**

Compact KPI cards and metric strips for air quality. They summarize pollution burden, extremes, frequency, weather context, and category behavior.

**Main Analytical Goal**

AQI KPI cards answer: "How polluted is the current filtered scope, and how serious is the exposure pattern?"

**Variables / Metrics Used**

- Mean PM2.5 in View: average fine-particle pollution. Higher values mean worse chronic burden.
- Peak PM2.5: maximum observed pollution. High peaks show acute extremes.
- Days Above 120 ug/m3: share of days above a high PM2.5 threshold. High values mean repeated severe exposure.
- Severe Days Count: number of severe pollution days.
- WHO Guideline Context: comparison against a health-oriented reference. It reminds users that local averages may still be far above health guidance.
- Dominant Category: most common AQI category.
- Strongest Weather Correlation: weather variable most strongly associated with PM2.5 in the current scope.
- Stagnation Trap Days: days with low visibility and high PM2.5.
- Low VV + High PM2.5: share of records combining poor visibility and high pollution.
- Category Transitions: how often AQI categories change over time.
- Severe Share: share of records in severe pollution conditions.

**Visual Components**

- Numeric value: main result.
- Label: metric name.
- Supporting note: interpretation guidance or caution.
- Category wording: converts numeric pollution into human severity.
- Reference comparisons: help users avoid normalizing dangerous values.

**What Patterns Matter**

High mean PM2.5 indicates chronic burden. High peak PM2.5 indicates acute extremes. High days-above-threshold means repeated exposure. Many category transitions indicate unstable air quality.

**Real-World Meaning**

These cards help users understand health-oriented air-quality burden quickly. They support public awareness, environmental monitoring, and policy discussion.

**Likely Intended User Interpretation**

Users should treat AQI KPIs as the dashboard's air-quality summary, then inspect temporal and weather charts to understand persistence and context.

**Potential User Confusion**

Users may confuse peak pollution with everyday exposure. They may also misunderstand WHO guideline context as a local legal threshold rather than a health reference.

**Glossary Terms Needed**

- PM2.5: fine airborne particles that can enter the lungs.
- WHO guideline: a health-oriented reference value.
- Severe share: the fraction of records in severe pollution conditions.
- Category transition: a change from one AQI severity category to another.
- Stagnation trap: conditions where pollution may accumulate.

**What These Cards Do NOT Explain**

They do not identify exact pollution sources, personal exposure, or health outcomes. They summarize filtered data and require charts for deeper interpretation.

## Interaction and Context Surfaces

### Global Filter Context

Global filters are persistent dataset-scope controls. They explain why charts changed after the user selected date ranges, areas, roads, seasons, weather, roadwork, or AQI categories. The key user explanation is: "Charts changed because the dashboard is now calculating from a smaller selected dataset."

Potential confusion: users may think charts changed due to an error or hidden recommendation. The correct explanation is that filter selections define the analytical scope.

Limit: global filter context does not explain analytical meaning by itself. It only explains why the data scope changed.

### Investigation Overlay and Visual Focus

Investigation overlays are temporary click-driven focus states. They help users follow a selected road, area, week, season, or regime across overlay-aware charts. Visual focus can highlight selected context without changing the permanent global filters.

Potential confusion: users may think a click permanently filtered the dashboard. The explanation should clearly separate "temporary investigation focus" from "global filter."

Limit: overlays do not create new data, change reducers, or prove causal relationships. They only adjust what is emphasized or scoped in presentation.

### Clear Focus

Clear Focus removes temporary visual focus and investigation overlays while preserving global filters. The key explanation is: "This returns the investigation view to baseline without undoing your filter selections."

Potential confusion: users may expect Clear Focus to reset all filters. It should not. Reset All is the broader action.

### Empty and Unavailable States

Empty states explain why a chart has no data or cannot render. The most important distinction is between "no records match the current filter or overlay" and "the chart is unavailable because required data is missing or the builder could not produce a figure."

Potential confusion: users may think an empty chart means the dashboard failed. It may simply mean the current analytical scope has no matching records.

Limit: empty states should not automatically clear filters, overlays, or focus. They should preserve analytical state and explain the condition.

## Cross-Chart Analytical Flow Notes

Traffic users can move from broad diagnosis to focused investigation:

- T-01 shows overall network pressure and area concentration.
- T-03, T-04, and T-15 explain time patterns.
- T-05, T-06, and T-07 explain road and area stress.
- T-09 and T-10 explain speed thresholds and public transport context.
- T-11, T-12, and T-08 explain distributions, operational conditions, and incident sensitivity.
- T-13, T-02, and T-14 support advanced profile and density exploration.

AQI users can move from burden to atmospheric explanation:

- A-01 and A-05 show category burden and persistence.
- A-02 and A-04 show weekly and monthly timing.
- A-03 shows seasonal distribution.
- A-06, A-07, A-09, A-10, A-11, A-12, A-13, and A-14 explain weather and atmospheric context.
- A-15 supports advanced multivariate exploration.

These relationships should be presented as analytical pathways, not forced recommendations. The dashboard should help users know where to investigate next while leaving navigation and interpretation under user control.
