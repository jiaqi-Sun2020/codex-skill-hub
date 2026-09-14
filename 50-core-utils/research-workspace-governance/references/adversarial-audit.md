# Adversarial Audit

Use distinct passes with different failure hypotheses. Do not count repeated proofreading as multiple rounds. Record evidence, defect, severity, repair, and rerun result for each pass.

## Pass 1: Scope and domain independence

Try to prove that the proposed framework solves the wrong problem or encodes one discipline as universal.

- Does it start from the research objective, evidence standard, and collaboration/retention constraints?
- Are file formats, programming languages, model types, metrics, or validation designs hard-coded without necessity?
- Can it represent computational, experimental, observational, qualitative, and mixed-methods work?
- Does it preserve established naming and tools when their contracts are already sound?
- Does it duplicate another system’s ownership or expand authority beyond the request?

Reject or generalize unsupported assumptions. A generic framework may offer profiles and examples, but must keep the invariant separate from the example.

## Pass 2: Traceability and reproduction

Assume the original researcher is unavailable and a skeptical collaborator must reproduce or audit one claim.

- Can they identify the exact source records and external references?
- Can they recover every transformation, exclusion, parameter, method revision, environment dependency, and random or manual decision that matters?
- Are derived datasets and run results uniquely versioned?
- Are machine-readable results separated from visual interpretation?
- Does the formal run include enough evidence to validate completeness and limitations?
- Are sensitive records traceable without being inappropriately exposed?

Fail the pass if reproduction depends on mutable global state, oral history, a `latest` folder without an immutable target, or hidden spreadsheet/notebook edits.

## Pass 3: Failure, concurrency, and deletion safety

Assume interruption, partial writes, duplicate launch, path mistakes, stale locks, and an overconfident cleanup operator.

- Can failure overwrite or remove the last known-good final artifact?
- Is staging on the same filesystem when atomic rename is claimed?
- If atomic rename is unavailable, is there an immutable version plus validated completion-marker protocol?
- Are checkpoints atomic and provenance-bound before resume?
- Are output paths resolved and constrained to an approved root?
- Can two runs write the same destination?
- Can a stale lock or expired lease be recovered without permitting two live writers?
- Does cleanup protect unknown files and distinguish durable intermediates from caches?
- Are delete targets exact, previewed, concurrency-checked, and authorized?
- Is rollback real and tested rather than asserted?

Fail the pass for delete-before-build replacement, broad recursive deletion, wildcard-only targeting, silent collision handling, or deletion based solely on age, name, or size.

## Pass 4: Operational usability and evolution

Assume a new collaborator, a second study, a new storage backend, and a future correction.

- Can a newcomer locate the active protocol, source inputs, processing method, formal run, and deliverable?
- Does normal work require excessive duplication or manual bookkeeping?
- Is the selected governance profile proportional to project size and risk?
- Can independent studies and runs coexist without naming collisions?
- Can the scheme scale from a small project without forcing empty bureaucracy?
- Can a correction supersede prior evidence without erasing history?
- Are ownership, retention, and archival responsibilities explicit?
- Are commands, working directories, and verification procedures executable?

Simplify ceremony that does not protect evidence or reduce coordination cost. Add structure only where ambiguity, risk, scale, or collaboration justifies it.

## Pass 5: Mandatory-policy reachability

Use this pass when one project contains nested roots from which an Agent or
command can be started independently.

- Are all execution roots inventoried rather than only the selected working directory?
- Can every managed execution root reach every applicable mandatory policy?
- Is the binding an explicit canonical reference, a verified loader, or an owner-approved isolation decision?
- Do references exist, remain inside the approved project, avoid links, and match their recorded hashes?
- Has copied policy prose drifted from its canonical source?
- Is a mandatory rule incorrectly stored only in optional memory?
- Does a child instruction set claim to replace, weaken, or silently omit a parent rule?

Machine checks can prove paths, hashes, and known loader behavior. They cannot in
general prove that arbitrary natural-language instructions do not weaken a parent
policy. Preserve that uncertainty as an explicit semantic-review finding.

## Pass 6: Equivalence and inference safety

Use this pass whenever results are described as equal, equivalent,
interchangeable, matching, or duplicates.

- Is the relation explicitly one of `matrix_exact`, `matrix_global_phase`,
  `observational_protocol`, or `metric_only`?
- Is the claim bounded by scope, protocol, observables, parameters, and tolerance?
- Does the evidence come from a domain comparator rather than from workspace naming or orchestration logic?
- Are allowed uses no stronger than the recorded relation?
- Are forbidden inferences explicit enough to stop downstream promotion?
- For global-phase equivalence, is physical irrelevance explicitly justified in scope?
- Do current invalidation keys still match the verified record?
- Can a stale, rejected, failed, or unknown comparison be misreported as verified?

Fail the pass if metric agreement is promoted to observational agreement, if
observational agreement is promoted to operator/matrix equivalence, or if stale
evidence remains marked verified.

## Acceptance record

Use this record for each pass:

```text
pass:
hypothesis attacked:
evidence inspected:
defects found:
severity: blocker | high | medium | low
repairs made:
rerun result: pass | conditional | fail
residual risk:
owner decision needed:
```

The framework is sufficient only when:

- no blocker or unresolved high-severity defect remains;
- roles and lifecycle rules cover every material artifact class;
- at least one realistic claim can be traced end to end;
- an interrupted run and an attempted unsafe cleanup have credible handling;
- a new collaborator can follow the workflow without relying on unstated conventions;
- loss or corruption of the working copy has a tested recovery path proportional to the evidence value;
- domain-specific scientific quality controls are delegated to the relevant protocol rather than falsely supplied by workspace organization.
- every applicable mandatory policy is reachable from each managed execution root, or its isolation is explicitly owner-approved;
- every material equivalence claim has a typed, scoped record whose allowed uses do not exceed its evidence.

State “conditionally sufficient” when unresolved owner choices, regulatory requirements, storage constraints, or missing provenance prevent an unconditional conclusion.
