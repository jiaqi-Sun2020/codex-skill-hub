# Teaching patterns

Use the smallest pattern that repairs the learner's current gap. These are
response tools, not mandatory templates.

## Diagnose the wording

| Learner signal | Likely need | Teaching move |
|---|---|---|
| “是什么” | missing object-level definition | give category, defining property, non-example, and role |
| “怎么来的” | missing origin or derivation | begin from accepted premises and expose every transition |
| “为什么要这样做” | missing motivation | name the problem, show failure without the device, then show what it enables |
| “物理上是什么意思” | formal-to-operational gap | connect symbols to preparation, evolution, measurement, or observable outcome |
| “这两个有什么区别” | category boundary is blurred | compare meaning, mathematical object, operation, observable effect, and failure mode |
| “第一段就卡住了” | earliest bridge failed | stop later material and repair only the first unsupported step |
| “太笼统” | mechanism lacks operations | name actors, state before, operation, state after, and observable evidence |
| “给具体例子” | abstraction is not grounded | work one small case completely before generalizing |
| “从头到尾串起来” | fragments exist without a model | give prerequisites, ordered chain, branch points, and final synthesis |
| “我能这样理解吗” | learner is testing a model | validate correct parts, locate first error, repair, then retest with a nearby case |
| “但这样不会丢失……吗” | information carrier is unclear | identify where that information is encoded, then test whether the operation changes it |
| “50字/100字解释” | concise synthesis requested | reason fully, output one accurate core relation near the requested length |
| “只给提示词” | transformation artifact requested | output only a self-contained prompt with scope and correctness constraints |
| “这部分太复杂” | hierarchy is obscured by detail | recover the core question and pipeline, then separate invariants from compressible detail |

## Output contract router

Use the latest explicit request to choose exactly one primary output mode:

| Mode | Required content | Usually omit |
|---|---|---|
| Full explanation | broken link, reason, mechanism, example, distinctions, check | unrelated background |
| Approximate 50/100-character explanation | one causal or logical relation in plain Chinese | derivation, headings, optional caveats |
| Prompt only | target, exact scope, preserved content, requested change, guardrails, output form | preface, tutoring recap, follow-up offer |
| Localized rewrite | replacement text for the named passage | changes to other sections |
| Method simplification | core research question, compact pipeline, essential assumptions, justified outputs | secondary notation and implementation detail |

Correctness and explicit epistemic limits remain mandatory in every mode. The
full-explanation defaults, compact recap, and understanding check do not apply
when they conflict with a length-bounded or prompt-only contract.

## New concept pattern

1. One-sentence answer: “X is a kind of ___ distinguished by ___.”
2. Why it exists or why the concept was introduced.
3. One concrete instance with all roles named.
4. Formal definition and notation.
5. One nearby non-example or contrast.
6. How it connects to the learner's known anchor.
7. A prediction question using a slightly changed instance.

## Derivation pattern

```text
Goal
Known premises and assumptions
Meaning of every symbol
Step 1 -- rule and reason
Step 2 -- rule and reason
...
Result
Physical or operational interpretation
Sanity check
```

Do not begin in the middle of a derivation. If a coefficient appears through
normalization, show the proportional relation first, state the normalization
condition, calculate the coefficient, and only then write the equality.

## Technical formula repair

Use this when the learner is stuck on one operator, term, matrix transformation,
normalization, loss component, or constraint.

1. Point to the exact token or transition being explained.
2. Give a one-sentence answer to its role.
3. Inventory the objects: type, dimensions, indices, and model role.
4. Name the operation and contrast the nearest lookalike. For example,
   elementwise squaring preserves the locations of nonzero matrix entries,
   whereas an ordinary matrix square aggregates two-step walks.
5. State the information carrier. Direction may be encoded by matrix position,
   while sign or phase may encode a different property; do not conflate them.
6. Test what would fail, cancel, remain ambiguous, or become invalid without the
   operation. If the current assumptions already prevent the failure, state that
   the operation is optional, conventional, or kept for compatibility; do not
   retrofit a false motivation.
