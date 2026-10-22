# Publication Architecture Layout Gate

Use this gate for journal-facing neural-network, workflow, and code-backed architecture figures before drawing or revising the visual layer. It addresses failures that can pass slide-level QA while remaining misleading or unreadable in a manuscript.

Scientific fidelity, unambiguous relationships, no information-obscuring overlap
and final-size readability are hard requirements. Anchor directions, grouping,
grid rhythm and line counts below are layout defaults, not scientific gates.
Use a different layout when the actual reading direction, content or medium
benefits; briefly explain the choice in the existing layout/QA record. This
does not unlock an approved project template or waive the hard requirements.

## 1. Final-Size Contract

Declare before layout:

```text
Canvas width:
Target manuscript width: 89 mm / 183 mm / venue-specific
Scale factor: target width / canvas physical width
Smallest source text:
Smallest final-size text:
Minimum final-size line weight:
```

Compute rather than guess:

```text
final text pt = source text pt × scale factor
final line pt = source line pt × scale factor
```

Reject the layout when essential text falls below the selected publication standard after scaling. Increasing the full-screen zoom is not a substitute for final-size QA. When the canvas is a 1600 px PowerPoint slide at 96 dpi, treat it as about 16.67 inches wide for this calculation.

## 2. Scientific Flow Before Visual Flow

Derive the graph from code, equations, data transformations, or manuscript evidence before arranging blocks.

For a contract-backed architecture figure, assign every node and edge a stable
ID and at least one evidence reference. Record tensor or vector dimensions
when the source defines them; use an explicit unresolved state rather than a
plausible-looking inferred dimension. Every edge endpoint must resolve to a
declared node. A change to a node, edge, dimension, branch, merge, or residual
relationship is a scientific change and invalidates dependent exports,
captions, and PPT surfaces until rebuilt and reviewed.

- Split branches at the point where their real transformations diverge.
- Do not place branch-specific features downstream of a shared preprocessing block unless the source implements that shared dependency.
- Distinguish raw measurements, normalized tensors, engineered features, learned features, and predictions.
- Label dimensions only when verified.
- Show residual and skip connections with explicit, connected origins and destinations.
- Use edge labels for transformations that would otherwise be ambiguous.

For code-backed diagrams, create a compact trace:

```text
node or edge -> file/class/function/config -> verified meaning
```

## 3. Data-Like Visuals

Curves, heatmaps, spectra, microscopy panels, and prediction traces look evidential even when used decoratively.

Priority:

1. use a real, traceable representative sample selected by a documented rule;
2. otherwise label the asset visibly as `schematic`, `illustrative`, or an equivalent manuscript term;
3. never present an invented trace with normal experimental axes as if it were measured data.

Record sample selection, transformations used only for display, and source location outside the figure canvas.

## 4. One Main Reading Path

Prefer an integrated scientific flow and only detail insets that add distinct information; the scientific argument, not a fixed inset count, determines the composition.

- Do not repeat input, model, and output in both an overview panel and a full architecture panel unless the overview adds a distinct manuscript claim.
- Use an inset to explain a reusable cell or operation rather than redrawing the complete pipeline.
- Allocate the largest area to the main claim and keep implementation detail subordinate.
- Check whether a reader can locate input, branch split, fusion and output promptly; a timed reading test is diagnostic, not a universal acceptance threshold.

## 5. Architecture Visual Grammar

### Parallel operations

Make parallel relationships explicit with source-backed edges and labels; a
visible fork, lanes and merge are useful defaults where those operations exist.
Do not invent a merge. A list that misleadingly depicts parallel operations
as a sequence fails regardless of its orientation.

### Residual connections

Connect the skip path to exact source and add/merge nodes. Put the projection operation on the skip edge when applicable. Avoid decorative rails that float above the network.

### Fusion

Bring branch connectors directly into the fusion node with one arrowhead per incoming edge. Avoid long disconnected arrows or separate line fragments that only appear joined.

### Connectors

- Prefer thin stroked connectors with compact arrowheads for publication figures.
- Reserve filled block arrows for a rare figure-level transition.
- Avoid crossings and text placed on top of connectors.
- Use line style as a redundant semantic cue when colour carries branch meaning.
- On a light canvas, default to the manifest's high-contrast foreground colour for structural connectors. Other approved semantic colours are valid if contrast and path meaning remain clear; do not use faint pastel connectors merely to match module fills.
- Distinguish learned, physical, residual, and auxiliary paths primarily with solid/dashed/dotted style, line width, and a short edge label.
- Render and verify arrow direction. The arrowhead must terminate at the target node.
- For adjacent nodes in a left-to-right lane, prefer straight connectors with explicit `right -> left` anchors. Other directions or elbow routes are valid when their endpoints, direction and non-obscuring path are clear at final size.
- For multiple branches, prefer an explicit split junction; direct source edges are also valid when their origins and separate targets are unambiguous. Reject ambiguous routing, not a particular junction style.
- Connector segments may sit behind module fills only at their endpoint masks. A visible edge must remain continuous from source boundary to target boundary.
- Keep connectors visible without obscuring labels; above the background and below labels is a useful z-order default. Do not apply an unconditional `sendToBack()` policy to every edge.

