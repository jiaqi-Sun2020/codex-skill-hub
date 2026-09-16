# Legacy Project Integration

Integrate incrementally. An established name is not a defect when its role,
authority, and mutability are clear.

## Default strategy

1. Inventory metadata without opening sensitive content or following links.
2. Resolve governance and Agent-context locations independently.
3. Map existing paths to roles before proposing new paths.
4. Preserve unknown and owner-authored material.
5. Add only records or boundaries that solve a demonstrated ambiguity.
6. Prefer adapters, manifests, and documented aliases over relocation.
7. Change references only through an exact reviewed map and focused verification.
8. Keep historical identities distinct; do not relabel old evidence as if it had
   been produced under a new contract.

## Governance roots

- Only `.agents/governance/`: canonical.
- Only root `governance/`: supported legacy authority; continue in place.
- Neither: absent; recommend canonical after Generator creates `.agents`.
- Both: ambiguous and write-blocking until the owner selects one authority and
  approves treatment of the other.
- A file, link, junction, reparse point, or escaping path at either candidate is
  unsafe and write-blocking.

Do not decide authority from timestamps, size, completeness, or naming style.
Governance data is never recursively loaded as Agent instructions.

## Existing `.agents` or `.agent`

The Pipeline preserves either context bundle. If both exist, stop for an owner
decision. Inside this one-time Pipeline, creation of a missing initial context is
delegated to `project-agent-generator-skill`, while knowledge and loading audit
is delegated to `neat-freak`. Existing context is not refreshed here; after
handoff, route reviewed project-information maintenance to Neat-Freak.

## Migration preview

Before any move, record:

```text
absolute source and destination
classified role
files and bytes
hashes where meaningful
dependents and references
active processes, schedulers, and locks
collisions and protected paths
reference-update set
rollback and verification
authority approving the move
```

Store an approved relocation map as a new version. Do not rewrite old maps,
historical records, or old locks. Resolve historical paths through the map only
for the task that needs them.

New contracts use `project_contract.json` with
`research-project-contract/v2`. A historical `project_contract.yaml` containing
the old JSON subset is a readable legacy v1 input; real YAML is not guessed. If
both filenames exist, contract authority is ambiguous and write-blocking.

Workspace inventory uses v2. Saved Pipeline plans use
`research-project-pipeline-plan/v3`, while command results use
`research-project-pipeline-result/v1`. A v1 inventory may be adapted for
read-only discovery but cannot establish governance authority; refresh it with
v2 before mutation. Hash-bound Pipeline plans using the former v1 or ambiguous
v2 identifier must be regenerated rather than translated and applied.

## Compatibility gate

Before accepting integration, verify established commands from their documented
working directories, project-contained paths, protected source and finalized
evidence, external consumers, automation triggers, recovery behavior, and scoped
status authority. Keep a compatibility adapter only with a named owner and
retirement condition.
