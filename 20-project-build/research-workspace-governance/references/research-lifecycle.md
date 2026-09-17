# Research Lifecycle Governance

Use this reference to govern work from inception through archive. It records
decisions and evidence but does not choose a domain method or establish a
scientific conclusion.

## Scope-aware state

Every current-status record identifies its scope:

```text
scope_type: project | work_item | evidence_package | claim | deliverable | custom
scope_id
status_record_id
supersedes
recorded_at
owner
work_state
claim_state
evidence_refs
next_action
```

There may be many scopes, but only one canonical current record per
`scope_type + scope_id`. If two records both claim to be current, report an
ambiguity and block status-dependent writes. Do not choose by timestamp.

`work_state` and `claim_state` are independent:

- `work_state`: `not_started | active | blocked | completed | abandoned`;
- `claim_state`: `not_applicable | unreviewed | unsupported | supported |
  contradicted | rejected`.

`work_state=completed` means the declared procedure and its completion checks
finished. It does not imply `claim_state=supported`.

## Inception

Record only what changes decisions:

```text
objective and decision context
questions or hypotheses when applicable
scope and exclusions
evidence and acceptance standard
owners and decision authority
ethical, legal, safety, access, licensing, or retention constraints
stopping conditions
expected deliverables
```

A delivery target is not an evidence standard. “Produce a report” does not state
what would support its conclusions.

## Planning and execution

Use independently reviewable work items. Each record states:

```text
work_id | scope | objective | owner | inputs | method/procedure reference
dependencies | expected evidence | validation | work_state
risks | next decision | completion condition
```

- Update status from observable evidence.
- Preserve unsuccessful, contradictory, and incomplete outcomes when they affect
  future decisions.
- Record material deviations and their impact.
- Supersede earlier records with linked corrections instead of rewriting history.
- Use domain Profile validation only when explicitly enabled by the project
  contract or owner.

## Claim control

For a conclusion used in a decision or deliverable, record:

```text
claim_id and scope
claim text
supporting and contradictory evidence
method/procedure and Profile identifiers
conditions and limitations
review status, reviewer, and review evidence
deliverables using the claim
```

Governance checks that this record is present, traceable, and internally
consistent. A domain reviewer or domain Skill determines whether the evidence is
scientifically adequate.

## Review gates

Use only gates justified by the project:

1. **Scope ready:** objective, boundaries, evidence standard, ownership, and
   constraints are explicit.
2. **Method ready:** the selected method or procedure, inputs, exclusions,
   validation, and deviation handling have domain approval where required.
3. **Work ready:** storage, identities, automation, logging, concurrency,
   recovery, and authorization are adequate.
4. **Evidence ready:** required outputs are complete, provenance-bound, validated
   under the declared Profile, and limitations are recorded.
5. **Claim ready:** the claim has an explicit review separate from work
   completion and does not exceed its evidence.
6. **Delivery ready:** deliverable, editable source when required, manifest,
   approvals, and archive obligations are complete.

Every gate result includes a machine section:

```text
gate_id
scope_type + scope_id
result: pass | conditional | fail
blockers
non_blockers
evidence_refs
suggested_actions
allowed_actions
forbidden_actions
```

It also includes a plain-language summary in the user's current language. The
summary answers these seven fixed questions, translated rather than renamed:

1. What is being reviewed now?
2. Why is this review required?
3. Which evidence must the reviewer inspect?
4. What permits approval?
5. What requires rejection?
6. What becomes allowed after approval?
7. What is the minimum-cost repair after rejection?

Do not pass a gate from checklist presence alone; cite evidence.

When durable machine validation is useful, a project contract may point to one
JSON governance-state carrier. Its `current_statuses` array contains the fields
above and is validated for one current record per scope. This is an optional
carrier for many scopes, not a rule that the project may have only one status
file or only one status. The carrier is governance data and is never loaded as
Agent instructions.

Ambiguity checks apply only to objects the project actually uses. A blocking
finding states the object, at least two interpretations, risk, minimum repair,
and verification. Check names and aliases, applicable units or coordinates,
configuration defaults and overrides, path identities, status criteria,
evidence links, and claim boundaries without inventing domain definitions.

## Handoff

A useful handoff states the objective, scoped current states, active method or
procedure reference, material deviations, canonical assets, completed and failed
work, claim review state, risks, exact next action, owner, prerequisites, and
recovery information. Prefer stable identifiers and links over duplicated prose.

## Closure and archive

- Freeze or version finalized status, evidence, claim, and delivery records.
- Record unanswered questions and why work stopped.
- Preserve the sources, methods, evidence, decisions, deviations, approvals, and
  environment information required by the declared contract.
- Verify integrity, access, restore procedure, ownership, and retention.
- Distinguish superseded evidence from disposable temporary material.
