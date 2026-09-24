# Personal Skills

[中文](README.md) | [English](README.en.md) | [Back to the root README](../README.en.md)

`90-personal/` stores Skills adapted over time to an individual's learning style. Its only active source is currently [`logic-chain-tutor`](logic-chain-tutor/SKILL.md). It is not part of the project-governance or paper-delivery pipelines and does not automatically modify an external learning profile.

## Overall framework

```text
Current point of confusion
  ↓
Identify the actually missing prerequisite
  ↓
Known anchor → missing bridge → target concept
  ↓
Minimal complete example / derivation / counterexample / comparison
  ↓
Check understanding and continue only as needed
```

## When to use

- An unfamiliar concept, symbol, equation, or paper method is blocking progress.
- A key foundation was forgotten and the learner needs a bridge from the current gap rather than a full course restart.
- Mathematical objects, operations, and physical meanings are easy to confuse.
- A detailed derivation, concrete example, counterexample, or complete review is requested.

Simple fact lookup, pure translation, or tasks that only require execution should not trigger the teaching workflow. When the user requests a short answer, hint only, local explanation, or length limit, that output contract takes precedence over the default depth.

## Responsibility boundaries

- Adapt within the current conversation without inferring a personal profile from unapproved external material.
- Do not treat analogy as proof or add mechanisms absent from the real concept.
- Do not merge conceptual similarity, numerical approximation, implementation equivalence, and theoretical equivalence.
- Do not replace domain experiments, project execution, or scientific-claim review.

## Usage entry

> Use `logic-chain-tutor` to explain this topic. Start from the exact step where I am stuck, show the logic map first, then explain the symbols, operations, reasons, and physical meaning step by step, and verify them with one minimal complete example.

See [`logic-chain-tutor/SKILL.md`](logic-chain-tutor/SKILL.md) for the detailed teaching contract, output modes, and safety boundaries.

## Verification

Run from the repository root:

```powershell
python -X utf8 -B "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" ".\90-personal\logic-chain-tutor"
```
