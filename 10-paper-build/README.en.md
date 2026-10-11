# Paper-build framework

[中文](README.md) | [English](README.en.md) | [Back to the root README](../README.en.md)

`10-paper-build/` directly maintains twelve peer Skills that turn research questions, evidence, and analysis into reviewable figures, Chinese author-review drafts, and final submission material. This document is the human entry point for the paper-build category; each Skill's `SKILL.md` remains its formal execution contract.

> The paper pipeline manages research arguments and deliverables. It does not perform the underlying research, invent data, or declare a scientific claim established because a figure, build, or polishing pass succeeded.

## Overall framework

```text
Scope and initial question
  ↓
Research logic: initial candidates (optional)
  ↕
Literature discovery/synthesis / known-set matrix
  ↕
Research logic: revise question, assumptions and claim boundary
  ↓
Experiment and evidence design ──→ Figure-argument planning
  ↓
Research execution and data analysis ──→ Usable evidence
  ↓                                      ↓
HTML report (optional)          academic-figure-workflow
  ↓                                      ↓
Chinese LaTeX manuscript ← figure package, caption, trace, QA
  ↓
Author scientific and visual review
  ↓
English polishing and submission checks
```

This is not a sequence that must always start from the beginning. Enter at the earliest missing or evidence-deficient stage; literature, figures and HTML reports are optional branches. Theory, qualitative work and reviews may form direct arguments/syntheses without new experiments.

## Repeatable goal-clarification loop

Enter as needed at any stage: existing material/decisions → current blockers → smallest next action → return to the requested stage. Start with a light check; clear goals do not require an interview. This adds neither a stage nor a Skill.

`latex-paper-build-skill` owns activation, scope and return routing; `research-logic` handles scientific questions only. The single execution protocol is the [goal-clarification reference](latex-paper-build-skill/references/goal-clarification.md); its interview rules are not duplicated here.

- Assess work goals, scientific questions, acceptance and action authority separately; negative results and insufficient evidence are permitted research outcomes.
- Reuse located decisions on reentry and reopen affected branches only. Confirm chat proposals conflicting with formal contracts rather than operating under both goals.
- `intake.md` holds the work goal or formal-contract pointer, `research_logic.md` the scientific question, and stage artifacts local decisions; `pipeline_context.md` only navigates.
- Unsaved chat is not guaranteed to survive another session. Missing fields in legacy workspaces do not trigger regeneration or insertion.

Example: “Use `latex-paper-build-skill` at the current figure stage. Clarify only unresolved figure information, reuse confirmed goals and permissions, then return to the figure workflow; do not rebuild the workspace.”

## First principles

1. **Claims precede evidence design.** Existing charts or convenient experiments cannot justify a stronger claim after the fact.
2. **Research execution is outside the paper Skills.** Computational, field, laboratory, qualitative, or other research is performed by project code, domain Skills, or human experts.
3. **Analysis and figure work have separate owners.** `data-analysis` determines whether data, statistics, and uncertainty are defensible; `academic-figure-workflow` turns approved material into figures.
4. **A figure expresses evidence; it is not the evidence itself.** Visual and structural QA cannot promote the scientific claim state.
5. **Review Chinese scientific content before English polishing.** Unless explicitly overridden, approve the science, boundaries, and figure/table intent before translation and venue adaptation.
6. **Simple projects remain simple.** Do not create empty directories, manifests, or ceremonial placeholders when figures, statistics, or HTML reports do not apply.

## Unique responsibilities of the twelve Skills

| Skill | Owns | Does not own |
|---|---|---|
| [`paper-project-initializer`](paper-project-initializer/SKILL.md) | Discover, preview, initialize minimal entries and hand off a selected stage | Research planning, implicit Hook enablement or rebuilding existing workspaces |
| [`literature-review`](literature-review/SKILL.md) | Discovery, screening, source appraisal and thematic synthesis | Treat limited search, DOI registration or review completion as scientific approval |
| [`literature-triage-matrix`](literature-triage-matrix/SKILL.md) | Compare a known set with source levels and unresolved checks | Certify coverage or equate relevance with quality |
| [`research-logic`](research-logic-skill/SKILL.md) | Question ideation, logic challenge and conditional method integration | Automatic winners, implementation or hypothesis validation |
| [`experiment-design`](experiment-design-skill/SKILL.md) | Research questions, evidence gaps, controls, ablations, metrics, and claim boundaries | Experiment execution, runners, or execution authority |
| [`data-analysis`](data-analysis/SKILL.md) | Data integrity, statistical tests, effect sizes, intervals, uncertainty, and reviewable interpretation | Presenting missing or unreliable data as a confident conclusion |
| [`research-html-report`](research-html-report/SKILL.md) | Standalone HTML research briefs, evidence plans, and risk displays | Replacing research design or manufacturing evidence |
| [`academic-figure-workflow`](academic-figure-workflow/SKILL.md) | Figure arguments, editable sources, style, exports, captions, evidence trace, and rendered QA | Inventing data, mechanisms, modules, or scientific support |
| [`latex-paper-build-skill`](latex-paper-build-skill/SKILL.md) | Pipeline orchestration, LaTeX architecture, figure placement, cross-references, and compilation | Reimplementing statistics or figure-generation logic |
| [`paper-polishing-skill`](paper-polishing-skill/SKILL.md) | Translation, structural revision, and Nature/PRL/PRA polishing of approved content | Inventing data, citations, or stronger claims |
| [`prl-manuscript-polisher`](prl-manuscript-polisher/SKILL.md) | PRL compression, adaptation, and evidence calibration for a technically complete physics manuscript | Hiding weak evidence with stronger prose |
| [`interactive-skill-builder`](interactive-skill-builder/SKILL.md) | Skill creation through interviews, specification confirmation, approval gates, and validation | Producing a final Skill without author confirmation |

