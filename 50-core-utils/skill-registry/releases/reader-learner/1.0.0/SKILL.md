---
name: reader-learner
description: Manage the user's personal literature-reading and technical-news knowledge profile under `.agents/reader-learner/knowledge_profile.json`, export its disposable learner-profile view, and maintain a separate curated visible Obsidian wiki under `.agents/wiki/` with stable concepts, entities, themes, questions, claims, source summaries, and knowledge-boundary maps. Use when Codex needs to import reader HTML feedback, AI/quantum news briefing feedback, update known/learning/unknown/mastered concept statuses, interpret natural-language feedback, maintain reading-session history, sync the learner profile, compile/lint the visible wiki, or generate source-grounded explanations after using reader-skill, nature-reader, or ai-quantum-news-briefing.
---

# Reader Learner

## Purpose

Maintain the user's evolving knowledge boundary for literature reading and AI/quantum news. This skill owns the long-term profile under `.agents/reader-learner/knowledge_profile.json`; `reader-skill` and `ai-quantum-news-briefing` may read that profile or emit feedback, but profile mutation belongs here.

Use this skill after a reader HTML session, after the user marks concepts as known or unknown, or when the user says something like "ansatz I understand, TDCSE I do not".

The JSON profile remains the source of truth. Obsidian export is a generated visualization/review layer and may be overwritten on the next sync. The Obsidian vault should organize knowledge points first; raw feedback events are evidence history, not the main browsing surface.

HTML presentation belongs to the pipeline-specific HTML owners. For news feedback, keep profile statuses and source/category evidence precise; do not store presentation layout decisions in `knowledge_profile.json`.

The llm-wiki boundary is:

- raw feedback JSON / reader bundles / news configs are immutable evidence sources;
- `knowledge_profile.json` is the normalized learner state compiled from evidence;
- `obsidian-vault/` is a generated wiki view with `index.md`, `log.md`, concept pages, source pages, maps, and review queues;
- this skill owns profile mutation and wiki export; domain readers only export feedback.

## Files

Default profile:

```text
<project-root>/.agents/reader-learner/knowledge_profile.json
```

Legacy generated Obsidian export:

```text
<project-root>/.agents/reader-learner/obsidian-vault
```

Default human-facing Obsidian vault:

```text
<project-root>/.agents/wiki
```

Default local Obsidian app path for open scripts:

```text
D:\software\Obsidian\Obsidian.exe
```

Read `references/learner-profile-schema.md` before changing schema fields, migrating data, or explaining the memory model. The current schema is v2 and separates `concepts`, `events`, `sources`, and `review_queue`.

## Feedback Sources

Accept two feedback forms:

1. JSON exported from reader HTML:

```json
{
  "reader_feedback_version": 1,
  "paper_title": "...",
  "reader_path": "...",
  "items": [
    {
      "concept": "ansatz",
      "status": "learning",
      "note": "I know the general idea but not this quantum-circuit usage.",
      "user_question": "Why does this ansatz stay correlation-efficient in this paper?",
      "confusion_type": "paper_usage",
      "explanation_style": "paper_context",
      "needs_explanation": true,
      "block_id": "S011",
      "annotation_kind": "concept",
      "source_excerpt": "Nearby reader paragraph or selected text.",
      "selected_language": "original",
      "original_context": "English/source side when available.",
      "translation_context": "Chinese translation side when available."
    }
  ]
}
```

2. Normalized news feedback produced by `ai-quantum-news-briefing`:

```json
{
  "reader_feedback_version": 2,
  "source_kind": "news_briefing",
  "paper_title": "AI + Quantum News Briefing - 2026-07-04",
  "reader_path": "path/to/news_feedback.json",
  "items": [
    {
      "concept": "quantum error correction",
      "status": "unknown",
      "annotation_kind": "news_concept",
      "action": "news_feedback",
      "source_title": "Short source title",
      "source_url": "https://example.com/source",
      "category": "quantum computing",
      "source_excerpt": "Briefing context.",
      "user_question": "Why is decoding the bottleneck?"
    }
  ]
}
```

For news briefings, do not infer knowledge from exposure alone. Use `unrated` for exposure-only concepts and use `unknown`, `learning`, `known`, or `mastered` only from explicit user feedback.

