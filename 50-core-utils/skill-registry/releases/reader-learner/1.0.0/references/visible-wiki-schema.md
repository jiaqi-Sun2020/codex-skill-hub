# Visible Wiki Schema

Use this schema for the persistent human-facing wiki at `<project-root>/.agents/wiki/`.

## Boundary

- Keep `knowledge_profile.json` as the learner-state source of truth.
- Keep PDFs, bundles, raw feedback, events, logs, and pipeline data outside `.agents/wiki/`.
- Keep the legacy generated vault under `.agents/reader-learner/obsidian-vault` unchanged.
- Use `feedback_visible_wiki_pipeline.py sync` to bootstrap concise pages for stable profile concepts and source summaries, then update managed blocks and navigation pages. It must never create a concept from raw event text, freeform annotation, or opaque candidate.

## Required Frontmatter

```yaml
---
id: concept.stable-id
type: concept
title: Example concept
aliases: []
status: active
knowledge_status: unrated
visibility: public-wiki
source_refs: []
profile_source_refs: []
relations: []
updated: 2026-07-13
---
```

Use JSON-style lists for `aliases`, `source_refs`, `profile_source_refs`, and `relations`; JSON is valid YAML and keeps the built-in validator dependency-free.

- `source_refs` contains stable IDs of public `source` pages, so Graph View and the Evidence Map can follow visible provenance.
- `profile_source_refs` contains internal profile source IDs such as `src-...`. It is used only to match a public source summary to the immutable learner profile and is never rendered as a raw path or payload.

## Page Types

- `concept`: a canonical, reusable technical idea tied to a stable profile concept ID.
- `entity`: a named organization, platform, method, person, model, or paper object.
- `theme`: a durable research cluster.
- `question`: a normalized, explicit, source-traceable user question.
- `synthesis`: a maintained cross-page conclusion.
- `claim`: a concise source-grounded proposition with `claim_status` of `supported`, `contested`, or `open`.
- `source`: a concise citation/provenance summary, never a raw source dump.

## Relations

Allow only `prerequisite`, `supports`, `contradicts`, `extends`, `example-of`, `evidence-for`, and `about`.

Each relation must have a target stable ID in frontmatter and a matching visible wikilink in `## Relations`. Graph View only shows real internal links.

## Knowledge Boundary

- Copy `mastered`, `known`, `learning`, `unknown`, and `unrated` exactly from the profile.
- Do not infer a rating from exposure, reading, a source mention, or a page visit.
- Do not project `freeform-annotation-*` or unresolved `concept-*` IDs as public concept pages.
- Show `unrated` as contact/probe material, not as a default global-graph node.

## Full Profile Projection

- Project every stable profile concept to exactly one public concept page.
- Project every profile source to exactly one concise public source summary.
- Retain `freeform-annotation-*`, unresolved `concept-*`, raw events, review scheduling, and reading-session records in the profile/source layer. Count them in `maps/Profile Coverage.md`; do not make them Graph View nodes.

## Evidence

Claims must cite a source summary plus a bounded anchor such as `p.1 S004`. Keep full excerpts, selected text, chat turns, and event records in the profile/source layer.

## Workflow

Run from the project root:

```powershell
python .\skills\reader-learner\scripts\feedback_visible_wiki_pipeline.py sync --dry-run
python .\skills\reader-learner\scripts\feedback_visible_wiki_pipeline.py sync
python .\skills\reader-learner\scripts\feedback_visible_wiki_pipeline.py reader-feedback --feedback <reader_feedback.json>
python .\skills\reader-learner\scripts\feedback_visible_wiki_pipeline.py news-feedback --feedback <news_feedback.json>
python .\skills\reader-learner\scripts\lint_visible_wiki.py --profile .\.agents\reader-learner\knowledge_profile.json --wiki .\.agents\wiki --strict --require-profile-coverage
```

The first command previews a full stable projection without writing. The feedback commands preserve importer validation and profile backup behavior before running the applied projection.
