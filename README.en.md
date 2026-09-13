# Codex Skill Hub

[中文](README.md) | [English](README.en.md)

`codex-skill-hub` is a central source, navigation, and version-governance repository for Codex Skills and compatible agents. It directly maintains reusable research utilities, an academic-figure workflow, and a personal teaching Skill, while providing a unified catalog for independently maintained [S Paper Skills](https://github.com/jiaqi-Sun2020/S_paper_skills) and [PaperTrace](https://github.com/jiaqi-Sun2020/PaperTrace).

As of 2026-09-13, the catalog contains **25 active Skills**: 8 maintained directly in this repository, 8 in S Paper Skills, and 9 in PaperTrace. `skill-registry` is version-governance infrastructure and is not counted as a Skill.

> This public repository contains reusable instructions, scripts, tests, templates, and documentation. Manuscripts, experimental data, learner profiles, conversation records, credentials, and machine-local state are not public artifacts.

## Quick start

```powershell
git clone https://github.com/jiaqi-Sun2020/codex-skill-hub.git
cd codex-skill-hub
```

For a directly maintained Skill, give Codex the corresponding `SKILL.md` path or install that Skill directory into your Skill search path. Obtain project-owned S Paper Skills and PaperTrace Skills from their own repositories instead of copying them here.

## Repository layout

```text
codex-skill-hub/
|-- README.md / README.en.md
|-- .agents/                         Agent context and durable knowledge entrypoint
|-- .codex/                          Project-scoped Codex startup hook
|-- 10-paper-build/
|   `-- academic-figure-workflow/    Canonical academic-figure source
|-- 50-core-utils/
|   |-- project-agent-generator-skill/
|   |-- research-project-pipeline/
|   |-- research-workspace-governance/
|   |-- skill-audit-refactor/
|   |-- training-code-architecture-skill/
|   |-- neat-freak/
|   `-- skill-registry/              Integrated shared-version registry
`-- 90-personal/
    `-- logic-chain-tutor/
```

## Skill selection guide

| Goal | Primary Skill |
|---|---|
| Determine whether an idea has a mechanism-level contribution | `research-logic` |
| Convert an idea into a reviewer-ready experiment plan | `experiment-design` |
| Analyze experimental results and statistical evidence | `data-analysis` |
| Build, restructure, or deliver a LaTeX manuscript | `latex-paper-build-skill` |
| Create paper figures, architecture diagrams, or multi-panel plots | `academic-figure-workflow` |
| Generate project-local Agent context | `project-agent-generator-skill` |
| Govern a complete research workspace | `research-workspace-governance` |
| Audit or simplify an existing Skill | `skill-audit-refactor` |
| Read a paper and build a bilingual reader | `nature-reader` → `reader-skill` |
| Maintain a personal reading-knowledge profile | `reader-learner` |
| Learn an unfamiliar concept from the current point of confusion | `logic-chain-tutor` |

## Paper and research-building Skills (9)

Eight Skills are maintained in [S Paper Skills](https://github.com/jiaqi-Sun2020/S_paper_skills); the canonical `academic-figure-workflow` source lives in this repository.

### `research-logic`

- **Domain:** Method integration, mechanism analysis, contribution diagnosis, and disciplined paper claims.
- **Output:** Shallow-stacking diagnosis, mechanism-level connections, state/transition logic, and testable claims.
- **Examples:** “Determine whether CTQW and a dynamic graph network form a mechanism-level contribution.”; “Rewrite this contribution claim with explicit evidence boundaries.”
- **Source:** `S_paper_skills/research-logic-skill/`.

### `experiment-design`

- **Domain:** Experimental design for machine learning, graph learning, physics-inspired models, and method papers.
- **Output:** Research questions, hypotheses, datasets, baselines, ablations, metrics, mechanism checks, and failure cases.
- **Examples:** “Design an experiment matrix that tests the model's three central claims.”; “Add baselines, ablations, and statistical tests until this plan is reviewer-ready.”
- **Source:** `S_paper_skills/experiment-design-skill/`.

### `data-analysis`

- **Domain:** Statistical analysis of CSV/JSON/NPZ files, training logs, repeated experiments, and paper results.
- **Output:** Integrity checks, significance tests, effect sizes, confidence intervals, and report-ready interpretation.
- **Examples:** “Compare five models across seeds with means, 95% confidence intervals, and effect sizes.”; “Check whether the available evidence supports the claimed performance gain.”
- **Source:** `S_paper_skills/data-analsys-skill/`; the historical directory spelling is preserved for compatibility.

### `research-html-report`

- **Domain:** Research briefs, paper-planning pages, mechanism explanations, and printable academic HTML.
- **Output:** Standalone reports with figures, tables, equations, citations, and explicit risk boundaries.
- **Examples:** “Turn the research logic and experiment plan into a shareable HTML brief.”; “Build a paper-style page with equations, ablation tables, and explanations for every figure.”
- **Source:** `S_paper_skills/util_skills/research-html-report/`.

### `latex-paper-build-skill`

- **Domain:** LaTeX project scaffolding, monolith splitting, REVTeX/ctex, BibTeX, and submission checks.
- **Output:** Compilable manuscript structure, unified `figures/` and `.bib` management, build instructions, and delivery audits.
- **Examples:** “Split this monolithic `main.tex` into maintainable sections without changing labels.”; “Create a REVTeX project for this QCT paper and audit figures, citations, and compilation.”
- **Source:** `S_paper_skills/latex-paper-build-skill/`.

### `paper-polishing-skill`

- **Domain:** Post-approval translation, Nature/PRL/PRA polishing, and argument-structure revision.
- **Output:** English manuscript text or revision notes that preserve equations, labels, citations, facts, and claim boundaries.
- **Examples:** “Translate this approved Chinese results section into PRL-style English without changing the claims.”; “Audit repeated values against the canonical table and tighten the introduction.”
- **Boundary:** Do not produce a final English manuscript before the author approves the scientific content.
- **Source:** `S_paper_skills/paper-polishing-skill/`.

### `interactive-skill-builder`

- **Domain:** Converting a repeated workflow into a Codex Skill through an interview-first process.
- **Output:** An approved Skill specification, resource plan, implementation, and validation record.
- **Examples:** “Interview me to turn my experiment-retrospective workflow into a Skill.”; “Audit the triggers and output contract before updating this existing Skill.”
- **Source:** `S_paper_skills/util_skills/interactive-skill-builder/`.

### `prl-manuscript-polisher`

- **Domain:** Physical Review Letters fit, compression, evidence audit, and REVTeX consistency.
- **Output:** PRL-fit audit, section revisions, word budget, claim-evidence checks, and a submission checklist.
- **Examples:** “Audit whether this manuscript fits PRL and identify the three issues most likely to affect editorial screening.”; “Compress the abstract and introduction without changing the physics.”
- **Source:** `S_paper_skills/util_skills/prl-manuscript-polisher/`.

### `academic-figure-workflow`

- **Domain:** Academic mechanism diagrams, neural-network architecture figures, real-data plots, multi-panel assembly, and submission QA.
- **Output:** Editable SVG/Draw.io/PowerPoint sources, reproducible plots, captions, evidence traces, and final-size checks.
- **Examples:** “Create an editable neural-network architecture diagram from this model code and verify every edge.”; “Turn the experiment data into a Nature-style multi-panel figure with captions and final-size readability checks.”
- **Source:** [`10-paper-build/academic-figure-workflow/`](10-paper-build/academic-figure-workflow/).

## Central core utilities (6)

### `project-agent-generator-skill`

- **Domain:** Repository onboarding, Agent context, durable knowledge entrypoints, and project-scoped Codex startup loading.
- **Output:** `.agents/` documentation, an `AGENTS.md` entrypoint, memory index, and a safe project hook.
- **Examples:** “Inspect this repository and generate Agent context without changing business code.”; “Safely refresh the existing `.agents` bundle while preserving owner-confirmed knowledge.”
- **Source:** [`50-core-utils/project-agent-generator-skill/`](50-core-utils/project-agent-generator-skill/).

### `research-project-pipeline`

- **Domain:** End-to-end onboarding, migration, governance, and handoff for new or legacy research projects.
- **Output:** Read-only discovery, workspace design, reviewed migration, Agent context, knowledge audit, and adversarial acceptance.
- **Examples:** “Onboard this legacy research project: inventory first, then propose migration.”; “Create the complete pipeline from workspace governance to Agent handoff for a new study.”
- **Source:** [`50-core-utils/research-project-pipeline/`](50-core-utils/research-project-pipeline/).

### `research-workspace-governance`

- **Domain:** Research directory design, evidence lifecycle, provenance, archiving, and cleanup policy.
- **Output:** SOURCE/derived/intermediate/final/temporary boundaries, artifact inventories, and reproducibility rules.
- **Examples:** “Design a research directory that cannot confuse raw data with generated results.”; “Audit whether each experiment artifact traces back to configuration, code, and source data.”
- **Source:** [`50-core-utils/research-workspace-governance/`](50-core-utils/research-workspace-governance/).

### `skill-audit-refactor`

- **Domain:** Skill triggering, context cost, resource decomposition, and safety-boundary review.
- **Output:** Prioritized findings, simplification plan, split recommendations, and capability-preserving refactors.
- **Examples:** “Audit whether this Skill is too long, broad, or easy to trigger incorrectly.”; “Move conditional details into references without losing behavior.”
- **Source:** [`50-core-utils/skill-audit-refactor/`](50-core-utils/skill-audit-refactor/).

### `training-code-architecture`

- **Domain:** Reusable machine-learning training systems, configuration-driven experiments, and multi-task adaptation.
- **Output:** A thin `main.py → train(args)` entrypoint, factories, adapters, checkpoints, logs, and result contracts.
- **Examples:** “Refactor this training script into a configuration-driven reproducible architecture.”; “Preserve the training framework while supporting static and dynamic graph tasks through adapters.”
- **Source:** [`50-core-utils/training-code-architecture-skill/`](50-core-utils/training-code-architecture-skill/).

### `neat-freak`

- **Domain:** `.agents/memory/`, project documentation, knowledge deduplication, and Codex bootstrap audits.
- **Output:** Read-only audits, hash-bound update plans, reconciled knowledge, and bootstrap verification.
- **Examples:** “Check the MEMORY index, topic files, and project documentation for conflicts.”; “Create an auditable plan for this durable decision, then apply it explicitly.”
- **Source:** [`50-core-utils/neat-freak/`](50-core-utils/neat-freak/).

## PaperTrace Skills (9)

These Skills are maintained independently in [PaperTrace](https://github.com/jiaqi-Sun2020/PaperTrace/tree/main/skills) and registered as project-owned `forked` implementations.

### `adaptive-teach`

- **Domain:** Learner-profile-backed diagnosis, teaching, review, and transfer practice.
- **Output:** A one-topic learning decision, short lesson, diagnostic task, and validated teaching-feedback handoff.
- **Examples:** “Use my learner profile to choose the next concept I should repair.”; “Schedule a due review and judge mastery from actual performance evidence.”

### `ai-quantum-news-briefing`

- **Domain:** AI and quantum-technology papers, model releases, policy, research blogs, and industry news.
- **Output:** Source-grounded briefing, concept fable, interactive HTML, and feedback JSON.
- **Examples:** “Create a briefing on the most important AI and quantum-computing developments from the last three days.”; “Turn today's briefing into an interactive feedback-enabled HTML page.”

### `allegory-teach`

- **Domain:** Intuition-first explanation of one advanced technical concept through a Chinese fable.
- **Output:** A causal story with delayed concept reveal, definition, analogy limits, misconception warning, and mapping table.
- **Examples:** “Choose one concept near my research boundary and explain it through a fable without naming it first.”; “Explain quantum error correction as a story and state exactly where the analogy breaks.”
- **Boundary:** It does not mutate the learner profile, collect news, or own teaching-session state.

### `nature-reader`

- **Domain:** Building a traceable bilingual evidence layer from PDF, DOI, arXiv, publisher HTML, or pasted text.
- **Output:** Source anchors, translation, equation/figure/table extraction, source map, and reader bundle.
- **Examples:** “Read this paper and build paragraph-level Chinese-English alignment with source anchors.”; “Extract every figure, table, and equation while preserving page-level provenance.”

### `reader-skill`

- **Domain:** Converting a paper evidence bundle into a standalone interactive bilingual reader.
- **Output:** HTML reader, translation-fidelity checks, learner annotations, and feedback export.
- **Examples:** “Turn this `paper_reader` directory into a browser-ready bilingual reader.”; “Audit whether the reader covers the complete paper and exports valid feedback.”

### `reader-learner`

- **Domain:** Importing reading, news, and teaching feedback, maintaining a learner profile, and projecting a visible knowledge wiki.
- **Output:** Validated concept states, events, sources, review queue, and Obsidian pages.
- **Examples:** “Import `reader_feedback.json` and synchronize the visible wiki.”; “List learning and due-review concepts without hand-editing the profile.”
- **Version note:** The central registry retains the generic `1.0.0` historical release. PaperTrace now owns a fork with chat-profile and reader-v3 integration.

### `chat-knowledge-profile`

- **Domain:** Extracting reviewable learning signals from local ChatGPT, Claude, DeepSeek, and similar conversation exports.
- **Output:** Bounded evidence events, conversation summaries, candidate profile signals, and human-reviewed patches.
- **Examples:** “Extract concepts I repeatedly struggle with from these chat exports, but do not mutate my profile.”; “Generate a reviewable profile patch with provenance for every proposed signal.”

### `demo-skill`

- **Domain:** Bilingual project demo pages built from verified README and Agent contracts.
- **Output:** Chinese and English HTML demos, pipeline storytelling, interaction, and pre-publication audit.
- **Examples:** “Build a bilingual demo page for the four project pipelines from the current README.”; “Audit the demo against repository facts and repair incorrect claims.”

### `lean-html-skill`

- **Domain:** PaperTrace's shared HTML shell, visual system, and feedback-export components.
- **Output:** Embedded CSS/JS, interactive feedback panels, copy/download JSON, and consistent page styling.
- **Examples:** “Add the shared feedback-export panel to this paper reader.”; “Refactor the briefing HTML onto the shared shell without duplicating CSS and JavaScript.”

## Personal Skill (1)

### `logic-chain-tutor`

- **Domain:** Prerequisite diagnosis, step-by-step derivation, conceptual distinctions, physical meaning, and paper-method teaching.
- **Output:** A logical chain from the learner's current blockage, small examples, misconception repair, and contract-aware depth.
- **Examples:** “I forgot the linear-algebra prerequisites; explain graph convolution starting from eigenvectors.”; “Derive this formula step by step and distinguish mathematical objects, operations, and information carriers.”
- **Boundary:** Do not use it for short factual lookups or execution-only tasks.
- **Source:** [`90-personal/logic-chain-tutor/`](90-personal/logic-chain-tutor/).

## Recommended workflows

```text
Research idea → research-logic → experiment-design → training-code-architecture
              → data-analysis → academic-figure-workflow → research-html-report
              → latex-paper-build-skill → paper-polishing-skill / prl-manuscript-polisher

Paper learning → nature-reader → reader-skill → reader-learner
               → adaptive-teach / allegory-teach

Governance → research-workspace-governance → project-agent-generator-skill
           → neat-freak → research-project-pipeline (for complete orchestration)
```

## Skill Registry

`50-core-utils/skill-registry/` manages shared Skills that must enter a project as locked copies:

- `sources/`: editable canonical sources.
- `releases/`: immutable release snapshots.
- `forked`: the project owns the implementation and central sync cannot overwrite it.
- `vendored`: the project consumes a locked central release.

All nine current PaperTrace Skills are registered as project-owned `forked` implementations. Central `reader-learner 1.0.0` is retained only as a traceable historical release.

## Validation

Run from the repository root:

```powershell
python -X utf8 -B "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" ".\50-core-utils\<skill-folder>"
python -X utf8 -B ".\50-core-utils\skill-registry\tools\skill_registry.py" registry-check --registry ".\50-core-utils\skill-registry"
python -X utf8 -B ".\50-core-utils\neat-freak\scripts\manage_project_knowledge.py" "." audit
```

## Maintenance and licensing

1. Every Skill has one canonical source location; project-owned Skills remain in their own repositories.
2. Never edit immutable `releases/` directly; create a new version when an upgrade is appropriate.
3. Inspect staged changes, tests, sensitive information, and licenses before pushing.
4. Never publish manuscripts, experimental data, learner profiles, conversation records, or credentials.

Each Skill and external repository retains its own license and provenance. This repository does not apply one blanket license to all content until per-Skill compatibility has been confirmed.
