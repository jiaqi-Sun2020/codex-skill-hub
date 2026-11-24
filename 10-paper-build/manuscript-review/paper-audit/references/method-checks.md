# Conditional referee checks

Locally adapted on 2026-10-28 from the review sources identified in
[LICENSE](../LICENSE), including selected Nature Skills Apache-2.0
claim/evidence and consistency methods. This is a narrowed implementation,
not their multi-reviewer, editing or research-execution workflow.

Local content update 2026-11-13: integrated reading dependencies, citation
scope, figure evidence and bilingual meaning into the existing review lenses.

Use only checks relevant to the manuscript's actual claims. The Skill entry
owns permissions and handoff; this file owns review methods. There is no minimum
concern count, fixed IMRAD form, training requirement or universal journal style.

## Scientific validity

- Trace the central claims through definitions, assumptions, design/reasoning,
  observations and inferential scope. Separate what the manuscript demonstrates
  from plausible interpretation, future work and author assertion.
- Ask which rival explanation or counterexample would change the conclusion,
  and whether the supplied argument addresses it. Reason through a proof or
  supplied arithmetic when feasible; disclose where expertise or material is
  insufficient. Do not run the research to fill the gap.
- Distinguish flawed evidence from a limited but honestly bounded claim.
  Negative results, inconclusive findings and exploratory observations are valid
  outcomes. Do not demand positive results or invent a mechanism.
- Evaluate method suitability for the question, not recency alone. Select only
  applicable design concerns: independence, controls, selection, causal
  identification, theoretical assumptions, qualitative interpretation or review
  coverage. A theoretical paper need not report seeds or training metrics.
- Flag load-bearing reporting omissions as limits on assessment, not proof of
  misconduct. Likewise, missing code/raw data do not alone establish a false
  claim. Relevant ethics/integrity concerns require located evidence; suspicion
  must remain labeled as suspicion.

## Contribution and literature

Identify the actual contribution and the prior-work comparison it relies on.
Do not impose Nature-style interdisciplinary importance on every paper.
If venue criteria are requested, use supplied/verified current criteria; without
those, leave venue fit unassessed rather than guessing an editor's preferences.

Use supplied sources first. Source identity/DOI registration, metadata matching,
located content support, retraction screening and scientific quality are
different checks. Mark each unperformed relevant check as unchecked.
Abstract access is not full-text verification. A valid DOI does not establish
that a source supports the claim. Identify whether the cited passage supplies a
definition, an existing method or the specific conclusion being asserted. Check
assumptions and transformations such as normalization, powers and roots before
calling two formulas equivalent. A source for a definition does not prove the
paper's new bound or empirical benefit; locate the manuscript's own reasoning.

External checks must follow the entry's authority and confidentiality rules.
Record what was actually searched/read, failures and coverage limits in the
report, not a new search ledger. No search results do not establish absence of
prior work. Do not invent references, demand citations by popularity, require a
fixed citation count or call novelty established after an incomplete search.

## Argument and readability

Separate two judgments: **scientific support** asks whether the question,
definitions, assumptions, method, evidence and conclusion connect validly;
**the reading path** asks whether the manuscript makes those relations clear.
Fluent prose does not supply a missing premise; poor ordering does not by itself
disprove a result. Identify which relation breaks before proposing a remedy.

Reconstruct the question-to-answer chain in both directions: where the question
is answered, and why each central result matters. As applicable, check:

- **Scope and promises:** do title, abstract, introduction, results and conclusion
  describe compatible questions and claim strength? Locate each central promise's
  answer, explicit non-answer or honest limit; do not demand a positive answer.
