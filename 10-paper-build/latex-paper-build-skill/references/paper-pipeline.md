# Paper Pipeline Contract

Use this reference when the user asks for a complete paper pipeline, or when `latex-paper-build-skill` is installed inside a hub category such as `10-paper-build`.

This pipeline borrows the staged-writing discipline of `alfonso0512/research-writing-skill`: separate literature/context intake, outline, section drafting, abstract/introduction/method writing, result interpretation, figure/table captions, logic checking, and reviewer simulation. In this repository those stages should become durable files, not chat-only prompt outputs.

## Pipeline Stages

```text
0. Intake, project inventory, and paper_config.json
1. Research logic
2. Experiment and evidence design, including optional figure intent
3. Evidence production, result integrity, and data analysis
4. Research HTML report
5. Optional academic-figure production and Chinese LaTeX manuscript architecture
6. User scientific, content, and figure review gate
7. Post-approval English polishing and submission checks
```

Each stage should produce a durable artifact. Avoid treating chat-only reasoning as complete unless the user explicitly wants a discussion rather than a managed project.

The academic-figure path is optional and cross-cutting rather than a mandatory
numbered stage. `latex-paper-build-skill` decides when to route into it and owns
manuscript placement, references, compilation, and figure-reading prose.
`academic-figure-workflow` exclusively owns figure method selection, editable
sources, style, exports, captions, evidence trace, and rendered QA.
`data-analysis` owns data integrity and statistical interpretation. None of
these states may be inferred from another: visual QA does not prove a
scientific claim, and a scientifically reviewed result does not prove the
export is readable or submission-ready.

## Stage 0: Intake, Inventory, And Config

Goal: identify what already exists, what is missing, and what stable manuscript metadata should drive generated frontmatter.

Inspect:

- paper idea or current manuscript;
- available `.tex`, `.bib`, figures, PDFs, logs;
- experiment code, configs, outputs, metrics CSVs;
- reports or planning notes;
- target venue, language, page limit, anonymity status;
- author names, affiliations, contact email, correspondence address, keywords, acknowledgments, and funding metadata.

Recommended artifacts:

```text
paper_config.json
00_research_logic/intake.md
```

Minimum contents:

- one-sentence project identity;
- current source assets;
- missing decisions;
- target pipeline stage;
- metadata TODOs that remain unresolved in `paper_config.json`.

Read `references/paper-config.md` before creating or editing `paper_config.json`. For QCT/QWCT papers, read `references/qct-writing-methodology.md` before drafting the abstract, introduction, contribution paragraph, results framing, or discussion boundary.

## Stage 1: Research Logic

Sibling skill: `../research-logic-skill/SKILL.md`

Use when the contribution, mechanism, or method combination is unclear.

Artifact:

```text
00_research_logic/research_logic.md
```

It should contain:

- native function of each method;
- direct connection point;
- shallow integration baseline;
- mechanism-level reconstruction;
- claim discipline and boundaries.

Exit gate:

- central mechanism is stated as a state, operator, update rule, or assumption change;
- claims avoid generic "we improve performance" phrasing;
- open theory gaps are explicit.

## Stage 2: Experiment Design

Sibling skill: `../experiment-design-skill/SKILL.md`

Use after the central claim is known, before running or rewriting experiments.

Artifact:

```text
01_experiment_design/experiment_plan.md
```

It should contain:

- central claim;
- research questions;
- datasets and tasks;
- baselines;
- ablations;
- mechanism checks;
- metrics and tables;
- failure cases;
- claim boundaries;
- minimum viable experiment plan.
- when figures are applicable, a lightweight figure-evidence plan stating the
  intended claim anchor, target section, panel roles, required evidence and
  analysis, target venue/size, and open decisions. This is a plan, not artwork.

Exit gate:

- every claim maps to an experiment or TODO;
- every table/figure in the future paper has a purpose;
- baselines include strong and mechanism-neighbor alternatives.
- planned figures do not imply that evidence or statistics have already been
  verified.

## Stage 3: Evidence Production, Results, And Data Analysis

