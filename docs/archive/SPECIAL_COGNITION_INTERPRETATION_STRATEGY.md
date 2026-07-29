# SUAQIS Special Cognition Interpretation Strategy

Status: planning-only cognitive strategy for the remaining multidimensional explainability migrations. This document does not implement metadata, UI, registry changes, modal changes, runtime AI, chart behavior, or analytical logic.

Scope:

- T-02 - Parallel Coordinates Matrix
- T-13 - Area Stress Profile
- A-13 - Rule-Based Atmospheric Regimes
- A-15 - Weather Variable Pairplot

These charts remain intentionally legacy until a dedicated special-cognition migration is designed and validated.

## 1. Why These Charts Need A Different Strategy

The stable-pattern migration model works for charts with one main reading path: rankings, trends, thresholds, distributions, heatmaps, and simple comparisons. The remaining charts are different. They ask users to reason across several variables at the same time.

Ordinary users struggle because they try to read the whole visual at once. They see many lines, axes, cells, colors, or clusters and do not know which relationship matters first. The goal of special-cognition interpretation is to reduce that burden.

The explainability layer should not explain every dimension equally. It should guide attention toward the few relationships that are most useful for understanding the situation.

## 2. Shared Special-Cognition Principles

Every special-cognition chart must still produce one dominant takeaway. The user should leave with one clear mental model, not a collection of partial observations.

Simple Mode should not teach the full chart. It should answer:

- What is the main situation?
- Which part deserves attention first?
- What should I ignore at the beginning?
- What practical meaning can I safely take away?
- What should I not overinterpret?

Analytical Mode may expose richer relationships, but it must still prioritize. It should not become a relationship dump.

Operational Mode should translate complexity into consequence: where stress concentrates, who is affected, what conditions deserve follow-up, and what decision context the chart supports.

## 3. Governance Rules For Multidimensional Explainability

Maximum visible relationships:

- Simple Mode: 1 primary relationship or pattern.
- Operational Mode: 1 primary relationship plus 1 operational consequence.
- Analytical Mode: up to 3 prioritized relationships, never all relationships.

Maximum visible dimensions:

- Simple Mode: 2 to 3 dimensions.
- Operational Mode: 3 to 4 dimensions if tied to consequence.
- Analytical Mode: more dimensions allowed only through progressive reveal.

Relationship priority order:

1. Strongest practical consequence.
2. Clearest repeated pattern.
3. Most unusual or risky combination.
4. Most stable relationship across the filtered data.
5. Secondary analytical relationships.

Progressive reveal requirements:

- Start with the dominant takeaway.
- Reveal the first focus area.
- Explain why other dimensions are background at first.
- Offer optional deeper relationship paths.
- Keep glossary terms local to the section where they are needed.

Anti-overload rules:

- Do not explain every axis, variable, trace, or pair at the same level.
- Do not display a large glossary block as the main support mechanism.
- Do not ask users to compare more than one complex relationship at a time.
- Do not use technical terms before the user knows why the chart matters.
- Do not make Simple Mode depend on chart literacy.

What must never happen:

- Relationship essays.
- Long lists of variable pair interpretations.
- Glossary walls.
- Simultaneous narration of all dimensions.
- Forcing users to decode the whole visual before understanding the situation.
- Treating weak visual complexity as if it were meaningful insight.

## 4. T-02 - Parallel Coordinates Matrix

### Primary Cognitive Failure Mode

Users struggle because every area line crosses many axes. They do not know whether to follow one line, compare line shapes, inspect one metric, or rank areas. The visual encourages full-profile comparison, but ordinary users cannot hold eight dimensions in memory at once.

The main failure is multi-axis overload. Users may also mistake normalized values for raw values.

### One Understanding Users Should Leave With

The chart should help users understand whether an area is stressed in one isolated way or across many traffic dimensions.

Dominant takeaway strategy:

"Some areas have broad stress across several traffic conditions, while others stand out for only one or two specific issues."

### Attention Orchestration Strategy

Simple Mode should use focus-first sequencing:

1. Start with one selected or most prominent area.
2. Ask whether its line stays high across several axes.
3. Treat the rest of the lines as background context.
4. Explain that broad high profiles deserve more attention than one isolated spike.

Users should be told to ignore line crossings at first. Crossings are advanced comparison details, not the first reading task.

### Relationship Prioritization

Most important relationships:

