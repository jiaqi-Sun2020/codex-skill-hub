---
name: latex-paper-build-skill
description: Build, restructure, and maintain complete research-paper delivery pipelines centered on LaTeX manuscripts. Use when Codex needs to inspect an existing .tex paper, generate a project-specific LaTeX scaffold, create a standalone editable main.tex, split a monolithic manuscript into modular files, preserve revtex/ctex/fontspec/BibTeX conventions, enforce .bib reference management and a single figures/ folder, check figure and bibliography paths, choose XeLaTeX/latexmk build commands, or orchestrate a full paper workflow from research logic, experiment design, evidence analysis, optional academic-figure production, HTML research reports, config-driven paper metadata, manuscript architecture, compilation, and submission checks. Also use for QCT/QWCT coin-state tomography manuscripts derived from experiment-code outputs or research reports, especially when the manuscript needs narrative QA for self-interrupted claims, thin result sections, or figures/tables that are not sufficiently read in the main text.
---

# LaTeX Paper Build Skill

## Overview

Use this skill to turn a research idea, experiment-code output, or LaTeX paper directory into a maintainable paper-delivery pipeline without overwriting the original source. The default target is a scientific manuscript with research notes, experiment plans, training outputs, reports, a root-level `paper_config.json`, `main.tex`, `preamble.tex`, `frontmatter.tex`, modular `sections/`, one shared `figures/` folder, `references/` containing `.bib` databases, `notes/`, and a reproducible build path. When the user explicitly asks for a complete editable `main.tex` or a rebuilt QCT/QWCT manuscript framework, generate a standalone manuscript file instead of forcing a modular split.

## Bundle Pipeline Rule

Inside the hub's `10-paper-build` workflow, paper-pipeline author-review output defaults to Chinese prose while preserving PRL/PRA reasoning logic. Final English manuscript translation and Nature/PRL/PRA style polishing are approval-gated and belong to `paper-polishing-skill` after the user has reviewed the Chinese scientific content.

## Workflow

1. Discover the paper context before editing.
   - Find the main `.tex`, `.bib`, figure directories, compiled PDFs/logs, and venue class.
   - Prefer `rg --files`, then inspect `\documentclass`, packages, `\title`, `\section`, `\includegraphics`, `\bibliographystyle`, and `\bibliography`.
   - Treat `.bib` files as the sole literature source for generated frameworks, and plan to consolidate manuscript images under one `figures/` folder.
   - If figure packages already exist, inventory editable sources, exports,
     captions, evidence traces, style manifests, and unresolved QA separately
     from the manuscript's use of those figures.
   - If the project is the QWCT/QWTA paper under `2026_06_17`, read `references/qwct-paper-profile.md`.
   - If creating or reorganizing a framework, read `references/framework-contract.md`.
   - If the paper needs authors, affiliations, corresponding address, contact email, keywords, venue, or acknowledgments configured centrally, read `references/paper-config.md`.
   - If the user asks for a complete standalone `main.tex`, a fresh QCT/QWCT framework, or a manuscript based on `QCT_run_all` experiment outputs, read `references/qct-standalone-maintex.md`.
   - If drafting or revising the QCT/QWCT abstract, introduction, contribution, results framing, terminology, or claim boundary, read `references/qct-writing-methodology.md`.
   - If the user reports that the main line is repeatedly interrupted by self-limiting caveats, that results only list numbers, or that figures/tables carry evidence the main text does not read, read `references/qct-writing-methodology.md` even if the visible task is a LaTeX scaffold or `main.tex` rebuild.

2. Choose the operation.
   - Full paper pipeline: read `references/paper-pipeline.md` and use the sibling skills listed there when available.
   - Existing monolithic paper: run `scripts/scaffold_latex_paper.py` with `--source`; use `--copy-figures` for managed manuscript frameworks so image assets are copied into `figures/`.
   - Pipeline workspace: run `scripts/create_paper_pipeline.py`; edit or pass `--paper-config` when author/affiliation metadata should drive `frontmatter.tex`.
   - New paper with similar conventions: copy or adapt `assets/revtex-qwct-template/`.
   - Standalone editable `main.tex`: when requested, create a fresh non-destructive manuscript directory and put the preamble, frontmatter, sections, evidence tables, TODO markers, and BibTeX hook in one file.
   - Compile/debug request: preserve the current file layout, then run the build command and fix only the failing surface.
   - Writing-only request: defer to the user's writing skill or local paper-writing rules; this skill owns architecture, paths, and build mechanics.

