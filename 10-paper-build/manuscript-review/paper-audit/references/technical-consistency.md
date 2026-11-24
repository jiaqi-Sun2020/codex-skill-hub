# Technical consistency

Local original guidance added 2026-11-09 and refined 2026-11-13; covered by the
local-material notice in [LICENSE](../LICENSE). Use relevant checks for claims
that depend on mathematical notation or computational steps. The entrypoint owns permissions; this reference
does not authorize research-code execution or manuscript edits.

Contents: [symbols](#symbols-and-index-scope), [operators](#operators-and-parameter-ownership),
[representations](#cross-representation-trace), [explanation](#purpose-and-reading-order),
[claim changes](#claim-scope-and-deletion-dependencies), [calibration](#calibration-and-closure).
Numerical provenance and uncertainty checks live in
[method checks](method-checks.md#internal-consistency).

## Symbols and index scope

For symbols carrying the argument, trace their first definition and consequential
reuse. Note object type (scalar, vector, matrix, tensor, set or operator), dimensions,
index domain, units where relevant and local/model/data scope. A short working map
may help; do not require a symbol ledger or publish a table for every symbol.

- Distinguish an index from a count: for example, a batch size from a sample index.
  Distinguish original sampling positions from retained-observation order, or time
  indices from channel indices. If different indices are needed, explain their
  domains or mapping rather than mechanically merging them.
- Check bold/italic/calligraphic forms, case, subscripts and superscripts against
  the readable PDF or source. Extraction can erase these distinctions. Determine
  whether a superscript denotes a time step, a layer, a power or parameter ownership
  before recommending its removal or addition.
- Distinguish **same mathematical role**, **same defined object**, and **same
  numerical instance**. Two sections can use the same eigenvector convention for
  different matrices. Different graphs, normalizations or versions can produce
  different eigenpairs even when the decomposition formula is identical.
- Track aliases and transformation boundaries: a feature array, one channel
  vector, its normalized or embedded state, and a readout are distinct objects.
  Locate their defining relation, domain, normalization and any nonzero-input
  condition needed for division. Removing or adding an index cannot substitute
  for explaining that relation. A matching letter alone does not establish it.
- Reusing a letter is not automatically wrong. Flag an unresolved collision only
  where scope or typography leaves a consequential ambiguity; retain a clear local
  convention. Do not rename unrelated objects into one symbol for visual uniformity.

## Operators and parameter ownership

Follow a critical expression from input through operation to output. Identify
which object is a function/operator, which is its learned parameter, and which is
the resulting feature array. For example, a convolutional operator, its kernel and
the tensor it produces are different objects; a library name alone need not define
the intended axes or transformation. Seek only details needed to understand the
claimed operation. Request a citation when external support is needed, not as a
substitute for defining the operation.

Check matrix/tensor compatibility, concatenation axes, real/complex domains and
residual operand shapes. Missing dimensions are an assessment limit; incompatible
stated dimensions can be a demonstrated contradiction. Do not infer an exact
kernel size, layout conversion or broadcasting rule without evidence.

For repeated parameter symbols, locate their owners: model variant, layer, time
step and trainable/fixed status. Ask whether weights are shared across steps,
independent across layers, or merely written with the same name in separate models.
An activation's step index does not imply independently learned step parameters;
the absence of a parameter index does not prove sharing. Compatible dimensions
are necessary for a proposed identity, not proof of shared parameter values.

Interpret overloaded operators in context: bars may denote norms, absolute values
or concatenation; a circled plus may denote a direct sum rather than addition.
Check definitions and operand types before requesting a notation change. Even a
standard convention can need a local clarification when the manuscript uses a
competing convention nearby; do not demand elementary definitions without a real
reading or assessment problem.

## Cross-representation trace

Select the steps that support the central method or claim. Compare the available
prose, equations, algorithm and inspected model figure for:

- the input, transformation order, state before/after update, and output;
- retained/removed branches, residual operands and trainable versus fixed weights;
- activation/readout operations, parameter sharing and applicable model variant;
- assumptions and approximations, including whether a claimed implementation
  realizes the whole model or only a propagation subroutine.

For figures, use the two-way correspondence check in
[figure review](figure-review.md#scientific-content-and-text-correspondence).
Preserve the distinction between a diagram's declared abstraction and a changed
computation; do not require one box per equation or identical wording.

Authorized, identifiable code can clarify the implementation through static
inspection, but neither code nor manuscript silently overrides the other. Record
the version and report a mismatch. A manuscript-only audit cannot certify runtime
behavior, recover a missing architecture or authorize experiments to resolve it.

Group linked discrepancies under one root concern and name the places that need
synchronization. Do not create separate issues for every occurrence of one error.

## Purpose and reading order

For an unexplained consequential step, reconstruct the minimum relation the reader
needs: what enters, why this transformation is used for the stated task, what leaves,
and how the next step uses it. Separate a mathematical consequence (such as matching
widths) from an empirical claim (such as improving stability); do not invent a
mechanism or benefit to make the prose flow.

At the first substantive use of a consequential concept, symbol or condition,
check what the reader must already know and where that prerequisite is supplied.
Definitions should precede or immediately accompany uses that depend on them.
An abstract or introduction may preview a later result without developing it;
such signposting is not a missing premise. If an explanation exists only later,
report a placement problem, not total absence, and locate both passages.

For recurrent/in-place updates, distinguish observation time, processing order,
previous state and current state. Trace initialization, the first-step exception,
gate calculation and state assignment against the algorithm. Identify an actual
dependency conflict; do not impose a causal/online restriction on a method that
explicitly allows whole-sequence processing.

For a bridging gap, prefer a short purpose/input/output connection while retaining
correct detailed update rules. Do not replace a sound paragraph merely to shorten
it. Before suggesting moves or merges, track prerequisites, qualifiers and referents
so the proposed order does not create a new gap. No fixed number of bridging
sentences or universal section order is required.

When time examples carry the method, reconcile index positions, retained-step
order and physical units using the stated mapping. Count elapsed sampling
intervals rather than equating them with missing observations; check boundary
intervals and separated missing segments where relevant. Compare the example with
figure ticks and equations. Do not invent an unstated end-interval convention.

## Claim scope and deletion dependencies

Distinguish needless repetition from a first definition, a useful reminder or a
necessary condition. Before endorsing deletion of an equation, definition or
qualifier, look for later uses in reasoning, symbols, captions and algorithms,
including indirect dependency on the concept. Material with no necessary role
may be removed; material needed elsewhere may need relocation or a brief
cross-reference instead.

Check whether shortening a model name, removing a variant distinction or replacing
qualified wording extends a claim beyond the stated method and evidence. Preserve
differences between exact/approximate operators, simulated/implemented components
and experimentally tested/theoretically described variants. Revisit affected
abstract and conclusion claims as needed. A reviewer's deletion mark is a proposal
to assess, not evidence that the resulting claim is scientifically supported.

## Calibration and closure

Use the evidence categories and counter-review in
[method checks](method-checks.md#internal-consistency). Before retaining a concern,
look for the strongest answer elsewhere in the supplied material. If it is present,
withdraw an absent-definition allegation; retain a narrower placement concern only
when the reading impact is demonstrable.

Close a technical concern when the affected definitions and representations agree
within explicit scope, or when evidence establishes that the criticism was mistaken.
Do not close it merely because one occurrence was renamed or the author said it
was fixed. Keep severity tied to impact: a typographic issue is usually local, but
an undefined parameter identity that blocks the central derivation may be major.

Illustrative repair direction: "Both passages use eigenvectors of a graph
Laplacian, but their typography differs. Align the convention and refer to the
first definition. If the passages use different matrices, specify that scope;
do not imply identical numerical eigenvectors." This is an example, not a finding
to repeat without checking the manuscript.
