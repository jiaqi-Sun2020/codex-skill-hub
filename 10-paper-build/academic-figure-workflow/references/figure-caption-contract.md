# Figure Caption Contract

Use this reference for every manuscript-facing figure and whenever the user asks for 图注, caption, figure legend, annotations after PPT generation, or removal of configuration text from the artwork.

## Artwork Versus Caption

Keep inside the artwork only information needed to decode the visual claim:

- panel labels, axes, units, tick labels, legends, category names, essential equations, and statistical symbols;
- short module names and transformations needed to follow a mechanism or architecture;
- concise metric callouts when the comparison itself is the panel claim.

Move to the caption by default:

- sample counts, source-group counts, train/validation/test scope, preprocessing recipes, interpolation point counts, normalization, fold-local rules, optimizer or training settings;
- definitions of error bars, confidence intervals, significance tests, aggregation, and cross-validation;
- longer implementation notes, calibration protocol, exclusions, and data provenance;
- explanatory grey text that duplicates the caption or competes with the data.

An exception is allowed when removing the text would make the marks ambiguous or scientifically misleading. Record the reason in the figure manifest.

## Required Caption Structure

Create `caption.md` beside the final figure or PPTX. It should contain:

1. **Figure number and claim-focused title.**
2. **Panel descriptions** in `(a)`, `(b)`, ... order, stating what is shown rather than restating visual appearance.
3. **Methods needed for interpretation**, including transformations and evaluation/calibration protocol.
4. **Statistics and uncertainty**, including sample size, aggregation, error-bar meaning, test name, and whether metrics are fit-domain or held-out.
5. **Scope and exclusions**, especially train/validation/test boundaries.
6. **Abbreviations and symbols** not already obvious from the manuscript.

Do not invent missing caption facts. Mark unresolved items explicitly.

## Element-by-Element Quantitative Caption

When the user asks for a detailed caption or when a quantitative panel is not self-explanatory, inventory every visible encoding before writing. For each panel, state:

- what the x-axis and y-axis represent, including units, transformations, normalization scope, and whether values are raw, derived, standardized, or predicted;
- what each line, point, bar, band, image, colour scale, marker fill, marker outline, error bar, dashed reference, and annotation means;
- the observation grain represented by one mark and whether any jitter, aggregation, smoothing, interpolation, or resampling affects display only or enters the computation;
- which marks are individual data, robust summaries, uncertainty, fitted models, baselines, proposed methods, or ground truth;
- the explicit comparison performed by the panel and the scientific role of every compared method or representation;
- for threshold or budget-selection figures, whether each mark represents a single criterion, an individual criterion pass rate, a joint all-criterion pass, a first isolated pass, or a consecutive stability window; include the denominator and distinguish prespecified from sensitivity-only rules;
- equations, symbol definitions, fit domain, coefficient units, metric definitions, and validation protocol when those are moved out of the artwork.

Removing a dense in-panel equation or metric callout transfers its explanatory burden to the caption. Confirm that every removed item remains defined in `caption.md` and PPT speaker notes. Do not describe a display-only jitter as measurement uncertainty or allow a generic legend term such as `Data spectra` to obscure the actual train/validation/test scope.

## PPTX Integration

For academic PPT figure kits, default to all three caption surfaces: `caption.md`, publication-slide speaker notes, and native editable visible panel explanations on a supporting slide or reserved column. Keep the publication artwork itself clean. Use notes-only or a single-slide exception only when the user explicitly asks for it, and record the override in the manifest.

### Clean publication artwork

For a publication-figure slide:

- keep the visible slide caption-free unless the user asks to typeset a caption on the slide;
- write the full caption into the slide speaker notes under `[Figure caption]`;
- keep provenance under a separate `[Sources]` block;
- record the caption path in `ppt_manifest.json` and trace it to the figure/PPT slide;
- component-board slides may contain a native `Caption draft` text box only when the user wants to edit the caption visually.

Speaker notes supplement but do not replace `caption.md`, because journal submission systems and manuscript editors need a portable text file.

### Visible detailed-caption mode — default for PPT figure kits

For every academic PPT figure kit, and especially when the user asks to add all figure captions, detailed panel explanations, or 逐图解释 inside the PPT:

- preserve the clean publication slide unless the user explicitly asks to typeset the manuscript caption beneath the artwork;
- add a separate native editable `Caption & Interpretation` slide, or a dedicated explanation column on a supporting slide;
- create one stable, named section for every displayed panel in display order;
- explain every visible encoding using the element-by-element quantitative caption requirements above;
- include the panel's scientific comparison and defensible result, not only a description of its appearance;
- keep long provenance and implementation details in speaker notes or `caption.md` rather than turning the visible page into a methods appendix;
- split the explanation across multiple slides when necessary; do not shrink text below the declared PPT editing-size minimum or allow clipping;
- keep the visible explanation, `caption.md`, and `[Figure caption]` speaker notes scientifically consistent. They may differ in layout and concision, but not in definitions, values, scope, or conclusions.

If the user explicitly requests a single publication slide or notes-only delivery, omit the visible explanation surface and record `caption_delivery.visible_override` with the user-approved reason. Do not silently fall back to notes-only.

Record the delivery in `ppt_manifest.json`:

```json
{
  "caption_delivery": {
    "caption_md": "caption.md",
    "speaker_notes": true,
    "visible_caption_slides": [2],
    "visible_override": null,
    "panel_annotation_map": {
      "a": "annotation_a",
      "b": "annotation_b"
    }
  }
}
```

## Caption QA

Verify that:

- every panel is described exactly once and in display order;
- every axis and every visible legend/mark type is explained, and the intended comparison is explicit;
- all visible encodings and error bars are defined;
- sample counts and data partitions match the source data;
- transformations and units match the plotting code;
- reported metrics distinguish calibration fit from held-out or cross-validated performance;
- no configuration paragraph remains in the plot merely because it was present in an earlier draft;
- the caption in PPT notes matches `caption.md`.
- every panel requested for visible PPT explanation has one native editable annotation section and a manifest mapping;
- visible caption text is not clipped, does not cover data, and is split rather than reduced below the declared editing-size minimum;
- the visible explanation, `caption.md`, and speaker notes do not contradict each other;
- single-metric threshold crossings are not described as joint acceptance unless every formal criterion passes at the same candidate value.
