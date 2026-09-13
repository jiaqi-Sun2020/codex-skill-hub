# Codex bootstrap audit contract

Audit the project-local mechanism that explicitly loads the canonical bundle
instructions. Do not maintain a second loader template here.

## Expected surfaces

- `.codex/config.toml` enables `features.hooks`.
- `.codex/hooks.json` invokes `load_project_agents.py` for `SessionStart` and
  `SubagentStart`.
- The session matcher covers `startup`, `resume`, `clear`, and `compact`.
- `.codex/hooks/load_project_agents.py` carries
  `project-agent-bootstrap/v1`.
- `.agents/AGENTS.md` is a regular UTF-8 file between 1 byte and 12 KiB.
- `.agents/scripts/start-codex.ps1` is the optional terminal launcher.

## Strict root-README layout

With `--strict-root-readme`:

- root ordinary files are exactly `README.md`;
- root `AGENTS.md` is a duplicate-entrypoint finding;
- `00-overview/` is a duplicate-overview finding.

Do not delete any conflict during an audit.

## Repair ownership

Use `project-agent-generator-skill` for an explicitly authorized repair. It owns
the Hook, loader, launcher, and safe config merge. Rerun `bootstrap-audit` after
repair. Never edit user-level Codex configuration or another project.