3. Generate the framework non-destructively.
   - Never overwrite the original manuscript unless the user explicitly asks.
   - Create a new output directory such as `<paper>_latex_framework`.
   - Keep root-level `paper_config.json` as the source of truth for title, authors, affiliations, correspondence address/email, keywords, venue, acknowledgments, and author-review abstract.
   - Keep one source of truth for packages in `preamble.tex`.
   - Keep title/authors/abstract in `frontmatter.tex`.
   - Keep each top-level section in `sections/NN_slug.tex`.
   - Exception: when a complete standalone `main.tex` is explicitly requested, keep all editable manuscript content in `main.tex` and place it in a new directory such as `05_manuscript_qct/`.
   - Manage all literature through `.bib` files. Create or copy the active `.bib` file into `references/` and use `\bibliographystyle` plus `\bibliography`; do not emit inline `thebibliography` in generated frameworks.
   - Move/copy cited `.bib` files into `references/` and update `\bibliography{references/<stem>}`.
   - Keep all manuscript images in a single `figures/` folder. After copying referenced graphics, rewrite `\includegraphics` paths to `figures/<file>` and avoid new `fig/`, `images/`, or source-local image roots.
   - Copy only referenced figures into `figures/` unless the user asks for the whole asset tree.

4. Validate the result.
   - Run `python -m py_compile scripts/scaffold_latex_paper.py` after script edits.
   - Run the skill validator after skill edits:
     `python (Join-Path ([Environment]::GetFolderPath('UserProfile')) '.codex\skills\.system\skill-creator\scripts\quick_validate.py') "<skill-dir>"`
   - For generated LaTeX frameworks, prefer:
     `latexmk -xelatex -bibtex -interaction=nonstopmode -file-line-error -outdir=build main.tex`
   - If `latexmk` is unavailable, use `xelatex`, `bibtex`, `xelatex`, `xelatex`.
   - For QCT/QWCT manuscript regeneration, run a narrative QA pass before finalizing: check main-line continuity, result-section interpretation depth, and whether each figure/table is explicitly read in the main text rather than left to carry the argument alone.
   - When figure work is applicable, verify that the manuscript uses exports
     from the one canonical `figures/` root and that each submission-facing
     figure has an editable source or documented exception, a caption,
     evidence trace, final-size QA, and explicit unresolved issues.
   - Treat figure-package QA and scientific claim review as separate states. A
     visually verified figure does not prove the claim it illustrates.

## Script Entry Point

Create a complete pipeline workspace:

```powershell
python scripts\create_paper_pipeline.py --project path\to\paper_pipeline --title "Paper Title"
```

Attach an existing LaTeX manuscript to that pipeline:

```powershell
python scripts\create_paper_pipeline.py --project path\to\paper_pipeline --title "Paper Title" --paper-config path\to\paper_config.json --latex-source path\to\paper.tex --bib path\to\refs.bib --copy-figures
```

Generate only the LaTeX framework:

Use:

```powershell
python scripts\scaffold_latex_paper.py --source path\to\paper.tex --bib path\to\refs.bib --out path\to\paper_latex_framework --copy-figures
```

Useful options:

- `--inspect-only`: print a Markdown structure report without writing a framework.
- `--force`: allow overwriting files inside the output directory.
- `--copy-figures`: copy referenced figure files into the single `figures/` folder and rewrite include paths.
- `--paper-key`: override the generated project key used in reports.

## Build Rules

