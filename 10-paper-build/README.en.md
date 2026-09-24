# Paper Build Skills

[中文](README.md) | [English](README.en.md)

`10-paper-build/` directly maintains nine Skills for research reasoning, evidence design, analysis, manuscript construction, editing, and figures. They are peer components: none is nested under `academic-figure-workflow`, and they are not part of the six-component project-governance architecture in `20-project-build/`.

## Selection guide

| Skill | Owns | Does not own |
|---|---|---|
| [`research-logic`](research-logic-skill/) | Diagnose shallow module stacking and build mechanism-level research logic with defensible contribution claims | Implementation or invented results |
| [`experiment-design`](experiment-design-skill/) | Derive research questions, hypotheses, evidence gaps, datasets, baselines, ablations, metrics, controls, and claim boundaries from a claim | Experiment execution, runners, or runtime gates |
| [`data-analysis`](data-analysis/) | Check experimental-data integrity, choose statistical tests, and report effect sizes, intervals, and reviewable interpretations | Turning missing or unreliable data into confident conclusions |
| [`research-html-report`](research-html-report/) | Package research logic, evidence plans, and risks as a standalone HTML research report | Replacing research design or manufacturing evidence |
| [`latex-paper-build-skill`](latex-paper-build-skill/) | Build, restructure, and maintain a LaTeX-centered paper-delivery pipeline | Changing scientific content without author approval |
| [`paper-polishing-skill`](paper-polishing-skill/) | Translate, restructure, and polish approved scientific content for Nature, PRL, or PRA | Inventing data, citations, mechanisms, or stronger claims |
| [`prl-manuscript-polisher`](prl-manuscript-polisher/) | Adapt, compress, and evidence-calibrate a technically complete physics manuscript for PRL | Hiding weak evidence behind stronger prose |
| [`academic-figure-workflow`](academic-figure-workflow/) | Plan, create, validate, and package editable, traceable academic figures | Inventing data, mechanisms, modules, or visual evidence |
| [`interactive-skill-builder`](interactive-skill-builder/) | Create or update Codex Skills through interviews, approved specifications, gates, and validation | Skipping author confirmation to generate a final Skill |

## Recommended compositions

The main sequence is not mandatory. Choose the smallest combination that closes the current gap:

```text
research idea
  -> research-logic
  -> experiment-design
  -> experiment execution (owned by project code or a dedicated execution Skill)
  -> data-analysis
  -> research-html-report (optional research brief)
  -> latex-paper-build-skill
  -> paper-polishing-skill
  -> prl-manuscript-polisher (PRL targets only)

paper claim / code / data
  -> academic-figure-workflow
  -> editable source + exports + caption + QA
```

The endpoint of `experiment-design` is a precise account of what must be tested, which evidence is missing, which controls are required, and how far the resulting claim may extend. It does not implement experiment runners, replace the project runtime, or grant execution, publication, or claim authority.

## Migration note

On 2026-09-24, this directory imported eight Skills from the `main` snapshot of the retired `jiaqi-Sun2020/S_paper_skills` repository (source commit `dcd573b1768e48e794975100f8548dc0f1bcb50e`). The import retains a source snapshot, not the old commit history; all old repository refs were saved separately in a Git bundle before retirement.

Path mapping:

| Old path | New path |
|---|---|
| `research-logic-skill/` | `10-paper-build/research-logic-skill/` |
| `experiment-design-skill/` | `10-paper-build/experiment-design-skill/` |
| `data-analsys-skill/` | `10-paper-build/data-analysis/` |
| `latex-paper-build-skill/` | `10-paper-build/latex-paper-build-skill/` |
| `paper-polishing-skill/` | `10-paper-build/paper-polishing-skill/` |
| `util_skills/research-html-report/` | `10-paper-build/research-html-report/` |
| `util_skills/interactive-skill-builder/` | `10-paper-build/interactive-skill-builder/` |
| `util_skills/prl-manuscript-polisher/` | `10-paper-build/prl-manuscript-polisher/` |

The original repository's MIT notice is retained in [`S_PAPER_SKILLS_LICENSE`](S_PAPER_SKILLS_LICENSE). These Skills are directly maintained hub sources and are not added to the Skill Registry's immutable `releases/`.

## Validation

Run from the repository root:

```powershell
Get-ChildItem .\10-paper-build -Directory | ForEach-Object {
    if (Test-Path (Join-Path $_.FullName 'SKILL.md')) {
        python -X utf8 -B "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" $_.FullName
    }
}

python -X utf8 -B -m py_compile `
  .\10-paper-build\latex-paper-build-skill\scripts\create_paper_pipeline.py `
  .\10-paper-build\latex-paper-build-skill\scripts\scaffold_latex_paper.py `
  .\10-paper-build\prl-manuscript-polisher\scripts\audit_tex.py
```
