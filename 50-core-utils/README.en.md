# Core utilities

[中文](README.md) | [English](README.en.md) | [Back to the root README](../README.en.md)

`50-core-utils/` stores nine active Skills reusable across projects plus version-registry infrastructure that is not counted as an active Skill. These components do not define domain research methods or replace the project-governance ownership in `20-project-build`.

## Overall framework

```text
One-time framework generation completed
  ↓
neat-freak: repeated project-information and loading maintenance
  ├─ skill-audit-refactor: audit or refactor a Skill
  ├─ training-code-architecture: reorganize training engineering
  ├─ find-skills: discover and inspect external Skill candidates
  └─ handoff: pause, transfer, or change sessions

Central Skill version governance
  └─ skill-registry: source, immutable releases, and consumer relationships

Learning and concept explanation
  └─ logic-chain-tutor: bridge the learner's current gap

Public-facing web design
  └─ design-taste-frontend (taste-skill): art direction, implementation, and visual checks

Interactive diagrams and explanation
  └─ archify: HTML diagrams of systems, workflows and relationships; on-demand one-page explainers

Prose editing
  └─ humanizer: preserve meaning while reducing redundant, inflated and formulaic prose
```

## Component responsibilities

| Component | Nature | Sole responsibility | Does not own |
|---|---|---|---|
| [`neat-freak`](neat-freak/SKILL.md) | Active Skill | Repeatedly audit and synchronize README, `.agents`, durable knowledge, and existing managed loading after initial generation | Initial framework generation, governance records, or scientific interpretation |
| [`handoff`](handoff/SKILL.md) | Active Skill | Produce a compact, evidence-linked continuation handoff | Proving task completion or expanding the next Agent's authority |
| [`skill-audit-refactor`](skill-audit-refactor/SKILL.md) | Active Skill | Audit Skill triggering, scope, resources, duplication, and safety, then make the smallest refactor | Expanding capability without evidence or removing necessary safety gates |
| [`training-code-architecture`](training-code-architecture-skill/SKILL.md) | Active Skill | Extract configuration, factories, adapters, training loops, and reproducible outputs from existing training scripts | Hard-coding one dataset, model, or metric as a universal standard |
| [`find-skills`](find-skills/SKILL.md) | Active Skill | Find, inspect, and recommend external Skills; help install only after explicit user approval | Automatically installing candidates, replacing human safety judgment, or adding outside Skills to this Hub |
| [`logic-chain-tutor`](logic-chain-tutor/SKILL.md) | Active Skill | Build prerequisites, derivations, examples, and understanding checks from the current gap | Replacing research execution or scientific review, or changing external learning profiles without approval |
| [`design-taste-frontend`](taste-skill/SKILL.md) | Active Skill | Taste v2: public-page art direction, layout, imagery, motion, and visual checks | Dashboards, app screens, universal design rules, or unauthorized downloads and browser operations |
| [`archify`](archify/SKILL.md) | Active Skill | Interactive HTML diagrams and on-demand one-page explainers from descriptions or repository evidence | Scientific certification, academic figure delivery, automatic global installation, or unauthorized global-rule edits |
| [`humanizer`](humanizer/SKILL.md) | Active Skill | Reduce formulaic prose while preserving facts and the writer's voice | Scientific review, authorship detection, detector-evasion guarantees, or unauthorized manuscript edits |
| [`skill-registry`](skill-registry/README.md) | Infrastructure | Maintain editable source, version metadata, immutable release snapshots, and consumer relationships | Counting as an active Skill or overwriting project-owned forks |

## When to use

- The Agent framework exists and code, directories, or decisions changed: use `neat-freak`.
- An existing Skill may be too long, overlapping, or missing validation: use `skill-audit-refactor`.
- Existing machine-learning training code needs a reusable architecture: use `training-code-architecture`.
- External Skills need to be discovered, inspected, or compared: use `find-skills`; it reads local locations, the AI Roasting library, skills.sh, and GitHub, and still requires explicit approval before candidate installation.
- Work is paused, context is compacted, or another session will continue: use `handoff`.
- An unfamiliar concept, symbol, equation, or paper method needs explanation: use `logic-chain-tutor`; initial Agent scaffolding is not required.
- A public-facing page needs design or improvement: read `taste-skill/SKILL.md`, invoked as `design-taste-frontend`; see [provenance](taste-skill/UPSTREAM.md) for prerequisites, licensing and the fixed version. Like `find-skills`, this is central source only, not automatic global discovery.
- A system, workflow, relationship, state, or code architecture needs explanation, or a one-page explainer is requested: read `archify/SKILL.md`; see [provenance](archify/UPSTREAM.md) for the fixed version, execution boundaries and licenses. It does not replace `academic-figure-workflow` in the paper category.
- Registry-managed versions need checking, publishing, or synchronization: use the `skill-registry` tools.

