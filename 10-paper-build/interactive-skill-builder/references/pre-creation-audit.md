# Pre-Creation Audit

Run this audit after drafting the skill specification and before creating or updating the final skill.

## Audit Checklist

### Scope

- The skill has one clear primary purpose.
- The skill is not a vague collection of unrelated advice.
- Non-triggers are clear enough to avoid accidental activation.
- If multiple workflows exist, they share a domain and output contract.

### Name and Trigger

- The `name` uses lowercase letters, digits, and hyphens only.
- The name is under 64 characters.
- The folder name matches the skill name unless the local bundle has a clear convention.
- The frontmatter `description` explains both capability and trigger situations.
- The description includes important file types, task phrases, or user intents that should activate the skill.

### Resource Plan

- `SKILL.md` contains only core routing and workflow instructions.
- Detailed question banks, schemas, long examples, or policies are in `references/`.
- Deterministic repeated operations are in `scripts/`.
- Reusable output files or boilerplate are in `assets/` or the local template folder.
- No unnecessary README, changelog, installation guide, or quick reference is added.

### Author Approval

- The future skill says when to ask the author for input.
- Risky actions require explicit approval.
- The creation/update plan itself has been approved before final files are written.
- Assumptions are visible and can be corrected by the author.

### Validation

- `quick_validate.py` will run on the final skill folder.
- Added scripts have syntax or smoke tests.
- Referenced files exist.
- `agents/openai.yaml`, if present, uses valid quoted strings and a default prompt that names the skill with `$skill-name`.

## Blocking Issues

Treat these as blockers:

- No concrete trigger examples.
- No destination path.
- Name does not follow skill naming rules.
- Skill scope mixes unrelated domains without a routing structure.
- Skill requires external actions but has no approval gate.
- Validation command is unknown or impossible to run.

## Approval Packet

Before creating the skill, present this packet:

```text
Pre-creation audit
- Scope: pass / revise
- Name and trigger: pass / revise
- Resource plan: pass / revise
- Author approval gates: pass / revise
- Validation plan: pass / revise

Blocking issues:
- None / ...

Ready to create:
- yes / no
```

Only proceed after the author explicitly approves the audited specification.
