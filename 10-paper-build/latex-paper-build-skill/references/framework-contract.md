# LaTeX Framework Contract

Use this contract when generating or reviewing a managed LaTeX paper framework.

## Target Tree

```text
paper_latex_framework/
  paper_config.json
  main.tex
  preamble.tex
  frontmatter.tex
  backmatter.tex
  latexmkrc
  sections/
    01_introduction.tex
    02_background.tex
    ...
  figures/
    referenced-figure-files
  references/
    paper.bib
  notes/
    paper_context.md
```

## File Responsibilities

- `paper_config.json`: root metadata source for title, short title, authors, affiliations, correspondence address/email, venue, keywords, acknowledgments, and author-review abstract.
- `main.tex`: orchestration only. It should contain `\input{preamble}`, `\begin{document}`, `\input{frontmatter}`, section inputs, `\input{backmatter}`, and `\end{document}`.
- `preamble.tex`: document class, numbering policy, packages, theorem definitions, and macros.
- `frontmatter.tex`: generated from or checked against `paper_config.json`; contains title, authors, affiliations, date, abstract, keywords when supported, and `\maketitle` policy.
- `sections/*.tex`: one top-level section per file. Preserve labels and internal subsection structure.
- `backmatter.tex`: bibliography style, bibliography command, acknowledgments, appendices, and any final material.
- `figures/`: the single folder for all figure and image assets referenced by the generated framework unless the user asks for archival copy.
- `references/`: `.bib` databases used by the paper. Do not manage literature through inline bibliography blocks in generated frameworks.
- `notes/paper_context.md`: generated structure report and known mechanical issues.

## Generation Rules

- Generate into a new directory by default.
- Write UTF-8 text files.
- Create or preserve `paper_config.json` before writing frontmatter metadata.
- Keep source prose unchanged when splitting.
- Keep labels unchanged unless fixing duplicates with explicit user approval.
- Keep citation keys unchanged.
- Manage all literature in `.bib` files, typically under `references/`; do not emit inline `thebibliography`.
- Rewrite bibliography paths only when the generated file layout requires it.
- Put every copied figure or image under `figures/` and rewrite figure paths only when the corresponding file has been copied.
- Prefer short, stable slugs: `01_introduction.tex`, `02_background.tex`, `03_model.tex`, `04_experiments.tex`, `05_conclusion.tex`.

## Build Rules

- Use `latexmk -xelatex -bibtex -interaction=nonstopmode -file-line-error -outdir=build main.tex` for `ctex` or `fontspec` papers.
- Use `latexmk -pdf` only when the paper has no Unicode/fontspec dependency.
- Keep build artifacts out of manuscript source folders.
- After compilation, inspect `.log` warnings for undefined references, missing citations, missing figures, overfull boxes, and font warnings.