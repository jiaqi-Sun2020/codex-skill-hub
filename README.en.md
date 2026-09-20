# Codex Skill Hub

[中文](README.md) | [English](README.en.md)

`codex-skill-hub` is a central source and version-governance repository for reusable Codex Skills. This document focuses on the **eleven active Skills whose source is actually stored in this repository**. Skills maintained independently in S Paper Skills and PaperTrace are covered only by a short overview and links near the end.

As of 2026-09-20, this repository contains:

- eleven directly maintained active Skills;
- one integrated version registry under `50-core-utils/skill-registry/`;
- lightweight indexes for two external Skill projects, without duplicating their project-owned source.

> The public repository contains reusable instructions, scripts, tests, templates, and documentation. Manuscripts, experimental data, learner profiles, conversation records, credentials, and machine-local state are outside its publication scope.

## Quick start

```powershell
git clone https://github.com/jiaqi-Sun2020/codex-skill-hub.git
Set-Location .\codex-skill-hub
```

To use a Skill, ask Codex to read the `SKILL.md` in its directory or install the entire Skill directory into your Skill search path. Do not copy only `SKILL.md`: related `scripts/`, `references/`, `assets/`, and `templates/` may be part of the execution contract.

## Repository structure

```text
codex-skill-hub/
|-- README.md / README.en.md
|-- .agents/                         Project context and durable knowledge
|-- .codex/                          Project-local Codex bootstrap
|-- 10-paper-build/
|   `-- academic-figure-workflow/    Academic figure workflow
|-- 20-project-build/
|   |-- experiment-protocol-audit/
|   |-- project-agent-generator-skill/
|   |-- project-submission-audit/
|   |-- research-project-pipeline/
|   `-- research-workspace-governance/
|-- 50-core-utils/
|   |-- handoff/
|   |-- skill-audit-refactor/
|   |-- training-code-architecture-skill/
|   |-- neat-freak/
|   `-- skill-registry/              Version infrastructure, not an active Skill
`-- 90-personal/
    `-- logic-chain-tutor/
