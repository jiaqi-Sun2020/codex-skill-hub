# Deliverable Templates

Use only the sections needed for the task. Empty templates are not deliverables.

## Research charter

```text
objective and decision context
questions/hypotheses
scope and exclusions
evidence/acceptance standard
exploratory, confirmatory, or operational status
owners and stakeholders
constraints and obligations
stopping conditions
deliverables
```

## Work, decision, and risk records

```text
work: work_id | objective | owner | dependencies | expected evidence | validation | status | next decision
decision: decision_id | context | alternatives | evidence | rationale | owner | date | consequences
risk: risk_id | condition | impact | likelihood/uncertainty | mitigation | owner | status
deviation: deviation_id | protocol/version | change | reason | affected evidence/claims | approval | date
```

## Claim-evidence record

```text
claim_id | claim and scope | evidence artifact/version | method/protocol
domain of validity | uncertainty/limitations | contradictory evidence
review status | deliverables using the claim
```

## Architecture brief

```markdown
# Research Workspace Architecture

## Objective and evidence standard
## Scope, assumptions, and constraints
## Current failure point
## Current-state map
## Target-state map
## Dependency and evidence flow
## Folder contracts
## Naming and versioning
## Access and sensitive-data boundaries
## Run/finalization contract
## Retention, archive, and cleanup policy
## Migration or initialization steps
## Verification and acceptance
## Residual risks and owner decisions
```

## Artifact lifecycle register

```text
artifact_id
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

## Run manifest

```json
{
  "run_id": "stable-unique-id",
  "status": "staging|failed|validated|finalized|archived",
  "objective": "research question or registered analysis",
  "protocol_id": "protocol/version",
  "input_artifacts": [],
  "method_revision": "version or revision identifier",
  "resolved_parameters": {},
  "environment": {},
  "started_at": "timestamp",
  "completed_at": null,
  "producer": "person, system, or workflow",
  "validation": [],
  "known_limitations": [],
  "supersedes": null
}
```

Use hashes where they provide meaningful integrity or identity. Do not place secrets, participant identifiers, credentials, or unnecessary machine-local paths in a shareable manifest.

## Migration plan

| Source | Classified role | Destination | Operation | Collision check | Reference updates | Verification | Rollback |
|---|---|---|---|---|---|---|---|

Precede the table with the approved root and authority. Follow it with unchanged protected paths and unresolved items. Moves that change scientific identifiers, checksums, access controls, or external links require explicit review.

## Cleanup manifest

| Exact path | Class | Files/bytes | Producer | Consumers checked | Recovery need | Authority | Decision |
|---|---|---:|---|---|---|---|---|

Allowed decisions are `safe-to-delete`, `conditional`, `retain`, and `unknown`. Only the first class is eligible for an approved automated cleanup. Conditional items need item-specific resolution.

## Adversarial acceptance summary

```markdown
## Conclusion
Pass | conditional | fail, with the reason.

## Audit passes
1. Scope/domain independence — result and evidence
2. Traceability/reproduction — result and evidence
3. Failure/deletion safety — result and evidence
4. Operational usability/evolution — result and evidence

## Repairs made
## Verification rerun
## Residual risks
## Owner decisions required
```
