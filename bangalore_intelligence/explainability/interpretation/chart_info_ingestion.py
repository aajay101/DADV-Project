"""Structured chart interpretation metadata extracted from chart_info.md.

This module intentionally keeps interpretation content structured instead of
loading the Markdown audit as a runtime blob. The audit remains the human source
document; this mapping is the renderable registry payload.
"""

from __future__ import annotations

from collections.abc import Iterable

from bangalore_intelligence.explainability.models import (
    ConsequenceMapEntry,
    ExplainabilityEntry,
    GlossaryTerm,
    HumanImpact,
    InterpretationMetric,
    VisualComponent,
)


def _metric(
    name: str,
    meaning: str,
    why: str,
    *,
    high: str = "",
    low: str = "",
    caution: str = "",
) -> InterpretationMetric:
    return InterpretationMetric(
        name=name,
        meaning=meaning,
        why_it_matters=why,
        high_values=high,
        low_values=low,
        caution=caution,
    )


def _component(name: str, meaning: str, why: str, notice: str) -> VisualComponent:
    return VisualComponent(name=name, meaning=meaning, why_it_exists=why, what_to_notice=notice)


def _term(term: str, definition: str) -> GlossaryTerm:
    return GlossaryTerm(term=term, definition=definition)


def _chart(
    *,
    reading_summary: str,
    visualization_reason: str,
    metrics: tuple[InterpretationMetric, ...],
    visual_components: tuple[VisualComponent, ...],
    patterns: tuple[str, ...],
    real_world_meaning: str,
    intended_interpretation: str,
    misunderstandings: tuple[str, ...],
    glossary: tuple[GlossaryTerm, ...],
    related_investigations: tuple[str, ...],
) -> dict[str, object]:
    return {
        "reading_summary": reading_summary,
        "visualization_reason": visualization_reason,
        "metrics": metrics,
        "visual_components": visual_components,
        "patterns": patterns,
        "real_world_meaning": real_world_meaning,
        "intended_interpretation": intended_interpretation,
        "misunderstandings": misunderstandings,
        "glossary": glossary,
        "related_investigations": related_investigations,
    }


