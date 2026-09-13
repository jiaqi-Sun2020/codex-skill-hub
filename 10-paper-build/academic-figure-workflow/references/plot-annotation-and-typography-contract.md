# Plot Annotation and Typography Contract

Use this reference when a plot has mixed fonts, crowded legends, repeated markers, competing direct labels, inconsistent annotations, or a final-size render that feels visually noisy even though the data are correct.

## Objective

Reduce visual grammar to the smallest set of encodings that still lets the reader decode the scientific comparison. This contract changes presentation, not data, statistics, axes, ordering, or scientific meaning.

## Required Visual-Grammar Record

For new or materially revised plots, record the following in the shared plot/PPT layout contract or an adjacent chart contract:

```yaml
typography:
  family: Arial
  axis_title_pt: 8.0
  tick_pt: 7.0
  legend_pt: 7.0
  annotation_pt: 7.0
  panel_title_pt: 9.0

visual_grammar:
  colour_roles: semantic
  line_policy: one solid line per strategy
  marker_policy: none for dense sweeps; declared events only
  legend_policy: one shared or compact legend
  direct_label_policy: do not combine with a complete legend
  threshold_policy: neutral reference styling
```

Use the project style manifest for actual font families, sizes, colours, strokes, and semantic roles. The example values are not universal defaults.

## Encoding Economy

Assign one primary encoding to each scientific distinction. Additional encodings are allowed only when they solve a real problem such as grayscale interpretation, colour-vision accessibility, overlapping traces, or a declared event.

- Do not encode the same strategy simultaneously with colour, line style, repeated marker, full legend, curve-end label, and per-point text.
- For dense ordered sweeps, default to one solid semantic-colour line per strategy and no repeated markers.
- For sparse observations whose locations matter, markers may represent samples. Keep one marker family across peer panels and record its meaning.
- Open circles, rings, stars, or other salient markers may denote a declared event such as a first joint pass. They must not be decorative and must not imply a second method.
- Use a neutral high-contrast style for thresholds, zero lines, full-grid references, and stability windows unless the reference itself is a compared method.
- Never remove a scientifically necessary event or uncertainty encoding merely to simplify appearance. Move detailed definitions to the caption when the mark can remain concise.

## Legend and Direct-Label Decision

Choose one primary identity mechanism:

1. **Compact legend** when names are long, traces cross, or curve ends are crowded.
2. **Direct labels** when there are few traces, endpoints are separated, and labels can sit in reserved whitespace.
3. **Shared legend** when peer panels repeat the same methods.

Do not use a complete legend and repeat the same method names at every curve end. A short threshold label or a single event annotation does not count as a second method legend.

Reserve legend bounds in the layout contract. Do not place a legend over claim-bearing data. If no clean location exists, move the legend above or beside the axes, use a shared legend, or enlarge/reallocate the panel.

## Annotation Density

- Label only events needed to understand the panel claim.
- Do not label every point, bar, or budget when axes provide the same information.
- Keep configuration prose, preprocessing details, sample counts, fold rules, optimizer settings, and long equations in the caption unless needed to decode a visible mark.
- Use a single annotation syntax for peer events: identical alignment, offset, colour rule, and numeric format.
- If more annotations are scientifically required than fit without collision, split the diagnostic view from the publication view rather than shrinking text.

## Typography Discipline

- Use one locked font family per paper unless mathematical notation requires a documented companion font.
- Use the style-manifest hierarchy for panel titles, axis titles, ticks, legends, annotations, and panel labels.
- Peer panels must use the same final-size font values for equivalent roles; effective font scale should differ by no more than the project QA tolerance.
- Do not introduce arbitrary bold, italic, colour, or all-caps styling to solve hierarchy locally.
- Avoid more than the declared role hierarchy within one panel. A new one-off font size requires a documented semantic role or should be removed.
- Never solve overflow by reducing text below the declared minimum. Shorten labels, move explanations to the caption, reserve more space, or split the panel.

## PPT Integration

Matplotlib/SVG generation and PPT placement must consume the same typography and visual-grammar record. Regenerate a plot for its final slot rather than stretching it or compensating with different PPT text sizes.

PPT-native panel titles, labels, legends, or annotations must inherit the same font family, hierarchy, semantic colours, and spacing rhythm. Office defaults are not an acceptable silent fallback.

## Intercept and QA

Reject or revise the figure when any of the following is true:

- dense curves carry repeated markers without a sample-level or event-level meaning;
- a full legend duplicates complete curve-end labels;
- method identity changes between panels;
- equivalent text roles use inconsistent font family, size, weight, or alignment;
- labels, legends, or annotations cover data or compete with the primary comparison;
- a salient marker is not defined in the caption;
- the plot passes at authoring size but becomes unreadable in the final publication or 1000–1200 px PPT preview;
- simplification removed or altered observed values, uncertainty, thresholds, axis limits, scales, or comparison roles.

Record what was removed or consolidated in `visual_grammar.redundant_encodings_removed` or the figure manifest.
