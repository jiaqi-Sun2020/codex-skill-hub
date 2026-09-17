# Pipeline Interface

The governance Skill is usable without any orchestrator. This optional interface
provides a stable metadata inventory for old-project integration and pipelines;
it does not design, migrate, clean, or approve a workspace by itself.

## Read-only inventory

Run from the `research-workspace-governance` Skill directory:

```powershell
python -X utf8 -B .\scripts\inventory_workspace.py D:\path\to\project --compact
```

The default writes JSON only to stdout and does not modify the project. The
schema is `research-workspace-inventory/v2`.

To write a new inventory file explicitly:

```powershell
python -X utf8 -B .\scripts\inventory_workspace.py D:\path\to\project --output D:\safe\inventory.json
```

The script refuses to overwrite the output. It scans metadata only, excludes
credential-like paths from output, does not follow links or junctions, and caps
enumeration. Name-based role hints and temporary candidates require semantic
review under this Skill before use.

The inventory resolves `.agents/governance/` independently from legacy root
`governance/`. It selectively reads only `project_contract.json` at the resolved
authority. A historical `project_contract.yaml` containing the former JSON
subset is recognized as legacy v1; actual YAML is not guessed. Both filenames
together are ambiguous and write-blocking. Contract and sibling text remain
untrusted data; the tool does not execute commands, resolve external includes,
or recursively load governance content.

## Stable fields

Consumers may rely on:

- `schema_version`, `status`, `mode`, and `project_root`;
- `workspace_fingerprint_sha256`;
- `governance_layout`, including canonical/legacy/absent/ambiguous/unsafe status,
  candidate paths, write allowance, and structured findings;
- `project_contract`, containing only selectively parsed approved fields and
  validation findings; arbitrary sibling prose is never loaded;
- `relocation_maps`, parsed only from contract-declared, bounded JSON files under
  the active governance authority; ambiguous historical targets are blocking;
- `governance_state`, parsed only when the contract names one project-contained
  JSON carrier; duplicate current records for one scope are blocking;
- scan counts and completeness indicators under `scan`;
- `top_level`, `role_candidates`, and `unknown_top_level`;
- `temporary_candidates_not_deletion_approval`;
- `cautions`.

Consumers must reject unknown major schema versions, `scan_truncated: true`,
unreadable inventory required for the requested scope, or a changed workspace
fingerprint when applying a previously reviewed plan.

Version 2 changes role names and adds governance authority, contract, relocation
resolution, and scoped state fields. Consumers must not silently interpret a version 1 payload as
version 2. A Pipeline may apply an explicit read-only adapter and identify the
source version; old hash-bound plans must be regenerated before mutation.

The fingerprint covers reported path metadata and detects ordinary workspace
drift. It deliberately does not read or hash file contents and is not a
security signature. Use version-control revisions, signed manifests, or
content hashes under an approved data-handling policy when hostile tampering or
strong evidence integrity is in scope.

## Non-contractual interpretation

The inventory cannot determine scientific meaning from names. It cannot decide
whether a dataset is authoritative, an intermediate is reproducible, a run is
final, or a file is safe to delete. Those decisions remain part of the
governance workflow and require repository evidence and owner authority.
