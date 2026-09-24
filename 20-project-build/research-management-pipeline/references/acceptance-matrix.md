# Cross-Disciplinary Acceptance Matrix

This matrix turns T01–T22 into generic failure hypotheses. Domain names and
numbers below are counterexamples, not universal contracts. The core code must
not branch on them.

| ID | Failure hypothesis | Evidence |
|---|---|---|
| T01 | A declared finite design silently gains or loses work units. | Protocol Audit cardinality and exact manifest-identity tests. |
| T02 | Data-level replicates and technical measurements are incorrectly merged. | Cross-disciplinary Profile test checks only the explicitly selected biological-unit path. |
| T03 | A theoretical project is forced to provide runtime, randomness, accelerator-specific, or statistical-test artifacts. | Governance accepts applicable SCI and STAT-13 contracts without unrelated ENG requirements. |
| T04 | A qualitative project is forced into a quantitative lifecycle. | Governance accepts an SCI plus GOV provenance subset. |
| T05 | A review project is forced to run experiments or generate charts. | Governance accepts question and evidence-admission contracts only. |
| T06 | Missingness is silently filled or ignored. | A declared missingness-policy rule fails on an absent observation. |
| T07 | Rounded output is treated as exact equality. | Equality fails when reported and computed values differ before any declared transform. |
| T08 | A fixed inclusion list permits silent additions, removals, or duplicates. | Set-equality and exact manifest tests fail on drift. |
| T09 | A supported `claim_ceiling` becomes a supported Claim. | Onboarding Pipeline keeps `claim_state=unreviewed` and authorization separate. |
| T10 | Negative evidence is classified as failed work rather than admitted contradiction. | Registry accepts an independently reviewed `contradicted` Claim while reporting evidence completeness separately. |
| T11 | An empty contract-aware audit reports `verified`. | Protocol Audit v2 returns `incomplete` for empty or uncovered required bindings. |
| T12 | A method or implementation amendment leaves dependents current. | Governance impact walks reverse dependencies with a visited set. |
| T13 | Generated, approved, or runtime work differs from the reviewed request. | Exact manifest and runtime identity tests fail loudly. |
| T14 | A revision rewrites historical PASS or evidence records. | Impact output asserts `historical_records_modified=false`. |
| T15 | Partial or stale evidence is treated as complete support. | Registry reports `evidence_missing_or_stale` and an incomplete gate. |
| T16 | Instruction-like governance text executes. | Auditor and validator read-only tests preserve the filesystem and treat strings as data. |
| T17 | A dual governance root, link, junction, or escaping path acquires write authority. | Inventory and validator path-safety tests block ambiguity and escape. |
| T18 | Invalidation stops before affected Claims or deliverables. | Amendment impact tests include affected Claim and deliverable closure. |
| T19 | A real external authorization cannot be represented separately from scientific review. | Registry accepts a traceable granted authorization decision without creating a Claim. |
| T20 | Routine changes rerun Generator or bypass the owning audit component. | Management has no scripts and routes Governance, Protocol Audit, Neat-Freak, and Submission Audit explicitly. |
| T21 | Self-authored `approved=true` creates authority. | Authorization requires a distinct stable decision reference; self-assertion remains a gap. |
| T22 | A simple project without version-control automation, randomness, specialized hardware, or an execution environment cannot be governed. | Minimal theoretical, qualitative, and review registries validate with only applicable contracts. |

Acceptance requires both the stated assertion and the absence of a domain-specific
branch in shared code. A passing process exit code alone is not evidence for any
row.
