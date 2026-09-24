---
name: prl-manuscript-polisher
description: Audit, restructure, and polish LaTeX manuscripts for Physical Review Letters (PRL), preserving scientific meaning while improving broad-physics accessibility, concision, evidential precision, APS/REVTeX consistency, and submission readiness. Use for PRL fit audits, PRL-style English editing, tracked LaTeX revision, word-budget reduction, abstract/introduction/conclusion rewriting, claim-evidence checks, and article-specific execution plans.
---

# PRL Manuscript Polisher

## Purpose

Transform a technically complete physics manuscript into a concise, evidence-calibrated PRL Letter. Treat PRL polishing as **scientific editorial engineering**, not grammar correction.

The workflow must optimize five objectives in this order:

1. scientific validity and claim–evidence alignment;
2. a single important physics message with broad interest;
3. compliance with the current PRL Letter length and presentation rules;
4. accessibility to physicists outside the immediate subfield;
5. grammatical, terminological, and LaTeX consistency.

Never strengthen a claim merely to make the paper sound more impressive. When evidence is weak, narrow the claim or flag the need for new analysis.

## Authoritative sources

Before applying numerical limits or submission rules, verify the current official APS pages when web access is available:

- PRL Information for Authors: https://journals.aps.org/prl/authors
- APS Length Guide: https://journals.aps.org/authors/length-guide
- PRL scope and criteria: https://journals.aps.org/prl/about
- APS Editorial Policies: https://journals.aps.org/authors/editorial-policies

As verified from the official APS pages on 2026-09-13, a PRL Letter has a 3,750-word equivalent core limit, with up to two pages of End Matter. Recheck this before every submission audit.

## Inputs

Accept any combination of:

- `.tex` manuscript;
- `.bib` bibliography;
- figures and tables;
- supplemental material;
- journal decision letter or referee reports;
- author constraints, such as “language only,” “do not change equations,” or “mark edits in red.”

If only the `.tex` file is present, complete the audit with explicit notes about checks that require the missing bibliography, figures, data, or source code.

## Modes

### 1. Audit mode

Do not rewrite the manuscript. Produce:

- PRL fit verdict;
- length and structure audit;
- scientific-expression risk register;
- section-by-section language findings;
- prioritized execution checklist.

### 2. Structural PRL rewrite mode

Rebuild the narrative around one physics result. Move, compress, or delete content while preserving technical correctness. Clearly distinguish:

- core Letter content;
- End Matter;
- Supplemental Material;
- content that should be removed.

### 3. Language-polish mode

Edit sentence-level English without changing scientific structure. Use only when the manuscript already passes the PRL architecture and evidence gates.

### 4. Tracked LaTeX mode

Preserve equations, labels, citations, commands, and environments. Mark changes using one of the following, according to the author’s request:

- `latexdiff` output;
- `\rev{...}` with `\newcommand{\rev}[1]{\textcolor{red}{#1}}`;
- a separate change log with original/revised pairs.

Do not wrap math delimiters, citation commands, labels, references, or paragraph breaks inside fragile color commands.

## Mandatory workflow

### Step 1 — Preflight and compilation safety

1. Make a backup copy.
2. Identify document class, REVTeX version, journal option, compiler assumptions, packages, external figures, bibliography, and custom commands.
3. Compile before editing when a complete source package is available.
4. Record existing warnings, undefined references, missing files, and overfull boxes.
5. Run `scripts/audit_tex.py` or an equivalent audit.

### Step 2 — Current PRL compliance

Check:

- current Letter length limit;
- title, abstract, introduction, central result, conclusion, references, and Data Availability Statement;
- PRL-specific End Matter allowance;
- REVTeX/APS formatting;
- accessibility of figures, especially meaning conveyed by color alone;
- required submission materials, including the approximately 100-word PRL justification paragraph.

Estimate length using the APS method, not plain prose count alone. Displayed mathematics, figures, tables, captions, footnotes, and endnotes contribute to the word-equivalent count.

### Step 3 — Define the one-sentence Letter claim

Write one sentence in this form:

> We show that **[physical mechanism or result]** leads to **[quantified or demonstrable consequence]**, revealing **[broader physical implication]**.

Reject or revise the sentence when:

- it is primarily a model name or architecture list;
- it depends on marketing words such as “competitive,” “novel,” or “effective” without a result;
- the evidence supports only validation performance or a single narrow benchmark but the claim is broad;
- the central contribution is an engineering combination rather than a new physical result or highly significant method.

Use this sentence as the retention test for every paragraph, equation, figure, and table.

### Step 4 — Scientific-integrity audit

Check each physics and statistical claim before language editing.

#### Quantum terminology

- Use **exact CTQW** only for evolution of the form `exp(-i H t)` under the stated Hamiltonian.
- Use **CTQW-inspired**, **unitary spectral filter**, or **phase-regularized propagator** when the phase has been modified and no longer represents evolution under the original Hamiltonian.
- Distinguish quantum dynamics, quantum-inspired classical computation, and an implementable quantum algorithm.
- Do not call generic complex-valued operations “quantum interference” unless amplitudes and the relevant interference mechanism are mathematically established.
- Distinguish a unitary operator from a nonunitary residual combination or measurement/readout process.
- For a quantity called fidelity, verify normalization, state definition, dimensions, and range `[0,1]`.

#### Machine-learning evidence

- Make the held-out test set the basis of performance claims; do not present validation minima as final evidence.
- Report uncertainty and the number of independent runs.
- Compare effect size with run-to-run variation.
- Avoid “outperforms” when differences are smaller than uncertainty or lack statistical support.
- Verify that baselines are competitive and matched in information, parameter budget, training protocol, and tuning effort.
- Separate mechanism evidence from benchmark performance.

#### Hardware feasibility

- Label conceptual mappings as conceptual.
- State encoding, state preparation, readout, postselection, and data-loading costs.
- Provide gate-count/depth or asymptotic resource estimates before claiming computational benefit.
- For LCU or sums of unitaries, discuss ancillas, success probability, normalization, and postselection/amplitude amplification.
- Do not infer end-to-end quantum advantage from natural Hamiltonian evolution alone.

Output every issue with severity:

- **P0**: validity, contradiction, unsupported central claim, or submission-blocking problem;
- **P1**: PRL fit, evidence, structure, or major clarity problem;
- **P2**: language, terminology, consistency, or formatting problem.

### Step 5 — Build the PRL content map

Classify every manuscript element:

- **KEEP-CORE**: required to understand and establish the central result;
- **COMPRESS-CORE**: required but overexplained;
- **MOVE-END**: specialist detail valuable within PRL End Matter;
- **MOVE-SM**: reproducibility, derivations, full tables, implementation, extra ablations;
- **DELETE**: repeated, generic, unsupported, or unrelated to the central Letter claim.

Default target for a computational/theoretical PRL Letter:

- abstract: 100–150 words;
- opening and motivation: 350–550 words;
- core physical construction: 600–900 words;
- decisive evidence and mechanism analysis: 1,200–1,600 words;
- conclusion/outlook: 180–300 words;
- remaining word-equivalent budget reserved for equations, figures, tables, captions, and footnotes.

These are editorial targets, not APS rules. Adjust them to the current official word-equivalent limit.

### Step 6 — Section-specific editing rules

#### Title

Prefer a result-led or mechanism-led title over a product/model name. It must be accurate, searchable, and intelligible outside the immediate subfield.

#### Abstract

Use one paragraph with this progression:

1. broad problem;
2. unresolved physical limitation;
3. central mechanism/result;
4. decisive quantitative or qualitative evidence;
5. broader implication.

Avoid literature review, architecture inventories, undefined acronyms, citations, and promotional adjectives. State limitations when they materially constrain the result.

#### Introduction

The first two paragraphs must be understandable across physics subfields. They must establish:

- the physical question;
- why existing approaches cannot answer it;
- the new physical idea;
- the primary result and why it matters.

Do not begin with a narrow dataset description unless the dataset itself is the physics system. Remove generic textbook definitions, exhaustive platform lists, and “the remainder of this paper is organized as follows.”

#### Theory/model

