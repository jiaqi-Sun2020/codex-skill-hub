# Research Contract Taxonomy

This catalog classifies responsibilities; it is not a mandatory sequence and a
project must instantiate only the contracts that affect its decisions. Domain
Profiles may add namespaced contracts while retaining one of the four owning
categories. A custom contract needs an authoritative definition reference.

## SCI — scientific validity

| ID | Responsibility |
|---|---|
| SCI-01 | Research question, target object, scope, and intended estimand or conclusion. |
| SCI-02 | Theory, mechanism, assumptions, and testable implications. |
| SCI-03 | Intervention, initial condition, measurement, and operational definition. |
| SCI-04 | Research type and scientific role. |
| SCI-05 | Validity, identifiability, proof obligations, or counterexamples. |
| SCI-06 | Domain semantics, units, coordinates, labels, and representation mapping. |
| SCI-07 | Comparisons, controls, competing explanations, and refutation. |
| SCI-08 | Claim scope, limits, and conditions of use. |
| SCI-09 | Calibration and domain validation. |

## STAT — evidence design

| ID | Responsibility |
|---|---|
| STAT-01 | Target population and evidence selection. |
| STAT-02 | Evidence scale, sample rationale, and partitions. |
| STAT-03 | Data-level repetition and variation. |
| STAT-04 | Method-level repetition and variation. |
| STAT-05 | Dependence, reuse, nesting, and blocking. |
| STAT-06 | Comparison, pairing, randomization, blinding, or declared alternatives. |
| STAT-07 | Evidence-unit completeness and allowed missingness. |
| STAT-08 | Uncertainty and inference. |
| STAT-09 | Robustness and sensitivity. |
| STAT-10 | Evaluation and target distribution. |
| STAT-11 | Missingness, anomalies, exclusions, and selective reporting. |
| STAT-12 | Analysis plan and stopping rule. |
| STAT-13 | Non-statistical evidence arguments, including qualitative and theoretical review. |

STAT does not require statistical testing. A theoretical, qualitative, or review
project may use only the applicable evidence contracts and record reviewed
not-applicability for the rest.

## ENG — implementation and artifact integrity

| ID | Responsibility |
|---|---|
| ENG-01 | Schema, interface, and versioning. |
| ENG-02 | Names, paths, and identity. |
| ENG-03 | Work graph and manifests. |
| ENG-04 | Acquisition, import, and publication. |
| ENG-05 | Representation parsing and information isolation. |
| ENG-06 | Provenance and fingerprints. |
| ENG-07 | Implementation and method-version binding. |
| ENG-08 | Execution environment, refined by ENG-08.1 through ENG-08.6 when applicable. |
| ENG-09 | Executors and concurrency isolation. |
| ENG-10 | Randomness and numerical reproducibility when applicable. |
| ENG-11 | Interruption and recovery. |
| ENG-12 | Logs and events. |
| ENG-13 | Evaluation outputs. |
| ENG-14 | Synthesis and aggregation. |
| ENG-15 | Preview and side effects. |
| ENG-16 | Validation and release. |
| ENG-17 | Data access and de-identification. |

Environment refinements are: `ENG-08.1` software/toolchain, `ENG-08.2`
hardware/instrument/firmware/calibration, `ENG-08.3` precision/tolerance,
`ENG-08.4` isolation/process/access, `ENG-08.5` resource/concurrency/storage,
and `ENG-08.6` cross-environment reproducibility, repeatability, or comparability.

## GOV — authority and lifecycle governance

| ID | Responsibility |
|---|---|
| GOV-01 | Project and asset boundaries. |
| GOV-02 | Protected and writable scope. |
| GOV-03 | Authority, precedence, and conflict resolution. |
| GOV-04 | Stage authorization. |
| GOV-05 | Review responsibility, independence, and conflicts of interest. |
| GOV-06 | Adversarial and counterexample review. |
| GOV-07 | Blocking and stopping conditions. |
| GOV-08 | History, retention, and locks. |
| GOV-09 | Pilot and formal-evidence separation. |
| GOV-10 | Evidence admission. |
| GOV-11 | Claim-to-deliverable handoff. |
| GOV-12 | Amendment and invalidation propagation. |
| GOV-13 | Ethics, consent, licensing, privacy, safety, and funding constraints. |
| GOV-14 | Correction, retraction, and separately authorized notification. |

## Cross-category rule

One fact has one normative owner. Other categories reference it. For example,
SCI-03 defines what a measurement means, ENG-08.2 records the instrument state,
and GOV-13 records the applicable approval. None duplicates the other two.
