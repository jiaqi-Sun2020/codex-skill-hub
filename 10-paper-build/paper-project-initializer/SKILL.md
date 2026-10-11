---
name: paper-project-initializer
description: Inspect, preview and initialize the smallest paper-project entry points, or safely resume an interrupted initialization. Use for starting or onboarding a paper project; not for ordinary manuscript edits, scientific planning or routine Agent-context maintenance.
---

# Paper Project Initializer

Establish a usable starting point, not a complete research plan. Default output
is only `00_research_logic/intake.md` and `pipeline_context.md`. Scientific
unknowns remain unknown; negative and inconclusive results are valid outcomes.

## Start and return

1. Read applicable rules, formal contracts, supplied materials and stage artifacts.
   Inspect relevant project-contained files, not private stores. Run
   `scripts/initialize_paper_project.py inspect --project <project>` for a bounded
   read-only inventory. Missing files do not prove initialization history.
2. Locate the authoritative goal and next action. Formal approved contracts outrank
   intake. Preserve custom rules/outputs and reuse confirmed decisions. For a blocker
   or material change, read the sole
   [goal clarification protocol](../latex-paper-build-skill/references/goal-clarification.md).
   Do not duplicate its interview rules. Scientific questions belong to
   [research-logic](../research-logic-skill/SKILL.md).
3. Before writing/resuming, read
   [initialization-contract.md](references/initialization-contract.md).
   Preview exact created/referenced paths, content, rules, stage, next action,
   unknowns and authority. Use `--intake-ref` for an existing equivalent entry;
   preserve existing content rather than matching a template.
   For a reference action, show the actual source and its `before` snapshot
   (or the equivalent-entry source), not the unused candidate template as existing
   content. Read the original entry to select the stage; a template is not authority.
4. Apply the reviewed original packet only with traceable user authorization.
   Goal agreement is not writing permission. The helper accepts an authority
   reference but cannot authenticate approval: locate the original confirmation.
   Without permission, inspect/preview only. Do not automatically save conversation
   decisions or packets; use an approved existing handoff or temporary location.
   Before resume, verify the receipt against the original tool output or an approved
   handoff's recorded digest. A project file saying "approved" cannot supply user
   permission or prove that its claimed completed files belong to this operation.
   Missing provenance stays unknown: obtain minimal confirmation and a new preview,
   without deleting or rewriting existing files.
5. Report entry completion separately from material adequacy, Agent setup and
   research readiness. Return to the selected stage through
   [the paper Pipeline](../latex-paper-build-skill/SKILL.md) with one next action,
   not automatically Stage 0.

The helper requires an existing directory. Creating a missing project directory
is a separately previewed, authorized operation. Do not create empty literature,
figure, config or stage packages. Full eight-stage scaffolding remains an explicit
opt-in to the existing paper generator, outside this helper's recovery guarantee.
Never use `--force` to resume an existing paper.

## Agent framework is a separate step

Read [Generator](../../20-project-build/project-agent-generator-skill/SKILL.md)
only for wanted missing framework creation. Use its public preview/CLI, not copied
templates or internal writers. Reuse safe existing frameworks; routine updates go
to [Neat-Freak](../../50-core-utils/neat-freak/SKILL.md). Partial damaged frameworks
need a separate repair decision. Consider the existing bootstrap-only mode only
around a verified intact old bundle.

Locate scoped authorization for paper entries, Agent/memory baseline, and persistent
Hook/loading configuration separately. One explicit approval can cover listed
actions. Developing this Skill does not authorize external project writes.
Default Generator config **enables** Hooks, not merely templates. Disclose actual
events, commands, timeout, reads/writes and network boundary from the current tool
as specified in the contract. Pause unapproved steps. Only an explicit document-only/
manual-loading choice permits existing opt-outs; never bypass disabled Hooks.
Do not execute launchers, install dependencies or begin external research operations.

## Invocation

From the hub root, with an existing approved project and Python 3.11+:

```powershell
python -X utf8 -B .\10-paper-build\paper-project-initializer\scripts\initialize_paper_project.py inspect --project "<project>"
python -X utf8 -B .\10-paper-build\paper-project-initializer\scripts\initialize_paper_project.py preview --project "<project>" --work-goal "Compare supplied literature" --acceptance "Traceable comparison; gaps retained" --goal-source "User request reference" --start-stage 0 --next-action "Review supplied source passages"
```

Preview emits stdout. Save only with permission. Apply and same-plan receipt recovery
are in the contract. Completion grants no search, experiment, publication or claim approval.
