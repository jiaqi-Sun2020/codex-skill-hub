---
name: research-html-report
description: Use when Codex needs to synthesize research logic, innovation points, paper outlines, experiment design, model claims, ablations, datasets, and mechanism analysis into a polished standalone HTML webpage or report. Use after research-logic or experiment-design outputs, or when the user asks to present research ideas as an HTML page, visual research brief, paper planning dashboard, shareable project summary, printable academic report, or paper-style HTML with figures, tables, equations, citations, publication-like CSS, and explicit explanations for all research, visual, formula, table, and diagram elements.
---

# Research HTML Report

## Purpose

Turn research reasoning into a polished standalone HTML report. The page must help the reader inspect the paper idea at once: motivation, claim, mechanism, innovation, experiment evidence, risks, and next steps.

Use this flow:

```text
research idea -> claim -> innovation -> mechanism -> experiment evidence -> risk boundary -> HTML report
```

This skill is an output-design layer. Use research-logic first when the contribution is unclear, and experiment-design first when the validation plan is weak.

## Design Principles

- Treat HTML as the final artifact, not a Markdown wrapper.
- Keep the report self-contained unless the user explicitly allows external assets or libraries.
- Do not invent fake results, metrics, citations, datasets, or placeholder image URLs.
- Mark missing evidence as concrete `TODO`, not as polished certainty.
- Use layout to clarify reasoning: cards for repeated claims, tables for evidence, diagrams for mechanisms, and LaTeX-style panels for formulas.
- Explain every meaningful visible element: badges, variables, arrows, colors, table columns, formula symbols, risks, abbreviations, and TODO markers.
- Keep visual design academic, restrained, readable, responsive, and print-friendly.

## Acknowledgements

This skill is inspired by:

- HTML-first thinking from [nexu-io/html-anything](https://github.com/nexu-io/html-anything).
- PubCSS-style academic HTML publishing ideas: semantic structure, counters, printable pages, figure/table/equation numbering, and citation-aware markup.

Do not copy either project's source text, branding, or stylesheet wholesale.

## Required Structure

Generate a complete `.html` file with embedded CSS. Use semantic HTML such as:

```html
<header>, <main>, <article>, <section>, <figure>, <figcaption>, <table>, <caption>, <aside>
```

Recommended sections:

1. Hero or paper header: title, one-sentence claim, status tags.
2. Motivation: problem, gap, why existing methods are insufficient.
3. Central claim: precise claim and claim boundary.
4. Innovation map: 3-5 contribution cards.
5. Method logic: state variables, transition rule, update rule, readout.
6. Deep integration: why this is not shallow module stacking.
7. Experiment design: RQs, datasets, baselines, ablations, metrics.
8. Evidence matrix: what supports each claim.
9. Risk ledger: failure modes and reviewer objections.
10. Minimum viable plan: next implementation and validation steps.
11. Citation ledger: real references if provided; otherwise explicit citation TODOs.

## Report Modes

### Research Brief

Use for shareable planning reports and visual research summaries.

Must include:

- dual-zone hero with central claim and 2-4 status cards;
- section kickers such as `Claim`, `Innovation Map`, `Method Logic`, `Experiment Design`, `Evidence Matrix`, `Risk Ledger`;
- at least one mechanism or model flow diagram;
- evidence-aware TODOs;
- risk ledger;
- next-step ledger such as `P0`, `P1`, `P2`.

### Publication Mode

Use for paper-like, printable, ACM/IEEE-inspired, lab memo, thesis note, or arXiv-style concept pages.

Must include:

- title, abstract, keywords, and contribution summary;
- numbered sections, figures, tables, equations, and references using CSS counters when useful;
- `@page` and `@media print` rules;
- readable formulas, captions, legends, and claim boundaries;
- no fake citations. If citations are missing, add `TODO: add related-work citations`.

## Formula Rules

Important equations must be bright, readable, labeled, and preferably LaTeX-style.

Do not render key formulas as dark monospace code blocks.

Use a bright formula panel:

```html
<div class="equation">
  <div class="equation-title">State transition</div>
  <div class="formula-row">
    <div class="formula-label">Inter-event evolution</div>
    <div class="math-display">\[
      \Psi(t_k^-)=\exp\!\left(-iH(t_{k-1})\Delta t_k\right)\Psi(t_{k-1}^+)
    \]</div>
    <p class="formula-note">Explain what this equation does.</p>
  </div>
  <details class="latex-source">
    <summary>LaTeX source</summary>
    <code>\Psi(t_k^-)=...</code>
  </details>
</div>
```

Rules:

- Use LaTeX display math for central formulas when the user asks for LaTeX or the method is equation-heavy.
- If using MathJax, include minimal config. If external resources are not allowed, show readable LaTeX source and explanation without relying on rendering.
- Split multi-step equations into labeled rows such as `Inter-event evolution`, `Event correction`, `Prediction readout`.
- Add a symbol legend for non-obvious symbols.
- Do not expose raw LaTeX fragments such as `t_{k-1}` in prose, tables, SVG text, captions, or status cards; use inline MathJax, HTML sub/sup, Unicode, MathML, or a clear fallback.
- Keep LaTeX source only inside formula blocks or explicit source details.

## Diagram Rules

For model or algorithm reports, include a model flow diagram near the method section.

It should show:

```text
input / event / graph
-> state encoder
-> core operator or mechanism
-> update module
-> readout
-> loss / metric / prediction target
```

Rules:

- Prefer inline SVG or CSS boxes so the report remains standalone.
- Label each stage by role, not only module name.
- Explain every node, arrow, color, branch, operator, and formula-like label in the caption or a diagram legend.
- If a diagram label contains `H(t)=f(A,w,s)`, define `H(t)`, `f`, `A`, `w`, and `s`, and say why this construction matters.
- Avoid raw LaTeX in SVG text because MathJax will not render it there.
- Avoid decorative-only diagrams.

## Chart and SVG Label Rules

Charts must be readable without text collisions.

- Reserve explicit label space before drawing bars, lines, nodes, or axes. For horizontal bar charts, keep a dedicated left label column and start the plotting area far enough to the right.
- Do not draw shapes on top of labels. If labels and shapes share an SVG, either render labels after shapes with a non-overlapping background or, preferably, separate the label column from the plotting area.
- Split long labels into short role/name text and secondary detail text. Do not force long labels into one SVG text node when they can overlap bars, values, ticks, or captions.
- Keep value labels inside the SVG viewBox. If a value label may overflow the right edge, shorten it, move it inside the bar, or increase the right margin.
- Add a caption or legend that explains label columns, color encodings, axis origin, and any scaling choices.
- Before finishing, inspect generated SVG coordinates: text x/y ranges, plot start, axis ticks, and value labels must not occupy the same visual space.

## Table Rules

Tables must be readable research artifacts.

- Use meaningful captions that explain the claim or evidence summarized.
- Do not use wide `letter-spacing`, forced all-caps, or decorative tracking in table headers.
- Preserve readable headers such as `Evidence Needed`, `Success Criterion`, and `Claim Supported`.
- Use `letter-spacing: 0`, normal casing, and natural wrapping.
- Explain non-obvious columns in the caption or a short note.
- Use tables for experiment plans, ablations, datasets, metrics, evidence matrices, risks, and next-step ledgers.

## Element Explanation Rules

Every meaningful element must answer:

```text
What is it?
Why is it here?
How should it affect the research argument?
```

Use the smallest useful explanation surface:

```text
caption -> figures and tables
symbol legend -> formulas
diagram legend -> arrows, colors, modules
status note -> badges and state labels
column note -> ambiguous table headers
inline definition -> abbreviations
```

Explain status cards, badges, colors, variables, formulas, abbreviations, method names, table fields, figure nodes, TODO markers, risks, and priority labels. Remove decorative-only elements that cannot be explained.

## Content Rules

### Central Claim

Rewrite vague ideas as:

```text
This paper claims that ___ improves/changes ___ because ___.
```

Place the claim near the top and state its boundary.

### Innovation Cards

Each card must include:

- title;
- mechanism;
- why it is new;
- validation path.

### Method Logic

Show the method as:

```text
state after previous event
-> principle-governed evolution
-> state before next event
-> event-induced correction
-> prediction
```

For CTQW dynamic graph ideas, render equations as formula panels, not code:

```text
Psi(t_k^-) = exp(-i H(t_{k-1}) Delta t_k) Psi(t_{k-1}^+)
Psi(t_k^+) = EventUpdate(Psi(t_k^-), e_k)
```

### Experiment Plan

Use tables:

```text
Research Question | Evidence Needed | Dataset | Baseline | Metric | Success Criterion
Variant | What It Tests | Expected Outcome | Claim Supported
```

### Claim Discipline

End with:

```text
If results show ___, we can claim ___.
If results show ___, we must weaken the claim to ___.
```

## Output Requirements

1. Choose a clear path, usually `reports/<topic-name>.html`.
2. Create parent directories if needed.
3. Write a complete standalone HTML file.
4. Use embedded CSS.
5. Avoid external CDN dependencies unless the user allows them or rendering requires them; if used, make fallback content readable.
6. Include no placeholder sections unless marked as actionable TODOs.
7. Include acknowledgement footer only when the user asks or the report is about HTML generation.
8. Report the file path and summarize the page contents.

## Quality Checklist

Before finishing, verify:

1. Title is specific.
2. Hero/header states the exact claim.
3. Every innovation card has a validation path.
4. Every table has meaningful headers, captions, and no empty rows.
5. Claims have boundaries.
6. No section or visual element is decorative-only.
7. Mobile and print layouts are readable.
8. Fonts, colors, spacing, and cards are consistent.
9. Tags are closed and anchors work.
10. Figures, tables, equations, and references are numbered when in publication mode.
11. Formulas are bright, readable, LaTeX-style when needed, and symbol-explained.
12. Model reports include a model flow diagram.
13. Table headers use normal letter spacing and readable casing.
14. Every meaningful visible element has a caption, legend, note, or nearby explanation.
15. Chart and SVG labels do not overlap bars, axes, values, nodes, captions, or nearby text.
16. Horizontal charts reserve label columns and right margins before plotting begins.
17. Missing evidence is marked as TODO, not implied as complete.

## Minimal Skeleton

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Research Plan</title>
  <style>
    :root { color-scheme: light; }
    body { margin: 0; font-family: Arial, sans-serif; color: #172033; background: #f7f8fb; line-height: 1.6; }
    main, article { max-width: 1180px; margin: 0 auto; padding: 32px 20px; }
    section { margin: 28px 0; }
    .panel { background: #fff; border: 1px solid #dde3ee; border-radius: 8px; padding: 20px; }
    table { width: 100%; border-collapse: collapse; }
    th, td { border-bottom: 1px solid #e2e7f0; padding: 10px; text-align: left; vertical-align: top; }
    th { letter-spacing: 0; text-transform: none; }
    figure, table, .equation { break-inside: avoid; }
    @page { size: A4; margin: 18mm 16mm; }
  </style>
</head>
<body>
  <main></main>
</body>
</html>
```

## One-Sentence Summary

Create standalone HTML research reports that make the claim, mechanism, evidence, risks, formulas, diagrams, and every visible element easy to understand.
