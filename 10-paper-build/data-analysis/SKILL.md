---
name: data-analysis
description: Analyze experimental datasets and paper results with statistically defensible code, integrity checks, significance tests, effect sizes, confidence intervals, and report-ready interpretation. Use when Codex is asked to analyze CSV/JSON/NPZ/pickle/log/result tables, compare methods, validate whether results support a paper claim, choose statistical tests, generate p-values/effect sizes/CI, audit data provenance, or write a data-analysis section for research.
---

# Data Analysis

Use this skill to turn raw experimental outputs or result tables into defensible analysis artifacts for research work.

## Core Workflow

1. Clarify the analysis target.
   - Identify the data source, response metric, grouping variables, repeated-measure structure, seeds/runs, and claim being tested.
   - If these are missing and cannot be inferred from files, ask concise questions before running statistics.

2. Inspect data before analysis.
   - Load data from original files, not copied summaries unless the user explicitly asks for summary-only analysis.
   - Record row counts, columns, missing values, units, duplicate keys, seeds, dataset names, and method labels.
   - Check whether each result is raw, normalized, averaged, or already post-processed.

3. Choose tests by design.
   - Read `references/statistical-test-selection.md` when selecting statistical tests.
   - Prefer paired tests when methods share the same seeds, folds, subjects, datasets, scenes, or tasks.
   - Report effect size and uncertainty with every significance result.

4. Run integrity checks.
   - Read `references/data-integrity-checklist.md` when results will support claims, tables, abstracts, or reports.
   - Verify ground-truth provenance, result-file existence, metric definitions, and whether any score is self-normalized.

5. Produce analysis artifacts.
   - Save reusable analysis code when the user asks for files or when the analysis is nontrivial.
   - Produce tables with nominal values plus uncertainty: CI, std, stderr, or credible intervals as appropriate.
   - Produce interpretation that separates observed result, statistical support, practical effect size, and claim boundary.

6. Review before claiming.
   - Perform a short self-review for code bugs, data handling mistakes, inappropriate tests, and overclaimed language.
   - If evidence is weak, say so directly and propose the next data collection or analysis step.

## Output Contract

For a complete analysis, include:

- Data provenance: files, row counts, metric columns, filters, and exclusions.
- Descriptive summary: central tendency, uncertainty, and sample size per group.
- Statistical test: test name, reason, assumptions, p-value, effect size, confidence interval when possible.
- Integrity status: pass/warn/fail for provenance, metric validity, result existence, and scope.
- Claim impact: supported, partially supported, unsupported, or requires more evidence.
- Reproducible artifacts: generated script paths, tables, figures, or JSON summaries if files are created.

Use `references/report-template.md` when writing a report-style answer.

## Approval Gates

Ask the user before:

- Modifying or deleting original data.
- Overwriting existing analysis outputs, tables, or reports.
- Running long jobs, external reviewers, network calls, or expensive computations.
- Treating proxy/simulation-only results as real ground truth.

## Analysis Code Rules

- Use pandas, numpy, scipy, statsmodels, sklearn, or standard Python when available.
- Use library implementations for statistical tests; do not hand-roll standard tests.
- Access DataFrame columns by names, not positional integer indices, unless the file has no headers.
- Preserve random seeds and filters in the script or report.
- Do not invent missing metrics, p-values, sample sizes, or confidence intervals.
- If a test assumption fails, switch tests or clearly label the limitation.

## Reference Routing

- Statistical test selection: `references/statistical-test-selection.md`
- Data/result integrity audit: `references/data-integrity-checklist.md`
- Report format: `references/report-template.md`