CHART_INTERPRETATION_METADATA: dict[str, dict[str, object]] = {
    "T-01": _chart(
        reading_summary="This overview helps users understand how stressed the traffic network is and which areas are driving that stress.",
        visualization_reason="A gauge gives an immediate network-level severity read, while ranked bars show where that pressure is concentrated.",
        metrics=(
            _metric("System Congestion Index", "Average congestion across the active records.", "It is the fastest signal of overall network pressure.", high="More crowded and slower roads.", low="Lower road pressure."),
            _metric("Area mean congestion", "Average congestion for each area.", "It shows where pressure is concentrated.", high="Area deserves closer review.", low="Area is less stressed in the current scope."),
            _metric("Capacity saturation", "Share of records near road capacity.", "High saturation means little room for disruption.", high="Fragile operating conditions."),
        ),
        visual_components=(
            _component("Gauge", "Network congestion on a 0-100 scale.", "It summarizes the whole filtered traffic scope.", "Whether the marker is in calm, caution, or severe territory."),
            _component("Area ranking bars", "Areas ordered by congestion.", "They show where network pressure is located.", "Long bars and bars near the critical reference line."),
            _component("Threshold markers", "Reference lines for concerning congestion.", "They help users compare values against operational risk levels.", "Values crossing the references need follow-up."),
        ),
        patterns=("High gauge plus many long bars means broad congestion.", "One dominant bar means concentrated area stress."),
        real_world_meaning="The chart turns many traffic records into a city operations summary for mobility pressure, delay risk, and where attention should start.",
        intended_interpretation="Start with this chart to decide whether traffic stress is broad or concentrated.",
        misunderstandings=("It does not explain the cause of congestion.", "It is calculated from the current filter scope, not necessarily live citywide traffic."),
        glossary=(
            _term("Congestion index", "A simple score for how crowded or slow the road network is."),
            _term("Capacity saturation", "How often roads are close to their usable limit."),
            _term("Filter scope", "The records currently included after dashboard filters are applied."),
        ),
        related_investigations=("T-03", "T-05", "T-13"),
    ),
    "T-02": _chart(
        reading_summary="This chart helps users see whether an area is stressed in one way or across many traffic dimensions.",
        visualization_reason="Parallel coordinates show a multi-metric profile in one view, which is better than many separate charts when comparing area fingerprints.",
        metrics=(
            _metric("Congestion", "Traffic pressure in an area.", "It shows crowding and delay burden.", high="Heavier traffic stress."),
            _metric("Speed", "How fast vehicles are moving.", "Low speed makes congestion meaningful in real mobility terms.", low="Poorer travel performance."),
            _metric("Capacity, incidents, environment, and exposure", "Supporting dimensions of area stress.", "They show whether the problem is broad or specific."),
            _metric("Normalized values", "Metrics converted to comparable scales.", "They allow unlike units to be compared fairly.", caution="They are not raw percentages."),
        ),
        visual_components=(
            _component("Vertical axes", "Each axis is a traffic dimension.", "They let users compare many measures at once.", "Which axes are high for each area."),
            _component("Profile lines", "Each line represents an area.", "The line shape becomes the area's traffic fingerprint.", "Lines that stay high across many axes."),
            _component("Focus opacity", "Selected areas can appear stronger.", "It helps users follow one area without changing data.", "Whether faded lines are only background context."),
        ),
        patterns=("Lines high across many axes indicate broad stress.", "Single-axis spikes indicate a specific issue.", "Crossing lines show tradeoffs between dimensions."),
        real_world_meaning="It helps planners avoid treating every congested area the same; different profiles imply different kinds of follow-up.",
        intended_interpretation="Look for area fingerprints and broad multi-factor stress patterns.",
        misunderstandings=("Normalized axes can hide original units.", "The chart does not prove which factor caused another."),
        glossary=(
            _term("Parallel coordinates", "A chart where each line crosses several metric axes."),
            _term("Normalized value", "A converted value used for fair comparison across different units."),
            _term("Area profile", "The pattern an area makes across several traffic measures."),
        ),
        related_investigations=("T-13", "T-05", "T-07"),
    ),
    "T-03": _chart(
        reading_summary="This chart shows whether congestion is rising, falling, seasonal, or different across areas over time.",
        visualization_reason="A multi-line chart is best for seeing month-to-month movement, slopes, and divergence across areas.",
        metrics=(
            _metric("Month", "The time period being compared.", "It places congestion into a time sequence."),
            _metric("Area", "The location represented by each line.", "It allows location comparison."),
            _metric("Mean congestion", "Average congestion for an area in a month.", "It shows monthly traffic burden.", high="Heavier pressure.", low="More relief."),
        ),
        visual_components=(
            _component("X-axis", "Calendar months.", "It shows time order.", "Recurring peaks or changes over time."),
            _component("Y-axis", "Mean congestion percentage.", "It shows severity.", "High values and rising values."),
            _component("Colored lines and markers", "One series per area.", "They show area trajectories.", "Diverging or rising lines."),
        ),
        patterns=("Upward slopes suggest worsening congestion.", "Repeated peaks suggest seasonal or operational rhythm.", "Diverging lines show unequal area trajectories."),
        real_world_meaning="Monthly patterns support planning for recurring traffic pressure, roadwork timing, and operations readiness.",
        intended_interpretation="Compare both level and direction; the worst area and the fastest-worsening area may not be the same.",
        misunderstandings=("One spike is not proof of long-term deterioration.", "Monthly averages hide daily variation."),
        glossary=(
            _term("Mean congestion", "Average congestion across records."),
            _term("Trend", "The direction a value moves over time."),
            _term("Seasonal pattern", "A pattern that repeats during parts of the year."),
        ),
        related_investigations=("T-01", "T-15", "T-04"),
    ),
    "T-04": _chart(
        reading_summary="This chart helps users see whether weekday congestion is routine, variable, or occasionally extreme.",
        visualization_reason="A violin or box distribution shows spread, median, and tails better than a weekday average alone.",
        metrics=(
            _metric("Day of week", "The weekday category.", "It supports weekly scheduling interpretation."),
            _metric("Congestion distribution", "The spread of record-level congestion values.", "It shows stability and extremes, not only average level.", high="More severe traffic values."),
            _metric("Median", "The middle congestion value.", "It gives a typical weekday condition."),
        ),
        visual_components=(
            _component("Violin shape", "The distribution of congestion values.", "It shows how common values are at each level.", "Wide areas and long upper tails."),
            _component("Box/median marker", "Typical and middle behavior.", "It helps compare routine pressure.", "Weekdays with high medians."),
            _component("Fallback boxplot", "Simpler distribution view for low data.", "It avoids overclaiming when records are sparse.", "The visual form may change with data volume."),
        ),
        patterns=("Wide shapes mean high variability.", "Long upper tails mean occasional severe congestion.", "High medians mean routine stress."),
        real_world_meaning="It helps distinguish predictable weekday pressure from occasional disruption, which affects staffing and scheduling decisions.",
        intended_interpretation="Look beyond averages and ask which weekdays are stable or risky.",
        misunderstandings=("Width means value frequency, not congestion size.", "A volatile day is not always the highest-average day."),
        glossary=(
            _term("Violin chart", "A distribution chart where width shows how common values are."),
            _term("Median", "The middle value."),
            _term("Tail", "The extreme end of a distribution."),
        ),
        related_investigations=("T-03", "T-11", "T-12"),
    ),
    "T-05": _chart(
        reading_summary="This chart helps users identify roads that combine high congestion and high capacity pressure.",
        visualization_reason="A quadrant scatter shows two risk dimensions at once and makes priority zones visible.",
        metrics=(
            _metric("Mean congestion", "Average congestion for a road.", "It shows road pressure.", high="More stressful road conditions."),
            _metric("Capacity utilization", "How much road capacity is being used.", "It shows whether the road has spare room.", high="Less operational headroom."),
            _metric("Flow instability", "How variable road performance is.", "Unstable roads may be harder to manage."),
        ),
        visual_components=(
            _component("Dots", "Roads in the current scope.", "They allow road-by-road comparison.", "Dots in the upper-right zone."),
            _component("Quadrant lines", "Reference thresholds for congestion and capacity.", "They divide roads into management zones.", "Roads near or beyond thresholds."),
            _component("Dot size and color", "Instability and priority category.", "They add severity context.", "Large, severe-colored points."),
        ),
        patterns=("Upper-right dots are critical overload candidates.", "Large dots indicate unstable flow.", "Dots near thresholds can become future risks."),
        real_world_meaning="It supports corridor prioritization for signal review, capacity management, or operational intervention.",
        intended_interpretation="Focus first on roads in or near critical overload, then inspect road pressure and speed-collapse charts.",
        misunderstandings=("Quadrant labels are analytical categories, not official road classes.", "The chart does not identify the root cause of overload."),
        glossary=(
            _term("Quadrant", "A chart divided into zones by reference lines."),
            _term("Capacity utilization", "How much of a road's usable capacity is being used."),
            _term("Critical overload", "A condition where congestion and capacity pressure are both high."),
        ),
        related_investigations=("T-07", "T-09", "T-11"),
    ),
    "T-06": _chart(
        reading_summary="This chart shows which areas and roads contribute most to traffic-related environmental burden.",
        visualization_reason="A treemap is useful because size can show contribution while nesting shows area-road hierarchy.",
        metrics=(
            _metric("Environmental impact", "A derived burden score connected to traffic conditions.", "It connects mobility pressure to broader environmental cost.", high="Greater burden."),
            _metric("Area and road", "Nested location groups.", "They show where the burden is located."),
            _metric("Mean congestion", "Congestion severity used as color context.", "It adds traffic stress interpretation."),
        ),
        visual_components=(
            _component("Rectangles", "Areas and roads sized by burden.", "They reveal dominant contributors.", "Large rectangles."),
            _component("Nested blocks", "Roads grouped within areas.", "They show responsibility inside each area.", "Whether one road dominates an area."),
            _component("Color intensity", "Congestion severity context.", "It shows whether burden is also congested.", "Large dark blocks."),
        ),
        patterns=("Large dark blocks are the most important.", "One dominant road suggests corridor concentration.", "Many medium blocks suggest distributed burden."),
        real_world_meaning="It helps users identify where traffic pressure may have broader environmental cost.",
        intended_interpretation="Find the biggest burden contributors, then inspect road stress and density charts.",
        misunderstandings=("Environmental impact is a derived score, not necessarily a direct emissions measurement.", "Small blocks can still matter locally."),
        glossary=(
            _term("Treemap", "A chart where rectangle size shows contribution to a total."),
            _term("Environmental burden", "A traffic-related environmental impact score."),
            _term("Hierarchy", "A parent-child grouping such as area and road."),
        ),
        related_investigations=("T-05", "T-07", "T-14"),
    ),
    "T-07": _chart(
        reading_summary="This chart shows which roads are above or below the current baseline pressure, with exposure context.",
        visualization_reason="Deviation bars make it easy to see roads worse or better than the current system baseline.",
        metrics=(
            _metric("Congestion deviation", "Difference from the filtered-scope baseline.", "It shows unusual road pressure.", high="Road is above baseline.", low="Road is below baseline."),
            _metric("System baseline", "Average context for the current records.", "It makes the comparison relative to the current filter scope."),
            _metric("Pedestrian exposure", "Walking and cycling context.", "High exposure makes pressure more socially sensitive."),
        ),
        visual_components=(
            _component("Horizontal bars", "Road-level deviation from baseline.", "They show outliers clearly.", "Large positive bars."),
            _component("Zero line", "The baseline split.", "It separates above-baseline from below-baseline roads.", "Which side each road falls on."),
            _component("Bar colors", "Positive or lower pressure states.", "They make pressure direction scannable.", "Severe positive bars."),
        ),
        patterns=("Large positive bars deserve closer review.", "Negative bars are only lower relative to the current baseline.", "Many positive roads in one area suggest localized area stress."),
        real_world_meaning="It helps users consider road stress where vulnerable road users may be exposed.",
        intended_interpretation="Use this to find road pressure outliers after an area or quadrant diagnosis.",
        misunderstandings=("Below baseline does not mean universally safe.", "Pedestrian exposure context is not the same as crash risk."),
        glossary=(
            _term("Baseline", "The comparison level for the current data."),
            _term("Deviation", "How far a value is above or below a baseline."),
            _term("Pedestrian exposure", "How much walking and cycling activity may be affected."),
        ),
        related_investigations=("T-05", "T-06", "T-11"),
    ),
    "T-08": _chart(
        reading_summary="This chart checks whether congestion changes sharply as incident counts increase.",
        visualization_reason="A step line fits grouped incident bands because it shows jumps between categories instead of implying smooth time movement.",
        metrics=(
            _metric("Incident band", "Grouped incident count range.", "It simplifies incident load comparison.", high="More incidents in the group."),
            _metric("Mean congestion", "Average congestion within each band.", "It shows whether congestion rises with incident load.", high="More pressure."),
            _metric("Step delta", "Change between bands.", "It reveals cliff-like behavior."),
        ),
        visual_components=(
            _component("Step line", "Mean congestion across incident bands.", "It emphasizes category jumps.", "Sharp upward steps."),
            _component("Markers", "Observed band averages.", "They show actual compared points.", "High markers after incident increases."),
            _component("Threshold line", "Concerning congestion reference.", "It helps interpret severity.", "Bands above the line."),
        ),
        patterns=("Sharp steps suggest incident sensitivity.", "Flat lines suggest incident bands do not separate congestion much.", "High low-incident values suggest routine congestion."),
        real_world_meaning="It supports incident-response planning and helps separate routine congestion from disruption-sensitive congestion.",
        intended_interpretation="Read this as an incident sensitivity check.",
        misunderstandings=("Association is not proof that incidents caused congestion.", "Bands can hide variation inside each group."),
        glossary=(
            _term("Incident band", "A grouped range of incident counts."),
            _term("Step change", "A jump from one category to another."),
            _term("Sensitivity", "How much one measure changes when another condition changes."),
        ),
        related_investigations=("T-09", "T-12", "T-03"),
    ),
    "T-09": _chart(
        reading_summary="This chart shows where high congestion and low speed happen together, indicating speed-collapse risk.",
        visualization_reason="A threshold scatter makes combined risk visible because speed collapse depends on two measurements at once.",
        metrics=(
            _metric("Speed", "How fast vehicles are moving.", "It turns congestion into practical mobility performance.", low="Slow or collapsed movement."),
            _metric("Congestion", "Traffic pressure.", "It shows crowding.", high="More road stress."),
            _metric("Thresholds", "Reference values for high congestion and low speed.", "They identify risk zones."),
        ),
        visual_components=(
            _component("Dots", "Traffic records.", "They show observed speed-congestion combinations.", "Clusters in the critical zone."),
            _component("Speed and congestion lines", "Operational references.", "They divide normal and risky states.", "Points beyond both references."),
            _component("Critical overload annotation", "Label for the highest-risk zone.", "It tells users where mobility breakdown appears.", "Repeated points in that zone."),
        ),
        patterns=("High-congestion, low-speed clusters are most serious.", "High congestion with tolerable speed is different from collapse.", "Low speed without high congestion may have other explanations."),
        real_world_meaning="Speed collapse affects commute reliability, emergency response, bus movement, fuel use, and public frustration.",
        intended_interpretation="Look for how often and where traffic enters the critical low-speed/high-congestion zone.",
        misunderstandings=("Each dot is a record, not necessarily a unique road.", "Thresholds are reference lines, not universal laws."),
        glossary=(
            _term("Speed collapse", "A state where roads are congested and vehicles move slowly."),
            _term("Threshold", "A reference value used to separate normal from concerning conditions."),
            _term("Scatter plot", "A chart where each dot shows one observation using two measurements."),
        ),
        related_investigations=("T-05", "T-08", "T-10"),
    ),
    "T-10": _chart(
        reading_summary="This chart compares congestion, speed, and incidents across public transport usage groups.",
        visualization_reason="Grouped bars plus a line allow several outcomes to be compared across the same usage quartiles.",
        metrics=(
            _metric("Public transport usage quartile", "Four groups from lower to higher public transport usage.", "It creates comparable mobility-mix groups."),
            _metric("Mean congestion", "Average pressure in each group.", "It shows traffic burden.", high="More congestion."),
            _metric("Mean speed and incidents", "Movement quality and disruption context.", "They prevent congestion from being read alone."),
        ),
        visual_components=(
            _component("Grouped bars", "Congestion and speed by quartile.", "They support side-by-side comparison.", "Whether bars improve or worsen across quartiles."),
            _component("Incident line", "Incident levels by quartile.", "It adds disruption context without another bar group.", "Rising or falling incident pattern."),
            _component("Dual axes", "Separate scales for traffic metrics and incidents.", "They keep different units readable.", "Do not compare bar height directly to line height."),
        ),
        patterns=("Lower congestion with higher public transport usage suggests a relationship worth exploring.", "Mixed patterns require caution.", "Incident increases may indicate busy corridors."),
        real_world_meaning="It helps examine how mobility mix aligns with road pressure and supports transport planning questions.",
        intended_interpretation="Compare quartiles, but treat the result as observational.",
        misunderstandings=("Public transport usage differences are not causal proof.", "Dual axes can be misread if scales are ignored."),
        glossary=(
            _term("Quartile", "One of four groups made by sorting values from low to high."),
            _term("Public transport usage", "The level or share of public transport use in the records."),
            _term("Secondary axis", "A second Y-axis for a metric with a different scale."),
        ),
        related_investigations=("T-09", "T-14", "T-05"),
    ),
    "T-11": _chart(
        reading_summary="This chart shows whether road congestion is chronic, occasional, skewed, or stable.",
        visualization_reason="Small histograms let users compare distribution shape across many roads without hiding road-specific behavior.",
        metrics=(
            _metric("Road", "The corridor shown in each panel.", "It supports road-level diagnosis."),
            _metric("Congestion distribution", "How often road congestion falls into ranges.", "It separates routine stress from occasional extremes."),
            _metric("Median congestion", "The middle road value.", "It indicates typical road pressure."),
        ),
        visual_components=(
            _component("Small-multiple grid", "One mini chart per road.", "It enables compact road comparison.", "Panels with high or skewed distributions."),
            _component("Histogram bars", "Frequency of congestion ranges.", "They show how often values occur.", "Bars concentrated near high congestion."),
            _component("Dotted median line", "Typical middle value for each road.", "It anchors comparison.", "Roads with high medians."),
        ),
        patterns=("High medians indicate chronic stress.", "Long right tails indicate occasional severe events.", "Narrow shapes indicate predictable conditions."),
        real_world_meaning="It helps decide whether a corridor problem is repeated and structural or occasional and event-driven.",
        intended_interpretation="Compare distribution shape, not just the highest value.",
        misunderstandings=("High bar count means many records in a range, not automatically high congestion.", "Only a subset of roads may be visible."),
        glossary=(
            _term("Histogram", "A chart showing how often values fall into ranges."),
            _term("Right-skewed", "A distribution with values extending far into high levels."),
            _term("Chronic congestion", "Congestion that appears repeatedly."),
        ),
        related_investigations=("T-05", "T-07", "T-04"),
    ),
    "T-12": _chart(
        reading_summary="This chart shows which weather and roadwork combinations are associated with higher congestion.",
        visualization_reason="A heatmap efficiently compares two categorical conditions against one congestion value.",
        metrics=(
            _metric("Weather condition", "The weather category.", "Weather can affect road operations."),
            _metric("Roadwork status", "Whether roadwork activity is present.", "Roadwork can reduce capacity or change flow."),
            _metric("Mean congestion", "Average congestion for each combination.", "It identifies risky operational combinations.", high="Higher traffic pressure."),
        ),
        visual_components=(
            _component("Grid cells", "Weather-roadwork combinations.", "They show joint conditions.", "Dark cells."),
            _component("Color scale", "Mean congestion severity.", "It makes high-risk combinations easy to scan.", "Rows, columns, or isolated cells that are dark."),
            _component("Axes", "Weather and roadwork categories.", "They define the operational context.", "Which condition combinations are being compared."),
        ),
        patterns=("Dark rows suggest difficult weather.", "Dark columns suggest roadwork status matters.", "Isolated dark cells suggest specific high-risk combinations."),
        real_world_meaning="It supports roadwork scheduling and traffic mitigation planning around weather conditions.",
        intended_interpretation="Use dark cells as planning risk signals, not causal proof.",
        misunderstandings=("Darker cells do not prove weather or roadwork caused congestion.", "Sparse combinations may be unstable."),
        glossary=(
            _term("Heatmap", "A grid where color represents a value."),
            _term("Roadwork status", "Whether construction or maintenance activity is active."),
            _term("Operational risk", "A condition that can make traffic harder to manage."),
        ),
        related_investigations=("T-08", "T-04", "T-09"),
    ),
    "T-13": _chart(
        reading_summary="This chart shows how areas differ across several traffic stress factors at once.",
        visualization_reason="A heatmap supports scanning many area-metric combinations, while radar mode helps compare a few area profiles.",
        metrics=(
            _metric("Stress index", "A normalized 0-100 comparison score.", "It makes unlike metrics comparable.", high="More stress."),
            _metric("Area", "The location being compared.", "It supports location diagnosis."),
            _metric("Stress dimensions", "Congestion, speed, capacity, incidents, environment, and related factors.", "They explain what kind of stress exists."),
        ),
        visual_components=(
            _component("Heatmap cells", "Area-by-metric stress values.", "They reveal specific stress dimensions.", "Dark cells and dark rows."),
            _component("Radar axes", "Stress dimensions around a circle.", "They show profile shape for focused areas.", "Wide shapes across many axes."),
            _component("Focus styling", "Selected areas are emphasized.", "It helps compare selected context.", "Whether only a few profiles are being compared."),
        ),
        patterns=("Dark rows indicate broad area stress.", "One dark column indicates a specific weakness.", "Wide radar shapes indicate multi-factor stress."),
        real_world_meaning="It helps distinguish broad systemic area problems from targeted operational issues.",
        intended_interpretation="Identify the type of stress, not just the most stressed area.",
        misunderstandings=("Normalized values are not raw percentages.", "Radar area can visually exaggerate differences."),
        glossary=(
            _term("Stress profile", "A multi-metric picture of area performance."),
            _term("Normalized index", "A converted score used for fair comparison."),
            _term("Radar chart", "A circular chart where each axis is a metric."),
        ),
        related_investigations=("T-02", "T-15", "T-05"),
    ),
    "T-14": _chart(
        reading_summary="This chart shows where traffic volume and congestion records cluster together.",
        visualization_reason="A 2D density heatmap avoids overcrowded dots and reveals common volume-congestion combinations.",
        metrics=(
            _metric("Traffic volume", "Amount of traffic activity.", "It shows demand load.", high="More traffic demand."),
            _metric("Congestion", "Traffic pressure.", "It shows whether demand turns into crowding.", high="More road stress."),
            _metric("Density", "Number of records in each value range.", "It reveals repeated conditions."),
        ),
        visual_components=(
            _component("X-axis", "Traffic volume.", "It shows demand level.", "High-volume regions."),
            _component("Y-axis", "Congestion.", "It shows pressure level.", "High-congestion regions."),
            _component("Colored bins", "Record density in volume-congestion ranges.", "They reveal clusters.", "Dense high-volume/high-congestion regions."),
        ),
        patterns=("Dense high-volume/high-congestion regions suggest sustained corridor load.", "High-volume/low-congestion areas may be handling demand better.", "Low-volume/high-congestion regions may suggest bottlenecks."),
        real_world_meaning="It helps separate demand-related pressure from other congestion patterns.",
        intended_interpretation="Focus on repeated clusters, not isolated cells.",
        misunderstandings=("Color primarily shows density, not congestion severity alone.", "The chart does not name specific roads by itself."),
        glossary=(
            _term("Density", "How many observations are concentrated in a chart region."),
            _term("Bin", "A grouped range of values."),
            _term("Overplotting", "When too many dots overlap and become unreadable."),
        ),
        related_investigations=("T-10", "T-06", "T-09"),
    ),
    "T-15": _chart(
        reading_summary="This chart shows where and when area congestion concentrates by month.",
        visualization_reason="An area-month heatmap compares location and time together in one compact grid.",
        metrics=(
            _metric("Area", "The location group.", "It shows where stress appears."),
            _metric("Month", "The time period.", "It shows when stress appears."),
            _metric("Mean congestion", "Average area-month congestion.", "It identifies temporal hotspots.", high="Higher stress."),
        ),
        visual_components=(
            _component("Grid cells", "One area during one month.", "They combine place and time.", "Dark cells."),
            _component("Colorbar", "Congestion percentage.", "It translates color into severity.", "Repeated high values."),
            _component("Clickable cells", "Interaction context for focus or filtering.", "They support investigation.", "Click behavior depends on interaction mode."),
        ),
        patterns=("Dark rows show persistently stressed areas.", "Dark columns show broadly difficult months.", "Isolated dark cells show localized temporal hotspots."),
        real_world_meaning="It supports seasonal and location-specific traffic planning.",
        intended_interpretation="Find when and where congestion concentrates, then inspect road-level and trend charts.",
        misunderstandings=("A click may create temporary focus rather than a global filter.", "Monthly cells hide daily variation."),
        glossary=(
            _term("Area-month", "One area during one month."),
            _term("Temporary focus", "A click-based context that does not necessarily change global filters."),
            _term("Heatmap", "A grid where color represents a value."),
        ),
        related_investigations=("T-03", "T-13", "T-01"),
    ),
    "A-01": _chart(
        reading_summary="This chart shows how often air quality falls into each PM2.5 severity category.",
        visualization_reason="A categorical bar chart is the clearest way to compare how many days fall into each air-quality category.",
        metrics=(
            _metric("AQI category", "A plain-language pollution severity group.", "It helps non-technical users understand PM2.5 burden."),
            _metric("Day count", "Number of days or records in each category.", "It shows frequency of exposure.", high="More days in that category."),
            _metric("PM2.5", "Fine particle pollution.", "It is the core air-quality burden metric.", high="More unhealthy air.", low="Cleaner air."),
        ),
        visual_components=(
            _component("Bars", "Counts by AQI category.", "They show category frequency.", "Tall bars in Poor, Very Poor, or Severe."),
            _component("Category colors", "Severity color coding.", "It makes the risk level readable.", "Whether severe colors dominate."),
            _component("X-axis categories", "Cleaner to more polluted groups.", "They convert numbers into human labels.", "Where the distribution is concentrated."),
        ),
        patterns=("Tall severe-category bars indicate repeated unhealthy exposure.", "A wide mix suggests unstable air quality."),
        real_world_meaning="It tells users whether residents mostly experience acceptable air or repeated unhealthy air.",
        intended_interpretation="Use this as the AQI burden overview before exploring time and weather context.",
        misunderstandings=("It does not identify pollution sources.", "Category mix changes with filters."),
        glossary=(
            _term("PM2.5", "Tiny airborne particles that can affect breathing and health."),
            _term("AQI category", "A severity label for air pollution."),
            _term("Day count", "How many days fall into a category."),
        ),
        related_investigations=("A-05", "A-02", "A-03"),
    ),
    "A-02": _chart(
        reading_summary="This chart shows when polluted weeks occur and whether they repeat across years.",
        visualization_reason="A weekly calendar heatmap preserves time order while making persistent polluted blocks visible.",
        metrics=(
            _metric("Week of year", "Weekly time unit.", "It shows when pollution occurs."),
            _metric("Year", "Yearly comparison.", "It shows whether patterns repeat."),
            _metric("Mean PM2.5", "Average weekly fine-particle pollution.", "It shows weekly exposure burden.", high="More polluted air."),
        ),
        visual_components=(
            _component("Calendar grid", "Weeks by year.", "It organizes pollution over time.", "Repeated high-color blocks."),
            _component("Cell color", "PM2.5 severity.", "It makes polluted weeks easy to locate.", "Dark or severe-colored cells."),
            _component("Highlight opacity", "Selected week focus.", "It supports temporary inspection.", "Faded cells are context, not deleted data."),
        ),
        patterns=("Long high-color bands indicate persistent pollution.", "Repeated weeks across years suggest seasonal behavior.", "Isolated cells suggest short episodes."),
        real_world_meaning="Weekly persistence matters because repeated exposure can be more important than one bad day.",
        intended_interpretation="Identify polluted blocks and compare whether they recur across years.",
        misunderstandings=("Week numbers may not feel intuitive.", "Color represents PM2.5, not record count."),
        glossary=(
            _term("Calendar heatmap", "A time grid where color shows intensity."),
            _term("Persistence", "Pollution staying high over a period."),
            _term("PM2.5", "Fine particle pollution."),
        ),
        related_investigations=("A-05", "A-04", "A-01"),
    ),
    "A-03": _chart(
        reading_summary="This chart compares the shape of daily PM2.5 values across seasons.",
        visualization_reason="Ridgelines show seasonal shifts, spread, and high-pollution tails better than seasonal averages.",
        metrics=(
            _metric("Season", "Winter, Spring, Monsoon, or Post-Monsoon.", "It groups pollution by environmental period."),
            _metric("Daily PM2.5", "Daily fine-particle pollution values.", "It shows exposure distribution.", high="More polluted air."),
            _metric("Density", "Where values are most common.", "It shows typical and unusual seasonal values."),
        ),
        visual_components=(
            _component("Ridgeline shapes", "Seasonal PM2.5 distributions.", "They compare spread and tails.", "Right-shifted or long-tailed seasons."),
            _component("X-axis", "PM2.5 level.", "It shows pollution severity.", "How far each season extends into high values."),
            _component("Season colors", "Separate seasonal groups.", "They keep comparisons readable.", "Which season carries the highest distribution."),
        ),
        patterns=("Right-shifted seasons have higher PM2.5.", "Long right tails mean occasional severe pollution.", "Narrow shapes mean more consistent values."),
        real_world_meaning="It helps identify seasons when residents may face higher pollution exposure risk.",
        intended_interpretation="Compare seasonal shapes, not just average pollution.",
        misunderstandings=("The shape is not a time trend.", "Density is not a count of days on the y-axis."),
        glossary=(
            _term("Ridgeline chart", "Stacked distribution shapes used to compare groups."),
            _term("Density", "How common values are in a range."),
            _term("Right tail", "The high-value end of a distribution."),
        ),
        related_investigations=("A-04", "A-05", "A-01"),
    ),
    "A-04": _chart(
        reading_summary="This chart shows which months and years had higher mean PM2.5.",
        visualization_reason="A month-year heatmap compactly reveals seasonal rhythm and multi-year pollution clusters.",
        metrics=(
            _metric("Month", "Calendar month.", "It shows seasonal timing."),
            _metric("Year", "Comparison year.", "It shows whether burden changes over years."),
            _metric("Mean PM2.5", "Average PM2.5 for each month-year cell.", "It shows monthly pollution burden.", high="Worse air quality."),
        ),
        visual_components=(
            _component("Month-year grid", "One month in one year.", "It compares time at two scales.", "Recurring dark months."),
            _component("Cell color", "Mean PM2.5.", "It shows severity quickly.", "Dark or severe-colored cells."),
            _component("Colorbar", "PM2.5 scale.", "It translates color into value.", "How severe dark cells are."),
        ),
        patterns=("Repeated dark months suggest seasonal hotspots.", "Dark clusters in one year suggest episode periods.", "Light monsoon cells may indicate relief."),
        real_world_meaning="Monthly patterns support seasonal air-quality preparation and public communication.",
        intended_interpretation="Find recurring high-PM2.5 months and compare across years.",
        misunderstandings=("Monthly averages can hide daily spikes.", "Moderate monthly average does not mean every day was moderate."),
        glossary=(
            _term("Mean PM2.5", "Average fine-particle pollution."),
            _term("Heatmap", "A color-coded grid."),
            _term("Seasonal cycle", "A pattern repeated across parts of the year."),
        ),
        related_investigations=("A-02", "A-03", "A-14"),
    ),
    "A-05": _chart(
        reading_summary="This chart helps users see whether pollution spikes briefly or stays high for many days.",
        visualization_reason="A time-series line with a 7-day rolling mean separates noisy daily movement from sustained pollution.",
        metrics=(
            _metric("Daily PM2.5", "Observed fine-particle pollution each day.", "It shows acute pollution movement.", high="More polluted air."),
            _metric("7-day rolling mean", "Average over recent days.", "It reveals sustained exposure.", high="Persistent pollution."),
            _metric("Severe threshold", "High-risk PM2.5 reference.", "It helps users interpret danger levels."),
        ),
        visual_components=(
            _component("Thin daily line", "Raw daily PM2.5.", "It shows spikes and volatility.", "Sharp peaks."),
            _component("Thick rolling line", "Smoothed 7-day PM2.5.", "It shows persistence.", "Long elevated stretches."),
            _component("Shaded band and severe line", "Pollution reference zones.", "They provide risk context.", "When values approach or cross them."),
        ),
        patterns=("Sharp spikes show acute events.", "A high rolling mean shows sustained exposure.", "Repeated waves suggest recurring episodes."),
        real_world_meaning="Sustained pollution is important for public health because repeated exposure can matter more than one bad day.",
        intended_interpretation="Compare daily volatility with the smoother trend to understand persistence.",
        misunderstandings=("The rolling mean smooths and lags sudden changes.", "A single peak is not the whole story."),
        glossary=(
            _term("Rolling mean", "An average over recent days that smooths daily changes."),
            _term("PM2.5", "Tiny pollution particles in the air."),
            _term("Persistence", "Pollution remaining high over time."),
        ),
        related_investigations=("A-01", "A-02", "A-06"),
    ),
    "A-06": _chart(
        reading_summary="This chart connects PM2.5 burden with pressure and visibility conditions.",
        visualization_reason="A density heatmap shows where atmospheric conditions and pollution levels cluster together.",
        metrics=(
            _metric("Sea-level pressure", "Air pressure normalized to sea level.", "It helps identify pressure regimes."),
            _metric("Vertical visibility", "How clear the air is vertically.", "Low visibility can align with haze or trapped pollution.", low="Poorer visibility."),
            _metric("PM2.5", "Average particle pollution in each condition cell.", "It shows pollution burden.", high="More unhealthy air."),
        ),
        visual_components=(
            _component("Pressure axis", "Sea-level pressure range.", "It shows atmospheric context.", "Pressure bands with high PM2.5."),
            _component("Visibility axis", "Vertical visibility.", "It shows clarity context.", "Low-visibility high-PM2.5 areas."),
            _component("Cell color", "Average PM2.5.", "It reveals pollution clusters.", "Warm or dark high-PM2.5 cells."),
        ),
        patterns=("High PM2.5 under low visibility suggests stagnation-like conditions.", "Seasonal drift lines can show burden changes over years.", "Clusters matter more than single cells."),
        real_world_meaning="It helps users understand when weather context may trap or coincide with pollution.",
        intended_interpretation="Use it to connect pollution persistence with atmospheric context.",
        misunderstandings=("Atmospheric association is not proof of causality.", "Pressure and visibility are technical and need plain-language explanation."),
        glossary=(
            _term("Sea-level pressure", "Air pressure adjusted so conditions can be compared."),
            _term("Vertical visibility", "How clearly air can be seen through vertically."),
            _term("Stagnation", "Conditions where pollution may become trapped."),
        ),
        related_investigations=("A-13", "A-14", "A-07"),
    ),
    "A-07": _chart(
        reading_summary="This chart compares weather profiles for cleaner, moderate, and severe PM2.5 categories.",
        visualization_reason="A radar chart compares several weather variables at once using one profile shape per category.",
        metrics=(
            _metric("Weather profile", "Temperature, humidity, visibility, wind, and pressure together.", "It shows environmental context for pollution categories."),
            _metric("AQI category", "Pollution severity group.", "It lets users compare cleaner and severe conditions."),
            _metric("Normalized 0-100 values", "Converted weather values.", "They make different units comparable.", caution="They are not raw units."),
        ),
        visual_components=(
            _component("Radar axes", "Weather dimensions.", "They show multiple conditions at once.", "Axes where severe differs from good."),
            _component("Filled shapes", "Category profiles.", "They make category differences visible.", "Large separations between shapes."),
            _component("Legend", "Good, Moderate, Severe categories.", "It identifies profile groups.", "Which profile belongs to severe pollution."),
        ),
        patterns=("Separated shapes show weather differences between categories.", "Overlapping shapes suggest weak separation.", "Low visibility or pressure differences may indicate atmospheric context."),
        real_world_meaning="It helps users understand that pollution severity can align with broader weather patterns.",
        intended_interpretation="Compare category shapes cautiously and look for variables that separate severe days.",
        misunderstandings=("Radar shape is descriptive, not a prediction.", "Normalized values are not raw temperature, wind, or pressure values."),
        glossary=(
            _term("Radar chart", "A circular chart comparing several variables."),
            _term("Normalized value", "A converted value on a shared scale."),
            _term("Humidity", "Moisture level in the air."),
        ),
        related_investigations=("A-06", "A-13", "A-15"),
    ),
    "A-08": _chart(
        reading_summary="This chart checks whether lower minimum temperatures align with higher PM2.5.",
        visualization_reason="A scatter plot lets users inspect the relationship between temperature and pollution directly.",
        metrics=(
            _metric("Minimum temperature", "The lowest temperature in the period.", "It can be part of seasonal pollution context."),
            _metric("PM2.5", "Fine-particle pollution.", "It measures air-quality burden.", high="More polluted air."),
            _metric("AQI category", "Pollution severity label.", "It colors the dots into understandable groups."),
        ),
        visual_components=(
            _component("Dots", "Observed temperature-PM2.5 records.", "They show the relationship shape.", "Clusters at low temperature and high PM2.5."),
            _component("Category colors", "AQI severity.", "They make polluted records visible.", "Severe colors in specific temperature ranges."),
            _component("Transition fallback grid", "AQI category movement counts.", "It safely summarizes category transitions when scatter data is not present.", "Large off-diagonal counts."),
        ),
        patterns=("High PM2.5 clustering at low temperatures suggests a pattern worth investigating.", "Mixed clouds mean temperature alone is not enough.", "Transition counts show category instability."),
        real_world_meaning="It helps users connect cold-period context with pollution without overclaiming causality.",
        intended_interpretation="Treat the relationship as exploratory and confirm with seasonal and atmospheric charts.",
        misunderstandings=("A scatter relationship is not proof that temperature caused pollution.", "Noisy clouds can still contain weak patterns."),
        glossary=(
            _term("Minimum temperature", "The lowest temperature in the period."),
            _term("Scatter plot", "A chart where each dot is one observation."),
            _term("Category transition", "A change from one air-quality category to another."),
        ),
        related_investigations=("A-15", "A-12", "A-03"),
    ),
    "A-09": _chart(
        reading_summary="This chart compares PM2.5 across pressure bands and seasons.",
        visualization_reason="Grouped bars make it easy to compare seasons within each pressure band.",
        metrics=(
            _metric("Pressure band", "Grouped sea-level pressure range.", "It simplifies pressure regime comparison."),
            _metric("Season", "Seasonal period.", "Pressure context can differ by season."),
            _metric("Mean PM2.5", "Average pollution in each group.", "It shows burden differences.", high="Worse pollution."),
        ),
        visual_components=(
            _component("Grouped bars", "Seasonal PM2.5 values within pressure bands.", "They support side-by-side comparison.", "Tall bars in specific bands."),
            _component("Season colors", "Season identity.", "They keep groups readable.", "Which season is highest."),
            _component("Pressure axis", "Pressure bands.", "It defines the atmospheric grouping.", "Bands with consistently high values."),
        ),
        patterns=("Tall bars in certain bands show high-pollution associations.", "Season differences show pressure context is not uniform year-round."),
        real_world_meaning="It supports investigation of pressure regimes that may align with pollution accumulation.",
        intended_interpretation="Compare pressure bands within each season and seasons within each band.",
        misunderstandings=("Pressure bands show association, not causation.", "Grouped bands simplify a continuous variable."),
        glossary=(
            _term("Sea-level pressure", "Atmospheric pressure adjusted for comparison."),
            _term("Pressure band", "A grouped pressure range."),
            _term("Mean PM2.5", "Average fine-particle pollution."),
        ),
        related_investigations=("A-14", "A-06", "A-13"),
    ),
    "A-10": _chart(
        reading_summary="This chart compares PM2.5 across wind speed bands and seasons.",
        visualization_reason="Grouped bars show whether pollution differs across wind ranges while preserving seasonal context.",
        metrics=(
            _metric("Wind speed band", "Grouped wind-speed range.", "It supports simple comparison of ventilation conditions."),
            _metric("Season", "Seasonal period.", "Wind effects may differ by season."),
            _metric("Mean PM2.5", "Average pollution in each wind-season group.", "It shows whether stronger wind aligns with lower pollution.", high="Worse pollution."),
        ),
        visual_components=(
            _component("Grouped bars", "Seasonal PM2.5 by wind band.", "They compare wind context and season together.", "Whether bars drop in stronger wind bands."),
            _component("Season colors", "Season identity.", "They prevent seasonal patterns from being hidden.", "Which season remains high."),
            _component("Wind band axis", "Grouped wind speed levels.", "It frames dispersion context.", "Differences between weak and strong wind bands."),
        ),
        patterns=("Lower PM2.5 under stronger wind may suggest dispersion.", "High PM2.5 even with wind suggests other factors matter.", "Seasonal differences matter."),
        real_world_meaning="It helps explain whether air movement may coincide with cleaner or more polluted conditions.",
        intended_interpretation="Use wind as one context factor, not the whole explanation.",
        misunderstandings=("Wind alone does not control pollution.", "Wind direction is not shown."),
        glossary=(
            _term("Wind band", "A grouped range of wind speeds."),
            _term("Dispersion", "Pollution spreading out or being carried away."),
            _term("Mean PM2.5", "Average particle pollution."),
        ),
        related_investigations=("A-11", "A-06", "A-15"),
    ),
    "A-11": _chart(
        reading_summary="This chart checks whether different gustiness levels align with different PM2.5 levels.",
        visualization_reason="Quintile bars with uncertainty bands show both average differences and how confident those differences are.",
        metrics=(
            _metric("Gust ratio quintile", "Five groups from lower to higher gust behavior.", "It checks ventilation or turbulence patterns."),
            _metric("Mean PM2.5", "Average pollution in each quintile.", "It shows pollution differences across gustiness."),
            _metric("Confidence interval", "Uncertainty around the mean.", "It prevents overreading small differences."),
        ),
        visual_components=(
            _component("Bars", "Mean PM2.5 by gust quintile.", "They compare grouped gust behavior.", "Monotonic increases or decreases."),
            _component("Error bars", "Uncertainty range.", "They show reliability.", "Wide or overlapping ranges."),
            _component("Quintile axis", "Sorted gust-ratio groups.", "It simplifies continuous gust behavior.", "Whether higher quintiles differ."),
        ),
        patterns=("Steady movement across quintiles suggests a relationship worth investigating.", "Wide error bars reduce confidence.", "Overlapping ranges weaken conclusions."),
        real_world_meaning="It helps users check whether gust behavior may align with pollutant mixing or ventilation.",
        intended_interpretation="Look for clear patterns and uncertainty together.",
        misunderstandings=("Small bar differences may not be meaningful.", "Gustiness is not causal proof."),
        glossary=(
            _term("Gust ratio", "A measure comparing gust behavior with normal wind."),
            _term("Quintile", "One of five groups made by sorting values."),
            _term("Confidence interval", "A range showing uncertainty around an estimate."),
        ),
        related_investigations=("A-10", "A-15", "A-06"),
    ),
    "A-12": _chart(
        reading_summary="This chart compares PM2.5 across day-night temperature spread groups.",
        visualization_reason="Band bars simplify temperature spread into readable groups for comparison.",
        metrics=(
            _metric("Diurnal temperature spread", "Difference between daily high and low temperature.", "It can relate to atmospheric stability."),
            _metric("Mean PM2.5", "Average pollution in each band.", "It shows burden by spread group.", high="Worse pollution."),
            _metric("Median PM2.5", "Middle pollution value.", "It checks whether averages are skewed."),
        ),
        visual_components=(
            _component("Bars", "Mean PM2.5 by spread band.", "They show group differences.", "Large differences between bands."),
            _component("Spread band axis", "Grouped temperature spread.", "It makes a continuous variable readable.", "Which spread groups are highest."),
            _component("Hover median", "Typical PM2.5 context.", "It adds robustness beyond the mean.", "Mean-median differences."),
        ),
        patterns=("Large bar differences suggest temperature spread may matter.", "Similar bars suggest weak separation.", "Mean-median gaps may indicate skew."),
        real_world_meaning="It supports investigation of atmospheric stability context for pollution.",
        intended_interpretation="Treat this as a weather-context comparison, not a causal finding.",
        misunderstandings=("Diurnal spread is not an everyday term.", "A high bar does not mean every day in that band was polluted."),
        glossary=(
            _term("Diurnal temperature spread", "The difference between a day's high and low temperature."),
            _term("Median", "The middle value."),
            _term("Atmospheric stability", "Conditions where air mixing may be limited."),
        ),
        related_investigations=("A-08", "A-15", "A-03"),
    ),
    "A-13": _chart(
        reading_summary="This chart groups pollution records into understandable atmospheric regimes.",
        visualization_reason="A regime scatter preserves individual records while making rule-based weather-condition groups visible.",
        metrics=(
            _metric("Vertical visibility", "How clear the air is.", "Low visibility can indicate haze or pollution context.", low="Poorer clarity."),
            _metric("PM2.5", "Fine-particle pollution.", "It shows pollution burden.", high="More unhealthy air."),
            _metric("Regime label", "Rule-based atmospheric condition group.", "It translates technical weather patterns into understandable categories."),
        ),
        visual_components=(
            _component("Dots", "Pollution-weather records.", "They show variation inside each regime.", "Clusters with high PM2.5."),
            _component("Regime colors", "Baseline, Stagnation Trap, Dispersive Relief, and Pressure Lock.", "They make condition groups readable.", "Which regime carries severe points."),
            _component("Highlight styling", "Selected regime emphasis.", "It supports focused comparison.", "Whether faded points are background context."),
        ),
        patterns=("Stagnation Trap points with low visibility and high PM2.5 are concerning.", "Dispersive Relief with lower PM2.5 may indicate cleaner ventilation context.", "Clusters reveal regime differences."),
        real_world_meaning="It helps translate technical atmospheric conditions into plain-language environmental states.",
        intended_interpretation="Compare regimes to see which conditions align with polluted air.",
        misunderstandings=("Regimes are rule-based labels, not AI predictions.", "They do not prove causes."),
        glossary=(
            _term("Atmospheric regime", "A named group of weather conditions."),
            _term("Stagnation trap", "Conditions where pollution may remain trapped."),
            _term("Dispersive relief", "Conditions where air movement may help reduce pollution."),
        ),
        related_investigations=("A-06", "A-14", "A-15"),
    ),
    "A-14": _chart(
        reading_summary="This chart shows which season-pressure combinations have the highest PM2.5.",
        visualization_reason="A heatmap efficiently compares season and pressure band against pollution burden.",
        metrics=(
            _metric("Season", "Seasonal period.", "It frames pollution timing."),
            _metric("SLP band", "Grouped sea-level pressure range.", "It frames pressure context."),
            _metric("Mean PM2.5", "Average pollution for each combination.", "It identifies high-burden conditions.", high="More pollution."),
        ),
        visual_components=(
            _component("Season-pressure grid", "One season and pressure band per cell.", "It combines two atmospheric categories.", "Dark cells."),
            _component("Cell color", "Mean PM2.5.", "It shows severity.", "Dark rows, columns, or isolated hotspots."),
            _component("Axes", "Season and SLP band categories.", "They define the comparison.", "Which combinations are highest."),
        ),
        patterns=("Dark rows suggest high-pollution seasons.", "Dark columns suggest high-pollution pressure bands.", "Dark cells identify combined hotspots."),
        real_world_meaning="It supports seasonal monitoring around pressure regimes associated with pollution burden.",
        intended_interpretation="Use it to identify concerning season-pressure combinations and follow up in A-06 or A-13.",
        misunderstandings=("Dark cells are associations, not causal proof.", "Cells hide day-level variation."),
        glossary=(
            _term("SLP", "Sea-level pressure."),
            _term("Pressure band", "A grouped pressure range."),
            _term("Heatmap", "A grid where color shows value."),
        ),
        related_investigations=("A-09", "A-06", "A-13"),
    ),
    "A-15": _chart(
        reading_summary="This advanced view helps users explore many weather-PM2.5 relationships at once.",
        visualization_reason="A pairplot matrix shows distributions and pairwise relationships in one exploratory workspace.",
        metrics=(
            _metric("Weather variables", "Temperature, minimum temperature, pressure, humidity, visibility, and wind.", "They provide environmental context for PM2.5."),
            _metric("PM2.5", "Fine-particle pollution.", "It is the outcome users compare against weather conditions.", high="More unhealthy air."),
            _metric("Correlation", "Fallback measure of how two variables move together.", "It helps detect relationships when scatter matrix is unavailable.", caution="Correlation is not causation."),
        ),
        visual_components=(
            _component("Matrix layout", "Variables compared pairwise.", "It supports broad exploration.", "Panels involving PM2.5."),
            _component("Diagonal distributions", "One-variable spread.", "They show how each variable behaves.", "Skewed or unusual shapes."),
            _component("Off-diagonal scatter plots", "Two-variable relationships.", "They reveal clusters and slopes.", "Category-colored clusters or clear trends."),
        ),
        patterns=("Sloped clouds suggest relationships.", "Category colors clustering in regions show pollution severity patterns.", "Strong correlation cells are leads for investigation, not final answers."),
        real_world_meaning="It gives analysts a map of possible weather-pollution relationships for deeper follow-up.",
        intended_interpretation="Use it as an exploratory lab view that helps form better questions.",
        misunderstandings=("Pairplots can overwhelm non-technical users.", "Correlation does not prove causation.", "Sampling may hide rare outliers."),
        glossary=(
            _term("Pairplot", "A matrix comparing many variables two at a time."),
            _term("Correlation", "A number showing how strongly two variables move together."),
            _term("Sampling", "Showing a subset of records to keep a chart readable."),
        ),
        related_investigations=("A-06", "A-08", "A-13"),
    ),
}


