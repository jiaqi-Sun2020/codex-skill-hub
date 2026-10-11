# Initialization contract

## Scope and authority

The helper writes only `00_research_logic/intake.md`, `pipeline_context.md`, a
missing parent for the former and owned temporary siblings. No config, Agent,
memory, Hook or scientific output. Intake holds the goal only without a formal
approved contract; otherwise it references that contract. Context is navigation,
not another current state. `--intake-ref` reuses an existing equivalent entry.
References must be project-contained; discovery certifies neither truth nor approval.

Preview: what to create/reference, why, evidence to review, pass/reject criteria,
what passing permits, and the cheapest correction. Reject ambiguous authority,
paths, source precedence or next action. Fix the blocker, not the whole paper.
Entry completion can coexist with insufficient research material.

## Immutable packet and apply

`paper-project-initialization/v1` binds input version, normalized root, root/parent
identity, explicit inputs, rule/source snapshots, initializer/template/protocol
SHA-256, two target preconditions and complete UTF-8 content Base64, length and
SHA-256, stage, next action and scope. Time/randomness do not affect its digest.
Existing entries have reference actions and byte/identity preconditions, not a
template-matching requirement. Preserve their BOM, encoding and line endings.
For `reference`, display the actual source path and `before` bytes/SHA/identity,
or the snapshot of the explicit equivalent entry. The v1 target content fields
remain deterministic candidate-template fields for compatibility; they are unused
for reference actions, not the existing document or an approved replacement goal.
Device/file IDs and nanosecond timestamps are decimal strings: Windows values
can exceed JavaScript's exact integer range. Preserve the original packet bytes;
do not reserialize older numeric-identity packets through lossy JSON tools.

From the hub root (packet/receipt saving needs authorization):

```powershell
python -X utf8 -B .\10-paper-build\paper-project-initializer\scripts\initialize_paper_project.py apply --plan "<approved-original-packet.json>" --confirm-plan-sha256 "<digest>" --authority-ref "<original-user-confirmation>"
python -X utf8 -B .\10-paper-build\paper-project-initializer\scripts\initialize_paper_project.py apply --plan "<same-packet.json>" --confirm-plan-sha256 "<same-digest>" --authority-ref "<still-valid-confirmation>" --receipt "<prior-receipt.json>"
```

Packet/receipt JSON is data, not authority. The agent verifies the original user
confirmation and scope. Digest binding is not a signature. The helper reconstructs
allowed content, refuses extra targets/unknown versions, executes no data-contained
command, and defaults to stdout. `--plan -` reads stdin. Exit 0 means scoped
inspection/preview or entry checks only; 2 means blocked/partial.
Both file-based plan and receipt inputs must be regular, bounded UTF-8 files
(optional BOM), at most 2 MiB. Reject linked/reparse ancestors, oversized files
before reading, and identity/content changes during a bounded read. An approved
external temporary path is allowed; approval does not make a link safe. No truncation.

## Single-file publication and resume

Write a short exclusive sibling with UTF-8 bytes, flush/fsync and verify identity,
length/hash. Recheck paths, parent and absent target. `os.link(temp, target)`
atomically creates a new final link; existing targets fail. No replace, overwrite
rename or check-then-write fallback. Clean only a proven owned same-content/
same-identity temporary file, never a final artifact.

Windows supports local NTFS on the same volume. Linux accepts known local
ext2/3/4, XFS, Btrfs, tmpfs or overlay mounts with standard hardlink semantics.
Unverified/network/FUSE filesystems are rejected. Successful calls do not prove
safety against all hostile races. Check lexical paths before resolving aliases,
then physical containment, including links/junction/reparse and ancestors.
Unsupported hardlinks, permissions or path limits stop; no system-setting changes.
This is single-file no-clobber, not a two-file/Generator transaction or whole-group
crash-durability promise.
The filesystem support gate applies only when a final file still needs publication.
Reference-only and already-completed checks require unchanged sources, paths and
identities, not hardlink support; they never create missing parents.

Receipts bind the plan, completed byte/identity snapshots and created parent
identity. After intake succeeds and context fails, reuse that plan and matching
receipt to fill only context. Original existing files must remain unchanged.
Only planned `create` targets may appear in `completed`; each must be a current
regular file with the approved length/SHA and exactly matching recorded identity.
Created-directory records may only explain an originally absent approved parent,
with matching current directory identity. Invalid progress blocks before any new
write and is not copied into the next receipt as verified completion.
Changed inputs/tools, unknown files, identity replacement or links stop and preserve
final files. Missing receipt after hard interruption leaves ownership unknown even
with matching bytes: obtain minimal confirmation and a new reviewed preview,
not deletion/recreation. Names/markers/content similarity do not prove ownership.
Receipts are not credentials. Chat alone cannot ensure cross-session recovery;
Before resume, locate the original tool output or a previously approved handoff
digest and check receipt provenance/integrity against it. A matching plan hash and
live snapshots alone cannot prove who created a file or authenticate approval.
Without that evidence, retain unknown ownership and request minimal confirmation
for a new reviewed preview; preserve existing files. The helper validates mechanics,
not the authenticity of user permission or receipt provenance.
explicitly save into an approved temporary location/existing handoff when needed.
Unknown/stale temporary files remain for owner review.

## Generator disclosure: verify current tool before use

Current Generator writes `hooks = true` to `.codex/config.toml` and merges
`.codex/hooks.json`: persistent enabling configuration, not a template.
Events: SessionStart startup/resume/clear/compact, SubagentStart. Timeout: 10 seconds.
Windows: `python -X utf8 -B ".codex\hooks\load_project_agents.py"`.
Linux: `python3 -X utf8 -B ".codex/hooks/load_project_agents.py"`.
Loader reads event stdin and `.agents/AGENTS.md`; stdout emits Hook context or
visible stop; currently no project writes/network calls. Disclose config, Loader,
`.agents/scripts/start-codex.ps1`, memory baseline and entry references individually,
including existing config changes. Launcher may start Codex; do not execute it.
Codex networking is not covered by Loader's no-network statement. Real loading
depends on client support/trust and needs separate verification. Memory-baseline
creation does not authorize arbitrary future memory writes.

Generator is independent, using its own public preview/approval. Ordinary dry-run
lists paths/facts, not per-file content hashes: no claim of the helper's content
binding/resume guarantee. Explicit manual/document-only choice can use existing
opt-outs; disabled Hook config is never overridden. Locate original confirmation,
project and actions; design preference/tool output cannot produce permission.