3. Validated teaching feedback produced by `adaptive-teach`. This is a narrow handoff containing an existing stable concept ID, actual learner performance, prompt use, provenance, and an already-calculated review proposal. This skill validates, normalizes, backs up, atomically persists, and optionally projects it; it does not rank topics or generate teaching plans.

3. Natural-language feedback from the user:

```text
ansatz: known; TDCSE: unknown; 1-RDM: learning, needs examples.
```

For natural language, map to statuses conservatively:

- Chinese feedback meaning "I know it" -> `known`
- Chinese feedback meaning "I can explain/apply it" -> `mastered`
- Chinese feedback meaning "partly understand" or "need examples" -> `learning`
- Chinese feedback meaning "do not understand" or "need explanation" -> `unknown`

Ask a short clarification only when one concept maps to conflicting statuses.

## Commands

List current profile:

```bash
python <skill-dir>/scripts/update_learner_profile.py --profile <profile> list
```

Mark one concept:

```bash
python <skill-dir>/scripts/update_learner_profile.py --profile <profile> mark --concept "ansatz" --status learning --note "Needs circuit examples"
```

Import JSON feedback exported by reader HTML:

```bash
python <skill-dir>/scripts/import_reader_feedback.py --profile <profile> --feedback <feedback.json>
```

Import JSON feedback and immediately sync Obsidian:

```bash
python <skill-dir>/scripts/import_reader_feedback.py --profile <profile> --feedback <feedback.json> --sync-obsidian
```

Rebuild the whole learner profile/wiki from raw feedback roots:

```bash
python <skill-dir>/scripts/rebuild_knowledge_base.py --profile <profile> --feedback-root <project-root>/news --feedback-root <project-root>/2026/7 --normalized-dir <profile-dir>/imports/rebuild_YYYYMMDD --sync-obsidian --obsidian-clean --audit --fail-on-warning
```

Use rebuild when the user wants the knowledge base regenerated from original feedback files instead of incrementally updated. The rebuild path starts from an empty v2 profile, upgrades older reader/news feedback into strict reader-learner payloads with `concept_id`, `concept_type`, and `source_anchor`, imports them in deterministic path order, writes normalized feedback copies under `imports/`, syncs Obsidian, and runs the final audit.

Migrate a legacy profile to v2:

```bash
python <skill-dir>/scripts/migrate_knowledge_profile_v2.py --profile <profile>
```

List review queue:

```bash
python <skill-dir>/scripts/update_learner_profile.py --profile <profile> review
```

Import a validated adaptive teaching handoff and sync visible Wiki:

```bash
python <skill-dir>/scripts/feedback_visible_wiki_pipeline.py teaching-feedback --feedback <teaching_feedback.json>
```

Export the current profile to Obsidian without importing new feedback:

```bash
python <skill-dir>/scripts/update_learner_profile.py --profile <profile> obsidian
```

Export raw evidence/event notes only when an audit trail is needed:

```bash
python <skill-dir>/scripts/update_learner_profile.py --profile <profile> obsidian --include-events
```

Audit and optionally normalize the profile/wiki boundary:

```bash
python <skill-dir>/scripts/audit_knowledge_base.py --profile <profile>
python <skill-dir>/scripts/audit_knowledge_base.py --profile <profile> --normalize-profile
python <skill-dir>/scripts/audit_knowledge_base.py --profile <profile> --fail-on-warning
```

Use `--normalize-profile` when old profile data contains placeholder translations, illegal aliases, duplicate evidence, duplicate review items, or broken event/source references. It creates a backup and uses the same atomic JSON writer as feedback import.

Use a specific Obsidian app path or vault path:

```bash
python <skill-dir>/scripts/update_learner_profile.py --profile <profile> obsidian --vault <project-root>/.agents/reader-learner/obsidian-vault --obsidian-app D:\software\Obsidian\Obsidian.exe
```

Open the generated vault on Windows:

```powershell
powershell -ExecutionPolicy Bypass -File <project-root>\.agents\reader-learner\open_reader_learner_obsidian.ps1
```

If Obsidian shows `Vault not found`, it is usually because Obsidian was already running before the vault was registered. Fully close Obsidian and run:

```powershell
powershell -ExecutionPolicy Bypass -File <project-root>\.agents\reader-learner\restart_reader_learner_obsidian.ps1
```

Diagnose whether the official desktop CLI is usable:

```powershell
powershell -ExecutionPolicy Bypass -File <project-root>\.agents\reader-learner\diagnose_reader_learner_obsidian.ps1
```

If the vault is not visible in Obsidian's vault list, open it once with the script above, or in Obsidian choose **Open folder as vault** and select:

```text
<project-root>\.agents\reader-learner\obsidian-vault
```

## Update Rules

- Import feedback with strict schema validation before mutating the in-memory profile. Required concept feedback metadata includes `status`, `concept`, `concept_id`, `concept_type`, and `source_anchor`.
- Normalize concept names, aliases, notes, and source excerpts with HTML unescape, tag stripping, whitespace collapse, and PDF hyphen repair such as `Trans- former` -> `Transformer`.
- Fail fast on replacement characters, control characters, mojibake markers, HTML fragments, source/page-index fragments, section headings, overlong selected text, full sentences, and user freeform questions used as concept keys.
- Keep English and Chinese aliases separate in `aliases_en` and `aliases_zh`; keep legacy `aliases` only for compatibility.
- Write `knowledge_profile.json` with `encoding="utf-8"` and `ensure_ascii=False`; writes must be atomic and create a backup during feedback import.
- If validation fails, do not overwrite the existing profile.
- Keep `concepts` keys stable and canonical; do not use full selected text or full sentences as keys.
- Preserve raw user notes, selected text, source excerpts, original/translation context, and source paths in `events`, not in bloated concept fields.
- Preserve papers, reader bundles, and news sources in `sources`.
- Add `unknown` and `learning` feedback to `review_queue`.
- Preserve AI/quantum news feedback with `source_kind`, source title, source URL, category, action, and source excerpt when present.
- Default new concepts to `unrated`, not `unknown`.
- Change to `unknown` only when the user says they do not understand it or asks for explanation.
- Do not downgrade `known` or `mastered` overall status based only on a hard paper. Update the specific `facet_status` and review queue instead.
- For `unknown` and `learning` concepts, add a concise `ai_explanation` when the source reader gives enough context.
- Record `source`, `block_id`, and timestamp whenever available.
- After importing feedback or manually updating important concepts, sync Obsidian when the user wants a browsable vault. Treat generated Markdown notes as derived output; do not manually edit the JSON from Obsidian notes.

## Obsidian Export Rules

- Export from `knowledge_profile.json` to `<profile-dir>/obsidian-vault` unless the user gives `--vault`.
- Generate notes for `Concepts`, `Sources`, `Reviews`, `Maps`, `Wiki`, `_meta`, `Templates`, and `wiki-export`.
- Treat `Concepts` as the knowledge-point layer. Preserve raw feedback history in `knowledge_profile.json.events`, but do not generate first-class event notes by default.
- Preserve backlinks between knowledge points, sources, and the review queue using Obsidian wiki links.
- Follow a wiki-style pattern inspired by Obsidian knowledge-base workflows: generate `index.md`, `hot.md`, `log.md`, YAML frontmatter summaries, controlled tags, `relationships`, provenance-ish source links, and stable MOC pages.
- Generate `01 Learning Dashboard.md` as the main entry after `00 Home.md`; include status/facet maps, review queue, embedded knowledge-point Bases, and links to visual maps.
- Generate `Wiki/Knowledge Points.md` as the primary organized table, status MOCs under `Wiki/Status/`, facet MOCs under `Wiki/Facets/`, and a bilingual-ish `Wiki/Glossary.md` from concept labels/translations.
- Generate native Obsidian Bases under `_meta/*.base` for knowledge points and review items. Obsidian 1.8+ supports Bases natively; Dataview is not required.
- If the user explicitly asks for raw feedback history, pass `--include-events` or `--obsidian-include-events`; this additionally generates `Evidence/*.md`, `_meta/evidence.base`, and evidence nodes in graph export.
- Generate `Maps/Knowledge Graph.canvas` and `Maps/Concept Relations.md` as low-clutter core-boundary maps, not generic relation graphs. The maps must foreground known anchors, active unknown gaps, unrated probes, domains, and facet blockers, while moving detailed concept lists into tables instead of dense graph edges.
- Generate `.obsidian/graph.json` color groups from `status/*` tags, plus a CSS snippet under `.obsidian/snippets/reader-learner.css`.
- Generate `wiki-export/reader-learner-graph.json` and `wiki-export/reader-learner-graph.html` as a portable core-boundary graph. Omit source nodes by default so paper/source hubs do not obscure the user's knowledge boundary; include source/evidence nodes only in explicit audit mode.
- Generate `.obsidian` settings and `open_reader_learner_obsidian.ps1` / `.cmd` beside the profile.
- Register the vault in `%APPDATA%\Obsidian\obsidian.json` only when the user explicitly runs the open/restart script, and launch Obsidian directly to avoid launcher errors.
- Generate `restart_reader_learner_obsidian.ps1` for the case where an already-running Obsidian process has not reloaded the newly registered vault.
- Generate `diagnose_reader_learner_obsidian.ps1` to probe the official desktop CLI (`Obsidian.com version` and `Obsidian.com vaults`) in the style recommended by `codex-obsidian`.
- Do not launch Obsidian unless the user explicitly asks. Creating the vault and open scripts is enough.
- Use `--clean` only to remove files from the previous managed export manifest; never delete unrelated vault files.
- Do not manually edit generated Obsidian notes as the long-term memory source. If the user's knowledge boundary changes, update/import into `knowledge_profile.json`, then regenerate the vault.
- The generated `log.md` must use parseable llm-wiki headings such as `## [timestamp] export | Obsidian vault`.
- Run `audit_knowledge_base.py --fail-on-warning` after profile cleanup or vault export before reporting the knowledge base as healthy.