_WEAK_SIGNAL_CHARTS = {
    "A-06",
    "A-07",
    "A-08",
    "A-09",
    "A-10",
    "A-11",
    "A-12",
    "A-13",
    "A-14",
    "A-15",
    "T-08",
    "T-10",
    "T-12",
    "T-14",
}


def _legacy_situation_payload(entry: ExplainabilityEntry, payload: dict[str, object]) -> dict[str, object]:
    """Return explicit temporary compatibility mappings for unmigrated charts."""

    reading_summary = str(payload.get("reading_summary", ""))
    real_world = str(payload.get("real_world_meaning", ""))
    intended = str(payload.get("intended_interpretation", ""))
    patterns = tuple(payload.get("patterns", ()))
    misunderstandings = tuple(payload.get("misunderstandings", ()))
    related = tuple(payload.get("related_investigations", ()))
    visual_components = tuple(payload.get("visual_components", ()))
    metrics = tuple(payload.get("metrics", ()))
    limitations = entry.limitations

    if entry.dashboard == "aqi":
        affected = "People spending time outdoors in the selected air-quality scope."
        experience = real_world or "The reading affects how people understand exposure and outdoor comfort."
        scope = "This applies to the filtered period and category context, not every day in the city."
        normal_consequence = "Air-quality burden is not elevated in the current view."
        concern_consequence = "Outdoor exposure and public-health attention become more relevant."
    else:
        affected = "People traveling through the selected traffic scope."
        experience = real_world or "The reading affects delay, route reliability, and movement through the city."
        scope = "This applies to the filtered records, not guaranteed live citywide traffic."
        normal_consequence = "Road movement appears manageable in the current view."
        concern_consequence = "Delay risk and operational attention become more relevant."

    uncertainty = ""
    if entry.surface_id in _WEAK_SIGNAL_CHARTS:
        uncertainty = (
            "The evidence may be weak or sparse in narrow filter scopes; if observations are limited, "
            "there is not enough evidence to conclude a strong relationship."
        )

    next_reason = ""
    if related:
        next_reason = f"Use {related[0]} next if you need one connected follow-up view."

    return {
        **payload,
        "dominant_takeaway": reading_summary,
        "situation_verdict": reading_summary,
        "significance": real_world or entry.decision_relevance,
        "focus_point": intended or entry.when_to_use,
        "human_impact": HumanImpact(
            who_is_affected=affected,
            what_they_experience=experience,
            duration_or_scope=scope,
        ),
        "pattern_consequence": patterns[0] if patterns else real_world,
        "next_investigation_reason": next_reason,
        "misunderstanding_guard": misunderstandings[0] if misunderstandings else entry.misinterpretation_warning,
        "confidence_anchor": "You now have the main takeaway; use deeper sections only if you need evidence details.",
        "uncertainty_note": uncertainty,
        "consequence_map": (
            ConsequenceMapEntry(
                data_state="Normal or low concern",
                consequence=normal_consequence,
                affected_group=affected,
                confidence="medium",
                is_normal_state=True,
            ),
            ConsequenceMapEntry(
                data_state="Elevated or concerning pattern",
                consequence=concern_consequence,
                affected_group=affected,
                confidence="medium",
            ),
        ),
        "analyst_detail": tuple(
            f"{metric.name}: {metric.meaning} {metric.why_it_matters}".strip() for metric in metrics
        )
        + limitations,
        "visualization_anatomy": visual_components,
        "guided_reading": intended or entry.when_to_use,
        "semantic_migration_status": "legacy",
    }