- Congestion with speed: high congestion plus low speed is operationally meaningful.
- Congestion with capacity: high congestion plus high capacity use suggests limited headroom.
- Congestion with incidents: high congestion with incident load suggests disruption context.
- Environmental impact and exposure: traffic pressure may carry wider social or environmental cost.

Do not prioritize all axes. Begin with congestion, speed, and capacity. Add other dimensions only when the user asks for deeper interpretation.

### Visual Overload Reduction Strategy

The explainability layer should provide:

- "Start here" guidance for one area profile.
- A short explanation of high-across-many-axes versus one-axis spike.
- A warning that normalized values are comparison values, not original units.
- Optional analyst expansion for each metric family.

If a focus area exists, use it as the interpretation anchor. If no focus exists, guide users to the broadest high-stress area or the most unusual profile.

### Beginner-Safe Interpretation Path

Beginner flow:

1. Look at one area line only.
2. Ask whether it is high on several important axes.
3. If it is high on many axes, treat the area as broadly stressed.
4. If it spikes on one axis only, treat it as a specific issue.
5. Do not try to explain every crossing line.

### Analyst Path

Analysts can access:

- Full axis-by-axis profile reading.
- Normalization caveats.
- Tradeoffs between dimensions.
- Comparison between selected area and background areas.
- Record-level fullscreen parallel coordinates context.

This should remain advanced-only and should not leak into Simple Mode.

### Special Glossary Strategy

Inline terms:

- Normalized value: "a comparison score, not the original unit."
- Profile: "the shape an area makes across several measures."
- Broad stress: "several conditions are concerning at the same time."

Avoid a large glossary for every axis. Explain only the axes currently used in the guided path.

### Redesign Assessment

Guided interpretation may be sufficient for analysts and semi-technical users. For beginners, explainability alone may not fully solve the burden unless the chart supports a stronger focus state.

Recommendation: partial redesign later. Add a focus-first summary or simplified profile strip before exposing the full parallel coordinates view.

### Special Needs

- Progressive focus.
- Selected area emphasis.
- Dimension grouping.
- "Ignore crossings first" guidance.
- Optional axis family expansion.

## 5. T-13 - Area Stress Profile

### Primary Cognitive Failure Mode

Users struggle because this chart can appear as a heatmap or radar comparison. It combines several stress factors and may switch interpretation mode depending on controls. Users may not know whether they are comparing areas, stress dimensions, or the shape of a profile.

The main failure is mixed-mode interpretation. The chart changes visual language, but the user's mental model may not change with it.

### One Understanding Users Should Leave With

The chart should help users understand what kind of stress pattern an area has, not just whether it is "bad."

Dominant takeaway strategy:

"An area can be stressed in different ways. The goal is to identify which stress dimensions are driving the concern."

### Attention Orchestration Strategy

Use mode-specific attention sequencing:

Heatmap mode:

1. Start with the darkest stress dimension for the focused area.
2. Compare that dimension with nearby areas or the selected comparison group.
3. Treat lighter cells as lower-priority context.

Radar mode:

1. Start with the largest outward spikes.
2. Compare shape, not exact area.
3. Use the radar as a stress fingerprint, not a precise measurement tool.

The explainability system should name which visual mode is active and provide only the matching reading path.

### Relationship Prioritization

Most important relationships:

- Congestion with speed.
- Capacity with congestion.
- Exposure with congestion.
- Environmental burden with traffic pressure.

Do not ask users to read all stress dimensions equally. Prioritize the largest stress driver for the active focus.

### Visual Overload Reduction Strategy

The explanation should:

- State the active mode first.
- Give one first-look instruction.
- Highlight the strongest stress dimension.
- Collapse secondary dimensions into optional detail.
- Avoid explaining both heatmap and radar mechanics at the same time.

### Beginner-Safe Interpretation Path

Beginner flow:

1. Identify the selected area.
2. Find the strongest stress factor.
3. Ask whether the stress is narrow or broad.
4. Treat broad stress as more serious than one isolated factor.
5. Do not compare every dimension immediately.

### Analyst Path

Analysts can access:

- Full dimension definitions.
- Area-to-area comparison.
- Radar shape interpretation.
- Heatmap intensity interpretation.
- Sensitivity to chart-local controls.

This belongs in Analytical Mode and optional visualization learning.

### Special Glossary Strategy

Inline terms:

- Stress factor: "one reason an area may be under pressure."
- Profile: "the area's pattern across several stress factors."
- Radar shape: "a quick shape comparison, not a precise ranking."

