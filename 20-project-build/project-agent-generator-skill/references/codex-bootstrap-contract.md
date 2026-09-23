# Codex bootstrap contract

Use this contract when the canonical project instructions stay below the project
root, normally at `.agents/AGENTS.md`.

## Managed surfaces

- Enable hooks in `<project>/.codex/config.toml` without replacing unrelated keys.
- Merge one managed `SessionStart` handler and one managed `SubagentStart` handler
  into `<project>/.codex/hooks.json`.
- Keep the loader at `.codex/hooks/load_project_agents.py`.
- Keep the optional PowerShell launcher at `<out-dir>/scripts/start-codex.ps1`.
- Never create or copy a root `AGENTS.md`.

## Loading behavior

- Run on `startup`, `resume`, `clear`, and `compact`.
- Resolve the project root from the loader's own verified location.
- Load only `<out-dir>/AGENTS.md`; let that file route task-relevant memory.
- Reject missing, empty, non-UTF-8, linked, junction-based, or over-12-KiB
  instruction files.
- Emit successful content as Hook `additionalContext`.
- Emit a visible stopped Hook result for invalid state; never silently continue
  as though project instructions were loaded.
- Add the same context for subagents.

## Configuration safety

- Require a trusted project for project-local config and hooks.
- Preserve existing TOML keys and unrelated JSON Hook events.
- Refuse an explicit `features.hooks = false`.
- Refuse to replace an unmarked loader or launcher. The retained `--force`
  behavior is break-glass legacy recovery, not routine maintenance.
- Back up changed existing project config under the generator backup directory.
- Do not modify user-level Codex config, Git hooks, or other projects.

## Legacy bootstrap-only completion

Use this mode only when exactly one safe `.agents` or `.agent` bundle already
exists and its `AGENTS.md` is non-empty.

- Preview all four managed targets before writing and bind the apply to the
  current manifest SHA-256.
- Create missing targets only. An exact existing managed file is unchanged; any
  differing existing target is a conflict, including config or Hook files that
  could otherwise be merged by full initial generation.
- Preserve all existing bundle documents and memory byte-for-byte.
- Reject `--force`, outside/project-root output exceptions, links, junctions, and
  a second competing Agent bundle.
- Rerun the loading audit after apply. Bootstrap completion does not establish
  knowledge freshness or governance readiness.

## Verification

1. Validate TOML and JSON syntax.
2. Invoke the loader with synthetic `SessionStart` and `SubagentStart` JSON.
3. Confirm the output names the correct event and contains the bundle heading.
4. Confirm a second ordinary generation refuses replacement without changing
   files and directs routine maintenance to Neat-Freak.
5. Confirm no root `AGENTS.md` or `00-overview/` was created.
6. For bootstrap-only, compare the existing bundle before and after byte-for-byte
   and confirm only the reviewed missing Bootstrap targets were created.
