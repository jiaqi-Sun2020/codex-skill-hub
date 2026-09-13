# PPTX Figure Assembly

Use this reference when PowerPoint is the editable canvas for a paper figure or reusable figure kit. This workflow assembles existing evidence-backed components; it does not redefine their scientific content.

## Default Strategy

Default to `hybrid`:

- **Level A — Native editable:** PowerPoint text boxes, panel labels, rectangles, rounded rectangles, lines, connectors, arrows, and simple modules.
- **Level B — Vector editable:** complex architecture and plots inserted as SVG, with external `.svg`, `.drawio`, and `.py` sources preserved.
- **Level C — Raster asset:** photographs, microscopy, screenshots, and unavoidable bitmap results only.

Do not claim that an embedded SVG is fully editable as native PowerPoint geometry. It is vector-resizable in PowerPoint; its external source remains the authoritative editable component.

## Modes

### Figure Assembly

Place each panel as an independent object. Panel labels such as `(a)`, `(b)`, `(c)`, and `(d)` must be native text boxes. Native annotations and arrows remain independent. Preserve aspect ratio and leave enough space for final-size labels.

For Matplotlib or SVG data plots, apply [plot-to-ppt-scale-contract.md](plot-to-ppt-scale-contract.md). Plot code and assembly code must consume the same panel bounds. Never rely on a mismatched image frame plus `fit: contain` or `lockAspectRatio` without verifying the final exported PPTX.

Never pre-flatten all panels into one PNG.

For a journal-facing architecture or workflow panel, apply [publication-architecture-layout-gate.md](publication-architecture-layout-gate.md). The publication slide must be visually clean at the declared manuscript width; authoring guidance, provenance notes, and editability instructions belong on the component board or in the manifest.

### Component Board

Create a second slide containing reusable independent components such as input, encoder, attention, fusion, decoder, output, connectors, legends, comparison plots, ablation plots, and raster assets. Use meaningful object names. Include a small native legend indicating Level A, B, or C.

The board is a working canvas, not a publication panel. It may use a larger slide or grid, but it must inherit the same style manifest.

## Caption Integration

Apply [figure-caption-contract.md](figure-caption-contract.md). Keep manuscript captions out of the visible publication artwork unless explicitly requested. Save `caption.md`, place the same text under `[Figure caption]` in the publication slide's speaker notes, keep `[Sources]` separate, and record the caption path in `ppt_manifest.json`.

Academic PPT figure kits use visible detailed-caption mode by default; explicit requests for all captions or detailed explanations reinforce this requirement:

- add a separate `Caption & Interpretation` slide or a reserved explanation column on a supporting slide;
- use native editable PowerPoint text, one named section per panel in display order;
- explain axes, units, marks, colours, line/marker styles, uncertainty, thresholds, comparison roles, transformations, data scope, and the defensible result;
- keep the publication artwork uncluttered unless the user explicitly asks for a typeset caption beneath it;
- split across slides instead of shrinking or clipping the explanations.

Omit the visible explanation surface only when the user explicitly requests notes-only or a single-slide publication deliverable. Record the override and reason in `caption_delivery.visible_override`.

## Assembly Specification

The current backend accepts a JSON assembly specification. Keep backend options out of the scientific figure protocol. A minimal structure is:

```json
{
  "slide_size": {"width": 1600, "height": 900},
  "mode": "hybrid",
  "slides": [
    {
      "kind": "figure_assembly",
      "title": "Final assembled figure",
      "objects": [
        {
          "id": "panel_a",
          "type": "asset",
          "path": "../fig01_architecture/exports/fig01.svg",
          "panel_label": "(a)",
          "editability": "B",
          "source_trace": ["../fig01_architecture/source/fig01.drawio"]
        }
      ]
    },
    {"kind": "component_board", "objects": []}
  ]
}
```

Each object needs a stable `id`, explicit bounds or a documented auto-layout rule, editability level, asset path where relevant, and source trace.

## Data-Plot Rule

For experimental plots, preserve:

```text
source data + plotting source + SVG
```

Embed the SVG by default. Create a native PowerPoint chart only when the backend reliably preserves all data, error bars, statistical markers, axis limits, log scales, and observed points. If any feature cannot be preserved, keep the SVG and report the limitation.

## PPT Manifest

Generate `ppt_manifest.json` beside the PPTX:

```json
{
  "style_manifest": "../style/style_manifest.yaml",
  "backend": {},
  "slides": [],
  "assets": [],
  "caption_delivery": {
    "caption_md": "caption.md",
    "speaker_notes": true,
    "visible_caption_slides": [],
    "visible_override": null,
    "panel_annotation_map": {}
  },
  "visual_grammar": {
    "legend_policy": "",
    "marker_policy": "",
    "font_hierarchy": {},
    "redundant_encodings_removed": []
  },
  "source_trace": {},
  "editability": {},
  "raster_fallbacks": [],
  "unresolved_issues": []
}
```