- **Method rationale:** is it clear why the method can address that question
  under the stated assumptions, rather than merely listing modules/operations?
  Distinguish an unexplained choice from a demonstrably unsuitable method.
  For a consequential projection, convolution or state update, identify its
  purpose, input/output and required preceding definitions using
  [technical consistency](technical-consistency.md#purpose-and-reading-order).
  Request the minimum explanation that resolves the gap, not a general tutorial.
- **Result progression:** does each key result advance an answer, with the
  relevant comparison and interpretation, rather than only report numbers or
  experiments? Do not invent a mechanism to fill an interpretive gap.
- **Paragraph dependencies:** what job does a relevant paragraph do, what must
  the reader already know, and what does it add? Use the
  [first-use and transition checks](technical-consistency.md#purpose-and-reading-order)
  to locate inferential gaps, misplaced prerequisites and background without a
  later role. Nonstandard order or a clearly signposted preview is not itself a
  defect; necessary reminders are not automatically redundant.
- **Figure/text cooperation:** use
  [figure review](figure-review.md) to connect a decisive comparison or method
  step with the prose in both directions, and assess readability at its supplied
  publication size. Keep content judgments distinct from layout judgments.
- **Discussion closure:** does it synthesize the answers, consider relevant
  alternatives and boundaries, rather than repeat results or introduce an
  unsupported claim? Related numerical checks remain in Internal consistency.
  Before recommending deletion or broader terminology, check the
  [claim and deletion dependencies](technical-consistency.md#claim-scope-and-deletion-dependencies).

Use a short reverse outline or known-to-new information check only to expose a
concrete dependency break; do not require a per-paragraph table or separate
story report.
Multiple questions and different article structures are valid; do not prescribe
ABT, IMRAD, three acts or a fixed paragraph count. An undramatic story alone is
not a rejection reason. Do not invent research gaps, causes or mechanisms to
complete a story, or use connecting words to conceal an unsupported inference.
Unexpected results may change the argument, but their exploratory/post-outcome
origin must not be rewritten as a prespecified hypothesis.

Treat unclear prose as a scientific problem only when it prevents assessment or
changes meaning. Flag empty inflation, ambiguous agency/comparison, lost
qualifiers and chat residue where they matter. Do not issue a sentence-by-sentence
rewrite, ban punctuation/passive voice, substitute defined terms for variety or
infer AI authorship. Concision cannot justify hiding a decisive counterexample,
necessary definition, heterogeneity or limitation. Diagnose and propose the
smallest repair direction; do not turn this check into manuscript rewriting.

## Internal consistency

For technical claims, first establish the objects being compared with
[technical consistency](technical-consistency.md): symbol meanings and scopes,
operator/output distinctions, parameter ownership, dimensions, and the actual
computation across representations. A matching glyph or formula does not prove
identical parameters, data or numerical instances; an apparent typography mismatch
must be checked against a readable source.

Before comparing values, identify the entity and conditions: dataset, scale,
configuration, batch/version, metric definition, denominator, aggregation level,
independent unit, units, selection and uncertainty convention where applicable.
Different objects need not share a value. Reasonable rounding and equivalent
unit conversions are not errors; do not invent a tolerance to resolve ambiguity.

For reported repetitions, identify what varies between runs and what counts as
an independent unit. A random seed controls a pseudo-random sequence; different
seed labels alone do not establish independent or otherwise comparable runs.
Distinguish seed variation from configuration variation, successful/selected runs
from attempted runs, and between-run SD from SE, confidence intervals or paired
difference uncertainty. Check what a plotted point and its error bar summarize
before comparing them. Do not assume equal sample counts to make labels uniform
or pool differently configured runs by folder/model names alone. For a difference,
distinguish a fixed reference from a random comparator and identify pairing or
dependence before interpreting uncertainty; subtracting a fixed constant does
not add sampling variation. Require these details only when they affect the claim.

Trace key numbers to available tables, logs or other authorized evidence and
record missing links without assuming the numbers are false. Transparent arithmetic
on supplied values is not statistical reanalysis or verification of underlying
experiments. Large spread or surprising values can motivate a specific check;
they do not establish a model failure, data error or misconduct.

Check supplied counts, percentages, differences, ranges, rankings and cross-
references with reproducible intermediate reasoning. Compare the same claim
across abstract, text, tables, figures and conclusions. Do not infer exact values
from indistinct plots. A plot of an intermediate quantity does not alone establish
an effect, or negligible effect, on a downstream outcome. Separate the observed
pattern, a proposed mechanism and a tested outcome; locate evidence for the last
or recommend a bounded claim without inventing a favorable explanation.

### Bilingual meaning

When corresponding language versions are supplied, compare their scientific
meaning rather than word order: objects, assumptions, quantifiers, negation,
counts, units, formulas, named variants and claim strength. Align passages by
their role or stable labels, not identical page or equation numbers. Identify
which language contains an omission or stronger assertion; a translation must
not silently add commentary as if it were in the source. Equivalent idiom and
different pagination are not discrepancies. A single-language paper does not
require a translation audit.

### Evidence categories

Distinguish:
- **Confirmed internal error:** a contradiction is demonstrable from reliable
  supplied values/definitions.
- **Definition/aggregation ambiguity:** multiple interpretations remain possible.
- **Provenance gap:** a necessary source, condition or selection rule is missing.
- **Suspected anomaly:** an unusual pattern needs additional evidence.
- **Not assessable:** available material or extraction cannot support the check.
- **Checked, no inconsistency found:** limited to what was actually examined.

Do not decide significance from error-bar overlap alone, infer misconduct from
repeated values/images, equate non-significance with no effect, or assume that
unreported procedures were never performed. An author-supplied statistical
summary is not a recomputation. Under the conventional definition, significance
level is alpha and the corresponding confidence level is 1 minus alpha; identify
the stated convention before alleging a labeling error.

## Counter-review and calibration

For each substantive candidate concern, inspect the strongest reasonable answer:
an explanation elsewhere (including captions and accessible appendices), an
applicable assumption, differing conditions or a narrower claim. If support is
already present, withdraw the missing-support criticism; retain a narrower
navigation/placement concern only if its actual reading impact is demonstrated.
Confirm source readability before calling a formula or figure wrong. Record the
decisive rebuttal and disposition for important disputed issues.

Retain, downgrade, merge, mark pending or withdraw the criticism according to
evidence. Do not keep a weak criticism to fill a quota; do not suppress a real
central contradiction because the rest of the paper reads well.

Major/minor concerns reflect impact on the paper, not hostility, repair cost or
certainty. Evidence sufficiency and blocking status are separate judgments.
A minor comment is non-blocking; an issue that blocks assessment of the central
case must be treated as major even if the fix is short. A major contribution or
reporting concern need not prove the scientific result false. For a narrative
concern, explain whether it prevents assessment of a core method, evidence or
conclusion (potentially major) or only disrupts local reading (usually minor);
do not assign severity from a stylistic label alone.

For requested new evidence, specify the uncertainty, why it affects a claim and
what observation would resolve it. Prefer an adequate clarification, already
available evidence or claim narrowing over gratuitous new experiments. Do not
turn a proposed remedy into an authorized action or a predetermined outcome.
