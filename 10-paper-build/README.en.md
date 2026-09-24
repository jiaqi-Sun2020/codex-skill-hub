# Paper-build framework

[中文](README.md) | [English](README.en.md) | [Back to the root README](../README.en.md)

`10-paper-build/` directly maintains nine peer Skills that turn research questions, evidence, and analysis into reviewable figures, Chinese author-review drafts, and final submission material. This document is the human entry point for the paper-build category; each Skill's `SKILL.md` remains its formal execution contract.

> The paper pipeline manages research arguments and deliverables. It does not perform the underlying research, invent data, or declare a scientific claim established because a figure, build, or polishing pass succeeded.

## Overall framework

```text
Research logic
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

This is not a sequence that must always start from the beginning. Enter at the earliest missing or evidence-deficient stage; figures and HTML reports are optional branches.

## First principles

1. **Claims precede evidence design.** Existing charts or convenient experiments cannot justify a stronger claim after the fact.
2. **Research execution is outside the paper Skills.** Computational, field, laboratory, qualitative, or other research is performed by project code, domain Skills, or human experts.
3. **Analysis and figure work have separate owners.** `data-analysis` determines whether data, statistics, and uncertainty are defensible; `academic-figure-workflow` turns approved material into figures.
4. **A figure expresses evidence; it is not the evidence itself.** Visual and structural QA cannot promote the scientific claim state.
5. **Review Chinese scientific content before English polishing.** Unless explicitly overridden, approve the science, boundaries, and figure/table intent before translation and venue adaptation.
6. **Simple projects remain simple.** Do not create empty directories, manifests, or ceremonial placeholders when figures, statistics, or HTML reports do not apply.

## Unique responsibilities of the nine Skills

| Skill | Owns | Does not own |
|---|---|---|
| [`research-logic`](research-logic-skill/SKILL.md) | Mechanism-level research logic, contribution claims, and theory gaps | Implementation or invented results |
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
| 0 Intake and inventory | Starting a paper or attaching an existing manuscript | LaTeX Pipeline | `paper_config.json`, asset and gap inventory | Current sources, venue, language, and missing decisions are visible |
| 1 Research logic | The contribution, mechanism, or combination is unclear | `research-logic` | `research_logic.md` | The central mechanism and defensible claim are explicit |
| 2 Experiment and evidence design | The claim is known but the evidence plan is weak | `experiment-design` | `experiment_plan.md`, optional Figure Evidence Plan | Every claim maps to evidence or an explicit TODO |
| 3 Research execution and analysis | Results must be produced or reviewed | Project/domain executor + `data-analysis` | Raw results, analysis code, statistics, and interpretation | Sources, units, transforms, uncertainty, and boundaries are reviewable |
| 4 Research brief | A shareable or printable plan is useful | `research-html-report` | Standalone HTML report | Claim, evidence matrix, risk, and TODOs are visible |
| 5 Figures and Chinese manuscript | Formal figures or manuscript structure are needed | Figure Skill + LaTeX Pipeline | Figure packets, `caption.md`, Chinese LaTeX manuscript | Paths, captions, prose interpretation, and build relationships resolve |
| 6 Author review | The Chinese manuscript and applicable figures exist | Author/domain expert | Review decision and retained TODOs | Science, claim boundary, terminology, figures, and metadata are approved |
| 7 English polishing and submission checks | Scientific content is author-approved | Polishing / PRL Skill | English manuscript and build/submission report | PDF, citations, figures, anonymity, and venue checks pass or expose gaps |

Completing a stage means only that its contract is satisfied. Work completion, data trustworthiness, figure quality, manuscript compilation, claim support, and publication authorization remain independent judgments.

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

## Default workspace

```text
paper_pipeline/
├── paper_config.json
├── 00_research_logic/
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
| Only a research idea exists | Stage 1 |
| The claim is clear but the evidence plan is missing | Stage 2 |
| Results exist but data, statistics, or uncertainty are unreviewed | Stage 3 |
| A shareable research brief is needed | Stage 4 |
| A figure, caption, style lock, or figure QA is needed | Optional figure lane, then return to Stage 5 |
| A `.tex` manuscript needs restructuring or configuration | Stage 5 |
| Chinese scientific content awaits an author decision | Stage 6 |
| Content is approved and needs English or PRL adaptation | Stage 7 |

Small edits do not restart from Stage 0. Missing evidence, an unapproved decision, or a failed gate returns the workflow to the earliest affected stage rather than being hidden by polishing.

## Usage and verification

Create a pipeline from the repository root:

```powershell
python -X utf8 -B ".\10-paper-build\latex-paper-build-skill\scripts\create_paper_pipeline.py" `
  --project "D:\path\to\paper_pipeline" `
  --title "Paper Title"
```

When attaching an existing LaTeX manuscript, add `--latex-source`, `--bib`, and `--copy-figures` as needed. The command does not run experiments, generate scientific conclusions, or approve a submission.

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
