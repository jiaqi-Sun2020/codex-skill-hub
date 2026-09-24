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

```bash
python scripts/figure_package_check.py --package figures --captions captions.md --output-md figure_package_check.md
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
