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

1. Evidence and data determine content; the style manifest determines appearance.
2. Once locked, `figures/style/style_manifest.yaml` is the only paper-wide visual source of truth. A local override requires an explicit user request and an override record.
3. Semantic colours are stable across figures: for example, `proposed_method`, `baseline`, `encoder`, and `uncertainty` keep the same meanings.
4. Reference-image transfer borrows design language, not pixels, scientific content, protected marks, or unsupported layout semantics.
5. Architecture deliverables default to `.drawio + .svg + .pdf + .png`; preserve SVG `<text>`, vector arrows, and independent groups.
6. Data figures default to source data + plotting source + `.svg + .pdf + .png`; keep `svg.fonttype = none` and `pdf.fonttype = 42`.
7. PPT assembly defaults to `hybrid`: native PowerPoint objects where reliable, SVG for complex vector panels, and raster only for inherently bitmap content.
8. PowerPoint editability never overrides scientific correctness. Do not alter values, error bars, statistics, axis ranges, scales, or observed points to obtain a native chart.
9. Preserve formulas, notation, labels, and manuscript terminology through every conversion.
10. Keep the artwork claim-focused. Move nonessential configuration text—sample counts, preprocessing recipes, fold protocol, optimizer settings, and similar authoring detail—to the figure caption unless it is required to decode the marks.
11. Build and validate in a temporary workspace, then deliver one clean folder per figure. Keep final deliverables and reproducibility sources; remove previews, inspect snapshots, layout dumps, caches, starter decks, and temporary QA renders unless the user explicitly asks to retain them.
12. When a plot is embedded in PPT or resized for publication, define the final container first. Make plot code and PPT assembly consume one layout contract; forbid non-uniform SVG scaling and verify final-size typography, strokes, and signal contrast after round-trip rendering.
13. Validate the data-axes rectangle separately from the outer SVG/PPT container. A non-stretched asset can still be aesthetically wrong when subplot margins, colorbars, or legends make the evidence area too tall or narrow.
14. Treat detailed quantitative captions as an element inventory: define both axes, every visible mark and uncertainty encoding, observation grain, transformations, comparison roles, validation scope, and any equation or metric removed from the artwork.
15. For dense budget or mask sweeps, preserve every evaluated value, use sparse event markers, separate single-metric thresholds from joint all-criterion acceptance, show actual multi-budget mask expansion when relevant, and keep prespecified stability rules distinct from sensitivity analyses.
16. Treat plot legends, markers, direct labels, annotations, and fonts as one visual grammar. Remove redundant encodings, use markers only for declared sample or event meanings, and keep peer typography locked at final size without altering scientific content.
17. Every academic PPT figure kit defaults to three caption surfaces: portable `caption.md`, publication-slide speaker notes, and native editable panel-mapped visible explanation sections on a supporting slide or reserved column. Keep the publication artwork clean. A notes-only or single-slide exception requires an explicit user request and a manifest record.
18. For editable PPT model or neural-network figures, use the bundled default model-diagram template only when the user has not supplied a reference PPTX and the project has no locked user-approved model template. The template contributes layout and visual grammar, never scientific content. Replace every example-specific label, tensor dimension, branch, operator, caption, and source with evidence from the target project.

## Workflow Router

1. Define the figure claim, target section, source facts, method, output files, and validation checks.
2. For complex, multi-panel, submission-bound, code-backed, or data-backed figures, apply [figure-argument-contract.md](references/figure-argument-contract.md).
3. If reference images define the desired visual language:
   - apply [reference-image-style-migration.md](references/reference-image-style-migration.md) and [figure-style-manifest.md](references/figure-style-manifest.md);
   - create or update `figures/style/style_manifest.yaml` and `style_report.md` before drawing;
   - make all later SVG, Draw.io, Matplotlib, and PPT outputs inherit the manifest.
4. For journal-facing figures, apply [publication-visual-standards.md](references/publication-visual-standards.md), [export-and-editability-standards.md](references/export-and-editability-standards.md), and [accessibility-and-color-standards.md](references/accessibility-and-color-standards.md).
5. For CSV, Excel, TSV, JSON, Parquet, NumPy, or DataFrame inputs, apply [data-visualization-advisor.md](references/data-visualization-advisor.md) before plotting. Verify columns, units, groups, sample size, missingness, metric definitions, and uncertainty provenance.
6. For Nature-style or multi-panel Matplotlib figures, apply [nature-matplotlib-protocol.md](references/nature-matplotlib-protocol.md), [multi-panel-layout-patterns.md](references/multi-panel-layout-patterns.md), and [chart-type-visual-standards.md](references/chart-type-visual-standards.md).
   - When those plots will be embedded in PPTX or resized from an authoring canvas, also apply [plot-to-ppt-scale-contract.md](references/plot-to-ppt-scale-contract.md) before plotting and during final QA.
   - When legends, markers, direct labels, annotations, or fonts are crowded or inconsistent, also apply [plot-annotation-and-typography-contract.md](references/plot-annotation-and-typography-contract.md). Record the chosen visual grammar, remove redundant encodings, and recheck the final-size render.
