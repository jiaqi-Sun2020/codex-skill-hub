---
name: paper-polishing-skill
description: Translate, polish, and structurally revise author-approved scientific manuscripts for Nature, PRL, and PRA style. Use when Codex needs to turn a Chinese author-review manuscript or full LaTeX paper into final English after user approval, polish English manuscript prose, improve inter-sentence logic and academic diction, audit PRL/PRA/Nature section logic, protect claims, preserve LaTeX labels/citations/equations, integrate with latex-paper-build-skill workflows, or enforce journal-specific abstract, title, introduction, results, discussion, and conclusion moves without inventing evidence.
---

# Paper Polishing Skill

## Purpose

Use this skill after the scientific content of a manuscript has been drafted or reviewed. It owns post-review language transformation and polishing, not experiment invention. It can polish English drafts directly, but its default role inside the hub's `10-paper-build` workflow is:

```text
Chinese author-review manuscript
-> user scientific/content approval
-> journal-targeted English translation and polishing
```

This skill inherits the discipline of `nature-polishing`: fix the argument before the sentence, protect the author's scientific core, and never hide weak logic under fluent prose. It extends that stance to PRL and PRA in addition to Nature-family writing.

## Hard Gates

- Do not perform a full Chinese-to-English final manuscript translation until the user states that the Chinese scientific content is approved or asks explicitly to translate despite pending review.
- Do not invent data, citations, baselines, theory, mechanisms, novelty claims, or limitations.
- Do not upgrade a planned, partial, or missing result into a completed result.
- Do not change the manuscript's scientific logic, argument architecture, section order, equations, experimental design, table values, figure evidence, or claim hierarchy when the user asks only for translation or polishing.
- Preserve numeric values, units, equations, figure/table references, LaTeX labels, citation keys, and BibTeX workflow unless the user explicitly asks for a technical correction.
- Treat Chinese manuscripts, `.tex` sources, and skill guidance as UTF-8 by default; on Windows, set `PYTHONUTF8=1` before Python-based reading, validation, or transformation.
- When evidence is incomplete, keep the boundary visible in the polished output and revision notes.

## Workflow

1. Identify the target journal style and task mode.
   - `nature`: broad conceptual significance, non-specialist accessibility, strong but bounded significance.
   - `prl`: one central physics result, fast motivation, compact evidence chain, strict claim discipline.
   - `pra`: complete physics context, reproducible method detail, careful notation, mechanisms, limitations, and parameter regimes.
   - `generic`: clear scientific English without venue-specific compression.
   - Modes: Chinese-to-English finalization, English polishing, section logic audit, title/abstract polish, LaTeX-safe revision.
2. Build a terminology ledger before rewriting.
   - Record canonical method names, abbreviations, physical quantities, metrics, datasets, symbols, and notation.
   - Use one canonical form throughout; do not vary technical terms for style.
3. Diagnose the highest-level problem first.
   - Paper type and venue fit.
   - Section job.
   - Paragraph logic.
   - Claim, evidence, boundary.
   - Sentence-level polish.
4. Load only the needed references.
   - Always read `references/claim-safety.md`.
   - For Nature, PRL, PRA, or target-style work, read `references/journal-styles.md`.
   - For Chinese drafts or Chinese-influenced English, read `references/translation-workflow.md`.
   - For `.tex` files or LaTeX snippets, read `references/latex-preservation.md`.
   - For whole-paper `.tex` translation or English-version generation, read `references/latex-full-paper-translation.md` and, when available, the sibling `../latex-paper-build-skill/SKILL.md`.
5. Rewrite in controlled passes.
   - Extract propositions and evidence before drafting prose.
   - Reconstruct missing logical links without adding new science.
   - Improve sentence-to-sentence links by making only source-supported relations explicit: contrast, mechanism, consequence, scope, condition, and transition.
   - Avoid over-compressed sentence-by-sentence translation. Rebuild paragraphs as academic argument units with an explicit progression such as scene -> mechanism -> data-shape change -> task reformulation -> model requirement.
   - Apply venue-specific compression or expansion.
   - Prefer precise academic diction over literal translation, but keep technical terminology stable across the manuscript.
   - Polish sentence mechanics last.
   - Report structural changes and unresolved evidence gaps.

## Output Contract

For passage-level work, return:

1. Polished text.
2. `Terminology ledger:` when a ledger is new or changed.
3. `Revision notes:` with 3-5 short bullets on logic, style, and claim-boundary changes.
4. `Needs author check:` only for unresolved scientific or terminology decisions.

For whole-manuscript or LaTeX work, preserve the user's file structure unless they ask for a rewrite. Prefer creating a sibling English file such as `<main>_EN.tex` and keep the original source untouched. If editing files, keep references in `.bib` files and figures in `figures/` according to the paper-build rules.
