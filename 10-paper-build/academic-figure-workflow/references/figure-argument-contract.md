# Figure Argument Contract

Use this reference for complex, submission-bound, multi-panel, data-backed, code-backed, or evidence-sensitive figures.

This contract is also the handoff boundary between a paper pipeline and
`academic-figure-workflow`. It is self-contained: a consuming pipeline may use
its own storage format, but it must preserve the meanings below.

## Paper Pipeline Handoff

Before drawing, record the smallest complete input packet:

```text
Figure id:
Target manuscript section:
Primary claim anchor:
Evidence/material sources:
Evidence readiness: unavailable | unreviewed | verified_for_figure
Statistics readiness: not_applicable | unreviewed | verified_for_figure
Panel roles and non-redundant messages:
Target venue and final physical size:
Required editable source and export formats:
Open scientific decisions:
```

- A **claim anchor** is a stable identifier or exact manuscript statement for
  the primary claim the figure is intended to communicate. It is not proof
  that the claim is true.
- An **evidence/material source** is a resolvable reference to the data, code,
  equation, manuscript passage, image, or user-approved fact used by the
  figure. Record provenance and relevant transformations rather than copying
  unrelated private material into the figure package.
- `verified_for_figure` means the source and its interpretation were checked
  for this visual use. It does not promote the scientific claim to supported,
  accepted, or publishable.
- Use `not_applicable` for statistics only when the figure does not make a
  quantitative statistical assertion, and state why.
- If evidence is unavailable or unreviewed, or a required statistical check is
  unreviewed, stop at a specification, storyboard, or clearly marked draft.
  Do not label the figure submission-ready.

## Contract

Before drawing, define:

```text
Figure id:
Target manuscript section:
Main claim and claim anchor:
Evidence hierarchy and material sources:
Evidence/statistics readiness:
Panel roles:
Non-redundant message per panel:
Drawing method:
Editable source:
Export targets:
Open decisions:
```

## Rules

- Every panel, node, arrow, label, plotted value, annotation, or visual element must support a specific claim, method step, comparison, or design decision.
- If two panels communicate the same message, merge them or explain the distinction before drawing.
- For data-backed plots, record the data source, analysis status, statistics or uncertainty status, and whether values are provided or pending.
- For image-based figures, record permitted image processing, scale bars, annotations, and any manipulation or disclosure requirement.
- If the evidence hierarchy is incomplete, stop at a specification or storyboard instead of producing a final-looking figure.
- Visual, packaging, or editability QA must not change the scientific claim's
  review state. Claim support is decided by the relevant research analysis or
  human scientific review, not by this figure workflow.

## Machine-Readable Contract

For new or materially revised complex figures, instantiate
`assets/figure_contract.template.json` as `figure_contract.json`. It is the
single machine-readable identity and lineage record for the figure. Do not
copy style tokens or complete layout geometry into it; reference the locked
style manifest and shared layout contract instead.

Use conditional sections only when applicable:

- data-backed panels declare stable `source`, `display`, `fit`, `statistical`,
  and `sensitivity` population roles when those sets differ;
- each population records its count, selector reference, evidence references,
  and its relationship to the displayed population;
- each display population explains its relationship to rendered rows; only an
  explicit one-to-one relationship permits a mechanical row-count comparison,
  because aggregated plots need not have one mark per research unit;
- uncertainty records the method, meaning, unit of analysis, and prohibited
  inference, or an explicit reason that it is not applicable;
- every meaningful element has one stable ID and one surface binding;
- architecture figures may add nodes, edges, dimensions, evidence references,
  and a protected template baseline;
- rebuild information records the working directory, hashed inputs, expected
  outputs, and either an argv-style command or a manual instruction reference
  for genuinely hand-edited sources;
- a revision that changes populations, exclusions, transformations,
  uncertainty, claims, nodes, edges, or dimensions must list the affected
  outputs in `revision.invalidated_outputs`.

The validator checks consistency and traceability. It cannot decide whether a
scientific method or conclusion is correct.

## Quality Gate

| Gate | Pass condition |
|---|---|
| Claim clarity | The figure can be summarized in one defensible manuscript claim. |
| Panel necessity | Each panel has a non-redundant role. |
| Evidence trace | Every plotted value, label, node, arrow, or annotation traces to data, code, manuscript text, or user-approved facts. |
| Editability | Source files remain editable and text is not unnecessarily outlined. |
| Submission fit | Size, typography, colour, and annotation density fit the target journal or thesis context. |

## Package QA Hook

When maintaining this skills repository or checking a figure package, use:

```powershell
python -X utf8 -B scripts/validate_figure_contract.py --contract figure_contract.json
```

Treat missing editable sources, missing exports, and captions without claim anchors as issues to resolve or explicitly waive.

## Output Packet

```text
Figure package status: specification | storyboard | draft | visually_and_structurally_verified
Figure source file:
Export files:
Caption draft:
Placement recommendation:
Evidence trace:
Related claim anchors:
Evidence/statistics readiness:
Rendered and structural QA summary:
Assumptions:
Manual checks:
Unresolved issues:
```
