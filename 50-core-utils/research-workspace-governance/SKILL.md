---
name: research-workspace-governance
description: Design, audit, initialize, manage, migrate, archive, or clean a research workspace with explicit objectives, artifact roles, provenance, claim-evidence links, immutable evidence, failure-safe publication, retention, and reproducibility. Use for research-project lifecycle and structure, source/derived/intermediate/final/temporary boundaries, experiment isolation, handoff, or cleanup policy. Do not use when the primary task is scientific-method selection, model/training-code architecture, project knowledge-base maintenance, skill refactoring, or ordinary file tidying unrelated to research evidence.
---

# Research Workspace Governance

Build a research workspace whose claims can be traced to inputs and methods, whose completed evidence cannot be overwritten accidentally, and whose disposable files can be identified without guessing. Adapt the structure to the research domain instead of imposing a tool-, language-, or model-specific repository.

## Select the operating mode

| Mode | Permitted action |
|---|---|
| Audit | Inspect and report only. Do not rename, move, create, or delete. |
| Design | Produce a proposed architecture, contracts, and migration plan without changing files. |
| Initialize | Create only the approved missing structure and governance files. Preserve existing content. |
| Manage/handoff | Maintain the approved charter, work state, decisions, deviations, risks, and claim-evidence map without rewriting scientific evidence. |
| Migrate | Apply an approved source-to-destination map with collision checks and rollback information. |
| Finalize/archive | Validate a completed evidence package and publish or archive it without changing its scientific contents. |
| Clean | Preview classified cleanup candidates; delete only explicitly authorized, exact targets. |

Infer the least-mutating mode consistent with the request. Words such as “review”, “audit”, “assess”, or “recommend” never authorize writes. Reorganization does not imply deletion authority.

## First-principles invariants

1. A research claim is defensible only when its source observations, transformations, parameters, execution context, and validation evidence are traceable.
2. Mutability follows epistemic role: source records and published evidence are immutable; derived artifacts are replaced only by a new version; working state may be resumable; temporary artifacts are disposable by contract.
3. “Intermediate” does not mean “temporary”. A derived dataset, calibrated instrument state, coded corpus, or cleaned table may be required to reproduce every downstream result.
4. A completed run is an evidence package, not a scratch directory. Do not mix outputs from independent runs or silently refresh files inside it.
5. Cleanup is a classification decision supported by provenance and dependency evidence. Age, size, filename, or apparent duplication alone is insufficient.
6. Failure must preserve the last known-good evidence. Build beside the destination, validate, then publish atomically when the filesystem permits; never delete the old final artifact before the replacement passes.
7. The framework must expose uncertainty. Mark inferred roles, unresolved ownership, and missing provenance rather than inventing them.
8. Equivalence is typed and scoped. Metric agreement does not prove observational agreement, and observational agreement does not prove operator or matrix equivalence.

## Workflow

### 1. Establish the contract

- State the real research objective, expected deliverables, evidence standard, collaborators, execution environment, retention obligations, and current failure point.
- Identify whether the work is computational, experimental, observational, qualitative, mixed-methods, or regulated. This changes artifact types and validation, not the core invariants.
- Distinguish exploratory, confirmatory, and operational work. Record preregistration or protocol deviations when that distinction affects claims.
- Ask at most the critical question that would materially change safety or architecture. Otherwise proceed with clearly labeled assumptions.

### 2. Inventory before prescribing

- Read applicable project instructions and current documentation first.
- Inventory paths, sizes, timestamps, manifests, configs, entry points, ignore rules, and producer/consumer references. Avoid opening large raw content when metadata is sufficient.
- Do not inspect suspected credentials, private keys, tokens, participant-identifying data, or restricted records without explicit need and authorization.
- For each material path, record: role, producer, inputs, consumers, mutability, validation, retention, and deletion authority.
- Mark unclassified artifacts as protected until their role is established.

For a deterministic metadata-only first pass, use the optional standalone
interface described in [references/pipeline-interface.md](references/pipeline-interface.md).
Its role hints are evidence for review, not an automatic migration or deletion decision.

### 3. Govern the research lifecycle