def _migrated_situation_payload(entry: ExplainabilityEntry, payload: dict[str, object]) -> dict[str, object]:
    """Return independently authored situation content for migrated reference charts."""

    base = _legacy_situation_payload(entry, payload)
    authored = _MIGRATED_SITUATION_CONTENT.get(entry.surface_id)
    if authored is None:
        return base
    return {**base, **authored, "semantic_migration_status": "migrated"}


_MIGRATED_SITUATION_CONTENT: dict[str, dict[str, object]] = {
    "T-02": {
        "dominant_takeaway": (
            "Area profiles are useful when they reveal broad operational stress instead of one isolated issue."
        ),
        "situation_verdict": (
            "The main situation is whether one area stays concerning across congestion, speed, and capacity pressure."
        ),
        "significance": (
            "Broad stress matters because it can point to a wider operating problem, while one spike may need a narrower follow-up."
        ),
        "focus_point": (
            "Pick one area profile first and check whether congestion, speed, and capacity pressure move together."
        ),
        "human_impact": HumanImpact(
            who_is_affected="People traveling through areas where several traffic pressures line up.",
            what_they_experience="Trips may feel less reliable when crowding, slow movement, and limited road headroom appear together.",
            duration_or_scope="This applies to the selected area profiles and current traffic filters.",
        ),
        "pattern_consequence": (
            "A broad high profile calls for area-level review; a single-dimension spike points to a more specific issue."
        ),
        "next_investigation_reason": (
            "Check whether the same area also appears highly stressed in the area stress profile."
        ),
        "misunderstanding_guard": (
            "Do not treat normalized line height as an exact raw measurement or every crossing as meaningful conflict."
        ),
        "confidence_anchor": (
            "You now know whether the area looks broadly stressed or only stressed in one narrow way."
        ),
        "uncertainty_note": (
            "If area lines are tightly grouped or records are sparse, there may be insufficient evidence to separate profiles confidently."
        ),
        "guided_reading": (
            "Read one area at a time. Ignore crossings first. Prioritize congestion, speed, and capacity pressure before using other dimensions as context."
        ),
        "analyst_detail": (
            "Profile values are normalized comparison scores, so they support relative pattern reading rather than raw-unit measurement.",
            "Congestion, speed, and capacity pressure are the first interpretation dimensions because they explain practical movement breakdown.",
            "Incident, exposure, compliance, and environmental fields should support the primary profile, not replace it in Simple Mode.",
            "Line crossings can reflect different scales or profile tradeoffs; they should not be treated as direct cause or contradiction.",
        ),
        "visualization_anatomy": (
            _component(
                "Area profile line",
                "One area's pattern across several traffic conditions.",
                "It lets users see whether pressure is broad or narrow.",
                "Follow one line first instead of comparing every line.",
            ),
            _component(
                "Primary dimensions",
                "Congestion, speed, and capacity pressure.",
                "They are the first conditions to check because they describe practical movement stress.",
                "Broad concern appears when these dimensions are elevated together.",
            ),
            _component(
                "Normalized scale",
                "A shared comparison scale used across unlike traffic measures.",
                "It makes profile shape comparable without claiming raw-unit precision.",
                "Treat height as relative comparison, not an exact percentage or speed.",
            ),
            _component(
                "Background lines",
                "Other areas shown for comparison context.",
                "They help users judge whether the focused area is unusual.",
                "Use them after the first area profile is understood.",
            ),
        ),
        "consequence_map": (
            ConsequenceMapEntry(
                data_state="One dimension stands out",
                consequence="Follow-up can focus on the specific pressure dimension instead of treating the whole area as broadly stressed.",
                affected_group="People traveling through the selected area",
                confidence="medium",
                is_normal_state=True,
            ),
            ConsequenceMapEntry(
                data_state="Several primary dimensions elevated together",
                consequence="The area may need broader operational review because pressure appears across movement and capacity conditions.",
                affected_group="Commuters, bus riders, and traffic operations teams",
                confidence="medium",
            ),
        ),
    },
    "T-01": {
        "dominant_takeaway": (
            "Road pressure is easiest to understand by finding whether one area is driving the strain "
            "or whether stress is spread across the network."
        ),
        "situation_verdict": (
            "The traffic situation is about concentration: a few areas can create most of the practical "
            "delay risk even when the whole network is not equally stressed."
        ),
        "significance": (
            "If pressure is concentrated, targeted area review matters more than treating every road user "
            "as facing the same level of disruption."
        ),
        "focus_point": (
            "Start with the leading stress area, then check whether nearby areas are also elevated or whether "
            "the pressure is mostly isolated."
        ),
        "human_impact": HumanImpact(
            who_is_affected="Commuters, bus riders, delivery teams, and pedestrians moving through the leading stress areas.",
            what_they_experience=(
                "Trips through those areas may feel slower and less predictable, while other parts of the "
                "network may be less affected."
            ),
            duration_or_scope="This applies to the selected dashboard filters, not guaranteed live citywide traffic.",
        ),
        "pattern_consequence": (
            "A concentrated pattern means one local bottleneck can deserve attention before a broad citywide response."
        ),
        "next_investigation_reason": (
            "Check whether the same stressed area contains roads that are also close to capacity."
        ),
        "misunderstanding_guard": (
            "Do not read this as the cause of congestion or as live traffic for every area in Bengaluru."
        ),
        "confidence_anchor": (
            "You now know whether to think about the situation as broad network strain or focused area pressure."
        ),
        "uncertainty_note": "",
        "guided_reading": (
            "First decide whether the highest-stress area stands apart from the rest. Then use the follow-up "
            "road-level view only if that concentration needs explanation."
        ),
        "consequence_map": (
            ConsequenceMapEntry(
                data_state="Low or evenly distributed road pressure",
                consequence="Movement is likely manageable in the selected scope, so broad intervention is less urgent.",
                affected_group="Road users in the selected traffic scope",
                confidence="medium",
                is_normal_state=True,
            ),
            ConsequenceMapEntry(
                data_state="One or two areas dominate congestion pressure",
                consequence="Targeted area review is more useful than treating the whole network as equally disrupted.",
                affected_group="Travelers passing through the leading stress areas",
                confidence="medium",
            ),
            ConsequenceMapEntry(
                data_state="Many areas are elevated together",
                consequence="Route reliability may be weaker across the network, not only around one bottleneck.",
                affected_group="Commuters and operational planners across the selected traffic scope",
                confidence="medium",
            ),
        ),
    },
    "A-05": {
        "dominant_takeaway": (
            "The important question is whether polluted air clears quickly or stays elevated long enough to become repeated exposure."
        ),
        "situation_verdict": (
            "Air quality concern becomes more serious when high PM2.5 persists for several days instead of appearing as one short spike."
        ),
        "significance": (
            "Persistent pollution changes the practical risk because people may breathe poor air repeatedly, even if any single day looks temporary."
        ),
        "focus_point": (
            "Focus on stretches where the smoother pollution line remains high after daily values rise and fall."
        ),
        "human_impact": HumanImpact(
            who_is_affected="Children, older adults, outdoor workers, and people with asthma or breathing sensitivity.",
            what_they_experience=(
                "Repeated high-pollution days can mean more irritation, reduced outdoor comfort, and a stronger reason to limit prolonged exposure."
            ),
            duration_or_scope="This applies to the filtered time period; it does not identify the pollution source.",
        ),
        "pattern_consequence": (
            "A sustained high period matters more than a single peak because exposure can accumulate across multiple days."
        ),
        "next_investigation_reason": (
            "Check whether pressure and visibility conditions line up with the same polluted period."
        ),
        "misunderstanding_guard": (
            "Do not treat one spike as a full pollution episode, and do not treat persistence as proof of a specific pollution source."
        ),
        "confidence_anchor": (
            "You now know whether the concern is a brief bad day or a longer exposure period."
        ),
        "uncertainty_note": (
            "If the selected period has sparse observations or large gaps, there may be insufficient evidence to judge persistence confidently."
        ),
        "guided_reading": (
            "Read the smoother line as the exposure story. Daily jumps matter, but the key signal is whether pollution stays high after the spike."
        ),
        "consequence_map": (
            ConsequenceMapEntry(
                data_state="Short isolated PM2.5 spike",
                consequence="The episode may be brief, so immediate context matters more than long-term exposure interpretation.",
                affected_group="People outdoors during the spike",
                confidence="medium",
                is_normal_state=True,
            ),
            ConsequenceMapEntry(
                data_state="Multi-day elevated PM2.5",
                consequence="Repeated exposure becomes the main concern, especially for sensitive groups.",
                affected_group="Children, older adults, outdoor workers, and respiratory-sensitive residents",
                confidence="medium",
            ),
            ConsequenceMapEntry(
                data_state="Sparse or interrupted observations",
                consequence="There is not enough evidence to conclude whether pollution truly persisted.",
                affected_group="Anyone relying on the selected time window for exposure judgment",
                confidence="low",
            ),
        ),
    },
    "T-03": {
        "dominant_takeaway": (
            "The key question is whether road pressure is becoming a recurring pattern over time or staying limited to short periods."
        ),
        "situation_verdict": (
            "Congestion matters more when the same areas keep rising or staying elevated across months."
        ),
        "significance": (
            "A repeated monthly pattern gives planners a timing problem, not just a location problem."
        ),
        "focus_point": (
            "Look for the area whose pressure stays high or climbs while others remain steadier."
        ),
        "human_impact": HumanImpact(
            who_is_affected="Commuters and transport operators who depend on predictable monthly movement.",
            what_they_experience="Recurring pressure can make travel reliability worse during known periods, not just on isolated bad days.",
            duration_or_scope="This applies to the filtered months and areas, not live traffic today.",
        ),
        "pattern_consequence": (
            "If the same area stays elevated month after month, follow-up should focus on recurring causes rather than one-time disruption."
        ),
        "next_investigation_reason": (
            "Check the area-month heatmap to see whether the timing pattern concentrates in specific area-month combinations."
        ),
        "misunderstanding_guard": (
            "Do not treat one monthly jump as proof that congestion is permanently worsening."
        ),
        "confidence_anchor": (
            "You now know whether the traffic problem looks temporary, recurring, or uneven across areas."
        ),
        "uncertainty_note": (
            "If the filtered date range is short, there may be insufficient evidence to call the movement a real trend."
        ),
        "guided_reading": (
            "Follow the direction of each area over time, then ask whether the movement repeats or only appears once."
        ),
        "consequence_map": (
            ConsequenceMapEntry(
                data_state="Flat or low monthly pressure",
                consequence="The selected period does not show a strong recurring congestion burden.",
                affected_group="Road users in the selected monthly scope",
                confidence="medium",
                is_normal_state=True,
            ),
            ConsequenceMapEntry(
                data_state="Repeated monthly elevation",
                consequence="Planning attention should shift toward recurring timing and area patterns.",
                affected_group="Commuters and traffic operations teams",
                confidence="medium",
            ),
        ),
    },
    "T-05": {
        "dominant_takeaway": (
            "The roads needing attention first are the ones that are crowded and have little spare capacity."
        ),
        "situation_verdict": (
            "Some roads may be fragile because pressure and capacity strain are happening together."
        ),
        "significance": (
            "A fragile road can turn a small disruption into wider delay because it has less room to absorb problems."
        ),
        "focus_point": (
            "Pay attention to roads that sit in the high-pressure, low-headroom group."
        ),
        "human_impact": HumanImpact(
            who_is_affected="Drivers, bus riders, delivery teams, and people crossing or walking near stressed corridors.",
            what_they_experience="Movement around those roads may feel slower, less reliable, and more sensitive to incidents.",
            duration_or_scope="This applies to the current filtered road records.",
        ),
        "pattern_consequence": (
            "A road under both congestion and capacity pressure is a stronger follow-up candidate than a road with only one issue."
        ),
        "next_investigation_reason": (
            "Check whether these same roads also show speed-collapse risk."
        ),
        "misunderstanding_guard": (
            "Do not read priority position as proof of the root cause; it only identifies where stress is concentrated."
        ),
        "confidence_anchor": (
            "You now know which roads deserve attention before lower-pressure corridors."
        ),
        "uncertainty_note": "",
        "guided_reading": (
            "Start with roads under both kinds of pressure. Then use related views to test whether delay, incidents, or speed collapse explain the risk."
        ),
        "consequence_map": (
            ConsequenceMapEntry(
                data_state="Few roads combine congestion and capacity strain",
                consequence="Road pressure appears more manageable and less structurally fragile.",
                affected_group="Road users in the selected road scope",
                confidence="medium",
                is_normal_state=True,
            ),
            ConsequenceMapEntry(
                data_state="Several roads combine congestion and capacity strain",
                consequence="Small incidents can matter more because stressed roads have less spare room.",
                affected_group="Commuters and traffic operations teams",
                confidence="medium",
            ),
        ),
    },
    "A-01": {
        "dominant_takeaway": (
            "The main issue is whether poor air quality is occasional or common enough to shape everyday exposure."
        ),
        "situation_verdict": (
            "Air quality becomes more concerning when unhealthy categories make up a meaningful share of the selected period."
        ),
        "significance": (
            "Category mix matters because people experience repeated exposure, not only one average pollution number."
        ),
        "focus_point": (
            "Focus on the category that appears most often and whether severe days are present."
        ),
        "human_impact": HumanImpact(
            who_is_affected="People outdoors, especially children, older adults, and anyone with breathing sensitivity.",
            what_they_experience="A higher share of unhealthy days can mean more days where outdoor activity needs caution.",
            duration_or_scope="This applies to the selected AQI filters and time period.",
        ),
        "pattern_consequence": (
            "If unhealthy categories dominate, the situation is about repeated exposure rather than an isolated bad day."
        ),
        "next_investigation_reason": (
            "Check whether the polluted periods cluster by week or month."
        ),
        "misunderstanding_guard": (
            "Do not treat the average alone as the whole story; the mix of categories changes the practical meaning."
        ),
        "confidence_anchor": (
            "You now know whether the selected period mostly feels clean, mixed, or repeatedly unhealthy."
        ),
        "uncertainty_note": "",
        "guided_reading": (
            "Start with the most common category, then check whether severe days are rare or frequent."
        ),
        "consequence_map": (
            ConsequenceMapEntry(
                data_state="Good or moderate categories dominate",
                consequence="Outdoor conditions are less concerning for most people in the selected period.",
                affected_group="General public in the selected AQI scope",
                confidence="medium",
                is_normal_state=True,
            ),
            ConsequenceMapEntry(
                data_state="Unhealthy or severe categories are common",
                consequence="Repeated exposure becomes the practical concern, especially for sensitive groups.",
                affected_group="Children, older adults, outdoor workers, and respiratory-sensitive residents",
                confidence="medium",
            ),
        ),
    },
    "A-06": {
        "dominant_takeaway": (
            "The useful question is whether polluted air lines up with weather conditions that can trap or reveal poor dispersion."
        ),
        "situation_verdict": (
            "PM2.5 patterns become more meaningful when high pollution appears alongside poor visibility or pressure conditions."
        ),
        "significance": (
            "That matters because weather context can help explain when pollution is likely to linger, even without proving the source."
        ),
        "focus_point": (
            "Look for high-pollution areas that also sit near low visibility or pressure-related clustering."
        ),
        "human_impact": HumanImpact(
            who_is_affected="People outdoors during weather conditions that coincide with elevated PM2.5.",
            what_they_experience="Air may feel hazier or more irritating when pollution and poor dispersion conditions appear together.",
            duration_or_scope="This applies to the filtered weather and PM2.5 records, not a forecast.",
        ),
        "pattern_consequence": (
            "When high pollution clusters with low visibility, follow-up should focus on persistence and atmospheric context rather than a single day."
        ),
        "next_investigation_reason": (
            "Check whether the same conditions appear in the atmospheric-regime view."
        ),
        "misunderstanding_guard": (
            "Do not read the weather relationship as proof that pressure or visibility caused the pollution."
        ),
        "confidence_anchor": (
            "You now know whether weather context is worth using to explain the pollution pattern."
        ),
        "uncertainty_note": (
            "If the filtered records are sparse or scattered, there may be insufficient evidence to call the relationship meaningful."
        ),
        "guided_reading": (
            "Look for clusters, not isolated cells. A single high-pollution point is weaker evidence than repeated clustering under similar weather."
        ),
        "consequence_map": (
            ConsequenceMapEntry(
                data_state="No clear pollution-weather clustering",
                consequence="Weather context is not strong enough to explain the selected pollution pattern.",
                affected_group="People using the selected AQI view for exposure context",
                confidence="low",
                is_normal_state=True,
            ),
            ConsequenceMapEntry(
                data_state="High pollution clusters with low visibility or pressure conditions",
                consequence="Atmospheric context becomes a useful follow-up for understanding why pollution may linger.",
                affected_group="Outdoor workers, sensitive residents, and public-health planners",
                confidence="medium",
            ),
        ),
    },
}

