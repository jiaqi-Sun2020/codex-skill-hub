# Project knowledge discovery and platform coexistence

## Project-local store

The default store is `<project-root>/.agents/memory/`, with
`<project-root>/.agents/memory/MEMORY.md` as its index. A single legacy
`<project-root>/memory/` store remains usable in place. This is a user-managed
project knowledge base, not evidence that any platform-native memory feature is
enabled.

Resolve both the project root and knowledge path before writing. Reject:

- absolute memory overrides;
- `..` path traversal;
- symbolic links, Windows junctions, and reparse points;
- a resolved path equal to or outside the project root;
- a second store when another project knowledge index already exists.

## Project-local entrypoint

This architecture deliberately keeps the only managed entrypoint at
`.agents/AGENTS.md`. The project workflow must load it explicitly; Neat-Freak
does not create or modify a root `AGENTS.md`.

The preferred Codex workflow is a trusted project-local `.codex/` layer with a
`SessionStart` and `SubagentStart` Hook. The Hook injects `.agents/AGENTS.md` as
developer context. Audit it with `bootstrap-audit`; repair it through the
project-agent generator so Neat-Freak does not carry a divergent loader template.

When project knowledge is enabled (the project-agent generator enables it by
default):

1. preserve `.agents/AGENTS.md`;
2. create or replace only its marked `project-knowledge` block;
3. direct the agent to read `.agents/memory/MEMORY.md` for the default layout;
4. direct the agent to open only task-relevant topics;
5. keep knowledge advisory and subordinate to current code, tests, artifacts, and
   user instructions.

Do not modify root or global rule files. Do not create a Claude `CLAUDE.md`
pointer unless the user separately requests it.

## Native memory separation

Do not inspect or require:

- `~/.codex/memories/`;
- Codex `features.memories`;
- Claude `/memory`;
- Claude `autoMemoryDirectory`;
- `.claude/settings*.json`;
- global conversation-retention settings.

Those mechanisms may coexist, but they are outside this project knowledge workflow.

## Legacy compatibility

- Preserve `.agent/`, `.agents/`, independent `AGENTS.md` and `CLAUDE.md`, untyped
  topics, unknown Markdown files, and `archive/`.
- Do not infer that a legacy folder should be migrated merely from its name.
- If multiple plausible indexes exist, stop writes and report their exact
  project-relative locations.
- Never force symlinks or copies between platform-specific rule files.