Avoid separate glossary entries for every stress metric in Simple Mode.

### Redesign Assessment

Guided interpretation is probably sufficient if the active mode is explained clearly. The bigger risk is mode confusion, not chart impossibility.

Recommendation: no immediate redesign required, but future UI should label heatmap mode and radar mode more explicitly.

### Special Needs

- Active-mode-aware explanation.
- One strongest dimension first.
- Separate heatmap and radar reading paths.
- Optional comparison detail.

## 6. A-13 - Rule-Based Atmospheric Regimes

### Primary Cognitive Failure Mode

Users struggle because atmospheric regimes are abstract. Terms like baseline, low-visibility, dispersive, and pressure regime sound like model outputs. Users may assume the regimes are predictions or scientific proof of causes.

The main failure is abstract state interpretation. Users do not know what a regime means in lived air-quality terms.

### One Understanding Users Should Leave With

The chart should help users understand which weather-condition groups tend to appear with higher or lower PM2.5.

Dominant takeaway strategy:

"Some weather-condition groups appear more often with polluted air, but they are descriptive groups, not proof of cause."

### Attention Orchestration Strategy

Use state-first sequencing:

1. Explain that regimes are named condition groups.
2. Start with the regime that has the clearest PM2.5 difference.
3. Compare it with the baseline group.
4. Treat smaller differences as secondary.
5. Repeat that regimes describe conditions; they do not diagnose sources.

### Relationship Prioritization

Most important relationships:

- Low visibility with high PM2.5.
- Dispersive conditions with lower PM2.5.
- Pressure-related regimes with elevated PM2.5.
- Baseline regime as comparison context.

The priority should be exposure meaning, not meteorological completeness.

### Visual Overload Reduction Strategy

The explanation should:

- Translate each regime into plain language.
- Limit Simple Mode to the most important regime contrast.
- Avoid listing all rule conditions at once.
- Put rule definitions in optional detail.
- Use confidence language for weak separation.

### Beginner-Safe Interpretation Path

Beginner flow:

1. Treat each regime as a weather-condition group.
2. Compare the most polluted group with the baseline group.
3. Ask whether the difference is clear or small.
4. Use the result as context, not cause.
5. Do not memorize the rule logic first.

### Analyst Path

Analysts can access:

- Rule definitions.
- Threshold logic.
- Regime membership caveats.
- Comparison across pressure, visibility, and dispersion.
- Relationship with A-06 and A-14.

This should remain in Analytical Mode.

### Special Glossary Strategy

Inline terms:

- Regime: "a named group of weather conditions."
- Baseline: "the comparison group."
- Dispersive: "conditions where air movement may help pollution spread out."
- Low visibility: "hazy conditions that may coincide with particles in the air."

Avoid a technical weather glossary wall. Teach each term only when it appears in the active comparison.

### Redesign Assessment

Guided interpretation should be sufficient if the regimes are translated into plain-English condition groups. The chart does not necessarily need redesign, but the labels need strong explanatory support.

Recommendation: guided interpretation sufficient, with possible label simplification later.

### Special Needs

- Regime translation.
- Cause guardrail.
- Baseline comparison.
- Rule logic hidden until requested.

## 7. A-15 - Weather Variable Pairplot

### Primary Cognitive Failure Mode

Users struggle because a pairplot is a matrix of many mini-charts. It asks users to compare many variable pairs, distributions, colors, clusters, and possible relationships at once.

The main failure is relationship overload. Users often do not know which cell to inspect first, and the visual can feel like a technical lab artifact.

### One Understanding Users Should Leave With

The chart should help users identify which weather relationship is worth investigating first, not understand every pair.

Dominant takeaway strategy:

"Do not read the whole matrix. Use it to find the one or two weather relationships that most deserve follow-up."

### Attention Orchestration Strategy

Use selective relationship sequencing:

1. Start with the strongest or selected relationship.
2. Explain only that pair first.
3. Use diagonal cells only as background distributions.
4. Treat all other cells as optional exploration.
5. Offer a ranked relationship path in Analytical Mode.

If a user clicks a scatter cell, the interpretation should focus on that relationship only.

### Relationship Prioritization

Most important relationships:

- PM2.5 with visibility.
- PM2.5 with pressure.
- PM2.5 with minimum temperature.
- PM2.5 with wind speed.
- Secondary weather-weather relationships only if they explain PM2.5 context.