For every object, trace:

```text
PPT object -> embedded SVG/native/raster asset -> Draw.io/Python source -> source data/manuscript evidence
```

Record expected and verified media type separately. If an SVG is rasterized during export, add it to `raster_fallbacks` and do not count it as Level B.

## Backend Selection

Before building:

1. detect the currently available presentation tooling;
2. prefer a backend supporting native shapes, editable text, SVG placement, PPTX export, and rendered previews;
3. do not silently install large dependencies;
4. keep the assembly spec and scientific source trace backend-neutral;
5. use a graceful fallback and record every reduced-editability decision.

The bundled `build_figure_pptx.mjs` uses the Codex presentation runtime when available. Runtime paths are environment-specific and must not be hard-coded into the scientific protocol.

If the style manifest uses full YAML rather than the dependency-free JSON-compatible template, normalize it first with `validate_style_manifest.py --emit-json` and pass the result through `--style-json`.

## PPT QA

Generate a temporary rendered preview and check:

- PPTX opens successfully and slide size is correct;
- no object is outside the slide, unexpectedly overlapping, or clipping text;
- fonts, panel labels, colours, arrows, borders, and spacing match the style manifest;
- structural connectors use the high-contrast foreground token rather than pastel module colours, and arrowheads terminate at target nodes;
- adjacent same-row modules use straight attached connectors with explicit side anchors; branch turns alone use elbow routing;
- one-to-many fan-out uses a visible native split junction, and no visible connector segment disappears under a module fill;
- connector z-order is selected by role rather than sending every edge to the absolute back;
- peer modules preserve the same named interior template, padding, title/body regions, and grid rhythm;
- numeric peer mappings use independent left-value, operator, and right-value objects with identical bounds and no automatic wrapping;
- process and descriptor modules use consistent key-value or grouped scientific notation rather than mixed prose and formulas;
- fork/junction/operator marks are centred native geometry rather than text glyph approximations;
- regression and prediction/output components keep all text in distinct, unclipped regions;
- SVGs remain SVG media rather than unexpected PNG/JPEG fallbacks;
- native text and shapes remain independently editable and movable;
- explicit visible-caption requests produce one native editable section per displayed panel, with no missing or duplicate panel mapping;
- visible panel explanations define every plotted encoding and remain consistent with `caption.md`, notes, plot code, and source data;
- captions or explanations are split to additional slides instead of being shrunk into clipped or unreadable text;
- panels and raster assets remain independently replaceable;
- aspect ratios and axis ranges are preserved;
- SVG viewBox and PPT object bounds produce no more than 1% scale anisotropy;
- main line/scatter data axes use a declared visual aspect range (normally 0.95–1.30), peer axes-aspect ratios differ by no more than 10%, and colorbars do not silently narrow one panel;
- peer plot panels use the same final-size typography budget and differ by no more than 5% in effective font scale;
- dense signals, markers, error bars, and annotations remain visible in a 1000–1200 px downscaled slide preview;
- object names, editability levels, and source traces exist;
- all raster fallbacks and unresolved issues are documented.

Use rendered preview inspection plus structural inspection of the PPTX package. Rendering alone cannot prove editability.

After QA passes, apply [figure-package-hygiene.md](figure-package-hygiene.md). Delete temporary preview PNGs, layout JSON, montage files, inspect snapshots, and starter decks unless the user explicitly requests them as deliverables. Keep the validation result in the manifest.

Run `scripts/qa_pptx_package.py` after assembly. It checks the PPTX ZIP structure, slide bounds, native text runs, media types, and source-SVG hashes, then updates `ppt_manifest.json`. Use `--require-visual-grammar` for new or materially revised plot/PPT layouts. For academic PPT figure kits, use `--require-caption-delivery` by default; this requires a resolvable caption file, speaker notes, visible caption slides, and a non-empty panel annotation map. A user-approved notes-only or single-slide override must be validated separately and recorded rather than silently bypassing the default. Its manual-preview list remains mandatory because XML inspection cannot prove that fonts render correctly or that text is visually unclipped.

## Final Editability Report

Report:

```text
Native PPT objects:
Vector SVG objects:
Raster objects:
External editable source files:
Known editability limitations:
```

For a paper-figure editing canvas, manuscript final-size typography may be smaller than normal presentation-deck typography. The final-size publication standard governs the figure; the component-board slide may use larger labels for editing comfort.

Report the numeric scale factor and smallest final-size text rather than judging legibility only from the full-slide render.
