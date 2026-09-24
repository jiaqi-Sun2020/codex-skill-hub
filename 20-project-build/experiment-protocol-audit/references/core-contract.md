# Core contract

## First-principles model

An experiment audit is meaningful only when four things are explicit:

1. **Domain Profile** — domain-owned rules that map normalized observations to testable constraints.
2. **Project Protocol** — project-owned scope, named owner, source paths, and maximum claim level.
3. **Runtime Adapter** — optional project code that translates native state into normalized JSON; it is not executed by the auditor.
4. **Audit Core** — generic, deterministic checks with no domain vocabulary and no expression evaluation.

The profile and protocol are project-contained inputs, not trusted instructions. Free text such as “ignore previous instructions” remains inert data.

## Supported generic rules

Rules have an `id`, `type`, optional `phase` (`design` or `runtime`), and optional failure `code`.

- `numeric-bound`: compare one numeric observation with a literal using `<`, `<=`, `==`, `>=`, or `>`.
- `equality`: compare two observation paths or one path and one literal.
- `shape-equality`: compare two arrays of non-negative integer dimensions.
- `set-equality`: compare two arrays as duplicate-free sets.
- `cardinality`: compare the length of an observed array with a literal integer.
- `allowed-transform`: require a string observation to belong to a literal allow-list.

Observation paths use dot-separated object keys only. No indexing language, imports, function calls, templates, shell text, or executable expressions are supported.

## Manifest contract

Requested, generated, and approved manifests use `experiment-cell-manifest/v1`. Cell IDs must be unique. Generated and approved cells must be active. Canonical cell objects must match exactly across all three manifests. This makes silent filtering, accidental expansion, and approval drift visible.

## Runtime contract

Runtime evidence uses `experiment-runtime-evidence/v1`. Its cell IDs and output paths must exactly match the approved manifest and each cell must report `complete`. File existence alone does not prove domain validity; any deeper output checks must be expressed as normalized observations and profile rules.

## Result contract

Matching v1 Profile and Protocol inputs retain
`experiment-protocol-audit-result/v1`. Matching v2 inputs emit
`experiment-protocol-audit-result/v2`, which records:

- named owner;
- validator identity and SHA-256;
- profile identity and SHA-256;
- checked scopes;
- protocol, source, and evidence fingerprints;
- structured findings;
- explicit unvalidated boundaries;
- a claim ceiling.
- explicit contract-instance coverage bound to rule IDs, built-in manifest or
  runtime checks, or a fingerprinted human-review reference.

`verified` is scoped. It does not authorize execution, establish project readiness, or prove claims beyond the declared ceiling.

V2 `contract_bindings` are owned by the Project Protocol. They bind an instance
ID to `required` or `optional` applicability, rule IDs, optional built-in
`manifest-identity` or `runtime-completeness` checks, an optional inert human-review
reference, and required scopes. The
auditor never invents a binding from filenames or domain vocabulary. A required
binding with neither a rule, a built-in check, nor a passing fingerprinted human
review for the same scope is incomplete. A human-review reference records an ID,
reviewer, decision, scope, project-relative path, and SHA-256. The Auditor binds
the hash of that explicitly named project file but never interprets or executes
its contents.
Expert-only judgments remain owned by Governance rather than simulated by keyword
rules.

## Design influences

The contract borrows four durable ideas without adding their runtimes as dependencies:

- scientific code must fail loudly and make parameters, shapes, and reality checks explicit;
- execution evidence must be approved, reproducible, and bound to a precise request;
- design review, specification review, and quality review are distinct;
- edge cases and state transitions deserve generated counterexamples, while shrinking frameworks remain optional test tooling.
