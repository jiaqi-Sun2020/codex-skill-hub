---
name: academic-figure-workflow
description: "Plan, create, revise, assemble, validate, caption, and package publication-ready academic figures. Use for reference-image style migration, paper-wide style locking, final-size architecture or plot review, legend/marker/font cleanup, SVG/Draw.io neural-network diagrams, real-data plots, multi-panel figures, editable PowerPoint figure kits, default model-diagram templates, detailed panel explanations inside PPT, plot-to-PPT scale control, evidence trace, and rendered QA. Chinese triggers include 论文作图, 参考图风格, 论文架构图审核, 默认模型图模板, 沿用模型图模板, 最终尺寸可读性, 图例混乱, 标记太多, 字体混乱, 简化图例, PPT图表缩放, 神经网络架构图, 实验数据绘图, 图注, 所有图的图注, PPT详细图注, 逐图解释, 可编辑PPT, 论文图片PPT, 清理预览文件. English triggers include reference-image style, default model-diagram template, model figure template, final-size plot review, legend cleanup, marker cleanup, typography cleanup, detailed panel annotations, plot-to-PPT scale, figure caption, clean figure package, neural network architecture, editable PowerPoint, figure assembly, and component board."
---

# Academic Figure Workflow

Use this skill for academic and thesis figures. Choose the method by scientific claim, evidence, editability, reproducibility, and final publication size. For data-backed plots, inspect the data before choosing the chart and prepare the paragraph-level figure argument needed by the manuscript.

## Boundaries

Do:

- Plan figure claims, panels, captions, source files, exports, and source trace.
- Abstract visual design language from reference images without copying their scientific content or layout verbatim.
- Create SVG mechanism figures, editable Draw.io engineering or neural-network diagrams, reproducible Matplotlib figures, and editable PowerPoint figure kits.
- Validate every visual element against evidence, data, code, manuscript text, or user-approved facts.

Do not:

- Invent data, units, uncertainty, mechanisms, system modules, results, labels, or visual evidence.
- Use AI image generation without the explicit gate in [ai-image-generation-gate.md](references/ai-image-generation-gate.md).
- Call a figure or PPTX submission-ready when labels overlap, source files or traces are missing, or vector/native editability was not verified.
- Flatten a complete editable figure or slide to one raster image unless the user explicitly requests a raster-only deliverable.

## Paper Pipeline Integration

When this skill is called from `latex-paper-build-skill`, treat it as an
optional evidence-figure lane, not a mandatory step for every manuscript.

- Read [figure-argument-contract.md](references/figure-argument-contract.md)
  for the incoming claim, evidence, analysis readiness, panel roles, venue,
  final size, and requested outputs.
- Use `05_manuscript_zh/figures/` as the single figure root for that generated
  pipeline. Do not create a second root-level `figures/` or duplicate figure
  packages under reports or submission folders.
- In standalone use, keep supporting a user-selected figure root and otherwise
  default to `<project>/figures/`; this skill does not depend on the LaTeX
  pipeline.
- Own figure method selection, editable sources, style, exports, captions,
  evidence trace, and rendered QA. The LaTeX skill owns placement,
  cross-references, compilation, and manuscript prose that interprets the
  figure.
- Accept data and statistical findings from `data-analysis`; do not repeat or
  silently upgrade their scientific review state.
- If the handoff lacks verified evidence needed by the figure, deliver only a
  specification, storyboard, or marked draft. Figure QA never proves the
  underlying scientific claim.
- Create package and style directories only when figure work is applicable;
  do not populate empty placeholders for figure-free papers.

## Intake

Collect:

- figure purpose, target manuscript section, audience, language, and scientific claim;
- source facts: manuscript text, evidence table, codebase, data files, equations, or rough sketch;
- reference images and their roles: `primary_style`, `chart_style`, `architecture_style`, or `layout_inspiration`;
- existing `figures/style/style_manifest.yaml` and whether its tokens are locked;
- target venue and stage: draft, thesis insertion, submission, accepted artwork, or supplement;
- requested source/export formats and final physical size;
- for PPTX: assembly mode, slide size, panel plan, and required editability level;
- AI image-generation permission when relevant.

Before execution, report only material gaps:

```text
Required or high-value materials:
Missing materials:
Can proceed without them: yes/no
Fallback if unavailable:
```

