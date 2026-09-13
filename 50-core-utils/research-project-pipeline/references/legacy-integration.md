# Legacy Project Integration

Integrate incrementally. Existing names are not defects when their roles and
boundaries are clear.

## Default strategy

1. Inventory without opening sensitive content or following links.
2. Map existing paths to governance roles before proposing new directories.
3. Preserve unknown and owner-authored paths.
4. Create only missing control records or boundaries that solve a demonstrated
   ambiguity.
5. Prefer adapters, manifests, and documented aliases over mass relocation.
6. Update code/config references only through an exact migration map and focused
   verification.
7. Keep old and new evidence identities distinct; do not relabel historical
   output as if it were produced under the new framework.

## Existing `.agents` or `.agent`

The pipeline treats either name as owner state and will not replace it. If both
exist, stop and establish which is canonical before maintenance. Read all
canonical files in the selected bundle, audit current loading and memory, then
choose one:

- preserve unchanged;
- manually update a small verified fact set;
- invoke `project-agent-generator-skill` independently with its dry-run,
  backed-up `--force` refresh, comparison, and validation workflow.

After a refresh, run `neat-freak` audit and compare `ARCHITECTURE.md`, config,
runbook, and decisions with the actual post-migration project.

## Compatibility gate

Before accepting integration, verify that established commands still run from
their documented directories, import/config paths resolve, source records and
formal outputs are unchanged unless approved, and existing external consumers
still find their artifacts. Keep a redirect or compatibility adapter only when
its owner and retirement condition are documented.
