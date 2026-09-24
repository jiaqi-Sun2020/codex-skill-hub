# Paper Pipeline Contract

Use this reference when the user asks for a complete paper pipeline, or when `latex-paper-build-skill` is installed inside a hub category such as `10-paper-build`.

This pipeline borrows the staged-writing discipline of `alfonso0512/research-writing-skill`: separate literature/context intake, outline, section drafting, abstract/introduction/method writing, result interpretation, figure/table captions, logic checking, and reviewer simulation. In this repository those stages should become durable files, not chat-only prompt outputs.

## Pipeline Stages

```text
0. Intake, project inventory, and paper_config.json
1. Research logic
2. Experiment design
3. Training code and result contract
4. Research HTML report
5. Config-driven Chinese author-review LaTeX manuscript architecture
6. User scientific/content review gate
7. Post-approval English polishing and submission checks
```

Each stage should produce a durable artifact. Avoid treating chat-only reasoning as complete unless the user explicitly wants a discussion rather than a managed project.

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

Exit gate:

- every claim maps to an experiment or TODO;
- every table/figure in the future paper has a purpose;
- baselines include strong and mechanism-neighbor alternatives.

## Stage 3: Training Code and Results

Use when creating or standardizing experiment code.

Artifacts:

```text
02_training_code/
03_results/
```

Expected result contract:

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

- training entrypoint is reproducible;
- configs are copied into run folders;
- final metrics can feed paper tables;
- result files include model, variant, dataset, seed, metric, split, and checkpoint path.

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

## Stage 6: User Scientific/Content Review Gate

Do not run whole-manuscript final English polishing before this gate unless the user explicitly overrides it. The author should review the Chinese manuscript for scientific content, claim boundaries, terminology, figure/table intent, and paper metadata.

Exit gate:

- user approves the Chinese scientific content or gives an explicit override;
- `paper_config.json` metadata has been checked by the author;
- unresolved TODOs are either fixed or deliberately carried forward;
- claims are marked as completed, partial, planned, or speculative.

## Stage 7: Post-Approval English Polishing And Submission

Sibling skill: `../paper-polishing-skill/SKILL.md`

Use after the review gate to translate and polish the approved Chinese manuscript into the requested Nature, PRL, or PRA style.

Required checks:

- compile with `latexmk -xelatex -bibtex -interaction=nonstopmode -file-line-error -outdir=build main.tex` when `ctex` or `fontspec` is used;
- check undefined references and citations;
- check missing figures and ensure image paths point into `figures/`;
- check bibliography drift and ensure references are `.bib` managed;
- check figure formats and raster/vector suitability;
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

## Routing Rules

- If the user asks "is this idea a paper?", start at Stage 1 after creating or checking `paper_config.json`.
- If the idea is clear but evidence is weak, start at Stage 2.
- If the experiments exist but code/results are messy, start at Stage 3.
- If the user wants a visual plan or shareable summary, start at Stage 4.
- If the user has a `.tex` manuscript, asks for paper architecture, or asks for author/contact metadata configuration, start at Stage 5.
- If the user has approved the Chinese manuscript and asks for final English output, start at Stage 7 with `paper-polishing-skill`.
- If the user has a manuscript and wants pre-final content review, start at Stage 6; after approval, continue to Stage 7.

Do not require all stages for small edits. A pipeline exists to preserve continuity, not to create ceremony.
