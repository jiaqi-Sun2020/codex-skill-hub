# QCT Standalone main.tex Reference

Read this reference when the user asks for a fresh QCT/QWCT paper framework, a complete editable `main.tex`, or a manuscript rebuilt from `QCT_run_all` experiment outputs. Chinese trigger phrases include "重新构建一个框架", "完整的 main.tex", "可供我编辑", and requests to treat `back/` or previous manuscripts as history.

## Required Behavior

- Before drafting the abstract, introduction, contribution paragraph, results overview, or discussion boundary, read `qct-writing-methodology.md` and apply its claim ladder and terminology rules.

- Generate non-destructively. Use a new manuscript directory such as `05_manuscript_qct/`, `manuscript_qct/`, or another clearly named sibling of the existing manuscript.
- Create or preserve root-level `paper_config.json` for title, authors, affiliations, correspondence address/email, keywords, venue, acknowledgments, and abstract metadata.
- Do not overwrite or mechanically rewrite an old QWTA, traffic-assignment, or legacy manuscript into a QCT paper. Mention it only as historical background when useful.
- Prefer a standalone `main.tex` when the user asks for a complete editable file. In this mode, keep the preamble, frontmatter, section skeleton, tables, equations, BibTeX hook, and TODO markers in one file.
- Add a sibling `latexmkrc` when the directory is new and the project uses `ctex`, `fontspec`, or RevTeX.
- Manage all literature through `.bib` files, normally under `references/`; do not generate inline `thebibliography` for QCT drafts.
- Put all manuscript images in one `figures/` folder, and make every generated `\includegraphics` path point to `figures/<file>`.
- Update the paper pipeline context if one exists, pointing the manuscript stage to the new standalone file.

## Source Inputs To Inspect

Use only verified local evidence. Prefer these sources when present:

- Project `.agents/` files for high-level context and boundary decisions.
- `QCT_run_all/.agents/`, README files, experiment specs, logs, and summary artifacts for experiment details.
- Reports under the pipeline, especially `04_reports/*.html` and `04_reports/*.zh.html`.
- Experiment outputs under `QCT_run_all/experiments` in read-only fashion unless the user asks to edit experiment code.
- Existing manuscripts only for style, package conventions, and historical contrast.

## Standalone main.tex Contract

The generated `main.tex` should be immediately editable by the researcher and compile-oriented even if citations and figures remain placeholders.

Include:

- RevTeX-compatible documentclass unless the venue says otherwise.
- For Chinese PRA author-review drafts, use `\documentclass[aps,pra,reprint,groupedaddress]{revtex4-2}` with `ctex`, explicit `fontspec`, `amsmath`, `amssymb`, `graphicx`, and `xcolor`.
- For final English PRA drafts, use `\documentclass[aps,pra,reprint,superscriptaddress]{revtex4-2}` with `amsmath`, `amssymb`, `graphicx`, and `xcolor`, and do not load `ctex` or `fontspec` unless the English manuscript still contains Chinese text.
- XeLaTeX-friendly Chinese support with `ctex` or `fontspec` when Chinese text is present.
- A QCT/QWCT-specific title, author placeholders, abstract placeholder, and keyword placeholders driven by `paper_config.json` when available. The abstract must follow `qct-writing-methodology.md`: scoped opening, explicit contribution, method summary, evidence hierarchy, and formal limitation language.
- A notation table or short notation paragraph for coin dimension, step count, position basis, measurement probability, transfer matrix, and reconstruction variable.
- Core problem equations: coin state, walk unitary, measurement map, vectorized linear system, inverse or regularized estimator, and fidelity metric.
- A current-evidence table populated only with values verified from local outputs or reports.
- Results subsections that read each planned or available figure/table in the main text: state the trend, comparison, interpretation, mechanism, and scoped caveat instead of only reporting numbers.
- Separate sections for introduction, related work/theoretical background, method, experimental protocol, current results, next experiments, discussion/limitations, and conclusion.
- TODO markers for missing baselines, statistics, ablations, noise robustness, figure generation, and references.
- A BibTeX hook such as `\bibliographystyle{apsrev4-2}` and `\bibliography{references/references}`; all references must be maintained in `.bib` files.
- A figure-path convention or TODO list for planned figures; all image assets should live in `figures/`.

## Default Section Map

Use this order unless the user's paper structure is more specific:

1. Introduction and contributions, using the five-paragraph introduction method from `qct-writing-methodology.md`.
2. QCT measurement model.
3. Reconstruction method and numerical implementation.
4. Experimental protocol and datasets/configurations.
5. Results from completed experiments, expanded as figure-by-figure and table-by-table analysis rather than a short numeric report.
6. Planned validation and ablation experiments.
7. Discussion, limitations, and scope of claims.
8. Conclusion.

## Claim Discipline

- Clearly distinguish completed experiments, partial experiments, and proposed next experiments, but keep repeated self-limitation out of the main throughline.
- Do not claim scalability, superiority, robustness, or publication-grade validation unless supported by completed runs.
- If a result comes from partial search, label it as partial and keep it out of final comparative claims.
- Convert vague paper ideas into editable TODOs instead of inventing missing numbers.

## Build Check

For the generated directory, prefer:

```powershell
latexmk -xelatex -bibtex -interaction=nonstopmode -file-line-error -outdir=build main.tex
```

If `latexmk` is unavailable, record that the file was scaffolded but not compiled. Do not spend time fixing citation warnings for placeholder references unless the user asked for a clean submission build.