_MIGRATED_SITUATION_CONTENT.update(
    {
        "T-04": {
            "dominant_takeaway": "The key issue is whether congestion is routine on certain weekdays or only occasionally spikes.",
            "situation_verdict": "Weekday pressure matters when some days repeatedly feel less reliable than others.",
            "significance": "A predictable weekday burden can shape staffing, travel planning, and roadwork timing.",
            "focus_point": "Look for days where typical pressure is high or severe values appear often.",
            "human_impact": HumanImpact(
                who_is_affected="Commuters, school trips, and operations teams planning around weekly routines.",
                what_they_experience="Some weekdays may feel consistently slower or more uncertain than others.",
                duration_or_scope="This applies to the filtered weekday records.",
            ),
            "pattern_consequence": "A routine weekday burden calls for scheduling attention, while rare spikes call for incident follow-up.",
            "next_investigation_reason": "Check whether the same weekday pressure also appears in monthly patterns.",
            "misunderstanding_guard": "Do not treat one extreme weekday value as the normal condition for that day.",
            "confidence_anchor": "You now know whether weekly congestion looks routine or occasional.",
            "uncertainty_note": "If a weekday has sparse records, there may be insufficient evidence to compare it confidently.",
            "guided_reading": "Compare typical pressure first, then notice whether severe values are frequent or rare.",
            "consequence_map": (
                ConsequenceMapEntry(
                    data_state="Similar weekday pressure",
                    consequence="Weekly timing is probably not the main explanation in the selected view.",
                    affected_group="Road users in the selected weekly scope",
                    confidence="medium",
                    is_normal_state=True,
                ),
                ConsequenceMapEntry(
                    data_state="One weekday repeatedly elevated",
                    consequence="Planning attention should focus on recurring weekly conditions.",
                    affected_group="Commuters and traffic operations teams",
                    confidence="medium",
                ),
            ),
        },
        "T-06": {
            "dominant_takeaway": "Environmental burden matters most when a few roads or areas carry a large share of the impact.",
            "situation_verdict": "The situation is about concentration of burden, not only total congestion.",
            "significance": "When burden is concentrated, targeted corridor review can matter more than broad network action.",
            "focus_point": "Start with the largest contributors and ask whether one road or area dominates.",
            "human_impact": HumanImpact(
                who_is_affected="People living, walking, or traveling near the highest-burden corridors.",
                what_they_experience="Traffic pressure may carry broader environmental cost around specific corridors.",
                duration_or_scope="This applies to the selected traffic and environmental-impact records.",
            ),
            "pattern_consequence": "A concentrated burden points to corridors where traffic stress may have wider environmental consequences.",
            "next_investigation_reason": "Check whether those same roads also show high congestion pressure against the baseline.",
            "misunderstanding_guard": "Do not treat the burden score as a direct pollution measurement.",
            "confidence_anchor": "You now know whether environmental attention should start broadly or with a few corridors.",
            "uncertainty_note": "",
            "guided_reading": "Look for dominance. One large contributor means a focused follow-up is more useful.",
            "consequence_map": (
                ConsequenceMapEntry(
                    data_state="Burden spread across many roads",
                    consequence="Environmental attention may need a broader network lens.",
                    affected_group="Road users and nearby residents in the selected scope",
                    confidence="medium",
                    is_normal_state=True,
                ),
                ConsequenceMapEntry(
                    data_state="One corridor dominates burden",
                    consequence="A targeted corridor review becomes the clearest next step.",
                    affected_group="People near the dominant burden corridor",
                    confidence="medium",
                ),
            ),
        },
        "T-07": {
            "dominant_takeaway": "The important roads are the ones running above the local pressure baseline.",
            "situation_verdict": "Some roads may be carrying more pressure than the surrounding system would lead you to expect.",
            "significance": "Above-baseline pressure is useful because it separates local outliers from normal network stress.",
            "focus_point": "Focus on roads with the strongest positive deviation from the baseline.",
            "human_impact": HumanImpact(
                who_is_affected="People moving through roads that stand out above the local pressure baseline.",
                what_they_experience="Those roads may feel more strained than nearby alternatives in the same filtered context.",
                duration_or_scope="This applies to the active traffic filters and baseline.",
            ),
            "pattern_consequence": "A strong positive deviation is a practical reason to inspect that road before lower-pressure roads.",
            "next_investigation_reason": "Check whether the same roads also appear in the road-priority quadrant.",
            "misunderstanding_guard": "Do not read a positive deviation as proof that pedestrian activity caused the pressure.",
            "confidence_anchor": "You now know which roads stand out from the current baseline.",
            "uncertainty_note": "",
            "guided_reading": "Compare each road with the baseline, then focus on the roads that stand farthest above it.",
            "consequence_map": (
                ConsequenceMapEntry(
                    data_state="Roads close to baseline",
                    consequence="Pressure appears aligned with the surrounding system.",
                    affected_group="Road users in the selected scope",
                    confidence="medium",
                    is_normal_state=True,
                ),
                ConsequenceMapEntry(
                    data_state="Roads far above baseline",
                    consequence="Local follow-up is more useful than only reading the network average.",
                    affected_group="People using the above-baseline roads",
                    confidence="medium",
                ),
            ),
        },
        "T-08": {
            "dominant_takeaway": "Incident pressure matters when congestion rises sharply after incident counts increase.",
            "situation_verdict": "The situation is about sensitivity: traffic may become less reliable when incidents accumulate.",
            "significance": "A sharp step means small increases in incidents can coincide with much worse movement.",
            "focus_point": "Look for the point where congestion changes suddenly between incident bands.",
            "human_impact": HumanImpact(
                who_is_affected="Travelers and responders moving through disruption-prone road conditions.",
                what_they_experience="Trips may become less predictable when incident load rises.",
                duration_or_scope="This applies to grouped incident records, not a live incident feed.",
            ),
            "pattern_consequence": "A strong step calls for disruption planning; a flat pattern makes incidents less central.",
            "next_investigation_reason": "Check whether speed also drops during the same high-pressure conditions.",
            "misunderstanding_guard": "Do not treat incident association as proof that incidents caused all congestion.",
            "confidence_anchor": "You now know whether incidents are worth treating as a major congestion context.",
            "uncertainty_note": "If incident bands have few records, there may be insufficient evidence to trust a sharp step.",
            "guided_reading": "Look for step changes, not tiny differences between neighboring bands.",
            "consequence_map": (
                ConsequenceMapEntry(
                    data_state="Little change across incident bands",
                    consequence="Incidents are not the clearest explanation in the selected view.",
                    affected_group="Road users in the selected incident scope",
                    confidence="medium",
                    is_normal_state=True,
                ),
                ConsequenceMapEntry(
                    data_state="Sharp congestion step at higher incidents",
                    consequence="Disruption readiness becomes more important for those conditions.",
                    affected_group="Travelers and traffic operations teams",
                    confidence="medium",
                ),
            ),
        },
        "T-09": {
            "dominant_takeaway": "Speed collapse matters when high congestion and low speed happen together.",
            "situation_verdict": "The most serious traffic state is not crowding alone; it is crowding that also slows movement sharply.",
            "significance": "Low speed turns congestion from pressure into practical mobility breakdown.",
            "focus_point": "Focus on records where congestion is high while speed is already low.",
            "human_impact": HumanImpact(
                who_is_affected="People traveling through roads where traffic is both crowded and slow.",
                what_they_experience="Trips may feel stuck rather than merely delayed.",
                duration_or_scope="This applies to the selected record-level traffic scope.",
            ),
            "pattern_consequence": "High congestion with low speed deserves more attention than high congestion with tolerable movement.",
            "next_investigation_reason": "Check whether those same roads appear in the road-priority quadrant.",
            "misunderstanding_guard": "Do not treat every congested record as speed collapse.",
            "confidence_anchor": "You now know when congestion becomes a movement failure.",
            "uncertainty_note": "",
            "guided_reading": "Look for the combination of crowded and slow. Either condition alone is less severe.",
            "consequence_map": (
                ConsequenceMapEntry(
                    data_state="Congestion without very low speed",
                    consequence="Traffic is pressured, but movement has not fully broken down.",
                    affected_group="Road users in the selected scope",
                    confidence="medium",
                    is_normal_state=True,
                ),
                ConsequenceMapEntry(
                    data_state="High congestion with low speed",
                    consequence="Mobility breakdown becomes the practical concern.",
                    affected_group="Travelers on affected roads",
                    confidence="medium",
                ),
            ),
        },
        "T-10": {
            "dominant_takeaway": "Public transport context matters when usage bands line up with different road-pressure outcomes.",
            "situation_verdict": "The situation is about whether mobility mix appears connected with congestion, speed, or incident burden.",
            "significance": "If road pressure stays high even where public transport use is higher, the corridor may need deeper context.",
            "focus_point": "Compare whether higher usage bands come with lower pressure or whether stress remains.",
            "human_impact": HumanImpact(
                who_is_affected="Commuters choosing between road travel and public transport in the selected corridors.",
                what_they_experience="Higher public transport use may not automatically mean smoother roads.",
                duration_or_scope="This applies to grouped usage bands, not individual travel choices.",
            ),
            "pattern_consequence": "A mismatch between usage and lower congestion means mode context alone does not explain the pressure.",
            "next_investigation_reason": "Check whether high-pressure roads also have speed-collapse risk.",
            "misunderstanding_guard": "Do not treat public transport usage as a direct cause of lower or higher congestion.",
            "confidence_anchor": "You now know whether transport mix is worth deeper follow-up.",
            "uncertainty_note": "If usage groups are uneven, there may be insufficient evidence for a strong comparison.",
            "guided_reading": "Compare the direction across groups, then ask whether the pattern is clear or mixed.",
            "consequence_map": (
                ConsequenceMapEntry(
                    data_state="Similar pressure across usage bands",
                    consequence="Public transport usage is not the clearest separator in the selected view.",
                    affected_group="Commuters in the selected mobility scope",
                    confidence="medium",
                    is_normal_state=True,
                ),
                ConsequenceMapEntry(
                    data_state="Clear pressure difference across usage bands",
                    consequence="Mobility mix deserves follow-up as part of corridor interpretation.",
                    affected_group="Commuters and mobility planners",
                    confidence="medium",
                ),
            ),
        },
        "T-11": {
            "dominant_takeaway": "Road reliability matters when a road is not only sometimes bad, but often stressed.",
            "situation_verdict": "Some roads may have chronic pressure while others only have occasional peaks.",
            "significance": "Chronic pressure changes planning because users face repeated delay, not just rare disruption.",
            "focus_point": "Focus on roads with high typical pressure and a long severe tail.",
            "human_impact": HumanImpact(
                who_is_affected="People who regularly use roads with high typical congestion.",
                what_they_experience="Travel may feel consistently unreliable instead of occasionally delayed.",
                duration_or_scope="This applies to the selected road records.",
            ),
            "pattern_consequence": "A road with frequent high pressure deserves closer review than a road with one rare extreme.",
            "next_investigation_reason": "Check whether chronically stressed roads also exceed the baseline pressure view.",
            "misunderstanding_guard": "Do not judge a road only by its worst value; typical pressure matters too.",
            "confidence_anchor": "You now know which roads look routinely stressed rather than occasionally disrupted.",
            "uncertainty_note": "",
            "guided_reading": "Read typical pressure first, then use extreme values as supporting context.",
            "consequence_map": (
                ConsequenceMapEntry(
                    data_state="Most road values clustered lower",
                    consequence="Stress appears occasional rather than routine.",
                    affected_group="Regular road users in the selected scope",
                    confidence="medium",
                    is_normal_state=True,
                ),
                ConsequenceMapEntry(
                    data_state="High typical pressure with severe tail",
                    consequence="Recurring reliability problems become the practical concern.",
                    affected_group="Frequent users of the stressed roads",
                    confidence="medium",
                ),
            ),
        },
        "T-12": {
            "dominant_takeaway": "Weather and roadwork matter when certain combinations repeatedly line up with higher congestion.",
            "situation_verdict": "Some operating conditions may make road pressure more likely or more difficult to manage.",
            "significance": "Condition-based pressure can guide timing decisions for roadwork and traffic operations.",
            "focus_point": "Look for combinations that stand out clearly from the rest.",
            "human_impact": HumanImpact(
                who_is_affected="Travelers and operations teams dealing with weather and roadwork overlap.",
                what_they_experience="Trips may become less predictable when difficult conditions overlap.",
                duration_or_scope="This applies to grouped weather and roadwork records.",
            ),
            "pattern_consequence": "A standout combination deserves scheduling attention before routine conditions do.",
            "next_investigation_reason": "Check whether the same conditions appear during high-volume congestion periods.",
            "misunderstanding_guard": "Do not treat a darker condition as proof that weather or roadwork caused the congestion.",
            "confidence_anchor": "You now know whether operating conditions are worth planning around.",
            "uncertainty_note": "If some condition combinations have few records, there may be insufficient evidence to rank them.",
            "guided_reading": "Look for repeated standout combinations, not isolated high cells.",
            "consequence_map": (
                ConsequenceMapEntry(
                    data_state="No standout condition combination",
                    consequence="Weather and roadwork mix is not the clearest explanation in the selected view.",
                    affected_group="Road users in the selected operating scope",
                    confidence="medium",
                    is_normal_state=True,
                ),
                ConsequenceMapEntry(
                    data_state="One condition combination stands out",
                    consequence="Scheduling and mitigation attention should focus on that operating context.",
                    affected_group="Travelers and traffic operations teams",
                    confidence="medium",
                ),
            ),
        },
        "T-14": {
            "dominant_takeaway": "The highest-risk load appears where high traffic volume and congestion cluster together.",
            "situation_verdict": "Volume matters most when many records sit in crowded, high-load conditions.",
            "significance": "High-volume congestion can affect more trips than a severe but rarely used corridor.",
            "focus_point": "Focus on dense clusters where volume and congestion are both high.",
            "human_impact": HumanImpact(
                who_is_affected="Large numbers of travelers using busy corridors in the selected scope.",
                what_they_experience="Many trips may be exposed to slower, more crowded movement.",
                duration_or_scope="This applies to the selected record-level volume and congestion data.",
            ),
            "pattern_consequence": "A dense high-load cluster deserves follow-up because many trips may be affected at once.",
            "next_investigation_reason": "Check whether high-load corridors also appear in road-level priority views.",
            "misunderstanding_guard": "Do not treat sparse extreme points as more important than dense high-load clusters.",
            "confidence_anchor": "You now know where load and congestion combine into broader travel impact.",
            "uncertainty_note": "If dense areas are weak or sparse, there may be insufficient evidence to name a load hotspot.",
            "guided_reading": "Look for dense clusters first. Isolated points matter less unless they repeat.",
            "consequence_map": (
                ConsequenceMapEntry(
                    data_state="No dense high-volume congestion cluster",
                    consequence="Traffic load does not clearly concentrate into a major hotspot.",
                    affected_group="Travelers in the selected volume scope",
                    confidence="medium",
                    is_normal_state=True,
                ),
                ConsequenceMapEntry(
                    data_state="Dense high-volume high-congestion cluster",
                    consequence="Many trips may be affected by the same corridor pressure.",
                    affected_group="Travelers using high-load corridors",
                    confidence="medium",
                ),
            ),
        },
        "T-15": {
            "dominant_takeaway": "Area-month stress matters when pressure concentrates in specific places at specific times.",
            "situation_verdict": "The traffic issue may be a timing-and-location problem, not only a citywide average.",
            "significance": "Knowing when and where pressure concentrates makes follow-up more targeted.",
            "focus_point": "Look for area-month combinations that stay darker than their surroundings.",
            "human_impact": HumanImpact(
                who_is_affected="People traveling through areas during their highest-pressure months.",
                what_they_experience="Trips may feel worse during specific periods rather than all year.",
                duration_or_scope="This applies to the selected area and month records.",
            ),
            "pattern_consequence": "A recurring area-month hotspot points to targeted timing review.",
            "next_investigation_reason": "Check whether the same area has a worsening monthly trend.",
            "misunderstanding_guard": "Do not treat one dark month as proof that the area is always stressed.",
            "confidence_anchor": "You now know whether pressure is tied to a specific area and period.",
            "uncertainty_note": "",
            "guided_reading": "Find the darkest area-month cells, then check whether they repeat or stand alone.",
            "consequence_map": (
                ConsequenceMapEntry(
                    data_state="No clear area-month hotspot",
                    consequence="Timing and location do not strongly concentrate the selected pressure.",
                    affected_group="Road users in the selected area-month scope",
                    confidence="medium",
                    is_normal_state=True,
                ),
                ConsequenceMapEntry(
                    data_state="Repeated area-month hotspot",
                    consequence="Follow-up should focus on that area during the affected period.",
                    affected_group="Travelers in the hotspot area",
                    confidence="medium",
                ),
            ),
        },
        "A-02": {
            "dominant_takeaway": "Weekly pollution matters when bad air clusters into repeated blocks instead of isolated days.",
            "situation_verdict": "A polluted week can mean exposure lasts long enough for people to notice and adjust behavior.",
            "significance": "Weekly clustering is more practical than a single daily spike because routines repeat across the week.",
            "focus_point": "Focus on weeks that stay elevated and whether similar weeks repeat across years.",
            "human_impact": HumanImpact(
                who_is_affected="People with outdoor routines during polluted weeks.",
                what_they_experience="Outdoor activity may need more caution across several days.",
                duration_or_scope="This applies to the selected weekly AQI records.",
            ),
            "pattern_consequence": "Repeated polluted weeks point to exposure periods that may deserve planning attention.",
            "next_investigation_reason": "Check whether those weeks belong to a broader monthly or seasonal pattern.",
            "misunderstanding_guard": "Do not treat one dark week as proof of a permanent air-quality shift.",
            "confidence_anchor": "You now know whether pollution appears isolated or week-level persistent.",
            "uncertainty_note": "",
            "guided_reading": "Look for blocks of elevated weeks before focusing on single cells.",
            "consequence_map": (
                ConsequenceMapEntry(
                    data_state="Mostly low weekly burden",
                    consequence="Weekly exposure is less concerning in the selected scope.",
                    affected_group="People outdoors during the selected period",
                    confidence="medium",
                    is_normal_state=True,
                ),
                ConsequenceMapEntry(
                    data_state="Repeated elevated weeks",
                    consequence="Outdoor routines may need caution across several days.",
                    affected_group="Children, outdoor workers, and sensitive residents",
                    confidence="medium",
                ),
            ),
        },
        "A-03": {
            "dominant_takeaway": "Seasonal air quality matters when one season carries more high-pollution days than the others.",
            "situation_verdict": "Pollution burden may be seasonal, meaning exposure risk changes across the year.",
            "significance": "Seasonal burden helps people plan outdoor activity, public messaging, and health precautions.",
            "focus_point": "Focus on the season with the most right-shifted or high-pollution values.",
            "human_impact": HumanImpact(
                who_is_affected="Residents and outdoor workers during the worst pollution season.",
                what_they_experience="Some seasons may bring more frequent irritation or reduced outdoor comfort.",
                duration_or_scope="This applies to daily PM2.5 records grouped by season.",
            ),
            "pattern_consequence": "A clearly worse season shifts attention toward seasonal preparation rather than daily reaction.",
            "next_investigation_reason": "Check whether the same season also appears as a monthly hotspot.",
            "misunderstanding_guard": "Do not treat seasonal shape as a day-by-day timeline.",
            "confidence_anchor": "You now know whether air-quality burden is strongly seasonal.",
            "uncertainty_note": "",
            "guided_reading": "Compare seasons by where most values sit, not by one extreme value.",
            "consequence_map": (
                ConsequenceMapEntry(
                    data_state="Seasons look similar",
                    consequence="Season alone is not the clearest separator in the selected view.",
                    affected_group="People outdoors across the selected seasons",
                    confidence="medium",
                    is_normal_state=True,
                ),
                ConsequenceMapEntry(
                    data_state="One season clearly worse",
                    consequence="Seasonal preparation becomes more useful than treating all months equally.",
                    affected_group="Residents and public-health communicators",
                    confidence="medium",
                ),
            ),
        },
        "A-04": {
            "dominant_takeaway": "Monthly pollution matters when high PM2.5 returns in the same parts of the calendar.",
            "situation_verdict": "Air quality concern may be tied to recurring monthly timing rather than random bad days.",
            "significance": "Recurring monthly burden helps people anticipate when exposure risk is more likely.",
            "focus_point": "Look for months that are repeatedly elevated across years.",
            "human_impact": HumanImpact(
                who_is_affected="People planning outdoor work, school activity, or health precautions by month.",
                what_they_experience="Some months may bring more repeated poor-air days.",
                duration_or_scope="This applies to monthly PM2.5 averages in the selected scope.",
            ),
            "pattern_consequence": "Repeated monthly hotspots support preparation before those periods arrive.",
            "next_investigation_reason": "Check whether weekly blocks explain the same monthly burden.",
            "misunderstanding_guard": "Do not assume a moderate monthly value means every day was moderate.",
            "confidence_anchor": "You now know whether pollution timing looks calendar-linked.",
            "uncertainty_note": "",
            "guided_reading": "Look for repeated monthly hotspots, then compare whether they appear across multiple years.",
            "consequence_map": (
                ConsequenceMapEntry(
                    data_state="No recurring monthly hotspot",
                    consequence="Monthly timing is not the clearest exposure story.",
                    affected_group="People outdoors in the selected period",
                    confidence="medium",
                    is_normal_state=True,
                ),
                ConsequenceMapEntry(
                    data_state="Recurring elevated months",
                    consequence="Seasonal communication and planning become more relevant.",
                    affected_group="Residents, schools, and outdoor workers",
                    confidence="medium",
                ),
            ),
        },
        "A-07": {
            "dominant_takeaway": "Weather profiles matter only when pollution categories separate clearly.",
            "situation_verdict": "Different air-quality categories may have different weather contexts, but weak separation should be treated cautiously.",
            "significance": "Clear separation can guide follow-up; overlapping profiles mean the weather story is not simple.",
            "focus_point": "Look for weather dimensions where severe days stand apart from cleaner days.",
            "human_impact": HumanImpact(
                who_is_affected="People exposed during weather patterns that align with worse PM2.5 categories.",
                what_they_experience="Certain weather conditions may coincide with more uncomfortable outdoor air.",
                duration_or_scope="This applies to category-level weather summaries, not individual forecasts.",
            ),
            "pattern_consequence": "Separated profiles justify weather-context follow-up; overlapping profiles reduce confidence.",
            "next_investigation_reason": "Check whether pressure and visibility explain the same category separation.",
            "misunderstanding_guard": "Do not treat profile separation as a prediction model or causal proof.",
            "confidence_anchor": "You now know whether weather context clearly separates pollution categories.",
            "uncertainty_note": "If the shapes overlap heavily, there is not enough evidence for a strong category-weather claim.",
            "guided_reading": "Use broad separation as the signal. Small shape differences are not enough.",
            "consequence_map": (
                ConsequenceMapEntry(
                    data_state="Profiles overlap",
                    consequence="Weather context is too weak to explain category differences confidently.",
                    affected_group="People using weather context for AQI interpretation",
                    confidence="low",
                    is_normal_state=True,
                ),
                ConsequenceMapEntry(
                    data_state="Severe category profile separates",
                    consequence="Weather context deserves follow-up as part of exposure interpretation.",
                    affected_group="Sensitive residents and air-quality analysts",
                    confidence="medium",
                ),
            ),
        },
        "A-08": {
            "dominant_takeaway": "Temperature context matters only if higher PM2.5 repeatedly appears under lower minimum temperatures.",
            "situation_verdict": "Cold-period pollution may be worth attention when low temperatures and high PM2.5 cluster together.",
            "significance": "A clear cluster can help explain seasonal exposure patterns, but mixed points weaken the story.",
            "focus_point": "Look for repeated high-PM2.5 points at lower minimum temperatures.",
            "human_impact": HumanImpact(
                who_is_affected="People outdoors during colder periods in the selected AQI scope.",
                what_they_experience="Cold-period days may coincide with poorer outdoor air if the pattern is strong.",
                duration_or_scope="This applies to the filtered temperature and PM2.5 records.",
            ),
            "pattern_consequence": "A repeated low-temperature cluster deserves seasonal follow-up; scattered points do not.",
            "next_investigation_reason": "Check whether the same colder periods align with season and pressure patterns.",
            "misunderstanding_guard": "Do not treat temperature as the cause of pollution from this view alone.",
            "confidence_anchor": "You now know whether temperature context is worth deeper attention.",
            "uncertainty_note": "If the points are mixed or sparse, there may be insufficient evidence for a clear relationship.",
            "guided_reading": "Look for repeated clustering, not a few isolated high values.",
            "consequence_map": (
                ConsequenceMapEntry(
                    data_state="Mixed temperature and PM2.5 points",
                    consequence="Temperature alone is not a clear explanation in the selected view.",
                    affected_group="People interpreting cold-period air quality",
                    confidence="low",
                    is_normal_state=True,
                ),
                ConsequenceMapEntry(
                    data_state="High PM2.5 clusters at low temperature",
                    consequence="Cold-period context deserves follow-up in seasonal and pressure views.",
                    affected_group="Residents and sensitive outdoor groups",
                    confidence="medium",
                ),
            ),
        },
        "A-09": {
            "dominant_takeaway": "Pressure bands matter when certain pressure conditions repeatedly carry higher PM2.5.",
            "situation_verdict": "Pollution may align with pressure context, especially when the pattern repeats across seasons.",
            "significance": "Repeated pressure-band burden can help explain when pollution is more likely to accumulate.",
            "focus_point": "Look for pressure bands that stay elevated within more than one season.",
            "human_impact": HumanImpact(
                who_is_affected="People outdoors during pressure conditions that coincide with higher PM2.5.",
                what_they_experience="Some atmospheric conditions may line up with more uncomfortable air.",
                duration_or_scope="This applies to grouped pressure and season records.",
            ),
            "pattern_consequence": "A repeated pressure-band pattern makes atmospheric follow-up more useful.",
            "next_investigation_reason": "Check whether pressure also combines with visibility in the density view.",
            "misunderstanding_guard": "Do not treat pressure bands as proof of pollution cause.",
            "confidence_anchor": "You now know whether pressure context is worth following.",
            "uncertainty_note": "If seasonal groups are uneven, there may be insufficient evidence for a firm comparison.",
            "guided_reading": "Compare bands within each season, then ask whether the same band stays elevated.",
            "consequence_map": (
                ConsequenceMapEntry(
                    data_state="Pressure bands look similar",
                    consequence="Pressure is not the clearest separator in the selected scope.",
                    affected_group="People using atmospheric context for AQI interpretation",
                    confidence="medium",
                    is_normal_state=True,
                ),
                ConsequenceMapEntry(
                    data_state="One pressure band repeatedly higher",
                    consequence="Pressure context deserves atmospheric follow-up.",
                    affected_group="Public-health planners and sensitive residents",
                    confidence="medium",
                ),
            ),
        },
        "A-10": {
            "dominant_takeaway": "Wind context matters when stronger wind lines up with cleaner air, or when it fails to do so.",
            "situation_verdict": "Air movement may help explain pollution relief, but the pattern must be clear and consistent.",
            "significance": "If pollution stays high even with stronger wind, other conditions likely matter.",
            "focus_point": "Compare whether PM2.5 falls as wind bands strengthen within the same season.",
            "human_impact": HumanImpact(
                who_is_affected="People outdoors during low-wind or high-pollution conditions.",
                what_they_experience="Poor dispersion may make air feel more stagnant when pollution is elevated.",
                duration_or_scope="This applies to grouped wind and season records.",
            ),
            "pattern_consequence": "Clear wind-related relief supports dispersion follow-up; mixed patterns call for other weather context.",
            "next_investigation_reason": "Check whether pressure and visibility explain periods when wind does not bring relief.",
            "misunderstanding_guard": "Do not treat wind speed alone as controlling pollution.",
            "confidence_anchor": "You now know whether wind context helps explain the selected pollution burden.",
            "uncertainty_note": "If wind groups are sparse or uneven, there may be insufficient evidence for strong comparison.",
            "guided_reading": "Compare wind bands within seasons, not across unrelated seasonal conditions.",
            "consequence_map": (
                ConsequenceMapEntry(
                    data_state="PM2.5 similar across wind bands",
                    consequence="Wind speed is not the clearest explanation in the selected view.",
                    affected_group="People using wind context for AQI interpretation",
                    confidence="medium",
                    is_normal_state=True,
                ),
                ConsequenceMapEntry(
                    data_state="PM2.5 lower under stronger wind",
                    consequence="Dispersion context becomes a useful follow-up.",
                    affected_group="Outdoor groups and air-quality planners",
                    confidence="medium",
                ),
            ),
        },
        "A-11": {
            "dominant_takeaway": "Gustiness only matters if PM2.5 changes steadily across gust behavior groups.",
            "situation_verdict": "The pattern is useful when gust behavior separates cleaner and more polluted conditions.",
            "significance": "A weak or overlapping pattern means gustiness is not a strong explanation.",
            "focus_point": "Look for steady movement across groups and whether ranges overlap.",
            "human_impact": HumanImpact(
                who_is_affected="People outdoors during wind conditions that may affect pollutant mixing.",
                what_they_experience="Air may feel cleaner or more stagnant only if the gust pattern is clear.",
                duration_or_scope="This applies to grouped gust-ratio records.",
            ),
            "pattern_consequence": "Clear movement across groups supports follow-up; overlapping ranges should lower confidence.",
            "next_investigation_reason": "Check whether wind-speed bands tell the same story.",
            "misunderstanding_guard": "Do not treat small bar differences as meaningful when ranges overlap.",
            "confidence_anchor": "You now know whether gustiness is strong enough to investigate further.",
            "uncertainty_note": "If ranges overlap widely, the evidence is weak for a strong gustiness claim.",
            "guided_reading": "Look for steady separation and range overlap together. One without the other is limited support.",
            "consequence_map": (
                ConsequenceMapEntry(
                    data_state="Overlapping gust-ratio groups",
                    consequence="Gustiness is not a reliable separator in the selected view.",
                    affected_group="People using wind context for AQI interpretation",
                    confidence="low",
                    is_normal_state=True,
                ),
                ConsequenceMapEntry(
                    data_state="Steady PM2.5 movement across gust groups",
                    consequence="Gust behavior deserves follow-up as part of dispersion context.",
                    affected_group="Air-quality analysts and outdoor groups",
                    confidence="medium",
                ),
            ),
        },
        "A-12": {
            "dominant_takeaway": "Day-night temperature spread matters when pollution changes clearly across spread groups.",
            "situation_verdict": "Temperature stability may be part of the pollution story if PM2.5 differs strongly by spread band.",
            "significance": "Clear spread-band differences can point toward atmospheric stability context.",
            "focus_point": "Look for large differences between spread bands, not tiny shifts.",
            "human_impact": HumanImpact(
                who_is_affected="People outdoors during conditions that may trap or disperse pollution differently.",
                what_they_experience="Some day-night temperature patterns may coincide with more polluted outdoor air.",
                duration_or_scope="This applies to grouped temperature-spread records.",
            ),
            "pattern_consequence": "Large differences justify atmospheric follow-up; small differences should not drive interpretation.",
            "next_investigation_reason": "Check whether the same periods align with pressure or seasonal patterns.",
            "misunderstanding_guard": "Do not treat temperature spread as a direct pollution cause.",
            "confidence_anchor": "You now know whether temperature spread is worth deeper attention.",
            "uncertainty_note": "If band differences are small or groups are sparse, there may be insufficient evidence for a clear claim.",
            "guided_reading": "Compare broad separation across bands. Ignore tiny differences unless they repeat elsewhere.",
            "consequence_map": (
                ConsequenceMapEntry(
                    data_state="Similar PM2.5 across spread bands",
                    consequence="Temperature spread is not a strong separator in the selected scope.",
                    affected_group="People interpreting atmospheric stability",
                    confidence="medium",
                    is_normal_state=True,
                ),
                ConsequenceMapEntry(
                    data_state="Large PM2.5 difference by spread band",
                    consequence="Atmospheric stability deserves follow-up.",
                    affected_group="Sensitive residents and AQI planners",
                    confidence="medium",
                ),
            ),
        },
        "A-14": {
            "dominant_takeaway": "Season and pressure matter together when one combination carries clearly higher PM2.5.",
            "situation_verdict": "Pollution burden may concentrate under specific season-pressure conditions.",
            "significance": "Combined conditions help narrow when exposure risk is more likely, without claiming a single cause.",
            "focus_point": "Look for season-pressure combinations that stand apart from neighboring cells.",
            "human_impact": HumanImpact(
                who_is_affected="People outdoors during seasons and pressure conditions linked with higher PM2.5.",
                what_they_experience="Certain periods may bring more repeated poor-air conditions.",
                duration_or_scope="This applies to grouped season and pressure records.",
            ),
            "pattern_consequence": "A clear combined hotspot supports targeted seasonal and atmospheric follow-up.",
            "next_investigation_reason": "Check whether the same pressure context appears in the pressure-band comparison.",
            "misunderstanding_guard": "Do not treat a dark cell as proof that pressure caused the pollution.",
            "confidence_anchor": "You now know whether combined weather timing is worth investigating.",
            "uncertainty_note": "If a season-pressure group has few records, there may be insufficient evidence to rank it confidently.",
            "guided_reading": "Look for standout combinations, then confirm whether the same pattern appears in related pressure views.",
            "consequence_map": (
                ConsequenceMapEntry(
                    data_state="No clear combined hotspot",
                    consequence="Season-pressure combinations do not strongly explain the selected pollution pattern.",
                    affected_group="People using weather context for AQI interpretation",
                    confidence="medium",
                    is_normal_state=True,
                ),
                ConsequenceMapEntry(
                    data_state="One combination clearly elevated",
                    consequence="Seasonal atmospheric follow-up becomes more useful.",
                    affected_group="Public-health planners and sensitive residents",
                    confidence="medium",
                ),
            ),
        },
    }
)


