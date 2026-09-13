# Evidence-to-Document Routing

Use the smallest set of surfaces that keeps each audience correct. Do not force every
change into every document.

## Placement

| Information | Canonical destination |
|---|---|
| Deterministic safety/permission enforcement | Recommend settings, permissions, or hooks; modify only with approval |
| Bundle-local instructions required at every Codex start | Project-local `.codex` SessionStart/SubagentStart bootstrap |
| Rule every project session must follow | Platform-loaded project rule file |
| Project purpose and stable architecture | README or architecture docs |
| Verified setup, test, operations, recovery | Runbook |
| Public API/SDK/integration behavior | Integration guide/reference |
| Durable design decision and rationale | Decision record |
| Dated release history | Changelog or Git history |
| Task-relevant fact/lesson needed only sometimes | Project-local knowledge topic |
| Current task progress/handoff | One scoped handoff topic or project handoff doc |

Do not duplicate cheaply recoverable Git/code/config facts in memory. Do not copy long
documentation into a project rule file.

If the owner declares the root README to be the sole human-facing overview, keep
inventory and stable architecture sections there. Treat `.agents/README.md` as an
Agent-context index and remove a redundant `00-overview/` only after explicit
deletion authorization and reference repair.

## Change Impact

| Verified change | Usually inspect/update |
|---|---|
| API or route | integration reference; architecture only if flow/boundary changed |
| Environment variable | runbook/config reference; integration guide if consumers set it |
| Data model | architecture/data reference |
| User workflow | README or user guide; runbook if operational |
| Deployment/recovery | runbook |
| Shared protocol/SDK | both sides' integration docs, but write downstream only with authorization |
| Feature retirement/rename | active docs and rules; deletion requires approval |
| Durable constraint | project rule file, kept short |
| Session-only progress | handoff/memory, not permanent rules |

## Memory Reconciliation

| Finding | Action |
|---|---|
| Duplicate topic | update/merge the canonical topic; delete duplicate only with authorization |
| Contradicted conclusion | replace the disproven canonical statement using current evidence |
| Completed temporary task | remove from active handoff when deletion/edit scope permits |
| Stable mechanism already in docs | keep at most an index pointer; do not copy prose |
| Relative date | replace with an absolute date when the date matters |
| Unused topic | report as a candidate; do not delete automatically |
| Suspected secret | report class and location without value; stop before further writes |

## Rule-File Compatibility

- Do not require CLAUDE/AGENTS symlinks.
- Do not create a missing platform rule file unless automatic loading is a confirmed
  requirement and the user authorized it.
- Do not modify global rules during a project sync.
- Do not treat `.agents/AGENTS.md` as automatically loaded by Codex.
- Audit `.codex/config.toml`, `.codex/hooks.json`, the managed loader, and the
  canonical bundle file before claiming automatic loading works.
- Keep Hook repair owned by the project-agent generator; Neat-Freak independently
  verifies the resulting contract.
- Preserve project-specific platform differences.

## Verification

After an authorized sync:

1. inspect the final diff;
2. verify referenced paths and commands;
3. validate edited JSON/YAML;
4. confirm no suspected secret value was introduced;
5. confirm no unrelated file changed;
6. report every change and unresolved conflict;
7. when memory is in scope, always report `MEMORY.md` lines and bytes, not only near the limit.
8. run the deterministic auditor and honor its nonzero exit status.
9. verify that no removed overview path remains referenced and that the canonical
   root README links resolve.
10. when automatic loading is in scope, run `bootstrap-audit` and require a clean
    result before claiming `.agents/AGENTS.md` loads automatically.
