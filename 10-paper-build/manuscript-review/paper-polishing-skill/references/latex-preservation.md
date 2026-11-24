# LaTeX Preservation

Use this reference when polishing `.tex` files or LaTeX snippets.

## Preserve Structure

- Keep `\label{}`, `\ref{}`, `\eqref{}`, `\cite{}`, `\bibliography{}`, and `\bibliographystyle{}` intact unless the user asks for structural edits.
- Do not replace BibTeX with inline `thebibliography`.
- Keep manuscript figures in `figures/` and literature in `.bib` files when working inside the hub's `10-paper-build` pipeline.
- Do not change equation semantics while polishing surrounding prose.
- Keep macro names and custom commands intact.

## Safe Edits

- Improve prose inside section bodies, abstracts, captions, and comments.
- Clarify figure and table callouts without changing labels.
- Normalize terminology around equations while preserving symbols.
- Flag broken references rather than guessing new keys.

## Whole-Manuscript Output

For full translation or polish, prefer a new output file or directory unless the user explicitly asks to overwrite the source. Keep an author-facing change summary with any major structural rewrites.
