# Pipeline Stage Contracts

The pipeline is a human-reviewed state machine. A stage may consume only a
validated output from the preceding stage. Natural-language console text is not
a stage contract.

## States

```text
discovered
architecture_proposed
awaiting_approval
framework_applying
framework_validated
context_planned
context_created_or_preserved
auditing
conditionally_complete
complete
failed_recoverable
failed_terminal
```

## Contract table

| Stage | Required input | Machine output | Mutation |
|---|---|---|---|
| Discover | Resolved project root | Generator inspection plus governance inventory | None |
| Architecture design | Complete inventories and research objective | Reviewed architecture/migration plan | None |
| Approval | Exact plan and fingerprint | Owner authorization bound to plan hash | None |
| Framework apply | Approved plan | Change manifest, rollback record, validation | Approved paths only |
| Context plan | Post-change inventory | Generator dry-run write set | None |
| Context create | Matching plan hash/fingerprint | New `.agents`/`.codex` or explicit preservation of `.agents`/`.agent` | Create-only by pipeline |
| Audit | Actual context and project | Structured findings and exit status | None |
| Final verification | Approved plan plus actual state | Acceptance and residual-risk report | None |

## Invariants

- `plan` and `verify` do not write inside the project.
- Plans written by support tooling must be outside the project so the act of
  saving a plan does not invalidate its own fingerprint.
- Re-run discovery after approved framework changes.
- `bootstrap-agents --apply` requires the exact SHA-256 embedded in the reviewed
  plan and recomputes the current workspace fingerprint.
- The pipeline creates `.agents` only when both `.agents` and legacy `.agent`
  are absent. Existing context is preserved for standalone generator review and
  refresh. Both names together are an ambiguity, not permission to select one.
- No stage passes `--force`, applies migration moves, or deletes files.
- A truncated or materially unreadable inventory blocks apply.
- Component schema major versions are checked before consumption.
- The inventory fingerprint is metadata-based drift detection, not a hostile
  tamper-proof content signature. Use repository revisions, signed manifests,
  or content hashes when the threat model requires stronger integrity.

## Resume

Resume from the latest stage whose inputs and output hashes still validate.
Never infer completion from a directory name alone. If project state changed,
return to discovery. If a component created partial output, follow that
component's recovery contract rather than rerunning the entire pipeline.

## Failure classification

- `failed_recoverable`: no protected/final evidence was lost and a validated
  prior stage can be resumed.
- `failed_terminal`: provenance, authorization, or source integrity cannot be
  established. Stop for owner investigation.
- `conditionally_complete`: the structure is usable but explicit audit findings
  or owner decisions remain; do not report it as fully complete.
