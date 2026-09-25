# Engineering Operations: Git and GitHub Actions

Use this reference when an engineering repair reaches Git or hosted CI. It is a
fact and authorization contract, not a command runner. The Management Pipeline
routes the next action; an authorized operator performs it; Submission Audit
re-reads the current state.

## Git ref contract

- Bind base, local head, remote-before, and remote-after to exact 40- or 64-digit
  lowercase object IDs.
- Before push, fetch or otherwise establish current remote state and verify that
  remote-before is an ancestor of local head. Default to fast-forward only.
- Version 1 prohibits force and force-with-lease. A protected-branch rejection
  stops the operation; it does not authorize a force push, policy change,
  alternate remote, or pull request.
- Multiple ref updates use one atomic push. If the remote lacks atomic push,
  stop the entire operation instead of degrading to per-ref pushes.
- Before an authorized high-risk update or deletion, create a local backup ref
  `refs/codex-backup/<operation-id>/<ref-hash>`. A remote backup ref is a separate
  external write and needs separate authorization.
- Branch deletion requires an exact ref, unchanged remote SHA, and proof that it
  is neither the default nor a protected branch.
- Recovery from a backup ref, repush, branch recreation/deletion, and pull
  request creation each need a new authorization and execution receipt.

## GitHub Actions evidence

Query by exact `head_sha` without a branch filter first, then follow every page.
Record every returned run because one commit can have runs on multiple branches
or events. For each run record workflow ID/path, head branch, event, attempt,
status, conclusion, and every job and step. Bind the required-check policy by
reference.

The legacy combined commit status is supplemental only. A green combined status
cannot replace Actions run/job/step evidence, and a `pending` combined status
with successful Actions runs does not invalidate those runs. Missing pagination,
jobs, required-check policy, or exact head binding yields `incomplete` or
`stale`, never PASS.

## Independent facts and failure classes

Keep these facts independent:

```text
commit created | push accepted | CI passed | scientific run authorized
```

No arrow between them is automatic. A receipt is a historical assertion; final
audit compares it with the live Git and GitHub state and marks drift `stale`.

Classify failures as `portability`, `infrastructure`, `artifact_integrity`,
`contract`, or `scientific`. A negative scientific result may be a successful
engineering execution and must not be relabeled as command failure.

CI must be hermetic: fixed action SHAs, no persisted checkout credentials,
fixture or mock data instead of live GitHub calls in unit tests, random external
working directories, minimal environment, repeated tests, and before/after
checks that the worktree and formal output locations did not change. Windows is
required; Linux is informational but runs all 20-project-build test suites.