If key evidence is missing, stop at a specification, storyboard, style report, or provisional template.

## Method Selection

| Figure need | Default method |
|---|---|
| Reference images define visual language | Style migration -> project `style_manifest.yaml` and `style_report.md` |
| Mechanism or conceptual schematic | SVG source plus SVG/PDF/PNG exports |
| Workflow, module, system, model, or neural-network architecture | Editable Draw.io source plus SVG/PDF/PNG exports |
| Quantitative plot or multi-panel comparison | Data-validation flow plus reproducible Matplotlib source and SVG/PDF/PNG |
| Editable paper-figure canvas or reusable kit | Hybrid PPT assembly: native shapes/text + SVG + raster only where unavoidable |
| Photorealistic or illustrative bitmap asset | OpenAI image generation after explicit confirmation |
| Simple numeric comparison | Native manuscript table/chart when scientifically sufficient |

Read [figure-method-selection.md](references/figure-method-selection.md) when more than one method is plausible.

## Core Contracts

1. Evidence determines scientific content. Preserve data, populations, units, formulas, topology, dimensions, uncertainty and claim boundaries; unknown facts remain unknown. A visual-only edit cannot silently change science.
2. Appearance comes from the existing project Style Manifest. Use [figure-style-manifest.md](references/figure-style-manifest.md) for precedence, locks and encoding scope. Current specific authorization overrides only its stated scope, never the protected baseline by implication.
3. Make the intended comparison readable at its actual final size. Declare colour meaning per figure/comparison; use meaningful non-colour cues where needed. Role colours and process-stage colours must not compete for the same fill.
4. Keep a usable editable/rebuild source and necessary evidence trace. Choose formats by the requested method: live SVG text/vectors, genuine Draw.io XML, reproducible data/plot source, or hybrid PPT as applicable. PowerPoint convenience never justifies altered science.
5. Deliver only applicable surfaces. A simple local preview/revision does not require PPT, a component board or visible explanations. Use [figure-caption-contract.md](references/figure-caption-contract.md) as the sole artwork-versus-caption rule; required decoding information must remain accessible.
6. For new or materially revised complex data-backed/code-backed/architecture work, multi-surface delivery or submission-bound figures, use the existing Figure Contract for identity, evidence, populations, bindings and invalidation. A local revision may reuse a valid existing record rather than create a second state. Bind actual surfaces, not imaginary deliverables. Retain source/display/fit/statistical/sensitivity distinctions when they differ.
7. Protect approved/user-edited assets and selected revisions. Do not infer approval from names, timestamps, hashes or a new reference. Follow [figure-package-hygiene.md](references/figure-package-hygiene.md) for storage and approval-bound cleanup; unknown files are not disposable.
8. Report scientific, structural and visual checks separately. Export, XML validity, hashes and script exit codes do not establish visual quality or scientific truth. Missing evidence/venue checks remain draft or unverified.

## Workflow Router

1. Establish claim, current scope, source facts, actual medium/final size and requested outputs. Reuse confirmed decisions; ask only about a gap that changes the next action.
2. For complex/code/data/submission work, read [figure-argument-contract.md](references/figure-argument-contract.md). Do not repeat domain analysis or run new experiments merely because figure evidence is missing.
3. Resolve appearance through [figure-style-manifest.md](references/figure-style-manifest.md). When images define style, also read [reference-image-style-migration.md](references/reference-image-style-migration.md). Reuse the single `<figure-root>/style/style_manifest.yaml`.
   - Only when the user explicitly selects Apple-inspired academic styling, read [apple-inspired-academic-figure-style.md](references/apple-inspired-academic-figure-style.md), even without reference images. A generic clean/minimal request does not select it. Preserve locked manifests and approved/user-edited templates unless the specific override is authorized and recorded with its reason. No default, science or QA gate changes.
   - Without a higher-priority style, keep the original paper1 diagram language in [default-model-diagram-template.md](references/default-model-diagram-template.md): white ground, navy structure, purposeful soft fills, modest corners and small open arrows. These are overridable preferences, not universal scientific rules or a requirement to author every figure in PPT.
