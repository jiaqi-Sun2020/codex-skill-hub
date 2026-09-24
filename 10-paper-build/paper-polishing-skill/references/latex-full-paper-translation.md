# Full LaTeX Paper Translation

Use this reference for whole-manuscript Chinese-to-English translation or English-version generation from `.tex` sources.

## Borrowed Workflow Pattern

Borrow the robust document-handling discipline of GPT-Academic-style LaTeX translation tools: split the paper into translation-safe units, preserve LaTeX syntax through the whole pass, maintain terminology consistency, and validate the rebuilt document before reporting completion. Do not copy external prompt text verbatim; translate the pattern into this skill's claim-safety and LaTeX-preservation rules.

## Preflight

1. Identify the active main `.tex`, `.bib`, figure directory, document class, build command, labels, citations, equations, tables, and figures.
2. Read the sibling `../latex-paper-build-skill/SKILL.md` when available to preserve the project layout and build conventions.
3. Decode and write `.tex` as UTF-8 first; on Windows, set `PYTHONUTF8=1` for Python-based extraction, validation, and rebuild scripts. Fall back to `gb18030`/`cp936` only if UTF-8 fails and record that exception.
4. If a prior English version exists, verify whether its Chinese source is identical to the current source. When it is identical, reuse it as the safest base, then polish it instead of retranslating from scratch.
5. Create a new English output file or directory. Do not overwrite the source manuscript unless explicitly requested.

## Translation Unit Rules

- Translate by logical units: title, abstract, section heading, paragraph, caption, table note, and algorithm prose.
- Preserve LaTeX commands, labels, citations, math environments, equation bodies, table values, figure paths, BibTeX hooks, comments that are structural, and custom macros.
- Translate captions and visible prose while keeping `\includegraphics`, `\label`, `\ref`, `\eqref`, `\cite`, and numeric values unchanged.
- Keep section order, subsection order, paragraph argument order, and figure/table evidence order unchanged unless the user explicitly asks for structural rewriting.
- Keep a terminology ledger for method names, abbreviations, datasets, metrics, symbols, model variants, and physical concepts.

## Logic-Link Polish

Chinese academic prose often leaves sentence relations implicit. Make the relation explicit only when it is already supported by the source. For whole-paper translation, prefer paragraph-level argument reconstruction over isolated sentence compression:

- argument progression: scene -> mechanism -> data-shape change -> task reformulation -> model requirement;
- contrast: `however`, `by contrast`, `whereas`;
- mechanism: `this arises because`, `this reflects`, `this mechanism`;
- consequence: `therefore`, `as a result`, `this enables`;
- scope: `under this setting`, `within this regime`, `for the tested cases`;
- boundary: `does not hold uniformly`, `is conditional on`, `should not be interpreted as`.

Avoid adding new premises, new limitations, new causal claims, or new statistical significance. Expand implicit links only when they are already present in the Chinese source. Avoid over-strong explanations such as `should have been sampled` or `unknown timestamps` when the source only says fixed-interval sampling or uncertain valid-step positions.

## Academic Diction

Prefer precise verbs that match evidence strength:

- Use `propose`, `construct`, `derive`, `evaluate`, `compare`, `observe`, `indicate`, `suggest`, and `examine`.
- Use `demonstrate` only when the evidence directly supports a completed claim.
- Avoid casual or inflated wording such as `greatly`, `obviously`, `perfect`, `prove`, and `breakthrough` unless the source explicitly supports it.
- Prefer stable technical forms: `continuous-time quantum walk`, `normalized Laplacian`, `spectral phase modulation`, `valid observation interval`, `missingness pattern`, `gated residual fusion`.

## Validation

Before finalizing a translated `.tex` manuscript:

1. Check that no unintended Chinese prose remains.
2. Compare structural anchors against the source: document class, section labels, figure labels, table labels, equation labels, citations, bibliography command, and major environments.
3. Confirm that equations, numeric table values, figure paths, labels, and citations are preserved.
4. Compile with the project build command when tools are available. If compilation is unavailable, report that explicitly and provide the exact command to run.
5. Summarize only language-level changes and any unresolved author checks.
