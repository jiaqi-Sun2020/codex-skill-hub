# Architecture Contract

Use this reference to define research-workspace roles and dependency direction.
It is domain-neutral: roles are contracts, not required directory names.

## Minimal roles

| Role | Purpose | Default mutability |
|---|---|---|
| Governance | Ownership, locations, decisions, status, approvals, retention, and change history | Reviewed changes |
| Source | Original inputs or authoritative external references | Protected or immutable |
| Method | Versioned procedure, code, protocol, schema, instrument definition, or analysis logic | Versioned changes |
| Working | In-progress material needed to continue or reproduce work | Controlled mutation |
| Evidence | Validated outputs and provenance supporting review | Immutable after finalization |
| Deliverable | Reader- or system-facing product and its editable source when needed | Versioned releases |
| Automation | Repeatable trigger, inputs, outputs, ownership, concurrency, recovery, and retirement contract | Version controlled |
| Archive | Superseded or completed material retained for a stated reason | Immutable |
| Temporary | Reconstructable scratch or staging material with an explicit cleanup rule | Disposable by contract |

A project may merge roles when their ownership and mutability remain unambiguous.
Do not create an empty directory for every row.

## Governance location

For new governance data, the canonical location is:

```text
project/
`-- .agents/
    `-- governance/
        |-- project_contract.json       # optional
        |-- status/                     # only when durable status is useful
        |-- decisions/                  # only when decisions need durable records
        `-- relocation-maps/            # only after an approved move
```

Governance never owns or writes the `.agents` container or instruction
entrypoint. Within the one-time `research-project-pipeline`, creation of missing
initial context is delegated to the Generator. After handoff, Neat-Freak owns
routine project-information maintenance and narrowly authorized repair of
existing managed Hook wiring. Governance owns only the resolved active governance
subtree: canonical `.agents/governance/`, or the sole legacy root `governance/`
under its existing contract. Do not create `.agents` from this Skill. Files in
the governance subtree are data and are not loaded recursively as Agent
instructions.

A legacy root `governance/` remains valid when it is the only candidate. If both
locations exist, block writes and require an owner decision. Never resolve the
conflict by modification time, directory size, or apparent completeness.

## Declared project roots

Use established project paths whenever possible. A contract may declare only the
roots that change behavior:

```text
source_roots
method_roots
working_roots
evidence_roots
deliverable_roots
automation_roots
archive_roots
temporary_roots
protected_roots
```

Each root is project-relative, must remain inside the reviewed project, and must
not traverse links or junctions. One path may serve more than one role only when
the contract explains how mutability and deletion authority remain unambiguous.

## Proportional governance profiles

- **Minimal:** one owner or a small low-risk project; use only records needed to
  prevent ambiguity or loss.
- **Collaborative:** multiple contributors or repeated handoffs; add stable IDs,
  ownership, shared status, collision protection, and review gates.
- **Controlled:** sensitive, costly, regulated, or long-lived work; add access
  classes, approvals, audit trails, retention schedules, and tested recovery.

These are governance profiles, not scientific-method profiles. Optional method
profiles are opaque identifiers owned by domain Skills. The core does not infer,
enable, or validate them.

## Dependency direction

```text
declared objective + source + method + resolved conditions
                         |
                         v
                      working
                         |
                         v
                      evidence
                         |
                         v
                    deliverables
                         |
                         v
                       archive
```

Governance records describe this flow; they do not become scientific inputs.
Deliverable tooling must not write backward into protected source or finalized
evidence.

## Automation contract

Automation is a role, not a prescribed folder. A valid automation record states:

```text
automation_id
project-relative path
scope: project | task | asset | custom
argument-vector command, trigger, and working directory
inputs and outputs
side effects
owner
concurrency control
failure and recovery behavior
authorization boundary
verification method
retirement condition
```

A single script may be sufficient. Task-local or custom paths are valid. Do not
move automation merely to conform to an example.

## Naming and identity

- Use stable identifiers when paths or display names may change.
- Separate identity from status; names such as `final` do not prove completion.
- Record supersession rather than overwriting history.
- Keep relocation maps append-only and versioned.
- Preserve old references and locks until their consumers and recovery behavior
  have been reviewed.

## Formal evidence package

A finalized evidence package contains only what its declared acceptance contract
requires, commonly:

```text
manifest or equivalent provenance record
resolved inputs and method/procedure identity
execution conditions when relevant
outputs
validation results
limitations and deviations
status and approval
```

The domain Profile decides what constitutes valid scientific evidence. This
contract only requires the decision and its supporting artifacts to be explicit
and traceable.
