# Plot-to-PPT Scale Contract

Use this reference whenever a Matplotlib or SVG plot will be placed in PowerPoint, or whenever a figure will be resized from an authoring canvas to a declared manuscript width.

## Final-Container-First Rule

Define the final container before plotting. Keep one machine-readable layout contract beside the plotting source and make both the plot generator and PPT builder read it. The contract must record:

```json
{
  "slide_px": {"width": 1600, "height": 900},
  "target_publication_width_mm": 183,
  "panels": {
    "a": {
      "asset": "../exports/panel_a.svg",
      "slot_px": {"left": 30, "top": 68, "width": 750, "height": 800},
      "source_canvas_mm": {"width": 85.78125, "height": 91.5},
      "subplot": {"left": 0.16, "right": 0.96, "bottom": 0.16, "top": 0.86},
      "final_metrics_pt": {"text": {"axis": 7.5, "tick": 7.0, "legend": 7.0}, "strokes": {"context": 0.55, "primary": 1.0}}
    }
  },
  "typography_final_pt": {
    "family": "Arial",
    "minimum": 6.5,
    "axis": 7.5,
    "tick": 7.0,
    "legend": 7.0,
    "annotation": 7.0,
    "panel_title": 9.0
  },
  "stroke_final_pt": {"context_minimum": 0.55, "primary_minimum": 1.0},
  "qa_thresholds": {"aspect_anisotropy_max": 0.01, "minimum_final_text_pt": 6.5, "minimum_context_stroke_pt": 0.55, "minimum_primary_stroke_pt": 1.0},
  "visual_grammar": {
    "line_policy": "one solid semantic-colour line per strategy",
    "marker_policy": "declared events only",
    "legend_policy": "one compact shared legend",
    "direct_label_policy": "not combined with a complete legend"
  }
}
```

These dimensions and thresholds are an example, not a global publication size.
The checker accepts the old `slide: {width_px, height_px}` spelling, but rejects
conflicting `slide` and `slide_px`. Missing text/stroke measurements are not
guessed. `final_metrics_pt` and PPT slots are **declarations**: the checker reads
SVG geometry and checks these declarations; it does not measure actual PPTX
fonts or perform visual review. Inspect the package and actual render as well.

Compute each panel's final physical size from the declared manuscript width:

```text
panel_final_width_mm  = target_width_mm * panel_width_px  / slide_width_px
panel_final_height_mm = target_width_mm * panel_height_px / slide_width_px
```

Generate the source plot at that physical width and height. Do not choose an unrelated Matplotlib `figsize` and stretch it later in PowerPoint.

## Aspect-Ratio Gate

For each embedded SVG, compare the SVG `viewBox` ratio with its final PPT object ratio. Compute:

```text
anisotropy = max(scale_x / scale_y, scale_y / scale_x) - 1
```

Fail assembly when anisotropy exceeds `0.01` by default. `fit: contain`, `lockAspectRatio`, or an editor checkbox is not proof that a round-trip renderer preserved the geometry. Verify the exported PPTX and rendered preview.

When ratios disagree, choose one of these fixes:

1. regenerate the plot at the intended slot ratio;
2. compute an aspect-preserving contained rectangle and accept explicit whitespace;
3. redesign the panel allocation.

Never stretch an SVG to fill a mismatched rectangle. Check publication slides and component-board copies independently.

## Axes-Geometry Gate

Passing the SVG/PPT anisotropy check proves only that the asset was not stretched. It does not prove that the source chart has an appropriate visual aspect ratio. Record the main data-axes rectangle separately from the outer canvas:

```text
axes_width  = source_canvas_width  * (subplot.right - subplot.left)
axes_height = source_canvas_height * (subplot.top - subplot.bottom)
axes_aspect = axes_width / axes_height
```

For ordinary line and scatter panels, use `0.95–1.30` as the default final-size axes-aspect range unless the data argument requires a deliberately wide or tall chart. Peer panels in the same row should normally differ by no more than `10%` in relative axes aspect. Treat these as configurable layout checks, not a reason to use `ax.set_aspect("equal")`; unrelated scientific units must not be forced to equal data scaling.