`latex-paper-build-skill` is the paper-pipeline orchestrator but does not own the other Skills' specialist capabilities. `interactive-skill-builder` is a peer utility, not a mandatory paper-lifecycle stage.

## Stages 0–7

| Stage | Enter when | Owner | Core artifact | Exit condition |
|---|---|---|---|---|
| 0 Intake and inventory | Initialization or attaching an existing paper | Initializer → LaTeX Pipeline | Intake/context or existing equivalents; config when needed | Goal source, permission, gaps and next stage are visible |
| 1 Logic and optional literature | Question, contribution, context or combination is unclear | logic / review / matrix | `research_logic.md`, requested literature artifacts | Question, source limits, candidates and unresolved decisions are explicit |
| 2 Experiment and evidence design | The claim is known but the evidence plan is weak | `experiment-design` | `experiment_plan.md`, optional Figure Evidence Plan | Every claim maps to evidence or an explicit TODO |
| 3 Research execution and analysis | Results must be produced or reviewed | Project/domain executor + `data-analysis` | Raw results, analysis code, statistics, and interpretation | Sources, units, transforms, uncertainty, and boundaries are reviewable |
| 4 Research brief | A shareable or printable plan is useful | `research-html-report` | Standalone HTML report | Claim, evidence matrix, risk, and TODOs are visible |
| 5 Figures and Chinese manuscript | Formal figures or manuscript structure are needed | Figure Skill + LaTeX Pipeline | Figure packets, `caption.md`, Chinese LaTeX manuscript | Paths, captions, prose interpretation, and build relationships resolve |
| 6 Author review | The Chinese manuscript and applicable figures exist | Author/domain expert | Review decision and retained TODOs | Science, claim boundary, terminology, figures, and metadata are approved |
| 7 English polishing and submission checks | Scientific content is author-approved | Polishing / PRL Skill | English manuscript and build/submission report | PDF, citations, figures, anonymity, and venue checks pass or expose gaps |

Completing a stage means only that its contract is satisfied. Work completion, data trustworthiness, figure quality, manuscript compilation, claim support, and publication authorization remain independent judgments.

## Optional literature lane and scientific checks

- Unknown context enters `literature-review`; a known paper set enters `literature-triage-matrix`.
- `research-logic` supports ideation, integration and logic challenge; reopen it after source checks. Integration depth is not a contribution-quality ladder.
- Brainstorming's assumptions, alternatives, counterevidence and decisions inform logic. Critical Thinking informs source appraisal, evidence design and actual data analysis; no duplicate Skill is added.
- DOI registration, statement support, search coverage, independent study count and author approval are separate. Abstracts/AI summaries are not full-text assessment; repeated agent passes are not independent dual review.
- Retain negative evidence, overlapping samples, versions, unavailable reports and unassessed claims. Simple methods remain valid; theory and qualitative work do not require training, seeds, statistics or figures.

Use `00_research_logic/literature/` only when activated:

| Artifact | Purpose | Create when |
|---|---|---|
| `literature_matrix.md` | Known-set comparison with requested columns | Matrix requested |
| `review_protocol.md` | Queries, screening, report/study links, appraisal, revisions and gaps | Traceable review needed |
| `literature_review.md` | Question/theme-based synthesis | Narrative requested |

Do not create three placeholders or a hidden `.research/` system. Standalone use can be inline or reuse an owner-selected location. Preserve the manuscript's active `.bib` and keys; source passages and review records are not another bibliography.

The record tool does not search databases and defaults to stdout; explicit file outputs refuse overwrite. Unknown years are pending; duplicate/version data are retained. DOI checks are optional metadata/registration checks, not claim validation. No automatic dependencies, manuscript uploads or deletion of unresolved references. Commands: [literature-review](literature-review/SKILL.md).

## Optional figure-evidence lane

Experiment design plans what a figure must answer; it does not draw the figure. The minimum handoff to `academic-figure-workflow` includes:

- figure ID and target manuscript section;
- primary claim anchor;
- source data, code, equations, text, or user-approved facts;
- evidence readiness: `unavailable / unreviewed / verified_for_figure`;
- statistics readiness: `not_applicable / unreviewed / verified_for_figure`;
- the non-redundant role of each panel;
- target venue, final physical size, editable source, and export formats;
- unresolved scientific decisions.

