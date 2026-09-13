# Architecture Contract

Use this reference to design or audit the boundaries of a research workspace. Folder names are examples; roles and dependency direction are the contract.

## Required roles

| Role | Purpose | Default mutability |
|---|---|---|
| Governance | Scope, ownership, decisions, conventions, retention, and operating instructions | Reviewed changes |
| Protocols | Research questions, preregistration, acquisition/analysis plans, and deviations | Versioned changes |
| Source records | Original observations, instrument exports, source documents, field notes, external reference snapshots | Immutable |
| Methods | Code, notebooks, schemas, instruments, forms, and reusable procedures | Version controlled |
| Derived data | Cleaned, normalized, coded, joined, calibrated, or feature-ready material | Immutable by version |
| Experiments/analyses | Run definitions, orchestration, tests, and report generation logic | Version controlled |
| Run evidence | Resolved parameters, provenance, checkpoints/models where needed, logs, results, and validation | Immutable after finalization |
| Reports | Internal interpretations, decision records, and review packages | Versioned |
| Publications/deliverables | Submitted or shared artifacts and their editable sources | Immutable releases plus new revisions |
| Archive | Superseded but retained evidence with an index and retention basis | Immutable |
| Temporary workspace | Reproducible previews, atomic-write files, caches, and disposable scratch | Disposable by contract |

## Reference layout

Adapt this layout rather than forcing it onto an established project:

```text
project/
|-- governance/
|-- protocols/
|-- data/
|   |-- raw/
|   |-- external/
|   |-- derived/<dataset-id>/
|   `-- audits/<audit-id>/
|-- src/                       # or methods/
|-- notebooks/                # exploratory unless governed as a formal method
|-- experiments/<study-id>/
|-- runs/<run-id>/
|-- reports/<report-id>/
|-- publications/<release-id>/
|-- archive/
|-- scripts/
|-- tests/
`-- .tmp/
```

Small projects may merge roles when ownership remains unambiguous. Large, multi-team, sensitive, or regulated projects may separate storage systems rather than directories. Record logical paths and access classes in the same role map.

## Proportional profiles

- **Lightweight:** one researcher, low-risk exploratory work. A compact tree and one artifact register are enough if roles, provenance, backups, and finalization remain explicit.
- **Collaborative:** repeated runs or multiple contributors. Add stable identifiers, ownership, review gates, shared manifests, collision protection, and documented handoff.
- **Controlled:** sensitive, regulated, costly, or long-lived work. Add access classes, chain of custody, approvals, audit trails, validated storage, retention schedules, and tested recovery appropriate to the governing requirements.

Choose the least ceremony that still protects the evidence. Do not create empty folders or records merely to resemble the reference layout.

## Dependency direction

```text
protocols + source records + methods + resolved configuration
                            |
                            v
                      derived data
                            |
                            v
                    experiment/analysis run
                            |
                            v
                       run evidence
                            |
                            v
                 reports and publications
```

- Downstream stages read upstream artifacts; they do not rewrite them.
- Derived data records all source identifiers and transformation versions.
- Reports and figures may select or summarize evidence but never become the hidden source of computed values.
- Shared utilities remain domain-neutral; study-specific assumptions stay with the owning protocol or experiment.
- Manual transformations must be captured as a reviewed procedure, change record, or machine-readable operation rather than hidden edits.
- Notebooks used as formal methods must run from a clean state or be promoted into a reproducible pipeline; cell output and execution order alone are not provenance.

## Folder contract fields

For each material folder, document:

```text
role:
owner:
allowed contents:
forbidden contents:
producers:
consumers:
mutability:
required metadata:
validation:
retention:
deletion authority:
```

If a path serves two incompatible roles, split it or make the sub-boundaries explicit. Warning signs include source code mixed with generated outputs, raw data mixed with cleaned data, independent runs writing into one directory, or canonical deliverables mixed with previews.

## Identifiers and versions

- Use stable, filesystem-safe identifiers that do not depend only on a display title.
- Include semantic versions, protocol versions, or sortable run timestamps when they help distinguish evidence.
- Never use `final`, `final2`, or `latest` as the only identity of a formal artifact. A `latest` pointer may reference, but must not replace, an immutable version.
- Record relationships such as `derived_from`, `supersedes`, `reproduces`, and `published_as` in manifests or an artifact registry.

## Formal run contract

A completed run should normally provide:

```text
runs/<run-id>/
|-- README.md or REPORT.md
|-- manifest.json              # identity, status, timestamps, producers
|-- config.resolved.*          # actual parameters, not only source config
|-- inputs.*                   # identifiers and hashes/signatures where appropriate
|-- environment.*              # relevant runtime and dependency information
|-- logs/
|-- results/                   # machine-readable primary results
|-- validation/                # tests, audits, diagnostics, exclusions
|-- figures/                   # derived views, when applicable
`-- models-or-checkpoints/     # only when required for reproduction or reuse
```

The exact files depend on the domain. A wet-lab run may record instrument state, batch, operator, calibration, protocol deviation, and sample chain of custody; a qualitative study may record coding schema, consent/access controls, coder decisions, and de-identification state; a simulation may record code revision, seed, solver, hardware, and numerical tolerances.

## Architecture acceptance conditions

- Every material artifact has one primary role and owner.
- Every scientific output has an identifiable producer and upstream evidence.
- Raw/source records cannot be overwritten by ordinary processing.
- Independent runs cannot silently merge.
- A failed run cannot replace the last known-good final run.
- Sensitive information has access and disclosure rules distinct from ordinary provenance.
- Source records and formal evidence have integrity checks, independent backup or durable replicated storage, and a tested recovery path proportional to their value and obligations.
- New collaborators can locate the active protocol, inputs, method, formal results, and limitations without oral history.
