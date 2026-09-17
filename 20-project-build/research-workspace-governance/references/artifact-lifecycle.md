# Artifact Lifecycle and Cleanup

Use this reference whenever the task involves source material, derived assets, resumable state, outputs, staging, retention, archival, or deletion.

## Classification

| Class | Examples across domains | Retention rule |
|---|---|---|
| Source record | Instrument export, original survey response, interview recording, source document snapshot, raw observation | Preserve; never clean automatically |
| External reference | Vendor calibration, public dataset snapshot, ontology, benchmark input | Preserve the exact used version and license/source metadata |
| Durable derived artifact | Cleaned table, coded corpus, calibrated signal, registered image, reusable feature set | Preserve by version while referenced or required to reproduce results |
| Working intermediate | Partial work, resumable state, or costly intermediate | Retain until downstream verification and retention decision |
| Evidence package | Resolved conditions, input identities, activity record, results, validation, and exclusions | Immutable after finalization |
| Deliverable | Report, paper source, submission, presentation, release export | Preserve released versions and provenance |
| Ephemeral | Cache, preview render, atomic-write temporary, disposable scratch | Delete when no live process or recovery need remains |
| Unknown | Unowned or unexplained file | Protect and investigate |

“Generated” is not a deletion class. Logs, manifests, audit tables, and plots may be generated but still be primary evidence.

## State transitions

```text
source record --transform--> durable derived artifact
                                  |
                                  v
                         working run/staging
                           |             |
                      validate          fail
                           |             |
                           v             v
                    finalized evidence  resumable/diagnostic state
                           |
                           v
                    deliverable/archive
```

Every transition identifies producer, input versions, parameters, timestamp, validation, and status. Preserve exclusions and rejected observations as records with reasons instead of silently removing them.

Correct a source record or finalized artifact through an append-only correction, new version, or documented superseding record. Preserve the original when legal, ethical, and storage rules allow; never silently rewrite history.

## Failure-safe publication

1. Resolve and boundary-check the intended output path.
2. Refuse an existing final destination by default.
3. Create a uniquely identified sibling staging directory on the same filesystem.
4. Write resolved configuration and input signatures before expensive work.
5. For long work, write atomic recovery points and a progress record. A resume verifies inputs, conditions, method/procedure, and work-unit identity.
6. Validate completeness, scientific invariants, machine-readable outputs, and required documentation.
7. Close file handles and flush logs.
8. Rename or replace staging into the final destination atomically when supported.
9. Mark the evidence package immutable. Publish a new version for later corrections.

Do not delete the existing final destination at step 2. If replacement is explicitly required, finish and validate the new package first, preserve or archive the old package, then perform a recoverable swap.

When the storage system does not provide atomic directory rename, write to a new immutable versioned location, validate it there, then publish a small completion marker, manifest state transition, or pointer whose update semantics are documented. Readers must ignore versions without a valid completion marker. Do not simulate atomicity by copying over a live final prefix file by file.

Prevent duplicate writers with a mechanism appropriate to the execution system: exclusive create, transaction, lease with expiry and ownership, scheduler-level mutual exclusion, or an operating-system-held lock. A persistent lock filename alone is not proof that a process is active. Record run identity and writer ownership, and define safe stale-lock recovery.

Atomic-write files such as `name.tmp.json` should be written, flushed as appropriate, and renamed over `name.json`. A leftover temporary is disposable only after confirming no writer is active and the stable target is complete or the interrupted attempt has been abandoned.

## Cleanup decision test

An artifact is eligible for deletion only when all applicable answers are satisfactory:

1. **Role known:** Is it explicitly ephemeral, or has its retention expired?
2. **Producer known:** Can it be regenerated, and is the producing method available?
3. **Inputs available:** Are all required source records, versions, parameters, and environments accessible?
4. **Consumers checked:** Do manifests, configs, code, reports, publications, or collaborators still reference it?
5. **Recovery checked:** Is it unnecessary for resume, audit, dispute resolution, or failure diagnosis?
6. **Authority present:** Did the owner authorize deletion of this class or exact target?
7. **Boundary verified:** Does the resolved absolute target remain inside the approved cleanup root?
8. **Concurrency checked:** Is no process, scheduler, lock, sync client, or collaborator actively using it?
9. **Preview reviewed:** Has a dry-run manifest shown exact paths, counts, and sizes?
10. **Post-check defined:** Is there a verification and, when material, a backup or rollback path?

If any answer is unknown, retain or quarantine the artifact. Do not infer disposability from a name such as `old`, `backup`, `copy`, `tmp`, or `final`.

## Cleanup classes

### Usually safe after concurrency checks

- language and tool caches;
- reproducible preview renders;
- empty scratch directories;
- completed atomic-write temporaries whose stable targets are valid;
- staging from an explicitly abandoned, non-resumable attempt.

### Conditional

- resumable recovery state;
- failed-run staging and diagnostic logs;
- local copies of verified remote artifacts;
- superseded derived datasets;
- intermediate exports used by publication tooling;
- lock files, which may persist after release by design.

### Retain by default

- source records and external-reference snapshots actually used;
- consent, provenance, exclusion, calibration, and audit records;
- formal run manifests, resolved configurations, primary results, and validation;
- released deliverables and editable sources;
- unclassified or access-restricted artifacts.

## Retention policy

Define retention by role, not extension:

```text
artifact class | minimum retention | trigger | archival destination
owner | deletion authority | required checks | legal/ethical constraints
```

Distinguish active storage, reproducibility archive, compliance archive, and disposable cache. If storage cost requires pruning large run internals, first define the minimal reproducibility package and prove that it recreates the retained primary results.

Checksums detect unexpected change but are not backups. Define independent copies or replicated durable storage, access recovery, restore ownership, and periodic recovery tests according to the loss impact. Do not rely on a working directory, synchronization service, or version-control metadata as the only copy of irreplaceable source records.

## Cleanup report

Report what was removed, exact scope, total files/bytes, why each class was eligible, what was retained, verification performed, and whether recovery remains possible. Never describe a deletion as reversible unless a verified backup, trash, snapshot, or archive exists.