_MIGRATED_SITUATION_CONTENT.update(
    {
        "T-13": {
            "dominant_takeaway": (
                "Area stress is easier to understand when you find the strongest stress driver first."
            ),
            "situation_verdict": (
                "The main situation is whether an area has one dominant stress factor or broad pressure across several factors."
            ),
            "significance": (
                "That matters because a narrow stress pattern needs a different follow-up than an area stressed in many ways at once."
            ),
            "focus_point": (
                "Start with the strongest stress factor for the focused area, then decide whether the rest of the profile supports it."
            ),
            "human_impact": HumanImpact(
                who_is_affected="People traveling through areas where several traffic pressures overlap.",
                what_they_experience="Movement may feel harder to manage when congestion, speed, capacity, or exposure pressure stack together.",
                duration_or_scope="This applies to the selected area stress view and current dashboard filters.",
            ),
            "pattern_consequence": (
                "A single strong driver points to targeted follow-up; broad stress points to wider area review."
            ),
            "next_investigation_reason": (
                "Check whether the strongest stress factor also appears in road-level congestion detail."
            ),
            "misunderstanding_guard": (
                "Do not treat every small profile difference as equally important; the strongest driver matters first."
            ),
            "confidence_anchor": (
                "You now know whether to read the area as narrowly stressed or broadly pressured."
            ),
            "uncertainty_note": (
                "If stress factors are close together or the selected area has sparse records, there may be insufficient evidence to rank one driver confidently."
            ),
            "guided_reading": (
                "Use the active view as a focus tool. In heatmap mode, start with the darkest stress factor. "
                "In radar mode, start with the largest outward spike. Ignore smaller differences until the main driver is clear."
            ),
            "analyst_detail": (
                "Stress factors use normalized comparison scores, so they support relative diagnosis rather than raw-unit measurement.",
                "Heatmap mode is better for finding the dominant stress dimension across many areas.",
                "Radar mode is better for comparing the shape of a few area profiles after a focus area is clear.",
                "Small differences between stress factors should be treated cautiously unless they repeat in related road-level views.",
            ),
            "visualization_anatomy": (
                _component(
                    "Heatmap intensity",
                    "Darker cells mark stronger stress for an area-factor pairing.",
                    "It helps users find the first stress driver before comparing everything else.",
                    "Start with the darkest cell in the focused area.",
                ),
                _component(
                    "Radar shape",
                    "Outward spikes mark stronger stress factors for selected areas.",
                    "It helps compare profile shape after the main driver is known.",
                    "Notice the largest spike before reading the full shape.",
                ),
                _component(
                    "Focused area",
                    "The selected or emphasized area anchors interpretation.",
                    "It prevents users from trying to decode all areas at once.",
                    "Read the focused area first and use others as comparison context.",
                ),
            ),
            "consequence_map": (
                ConsequenceMapEntry(
                    data_state="One stress factor dominates",
                    consequence="Follow-up can start with that specific pressure point.",
                    affected_group="People moving through the focused area",
                    confidence="medium",
                    is_normal_state=True,
                ),
                ConsequenceMapEntry(
                    data_state="Several stress factors remain high together",
                    consequence="The area may need broader operational review rather than one narrow fix.",
                    affected_group="Travelers, traffic operations teams, and nearby road users",
                    confidence="medium",
                ),
            ),
        },
    }
)