Read [references/research-lifecycle.md](references/research-lifecycle.md) when initializing or managing a project, planning work, recording decisions or deviations, assessing readiness, or preparing a handoff/archive.

- Keep the research question, decision context, evidence standard, scope, and stopping conditions visible.
- Track work packages, dependencies, risks, owners, and status at the smallest useful level; do not turn the repository into an unnecessary project-management database.
- Connect conclusions to versioned evidence and record contradictory or negative results rather than preserving only successful narratives.
- Treat protocol changes, analysis deviations, and claim changes as reviewable decisions with rationale and impact.

### 4. Model the workspace

Read [references/architecture-contract.md](references/architecture-contract.md) when designing, initializing, or restructuring a workspace.

- Separate research intent/protocols, immutable source records, reusable methods/code, versioned derived data, run-scoped evidence, reader-facing deliverables, archives, and ephemeral working space.
- Define dependency direction and prohibit reverse writes from reports or publication tooling into source records.
- Prefer role contracts over exact folder names. Preserve established names when they already satisfy the contracts.
- Give every formal dataset, run, and deliverable a stable identifier and a manifest or equivalent provenance record.

### 5. Govern the artifact lifecycle

Read [references/artifact-lifecycle.md](references/artifact-lifecycle.md) for data handling, run publication, checkpoints, retention, cleanup, or archival.

- Classify every artifact before moving or deleting it.
- Use versioned destinations rather than in-place transformation.
- Make formal runs self-contained enough to understand and verify without relying on mutable global state.
- Use sibling staging for atomic publication on one filesystem. For long work, retain validated checkpoints and an explicit resume contract.
- Keep logs and status records when they explain failure or support provenance; do not label them temporary merely because they are machine-generated.

When a workflow compares implementations, operators, observations, or metrics,
read [references/equivalence-contract.md](references/equivalence-contract.md).
Require a typed, scoped record with domain-produced evidence, allowed uses,
forbidden inferences, and invalidation keys. The governance validator may check
that record and its evidence metadata; it must not substitute for a scientific
comparison protocol.

### 6. Change only within authority

- Before migration, produce an exact mapping with collisions, link/reference updates, rollback path, and verification checks.
- Before cleanup, produce a dry-run manifest divided into safe-to-delete, conditional, retain, and unknown. Do not recursively delete a broad root, unresolved path, or computed target that has not been boundary-checked.
- Preserve unrelated user changes. Never use destructive version-control recovery to simplify migration.
- When commands are required, state the working directory and provide complete, reversible commands. Prefer native same-shell filesystem operations.

### 7. Validate and challenge the result

Read [references/adversarial-audit.md](references/adversarial-audit.md) for structural changes, migrations, cleanup, archival, or when the user asks whether the framework is sufficient.

- Validate observable invariants: required manifests exist, recorded inputs resolve, hashes or signatures match when used, final outputs are complete, staging is distinguishable, and no protected source was modified.
- Conduct separate adversarial passes for scope/domain fit, traceability/reproduction, failure/deletion safety, operational usability, policy reachability, and equivalence/inference safety when those concerns apply. A repeated reread is not a distinct audit.
- Repair supported defects and rerun the affected pass. Report residual risks and owner decisions that remain.

## Deliverables

Use [references/deliverable-templates.md](references/deliverable-templates.md) when a durable architecture brief, lifecycle register, migration plan, run manifest, cleanup manifest, or acceptance report is requested.

Lead with the conclusion. Then provide the minimum useful combination of:

- current-state and target-state maps;
- charter, work-state, decision/risk/deviation, and claim-evidence records when relevant;
- folder and artifact contracts;
- data/evidence flow;
- migration or initialization changes;
- run, retention, and cleanup policy;
- how to execute and verify;
- unresolved risks, assumptions, and cautions.

Do not claim that a workspace is reproducible merely because it has the recommended folders. Reproducibility requires complete provenance, executable or documented transformations, controlled inputs, and verification evidence.

## Standalone and pipeline compatibility

This Skill remains independently usable. The pipeline interface is additive:
it does not require the project-agent generator, does not create `.agents`, and
does not change the authorization rules above. An orchestrator may consume its
versioned JSON inventory, but must not bypass semantic review, approval gates,
or this Skill's adversarial audit.
