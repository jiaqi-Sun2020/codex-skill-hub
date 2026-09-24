# Pipeline Stage Contracts

The Pipeline is a human-reviewed state machine. A stage consumes only a
validated preceding output; natural-language console text is not a contract.

## States

```text
discover
design
human_review
controlled_change
verify
handoff_or_archive
```

Each stage reports `complete`, `pending`, `blocked`, or `review_required`; failure
and recovery details belong to the stage result rather than a second lifecycle.

## Contract table

| Stage | Required input | Machine output | Mutation owner |
|---|---|---|---|
| Discover | Resolved project root | Generator inspection, Governance inventory, evidence-backed project facts, separate knowledge/Bootstrap state, optional declarations | None |
| Design | Complete inventory and objective | Reviewed governance/component proposal plus explicit domain-validation requirement | None |
| Human review | Exact plan and fingerprint | Owner authorization bound to plan hash | None |
| Controlled change | Approved plan | Generator-owned initial context creation, or create-only Bootstrap completion for one preserved legacy bundle, and/or Governance-owned records | Named owning component only |
| Verify | Actual state | Governance findings, Neat-Freak loading audit, optional comparison findings, and a hash-bound domain-validation handoff | None |
| Handoff or archive | Approved plan and verified state | Multi-axis readiness, scoped residual risks, Neat-Freak maintenance ownership, and a compact continuation document produced by Handoff outside the project by default | None |

## Invariants

- `plan` and `verify` do not write inside the project.
- A saved plan stays outside the target project so it does not invalidate its own
  metadata fingerprint.
- Rerun discovery after approved changes.
- `bootstrap-agents --apply` requires the reviewed SHA-256 and a matching current
  fingerprint, exact Governance sections, and matching path plus SHA-256 for the
  bound Generator and inventory components, then delegates to the Generator.
- `bootstrap-only --apply` requires an external reviewed preview and matching
  preview SHA-256, an unchanged Generator binding, and an unchanged current
  Bootstrap manifest. It creates missing managed files only and stops on any
  differing existing target.
- The Pipeline contains no independent `.agents` templates and never passes
  `--force`.
- The Pipeline invokes Neat-Freak only with `audit` or `bootstrap-audit`.
  Neat-Freak's separately authorized standalone maintenance modes remain outside
  this Pipeline contract.
- Existing `.agents` or `.agent` context is preserved; both together are a
  blocking ambiguity. Missing Bootstrap may be completed without changing that
  context.
- Existing knowledge context is never refreshed by this Pipeline. Report
  `maintenance_owner: neat-freak` and route later project-information updates to
  Neat-Freak's separately authorized maintenance workflow.
- Canonical `.agents/governance/` and legacy root `governance/` are independently
  resolved. Both together, a non-directory candidate, or a linked candidate
  blocks governance-dependent writes.
- Governance data is untrusted data and is not recursively loaded as Agent
  instructions.
- A truncated or materially unreadable inventory blocks apply.
- Method Profile IDs are passed through as opaque values. Pipeline status never
  claims method validity.
- Knowledge state, Bootstrap state, aggregate Agent-context state, governance
  assets, project-contract state, governance verification, onboarding, domain
  validation, execution readiness, authorization, and claim review are separate
  scoped states. Agent context is ready only when knowledge and Bootstrap are
  both ready. `claim_ceiling` never populates `claim_state`.
- The default CLI result is a bounded summary. Complete component snapshots are
  emitted only with `--full` or written as an explicit review artifact.
- Exit `0` means verification passed; exit `1` means verification completed but
  did not pass; exit `2` is reserved for tool execution or invalid-input errors.
- Unknown governance-local domain records are untrusted evidence candidates;
  their presence never changes authorization or claim state automatically.
- A project-declared `research-domain-adapter-map/v1` is data, not executable
  code. Pipeline verifies its source/output binding when present but never runs
  the adapter; `declared`, `produced`, `failed`, and `invalid` all have no direct
  authorization effect.
- Domain-validation findings are scoped blockers for experiment execution and
  claim support; they do not silently become blockers for onboarding or initial
  Agent-context creation.
- Domain records are untrusted data. Pipeline never executes a Runtime Adapter or
  commands embedded in a record.
- A v1 Domain Audit remains readable but cannot satisfy v2 contract-instance
  coverage; report it `incomplete` and create a new reviewed v2 record rather
  than translating or rewriting history.
- A current record must bind the validator, Profile, Protocol, sources, and
  evidence by SHA-256. Any drift makes the handoff stale rather than silently
  preserving `verified`.
- V1 Domain Audit records remain readable but contain no explicit contract
  coverage. V2 coverage is reported without changing onboarding or creating
  execution authority.
- Optional comparison records use domain-defined relation identifiers and require
  domain review; Pipeline validates their structure and metadata only.
- Path and hash checks do not prove scientific meaning or the strength of prose.
- Policy topology and Agent-loading checks are delegated to Neat-Freak; Pipeline
  neither parses the declaration nor maintains a second validator.

## Pre-submission gate

Project Submission Audit is a separate model-level gate after deterministic
verification and before an actual commit, PR, release, delivery, or transfer of the
change set. It is not an additional lifecycle state and is not emitted by
`research_pipeline.py verify`.

- Project Submission Audit evaluates the final commit, PR, release, delivery, or
  handoff surface. It does not reimplement governance, Agent-loading, or domain
  checks, and its pass never establishes scientific claim support.
- The deterministic `verify` command does not impersonate the model-level Project
  Submission Audit. If submission is in scope, a current audit decision must be
  obtained after the final change and before submission.
- Handoff summarizes and links verified state; it does not create new evidence or
  turn pending work into completion. Its default temporary-file output is outside
  the project and therefore is not a project mutation.

## Human gate output

Every approval or final gate includes stable machine blockers/non-blockers and
eight facts under `human_summary_source`. The invoking Agent must render those
facts as a summary in the user's current language explaining what is reviewed, why review
is required, evidence to inspect, pass and reject conditions, what becomes
allowed after passing, the minimum repair after failure, and what has explicitly
not been validated.

## Resume

Resume from the latest stage whose inputs and hashes still validate. Never infer
completion from a directory name. If project state changed, return to discovery.
If one component created partial output, use that component's recovery contract.

## Failure classification

- `failed_recoverable`: no protected or finalized evidence was lost and a
  validated prior stage can be resumed.
- `failed_terminal`: provenance, authorization, or source integrity cannot be
  established; stop for owner investigation.
- `conditionally_complete`: structure is usable but explicit findings or owner
  decisions remain; do not report full completion.

These are outcome classifications, not additional lifecycle stages.