_MIGRATED_SITUATION_CONTENT.update(
    {
        "A-13": {
            "dominant_takeaway": (
                "Atmospheric regimes are useful when they clarify whether pollution is lingering, clearing, or shifting."
            ),
            "situation_verdict": (
                "The main situation is whether the selected records look like trapped-air pollution, dispersive relief, or mixed conditions."
            ),
            "significance": (
                "That matters because trapped conditions can extend exposure, while dispersive conditions may help pollution clear."
            ),
            "focus_point": (
                "Start with the condition group where high PM2.5 appears with low visibility, then compare it with cleaner groups."
            ),
            "human_impact": HumanImpact(
                who_is_affected="People outdoors during condition groups linked with elevated PM2.5 or poor visibility.",
                what_they_experience="Air may feel hazier or slower to clear when pollution appears under trapped-air conditions.",
                duration_or_scope="This applies to the selected regime records and current AQI filters.",
            ),
            "pattern_consequence": (
                "A trapped-air pattern points to repeated exposure risk; a dispersive pattern suggests conditions may be helping recovery."
            ),
            "next_investigation_reason": (
                "Check whether these conditions persist across multiple days in the pollution persistence view."
            ),
            "misunderstanding_guard": (
                "Do not treat regime labels as exact predictions or proof that weather caused the pollution."
            ),
            "confidence_anchor": (
                "You now know whether the condition pattern is more about trapping, clearing, or mixed behavior."
            ),
            "uncertainty_note": (
                "If regime groups overlap or have sparse records, there may be insufficient evidence to name one dominant condition confidently."
            ),
            "guided_reading": (
                "Read regimes as plain condition groups. Start with high PM2.5 and low visibility, then ask whether that group repeats enough "
                "to suggest trapped air rather than a temporary spike."
            ),
            "related_investigations": ("A-05", "A-06", "A-14"),
            "analyst_detail": (
                "Regime labels are rule-based condition groups, not predictive model outputs.",
                "Low visibility with high PM2.5 is the clearest practical warning pattern in this view.",
                "Dispersive relief should be read as possible clearing context, not guaranteed clean air.",
                "Overlapping regime clusters lower confidence and should be checked against persistence and pressure views.",
            ),
            "visualization_anatomy": (
                _component(
                    "Regime groups",
                    "Named condition groups such as trapped, dispersive, or pressure-related states.",
                    "They translate weather context into a practical comparison.",
                    "Start with the group that combines higher PM2.5 and lower visibility.",
                ),
                _component(
                    "PM2.5 position",
                    "Higher points mean more fine-particle pollution.",
                    "It connects each condition group to exposure burden.",
                    "Notice whether high values repeat within one condition group.",
                ),
                _component(
                    "Visibility position",
                    "Lower visibility can point to hazier conditions.",
                    "It helps users recognize when pollution may be lingering in harder-to-clear air.",
                    "Low visibility with high PM2.5 deserves first attention.",
                ),
                _component(
                    "Highlighted regime",
                    "A selected condition group can be emphasized while others fade back.",
                    "It prevents users from decoding all groups at once.",
                    "Read the highlighted group first and use others as comparison context.",
                ),
            ),
            "consequence_map": (
                ConsequenceMapEntry(
                    data_state="Cleaner or dispersive condition group",
                    consequence="Atmospheric context may be helping pollution clear in the selected scope.",
                    affected_group="People outdoors during the selected AQI period",
                    confidence="medium",
                    is_normal_state=True,
                ),
                ConsequenceMapEntry(
                    data_state="High PM2.5 with low visibility in one regime",
                    consequence="Trapped-air exposure risk deserves follow-up in persistence and visibility views.",
                    affected_group="Sensitive residents, outdoor workers, and public-health planners",
                    confidence="medium",
                ),
            ),
        },
    }
)


