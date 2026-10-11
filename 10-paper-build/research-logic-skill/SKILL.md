---
name: research-logic
description: Formulate research questions and candidate directions from ideas or observations, challenge assumptions and contribution claims, or analyze how methods can be integrated. Use for scientific ideation and reasoning; not for implementation-only coding, literature-search completeness, empirical validation, or final claim approval.
---

# Research Logic

Turn an uncertain question, observation, or method combination into a scoped
reasoning path. An idea is a proposal, not a finding. A simpler method,
replication, theory, qualitative inquiry, or synthesis can be a valid contribution.

## Choose the mode

- **Question / direction:** develop candidates from a question or observation,
  with assumptions, predictions, rival explanations, and feasibility.
- **Method integration:** analyze two or more methods. Read
  [references/method-integration.md](references/method-integration.md).
  Its QWTA/TGN example is conditional, not a default model or quality standard.
- **Logic challenge:** locate premises and evidence of an existing contribution,
  then identify its weakest consequential inference.

Do not force equations, fusion, numerical scores, fixed candidate counts, or
new experiments onto an unrelated question.

## Shared workflow

In the paper hub, use the Pipeline's
[shared goal-clarification protocol](../latex-paper-build-skill/references/goal-clarification.md)
when a consequential ambiguity or changed decision needs a repeatable interview.
The Pipeline owns scope and stage return; this Skill handles the scientific
question, hypotheses and contribution only, not delivery choices or permissions.
Standalone use remains available through the workflow below; it does not require
the Pipeline to be installed or create Pipeline files.

1. State the focal question, decision, scope, known observations, and real
   constraints. Distinguish an observation from its possible explanations.
2. Label reasoning as **idea**, **assumption**, **prediction**, **located
   evidence**, or **decision**. Record which data/results were already seen.
3. When useful, generate initial alternatives before search to reduce anchoring.
   If evidence was supplied, use it; do not pretend independence. Preserve simpler
   explanations, negative results, minority views, and uncertainty.
4. Set criteria before selection: relevance, information gained, discriminating
   predictions, feasibility, cost, reversibility, and applicable ethical/safety
   review. No automatic winner or mandatory scoring.
5. Route unknown context to `literature-review`; compare a known set with
   `literature-triage-matrix`. Reopen candidates after evidence checks.
   Bounded search absence does not prove novelty; literature support does not
   validate a new hypothesis.
6. Challenge each serious candidate: what would contradict it, what else predicts
   the same observation, and what measurement or selection effect could explain it?
   For each concern give source/locator or explicit assumption, consequence for
   the claim, uncertainty, and the smallest useful remedy.
7. Explain the decision and rejected alternatives. The accountable user chooses;
   unresolved scientific or institutional decisions stay open. Route evidence
   design to `experiment-design`, actual data analysis to `data-analysis`,
   and final scientific acceptance to the author/domain expert.

One agent's varied perspectives are self-review, not independent reviewers.
Consensus and scores are not truth. Formal clinical/ethics appraisal requires
an applicable project requirement and qualified review.

## Minimal handoff

For managed paper work, maintain `00_research_logic/research_logic.md`: question
and mode, candidate reasoning, located support and counterevidence, assumptions,
rivals, chosen or undecided directions, bounded claims, open gaps, and next step.
Reuse literature artifacts instead of duplicating their search log.

Tests on observations used to form an idea remain exploratory. Confirmatory
claims need an appropriately justified design, e.g. new data or an untouched
holdout where applicable. Do not invent retroactive preregistration.

## Invocation

`Use $research-logic to compare explanations of this observation and propose
the smallest evidence plan that could distinguish them.`

See [third-party notices](../THIRD_PARTY_NOTICES.md) for adaptation provenance.