- Use XeLaTeX when the paper loads `ctex` or `fontspec`.
- Preserve `revtex4-2` options unless the user asks for a venue change.
- Preserve labels, citations, equations, algorithms, captions, and section content verbatim during scaffolding.
- For QCT/QWCT standalone frameworks, do not patch an old QWTA or traffic-assignment manuscript into a QCT paper. Treat old files and `back/` as historical background, then build a new manuscript around verified experiment code, reports, and explicit TODOs.
- Treat bibliography drift as a build issue. For example, if the source says `\bibliography{QWTA_cite}` but the available file is `QWCT_cite.bib`, rewrite the generated framework to the available `.bib` and report the drift.
- Treat inline `thebibliography` in generated frameworks as bibliography drift; migrate it to `.bib`.
- Treat generated figure paths outside `figures/` as layout drift; copy the asset into `figures/` and rewrite the path when the file is available.
- Do not silently convert Chinese text encodings. Read as UTF-8 first, then fall back to `gb18030`/`cp936`; write generated framework files as UTF-8.


## Narrative QA Rules

Apply these rules whenever generating or revising the scientific content of a QCT/QWCT manuscript, not only when editing prose by hand:

- Preserve a clear positive throughline. Put scope limits in designated boundary paragraphs, discussion, or limitations, rather than interrupting every claim with defensive caveats. A scoped claim should still read as a claim.
- Expand results as analysis, not as a numeric ledger. Each major result paragraph should state the question, describe the comparison, interpret the trend, connect it to the walk/measurement mechanism, and only then give representative numbers.
- Read every figure and table in the main text. Captions and tables are not substitutes for prose interpretation. For each figure/table, the main text should identify the axes or columns, the dominant trend, the key comparison, the scientific implication, and any local caveat.
- When rebuilding `main.tex`, create enough result-section scaffolding for figure-by-figure reading paragraphs, even if some numeric slots remain TODOs.


## Research Writing Workflow Borrowing

Borrow the staged-writing discipline from `alfonso0512/research-writing-skill`: literature/context intake, outline, section expansion, abstract/introduction/method drafting, result interpretation, figure/table captioning, logic checking, and reviewer simulation. In this skill, translate those prompt stages into durable artifacts under the paper pipeline rather than copying prompt templates verbatim. Preserve the local rule that Chinese author-review output comes first and English polishing is approval-gated.
## Pipeline Integration

When this skill lives inside a skill hub such as `10-paper-build`, treat sibling skills as pipeline stages rather than duplicated content. Read only the sibling `SKILL.md` needed for the active stage:

- `../research-logic-skill/SKILL.md` for contribution logic and mechanism-level claims.
- `../experiment-design-skill/SKILL.md` for paper-grade validation plans.
- `../data-analysis/SKILL.md` for data integrity, statistical analysis,
  uncertainty, and claim-support assessment before quantitative figure work.
- `../academic-figure-workflow/SKILL.md` for the optional figure-evidence lane:
  figure arguments, editable sources, style, exports, captions, source trace,
  and rendered QA. Inside a generated pipeline, its single figure root is
  `05_manuscript_zh/figures/`.
- `../research-html-report/SKILL.md` for shareable research briefs and publication-style HTML reports.
- `../paper-polishing-skill/SKILL.md` for post-approval Chinese-to-English translation and Nature/PRL/PRA manuscript polishing.
- `references/paper-config.md` for config-driven title, author, affiliation, correspondence, keyword, acknowledgment, and abstract metadata.
- `references/qct-writing-methodology.md` for reusable QCT/QWCT abstract, introduction, contribution, result-framing, terminology, and claim-boundary methodology.

Do not copy all sibling skill instructions into context by default. Use `references/paper-pipeline.md` as the routing contract.

This skill orchestrates figure work but does not implement drawing, plotting,
style migration, or figure-package QA. It owns manuscript placement,
cross-references, compilation, and prose interpretation only. Figure-free
papers must remain valid and must not receive empty figure metadata.

## Extensibility

Add new paper or venue behavior by adding one focused reference file under `references/` and, only when deterministic automation is needed, a script under `scripts/`. Keep `SKILL.md` as the routing layer rather than a large manual.
