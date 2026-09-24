---
name: interactive-skill-builder
description: Create or update Codex skills through an interview-first workflow with explicit author requirements, concrete use cases, destination selection, resource planning, pre-creation review, approval gates, initialization, editing, and validation. Use when the user asks to create a new skill, design a skill, scaffold a skill, turn a workflow into a skill, improve an existing skill, or build a reusable skill only after confirming detailed requirements and auditing the plan.
---

# Interactive Skill Builder

## Overview

Use this skill to create or update Codex skills only after interviewing the author, confirming a written specification, and passing a pre-creation audit. It wraps the official `skill-creator` process with stricter author-facing gates.

## Required Workflow

1. Load the creation rules.
   - Read the official `skill-creator` instructions when available.
   - Read local skill indexes such as a repository README when the destination is a skill bundle.
   - If updating an existing skill, read its `SKILL.md`, referenced resources, and `agents/openai.yaml` before proposing edits.

2. Interview the author.
   - Read `references/author-interview.md`.
   - Ask at most three focused questions per round.
   - Prefer the next question that changes the skill design most: purpose, concrete trigger, output artifact, destination, resource needs, safety/approval constraints, or validation.
   - Continue until the author requirements are specific enough to write a skill specification.

3. Draft the skill specification.
   - Propose the normalized skill name and folder name.
   - State the destination path.
   - State the intended triggers and non-triggers.
   - List expected resources: `scripts/`, `references/`, `assets/`, or none.
   - List required user approvals during future use of the skill.
   - List validation commands.
   - Mark assumptions explicitly.

4. Require explicit approval before creating or modifying the final skill.
   - Show the specification and ask for confirmation.
   - Do not create, overwrite, or substantially edit the target skill until the author approves the specification.
   - If the author changes requirements, revise the specification and ask for approval again.

5. Run the pre-creation audit.
   - Read `references/pre-creation-audit.md`.
   - Check scope, name, trigger description, resource plan, context size, safety gates, and validation.
   - If the audit finds a blocking issue, fix the specification and ask for approval again.

6. Create or update the skill.
   - For a new skill, use the official `init_skill.py` when available.
   - Keep frontmatter limited to `name` and `description`.
   - Keep `SKILL.md` concise and route detailed material into `references/`.
   - Generate or update `agents/openai.yaml` when the local bundle uses it.
   - Avoid auxiliary docs such as README, quick-reference, changelog, or install guides unless the author explicitly asks.

7. Validate and report.
   - Run `quick_validate.py` on the final skill folder.
   - Run syntax checks for any scripts added.
   - Report files created or changed, validations run, and any remaining risks.

## Approval Gates

This skill has two hard gates:

- **Specification approval**: the author confirms the name, scope, destination, trigger, resources, and validation plan.
- **Audit approval**: the author confirms any audit-driven changes before creation proceeds.

If the author explicitly says to proceed without more questions, still produce a compact specification and ask for one final confirmation before writing the final skill.

## Output Format

Before creation, present:

```text
Skill specification
- Name:
- Destination:
- Purpose:
- Trigger description:
- Non-triggers:
- Required resources:
- Future approval gates:
- Validation:
- Assumptions:

Audit result
- Pass / revise:
- Blocking issues:
- Recommended edits:
```

After creation, present:

```text
Created / updated
- Files:

Validated
- quick_validate.py:
- Script checks:

Remaining notes
- ...
```

## Hub Handling

When working inside this hub, choose the numbered category that owns the new Skill's public contract and keep the Skill directly under that category. For paper-building Skills, use `10-paper-build/<skill-directory>/`; do not recreate a `util_skills/` wrapper. After creating or renaming a Skill, update the category README and both root README indexes with its path, purpose, and validation command.
