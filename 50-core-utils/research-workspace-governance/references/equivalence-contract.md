# Typed Equivalence Contract

Use this contract when a workflow compares implementations, operators, matrices,
observations, or summary metrics. The contract records what was actually shown
and blocks stronger conclusions that the evidence does not support.

## Relation types

| Type | Meaning | Does not by itself prove |
|---|---|---|
| `matrix_exact` | The domain comparator reports element-by-element equality under its declared representation. | Empirical observational or metric agreement without a protocol. |
| `matrix_global_phase` | The domain comparator reports equality up to one global phase, and the record explicitly states that this phase is physically irrelevant in scope. | Literal matrix identity or empirical agreement without a protocol. |
| `observational_protocol` | The declared protocol cannot distinguish the candidates within its stated observables and tolerance. | Operator or matrix equivalence, or agreement under another protocol. |
| `metric_only` | One named summary metric agrees within its declared tolerance. | Observational interchangeability or operator/matrix equivalence. |

Metric agreement is weaker than observational agreement. Observational agreement
is weaker than operator or matrix agreement. Never promote a weaker relation to a
stronger one because its result is convenient.

## Required record

Each record must contain:

- a stable `id`, one relation `type`, and a bounded `scope`;
- non-empty `evidence` produced by a domain-specific comparison or protocol,
  identified by a project path plus SHA-256 or an external ID plus content hash;
- a named `comparison_method`, explicit `tolerance` (including `null` for exact
  comparison), and non-empty `invalidation_keys`;
- `allowed_use` and `forbidden_inference` claim lists;
- a declared `status` of `verified`, `unverified`, `stale`, or `rejected`.

Read [equivalence-record.schema.json](equivalence-record.schema.json) for the
machine shape. Use `scripts/validate_equivalence_records.py` to validate the
record collection. The validator checks declaration consistency, evidence
metadata, hashes for project-contained evidence paths, invalidation drift, and
forbidden inference boundaries. It does not perform scientific comparison.

## Claim vocabulary

Use the following values in `allowed_use` and `forbidden_inference`:

- `matrix_identity`
- `matrix_equivalence_up_to_global_phase`
- `observational_interchangeability`
- `metric_comparison`
- `deduplicate_operator_evidence`
- `deduplicate_observation_evidence`

The validator rejects an allowed claim that is stronger than the declared
relation. It also requires weaker relations to state their important forbidden
inferences, so downstream consumers do not have to infer the safety boundary.

For example, a verified metric-only record remains deliberately narrow:

```json
{
  "id": "score-comparison-17",
  "type": "metric_only",
  "scope": {"metric": "accuracy", "dataset": "held-out-v3"},
  "evidence": [{"path": "runs/17/comparison.json", "sha256": "<64 hexadecimal characters>"}],
  "comparison_method": {"name": "absolute-difference", "result": "pass"},
  "tolerance": 0.000001,
  "invalidation_keys": {"implementation_sha256": "...", "dataset_sha256": "..."},
  "allowed_use": ["metric_comparison"],
  "forbidden_inference": [
    "matrix_identity",
    "matrix_equivalence_up_to_global_phase",
    "observational_interchangeability",
    "deduplicate_operator_evidence",
    "deduplicate_observation_evidence"
  ],
  "status": "verified"
}
```

## Invalidation

`invalidation_keys` bind the conclusion to inputs such as implementation hash,
protocol version, observable set, parameter set, environment, or dataset. When
`current_invalidation_keys` supplies a different value for a record, the
effective status becomes `stale` even if the stored record says `verified`.

Do not silently refresh a stale record. Rerun the domain comparison, preserve its
new evidence, and review a new or superseding record.

`verified` requires a passing comparison and a structurally valid record.
`unverified` means evidence is incomplete or not yet accepted, `stale` means an
invalidation key changed, and `rejected` preserves a reviewed negative result.
The validator returns `0` only when every record is effectively verified, `1`
for valid but non-verified records, and `2` for invalid declarations or unsafe
evidence paths/hashes.

## Ownership boundary

The research workspace layer owns this declaration and its traceability. A
domain tool owns numerical comparison and scientific validity. A pipeline may
invoke this validator and report its findings, but it must not manufacture a
passing comparison result or infer a stronger relation.