4. Select only the applicable method references:
   - Data: [data-visualization-advisor.md](references/data-visualization-advisor.md); Matplotlib: [nature-matplotlib-protocol.md](references/nature-matplotlib-protocol.md), [multi-panel-layout-patterns.md](references/multi-panel-layout-patterns.md), [chart-type-visual-standards.md](references/chart-type-visual-standards.md). Budget/mask/threshold advice applies only to those questions; it is not an instruction to conduct missing experiments.
   - SVG/Draw.io: [svg-and-drawio-diagrams.md](references/svg-and-drawio-diagrams.md), and for code/model diagrams [drawio-engineering-diagram-standards.md](references/drawio-engineering-diagram-standards.md). For journal-facing architecture also read [publication-architecture-layout-gate.md](references/publication-architecture-layout-gate.md). Layout numbers are template starting points, not universal gates.
   - Image plates: [image-panel-integrity.md](references/image-panel-integrity.md). AI bitmaps still require the explicit permission in [ai-image-generation-gate.md](references/ai-image-generation-gate.md).
5. When PPT/PPTX or a component kit is requested, read [pptx-figure-assembly.md](references/pptx-figure-assembly.md). Use the bundled model PPTX only under [default-model-diagram-template.md](references/default-model-diagram-template.md) precedence; never carry its example science into a new project. Keep native objects, SVG and unavoidable raster distinguishable.
6. For resized/fixed-slot plots read [plot-to-ppt-scale-contract.md](references/plot-to-ppt-scale-contract.md); for legends/markers/typography read [plot-annotation-and-typography-contract.md](references/plot-annotation-and-typography-contract.md). One geometry record and actual final-size rendering govern scaling, not source font values alone.
7. Apply [figure-caption-contract.md](references/figure-caption-contract.md); add notes/boards/visible explanations only for the actual delivery scope. Complex contract-backed PPT surfaces retain the existing binding/hash checks when declared.
8. Verify current official venue requirements only when relevant using [publisher-visual-source-map.md](references/publisher-visual-source-map.md). Apply [publication-visual-standards.md](references/publication-visual-standards.md), [export-and-editability-standards.md](references/export-and-editability-standards.md), [accessibility-and-color-standards.md](references/accessibility-and-color-standards.md) and [rendered-figure-qa.md](references/rendered-figure-qa.md). Inspect actual exports for clipping, glyphs, connectors, proportion, grayscale and final-size readability; retain previews until reviewed.
9. Validate the applicable Figure Contract with `scripts/validate_figure_contract.py`, passing the previous contract for revisions. Invalidate dependent outputs when scientific inputs/meaning change. Keep Style Manifest as appearance and the layout contract as geometry, not competing current states.
10. Deliver requested artwork, usable source, necessary caption/evidence pointers, actual checks and unresolved issues. Cleanup is a separate classified/approved action under the hygiene reference; a successful build is not visual acceptance.

## Validation

Before finishing, check only the formats, data and records actually used or
required by the applicable contract. Do not create extra deliverables merely
to satisfy this checklist; a missing required item remains unresolved, not
not-applicable.

- confirm method, panel claims, and evidence trace;
- validate the style manifest when present or required, and confirm semantic-colour consistency;
- inspect editable sources and rendered previews at intended final size;
- check overlap, clipping, font consistency, line weight, contrast, grayscale and colour-blind interpretation;
- check that legends, direct labels, markers, annotations, and fonts follow one declared visual grammar, with no redundant method identities or undefined decorative markers;
- for SVG/Draw.io delivery, verify SVG text remains editable and Draw.io files are genuine editable XML as applicable;
- for data-backed figures, verify data columns, units, sample counts, missing values, transformations, uncertainty, and axis scales against source data;
- for PPTX, verify openability, slide bounds, independent objects, panel labels, aspect ratios, vector/raster classification, source trace, and documented fallbacks;
- for requested visible PPT explanations, verify one native editable section per panel and consistency with caption, notes, source and data; verify all surfaces explicitly required by an applicable Figure Contract;
- list unresolved scientific, data, style, font, export, and editability issues separately.

## References