```

## Choosing a Skill from this repository

| Goal | Skill |
|---|---|
| Create paper figures, model diagrams, multi-panel plots, or editable PPT figures | `academic-figure-workflow` |
| Generate the initial `.agents/`, durable-knowledge baseline, and Codex bootstrap loading once | `project-agent-generator-skill` |
| Orchestrate one-time research-project discovery, onboarding, governance checks, Agent setup, and acceptance | `research-project-pipeline` |
| Independently audit an experimental design or run manifest against an explicit domain profile, protocol, and evidence | `experiment-protocol-audit` |
| Audit the actual change surface before a commit, PR, release, delivery, or handoff | `project-submission-audit` |
| Govern research assets, locations, statuses, evidence, migration, deletion approval, and comparison-claim boundaries | `research-workspace-governance` |
| Prepare a compact, traceable task handoff for another agent or later session | `handoff` |
| Audit, simplify, split, or refactor an existing Skill | `skill-audit-refactor` |
| Refactor ML scripts into a reusable configuration-driven training system | `training-code-architecture` |
| Repeatedly update project documentation and `.agents/memory/`, then audit or repair managed bootstrap wiring | `neat-freak` |
| Learn a concept or formula from the exact point of confusion | `logic-chain-tutor` |

## 1. Academic figure workflow

### `academic-figure-workflow`

**Domain**

Formal figures for papers, theses, and research reports: mechanism schematics, neural-network or system diagrams, real-data plots, multi-panel compositions, editable PowerPoint figure kits, captions, and pre-submission visual QA.

**Use it when**

- a figure set must be planned from manuscript claims and evidence rather than appearance alone;
- a reference image should guide visual language without copying its scientific content;
- the deliverable must remain editable and reproducible in Draw.io, SVG, Matplotlib, PDF, PNG, or PPTX;
- typography, strokes, legends, markers, colour, accessibility, and layout must be checked at final publication size;
- figures, captions, data, code, and manuscript claims need an inspectable provenance chain.

**Typical inputs and outputs**

- Inputs: manuscript passages, model code, datasets, equations, sketches, reference images, target venue, and final dimensions.
- Outputs: editable sources, SVG/PDF/PNG exports, PPT figure kits, `caption.md`, style manifests, evidence traces, and rendered QA results.

**Critical boundary**

The workflow does not invent data, units, uncertainty, mechanisms, or model components. Data-backed figures require source and uncertainty checks, and complex figures are not complete until reviewed at their intended final size.

**Example prompts**

> Build an editable Draw.io neural-network architecture figure from the model code and manuscript methods, then verify every connection.

> Turn these CSV results into a Nature-style multi-panel figure with an editable PPT kit, caption, and final-size QA.

Source: [`10-paper-build/academic-figure-workflow/`](10-paper-build/academic-figure-workflow/)

## 2. Central utilities

### `project-agent-generator-skill`

**Domain**

Generate repository-local Agent context once for a project that has not yet initialized its Agent framework, using verified facts about architecture, commands, configuration, decisions, and safety boundaries.

**Core capabilities**

- Generate the initial `.agents/` documentation bundle once.
- Initialize the `.agents/memory/` durable-knowledge index.
- Install a project-local `.codex/` hook that loads `.agents/AGENTS.md` on startup and resume.
- Hand routine updates to `neat-freak`; retain forced replacement only as explicitly authorized legacy recovery.
- Reject paths outside the project, link targets, and suspected credential content.

**Typical output**

`AGENTS.md`, `PROJECT_CONTEXT.md`, `ARCHITECTURE.md`, `CONFIG_SPEC.md`, `RUNBOOK.md`, `DECISIONS.md`, a documentation index, a knowledge baseline, and the project bootstrap hook.

**Example prompts**

> Inspect this repository and generate project-local `.agents` context. Preview all destinations first and do not modify application code.

> This project has no Agent context yet. Generate the framework once, then hand routine maintenance to Neat-Freak.

Source: [`20-project-build/project-agent-generator-skill/`](20-project-build/project-agent-generator-skill/)

### `research-project-pipeline`

**Domain**

Initialize a new research project, or onboard a legacy project that has not completed Agent setup, through a one-time workflow spanning governance, Agent context, knowledge audits, and final acceptance.

**Core capabilities**

- Begin with read-only discovery and separate facts, risks, and unresolved choices.
- Use research-workspace rules to design the target structure.
- Produce a reviewable and reversible migration plan.
- Delegate project Agent-context generation to the Generator, or preserve existing context.
- Run knowledge, bootstrap, and adversarial acceptance checks.
- Accept an optional Agent-loading manifest path and delegate its content audit to `neat-freak`; Pipeline performs only project-boundary path checks.
- Invoke a domain-neutral comparison-record validator that checks structure, evidence, review, and declared boundaries without prescribing relation types.
- Bind an independent `experiment-protocol-audit` record when applicable, reporting onboarding, governance, domain validation, execution authorization, and claim support on separate axes.

**Difference from adjacent Skills**

- For `.agents/` generation alone, use `project-agent-generator-skill`.
- For research-directory and evidence policy alone, use `research-workspace-governance`.
- Use this Skill when both are required together with migration and handoff.

**Example prompts**

> Integrate this legacy research project into the standard workflow: inventory it read-only, propose a migration plan, and wait for review before applying it.

> Set up a new research project from workspace structure through Agent context and adversarial acceptance.

> Audit whether nested subprojects can load every applicable mandatory policy, and confirm that comparison claims remain owned by an explicitly selected domain Profile or reviewer.

Source: [`20-project-build/research-project-pipeline/`](20-project-build/research-project-pipeline/)

### `experiment-protocol-audit`

**Domain**

Use this Skill to evaluate explicit domain constraints against a project-owned Domain Profile, Project Protocol, normalized observations, manifests, and runtime evidence without running experiments or project commands.

**Core capabilities and boundary**

- Support generic numeric bounds, equality, shapes, sets, cardinality, and allowed transforms.
- Compare requested/generated/approved manifests exactly and record validator/profile/protocol/source/evidence hashes so a change makes the old record stale.
- Emit an independent record for Pipeline binding; never execute Runtime Adapters, create project frameworks, choose methods, or equate completed work with a supported scientific claim.

**Example prompts**

> Audit the experimental design against this project's declared Domain Profile and Project Protocol. Read normalized JSON only; do not run experiments, project commands, or adapters. Produce a validation record that the Pipeline can bind.

> Compare the requested, generated, and approved task manifests exactly. Identify silent filtering, duplicate units, or unapproved scope expansion.

Source: [`20-project-build/experiment-protocol-audit/`](20-project-build/experiment-protocol-audit/)

### `project-submission-audit`

**Domain**

Perform a read-only audit of the exact proposed change surface before a commit, pull request, release, external delivery, or task handoff. It checks scope, behavior contracts, architecture, tests, security, documentation, and repository cleanliness, then returns `PASS`, `BLOCKED`, or `INCOMPLETE`.

**Core capabilities and boundary**

- Reconcile staged, unstaged, and untracked state so the reviewed content matches the proposed submission.
- Map requirements to implementation, affected interfaces, and verification evidence.
- Apply locality, module depth, seams, and the deletion test only to architecture relevant to the change.
- Record P0/P1/P2 findings with evidence, impact, smallest repair, and verification method.
- Remain read-only by default; it does not commit, push, publish, or establish scientific validity.

**Example prompt**

> Audit the final diff before I submit this branch. Confirm that tests reach the changed behavior and return an evidence-backed PASS or BLOCKED decision.

Source: [`20-project-build/project-submission-audit/`](20-project-build/project-submission-audit/)

### `research-workspace-governance`

**Domain**

Govern a research workspace in a domain-neutral way when sources, working assets, evidence, automation, temporary material, and deliverables have become mixed or difficult to trace.

**Core capabilities**

- Define roles such as `source`, `method`, `working`, `evidence`, `deliverable`, `automation`, `archive`, and `temporary`.
- Trace sources, methods, working assets, evidence, claims, and deliverables.
- Resolve canonical `.agents/governance/` and legacy root `governance/` without guessing when both exist.
- Support single-file, task-local, and custom-path automation contracts.
- Protect immutable evidence and provide failure-safe migration and cleanup policies.
- Record work completion separately from scientific-claim review.
- Audit reproducibility and handoff readiness.

**Boundary**

This Skill owns research assets, locations, status, evidence, and change governance. It does not replace any field's method design or scientific interpretation. Its comparison validator checks declaration shape, evidence metadata, review state, invalidation, and allowed uses; an explicitly selected domain Skill or reviewer remains responsible for scientific validity.

**Example prompts**

> Establish a minimal governance contract for this project without renaming its existing directories, and define each asset lifecycle.

> Audit whether each conclusion traces to sources, methods, work records, evidence, and review state.

> Create a domain-defined comparison record for two candidate results, including allowed uses, forbidden inferences, reviewer, and revalidation conditions.

Source: [`20-project-build/research-workspace-governance/`](20-project-build/research-workspace-governance/)

### `skill-audit-refactor`

**Domain**

Audit and refactor existing Codex Skills, especially when triggers are vague, instructions are bloated, scope is overloaded, resources are duplicated, validation is missing, or safety boundaries are unclear.

**Core capabilities**

- Review frontmatter, triggers, body instructions, scripts, references, templates, and Agent metadata.
- Classify content as keep, compress, move to resources, or delete.
- Decide whether a Skill should remain whole, split into sub-Skills, or only decompose resources.
- Reduce context cost without losing critical capability or safety rules.
- Validate the refactor and explain residual risk.

**Example prompts**

> Audit whether this Skill is too long, broad, or easy to trigger incorrectly. Give me prioritized findings and a refactor plan first.

> Move conditional details into `references/` while preserving every safety gate and output-quality contract.

Source: [`50-core-utils/skill-audit-refactor/`](50-core-utils/skill-audit-refactor/)

### `training-code-architecture`

**Domain**

Extract a reusable machine-learning training architecture from existing code. It preserves execution structure and interfaces, not the special logic of one dataset, model, or task.

**Core capabilities**

- Establish a thin `main.py → train(args)` entry point.
- Organize experiment, data, model, training, task, and output settings in JSON.
- Use factories for model, optimizer, scheduler, and component construction.
- Isolate batching, graph structure, model calls, losses, and metrics behind a `TaskAdapter`.
- Standardize checkpoints, logs, copied configuration, history, and final metrics.
- Reuse one training engine across static-graph, dynamic-graph, sequence, or other tasks.

**Critical boundary**

Fixed tensor shapes, preprocessing rules, graph assumptions, losses, and model names from the example project are not hard-coded as universal architecture.

**Example prompts**

> Convert this training script into a reusable configuration-driven template while preserving the `main.py → train(args)` workflow.

> Isolate task logic behind adapters so one training engine supports both static and dynamic graph experiments.

Source: [`50-core-utils/training-code-architecture-skill/`](50-core-utils/training-code-architecture-skill/)

### `neat-freak`

**Domain**

After one-time framework generation, repeatedly maintain repository-local Markdown knowledge and Agent documentation while preventing contradictions and duplication across `.agents/memory/`, README files, architecture documentation, and current code.

**Core capabilities**

- Audit the knowledge index, topic files, project documentation, and provenance without writing.
- Initialize only missing knowledge baselines.
- Update durable knowledge through a hash-bound `plan → apply` workflow.
- Audit `.agents/AGENTS.md` and project-local Codex hooks for correct loading.
- With explicit authorization, repair existing managed project-local Codex Hook wiring without regenerating the framework.
- Independently verify mandatory-policy paths, hashes, loader evidence, isolation decisions, and copy drift across nested execution roots.
- Reconcile duplicate knowledge, repair indexes, and prepare durable handoff context.

**Critical boundary**

Requests phrased as “audit,” “check,” or “review” are read-only. Writing requires an explicit initialize, sync, repair, or maintenance request.

**Example prompts**

> Audit the MEMORY index, topic files, and project documentation for conflicts. Do not modify anything.

> Prepare a hash-bound update plan for this durable decision, then apply it only after review.

> Audit whether every nested Agent root can reach its applicable mandatory policy; report missing declarations and unreviewed natural-language weakening as risks.

Source: [`50-core-utils/neat-freak/`](50-core-utils/neat-freak/)

### `handoff`

**Domain**

Create a compact, evidence-linked continuation document when work is paused, transferred, compacted, or continued by another agent or later session.

**Core capabilities and boundary**

- Prefer current files, Git state, and test output over conversational memory.
- Separate completed, in-progress, not-started, blocked, and unauthorized work.
- Link to existing specs, issues, ADRs, diffs, and reports instead of copying them.
- Record working directories, complete commands, results, decisions, residual risks, and one exact next action.
- Write to the operating-system temporary directory by default; it neither mutates the project nor proves completion or authorizes external actions.

**Example prompt**

> Prepare a handoff for the next session with only the current state, verification evidence, blockers, and exact next action, saved in the system temporary directory.

Source: [`50-core-utils/handoff/`](50-core-utils/handoff/)

## 3. Personal teaching Skill

### `logic-chain-tutor`

**Domain**

Teach an unfamiliar concept, mathematical expression, physical meaning, or paper method from the learner's exact point of confusion. It is designed for questions such as “what is it?”, “why does this follow?”, “where does this formula come from?”, and “how do these two objects differ?”

**Core capabilities**

- Diagnose the missing prerequisite instead of restarting an entire course mechanically.
- Present a map from known anchor to missing bridge, target idea, and application.
- Explain each symbol's type, shape, operation, and physical meaning step by step.
- Repair misconceptions with the smallest complete example, counterexample, and explicit comparison.
- Respect output contracts such as concise explanation, prompt-only, or localized rewrite.

**Boundary**

It should not trigger for simple factual lookup or execution-only work. It adapts teaching within the current exchange and does not mutate an external learner profile.

**Example prompts**

> I have forgotten the linear-algebra prerequisites. Explain graph convolution from eigenvectors and justify each step.

> Distinguish a quantum state, operator, eigenvalue, and measurement outcome, then use one minimal example to show why they are not interchangeable.

Source: [`90-personal/logic-chain-tutor/`](90-personal/logic-chain-tutor/)

## Skill Registry infrastructure

[`50-core-utils/skill-registry/`](50-core-utils/skill-registry/) is version-governance infrastructure integrated into this repository. It is not a twelfth active Skill and is no longer published as a separate repository.

| Path | Purpose |
|---|---|
| `registry.json` | Records governed Skill versions and integrity metadata |
| `sources/` | Editable canonical source |
| `releases/` | Immutable published snapshots |
| `tools/skill_registry.py` | Registry checking, release, and synchronization tool |
| `tests/` | Registry behavior tests |

The registry supports two project relationships:

- `vendored`: a project consumes a locked central release;
- `forked`: a project owns its implementation and central synchronization must not overwrite it.

The central `reader-learner 1.0.0` is retained as a traceable historical release. PaperTrace's current `reader-learner` is a project-owned fork and must not be overwritten from this registry.

## Common compositions

```text
Initial research-project onboarding
research-project-pipeline
  → project-agent-generator-skill (one-time generation)
  → research-workspace-governance (governance design and checks)
  → neat-freak (initial acceptance)
  → project-submission-audit (pre-submission or pre-delivery audit)
  → handoff (continue in another session or agent)

