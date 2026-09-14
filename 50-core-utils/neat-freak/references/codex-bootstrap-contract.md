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

## Mandatory-policy topology

When `--policy-topology` is supplied, independently read the project-contained
`research-policy-topology/v1` declaration. Discover nested execution roots from
their `.agents/AGENTS.md` or legacy `.agent/AGENTS.md`, without following links
or junctions, and verify:

- every mandatory policy path exists inside the project and matches its hash;
- every applicable execution root has one declared binding;
- explicit bindings contain the canonical relative reference, declare
  `non_weakening=true`, and have a reviewed semantic assertion;
- nested explicit bindings have a managed local bootstrap;
- verified loaders have immutable loader and passing-verification evidence;
- isolation has an owner, date, and rationale;
- policy bodies listed in `known_copies` are compared and divergent copies are
  unsafe; matching filenames alone are not treated as proof of policy identity;
- mandatory policy is not available only through optional memory.

Path and hash checks cannot prove semantic non-weakening. Keep an unreviewed
natural-language relationship as a finding instead of reporting it clean.

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
