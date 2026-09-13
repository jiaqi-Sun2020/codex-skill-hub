# Learner Profile Schema v2

Use this reference when updating `.agents/reader-learner/knowledge_profile.json`, importing reader/news feedback, or explaining the memory model.

## Location

Default path:

```text
<project-root>/.agents/reader-learner/knowledge_profile.json
```

Use the existing `.agents` directory. Do not create both `.agent` and `.agents`.

Generated Obsidian vault path:

```text
<project-root>/.agents/reader-learner/obsidian-vault
```

The Obsidian vault is derived output. `knowledge_profile.json` remains the source of truth. The vault is knowledge-point-centered by default; raw `events` are compact evidence signals unless explicitly exported as detail notes.

## Design Goal

The profile is split into four surfaces:

- `concepts`: stable personal knowledge boundary by canonical concept ID.
- `events`: raw historical feedback/annotations/questions.
- `sources`: deduplicated source index for papers, reader bundles, and news briefings.
- `review_queue`: scheduling layer for concepts/facets that need review.

Do not use long selected text, full Chinese sentences, or paragraph excerpts as concept keys. Preserve that material in `events`.

## Top-Level Shape

```json
{
  "version": 2,
  "updated_at": "2026-07-04T00:00:00+00:00",
  "description": "Personal knowledge boundary for literature reading and AI/quantum news.",
  "status_scale": {},
  "concepts": {},
  "events": [],
  "sources": {},
  "review_queue": [],
  "reading_sessions": [],
  "migrations": []
}
```

## Concept Shape

Concept keys are stable IDs such as `ansatz`, `tdcse`, `ctqwformer`, `hamiltonian-simulation`, or `two-electron-hamiltonian-representation`.

```json
{
  "concept_id": "tdcse",
  "label": "TDCSE",
  "aliases": ["time-dependent contracted Schrödinger equation (TDCSE)"],
  "translation": "含时收缩薛定谔方程",
  "status": "learning",
  "confidence": 0.0,
  "facet_status": {
    "definition": "known",
    "paper_usage": "learning",
    "math_derivation": "unknown",
    "algorithm_step": "unrated",
    "assumption": "unrated",
    "evidence_interpretation": "unrated",
    "relation": "learning",
    "english_term": "known",
    "physical_intuition": "learning"
  },
  "learning_needs": ["math_step", "paper_usage"],
  "preferred_explanation_styles": ["first_principles"],
  "ai_explanation": "",
  "user_note": "Latest question: ...",
  "summary": "",
  "stats": {
    "seen": 3,
    "feedback_events": 3,
    "questions": 1,
    "unknown_marks": 1,
    "learning_marks": 1,
    "known_marks": 0,
    "mastered_marks": 0
  },
  "source_ids": ["src-abc"],
  "event_ids": ["evt-abc"],
  "last_seen_at": "2026-07-04T00:00:00+00:00",
  "next_review_at": "2026-07-05T00:00:00+00:00",
  "review_priority": 90
}
```

## Event / Evidence Signal Shape

Events preserve raw history and can be large. In user-facing Obsidian output, call them evidence signals. This is where selected text, source excerpts, original/translation context, and user questions belong.

```json
{
  "event_id": "evt-abc",
  "timestamp": "2026-07-04T00:00:00+00:00",
  "source_id": "src-abc",
  "concept_id": "tdcse",
  "raw_concept": "将 TDCSE 的各项用 ...",
  "status": "unknown",
  "event_type": "reader_feedback",
  "action": "reader_feedback",
  "annotation_kind": "freeform",
  "difficulty_type": "math_step",
  "facet": "math_derivation",
  "explanation_style": "first_principles",
  "user_question": "Why does this contraction imply TDSE?",
  "note": "",
  "selected_text": "selected text",
  "selected_language": "translation",
  "source_excerpt": "nearby source context",
  "contexts": {
    "original": "English/source context",
    "translation": "Chinese translation context"
  },
  "block_id": "S009",
  "bilingual_block_id": "S009",
  "source_title": "",
  "source_url": "",
  "category": "",
  "needs_explanation": true
}
```

## Source Shape

```json
{
  "source_id": "src-abc",
  "source_kind": "reader_feedback|news_briefing|manual_update|legacy_profile",
  "title": "Paper or briefing title",
  "path": "reader directory, feedback path, or briefing path",
  "url": "news source URL when applicable",
  "date_range": "2026-07-02 to 2026-07-04",
  "first_seen_at": "2026-07-04T00:00:00+00:00",
  "last_seen_at": "2026-07-04T00:00:00+00:00",
  "event_ids": ["evt-abc"]
}
```

