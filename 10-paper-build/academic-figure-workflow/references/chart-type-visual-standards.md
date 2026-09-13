# Chart Type Visual Standards

Use this reference when choosing or polishing a data-backed plot, benchmark figure, ablation chart, heatmap, confusion matrix, or table-like figure.

## Universal Data Plot Rules

- State units in axis labels when units exist.
- State uncertainty meaning before plotting error bars or bands.
- Do not add statistical marks without test name, sample size or run count, and comparison meaning.
- Prefer source-data-driven scripts over manual chart editing.
- Use consistent category order across panels.
- Avoid chart junk: shadows, gradients, 3D bars, decorative icons, and heavy grid backgrounds.
- For small samples, show individual observations rather than hiding them behind aggregates.
- If a user requests a misleading chart type, explain the risk and propose a safer alternative before drawing.

## Bars

Use for discrete comparisons, not continuous trends.

- Keep a clear zero baseline unless a justified truncated axis is explicitly labelled.
- Do not use mean-only bars for `n < 10` per group; use dot/strip plots, box plots, or violin plots with visible points.
- Prefer horizontal bars for long method names or ablation components.
- Use direct value labels sparingly; do not label every bar if axis reading is cleaner.
- For many methods, use one hue family plus alpha or lightness changes for related variants.
- Use hatch/line/marker redundancy when colour carries category meaning.

## Lines And Trends

Use for ordered x-values, time, training steps, or sample size trends.

- Do not connect categorical or unordered x-values with lines unless the connection encodes a real paired/repeated-measure relation.
- Keep line identities consistent across panels.
- Use uncertainty bands with low alpha when uncertainty is available.
- Use markers only when sample points matter or lines overlap.
- Use sparse tick marks and avoid dense grids.
- Place a shared legend above or beside the group when several panels reuse the same methods.
- For dense ordered sweeps, prefer one solid line per semantic strategy, remove repeated point markers, and use direct labels or a compact shared legend. Preserve the raw evaluated values.
- Use open or otherwise visually distinct markers only for declared events such as the first all-criterion pass; do not let marker style imply a new method.

## Legend, Marker, Label, and Font Economy

When legends, markers, direct labels, annotations, or fonts compete with the data, apply [plot-annotation-and-typography-contract.md](plot-annotation-and-typography-contract.md).

- Choose one primary method-identity mechanism: compact legend, shared legend, or direct labels.
- Do not combine a complete legend with repeated curve-end method names.
- Dense sweeps default to unmarked solid lines; markers require a declared sample-level or event-level meaning.
- Keep threshold and reference styling neutral so it is not mistaken for another compared method.
- Use one project font family and the locked role hierarchy; equivalent roles in peer panels must use the same final-size typography.
- Remove redundant labels before reducing font size. Move methods and configuration detail to the caption when it is not needed to decode the marks.
- Validate the simplified grammar after final-size rendering; do not alter data, uncertainty, axis limits, or scientific roles to obtain a cleaner appearance.

## Criterion And Budget-Selection Figures

- Separate four questions into non-redundant panels when needed: how the selection expands, how the primary metric changes, which individual criteria are restrictive, and whether joint passes are stable across adjacent budgets.
- A pass-rate panel must include all formal criteria, a common 0–100% scale, the exact denominator, and one consistent strategy colour per method.
- Do not mix the descriptive best observed metric with the formal minimum reliable budget unless the figure explicitly compares those definitions.
- Use a detailed per-budget × criterion audit map as a diagnostic or supplementary component, not as the only explanation of the selection rule.
- Draw stability-window references as neutral thresholds; label which window was prespecified and which is sensitivity-only.

## Scatter And Embeddings

Use for point-level relationships or projected spaces.

- Avoid overplotting by using alpha, smaller markers, density contours, or hexbin summaries.
- State whether axes are meaningful dimensions, embeddings, or arbitrary projections.
- Do not imply clusters are real categories unless the analysis supports that claim.
- Label highlighted groups directly when there are only a few.

## Heatmaps And Matrices

Use for dense matrix-like relationships.

- Include a readable colour bar with units or score definition.
- Choose sequential, diverging, or categorical palettes according to the data type; avoid rainbow/jet palettes for quantitative values.
- Keep missing values visually distinct from low values.
- Use text inside cells only when the matrix is small enough at final size.
- For confusion matrices, state whether values are counts, row-normalized, column-normalized, or percentages.

## Ablation And Benchmark Figures

- Group baselines, variants, and the proposed method consistently.
- Encode improvement direction unambiguously.
- Keep the same metric direction across panels; if higher/lower changes, label it.
- Do not use colour to make a method look better than the data justify.
- Include run count, split, dataset, and metric definition in the caption or support note.

For manuscripts that already include ablation experiments, use three progressive checks:

1. Replacement ablation: do not only compare "with module A" against "without module A"; when feasible, replace A with a traditional module of comparable parameter scale or computational role to show the proposed design is not only benefiting from added capacity.
2. Hyperparameter robustness: for new mechanism hyperparameters such as loss weights, mask ratios, thresholds, or module depths, show a trend plot or heatmap across a meaningful range rather than only the best value. A stable plateau supports robustness; a narrow isolated peak requires training-stability discussion.
3. Cross ablation: when two or more new core components are claimed, provide a full-combination table or matrix, such as 2x2 or 3x3, to show each component alone and the joint effect.

If the data needed for these checks is missing, route the gap to writing or research verification as an experiment/material request instead of implying the ablation is complete.

## Tables As Figures

Use only when visual comparison is stronger than a native table.

- Keep typography consistent with the manuscript.
- Use subtle rules, not heavy cell borders.
- Align numbers by decimal point when practical.
- Highlight only the values that support the figure's claim.
- Keep the source table or structured data available.

## Intercept Checklist

Before finalizing a data plot, reject or revise:

- mean-only bars for small n;
- dual y-axes for unrelated variables;
- pie charts or 3D charts for precise comparisons;
- truncated y-axes on bars without explicit visual break and justification;
- continuous colour encodings without a labeled colorbar;
- red/green-only encodings without marker, line, hatch, label, or grayscale redundancy;
- overpacked legends or more than roughly 12 category combinations in one panel;
- statistical stars without test, n, comparison, and correction context.

## Source Basis

This reference adapts high-impact figure design patterns, Nature/PLOS readability constraints, common ML/engineering paper plotting standards, and data-visualization advisor patterns from the referenced SciPilot figure skill into chart-specific checks.