For a nonstandard evidence panel whose argument intrinsically requires a strip, timeline, raster, or other deliberately extreme aspect ratio, declare a non-empty `axes_aspect_exempt` reason in that panel's layout record. The scale checker may then omit that panel from ordinary axes-range and peer-aspect comparisons, while still enforcing the SVG/PPT anisotropy, source-canvas, text-size, and stroke-width gates. Do not use this field to excuse an ordinary chart that merely has a poor allocation.

Colorbars, legends, and secondary axes consume visual width. Reserve them explicitly in the shared layout contract and judge the main data-axes rectangle after that reservation. A panel can pass the outer-canvas aspect check yet still fail because an external colorbar makes the evidence area too narrow.

## Matplotlib Export Rule

For fixed PPT panel assets:

- use the physical canvas from the shared layout contract;
- use explicit subplot margins;
- avoid `bbox_inches="tight"` because content-dependent cropping changes the exported viewBox and effective font scale;
- use `save_nature_figure(..., fixed_canvas=True)` or the multi-panel CLI's
  `--fixed-canvas` for a fixed slot; standalone export keeps its legacy crop;
- if tight cropping is scientifically necessary, read the exported viewBox and recompute the PPT object bounds before assembly;
- keep the canonical SVG text-editable and create a same-viewBox outlined-text copy only when the PowerPoint backend requires it.

## Final-Size Typography

Record and report the complete scale chain:

```text
source plot -> embedded PPT object -> final manuscript width
```

Default paper-figure targets, unless a venue requires otherwise:

- smallest visible chart text: at least `6.5 pt` at final manuscript size;
- ticks, legend, and annotations: target `7 pt`;
- axis labels: target `7.5–8 pt`;
- panel titles: target `8.5–9.5 pt`;
- effective font-size difference between peer panels: no more than `5%`.

Do not judge chart typography from source-code font values alone. Cropping and placement scale can make identical source values render at different final sizes.

For native PPT objects, declare the assembly spec's
`target_publication_width_mm` when known. The builder compensates manifest
point-sized fonts/strokes for the source-canvas-to-manuscript scale. Omission
keeps legacy source sizing and leaves final-size readiness unverified; it does
not assume 183 mm. Existing object `font_size` remains backend pixels. Do not
apply the native-object compensation again to a plot already drawn at its final
physical size. Confirm actual exported XML and final-size rendering.

Use one locked project font family and record every final-size role needed by the chart. Equivalent roles in peer panels must use the same role value. Do not introduce a one-off font size, weight, or family merely to make a local annotation fit; simplify, relocate, or move it to the caption.

When the plot has legends, markers, direct labels, or dense annotations, apply [plot-annotation-and-typography-contract.md](plot-annotation-and-typography-contract.md) and store the chosen visual grammar beside the geometry. Plot and PPT assembly must consume the same record.

## Contrast-Survival Gate

Dense observations may be contextual, but they must remain detectable after resizing. Separate fill and outline tokens when a pale semantic colour is unsuitable for a fine signal.

Default thresholds:

- dense context strokes: at least `0.55 pt` at final size;
- primary or summary strokes: at least `1.0 pt` at final size;
- marker outlines: at least `0.65 pt` at final size;
- dense context alpha: normally `0.28–0.40`; lower values require a successful downscale preview;
- pale fills may remain pale, but fine outlines and reference lines use a darker companion token.

Do not merely darken every overlapping observation until the panel becomes a solid mass. Use layered encoding: visible context observations, stronger representative summaries, and the highest-contrast claim-bearing marks.

## QA Surfaces

Inspect all of the following:

1. canonical SVG/PDF or PNG at declared physical size;
2. the final PPT slide at full render size;
3. a downscaled preview around `1000–1200 px` wide;
4. a grayscale preview when colour carries distinction.

The scale QA report must list SVG viewBox, PPT bounds, scale-x, scale-y, anisotropy, declared final panel size, main axes size and aspect, font family and final-size role hierarchy, minimum final text, minimum final stroke, selected legend/marker/direct-label policy, and unresolved issues. For a new or materially revised plot that uses the visual-grammar contract, run `qa_plot_ppt_scale.py --require-visual-grammar --strict`.