Use the project's domain method or execution workflow to produce evidence. For
quantitative results, use sibling skill `../data-analysis/SKILL.md` to check
data provenance, units, missingness, statistical design, uncertainty, and the
claim boundary before a submission-facing plot is produced. Non-quantitative
projects may provide other reviewable evidence and mark statistical analysis
as not applicable with a reason.

Artifacts:

```text
02_training_code/
03_results/
```

`02_training_code/` is retained for compatibility and is used only when the
project actually has training or analysis code. A training-based project may
use this result contract:

```text
outputs/runs/{run_name}/
  config.json
  checkpoints/best.pt
  logs/train.log
  results/train_history.csv
  results/final_metrics.csv
  results/ablation_ready_metrics.csv
```

Exit gate:

- evidence sources and transformations are identifiable;
- applicable data-integrity and statistical checks are recorded;
- uncertainty, units, exclusions, and analysis limitations are explicit when
  relevant;
- figure inputs are marked `unavailable`, `unreviewed`, or
  `verified_for_figure` rather than assumed ready from file existence;
- training-specific reproducibility fields are required only for projects that
  actually train models.

## Stage 4: Research HTML Report

Sibling skill: `../research-html-report/SKILL.md`

Use when the user wants a shareable research brief, a paper-planning dashboard, or a printable pre-paper report.

Artifact:

```text
04_reports/<project-key>.html
```

Exit gate:

- report states the exact claim;
- mechanism, experiment plan, evidence matrix, risks, and TODOs are visible;
- missing evidence is marked as TODO rather than implied as complete.

## Optional Figure Evidence Lane

Sibling skill: `../academic-figure-workflow/SKILL.md`

Activate this lane only when the paper needs a diagram, data plot, image plate,
multi-panel figure, editable PowerPoint kit, or submission-quality figure QA.
Do not require it for a figure-free theoretical, qualitative, or short paper.

Before drawing, apply the figure handoff in
`../academic-figure-workflow/references/figure-argument-contract.md`. The
handoff states the figure ID, target manuscript section, claim anchor, source
materials, evidence/statistics readiness, panel roles, target venue and final
size, required sources/exports, and unresolved scientific decisions.

Inside this generated pipeline the only figure root is:

```text
05_manuscript_zh/figures/
```

Create `style/` and `figNN_<slug>/` packages only when needed. Do not create a
second root-level `figures/`, copy packages into `04_reports/` or
`07_polished_submission/`, or create empty manifests for a figure-free paper.

Exit gate for a submission-facing figure:

- evidence and applicable statistics are verified for the figure;
- each panel has one necessary, non-redundant role;
- editable source, requested exports, `caption.md`, evidence trace, and
  unresolved issues are present;
- rendered output passes final-size, clipping, typography, accessibility, and
  scientific-consistency review;
- the figure's visual/package status is recorded separately from the review
  state of the scientific claim.

If any required item is missing, retain a specification, storyboard, or marked
draft and do not call it submission-ready.

## Stage 5: Config-Driven Chinese Author-Review LaTeX Manuscript Architecture

This skill owns this stage. By default in the hub's `10-paper-build` workflow, generated author-review prose should be Chinese while preserving PRL/PRA paper logic. The English finalization is a later, approval-gated stage.

Paper metadata config: read `references/paper-config.md`. Create or preserve root-level `paper_config.json` and use it as the source of truth for title, authors, affiliations, correspondence address/email, keywords, acknowledgments, venue, and author-review abstract.

Artifacts:

```text
paper_config.json
05_manuscript_zh/
  main.tex
  preamble.tex
  frontmatter.tex
  sections/
  figures/
    style/                  # only when shared style is applicable
    figNN_<slug>/           # only when this figure package exists
      source/
      exports/
      caption.md
      manifest
  references/
    references.bib
  notes/paper_context.md
```

Use `scripts/scaffold_latex_paper.py` for existing monolithic papers. Use `scripts/create_paper_pipeline.py` for new config-driven workspaces. Use `assets/revtex-qwct-template/` for new REVTeX/QWCT-style manuscripts.

Exit gate:

- `paper_config.json` exists and has title, authors, affiliations, correspondence, and venue fields;
- `frontmatter.tex` is generated from or manually checked against `paper_config.json`;
- QCT/QWCT abstract and introduction follow `qct-writing-methodology.md`;
- source manuscript is modular;
- original source remains untouched unless explicitly requested;
- figure and bibliography paths resolve;
- all literature is managed through `.bib` files;
- all manuscript images live under the single `figures/` folder;
- labels and citation keys are preserved.
- applicable figures come from the canonical figure packages and have caption,
  evidence-trace, and QA state available;
- manuscript prose identifies what each included figure shows, the decisive
  comparison, its scientific implication, and its local boundary.

## Stage 6: User Scientific/Content Review Gate

Do not run whole-manuscript final English polishing before this gate unless the user explicitly overrides it. The author should review the Chinese manuscript for scientific content, claim boundaries, terminology, figure/table intent, and paper metadata.

Exit gate:

- user approves the Chinese scientific content or gives an explicit override;
- `paper_config.json` metadata has been checked by the author;
- unresolved TODOs are either fixed or deliberately carried forward;
- claims are marked as completed, partial, planned, or speculative.
- for each applicable figure, the author has reviewed scientific consistency,
  source trace, caption, final-size readability, accessibility, editability,
  and unresolved issues;
- a visual/package PASS has not been treated as scientific claim approval.

## Stage 7: Post-Approval English Polishing And Submission

Sibling skill: `../paper-polishing-skill/SKILL.md`

Use after the review gate to translate and polish the approved Chinese manuscript into the requested Nature, PRL, or PRA style.

Required checks:

- compile with `latexmk -xelatex -bibtex -interaction=nonstopmode -file-line-error -outdir=build main.tex` when `ctex` or `fontspec` is used;
- check undefined references and citations;
- check missing figures and ensure image paths point into `figures/`;
- check bibliography drift and ensure references are `.bib` managed;
- check figure formats and raster/vector suitability;
- check that each applicable figure resolves under the one manuscript
  `figures/` root and includes its required editable source or approved
  exception, exports, caption, evidence trace, and final-size QA;
- check page count and venue constraints if known;
- check anonymity if double blind;
- check that `paper_config.json` remains the source for final title, authors, affiliations, and correspondence.

Artifact:

```text
07_polished_submission/build_report.md
```

Exit gate:

- PDF builds;
- unresolved references are listed or fixed;
- warnings that affect submission are separated from harmless typography warnings.

## Default Project Tree

```text
paper_pipeline/
  paper_config.json
  00_research_logic/
    intake.md
    research_logic.md
  01_experiment_design/
    experiment_plan.md
  02_training_code/
  03_results/
  04_reports/
  05_manuscript_zh/
  06_review_gate/
    author_review_checklist.md
  07_polished_submission/
    build_report.md
  pipeline_context.md
```

The generator does not create empty figure-package or style files. The
`05_manuscript_zh/figures/` root appears only when referenced figures are
imported or the figure workflow needs it.

## Routing Rules

- If the user asks "is this idea a paper?", start at Stage 1 after creating or checking `paper_config.json`.
- If the idea is clear but evidence is weak, start at Stage 2.
- If the experiments exist but code/results are messy, start at Stage 3.
- If quantitative evidence exists but its integrity, uncertainty, or
  statistics are not reviewed, stay at Stage 3 and use `data-analysis` before
  producing final plots.
- If the user wants a visual plan or shareable summary, start at Stage 4.
- If the user asks for a figure, diagram, data plot, style lock, caption, figure
  package, or figure QA, route through the optional figure lane. Return to Stage
  5 for manuscript placement and prose interpretation after the figure packet
  is ready.
- If the user has a `.tex` manuscript, asks for paper architecture, or asks for author/contact metadata configuration, start at Stage 5.
- If the user has approved the Chinese manuscript and asks for final English output, start at Stage 7 with `paper-polishing-skill`.
- If the user has a manuscript and wants pre-final content review, start at Stage 6; after approval, continue to Stage 7.

Do not require all stages for small edits. A pipeline exists to preserve continuity, not to create ceremony.