_MIGRATED_SITUATION_CONTENT.update(
    {
        "A-15": {
            "dominant_takeaway": (
                "The pairplot is useful only after you choose one PM2.5 relationship to inspect first."
            ),
            "situation_verdict": (
                "The main situation is whether one weather relationship with PM2.5 looks clear enough to deserve follow-up."
            ),
            "significance": (
                "That matters because a clear relationship can guide the next question, while a scattered pattern should not drive interpretation."
            ),
            "focus_point": (
                "Start with PM2.5 and visibility, then ask whether the pattern is directional, clustered, or mostly scattered."
            ),
            "human_impact": HumanImpact(
                who_is_affected="People using weather context to understand when PM2.5 exposure may become worse or easier to explain.",
                what_they_experience="A clear relationship can point to conditions linked with hazier or more polluted outdoor air.",
                duration_or_scope="This applies to the selected weather and PM2.5 records, not every weather condition in the city.",
            ),
            "pattern_consequence": (
                "A tight directional pattern deserves follow-up; a noisy pattern should be treated as weak evidence."
            ),
            "next_investigation_reason": (
                "Check whether the same PM2.5 relationship appears in the pressure and visibility density view."
            ),
            "misunderstanding_guard": (
                "Do not treat every matrix cell as important, and do not treat a relationship as proof of cause."
            ),
            "confidence_anchor": (
                "You now know whether there is one relationship worth following or whether the matrix is mostly exploratory."
            ),
            "uncertainty_note": (
                "If points are scattered, sampled, or sparse, there may be insufficient evidence to call the relationship meaningful."
            ),
            "guided_reading": (
                "Read one PM2.5 relationship first. A clear direction or tight cluster matters more than a noisy cloud. "
                "Use the rest of the matrix only after the first relationship is understood."
            ),
            "related_investigations": ("A-06", "A-09", "A-13"),
            "analyst_detail": (
                "Pairplot cells are exploratory relationship checks, not final explanations.",
                "PM2.5 with visibility, pressure, temperature, or wind should be prioritized before weather-weather pairs.",
                "Diagonal cells show one variable by itself and should not interrupt the first relationship reading.",
                "Correlation or clustered points describe association only; they do not prove cause.",
                "Sampling can keep the matrix readable but may hide rare outliers.",
            ),
            "visualization_anatomy": (
                _component(
                    "PM2.5 relationship cell",
                    "A comparison between PM2.5 and one weather variable.",
                    "It is the first place to look because pollution meaning is the main question.",
                    "Start with PM2.5 versus visibility or pressure.",
                ),
                _component(
                    "Directional pattern",
                    "Points that generally move upward, downward, or cluster together.",
                    "It helps users judge whether the relationship is worth follow-up.",
                    "A tight direction is stronger than scattered points.",
                ),
                _component(
                    "Scattered pattern",
                    "Points spread without a clear direction.",
                    "It warns users not to overread weak relationships.",
                    "Treat scattered clouds as low-confidence evidence.",
                ),
                _component(
                    "Diagonal distribution",
                    "A single-variable summary inside the matrix.",
                    "It is useful later, but it should not distract from the first PM2.5 relationship.",
                    "Ignore diagonal cells at the beginning.",
                ),
            ),
            "consequence_map": (
                ConsequenceMapEntry(
                    data_state="PM2.5 relationship is scattered",
                    consequence="The visible relationship is too weak to guide practical interpretation by itself.",
                    affected_group="People using weather context for AQI interpretation",
                    confidence="low",
                    is_normal_state=True,
                ),
                ConsequenceMapEntry(
                    data_state="PM2.5 relationship is directional or tightly clustered",
                    consequence="That weather condition deserves follow-up in a focused AQI view.",
                    affected_group="Sensitive residents, outdoor workers, and AQI analysts",
                    confidence="medium",
                ),
            ),
        },
    }
)


def enrich_entries_with_chart_interpretation(
    entries: Iterable[ExplainabilityEntry],
) -> tuple[ExplainabilityEntry, ...]:
    """Return entries enriched with structured interpretation metadata when available."""

    enriched: list[ExplainabilityEntry] = []
    for entry in entries:
        payload = CHART_INTERPRETATION_METADATA.get(entry.surface_id)
        if payload is None:
            enriched.append(entry)
            continue
        enriched.append(entry.with_interpretation(**_migrated_situation_payload(entry, payload)))
    return tuple(enriched)


__all__ = ["CHART_INTERPRETATION_METADATA", "enrich_entries_with_chart_interpretation"]