7. Work the smallest complete numerical example line by line.
8. Generalize to the symbolic formula and reconnect it to the surrounding
   research pipeline.
9. End with the exact claim the formula supports and one nearby claim it does
   not support.

If the learner objects, do not defend the original wording automatically. Check
whether the objection exposes a domain mismatch—for example, a formula designed
for a real directed adjacency matrix being applied to a complex Hermitian
dynamics matrix. Preserve the valid distinction even when the final formula is
unchanged.

## Relationship pattern

For questions connecting several ideas, distinguish:

```text
A: what it is
B: what it is
A -> B: the operation or theorem that connects them
what is preserved
what changes
why the connection is useful
```

Use this for connections such as state and wavefunction, position and momentum
representations, commutation and simultaneous measurability, or an abstract model
and its experiment.

## Paper or unfamiliar technical system

Teach in four passes:

1. **Question:** what the work is trying to establish and why it matters.
2. **Objects:** systems, parties, variables, assumptions, and what is controlled
   or measured.
3. **Mechanism:** chronological operations and information flow.
4. **Evidence:** what equation or observation rules out the alternative and what
   conclusion is justified.

Only then walk through formulas. Keep a live glossary and reuse the same notation.

## Research-method compression

Use this when a technically valid section has become too detailed for its
communicative role, such as a proposal, overview, or interface description.

1. Write the single research question the section must answer.
2. Recover the shortest input-to-output pipeline and its connection to adjacent
   sections.
3. Mark non-negotiable assumptions, identification conditions, temporal rules,
   physical constraints, and conclusion limits.
4. Classify the remaining material as core mechanism, implementation choice,
   estimator detail, diagnostic, or appendix candidate.
5. Remove or downshift detail only when the core question, interfaces, and
   justified conclusion remain intact.
6. If a learned model replaces hand-designed scoring or function estimation,
   state exactly what it replaces and what governing conditions it cannot prove
   or replace.
7. Present the result around two or three reader-facing questions rather than a
   chain of every intermediate variable.

Do not equate fewer formulas with better teaching. Compression succeeds only
when the learner can still explain the pipeline, the indispensable constraints,
and what the output does and does not establish.

## Progressive transformation

The learner may move through these requests over several turns:

```text
detailed explanation -> focused numerical example -> 50/100-character recap
-> prompt-only rewrite -> whole-section simplification
```

Treat each new request as a transformation of the established understanding, not
as permission to repeat all earlier material. Preserve notation and conceptual
invariants across modes, but output only the requested artifact.

## Inequality as a model test

Use this for Bell/CHSH, steering/LHS, contextuality, uncertainty bounds,
entanglement witnesses, and similar arguments. The learner understands these
better as tests of a constrained explanation than as formulas to memorize.

### Pass 1: Tell the alternative-model story

Name the model that the inequality is testing. Describe, in chronological order:

1. what information or shared resource is prepared before a trial;
2. which choices are made later and independently;
3. what each party is allowed to know or communicate;
4. what answer or outcome each party must produce.

A useful starting analogy is a pair of answer sheets prepared before two random
questions are chosen. Immediately map the analogy back:

| Story | Formal role |
|---|---|
| hidden instruction or answer sheet | hidden variable or local state |
| random question | measurement setting |
| written answer | measurement outcome |
| no editing after question choice | locality/causal separation constraint |
| question choice independent of sheet | measurement independence |
| score over many trials | correlation statistic |

State the analogy's limit: a hidden-variable model may be probabilistic, and the
formal claim concerns a factorization or allowed conditional distributions, not
literal paper cards. Explain why any extra local randomness can be included in a
more complete hidden variable when that step matters.

### Pass 2: Derive the ceiling

Show how the allowed strategies constrain the statistic. For a CHSH-style example:

- define `x,y` as setting labels before using values such as `0,1`; define
  `A_x(λ),B_y(λ)` as the responses for a chosen setting and fixed hidden
  variable; define `ρ(λ)` as a normalized distribution or density;
- explicitly separate setting labels (`x,y`), response functions (`A_x,B_y`),
  observed outcomes (`a,b`), correlations (`E_{xy}`), a fixed-strategy score
  (`S_λ`), and the ensemble score (`S`);
- define each `+1/-1` response and explain why, for fixed `λ`, the response values
  are ordinary numbers that can be regrouped algebraically;
- write one trial's combination;
- show why every precommitted local assignment makes that combination `+2` or
  `-2`, rather than merely announcing the bound;
- average over strategies/trials to obtain the model's ceiling.

Do not say the factorization works because `A_0,A_1,B_0,B_1` are mutually
independent. They may be strongly correlated through the same `λ`. The relevant
facts are that, for fixed `λ`, each is a well-defined scalar response and each
side's response uses only its local setting and `λ`.

Before writing an integral, use a discrete example:

```text
λ1 occurs with probability 0.5 and gives S_λ1 = 2
λ2 occurs with probability 0.3 and gives S_λ2 = 2
λ3 occurs with probability 0.2 and gives S_λ3 = -2
S = 0.5(2) + 0.3(2) + 0.2(-2)
```

Then explain:

```text
discrete hidden strategies: S = Σλ P(λ) S_λ
continuous hidden variable: S = ∫dλ ρ(λ) S_λ
normalization: Σλ P(λ) = 1 or ∫dλ ρ(λ) = 1
```

The integral means only “take the probability-weighted average over all possible
hidden-variable cases.” Establish the bound for every fixed `λ` first; then show
that a normalized weighted average of values in `[-2,2]` remains in `[-2,2]`.

For another inequality, use the same structure but never borrow CHSH's numerical
bound. Derive the bound from that model's actual assumptions.

### Pass 3: Compare with the tested system

Define the measured statistic, calculate or report the prediction, and compare it
with the bound. Keep three conclusions separate:

```text
within the bound -> this test has not ruled out the candidate model
above the bound -> the candidate model's joint assumptions cannot explain the data
additional interpretation -> requires additional assumptions or evidence
```

Never translate “the joint assumptions fail” into a stronger metaphysical claim
without justification.

### Pass 4: Connect neighboring models

When comparing Bell and steering, keep the trust boundary visible:

- Bell tests local hidden-variable explanations with neither measurement device
  treated as trusted in the core correlation claim.
- Steering tests a local-hidden-state explanation with a trusted quantum-state or
  measurement description on one side.

Explain the common skeleton first, then the changed assumptions, allowed classical
strategy, bound, and strength of the conclusion. Do not teach them as unrelated
collections of formulas.

### Pass 5: Test the learner's model

Invite a one-paragraph explanation in the learner's own words. Respond in this
order:

1. quote or paraphrase the part that is structurally correct;
2. identify the first inaccurate link—for example, confusing “one fixed
   measurement” with “one pre-existing state or response rule for every possible
   setting”, or confusing local response structure with mutual statistical
   independence;
3. replace that link with the technically precise condition;
4. test the repaired model with one changed setting or strategy.

## Adaptive checkpoint

Choose one:

- “如果把条件 X 改成 Y，你预测哪一步先变化？为什么？”
- “请用一句话区分 A 和 B，我会只修正不准确的部分。”
- “这个式子左边和右边分别代表什么对象？”
- “不用公式复述一次从准备到测量的过程。”

Use the answer to select the next move. If the issue is vocabulary, redefine; if
it is mechanism, simulate a process; if it is algebra, reduce to a smaller case;
if it is the global map, redraw the logic chain.

## Compact recap

Finish with no more than:

```text
Core idea: ...
Logic chain: A -> B -> C -> D
Do not confuse: A != A'; B != B'
Check: one prediction or paraphrase question
```

Expand beyond this only when the learner explicitly asks for a complete review.