## Review Queue Shape

```json
{
  "concept_id": "tdcse",
  "label": "TDCSE",
  "facet": "math_derivation",
  "status": "unknown",
  "priority": 98,
  "reason": "math_step",
  "due_at": "2026-07-05T00:00:00+00:00",
  "last_event_id": "evt-abc",
  "source_ids": ["src-abc"],
  "updated_at": "2026-07-04T00:00:00+00:00"
}
```

## Status Rules

- `mastered`: user can explain and apply the concept without help.
- `known`: user understands it in ordinary context.
- `learning`: user partly understands and benefits from examples/reminders.
- `unknown`: user needs explanation before reading fluently.
- `unrated`: concept was seen but not judged.

Do not downgrade `known` or `mastered` overall status just because a hard paper creates a local question. Instead, mark the relevant `facet_status` and add a review item.

## Difficulty Facets

Map feedback question types to facets:

- `term_definition` -> `definition`
- `paper_usage` -> `paper_usage`
- `math_step` -> `math_derivation`
- `algorithm_step` -> `algorithm_step`
- `assumption` -> `assumption`
- `evidence` -> `evidence_interpretation`
- `relation` -> `relation`
- `english_term` -> `english_term`
- `physical_intuition` -> `physical_intuition`

## Update Discipline

- Keep concept keys short and canonical.
- Put raw selected text and excerpts in `events`, not in concept keys or `user_note`.
- Keep `user_note` short, usually the latest question/note only.
- Preserve source paths/URLs in `sources` and event references.
- Add or update `review_queue` for `unknown` and `learning` events.
- Use `migrate_knowledge_profile_v2.py` before manually reshaping old profiles.

## Obsidian Export Shape

`export_obsidian_vault.py` converts the profile into a knowledge-point-centered vault with generated Markdown notes:

```text
obsidian-vault/
  00 Home.md
  01 Learning Dashboard.md
  Concepts/
  Sources/
  Reviews/Review Queue.md
  Wiki/Knowledge Points.md
  Wiki/Status/
  Wiki/Facets/
  Maps/Knowledge Boundary.md
  Maps/Knowledge Graph.canvas
  Maps/Sources Index.md
  _meta/concepts.base
  _meta/review-queue.base
  .obsidian/
```

Export rules:

- Generate concept notes from `concepts`; treat these as the primary knowledge-point pages.
- Do not generate event/evidence detail notes by default. Instead, summarize recent evidence signals inside the relevant concept and source notes.
- Generate evidence detail notes only when the user asks for auditability and the command uses `--include-events` or `--obsidian-include-events`; those notes are written under `Evidence/` and `_meta/evidence.base`.
- Generate source notes from `sources`.
- Generate review and boundary maps from `review_queue` and concept statuses.
- Use Obsidian wiki links so knowledge points and sources form the default graph.
- Treat all generated notes as disposable derived output; edit the profile through `reader-learner` commands, then export again.

## Audit / Lint Shape

The reader-learner knowledge base follows the llm-wiki pattern:

- raw feedback files and reader bundles are evidence;
- `knowledge_profile.json` is normalized compiled state;
- `obsidian-vault/` is a generated wiki view;
- skill docs and `.agents/*.md` are the schema/runbook layer.

Run:

```bash
python skills/reader-learner/scripts/audit_knowledge_base.py --profile .agents/reader-learner/knowledge_profile.json --fail-on-warning
```

The audit checks profile schema, concept labels, statuses, placeholder translations, dirty aliases, event/source references, review queue references, required vault files, `index.md` wiki links, parseable `log.md` entries, managed export manifest, and concept-note coverage.

Use:

```bash
python skills/reader-learner/scripts/audit_knowledge_base.py --profile .agents/reader-learner/knowledge_profile.json --normalize-profile
```

only for deterministic cleanup: known translation placeholders, illegal aliases, duplicate events, broken concept/source/event references, and duplicate review queue items. It must create a backup and atomically rewrite JSON.

For a full llm-wiki rebuild from raw feedback evidence, run:

```bash
python skills/reader-learner/scripts/rebuild_knowledge_base.py --profile .agents/reader-learner/knowledge_profile.json --feedback-root news --feedback-root 2026/7 --normalized-dir .agents/reader-learner/imports/rebuild_YYYYMMDD --sync-obsidian --obsidian-clean --audit --fail-on-warning
```

The rebuild command starts from `empty_profile_v2()`, upgrades older feedback shapes into strict v2 reader-feedback payloads, writes those normalized payloads as a persistent intermediate layer, imports them deterministically, regenerates `obsidian-vault/`, and writes both rebuild and audit reports.