7. For SVG or Draw.io diagrams, apply [svg-and-drawio-diagrams.md](references/svg-and-drawio-diagrams.md); for code-backed or neural-network architecture diagrams also apply [drawio-engineering-diagram-standards.md](references/drawio-engineering-diagram-standards.md).
   - For journal-facing neural-network, workflow, or code-backed architecture figures, also apply [publication-architecture-layout-gate.md](references/publication-architecture-layout-gate.md) before drawing and again during final-size QA.
   - If the requested deliverable is an editable PPT model diagram and neither a user reference deck nor a project-locked model template exists, also apply [default-model-diagram-template.md](references/default-model-diagram-template.md) and clone `assets/model-diagram/default-model-diagram-template.pptx` as the starting deck. User references and project-locked styles always take precedence.
8. For image plates or mixed raster/vector panels, apply [image-panel-integrity.md](references/image-panel-integrity.md).
9. For AI-generated bitmap assets, apply [ai-image-generation-gate.md](references/ai-image-generation-gate.md) before generation.
10. If the user requests PPT, PPTX, PowerPoint assembly, a figure kit, or a component board, apply [pptx-figure-assembly.md](references/pptx-figure-assembly.md). Generate the PPTX, `ppt_manifest.json`, independently movable components, and rendered QA preview.
    - By default, create native editable panel-mapped explanation sections on a supporting slide or reserved column. Split them across slides rather than shrinking or clipping text. Omit visible explanations only when the user explicitly requests notes-only or a single-slide deliverable, and record that override.
11. Apply [figure-caption-contract.md](references/figure-caption-contract.md) before final export. Keep a caption draft beside the figure package and embed it in the publication slide's speaker notes when PPTX is produced. The default visible PPT explanation surface supplements rather than replaces these two sources.
12. When venue-specific artwork rules matter, apply [publisher-visual-source-map.md](references/publisher-visual-source-map.md) and verify the current official guide.
13. When labels, formulas, citations, or cross-references are converted between
    formats, compare the rendered output with the source and reject missing
    symbols, substituted glyphs, changed notation, or broken references.
14. Apply [rendered-figure-qa.md](references/rendered-figure-qa.md) to every submission-quality figure and the additional PPT QA in [pptx-figure-assembly.md](references/pptx-figure-assembly.md).
15. After validation, apply [figure-package-hygiene.md](references/figure-package-hygiene.md). Remove transient files only after their final outputs and source traces are verified.
16. Deliver editable sources, exports, caption draft, placement recommendation, evidence/code/data trace, style-manifest path, validation summary, editability report, and unresolved issues.

## Validation

Before finishing:

- confirm method, panel claims, and evidence trace;
- validate the style manifest and confirm semantic-colour consistency;
- inspect editable sources and rendered previews at intended final size;
- check overlap, clipping, font consistency, line weight, contrast, grayscale and colour-blind interpretation;
- check that legends, direct labels, markers, annotations, and fonts follow one declared visual grammar, with no redundant method identities or undefined decorative markers;
- verify SVG text remains editable and Draw.io files are genuine editable XML;
- verify data columns, units, sample counts, missing values, transformations, uncertainty, and axis scales against source data;
- for PPTX, verify openability, slide bounds, independent objects, panel labels, aspect ratios, vector/raster classification, source trace, and documented fallbacks;
- for academic PPT figure kits, verify one native editable explanation section per displayed panel, complete encoding definitions, manifest mapping, and scientific consistency with `caption.md`, notes, plot source, and data; verify any notes-only/single-slide override is explicit and recorded;
- list unresolved scientific, data, style, font, export, and editability issues separately.

## References

- [figure-style-manifest.md](references/figure-style-manifest.md): project style schema, precedence, locking, overrides, and directory contract.
- [reference-image-style-migration.md](references/reference-image-style-migration.md): reference analysis, style-token extraction, conflict resolution, and non-copying rules.
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
