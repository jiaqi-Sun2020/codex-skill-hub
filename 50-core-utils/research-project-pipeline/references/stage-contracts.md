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
| Discover | Resolved project root | Generator inspection, Governance inventory, optional declarations | None |
| Design | Complete inventory and objective | Reviewed governance and component-action proposal | None |
| Human review | Exact plan and fingerprint | Owner authorization bound to plan hash | None |
| Controlled change | Approved plan | Generator-owned initial context creation and/or Governance-owned records | Named owning component only |
| Verify | Actual state | Governance findings plus Neat-Freak loading audit and optional comparison findings | None |
| Handoff or archive | Approved plan and verified state | Five-pass acceptance, scoped status, residual risks, and Neat-Freak maintenance handoff | None |

## Invariants

- `plan` and `verify` do not write inside the project.
- A saved plan stays outside the target project so it does not invalidate its own
  metadata fingerprint.
- Rerun discovery after approved changes.
- `bootstrap-agents --apply` requires the reviewed SHA-256 and a matching current
  fingerprint, exact Governance sections, and matching path plus SHA-256 for the
  bound Generator and inventory components, then delegates to the Generator.
- The Pipeline contains no independent `.agents` templates and never passes
  `--force`.
- The Pipeline invokes Neat-Freak only with `audit` or `bootstrap-audit`.
  Neat-Freak's separately authorized standalone maintenance modes remain outside
  this Pipeline contract.
- Existing `.agents` or `.agent` context is preserved; both together are an
  ambiguity.
- Existing context is never refreshed by this Pipeline. Report
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
- Work completion and claim support are separate scoped states.
- Optional comparison records use domain-defined relation identifiers and require
  domain review; Pipeline validates their structure and metadata only.
- Path and hash checks do not prove scientific meaning or the strength of prose.
- Policy topology and Agent-loading checks are delegated to Neat-Freak; Pipeline
  neither parses the declaration nor maintains a second validator.

## Human gate output

Every approval or final gate includes stable machine blockers/non-blockers and
seven facts under `human_summary_source`. The invoking Agent must render those
facts as a summary in the user's current language explaining what is reviewed, why review
is required, evidence to inspect, pass and reject conditions, what becomes
allowed after passing, and the minimum repair after failure.

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
