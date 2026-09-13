---
name: skill-audit-refactor
description: Use when Codex needs to review, audit, simplify, refactor, or split an existing Codex skill. Trigger when the user asks whether a skill is too long, too broad, poorly triggered, duplicated, missing resources, should be split into references/scripts/assets, or needs a safer smaller SKILL.md without losing capability.
---

# Skill Audit Refactor

## Purpose

Audit an existing Codex skill and improve it without weakening its practical performance.

Use this skill to:

- review whether a `SKILL.md` triggers correctly;
- remove bloat and duplicated instructions;
- preserve high-value behavior while reducing context cost;
- decide whether content belongs in `SKILL.md`, `references/`, `scripts/`, `assets/`, or another skill;
- produce a clear before/after summary and validation plan.

## Audit Principles

- Preserve capability before reducing length.
- Keep `SKILL.md` focused on trigger-critical workflow and non-obvious rules.
- Move detailed examples, long variants, schemas, or style catalogs into `references/`.
- Move repeated deterministic operations into `scripts/`.
- Move output templates, boilerplate projects, icons, fonts, or sample files into `assets/` or `templates/`.
- Split a skill only when the sub-capabilities have different triggers, workflows, resources, or user intents.
- Do not remove safety, validation, claim-boundary, or output-quality rules merely because they are long.

## Required Review Steps

### 1. Inventory

Read the target skill completely:

- frontmatter `name` and `description`;
- body sections;
- referenced files;
- scripts, references, assets, templates;
- `agents/openai.yaml` if present.

Record:

```text
Skill name:
Current purpose:
Main triggers:
Resources:
Approximate size:
Obvious risks:
```

### 2. Trigger Audit

Check whether `description` is specific enough to activate the skill.

Look for:

- missing trigger phrases;
- too many unrelated trigger contexts;
- vague phrases such as "helps with things";
- mismatch between frontmatter and body;
- naming inconsistency between folder and `name`;
- forbidden or fragile metadata characters.

Improve the description only when it helps discovery.

### 3. Scope Audit

Classify the skill as one of:

```text
Single-purpose: one clear workflow.
Multi-mode: one domain with several output modes.
Overloaded: multiple unrelated workflows.
Resource-heavy: mostly references/templates/scripts.
```

If overloaded, decide whether to split.

### 4. Bloat Audit

Mark content as:

- **Keep**: trigger-critical workflow, hard constraints, quality checks.
- **Compress**: repeated explanations, verbose examples, long prose.
- **Move**: detailed variants, schemas, style catalogs, large examples.
- **Delete**: stale TODOs, duplicate sections, generic advice Codex already knows.

Prefer concise rules over long explanations.

### 5. Split Decision

Recommend splitting only if at least two are true:

- different user intents would trigger different subsets;
- sections require different resources or tools;
- one part is large but rarely needed;
- parts have different output contracts;
- one part can be reused independently by other skills;
- the current description must be vague to cover everything.

Do not split merely because the file is long. A single coherent workflow can remain one skill if it is clearer that way.

Use this decision format:

```text
Split decision: keep together / split / move details to references
Reason:
Proposed structure:
Risk if not split:
Risk if split:
```

### 6. Refactor Plan

Before editing, state:

```text
Preserve:
Compress:
Move:
Delete:
Validate:
```

If editing files, keep changes scoped to the target skill unless the user asks to update indexes or README files.

## Refactor Rules

- Keep frontmatter minimal: `name` and `description`.
- Keep the body under 500 lines when feasible.
- Use imperative instructions.
- Avoid auxiliary docs such as `CHANGELOG.md`, `QUICK_REFERENCE.md`, or extra README files unless the user explicitly asks.
- Do not duplicate the same rule in several sections.
- Keep examples short and directly reusable.
- Keep quality checklists short but enforceable.
- Preserve all critical edge cases discovered from user feedback.

## Output Format

When auditing without editing, report:

```text
Findings
- Severity, location, issue, recommendation.

Split Assessment
- Decision and rationale.

Slimming Plan
- Keep / compress / move / delete.

Validation
- Commands or checks to run.
```

When editing, report:

```text
Changed
- Files updated.

Preserved
- Capabilities kept.

Reduced
- Size or duplication removed.

Split Decision
- Whether split is needed.

Validation
- Results from quick_validate.py and any relevant checks.
```

## Validation

After editing a skill, run:

```text
python path-to-skill-creator/scripts/quick_validate.py path-to-skill
```

Also check:

- `name` matches lowercase hyphen rules;
- `description` captures the real trigger;
- referenced files exist;
- no required behavior was removed;
- README or skill index is updated if the user asked for synchronization.

## One-Sentence Summary

Audit skills like compact operating manuals: keep the trigger, workflow, resources, and quality gates strong while removing everything that does not help future Codex runs.