### Junctions and operators

- Prefer native/vector geometry for junction, fork, add and merge marks. Other reliable representations are allowed when their centres, meaning and final rendering are verified.
- For a dot inside a circle, verify coincident visual centres; two concentric shapes are one implementation, not a required object count.
- Use `+` only for verified addition. Use an unlabelled junction for a fork or routing point, and label concatenation explicitly.
- For repeated numeric mappings, a three-slot operator row is a useful template; use another representation when it better expresses the verified mapping without accidental wrapping.
- Align comparable mappings consistently at final size. A 2 px tolerance is a template starting point, not a scientific requirement.

## 6. Module Interior and Grid Contract

The following is an example starter rhythm for the bundled 1600 × 900 template, not a required canvas, grid or universal gate. Resolve actual size and content first.

```text
compact gap: 24 px
standard module gap: 32 px
major stage gap: 40 px
peer alignment tolerance: 2 px
horizontal inner padding: 14 px
top inner padding: 10 px
bottom inner padding: 12 px
title region: 30 px
title-to-body gap: 6 px
```

- Prefer consistent height, padding and alignment for comparable modules. Content length, reading order or medium can justify a local layout exception; it need not invent a scientific distinction.
- Prefer reusable module treatments to arbitrary local fixes; no new named-template system is required. Permit a purposeful local exception when it improves the current scientific layout.
- Keep titles and body readable without overlap or clipping; line counts follow actual content and final size.
- For dense mathematical descriptors, prefer a structured list, matrix or aligned rows when these improve scanning. Item count alone (including seven or more) does not determine the layout; reject ambiguity, overlap or unreadable final-size text instead.
- Compare peer optical weight as a diagnostic. A different fill ratio is not itself failure and must not force padding or invented text merely to match a percentage.
- Transformation summaries should use a key-value process table when prose, values, units, and operations would otherwise mix in one paragraph.
- Keep mathematical notation consistent with verified source definitions. Parenthesized function arguments are a useful default, not permission to change an operator, symbol or scientific meaning to fit a visual convention.

## 7. Canvas Fill and Output Contract

- Record usable-canvas coverage when helpful; do not impose 90% width/78% height as universal minima or enlarge scientific objects just to meet them.
- Use whitespace to separate stages or branches; assess unexplained gaps against readability rather than forcing uniform canvas fill.
- Dual branches should reuse column centres so corresponding transformations align vertically.
- For the 1600 x 900 template, 64–88 px can be a useful initial branch gap. Adapt it to the actual labels, objects and publication width.
- Inspect unexplained dead zones qualitatively; a 15% ratio is a diagnostic, not a reason to change correct scientific topology.
- Keep output quantities, notation and units unambiguous and readable. Prefer one or two intentional lines; another arrangement is valid if it preserves meaning and final-size readability.
- Prefer separate title and body regions for regression heads; allow wrapping or another organization when every verified operation remains clear without clipping or overlap.

## 8. Anti-Card Gate

Reference-image style migration may reuse colour, corner treatment, spacing,
and grouping rhythm. Avoid dashboard-like ornament that has no scientific
role; do not remove a genuine source-backed interface or grouping merely to
match this visual preference.

Reject or simplify when:

- most nodes sit inside multiple nested rounded containers;
- large cards contain mostly empty space while labels are small;
- repeated panel frames do not encode a scientific boundary;
- badges, pills, or heavy filled arrows imply interface controls;
- decorative containers compete with tensors, branches, or evidence.

Prefer a flat white canvas, restrained semantic tints, one grouping level, and whitespace before adding another frame.

## 9. Publication Text Filter

Use the sole artwork-versus-caption rule in
[figure-caption-contract.md](figure-caption-contract.md#artwork-versus-caption).
Do not suppress necessary scientific labels or schematic/evidential distinctions
under a blanket request to remove footnotes.

## 10. PPT Separation

- Slide 1 may be the clean publication panel and must pass this gate.
- Slide 2 may be a component board with editing guidance, larger labels, and editability metadata.
- Do not judge the component board as final artwork or export it as the manuscript figure.
- Preserve the original deck when a major redesign is requested; write a versioned output unless the user explicitly requests in-place replacement.

## Required QA Result

```text
Target width and scale factor:
Smallest source/final text:
Real or schematic data-like assets:
Branch fidelity checked against:
Parallel structure visually explicit: yes/no
Residual endpoints explicit: yes/no/not applicable
Redundant overview removed or justified: yes/no
Publication-only text filter: pass/fail
Reading order (qualitative, not a timed threshold): clear/unclear
Connector contrast and target arrowheads: pass/fail
Connector anchors/routing clear and unobscured: pass/fail
Multi-branch origins and targets explicit: pass/fail/not applicable
Peer module padding/alignment or justified exception: pass/fail
Peer mappings aligned/no accidental wrapping: pass/fail/not applicable
Scientific notation normalized: pass/fail
Junction geometry centred: pass/fail
Text overlap/clipping: pass/fail
Inter-branch clear gap/dead-zone ratio:
Usable width/height coverage:
Output quantity and unit readable: pass/fail
Remaining issues:
```