When `.agents` is missing, use `20-project-build/project-agent-generator-skill` rather than asking Neat-Freak to regenerate a framework. Auditing the final change surface belongs to `20-project-build/project-submission-audit`, not Handoff.

- For redundant or formulaic prose, read `humanizer/SKILL.md`, invoked as `humanizer`; see [provenance](humanizer/UPSTREAM.md). This is central source, not a global installation.

## Boundaries and safety

- “audit / check / review” is read-only by default; writing requires an explicit initialization, synchronization, repair, or maintenance request.
- Preserve user changes and dirty worktrees; do not use repository-wide rollback to clean unrelated work.
- Registry `releases/` are immutable snapshots and are not edited directly.
- Project-owned forks are not silently overwritten from central historical releases.
- Handoff writes to the operating-system temporary directory by default and does not copy secrets or full conversations.
- Training architecture extracts stable interfaces; data, loss, shape, and domain rules remain in project Adapters.
- Find Skills uses network search only to collect candidates and evidence; a discovery result never modifies local Skills, user-level Codex configuration, or this Hub.
- Full Taste checks need Node 22+ and a browser; future runs create project working files and screenshots and may download assets. Importing the source grants none of those actions; user intent and project rules take precedence.
- Future Archify runs may create `.archify/`, HTML and review receipts; some commands launch a browser and check upstream updates. Importing it grants none of those actions and does not enable proactive explanation or edit global rules.

Humanizer's upstream file mode writes text back and needs an actual edit authorization. Its punctuation and wording preferences are not universal scientific standards. Preserve scientific qualifiers, numbers, terms and citations; prose editing does not replace `paper-audit`.

## Verification

Run from the repository root:

```powershell
python -X utf8 -B ".\50-core-utils\neat-freak\scripts\manage_project_knowledge.py" "." audit
python -X utf8 -B ".\50-core-utils\skill-registry\tools\skill_registry.py" registry-check --registry ".\50-core-utils\skill-registry"
python -X utf8 -B -m unittest discover -s ".\50-core-utils\neat-freak\tests" -p "test_*.py"
python -X utf8 -B ".\50-core-utils\skill-registry\tests\test_skill_registry.py"
```

The corresponding `SKILL.md` or Registry README remains authoritative for commands, approval gates, inputs, and outputs.

## Provenance and license

[`Humanizer`](https://github.com/blader/humanizer), maintained by Siqi Chen (blader), is MIT licensed, version `3.1.0`, pinned to `8c307f367c91bd974002f10f2be2965d642c13df`. Nine execution, documentation, license and offline-validation files were selected from the owner-provided local copy and matched to that commit. Only two README trailing spaces were removed, and [provenance](humanizer/UPSTREAM.md) was added. Plugin JSON remains for the original validator; no plugin/global installation or private paper material is included.

[`Archify`](https://github.com/tt-a1i/archify), maintained by tt-a1i and originating from Cocoon AI, is pinned to `81c6be8d87090670c45d08a8f97f9d29c5af0bec` (v3.2.0). All 206 files in its single `archify/` directory are retained. Apache-2.0 applies, with historical MIT grants and separate font/icon terms retained. LICENSE, NOTICE and third-party notices remain intact; see [UPSTREAM.md](archify/UPSTREAM.md). The website, repository development tooling and global integrations are excluded.

[`Taste Skill`](https://github.com/Leonxlnx/taste-skill) is Leonxlnx's MIT-licensed default v2 Skill, pinned to `f624f37a8c650b9cc550253104925efe4c8de246`. The single Skill directory is imported intact with its original contract and resources; see [UPSTREAM.md](taste-skill/UPSTREAM.md) for licensing and scope. Other style Skills, plugins and the desktop app are excluded.

The local `neat-freak` draws on KKKKhazix's [`neat-freak`](https://github.com/KKKKhazix/khazix-skills/blob/main/neat-freak/SKILL.md) (MIT) for knowledge organization and workspace-consistency ideas, and extends them with `.agents/memory/`, hash-bound updates, and Codex startup-loading audits. The local `handoff` draws on Matt Pocock's [`handoff`](https://github.com/mattpocock/skills/tree/main/skills/productivity/handoff) (MIT) for temporary-directory defaults, existing-evidence references, and sensitive-information cleanup. [`find-skills`](https://github.com/airoasting/find-skills) is an AI ROASTING MIT-licensed fixed snapshot (v1.2.1, commit `55aba1789fe0504734964d98ae1ccd39e2fefea0`); its original execution contract, license, and provenance record are retained, while this Hub includes only the files needed for Codex execution and offline regression. These acknowledgements do not imply endorsement; third-party obligations remain in effect.