The output packet contains editable sources, SVG/PDF/PNG or other exports, `caption.md`, placement recommendation, evidence trace, related claim anchors, rendered/structural QA, and unresolved issues. Insufficient evidence permits only a specification, storyboard, or explicitly marked draft.

The generated paper pipeline has one figure root:

```text
05_manuscript_zh/figures/
├── style/                 # create only when a shared visual system is needed
└── figNN_<slug>/          # create only when this figure exists
    ├── source/
    ├── exports/
    ├── caption.md
    └── manifest
```

Do not create a second root-level `figures/` or duplicate figure packets under `04_reports/` or `07_polished_submission/`. Standalone figure-workflow use may still select another figure root.

## Minimal initialization

Use [paper-project-initializer](paper-project-initializer/SKILL.md) for starting, onboarding checks or same-plan recovery. Default: two entries (`00_research_logic/intake.md`, `pipeline_context.md`), no config or empty stages. Existing rules/goals are referenced, not overwritten. Agent/memory baseline and persistent Hooks are separately disclosed and approved; entry creation grants no research authority. Return to the selected stage; ordinary editing remains in its current stage.

## Explicit full workspace

```text
paper_pipeline/
├── paper_config.json
├── 00_research_logic/     # literature/ appears only when that lane is used
├── 01_experiment_design/
├── 02_training_code/      # use only when training or analysis code exists
├── 03_results/
├── 04_reports/            # optional
├── 05_manuscript_zh/
│   ├── main.tex
│   ├── preamble.tex
│   ├── frontmatter.tex
│   ├── sections/
│   ├── figures/           # create when figures exist
│   └── references/
├── 06_review_gate/
├── 07_polished_submission/
└── pipeline_context.md
```

Directory numbers are compatibility contracts and are not renumbered for the figure lane. `02_training_code/` is also a compatibility location; it does not require every research project to train a model.

## Choose the entry by current state

| Current state | Entry |
|---|---|
| Only a research idea exists | Stage 1: question ideation |
| Research context is unclear | literature-review, then Stage 1 |
| Known papers need comparison | literature-triage-matrix |
| The claim is clear but the evidence plan is missing | Stage 2 |
| Results exist but data, statistics, or uncertainty are unreviewed | Stage 3 |
| A shareable research brief is needed | Stage 4 |
| A figure, caption, style lock, or figure QA is needed | Optional figure lane, then return to Stage 5 |
| A `.tex` manuscript needs restructuring or configuration | Stage 5 |
| Chinese scientific content awaits an author decision | Stage 6 |
| Content is approved and needs English or PRL adaptation | Stage 7 |

Small edits do not restart from Stage 0. Missing evidence, an unapproved decision, or a failed gate returns the workflow to the earliest affected stage rather than being hidden by polishing.

## Usage and verification

Create a complete eight-stage pipeline only when explicitly requested, from the repository root:

```powershell
python -X utf8 -B ".\10-paper-build\latex-paper-build-skill\scripts\create_paper_pipeline.py" `
  --project "D:\path\to\paper_pipeline" `
  --title "Paper Title"
```

When attaching an existing LaTeX manuscript, add `--latex-source`, `--bib`, and `--copy-figures` as needed. The generator creates scaffolding and routes only; agents invoke the two literature Skills on demand, not automatic searches or source appraisal. It does not run experiments, generate scientific conclusions, or approve a submission. DOI registration, metadata matching, content support, retraction screening and scientific quality are recorded independently; unchecked axes remain unassessed.

Validate this category:

```powershell
Get-ChildItem .\10-paper-build -Directory | ForEach-Object {
    if (Test-Path (Join-Path $_.FullName 'SKILL.md')) {
        python -X utf8 -B "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" $_.FullName
    }
}

python -X utf8 -B -m unittest discover `
  -s ".\10-paper-build\latex-paper-build-skill\tests" `
  -p "test_*.py"
```

## Migration, provenance, and license

On 2026-09-24, this directory imported eight Skills from the `main` snapshot of the retired `jiaqi-Sun2020/S_paper_skills` repository (source commit `dcd573b1768e48e794975100f8548dc0f1bcb50e`). Together with the existing `academic-figure-workflow`, they form nine peer Skills. The old `data-analsys-skill/` path is normalized to `data-analysis/`; the wrapper, `util_skills/` layer, and shortcut are retired. The source repository's MIT notice is retained in [`S_PAPER_SKILLS_LICENSE`](S_PAPER_SKILLS_LICENSE).

The figure workflow draws on argument-driven multi-panel design, semantic colour, and submission QA ideas from [`nature-figure`](https://github.com/Yuan1z0825/nature-skills/tree/main/skills/nature-figure), and the data-first visualization-advisor approach from [`scipilot-figure-skill`](https://github.com/Haojae/scipilot-figure-skill). Specific publication-guideline sources are recorded in [`publisher-visual-source-map.md`](academic-figure-workflow/references/publisher-visual-source-map.md). These acknowledgements do not imply endorsement; third-party material remains subject to its original licenses and notices.

Fixed upstream commits, adaptation scope and full MIT notices for literature and scientific reasoning are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). The category now has 12 Skills; the historical eight imports plus the figure Skill remain the original nine-source history.
