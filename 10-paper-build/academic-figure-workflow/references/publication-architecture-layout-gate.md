# Publication Architecture Layout Gate

Use this gate for journal-facing neural-network, workflow, and code-backed architecture figures before drawing or revising the visual layer. It addresses failures that can pass slide-level QA while remaining misleading or unreadable in a manuscript.

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

Prefer one integrated scientific flow plus at most one non-redundant detail inset.

- Do not repeat input, model, and output in both an overview panel and a full architecture panel unless the overview adds a distinct manuscript claim.
- Use an inset to explain a reusable cell or operation rather than redrawing the complete pipeline.
- Allocate the largest area to the main claim and keep implementation detail subordinate.
- A reader should identify input, branch split, fusion, and output within five seconds.

## 5. Architecture Visual Grammar

### Parallel operations

Show a visible fork, parallel lanes, and merge/concatenation. A vertical or horizontal list of boxes without branch edges reads as a sequence and fails this gate.

### Residual connections

Connect the skip path to exact source and add/merge nodes. Put the projection operation on the skip edge when applicable. Avoid decorative rails that float above the network.

### Fusion

Bring branch connectors directly into the fusion node with one arrowhead per incoming edge. Avoid long disconnected arrows or separate line fragments that only appear joined.

### Connectors

- Prefer thin stroked connectors with compact arrowheads for publication figures.
- Reserve filled block arrows for a rare figure-level transition.
- Avoid crossings and text placed on top of connectors.
- Use line style as a redundant semantic cue when colour carries branch meaning.
- On a light canvas, structural connectors must use the manifest's high-contrast foreground colour. Do not use pastel connector colours merely to match module fills.
- Distinguish learned, physical, residual, and auxiliary paths primarily with solid/dashed/dotted style, line width, and a short edge label.
- Render and verify arrow direction. The arrowhead must terminate at the target node.
- Adjacent peer nodes on the same baseline must use a straight connector with explicit `right -> left` anchors. Do not rely on automatic elbow routing for a short horizontal edge.
- When one source feeds two or more branches, use a visible split junction and route from that junction. Do not attach multiple auto-routed edges directly to a large source card.
- Connector segments may sit behind module fills only at their endpoint masks. A visible edge must remain continuous from source boundary to target boundary.
- Use connector-specific z-order: above the canvas/background and below module labels. Do not apply an unconditional `sendToBack()` policy to every edge.

### Junctions and operators

- Junction, fork, add, and merge marks must be native geometry, not font glyphs positioned by eye.
- A dot inside a circle must use two concentric shapes with coincident geometric centres.
- Use `+` only for verified addition. Use an unlabelled junction for a fork or routing point, and label concatenation explicitly.
- For peer blocks with numeric mappings, build a fixed three-slot operator row: left value, native operator/arrow, right value. Do not place the complete mapping in one auto-wrapping text box.
- Peer operator rows must use identical slot bounds and align within 2 px. Keep the operator and both values on one line.

## 6. Module Interior and Grid Contract

Use an 8 px base grid on a 1600 × 900 source canvas unless the project manifest defines an equivalent rhythm.

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

- Peer modules in one processing lane must share height, title region, body region, padding, and vertical alignment unless a documented scientific reason requires a different class.
- Do not repair individual boxes with arbitrary `bodyTop`, title-height, or padding overrides. Select a named `compact`, `standard`, or `detailed` module template.
- A title may use at most two lines. Body copy may not overlap, clip, or visually touch the title region.
- Dense mathematical descriptors must use a structured list, two-column matrix, or aligned rows. Do not compress seven or more items into a centred paragraph.
- A peer row fails when internal whitespace or text fill differs visibly across boxes. Keep peer-card optical fill within about 10% by choosing compatible dimensions and line counts.
- Transformation summaries should use a key-value process table when prose, values, units, and operations would otherwise mix in one paragraph.
- Normalize mathematical notation within one figure: write function arguments with parentheses, for example `log1p(I580)`, `max(I)`, and `sigma(I)`. Avoid mixed forms such as `log1p I580`, `max I`, and `sigma I`.

## 7. Canvas Fill and Output Contract

- The main scientific artwork should occupy at least 90% of the usable panel width and 78% of its usable height, excluding deliberate panel-heading space.
- Whitespace must separate stages or branches; it must not arise from unrelated coordinates or undersized nodes.
- Dual branches should reuse column centres so corresponding transformations align vertically.
- For a 1600 x 900 dual-branch source figure, keep the clear vertical gap between peer branch modules in the 64-88 px range unless the content requires a documented exception.
- Reject an unexplained inter-branch dead zone occupying more than 15% of the usable panel height.
- Prediction/output nodes must be wide enough to keep the quantity and unit readable on one or two intentional lines. Reject narrow output boxes that force `T`, hat marks, parentheses, or units into a vertical stack.
- Regression heads must reserve a single-line title region and a separate body region large enough for every verified operation.

## 8. Anti-Card Gate

Reference-image style migration may reuse colour, corner treatment, spacing, and grouping rhythm, but it must not turn the figure into a dashboard.

Reject or simplify when:

- most nodes sit inside multiple nested rounded containers;
- large cards contain mostly empty space while labels are small;
- repeated panel frames do not encode a scientific boundary;
- badges, pills, or heavy filled arrows imply interface controls;
- decorative containers compete with tensors, branches, or evidence.

Prefer a flat white canvas, restrained semantic tints, one grouping level, and whitespace before adding another frame.

## 9. Publication Text Filter

The publication slide or exported panel must not contain:

- `Figure 1`, the manuscript title, or a caption-like headline;
- repository-verification notes, source paths, QA status, editability instructions, or authoring guidance;
- long method caveats that belong in the caption or Methods section.

Keep this information in speaker notes, manifests, source trace, or the component board. Short scientific labels essential to interpreting an edge or node remain allowed.

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
Five-second reading order: pass/fail
Connector contrast and target arrowheads: pass/fail
Adjacent connectors straight and unobscured: pass/fail
Multi-branch source uses visible split junction: pass/fail
Peer module padding/alignment: pass/fail
Peer operator slots aligned/no wrapping: pass/fail
Scientific notation normalized: pass/fail
Junction geometry centred: pass/fail
Text overlap/clipping: pass/fail
Inter-branch clear gap/dead-zone ratio:
Usable width/height coverage:
Output quantity and unit readable: pass/fail
Remaining issues:
```
