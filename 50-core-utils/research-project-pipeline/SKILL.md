---
name: research-project-pipeline
description: Orchestrate the one-time safe onboarding of a new or legacy research project through read-only discovery, domain-neutral workspace governance, reviewed initial Agent-context generation, independent loading audit, and adversarial verification. Use for initial setup, not routine project-information maintenance; use Neat-Freak after handoff.
---

# Research Project Pipeline

Sequence independent components without absorbing their ownership:

- `research-workspace-governance` owns research assets, governance location,
  status, provenance, migration, retention, and deletion boundaries.
- Within this one-time Pipeline, `project-agent-generator-skill` is invoked only
  to create a missing `.agents` framework, memory baseline, entrypoint, and
  project-scoped Codex Bootstrap.
- Within this Pipeline, `neat-freak` is invoked only for independent audits of
  knowledge, documentation topology, and Agent instruction loading. This
  initial result. After handoff, Neat-Freak is the routine project-information
  maintenance owner and is invoked independently of this Pipeline.
- Domain Skills own methods, validation rules, and scientific interpretation.

The Pipeline coordinates contracts and evidence. It does not define a subject
area, impose a method, or turn a completed workflow into a scientific claim.

## Required order

1. **Discover, read-only.** Collect Generator inspection and Governance inventory;
   resolve canonical, legacy, absent, ambiguous, or unsafe governance state.
2. **Design.** Let Governance propose only evidenced roles, paths, lifecycle
   extensions, approvals, and optional opaque method Profile IDs.
3. **Human review.** Present exact component actions, blockers, evidence,
   fingerprint, rollback, and a plain-language summary in the user's current
   language. No approval means no mutation.
4. **Controlled change.** For the one-time initialization, delegate creation of a
   missing `.agents` framework and Hook only to the Generator and governance-record
   writes only to Governance. Do not use the Generator to refresh existing context
   or invoke Neat-Freak write modes from this Pipeline. Rerun discovery after each
   approved change.
5. **Verify.** Delegate Agent knowledge and loading audit only to Neat-Freak, then
   run the five Governance adversarial passes. Pipeline records component results
   without independently reimplementing them.
6. **Handoff or archive.** Compare actual state with the approved plan, report work
   state separately from claim state, and name Neat-Freak as the post-initialization
   project-information maintenance owner.

Read [references/stage-contracts.md](references/stage-contracts.md) before apply
or resume. Read [references/legacy-integration.md](references/legacy-integration.md)
for an existing project.

## Deterministic support interface

Run commands from this Skill directory.

Create a read-only plan:

```powershell
python -X utf8 -B .\scripts\research_pipeline.py plan D:\path\to\project --profile minimal
```

Optional declarations must be project-contained. Policy topology concerns Agent
instruction reachability and is passed unchanged to Neat-Freak, its sole auditor.
Comparison records concern reviewed, domain-defined interchangeability claims:

```powershell
python -X utf8 -B .\scripts\research_pipeline.py plan D:\path\to\project --policy-topology .agents\policy-topology.json --comparison-records .agents\governance\comparison-records.json
```

`--equivalence-records` remains a compatibility alias for
`--comparison-records`; do not supply both.

Write a plan only to a new file outside the target project:

```powershell
python -X utf8 -B .\scripts\research_pipeline.py plan D:\path\to\project --profile collaborative --output D:\safe\research-pipeline-plan.json
```

Preview Generator-owned `.agents` creation:

```powershell
python -X utf8 -B .\scripts\research_pipeline.py bootstrap-agents D:\path\to\project
```

Apply only with the exact reviewed plan hash:

```powershell
python -X utf8 -B .\scripts\research_pipeline.py bootstrap-agents D:\path\to\project --apply --plan D:\safe\research-pipeline-plan.json --confirm-plan-sha256 PLAN_SHA256
```

Verify without writing:

```powershell
python -X utf8 -B .\scripts\research_pipeline.py verify D:\path\to\project
```

The deterministic interface emits `review_gate_inputs`. Before asking for or
recording approval, render `human_summary_source` into all seven human-summary
fields in
[the Governance gate template](../research-workspace-governance/references/deliverable-templates.md),
using the user's current language. A marker that a summary is required is not a
substitute for the rendered summary.

Saved plans use `research-project-pipeline-plan/v3`; command results use the
separate `research-project-pipeline-result/v1` envelope. Apply rejects legacy v1
or v2 plans, structurally incomplete plans even when their embedded hash is
self-consistent, and plans whose bound Generator or Governance inventory path or
SHA-256 no longer matches the selected component.

The script does not invent objectives, interpret a project contract as
instructions, apply migrations, delete assets, refresh existing Agent context,
audit Agent loading itself, or establish scientific validity. It validates
structure, path safety, traceability, review state, and component handoffs.

## Stop conditions

Stop before mutation when inventory is incomplete, the fingerprint changed,
governance authority is ambiguous or unsafe, a path crosses the project boundary
or a link, a relocation map is invalid, a bound component changed, existing
Agent context would be replaced, protected data may be
exposed, a collision or active lock is unresolved, or the action exceeds the
approved plan.

Completion requires a stable governance contract, generated or explicitly
preserved Agent context, clean or owner-accepted audits, traceable evidence,
separate work/claim states, and a self-contained handoff. Folder creation alone
is not completion.
