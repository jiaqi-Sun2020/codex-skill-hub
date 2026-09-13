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

State “conditionally sufficient” when unresolved owner choices, regulatory requirements, storage constraints, or missing provenance prevent an unconditional conclusion.