## Persistent Visible Wiki

Use `<project-root>/.agents/wiki/` as the human-facing Obsidian vault. It is separate from the disposable profile export at `.agents/reader-learner/obsidian-vault`.

- Read `references/visible-wiki-schema.md` before adding or revising a public wiki page.
- Keep public pages limited to stable concepts, entities, themes, normalized questions, syntheses, claims, and concise source summaries.
- Keep raw feedback, events, source excerpts, reader bundles, source paths, pipeline logs, and scheduling internals outside the visible wiki.
- Never project `freeform-annotation-*` or unresolved `concept-*` records into `.agents/wiki/concepts/`.
- Do not infer `known` or `mastered` from exposure. The projection copies only explicit profile status.
- Preserve curated explanatory text. `compile_visible_wiki.py` may replace only its `PROFILE PROJECTION` block and generated Home/index/map pages.
- Use `feedback_visible_wiki_pipeline.py sync` to create missing concise public pages for every stable profile concept and every profile source. It does not create a page from raw event text.
- Use `maps/Profile Coverage.md` plus `--require-profile-coverage` to verify that all stable profile records are visible while raw annotations, events, and scheduling remain in the source layer.

Run from the project root:

```powershell
python .\skills\reader-learner\scripts\feedback_visible_wiki_pipeline.py sync --dry-run
python .\skills\reader-learner\scripts\feedback_visible_wiki_pipeline.py sync
python .\skills\reader-learner\scripts\feedback_visible_wiki_pipeline.py reader-feedback --feedback <reader_feedback.json>
python .\skills\reader-learner\scripts\feedback_visible_wiki_pipeline.py news-feedback --feedback <news_feedback.json>
python .\skills\reader-learner\scripts\lint_visible_wiki.py --profile .\.agents\reader-learner\knowledge_profile.json --wiki .\.agents\wiki --strict --require-profile-coverage
```

The first command is a dry-run. The pipeline never mutates the profile during `sync`; feedback commands first use the strict profile importer with its backup behavior and only project the visible wiki after a successful import. Use `--no-bootstrap` only for a deliberately partial curation pass.

## Explanation Rules

When explaining unclear concepts:

- Ground the explanation in the current paper's `paper.md` and `source_map.json` when available.
- Give a short first-principles explanation first, then connect it to the paper's usage.
- Mention the source block ID, for example `p.2 S016`, if available.
- Keep the explanation matched to the user's current status.

## Relationship To Reader Skill

Use `reader-skill` to generate the HTML and collect click feedback. Use this skill to import that feedback, update `.agents`, and produce the next round of explanations.