The matrix should not prioritize weather relationships that do not connect to PM2.5 meaning.

### Visual Overload Reduction Strategy

The explanation should:

- Explicitly tell users not to read every cell.
- Name one first relationship.
- Explain that diagonal cells show individual variable spread.
- Explain that off-diagonal cells compare two variables.
- Move correlation or matrix mechanics to optional detail.

### Beginner-Safe Interpretation Path

Beginner flow:

1. Find the PM2.5 row or column.
2. Choose one weather variable connected to PM2.5.
3. Look for a clear cluster or direction.
4. If the pattern is scattered, treat it as weak evidence.
5. Ignore the rest of the matrix at first.

### Analyst Path

Analysts can access:

- Pair-by-pair relationship ranking.
- Correlation fallback interpretation.
- Distribution shape on diagonals.
- Category-color interpretation.
- Sampling and low-row fallback caveats.

This should not appear in Simple Mode.

### Special Glossary Strategy

Inline terms:

- Pairplot: "a grid of small comparisons between variable pairs."
- Diagonal cell: "a small view of one variable by itself."
- Scatter cell: "a comparison between two variables."
- Correlation: "a pattern where two values tend to move together, without proving cause."

Glossary must be staged. Do not define every weather variable before the user has chosen a relationship.

### Redesign Assessment

Explainability alone is probably not enough for most beginners. A-15 is the strongest candidate for partial redesign or split-view support.

Recommendation: partial redesign recommended. Consider a beginner view that shows only ranked PM2.5-related relationships, with the full pairplot kept as an advanced lab view.

### Special Needs

- Relationship filtering.
- Click-selected relationship focus.
- Ranked relationship summaries.
- Diagonal/off-diagonal teaching.
- Strong Simple Mode suppression.
- Analyst-only full matrix explanation.

## 8. Special-Cognition Migration Model

The normal migrated flow is:

1. Situation Understanding
2. Guardrail
3. Next Step
4. Optional Deeper Understanding

The special-cognition flow should adapt this without exposing complexity:

1. Main Situation
   - One dominant takeaway.
   - One selected focus.
   - One reason it matters.

2. First Focus Path
   - Where to look first.
   - What to ignore initially.
   - What relationship matters most.

3. Guardrail
   - What the chart does not prove.
   - When the pattern is too weak.
   - Why not all dimensions should be interpreted equally.

4. Next Investigation
   - One natural follow-up.
   - No forced recommendations.
   - No relationship branching in Simple Mode.

5. Optional Relationship Lab
   - Analyst-only or collapsed by default.
   - Supports dimensions, metrics, rules, and visual anatomy.

## 9. Migration Readiness By Chart

| Chart | Explainability Alone? | Recommended Strategy | Redesign Risk |
| --- | --- | --- | --- |
| T-02 | Partially sufficient | Focus-first area profile with dimension grouping | Medium |
| T-13 | Mostly sufficient | Active-mode-aware stress driver explanation | Low |
| A-13 | Sufficient with strong translation | Regime-as-condition-group explanation | Medium |
| A-15 | Not sufficient for beginners | Relationship filtering or split beginner/advanced view | High |

## 10. Recommended Implementation Phasing Later

This is not implementation, but future migration should be staged carefully:

Phase SC-1: Add special-cognition metadata fields only if current fields cannot express focus paths cleanly. Prefer reusing existing fields first.

Phase SC-2: Migrate T-13 first because it is closest to the existing stable-pattern model.

Phase SC-3: Migrate A-13 with strong regime translation and cause guardrails.

Phase SC-4: Migrate T-02 with focus-first area profile guidance.

Phase SC-5: Treat A-15 separately. Do not migrate it until relationship prioritization or split-view strategy is decided.

## 11. Acceptance Criteria

A special-cognition migrated chart is successful only if a non-technical user can answer:

- What is the one main situation?
- Where should I look first?
- Which dimensions can I ignore at first?
- What does the pattern mean in real life?
- What should I not assume?
- What is the one next useful investigation?

The user should not need to:

- Decode every dimension.
- Compare every relationship.
- Read a long glossary.
- Understand the chart type before understanding the situation.
- Think like a data scientist.

## 12. Final Recommendation

Do not force the stable-pattern migration template onto these charts. Use the existing explainability architecture, but treat these charts as attention-orchestration problems.

The core migration goal should be:

"Help the user choose the right relationship to think about first."

That is more important than explaining the full visual.
