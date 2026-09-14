---
name: research-project-pipeline
description: Orchestrate safe onboarding or integration of a new or legacy research project through read-only discovery, research-workspace design, reviewed migration, project-local agent-context generation or preservation, knowledge/bootstrap audit, and adversarial verification. Use when the user wants the complete research setup pipeline rather than either component Skill alone. Do not use for ordinary research work, isolated .agents generation, or a workspace-only audit.
---

# Research Project Pipeline

Coordinate the independent `research-workspace-governance` and
`project-agent-generator-skill` capabilities without absorbing their ownership.
The governance Skill remains usable alone for research architecture and artifact
lifecycle work. The generator remains usable alone for `.agents`, project
knowledge, and Codex bootstrap work.

## Required order

1. **Preflight and discover, read-only.** Read active project instructions. Run
   the pipeline plan interface to collect both component inventories. Do not
   create `.agents` merely to hold a draft architecture.
2. **Design under research governance.** Use `research-workspace-governance` to
   classify artifacts, select a proportional profile, and propose the target
   architecture, lifecycle, retention, migration, and verification contracts.
3. **Review gate.** Present exact create/move/update/delete sets, collisions,
   protected paths, rollback, and the inventory fingerprint. No approval means
   no project mutation.
4. **Apply the approved framework.** Preserve source records and existing owner
   material. For legacy projects, prefer mapping and incremental adoption over
   wholesale relocation. Do not automate deletion.
5. **Refresh the snapshot.** Rerun the read-only plan after framework changes.
   A pre-change fingerprint must never authorize a post-change write.
6. **Generate project context.** Invoke `project-agent-generator-skill` only
   after the actual architecture is stable. The pipeline may create a missing
   default `.agents`; it never passes `--force`. Preserve an existing `.agents`
   or legacy `.agent` bundle and use the generator independently for a reviewed,
   backed-up refresh. Treat both names existing together as an ambiguity that
   requires an owner decision.
7. **Audit context and loading.** Use `neat-freak` when available to audit the
   memory index, Codex bootstrap, and declared mandatory-policy reachability
   across nested execution roots. Findings do not authorize repair.
8. **Adversarial verification and handoff.** Use the governance Skill's distinct
   scope, traceability, failure/deletion, usability, policy-reachability, and
   equivalence/inference passes when applicable. Compare actual state with the
   approved plan, then report residual risks and next action.

Read [references/stage-contracts.md](references/stage-contracts.md) before an
apply or resume. Read
[references/legacy-integration.md](references/legacy-integration.md) for an
existing project with owner files, `.agents`, or legacy `.agent` context.

## Deterministic support interface

Run commands from this Skill directory.

Create a read-only pipeline plan on stdout:

```powershell
python -X utf8 .\scripts\research_pipeline.py plan D:\path\to\project --profile collaborative
```

When nested execution roots or scientific-equivalence claims are in scope, pass
project-contained declarations. Read
[references/policy-topology.md](references/policy-topology.md) and
[references/policy-topology.schema.json](references/policy-topology.schema.json)
and the governance Skill's `references/equivalence-contract.md` before authoring
them:

```powershell
python -X utf8 .\scripts\research_pipeline.py plan D:\path\to\project --policy-topology .agents\policy-topology.json --equivalence-records governance\equivalence-records.json
```

The pipeline discovers execution roots even without a topology declaration. It
does not guess which prose is mandatory. Nested roots without a declaration are
conditional, not verified.

Write the plan outside the target project:

```powershell
python -X utf8 .\scripts\research_pipeline.py plan D:\path\to\project --profile collaborative --output D:\safe\research-pipeline-plan.json
```

Preview missing `.agents` generation after the framework is stable:

```powershell
python -X utf8 .\scripts\research_pipeline.py bootstrap-agents D:\path\to\project
```

Creation requires the exact reviewed plan hash. The command refuses an existing
`.agents` or `.agent` and never uses `--force`:

```powershell
python -X utf8 .\scripts\research_pipeline.py bootstrap-agents D:\path\to\project --apply --plan D:\safe\research-pipeline-plan.json --confirm-plan-sha256 PLAN_SHA256
```

Verify without writing:

```powershell
python -X utf8 .\scripts\research_pipeline.py verify D:\path\to\project
```

The script is support tooling, not an autonomous migration engine. It will not
invent the research objective, apply a semantic workspace plan, move legacy
files, delete artifacts, refresh existing `.agents`/`.agent` context, or resolve audit
findings. Those remain explicit Agent/user decisions under the component Skills.
It also does not prove scientific equivalence: the governance validator checks
typed declarations and evidence metadata supplied by domain protocols.

## Stop conditions

Stop before mutation when the scan is truncated or materially unreadable, the
project fingerprint changed after review, an output path crosses a link or the
approved root, an existing `.agents`/`.agent` would be replaced, secrets or restricted
records may be exposed, a migration collision is unresolved, or the requested
action exceeds the approved plan.

Completion requires a stable architecture, generated or explicitly preserved
project context, clean or owner-accepted audits, a verified evidence lifecycle,
and a self-contained handoff. Folder creation alone is not completion.