Later project-information updates
project change → neat-freak (repeated maintenance)

Machine-learning engineering
existing code → training-code-architecture → reusable training template

Paper figures
claim / code / data → academic-figure-workflow → editable source + exports + QA

Concept learning
current blockage → logic-chain-tutor → prerequisite bridge → derivation / example / check

Ordinary project submission
final change surface → project-submission-audit → PASS / BLOCKED / INCOMPLETE
  → handoff (when work continues elsewhere)
```

## External Skill projects at a glance

The following Skills are not maintained in this repository. This is navigation only; consult each linked repository for complete documentation, current scripts, and project-specific constraints.

| External repository | Broad purpose | Included Skills |
|---|---|---|
| [S Paper Skills](https://github.com/jiaqi-Sun2020/S_paper_skills) | Research logic, experiment design, data analysis, LaTeX paper construction, polishing, and venue adaptation | `research-logic`, `experiment-design`, `data-analysis`, `research-html-report`, `latex-paper-build-skill`, `paper-polishing-skill`, `interactive-skill-builder`, `prl-manuscript-polisher` |
| [PaperTrace](https://github.com/jiaqi-Sun2020/PaperTrace/tree/main/skills) | Paper evidence extraction, bilingual readers, learner profiles, teaching, news briefings, and HTML presentation | `nature-reader`, `reader-skill`, `reader-learner`, `adaptive-teach`, `allegory-teach`, `chat-knowledge-profile`, `ai-quantum-news-briefing`, `demo-skill`, `lean-html-skill` |

Obtain external Skills from their own repositories. Their presence in this README index is not a reason to copy them into this repository.

## Acknowledgements and influences

We thank the authors and maintainers of the following open-source Skills. The local implementations have been reorganized and extended; acknowledgement does not imply endorsement by the original authors.

- [`nature-figure`](https://github.com/Yuan1z0825/nature-skills/tree/main/skills/nature-figure), from the `nature-skills` project maintained by Yuan1z0825 (Apache-2.0). This repository draws on its ideas for claim-driven multi-panel information architecture, semantic colour, editable SVG, and pre-submission QA.
- [`scipilot-figure-skill`](https://github.com/Haojae/scipilot-figure-skill), maintained by Haojae (MIT). This repository draws on its data-first visualization-advisor approach—understand the data and argument before selecting a chart—and its active interception of common scientific-plotting anti-patterns.
- [`neat-freak`](https://github.com/KKKKhazix/khazix-skills/blob/main/neat-freak/SKILL.md), from `khazix-skills` maintained by KKKKhazix (MIT). The local Skill draws on its knowledge-and-governance closeout concept and its approach to reconciling code, runtime state, documentation, Agent rules, authorized memory, and workspace state. This repository extends that foundation with `.agents/memory/`, hash-bound updates, and Codex bootstrap audits.

- [`Scientific-Coding-Skill`](https://github.com/cemde/Scientific-Coding-Skill) (MIT), [`opensciflow-skill`](https://github.com/OpenSciFlow/opensciflow-skill), [`superpowers`](https://github.com/obra/superpowers) (MIT), and [`Hypothesis`](https://github.com/HypothesisWorks/hypothesis) (MPL-2.0) informed `experiment-protocol-audit` principles for explicit parameters, fail-closed evidence, approval records, separated review layers, boundary counterexamples, and minimal failing examples. Their runtimes were neither copied nor added as dependencies.

- Matt Pocock's [`improve-codebase-architecture`](https://github.com/mattpocock/skills/tree/main/skills/engineering/improve-codebase-architecture) and [`handoff`](https://github.com/mattpocock/skills/tree/main/skills/productivity/handoff) (MIT) informed, respectively, the change-surface-first, locality/module-depth/deletion-test architecture review in `project-submission-audit`, and the temporary-directory, evidence-linking, and sensitive-data rules in this repository's `handoff`. The local Skills extend those ideas into a generic submission gate and verifiable transfer without adding the upstream runtime as a dependency.

We also thank the authors of the public figure and accessibility guidance from Nature, PLOS, Springer Nature, Elsevier, IEEE, ACM, SIGACCESS, and JCB. Those sources ground the publication-quality, accessibility, and export checks in this repository. Exact links are recorded in [`publisher-visual-source-map.md`](10-paper-build/academic-figure-workflow/references/publisher-visual-source-map.md).

When a future Skill explicitly draws from another open-source Skill, its author, project link, scope of influence, and license should be added here during integration rather than being recorded only in a commit message.

## Validation

Run all commands from the repository root:

```powershell
Set-Location C:\path\to\codex-skill-hub

