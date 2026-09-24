# QCT/QWCT Scientific Narrative Methodology

Read this reference before drafting or revising a QCT/QWCT abstract, introduction, contribution paragraph, results overview, figure/table discussion, or discussion boundary. This is a reusable writing methodology, not a one-paper patch.

## Core Principle

Write the paper as a scoped physics-methodology claim:

```text
Under a specified quantum-walk model and data regime,
sparse position probabilities can be used as a diagnostic of coin-state observability.
```

Do not write it as a universal theorem unless identifiability, noise, masks, dimensions, and baselines have been proved or exhaustively tested. At the same time, do not let limitations erase the throughline. A scoped claim should still read as a claim.

## Claim Ladder

Use this hierarchy when choosing wording:

1. Setting: specify coin operator, shift rule, initial walker position, step range, simulated/noisy probability regime, training/test distribution, and mask construction.
2. Question: ask whether a restricted position-probability vector retains enough information to reconstruct the coin state within that setting.
3. Method contribution: define the keep-k sparse-position diagnostic, including how positions are ranked or chosen.
4. Evidence: report the strongest completed regime first, then comparative regimes, then inconclusive extensions.
5. Boundary: state what remains unproved, such as arbitrary states outside the training distribution, finite-shot noise, random masks, strong baselines, independent seeds, and formal identifiability.

## Throughline Without Repeated Self-Limitation

When a manuscript repeatedly says what it cannot claim, the reader loses the main scientific line. Use this repair pattern:

- State the positive scoped claim first. Example: "In the studied Grover-walk setting, sparse position probabilities provide an empirical diagnostic of coin-state observability."
- Put caveats in planned locations: the end of the abstract, the final introduction paragraph, the end of each major results subsection, and the discussion/limitations section.
- Avoid caveat chains inside the same sentence as the main claim. Replace "we cannot prove X; we only show Y" with "within this specified regime, the evidence shows Y; X remains outside the present scope."
- Use boundary paragraphs instead of defensive parentheticals. One strong limitation paragraph is better than five interrupted claims.
- Separate author-review honesty from manuscript voice. Internal status such as missing checkpoints, partial eval files, pipeline names, and TODO reasoning belongs in notes, not in formal manuscript prose.

## Abstract Method

A good abstract should follow this order:

1. Scoped opening, not a universal conclusion. Prefer a setting-qualified sentence such as "In a specified quantum-walk setting, position probability distributions may carry information useful for coin-state reconstruction." Avoid unrestricted statements that quantum walks generally encode all coin-state amplitudes and phases into position probabilities.
2. Problem with boundary. State whether reconstruction is for simulated noiseless probabilities, finite-shot data, training-distribution test samples, arbitrary pure states, or density matrices.
3. Contribution sentence. Name the reusable contribution, e.g. "keep-k sparse-position observability diagnostic".
4. Method summary. Explain that the work trains/evaluates an inverse estimator on simulated quantum-walk probability distributions; do not mention internal code names unless the software artifact is formally defined.
5. Evidence hierarchy. Put interpretation before numbers. Use numbers sparingly and only for completed evidence.
6. Formal limitation. Use publication language such as "high-dimensional extension remains to be validated" instead of process language such as "only partial eval exists" or "not finished yet".

## Introduction Method

Use five paragraph jobs:

1. Context and gap: quantum state tomography infers latent states from measurement statistics; quantum walks couple coin and position degrees of freedom; prior work motivates the setting but does not make sparse position observability trivial.
2. Why the inverse problem is nontrivial: influence is not invertibility. Position probabilities discard complex amplitudes and phases, the map can be non-injective, different coin states may induce similar distributions, and finite masks can remove discriminative positions.
3. Why sparse positions matter: motivate detector cost, restricted access, compressed measurement, and observability diagnosis before presenting technical mask definitions.
4. Positive contribution statement: say what the paper proposes and tests. Do not write internal reminders such as "the contribution should not be described as...".
5. Paper organization: use neutral section descriptions. Do not mention "PRA style", "pipeline", or "author-review" in the manuscript body.

## Contribution Types

Choose explicit contribution language:

- Diagnostic scheme: a keep-k sparse-position observability diagnostic.
- Empirical finding: high-fidelity reconstruction is observed in a specified quantum-walk regime.
- Comparative boundary: lower/higher dimensional settings, alternative coins, initial-position states, and ablations identify limits rather than proving universal scalability.
- Measurement insight: position selection and walk step affect how coin information appears in probability observations.

