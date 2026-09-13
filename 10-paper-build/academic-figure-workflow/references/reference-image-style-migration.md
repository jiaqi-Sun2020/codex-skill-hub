# Reference-Image Style Migration

Use this reference when one or more supplied academic figures define the desired visual language. It extends the existing evidence, publication, accessibility, and editability protocols; it does not replace them.

## Objective

Convert observable design choices into reusable style tokens. Do not copy the reference figure's scientific content, distinctive arrangement, logos, icons, annotations, or data. The result is a paper-wide system that can be applied consistently to new diagrams, plots, and PPT components.

## Reference Roles

Assign every reference exactly one primary role:

- `primary_style`: global authority for typography, palette character, strokes, spacing, and density;
- `chart_style`: chart-specific axes, markers, legends, grids, and statistical annotations;
- `architecture_style`: blocks, connectors, feature maps, groups, and architecture semantics;
- `layout_inspiration`: composition cue only; it cannot override global tokens.

When roles are not supplied, ask only if the choice would materially change the output. Otherwise select the clearest global reference as provisional `primary_style` and record the assumption.

## Extraction Pass

Inspect each reference at its native resolution where possible. Record observed, inferred, and unresolved values separately.

Extract at least:

- primary, secondary, accent, neutral, background, and text colours;
- colour-to-semantic-role mappings;
- font category and available family candidates;
- title, body, annotation, panel-label, axis-label, tick, and legend hierarchy;
- stroke widths, connector widths, dash patterns, arrowheads, border colours, and corner radii;
- flat/gradient/pattern fill rules and shadow policy;
- panel gaps, internal padding, outer margins, alignment rhythm, and visual density;
- axis spines, ticks, grids, legends, markers, lines, bars, scatter points, uncertainty bands, and statistics;
- architecture grammar for input, output, encoder, decoder, attention, fusion, skip, residual, and uncertainty modules;
- use of 2D, pseudo-3D, stacked maps, repeated blocks, and grouping containers.

Use colour sampling only to estimate tokens. Prefer stable rounded hex values over noisy pixel-by-pixel colours. Mark uncertain samples as provisional.

## Conflict Resolution

Resolve conflicts in this order:

1. publication legibility, data integrity, accessibility, and evidence constraints;
2. explicit user instruction;
3. `primary_style`;
4. domain reference for the relevant figure type;
5. existing locked project token;
6. conservative publication default.

Do not silently replace a locked token. Record every conflict in `style_report.md` with:

```text
Token:
References in conflict:
Observed alternatives:
Selected value:
Reason:
Status: locked/provisional/unresolved
```

## Transfer Rules

- Transfer hierarchy, rhythm, palette relationships, geometry language, and semantic conventions.
- Adapt density and font size to final insertion dimensions rather than copying source pixels.
- Keep the user's terminology and architecture truth even when the reference uses different module names.
- If a reference assigns the same colour to two incompatible semantics, split the roles using lightness, pattern, marker, or line-style redundancy.
- Preserve grayscale and colour-blind interpretation with direct labels or redundant encodings.
- Treat raster photographs and microscopy as content assets, not style tokens.

## Required Outputs

Create:

```text
figures/style/
├── reference_images/
├── style_manifest.yaml
└── style_report.md
```

`style_report.md` must contain:

1. reference inventory and assigned roles;
2. observable visual-language summary;
3. accepted tokens and confidence;
4. conflicts and resolutions;
5. rejected non-transferable content;
6. accessibility and final-size adjustments;
7. lock status and approved overrides;
8. unresolved issues.

The report explains decisions; the manifest is the machine-readable source of truth.

## Multi-Reference Example

```yaml
references:
  reference_01:
    role: primary_style
  reference_02:
    role: chart_style
  reference_03:
    role: architecture_style
```

If the styles conflict, `primary_style` controls the shared token unless a scientific or accessibility rule requires a documented adjustment.

## QA

- Verify that no reference text, data, scientific labels, or exact panel arrangement was copied unintentionally.
- Compare at least one architecture component, one chart sample, and one panel label against the manifest.
- Confirm that all provisional tokens are identifiable and that locked tokens have explicit provenance.
- Render at final insertion size; a visually similar full-screen preview is not sufficient.
