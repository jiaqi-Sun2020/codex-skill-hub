# Figure content and final-PDF readability

Local original guidance added 2026-11-13; covered by the local-material notice in
[LICENSE](../LICENSE). Apply when a figure carries a method or result. The
[entrypoint](../SKILL.md#source-and-action-boundary) owns the read-only boundary:
inspection and recommendations do not authorize redrawing, compilation or research
execution. Return findings in the existing report, not a separate design audit.

Contents: [correspondence](#scientific-content-and-text-correspondence),
[evidence](#plotted-evidence), [readability](#final-pdf-readability),
[reporting](#finding-and-completion).

## Scientific content and text correspondence

Read the figure and its caption, then follow the manuscript's reference to it.
For elements carrying the method or claim, check in both directions:

- **Figure to prose:** locate the meaning of each consequential module, variable,
  state, branch, arrow, operator, input/output and comparison. Core operations
  and relations need a recoverable explanation in the body, possibly through
  an existing equation/algorithm and explicit reference. A central method step
  shown only in the figure is a reporting gap.
- **Prose to figure:** confirm that the cited panel actually shows the stated
  operation, comparison or pattern. Check branch operands, arrow direction,
  update order, conditions and model scope against
  [technical consistency](technical-consistency.md#cross-representation-trace).
- **Abstraction:** a schematic may omit detail when the omission is intelligible;
  it must not imply a different computation. One box may summarize several
  equations, and multiple labels may denote documented views of one object.
  Correspondence means recoverable meaning, not one box per equation or forced
  merging of different objects.

Captions can define units, mark shapes, colors and local abbreviations; prose need
not repeat each plotted value or decorative element. If a needed explanation
already exists in the caption, withdraw an allegation of total absence. Retain a
narrower placement/body-explanation concern only when the missing connection
affects understanding of the method or claim. An unreadable or unavailable panel
is unassessed, not evidence of a contradiction.

For diagrams and circuits, check mathematical type as well as labels: a feature
vector is not automatically its normalized state, an operator is not its output,
and an approximate decomposition need not mean applying both sides in sequence.
Look for connections, control branches or condition markers that change the
stated computation. Do not infer a new operation from a purely decorative arrow.

## Plotted evidence

Use [internal consistency](method-checks.md#internal-consistency) for point
provenance, aggregation, sample counts and uncertainty. In the figure itself,
check metric/units, axis scales, baseline/comparator, legend mapping and caption
against those definitions. Reconcile any numerical example with the stated
mapping; missing observations and elapsed intervals are not interchangeable.

Separate a visible pattern from its proposed cause and from a downstream
performance claim. Do not infer an exact value from an indistinct image, statistical
significance from error-bar appearance, or comparable runs from a common label.
Report a misleading scale, clipped error bar or omitted condition only with the
specific information or inference it changes.

## Final-PDF readability

Judge the supplied paper at its intended placed size: inspect the whole page and
use a crop/zoom to diagnose small details. A large standalone preview, source
font size or raster DPI alone does not establish readability after placement.
If only the source image is available, limit findings to it and mark final-layout
readability unassessed.

Use an author-selected reference figure from an identifiable PDF when available.
Compare like roles (axis title, tick, legend, module label, equation) at their
actual placed scale. A prior measured size is not a new measurement. The reference
is project-specific: do not hard-code its figure number, font sizes, model names
or layout as a standard for other papers. Without a supplied benchmark, assess
legibility from the available layout and state the basis instead of inventing one.

| Inspect | Decision-relevant check |
|---|---|
| Type and scale | Are comparable labels readable at the intended column/page size? Source font sizes can match while placed sizes differ. |
| Math | Can readers distinguish boldface, hats, subscripts, norm indices and similar letters? Prefer a layout remedy to shrinking all symbols into a box. |
| Points, lines and error bars | Inspect dense as well as isolated regions. Larger points can hide evidence; thin lines and overlapping error bars can obscure it. |
| Legend and axes | Are groups and axes identifiable without guessing? Check label direction, proximity, collisions and cropping, including uncertainty endpoints. |
| Color and shape | Can meaningful groups be distinguished? Suggest a redundant shape or line encoding when useful, without prescribing a palette or adding clutter. |
| 3D geometry | Do depth, perspective or occlusion hide the relationship? A third dimension should carry interpretable information; it is not inherently better than 2D. |
| Schematics | Are arrowheads, gate borders, control markers, ellipses and crossings unambiguous? Layout must not imply an extra branch or operation. |
| Space and clipping | Does whitespace force important content to become too small, or does tight cropping remove labels/data? Do not maximize density at the expense of meaning. |

Layout recommendations should preserve the stated data, operators and conditions.
A proposed readability fix must not silently hide points, shorten error bars,
change an axis interpretation or simplify away a necessary branch. The review
diagnoses and recommends; it does not implement those changes.

## Finding and completion

Name the panel/element, visible problem and consequence. Distinguish scientific
contradiction, missing explanation, local readability and an unassessable check.
Link affected prose or equations rather than reporting one issue per occurrence.

A completion condition should say what a reader must be able to identify or
compare in the final layout and which meanings must remain consistent. Do not
declare a whole figure clear because one enlarged crop is readable, or escalate
every aesthetic preference into a scientific concern.
