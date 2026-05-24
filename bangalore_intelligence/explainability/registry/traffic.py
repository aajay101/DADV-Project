"""Traffic chart explainability metadata."""

from __future__ import annotations

from bangalore_intelligence.explainability.models import ExplainabilityEntry

TRAFFIC_EXPLAINABILITY: tuple[ExplainabilityEntry, ...] = (
    ExplainabilityEntry(
        surface_id="T-01",
        dashboard="traffic",
        surface_type="chart",
        title="Network Congestion And Area Ranking",
        complexity_level="basic",
        priority="high",
        what_this_shows=(
            "A command-level summary of current traffic pressure, combining the system congestion index with "
            "area-level severity ranking."
        ),
        why_this_visualization=(
            "A scorecard plus ranked bars gives users a fast read of overall network pressure and where that "
            "pressure is concentrated."
        ),
        when_to_use="Use this first for a broad traffic diagnosis before moving into time, road, or threshold analysis.",
        decision_relevance=(
            "High system pressure or concentrated area stress helps identify where operational attention should start."
        ),
        misinterpretation_warning=(
            "Area ranking shows current filtered-scope severity; it does not explain the cause of congestion by itself."
        ),
        related_visuals=("T-03", "T-05", "T-13"),
        limitations=(
            "Rankings depend on the active global filter scope.",
            "A high area bar should be followed with road-level or temporal analysis.",
        ),
    ),
    ExplainabilityEntry(
        surface_id="T-02",
        dashboard="traffic",
        surface_type="chart",
        title="Parallel Coordinates Matrix",
        complexity_level="advanced",
        priority="high",
        what_this_shows=(
            "Area-level traffic performance across multiple normalized dimensions, including congestion, speed, "
            "capacity, incidents, environmental burden, and mobility context."
        ),
        why_this_visualization=(
            "Parallel coordinate style views are useful when the analytical question is about multi-factor profile "
            "shape rather than one metric at a time."
        ),
        when_to_use=(
            "Use this visual when comparing broad area performance fingerprints or looking for areas that remain "
            "high-risk across several dimensions."
        ),
        decision_relevance=(
            "Areas that stay elevated across many axes may require coordinated intervention rather than a single "
            "road-level fix."
        ),
        misinterpretation_warning=(
            "High values across several axes identify a multi-factor stress pattern; they do not prove which factor "
            "caused congestion."
        ),
        related_visuals=("T-13", "T-05", "T-07"),
        limitations=(
            "Normalized axes support comparison but can hide the original unit scale.",
            "Dense profiles can become harder to read without focused selection or fullscreen inspection.",
        ),
    ),
    ExplainabilityEntry(
        surface_id="T-03",
        dashboard="traffic",
        surface_type="chart",
        title="Monthly Congestion Trend By Area",
        complexity_level="basic",
        priority="high",
        what_this_shows="Monthly mean congestion patterns across monitored traffic areas.",
        why_this_visualization=(
            "A multi-series line chart is suited to comparing temporal movement, slope, and divergence between areas."
        ),
        when_to_use="Use this chart to see whether congestion is stable, worsening, seasonal, or diverging across areas.",
        decision_relevance=(
            "Persistent upward movement can indicate growing infrastructure or operational strain that needs "
            "time-aware planning."
        ),
        misinterpretation_warning="A rising line identifies temporal movement, not the cause of the change.",
        related_visuals=("T-01", "T-15", "T-05"),
        limitations=(
            "Monthly averages can hide short spikes or road-level extremes.",
            "Area lines should be interpreted inside the active filter scope.",
        ),
    ),
    ExplainabilityEntry(
        surface_id="T-04",
        dashboard="traffic",
        surface_type="chart",
        title="Weekly Violin Distribution",
        complexity_level="intermediate",
        priority="medium",
        what_this_shows="Day-of-week congestion distribution shape for the current traffic scope.",
        why_this_visualization=(
            "Violin and box-style distributions reveal spread, median behavior, and heavy tails better than an "
            "average alone."
        ),
        when_to_use="Use this chart to compare routine weekday pressure against volatile or unusually severe days.",
        decision_relevance=(
            "High spread or long upper tails can indicate scheduling risk even when the weekly average looks moderate."
        ),
        misinterpretation_warning=(
            "A wide distribution means variability, not necessarily worse average congestion."
        ),
        related_visuals=("T-03", "T-11", "T-12"),
        limitations=(
            "Low record counts may trigger simpler distribution fallbacks.",
            "Weekday patterns depend on the active date and filter scope.",
        ),
    ),
    ExplainabilityEntry(
        surface_id="T-05",
        dashboard="traffic",
        surface_type="chart",
        title="Road Management Priority Quadrant",
        complexity_level="intermediate",
        priority="high",
        what_this_shows="Roads positioned by congestion level and capacity pressure.",
        why_this_visualization="A quadrant scatter exposes two operational risk dimensions at once and makes priority zones explicit.",
        when_to_use="Use this chart to identify roads that need operational attention or deeper corridor review.",
        decision_relevance=(
            "Roads with high congestion and high capacity pressure may require corridor-level intervention, signal "
            "review, or capacity management."
        ),
        misinterpretation_warning="Quadrant position is descriptive. It does not prove the root cause of road stress.",
        related_visuals=("T-07", "T-09", "T-11"),
        limitations=(
            "Sparse road records can make quadrant placement less stable.",
            "Capacity and congestion are summarized from the active filtered scope.",
        ),
    ),
    ExplainabilityEntry(
        surface_id="T-06",
        dashboard="traffic",
        surface_type="chart",
        title="Environmental Burden Treemap",
        complexity_level="intermediate",
        priority="medium",
        what_this_shows="Hierarchical contribution of areas and roads to traffic-related environmental burden.",
        why_this_visualization=(
            "A treemap shows nested share-of-total contribution, making dominant burden sources visible quickly."
        ),
        when_to_use="Use this chart to find which area-road combinations contribute most to environmental impact.",
        decision_relevance=(
            "Large burden blocks can guide where mobility interventions may also reduce environmental cost."
        ),
        misinterpretation_warning=(
            "A large treemap block reflects contribution in the current scope, not necessarily the only cause of impact."
        ),
        related_visuals=("T-05", "T-07", "T-14"),
        limitations=(
            "Small contributors can be visually compressed.",
            "The environmental score is a derived indicator and should be interpreted with its source metrics.",
        ),
    ),
    ExplainabilityEntry(
        surface_id="T-07",
        dashboard="traffic",
        surface_type="chart",
        title="Pedestrian-Adjusted Road Pressure",
        complexity_level="intermediate",
        priority="medium",
        what_this_shows="Road congestion deviation from the filtered-scope baseline with pedestrian exposure context.",
        why_this_visualization=(
            "Deviation bars make above-baseline and below-baseline road pressure easy to compare."
        ),
        when_to_use="Use this chart to identify road pressure outliers after reviewing area or quadrant stress.",
        decision_relevance=(
            "Roads above baseline with high vulnerable-user exposure may deserve more cautious operational review."
        ),
        misinterpretation_warning=(
            "A positive bar shows relative pressure, not absolute failure or causal pedestrian impact."
        ),
        related_visuals=("T-05", "T-06", "T-11"),
        limitations=(
            "Baseline is computed from the current filter scope.",
            "Exposure context changes interpretation but does not replace safety analysis.",
        ),
    ),
    ExplainabilityEntry(
        surface_id="T-08",
        dashboard="traffic",
        surface_type="chart",
        title="Incident Impact On Congestion",
        complexity_level="basic",
        priority="medium",
        what_this_shows="Mean congestion across incident-count bands.",
        why_this_visualization=(
            "A step line emphasizes whether congestion changes sharply as incident load increases."
        ),
        when_to_use="Use this chart to check whether incidents coincide with visible congestion cliffs.",
        decision_relevance=(
            "A sharp step can support incident-response planning and targeted operational monitoring."
        ),
        misinterpretation_warning=(
            "Incident bands show association, not proof that incidents alone caused congestion."
        ),
        related_visuals=("T-09", "T-12", "T-03"),
        limitations=(
            "Incident counts are grouped into bands, which can hide within-band variation.",
            "Low-count bands can be less stable.",
        ),
    ),
    ExplainabilityEntry(
        surface_id="T-09",
        dashboard="traffic",
        surface_type="chart",
        title="Speed Collapse Threshold",
        complexity_level="intermediate",
        priority="high",
        what_this_shows="Record-level relationship between congestion and speed with operational threshold lines.",
        why_this_visualization="A threshold scatter makes high-congestion and low-speed combinations visible as risk zones.",
        when_to_use="Use this chart to inspect where congestion crosses into speed-collapse conditions.",
        decision_relevance=(
            "Repeated points in the critical zone suggest mobility breakdown and can support targeted operations review."
        ),
        misinterpretation_warning="Crossing a threshold identifies a risk condition, not a complete causal diagnosis.",
        related_visuals=("T-05", "T-08", "T-10"),
        limitations=(
            "Scatter density can obscure rare but important points in crowded scopes.",
            "Thresholds provide operational reference lines and should be interpreted with local context.",
        ),
    ),
    ExplainabilityEntry(
        surface_id="T-10",
        dashboard="traffic",
        surface_type="chart",
        title="Public Transport Usage Comparison",
        complexity_level="basic",
        priority="medium",
        what_this_shows="Congestion, speed, and incidents compared across public-transport usage quartiles.",
        why_this_visualization=(
            "Grouped bars and a line compare several operational metrics across usage bands without implying a time sequence."
        ),
        when_to_use="Use this chart to test whether mobility mix aligns with road pressure differences.",
        decision_relevance=(
            "Differences across usage quartiles can guide deeper transport planning questions."
        ),
        misinterpretation_warning=(
            "Higher public transport usage can reflect demand patterns; it does not automatically cause lower congestion."
        ),
        related_visuals=("T-09", "T-14", "T-05"),
        limitations=(
            "Quartiles simplify a continuous usage measure.",
            "The chart is descriptive and should not be read as a modal-shift causal model.",
        ),
    ),
    ExplainabilityEntry(
        surface_id="T-11",
        dashboard="traffic",
        surface_type="chart",
        title="Road Congestion Distribution Profiles",
        complexity_level="intermediate",
        priority="medium",
        what_this_shows="Small-multiple congestion distributions for individual roads, sorted by median congestion.",
        why_this_visualization=(
            "Small histograms let users compare distribution shape and typical pressure across many roads."
        ),
        when_to_use="Use this chart after identifying priority roads to see whether stress is chronic or occasional.",
        decision_relevance=(
            "High medians and right-skewed distributions point to roads with repeated congestion burden."
        ),
        misinterpretation_warning=(
            "A road with a high tail may have occasional severe events even if its median is moderate."
        ),
        related_visuals=("T-05", "T-07", "T-04"),
        limitations=(
            "Only a subset of roads may be shown in compact layouts.",
            "Distribution shape depends on available records in the filtered scope.",
        ),
    ),
    ExplainabilityEntry(
        surface_id="T-12",
        dashboard="traffic",
        surface_type="chart",
        title="Weather x Roadwork Heatmap",
        complexity_level="basic",
        priority="medium",
        what_this_shows="Mean congestion for combinations of weather condition and roadwork activity.",
        why_this_visualization=(
            "A heatmap efficiently compares two operational categories against one continuous risk measure."
        ),
        when_to_use="Use this chart to inspect whether weather-roadwork combinations align with higher congestion.",
        decision_relevance=(
            "High-risk cells can inform scheduling, staffing, or mitigation planning around roadwork and weather."
        ),
        misinterpretation_warning=(
            "Darker cells show association in the current data; they do not prove weather or roadwork caused congestion alone."
        ),
        related_visuals=("T-08", "T-04", "T-09"),
        limitations=(
            "Sparse category combinations can be unstable.",
            "Mean values can hide within-cell variation.",
        ),
    ),
    ExplainabilityEntry(
        surface_id="T-13",
        dashboard="traffic",
        surface_type="chart",
        title="Area Stress Profile",
        complexity_level="advanced",
        priority="high",
        what_this_shows="Focused area stress across multiple traffic dimensions as a heatmap or radar comparison.",
        why_this_visualization=(
            "Heatmaps support compact dimension comparison, while radar mode supports focused multi-axis profile "
            "comparison across selected areas."
        ),
        when_to_use="Use this chart to compare whether an area's stress is narrow, broad, or imbalanced.",
        decision_relevance=(
            "Broad stress profiles may indicate systemic area pressure, while narrow spikes may indicate targeted "
            "operational issues."
        ),
        misinterpretation_warning="Radar area and shape are descriptive comparisons, not predictive scores or causal rankings.",
        related_visuals=("T-02", "T-15", "T-05"),
        limitations=(
            "Radar comparisons are best for a small number of areas.",
            "Heatmap and radar views summarize dimensions and should be read with their active filtered scope.",
        ),
    ),
    ExplainabilityEntry(
        surface_id="T-14",
        dashboard="traffic",
        surface_type="chart",
        title="Traffic Volume And Congestion Density",
        complexity_level="intermediate",
        priority="medium",
        what_this_shows="Density of records by traffic volume and congestion level.",
        why_this_visualization=(
            "A 2D density heatmap reduces overplotting and reveals where high-volume and high-congestion records cluster."
        ),
        when_to_use="Use this chart to inspect sustained corridor load rather than individual road rankings.",
        decision_relevance=(
            "Dense high-volume, high-congestion regions can identify corridors needing capacity or demand management review."
        ),
        misinterpretation_warning=(
            "Density clusters show where observations accumulate; they do not identify one specific road by themselves."
        ),
        related_visuals=("T-10", "T-06", "T-09"),
        limitations=(
            "Density aggregation can hide individual outliers.",
            "Interpret with road or area charts when location-specific action is needed.",
        ),
    ),
    ExplainabilityEntry(
        surface_id="T-15",
        dashboard="traffic",
        surface_type="chart",
        title="Area-Month Congestion Heatmap",
        complexity_level="basic",
        priority="medium",
        what_this_shows="Congestion pressure by area and month.",
        why_this_visualization=(
            "A matrix heatmap is well suited for comparing time and area at the same time."
        ),
        when_to_use="Use this chart to find when and where congestion pressure concentrates.",
        decision_relevance=(
            "Recurring hot area-month cells can support seasonal or location-specific planning."
        ),
        misinterpretation_warning=(
            "A dark cell identifies a hotspot in the filtered data, not the cause of that hotspot."
        ),
        related_visuals=("T-03", "T-13", "T-01"),
        limitations=(
            "Monthly aggregation can hide day-level spikes.",
            "Areas with fewer records may be less stable.",
        ),
    ),
)