Present the minimum chain of equations needed to establish the mechanism. Define every symbol at first use. Remove derivations that a specialist can reconstruct or move them to End Matter/SM. After an equation, explain its physical consequence rather than restating every symbol.

#### Results

Lead with the decisive figure or test. Report effect sizes and uncertainty. Explain what result discriminates the proposed physical mechanism from classical or alternative explanations. Put exhaustive benchmark tables and hyperparameters in End Matter/SM.

#### Conclusion

Do not repeat the architecture. State what was learned physically, the range of validity, the strongest limitation, and the next falsifiable or experimentally actionable step.

### Step 7 — Sentence-level PRL English

Apply these rules:

- one principal claim per sentence;
- favor concrete subjects and active verbs;
- use present tense for established knowledge and the paper’s enduring claims; use past tense for procedures and observations;
- remove throat-clearing phrases and repeated definitions;
- replace promotional wording with evidence-calibrated wording;
- use hedging only when scientifically necessary;
- keep terminology and hyphenation consistent;
- use American English unless the manuscript has a justified alternative house style;
- use “Fig.” and “Eq.” in running text according to APS style;
- avoid “obviously,” “clearly,” “successfully,” “competitive,” “significant” without a defined statistical or scientific meaning;
- avoid absolute contrasts such as “classical methods cannot” unless proved under explicit assumptions.

Preferred transformations:

- “The results show that …” → “We find/show that …”
- “provides a physically motivated design” → state the mechanism and observed consequence;
- “achieves better performance” → give the metric, comparator, effect size, and uncertainty;
- “in order to” → “to”;
- “it can be seen that” → delete or state the observation directly.

### Step 8 — Consistency and LaTeX QA

Check:

- `continuous-time quantum walk` as a compound modifier;
- `nonmonotonic`, unless a target dictionary requires otherwise;
- singular/plural acronyms;
- notation for transpose versus Hermitian conjugate;
- real/complex domains of all parameters;
- dimensions of tensors and operators;
- equation punctuation;
- labels and cross-references;
- duplicated labels;
- figure extensions and missing files;
- bibliography keys and unused references;
- package compatibility with REVTeX;
- section numbering and formatting customizations that override APS defaults.

Compile after structural edits and again after final polishing. Compare the PDF visually, not only the source.

### Step 9 — Required outputs

Produce:

1. `PRL_AUDIT.md` — verdict, length, P0/P1/P2 findings, and evidence gaps;
2. `PRL_CONTENT_MAP.md` — keep/compress/move/delete decisions;
3. `PRL_EXECUTION_CHECKLIST.md` — ordered tasks with acceptance criteria;
4. `MANUSCRIPT_PRL_EDITED.tex` — only when editing is requested;
5. `PRL_CHANGELOG.md` — high-impact revisions and unresolved author decisions;
6. `PRL_JUSTIFICATION_100W.md` — a defensible editor-facing justification, only after the central claim passes the evidence audit.

## Quality gates

Do not declare the manuscript “PRL-ready” unless all gates pass:

- **G1 Validity:** no unresolved P0 scientific-expression issue;
- **G2 Central claim:** one result-led claim supported by the manuscript;
- **G3 Broad interest:** introduction and justification explain why physicists beyond the niche should care;
- **G4 Evidence:** central claims use held-out evidence and uncertainty appropriate to the claim;
- **G5 Length:** estimated APS word-equivalent count is within the current limit or an explicit waiver strategy exists;
- **G6 Accessibility:** nonexpert physicists can understand the problem, result, and implication without Supplemental Material;
- **G7 Reproducibility:** specialist detail is available in End Matter/SM;
- **G8 Technical QA:** LaTeX compiles and notation, citations, figures, and metadata are consistent.

## Refusal and escalation rules

- Do not fabricate results, statistical significance, physical interpretations, references, or hardware advantages.
- Do not silently repair a scientific inconsistency; flag it and offer the mathematically valid alternatives.
- Do not perform “language-only polishing” on a sentence whose scientific meaning is internally inconsistent.
- When the evidence cannot support PRL criteria, state that the manuscript may be better suited to a specialized journal unless new results are added.
