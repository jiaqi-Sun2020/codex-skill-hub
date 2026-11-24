# QWCT/QWTA Paper Profile

Use this profile when working on a paper that follows the same Quantum Walk Temporal Architecture style.

Observed on 2026-06-24:

- Main source: `2026_06_17/QWCT.tex`
- Bibliography file present: `2026_06_17/QWCT_cite.bib`
- Figure root: `2026_06_17/fig/`
- Citation PDFs: `2026_06_17/cite/`
- Class: `\documentclass[aps,prl,twocolumn,groupedaddress]{revtex4-2}`
- Section numbering: Roman sections and alphabetic subsections.
- Language/runtime: Chinese manuscript text with `ctex` and `fontspec`; compile with XeLaTeX or LuaLaTeX, prefer XeLaTeX.
- Packages observed: `ctex`, `fontspec`, `amsmath`, `amssymb`, `amsthm`, `algorithm`, `algorithmic`, `float`, `xcolor`, `graphicx`.
- Bibliography style: `apsrev4-2`.
- Known drift: source contains `\bibliography{QWTA_cite}`, while the actual `.bib` file is `QWCT_cite.bib`. Generated frameworks should point to the available bibliography file unless the user confirms a rename; all literature must remain `.bib` managed.

Paper identity:

- Topic: Continuous-time quantum walk propagation for irregular temporal graph neural networks.
- Core method names: QWTA, QWTA-Base, QWTA-GR.
- Theory backbone: normalized graph Laplacian, CTQW spectral evolution, phase modulation by irregular observation intervals.
- Evaluation domain: METR-LA traffic prediction under controlled missing-history / irregular-observation settings.

Current top-level structure:

1. Introduction
2. Theoretical Background
3. QWTA Model
4. Experiments
5. Conclusion

Current major subsections:

- Graph propagation in graph neural networks.
- Continuous-time quantum walk.
- Mapping CTQW to graph neural network propagation operators.
- Raw information preprocessing and encoding.
- Quantum evolution process.
- Nonlinear activation and output layer.
- Gated residual fusion extension: QWTA-GR.
- QWTA full forward propagation.
- Training setup.
- Baseline comparison and main results.
- Model complexity.
- Phase soft-clipping propagation analysis.
- Module ablation.
- Quantum gate circuit design.

Figure and table assets referenced by the source include:

- `fig/irregular_graph_snapshots.pdf`
- `fig/model.png`
- `fig/fig_learned_eta_by_mask.pdf`
- `fig/fig_hin_raw_s_vs_F.pdf`
- `fig/fig_ablation_bar_no_diffusion_fixtime.png`
- `fig/fig_test_mse_qwta_mechanism.pdf`
- `fig/quantum_flow.png`

Practical handling notes:

- PowerShell `Get-Content` may display mojibake for UTF-8 files without BOM. Prefer `rg` for quick inspection or explicitly read as UTF-8.
- Keep figure paths stable during in-place edits; when scaffolding, copy referenced assets into the single `figures/` folder and rewrite `./fig/...` to `figures/...` only after copying the referenced file.
- Preserve labels verbatim during splitting. Some labels intentionally preserve old names to avoid breaking citations.
- This paper is currently a monolithic source. The preferred architecture is a generated copy with modular sections, not an in-place split of the original manuscript.
