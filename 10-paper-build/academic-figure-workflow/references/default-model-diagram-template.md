# Default Model-Diagram Template

Use this reference for an editable PowerPoint neural-network or model-architecture figure only when no higher-priority visual source exists.

## Precedence

Apply the first available source:

1. a PPTX or template explicitly supplied by the user for the current request;
2. a project-level user-approved model template or locked `style_manifest.yaml`;
3. the bundled `../assets/model-diagram/default-model-diagram-template.pptx`;
4. the ordinary method-selection workflow when PowerPoint is not the requested authoring surface.

Do not let the bundled template override a user reference, a paper-wide semantic-colour lock, or a requested Draw.io-first deliverable.

## Asset Role

The bundled PPTX is a user-refined visual and layout exemplar. It contains two slides:

- slide 1: a publication model figure with an overview flow and a module-detail panel;
- slide 2: an editable component board with semantic colours, module treatments, connector examples, and a publication-size gate.

The asset is not a scientific source. Its example spectrum, dual-branch structure, Inception blocks, physical descriptors, dimensions, operations, and temperature output belong to the originating project.

Never carry the following into a new project without evidence:

- `Dual-branch`, `InceptionTime`, or two Inception blocks;
- 520–680 nm, 256 positions, 16 channels, or any other example dimension;
- seven physical descriptors, 580/610 FIR terms, or fold-local standardization;
- global mean/max pooling, 32 + 8 fusion, dropout 0.15, or temperature regression;
- the example caption, source paths, figure number, or panel wording.

## Clone/Edit Contract

Treat the PPTX as a source deck rather than rebuilding its appearance from screenshots or hard-coded approximations.

1. Copy the bundled PPTX into a task-scoped temporary workspace.
2. Inspect and render both source slides.
3. Create a frame map that classifies each inherited object as `keep`, `rewrite`, `replace`, or `delete`.
4. Duplicate the required source slides and edit inherited objects in place.
5. Preserve native PowerPoint geometry, text editability, masters, layouts, theme parts, object grouping, and connector semantics.
6. Replace speaker notes with the target figure caption and `[Sources]` block.
7. Preserve the component board unless the user explicitly requests a publication-slide-only output; when omitted, record the reduced editability surface in the manifest.
8. Export a versioned copy. Never overwrite the bundled asset.

Use the presentation template-following workflow for inspection, frame mapping, editing, theme preservation, and fidelity QA.

## Reusable Visual Grammar

Preserve these qualities unless a higher-priority project style overrides them:

- white 1600 × 900 canvas;
- dark navy structural ink and arrowheads;
- Arial typography with a clear title, stage-label, tensor-label, and annotation hierarchy;
- flat pastel semantic fills, no gradients, and no decorative shadows;
- blue for measured/input information, green for preprocessing, pale yellow for constructed features, lilac for learned model stages, purple for physical features, blue-purple composition for fusion, and pink for prediction/output;
- one main left-to-right reading path, with secondary branches aligned beneath or above corresponding stages;
- compact but stable peer gaps, consistent module padding, and strong usable-canvas coverage;
- straight connectors between adjacent peer stages; elbow routes only for branch, residual, or cross-lane connections;
- solid dark lines for learned paths and dark dashed lines for engineered/physical paths;
- native centred junction and addition geometry instead of font symbols positioned by eye;
- publication artwork on slide 1 and reusable/editing components on slide 2.

## Tensor and Vector Grammar

For one-dimensional spectral or temporal tensors:

- ribbon width represents sequence length `L`;
- visible stack depth represents channel count `C`;
- batch is normally omitted;
- equal `L` values must use equal ribbon width;
- when only representative sheets are drawn, state the exact channel count in the adjacent label.

For vectors:

- horizontal strip length represents feature dimension `D`;
- small vectors may show every cell;
- large vectors may use grouped cells, but the exact dimension must remain explicit;
- concatenation must preserve visible component proportions when practical, for example a `32 + 8` split;
- regression or projection should visibly contract or expand the vector only when the verified dimensions change.

For image-like tensors, map plane width/height to spatial dimensions and stack depth to channels. Do not reuse one-dimensional ribbon geometry when it would misrepresent `(C,H,W)` data.

## Layout Lessons Locked from the User Refinement

- Route a residual path above the main lane without crossing the input title or hiding behind a tensor block.
- Keep the residual projection label, exact dimensional mapping, tensor stack, and addition endpoint visually connected.
- Place regression operations in a dedicated annotation region rather than compressing them into the tensor title.
- Reserve enough width for the final output quantity and unit; do not stack the unit vertically.
- Align the physical branch under the corresponding spectral stages and reuse column centres so the canvas feels filled rather than scattered.
- Keep the main stage labels close to their tensors and prevent connector lines from crossing label regions.
- Preserve a clean panel divider and a separately readable module-detail panel.

## Scientific Adaptation

Before editing, derive a verified architecture contract from code, equations, model summaries, or manuscript evidence:

```text
Input representation:
Preprocessing:
Main stages and exact dimensions:
Parallel branches:
Residual/skip connections:
Pooling or aggregation:
Fusion rule:
Prediction head:
Output quantity and units:
Detailed module selected for panel (b):
Evidence anchors:
```

Delete unsupported template branches instead of filling them with plausible-looking modules. Add a new branch only when the source evidence requires it.

## Template QA

In addition to the normal architecture and PPT QA, verify:

- every example-specific label and source has been replaced or intentionally retained with evidence;
- source-slide structure was cloned rather than visually reconstructed;
- theme parts and master/layout relationships remain intact;
- object names are unique and meaningful after adaptation;
- tensor and vector geometry agrees with the verified dimensions;
- residual, skip, branch, merge, add, and concatenate semantics are correct;
- connectors remain dark, continuous, unobscured, and attached to the intended endpoints;
- no stage title, dimension label, operation note, or output unit overlaps;
- slide 1 remains publication-clean and slide 2 remains an editing surface;
- the final manifest records the bundled template path, template hash, intentional deviations, caption path, editability, and source trace.

## Bundled Files

- `assets/model-diagram/default-model-diagram-template.pptx`: editable two-slide template.
- `assets/model-diagram/default-model-diagram-template.json`: provenance, checksum, editability, and locked-template metadata.