python -X utf8 -B "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" ".\<skill-source-directory>"

python -X utf8 -B ".\50-core-utils\skill-registry\tools\skill_registry.py" registry-check --registry ".\50-core-utils\skill-registry"

python -X utf8 -B ".\50-core-utils\neat-freak\scripts\manage_project_knowledge.py" "." audit

python -X utf8 -B ".\20-project-build\research-project-pipeline\tests\test_research_pipeline.py"
python -X utf8 -B ".\20-project-build\experiment-protocol-audit\tests\test_audit_experiment_protocol.py"

python -X utf8 -B ".\20-project-build\research-workspace-governance\tests\test_equivalence_records.py"
```

## Maintenance and licensing

1. Keep one canonical source location for each Skill.
2. Keep project-owned external Skills in their projects instead of duplicating them here.
3. Never edit immutable Registry `releases/` directly; create a new version for an upgrade.
4. Review diffs, tests, sensitive information, machine-specific paths, and license compatibility before pushing.
5. Never publish manuscripts, experimental data, learner profiles, conversation records, or credentials.

Content originally created by `jiaqi-Sun2020`, or otherwise eligible for relicensing, is released under the permissive [MIT License](LICENSE). Anyone may use, copy, modify, merge, publish, distribute, sublicense, and build on these Skills, provided the copyright and MIT permission notice are retained. If this project helps you, attribution or a Star is appreciated, but it is not an additional restriction beyond MIT.

Third-party and derivative portions remain subject to their original licenses, copyright notices, and notice requirements. This repository's MIT License does not override those obligations. Confirmed Skill-level sources are listed above under “Acknowledgements and influences.”
