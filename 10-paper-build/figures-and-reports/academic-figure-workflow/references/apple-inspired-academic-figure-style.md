# Apple-Inspired Academic Figure Style (Optional)

Read this only when the user explicitly selects Apple-inspired / 苹果风 academic
figures. This is an independent, unofficial adaptation, not an Apple standard,
product, affiliation or endorsement. A request for a clean or minimal figure
alone does not select it. Without selection, retain the existing workflow.

## Purpose and precedence

Make scientific structure easier to read through restrained hierarchy,
alignment, consistent spacing and a cool neutral ground. Do not turn figures
into a website or app interface. Preserve information, not ornamental density.

Use the sole precedence in
[figure-style-manifest.md](figure-style-manifest.md#precedence-and-encoding-scope).
This optional preference cannot change scientific protections, actual delivery
requirements or QA gates; it does not replace the existing workflow default
when it has not been explicitly selected.

If a higher requirement conflicts with a locked token or template, report the
conflict and request a specific authorized deviation; priority is not permission
to overwrite a protected baseline. Selecting this style is not approval to
unlock an existing project, remove scientific content, or replace a template.

## One appearance source, no new configuration

Read the project's [Style Manifest](figure-style-manifest.md). Use its resolved
`<figure-root>/style/style_manifest.yaml`, including the existing paper-Pipeline
root `05_manuscript_zh/figures/` when applicable. Do not create a second manifest,
new schema version, preset loader, style-name flag or figure-local palette.

For an unlocked style, review candidate tokens before use. The following is an
**illustrative token patch**, not a complete manifest or a mandatory preset.
All fields already exist in `assets/style_manifest.template.yaml`. Apply only
approved values to the current complete manifest; validate with the existing
validator. These point sizes are a starting point for a 183 mm test figure,
not a substitute for final-size or venue checks.

```json
{
  "neutral_colors": {"text": "#1D1D1F", "muted_text": "#515154", "border": "#6E6E73", "grid": "#D2D2D7"},
  "backgrounds": {"figure": "#FFFFFF", "panel": "#FFFFFF", "slide": "#FFFFFF"},
  "typography": {"hierarchy_pt": {"title": 8.0, "body": 7.0, "annotation": 6.5, "panel_label": 8.0, "axis_label": 7.0, "tick": 6.5, "legend": 6.5}},
  "strokes": {"axis_pt": 0.6, "module_pt": 0.7, "line_pt": 1.15, "connector_pt": 0.9},
  "borders": {"color": "#6E6E73", "style": "solid"},
  "corners": {"panel_radius_pt": 2.0, "module_radius_pt": 2.0},
  "fills": {"mode": "flat", "gradient_allowed": false},
  "shadows": {"enabled": false, "token": "shadow-none"}
}
```

Keep existing semantic colours and their role mappings. The patch deliberately
does not replace `semantic_colors`, change axes, uncertainty, markers or line
identities. Refine neutral presentation only when needed. Never collapse
distinct methods or branches into one colour merely to obtain a single accent.
Use shape, line style, position or labels as non-colour cues; make uncertainty
and essential connectors legible in grayscale and colour-vision previews.

Keep the manifest's approved font family. Choose an installed, embeddable
publication-appropriate font only when none is fixed; verify actual glyphs and
fallbacks. Do not distribute SF Pro, SF Symbols, Apple logos/UI kits, product
silhouettes or website screenshots. Do not import web pixel sizes, negative
tracking, touch targets, animations or mandatory glass effects into print art.

## Architecture figures

- Read [publication-architecture-layout-gate.md](publication-architecture-layout-gate.md)
  and the existing SVG/Draw.io rules. Establish source-backed entities and edges
  before visual styling.
- Use alignment, whitespace, a small type hierarchy and consistent fine strokes
  to distinguish stages. A background or modest corner treatment must encode a
  real boundary, not a decorative card.
- Preserve every required module, branch, merge, arrow direction, equation,
  label and tensor dimension. Show parallel paths as parallel paths, and keep
  arrowheads connected and visible against the actual background.
- Do not hide connectors, shrink essential labels, merge scientific branches,
  or omit dimensions for a quieter composition.

## Quantitative figures

- Keep actual data, displayed populations, selectors, transformations, ordering,
  axes/ranges/scales/units, threshold values, uncertainty definitions, error
  bars and statistical annotations unchanged during a visual-only revision.
- Use the existing `--style-manifest` interface or `nature_mpl_style.py` for
  custom plots. Do not add a special renderer or recompute science for this style.
- Keep one coherent legend/direct-label grammar and meaningful point/line
  encodings. Markers may be simplified only when they carry no scientific
  meaning; never remove evaluated samples or error bars as decoration.
- Pale text, faint evidence, clipped axes and a truncated scale do not become
  acceptable because the result looks restrained. A semantic or data change is
  scientific and requires the existing invalidation/review path.

## Editability and controlled overrides

For the actual method and requested or contract-required formats, retain the
corresponding editable/rebuild sources: live SVG text/vectors, genuine Draw.io
XML, or plotting source with required data/evidence pointers. Retain hybrid
PPTX when requested or contract-required. Do not add unused formats or omit
contract-required surfaces. Keep the Figure Contract as identity/lineage and
the layout contract as geometry; neither becomes another style store.

For a protected style, read and hash the current manifest/template, present
the exact proposed token changes, obtain specific user authorization, and use
the existing `overrides` record (`figure_id`, `token`, `old_value`, `new_value`,
`reason`, `approved_by`). Record the decision/source in `style_report.md`;
never infer approval from this document, an agent label or a filename.

## Rendered acceptance

Compare A (existing style) with B (explicitly selected adaptation) at the same
physical size and export settings, with identical scientific inputs. Apply
[rendered-figure-qa.md](rendered-figure-qa.md),
[accessibility-and-color-standards.md](accessibility-and-color-standards.md)
and the existing contract validators. Inspect exports in the actual requested
or contract-required formats (such as SVG, PDF or PNG); when PPTX is required,
inspect its actual render and native/vector editability as well. A/B comparison
does not itself require additional delivery formats.

Record pass/fail/not-applicable separately for scientific equivalence, text and
arrow survival, hierarchy, final-size readability, alignment/spacing/strokes,
semantic colour plus non-colour encoding, grayscale/colour-vision previews,
unnecessary decoration, venue fit and editability. A pixel diff is diagnostic,
not a quality verdict. Source checks and successful exports do not replace
visual inspection or an author's scientific review.

Reject any scientific mismatch, clipping, substituted glyph, missing arrow,
non-uniform scaling or unexplained rasterization. Missing venue rules, tools
or evidence remain explicitly unverified; do not call the result submission-
ready. A valid locked manifest can be read without alteration; do not claim
the validator itself enforces approval or prevents external file writes.

## Sources and legal notice

Principles were independently adapted, not entire Skills or assets imported:

- [naplesblue/apple-design-skill](https://github.com/naplesblue/apple-design-skill/tree/e81692da299d64b9bf38ae26db2d709fc60c8bf3),
  MIT, copyright (c) 2026 naplesblue: restrained cool neutrals, clear hierarchy,
  spacing and reduced fragmentation. Its glass, UI, font and motion recipes
  are not part of this academic adaptation.
- [2TheFar/apple-inspired-design-skill](https://github.com/2TheFar/apple-inspired-design-skill/tree/f709388017307d8cefcdab4b9bc0f9f54e32bb8e),
  MIT, copyright (c) 2026 2TheFar: task-first design, semantic tokens,
  accessibility, rendered verification and explicit risk reporting.

MIT permission notice for these attributed adaptations:

Copyright (c) 2026 naplesblue
Copyright (c) 2026 2TheFar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