- <a href="Ten%20Simple%20Rules%20for%20Better%20Figures.pdf">Ten Simple Rules for Better Figures</a>: CC0 PLOS reading on figure purpose, audience, medium, captions, and integrity; a general design reference, not a venue requirement, scientific-evidence source, or replacement for the workflow's contracts and QA.
- [figure-style-manifest.md](references/figure-style-manifest.md): project style schema, precedence, locking, overrides, and directory contract.
- [reference-image-style-migration.md](references/reference-image-style-migration.md): reference analysis, style-token extraction, conflict resolution, and non-copying rules.
- [apple-inspired-academic-figure-style.md](references/apple-inspired-academic-figure-style.md): optional, independently adapted academic styling, read only after an explicit Apple-inspired selection; it preserves the existing Style Manifest, scientific protections, delivery requirements, and QA gates.
- [pptx-figure-assembly.md](references/pptx-figure-assembly.md): Figure Assembly, Component Board, editability levels, manifest, backend separation, and PPT QA.
- [figure-caption-contract.md](references/figure-caption-contract.md): artwork-versus-caption content, panel descriptions, methods detail, PPT notes, and caption trace.
- [figure-package-hygiene.md](references/figure-package-hygiene.md): per-figure folders, final/source/transient classification, safe cleanup, and retention rules.
- [plot-to-ppt-scale-contract.md](references/plot-to-ppt-scale-contract.md): shared plot/PPT container geometry, aspect-ratio gate, final-size typography, stroke and contrast survival.
- [plot-annotation-and-typography-contract.md](references/plot-annotation-and-typography-contract.md): legend/direct-label choice, marker semantics, annotation density, locked font hierarchy, redundant-encoding removal, and final-size visual-grammar QA.
- [figure-method-selection.md](references/figure-method-selection.md): method choice.
- [figure-argument-contract.md](references/figure-argument-contract.md): claim and evidence contract.
- [data-visualization-advisor.md](references/data-visualization-advisor.md): data inspection and honest chart selection.
- [nature-matplotlib-protocol.md](references/nature-matplotlib-protocol.md): reproducible Matplotlib figures.
- [multi-panel-layout-patterns.md](references/multi-panel-layout-patterns.md) and [chart-type-visual-standards.md](references/chart-type-visual-standards.md): panel composition and chart rules.
- [svg-and-drawio-diagrams.md](references/svg-and-drawio-diagrams.md) and [drawio-engineering-diagram-standards.md](references/drawio-engineering-diagram-standards.md): editable diagrams.
- [publication-architecture-layout-gate.md](references/publication-architecture-layout-gate.md): final-size calculation, scientific branch fidelity, connector visibility, fixed operator rows, notation normalization, branch density, parallel/residual grammar, anti-card layout, and publication-text filtering.
- [default-model-diagram-template.md](references/default-model-diagram-template.md): precedence, clone/edit workflow, reusable layout grammar, tensor/vector encoding, protected style, content-replacement rules, and template-specific QA for the bundled PPT model-diagram asset.
- [publication-visual-standards.md](references/publication-visual-standards.md), [export-and-editability-standards.md](references/export-and-editability-standards.md), and [accessibility-and-color-standards.md](references/accessibility-and-color-standards.md): publication output.
- [image-panel-integrity.md](references/image-panel-integrity.md), [ai-image-generation-gate.md](references/ai-image-generation-gate.md), [publisher-visual-source-map.md](references/publisher-visual-source-map.md), and [rendered-figure-qa.md](references/rendered-figure-qa.md): asset integrity, generation gate, venue mapping, and QA.

## Bundled Utilities

- `scripts/make_nature_multipanel.py`: build editable SVG/PDF plus PNG previews and QA from a panel spec and source data; accepts `--style-manifest`.
- `scripts/nature_mpl_style.py`: shared Matplotlib defaults and style-manifest mapping.
- `scripts/validate_style_manifest.py`: validate required style tokens and optionally emit normalized JSON.
- `scripts/build_figure_pptx.mjs`: assemble a hybrid editable PPTX, component board, manifest, and previews with the currently supported presentation backend.
- `scripts/qa_pptx_package.py`: verify PPTX structure, native text, slide bounds, SVG media hashes, and documented raster fallbacks.
- `scripts/qa_plot_ppt_scale.py`: compare SVG viewBoxes with declared PPT slots and enforce final-size font/stroke contract values.
- `scripts/validate_figure_contract.py`: read-only validation of scientific populations, uncertainty, stable element IDs, surface coverage, architecture topology, revision invalidation, paths, hashes, and rebuild records.
- `assets/figure_contract.template.json`: minimal conditional template for `academic-figure-contract/v1`; never use the template itself as a delivery contract.
