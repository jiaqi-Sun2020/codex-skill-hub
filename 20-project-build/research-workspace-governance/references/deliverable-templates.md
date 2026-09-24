# Deliverable Templates

Use only sections needed for the task. Empty templates are not deliverables.

## Project charter

```text
objective and decision context
questions or hypotheses when applicable
scope and exclusions
evidence and acceptance standard
owners and authority
constraints and obligations
stopping conditions
deliverables
```

## Work, status, decision, and risk records

```text
work: work_id | scope | objective | owner | dependencies | expected evidence | validation | work_state | next decision
status: status_id | scope_type | scope_id | work_state | claim_state | claim_review_ref | evidence | supersedes | recorded_at | owner
decision: decision_id | context | alternatives | evidence | rationale | owner | date | consequences
risk: risk_id | condition | impact | likelihood/uncertainty | mitigation | owner | status
deviation: deviation_id | method/version | change | reason | affected evidence/claims | approval | date
```

## Claim-evidence record

```text
claim_id | claim and scope | supporting and contradictory evidence
method/procedure and Profile identifiers | conditions | limitations
review status | reviewer | deliverables using the claim
```

## Contract registry carrier

Use the versioned `research-contract-registry/v1` schema. Instantiate only
applicable SCI, STAT, ENG, GOV, or Profile-owned contracts; do not create empty
files for the full catalog. Keep one registry as the editable source of truth.

```text
instance_id | catalog_id + category | scope | applicability + decision_ref
owner_ref | definition_ref + definition_state | depends_on
implementation_refs | verification_refs | work_refs | evidence_refs
claim_refs | authorization_refs | deliverable_refs | required_gates
```

Derive the trace matrix with the Governance validator. Do not hand-maintain a
second matrix. Append changes to the registry's `amendments` array and preserve
the prior revisions and historical PASS records.

## Amendment impact summary

```text
change_id | reason | old_revision -> new_revision | decision_ref
changed assumptions or parameters | directly affected contracts
dependency closure | stale verification scope | affected evidence
affected claims | affected gates | affected deliverables
reuse policy | required revalidation | next allowed action
historical_records_modified: false
```

## Architecture brief

```markdown
# Research Workspace Architecture

## Objective and evidence standard
## Scope, assumptions, and authority
## Current failure point
## Governance-location resolution
## Current and target role maps
## Dependency and evidence flow
## Automation contracts
## Naming, identity, and status
## Access and sensitive-data boundaries
## Finalization contract
## Retention, archive, and cleanup policy
## Migration or initialization preview
## Verification and acceptance
## Residual risks and owner decisions
```

## Asset lifecycle record

```text
asset_id
logical_path
role
owner
producer
input_ids
consumer_ids
version_or_hash
mutability
validation
access_class
retention
deletion_authority
status
notes
```

## Evidence-package manifest

```json
{
  "package_id": "stable-unique-id",
  "status": "working|failed|validated|finalized|archived",
  "objective": "declared objective",
  "method_ref": "method or procedure identifier",
  "profile_ids": [],
  "input_assets": [],
  "resolved_conditions": {},
  "started_at": "timestamp",
  "completed_at": null,
  "producer": "person, system, or workflow",
  "validation": [],
  "known_limitations": [],
  "supersedes": null
}
```

Use hashes where they provide meaningful integrity. Do not place secrets,
restricted identifiers, credentials, or unnecessary machine-local paths in a
shareable manifest.

## Migration preview

| Absolute source | Classified role | Absolute destination | Files/bytes | Hash | Dependents | Active locks | Collision | Reference updates | Verification | Rollback |
|---|---|---|---:|---|---|---|---|---|---|---|

Follow the table with protected unchanged paths, unresolved items, authority,
and a versioned append-only relocation-map destination. No preview authorizes a
move by itself.

## Cleanup manifest

| Exact path | Class | Files/bytes | Producer | Consumers checked | Concurrency checked | Recovery | Authority | Decision |
|---|---|---:|---|---|---|---|---|---|

Decisions are `safe-to-delete`, `conditional`, `retain`, or `unknown`. Only an
exact, separately approved `safe-to-delete` target is eligible for deletion.

## Gate summary

```text
result: pass | conditional | fail
scope:
blockers:
non_blockers:
evidence:
suggested_actions:
allowed_actions:
forbidden_actions:

human_summary_language:
what_is_reviewed:
why_review_is_required:
evidence_to_review:
pass_conditions:
reject_conditions:
after_pass:
minimum_repair:
```

The keys remain stable for machines; the summary values use the user's current
language. One carrier may contain multiple explicitly scoped gate results. Do
not create a separate file for every gate.

## Adversarial acceptance summary

```markdown
## Conclusion
Pass | conditional | fail, with the reason.

## Passes
1. Objective and ownership
2. Safety and loading
3. Compatibility and migration
4. Human understandability
5. Tests and counterexamples

## Blockers and non-blockers
## Evidence
## Repairs made
## Verification rerun
## Residual risks
## Owner decisions required
## Conflicts between passes requiring adjudication
```
