# Core utilities

[中文](README.md) | [English](README.en.md) | [Back to the root README](../README.en.md)

`50-core-utils/` stores four active Skills reusable across projects plus version-registry infrastructure that is not counted as an active Skill. These components do not define domain research methods or replace the project-governance ownership in `20-project-build`.

## Overall framework

```text
One-time framework generation completed
  ↓
neat-freak: repeated project-information and loading maintenance
  ├─ skill-audit-refactor: audit or refactor a Skill
  ├─ training-code-architecture: reorganize training engineering
  └─ handoff: pause, transfer, or change sessions

Central Skill version governance
  └─ skill-registry: source, immutable releases, and consumer relationships
```

## Component responsibilities

| Component | Nature | Sole responsibility | Does not own |
|---|---|---|---|
| [`neat-freak`](neat-freak/SKILL.md) | Active Skill | Repeatedly audit and synchronize README, `.agents`, durable knowledge, and existing managed loading after initial generation | Initial framework generation, governance records, or scientific interpretation |
| [`handoff`](handoff/SKILL.md) | Active Skill | Produce a compact, evidence-linked continuation handoff | Proving task completion or expanding the next Agent's authority |
| [`skill-audit-refactor`](skill-audit-refactor/SKILL.md) | Active Skill | Audit Skill triggering, scope, resources, duplication, and safety, then make the smallest refactor | Expanding capability without evidence or removing necessary safety gates |
| [`training-code-architecture`](training-code-architecture-skill/SKILL.md) | Active Skill | Extract configuration, factories, adapters, training loops, and reproducible outputs from existing training scripts | Hard-coding one dataset, model, or metric as a universal standard |
| [`skill-registry`](skill-registry/README.md) | Infrastructure | Maintain editable source, version metadata, immutable release snapshots, and consumer relationships | Acting as a fifth active Skill or overwriting project-owned forks |

## When to use

- The Agent framework exists and code, directories, or decisions changed: use `neat-freak`.
- An existing Skill may be too long, overlapping, or missing validation: use `skill-audit-refactor`.
- Existing machine-learning training code needs a reusable architecture: use `training-code-architecture`.
- Work is paused, context is compacted, or another session will continue: use `handoff`.
- Registry-managed versions need checking, publishing, or synchronization: use the `skill-registry` tools.

When `.agents` is missing, use `20-project-build/project-agent-generator-skill` rather than asking Neat-Freak to regenerate a framework. Auditing the final change surface belongs to `20-project-build/project-submission-audit`, not Handoff.

## Boundaries and safety

- “audit / check / review” is read-only by default; writing requires an explicit initialization, synchronization, repair, or maintenance request.
- Preserve user changes and dirty worktrees; do not use repository-wide rollback to clean unrelated work.
- Registry `releases/` are immutable snapshots and are not edited directly.
- Project-owned forks are not silently overwritten from central historical releases.
- Handoff writes to the operating-system temporary directory by default and does not copy secrets or full conversations.
- Training architecture extracts stable interfaces; data, loss, shape, and domain rules remain in project Adapters.

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

The local `neat-freak` draws on KKKKhazix's [`neat-freak`](https://github.com/KKKKhazix/khazix-skills/blob/main/neat-freak/SKILL.md) (MIT) for knowledge organization and workspace-consistency ideas, and extends them with `.agents/memory/`, hash-bound updates, and Codex startup-loading audits. The local `handoff` draws on Matt Pocock's [`handoff`](https://github.com/mattpocock/skills/tree/main/skills/productivity/handoff) (MIT) for temporary-directory defaults, existing-evidence references, and sensitive-information cleanup. These acknowledgements do not imply endorsement; third-party obligations remain in effect.