Avoid vague phrases such as "diagnosis" alone unless the diagnostic procedure and output curve are defined.

## Result Section Expansion Method

Do not write results as a list of fidelities. Each results subsection should have a minimum narrative unit:

1. Question: what physical or methodological question does this figure/table answer?
2. Setup: which dimension, coin, step range, mask policy, initial position, noise regime, and baseline are being compared?
3. Observation: what trend is visible before giving exact numbers?
4. Interpretation: what does the trend imply about position-probability information, interference, mixing, or observability?
5. Comparison: how does it differ across keep-k, step, coin, initial position, or dimension?
6. Mechanism: offer a plausible walk-level explanation when supported by the setup.
7. Boundary: close with a scoped limitation or a next comparison, not with an apology.

Use representative numbers to anchor the interpretation, but never let numbers replace interpretation. A weak results paragraph says "the fidelity is 0.98, 0.95, and 0.91". A stronger paragraph says what changes across masks or steps, why that pattern matters, and then reports the numbers as evidence.

## Figure And Table Reading Protocol

Every figure/table that carries an argument must be explicitly read in the main text. Captions are not enough.

For each figure, the main text should include:

- Orientation: identify panels, axes, color/marker meaning, and what is held fixed.
- Dominant trend: describe the main shape before giving values.
- Key comparison: state the contrast that supports the claim, such as position-superposition vs single-position initial states, RX vs non-RX coins, all-position vs sparse keep-k observations, or low vs high step.
- Scientific implication: connect the visual trend to observability, information loss, interference, or failure modes.
- Local caveat: mention noise, missing baselines, insufficient seeds, or partial coverage only after the figure has been interpreted.

For each table, the main text should include:

- What each row/column represents.
- Which row/column is the primary evidence.
- Which contrast is most important.
- What conclusion the reader should draw from the table.

Do not let a table be a storage device for unprocessed numbers. Tables summarize; the manuscript body argues.

## Result Reporting Method

- Do not place raw experiment numbers before the reader knows the method and contribution.
- Report completed evidence as completed evidence; report partial evidence as a scoped subset, not an internal process failure.
- Replace internal language:
  - "QCT_run_all" -> "simulated quantum-walk probability distributions" or a formally defined software artifact only after definition.
  - "partial eval aggregation" -> "the evaluated subset".
  - "step 4 has no checkpoint" -> "step-4 evidence is not included in the present comparison".
  - "next experiment" in body prose -> "limitations and future work".
  - "PRA-style organization" -> remove from manuscript body.

## Terminology Rules

For Chinese author-review manuscripts, write in Chinese while keeping PRL/PRA reasoning logic. Use English technical terms only on first use or when the English term is conventional. After first use, keep terminology consistent and avoid workflow words.

Use stable equivalents for:

- coin state
- position probability distribution
- position mask
- keep-k sparse-position observation
- inverse estimator
- fidelity
- observability diagnostic

Avoid mixing `claim`, `pipeline`, `eval`, `checkpoint`, `author-review`, or other workflow terms into formal manuscript prose.

## Forbidden Or Needs-Definition Phrases

Do not use these unless explicitly defined and supported:

- "structured tomography-measurement preprocessing"
- unrestricted statements that quantum walks encode all coin-state information into position probabilities
- claims that sparse position measurements prove tomography for arbitrary coin states
- universal high-dimensional tomography claims
- "the neural network improves reconstruction performance" as the central contribution
- internal code or workflow names in abstract/introduction

## Manuscript QA Checklist

Before finalizing, check:

- The abstract's first sentence has a setting qualifier.
- The abstract names one reusable contribution.
- The abstract separates method, evidence, and limitation.
- The introduction explains why influence does not imply invertibility.
- keep-k has a physical or diagnostic meaning, not only a machine-learning feature-selection meaning.
- The manuscript has a positive throughline that is not interrupted by repeated self-limitations.
- Each major results subsection contains interpretation, comparison, and mechanism-level analysis, not only numbers.
- Every figure and table is read in the main text with trend, comparison, implication, and caveat.
- Negative or inconclusive evidence is framed as boundary mapping.
- No internal writing-process terms appear in the manuscript body.
