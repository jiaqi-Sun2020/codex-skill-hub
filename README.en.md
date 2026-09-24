# Codex Skill Hub

[中文](README.md) | [English](README.en.md)

`codex-skill-hub` is the central source and navigation repository for reusable Codex Skills. It keeps project governance, paper delivery, cross-project utilities, and personal teaching separate so every capability has one canonical source while users retain one concise place to find the correct workflow.

The repository directly maintains 20 active Skills: nine under `10-paper-build`, six under `20-project-build`, four under `50-core-utils`, and one under `90-personal`. Version-registry infrastructure, external shortcuts, staging, and archives are not counted as active Skills.

> Reusable instructions, scripts, tests, templates, and documentation may be public. Manuscripts, experimental data, learning profiles, conversation records, credentials, tokens, and machine-private state are not public repository content.

## Overall framework

```text
Initial onboarding and ongoing governance → 20-project-build
Research results to paper delivery         → 10-paper-build
Cross-project maintenance and quality      → 50-core-utils
Personal learning and teaching             → 90-personal
External and compatibility entry points    → 30-papertrace / 40-skill-registry
Unreviewed and historical material         → 98-inbox / 99-archive
```

The three documentation layers have distinct responsibilities:

1. This README explains the repository-wide framework, categories, and entry selection.
2. Numbered-category READMEs explain the components, workflows, boundaries, and verification for their category.
3. Each Skill's `SKILL.md` is its formal execution contract; READMEs do not duplicate the complete rules.

## Category navigation

| Category | Nature | Purpose | Details |
|---|---|---|---|
| `10-paper-build` | Active source | Move from research logic, evidence design, and analysis to figures, Chinese review drafts, review, and submission | [Paper-build framework](10-paper-build/README.en.md) |
| `20-project-build` | Active source | Initial onboarding, governance contracts, repeated research management, protocol audits, and submission audits | [Project-build framework](20-project-build/README.en.md) |
| `30-papertrace` | External navigation | Point to reader, teaching, and briefing Skills owned by PaperTrace | [PaperTrace entry](30-papertrace/README.en.md) |
| `40-skill-registry` | Compatibility navigation | Point to the repository's one canonical Skill Registry source | [Registry entry](40-skill-registry/README.en.md) |
| `50-core-utils` | Active source and infrastructure | Project-information maintenance, handoff, Skill audits, training architecture, and version governance | [Core utilities](50-core-utils/README.en.md) |
| `90-personal` | Active source | Teaching Skills adapted to personal learning | [Personal Skills](90-personal/README.en.md) |
| `98-inbox` | Unreviewed staging | Hold patches, plans, and candidate documents that have not been approved | [Staging rules](98-inbox/README.en.md) |
| `99-archive` | Historical archive | Hold historical material excluded from current discovery and execution | [Archive rules](99-archive/README.en.md) |

`.agents/` stores project Agent context and durable knowledge; `.codex/` stores project-local startup loading. Neither replaces the human overview or creates another root `AGENTS.md`.

## Twenty active Skills

| Category | Skill | One-line responsibility |
|---|---|---|
| Paper build | `research-logic` | Build mechanism-level research logic and defensible contribution claims |
| Paper build | `experiment-design` | Derive evidence gaps, controls, ablations, and claim boundaries from a claim |
| Paper build | `data-analysis` | Check data integrity and produce statistics, intervals, and reviewable interpretation |
| Paper build | `research-html-report` | Package research logic and evidence plans as a standalone HTML report |
| Paper build | `academic-figure-workflow` | Produce editable, traceable academic figures with rendered QA |
| Paper build | `latex-paper-build-skill` | Build and maintain a LaTeX-centered paper-delivery pipeline |
| Paper build | `paper-polishing-skill` | Translate, restructure, and polish approved content for a target venue |
| Paper build | `prl-manuscript-polisher` | Adapt, compress, and evidence-calibrate a technically complete manuscript for PRL |
| Paper build | `interactive-skill-builder` | Create or update Skills through interviews, specifications, and approval gates |
| Project build | `project-agent-generator-skill` | Create missing `.agents` scaffolding and startup loading once |
| Project build | `research-project-pipeline` | Orchestrate project discovery, onboarding, verification, and handoff once |
| Project build | `research-workspace-governance` | Manage research contracts, state, evidence, migration, and traceability |
| Project build | `research-management-pipeline` | Repeatedly summarize state and route one smallest next action after onboarding |
| Project build | `experiment-protocol-audit` | Read-only audit explicit Profiles, Protocols, manifests, and runtime evidence |
| Project build | `project-submission-audit` | Read-only audit the actual change surface before submission or delivery |
| Core utility | `neat-freak` | Repeatedly reconcile README, Agent documents, and durable project knowledge |
| Core utility | `handoff` | Produce a compact, evidence-linked continuation handoff |
| Core utility | `skill-audit-refactor` | Audit, simplify, split, or refactor an existing Skill |
| Core utility | `training-code-architecture` | Turn training scripts into reusable, configuration-driven architecture |
| Personal teaching | `logic-chain-tutor` | Build a logical chain from the learner's current gap to the target concept |

## Where should I start?

| Current goal | Entry point |
|---|---|
| New research project or a legacy project not yet onboarded | Start with the one-time onboarding flow in [20-project-build](20-project-build/README.en.md) |
| Contracts, evidence, or state changed in an onboarded project | Use the repeated research-management flow in the project-build framework |
| Turn existing research into a paper | Enter [10-paper-build](10-paper-build/README.en.md) at the earliest missing stage |
| Update README, `.agents`, or durable knowledge in an initialized project | Use the repeated maintenance tools in [50-core-utils](50-core-utils/README.en.md) |
| Audit a Skill or reorganize training code | Choose the corresponding core utility |
| Prepare a submission, delivery, or session transfer | Use submission audit and handoff separately; neither grants automatic commit authority |
| Learn an unfamiliar concept, formula, or paper method | Use the teaching entry in [90-personal](90-personal/README.en.md) |

## Quick start

```powershell
git clone https://github.com/jiaqi-Sun2020/codex-skill-hub.git
Set-Location .\codex-skill-hub
```

Ask Codex to read the target directory's `SKILL.md`, or install the complete Skill directory. Do not copy only `SKILL.md`: `scripts/`, `references/`, `assets/`, and `templates/` may also be part of the execution contract.

Run the minimum repository checks from the repository root:

```powershell
git diff --check
python -X utf8 -B ".\50-core-utils\neat-freak\scripts\manage_project_knowledge.py" "." audit
```

See each category README for category commands and tests. The corresponding `SKILL.md` remains authoritative for execution semantics.

## External projects, provenance, and license

Project-owned PaperTrace Skills are maintained in their [separate repository](https://github.com/jiaqi-Sun2020/PaperTrace/tree/main/skills). This repository provides navigation only and does not copy their current source. The one canonical Skill Registry source is [`50-core-utils/skill-registry/`](50-core-utils/skill-registry/README.md).

Each category README records the migration sources, open-source influences, and licenses directly relevant to that category. New influences must record the author or maintainer, project link, scope of influence, and license rather than leaving provenance only in commit history.

Content created by `jiaqi-Sun2020` or otherwise eligible for relicensing is provided under the [MIT License](LICENSE). Third-party and derivative portions remain subject to their original licenses, copyright notices, and notice obligations; the root MIT License does not override those requirements.
