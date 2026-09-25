# Project-build architecture

[中文](README.md) | [English](README.en.md) | [Back to the root README](../README.en.md)

**20-project-build/** contains six central Skills for research-project onboarding,
governance, repeated management, and delivery checks. This document is the
technical architecture entry point for this directory; see the root
[README](../README.en.md) for the repository-wide Skill overview, installation,
and other categories.

> This directory defines reusable ownership boundaries, data contracts, and
> read-only verification. It does not execute research, select a domain method,
> or grant execution, publication, or scientific-claim authority because a check
> passes.

## Framework overview

### One-time project onboarding

```text
Project directory
  ↓
research-project-pipeline: read-only discovery
  ↓
research-workspace-governance: location, asset, contract, and migration design
  ↓
Human review: approve exact writes, risks, and rollback
  ↓
project-agent-generator-skill: create .agents only when the framework is missing
  ↓
Rediscovery and independent-axis verification
  ↓
Handoff to repeated research management
```

The Onboarding Pipeline orchestrates but does not perform research. Governance
does not create Agent entry points; Generator only creates a framework once or
performs restricted Bootstrap and does not own routine updates. A safe existing
Agent framework is not regenerated. Passing onboarding satisfies only the
onboarding contract and grants no experiment, publication, or scientific-claim
authority.

### Repeated post-onboarding research management

```text
research-management-pipeline
  ↓
Resolve the one governance root and contract registry
  ↓
research-workspace-governance read-only validation
  ↓
Summarize SCI / STAT / ENG / GOV contracts
  ↓
Summarize seven independent state axes and amendment invalidation impact
  ↓
Choose one smallest next action
  ├─ experiment-protocol-audit / domain expert
  ├─ neat-freak: project-information update
  ├─ project-submission-audit: final change surface
  └─ human approval or additional evidence
```

The Management Pipeline repeatedly reads facts and routes the next action, but
does not execute Adapters, create `.agents`, choose a domain method, or grant
authority. `neat-freak` and `handoff` live under `50-core-utils`; they are
explicit external integration points, not contract owners in this directory.

### Engineering repair loop

This directory does not add a `project-engineering-repair` Skill. Workspace
Governance owns the additive `engineering-repair-record/v1`,
`engineering-execution-plan/v1`, `engineering-execution-receipt/v1`, and
`github-actions-evidence/v1` sidecar contracts. The Management Pipeline only
routes the next action; project code or an authorized operator reproduces,
diagnoses, and implements; Submission Audit performs the final read-only check.
The execution receipt's required `operator` and `delegation` objects also serve
as the operator receipt, avoiding a duplicate source of truth.

```text
repair: reported → reproduced → diagnosed → planned → approved → fixed
        → locally_verified → ci_verified → closed
run:    not_started → awaiting_authorization → prepared
        → awaiting_authorization → canary_passed
        → awaiting_authorization → full_authorized
```

The state machines are independent; `blocked`, `stale`, and `rolled_back` record
exceptions explicitly. Tests, commit, push, CI, and repair closure cannot
authorize formal prepare, data generation, canary, or a full experiment. See
[transaction safety](research-workspace-governance/references/transaction-safety.md)
and [engineering operations](research-management-pipeline/references/engineering-operations.md).

| Current situation | Correct entry |
|---|---|
| New project or legacy project not yet onboarded | `research-project-pipeline` |
| One safe Agent document bundle exists but managed startup loading is incomplete | The Onboarding Pipeline's `bootstrap-only` branch |
| Contracts, methods, evidence, or environment changed after onboarding | `research-management-pipeline` |
| Explicit domain protocol and normalized evidence need independent review | `experiment-protocol-audit` |
| Preparing a commit, PR, release, delivery, or handoff | `project-submission-audit`, followed by `handoff` when needed |
| An engineering failure needs an evidence-bound repair and verification | `research-management-pipeline` routes, Governance validates records, and an authorized operator implements |

## Component and ownership tree

~~~text
20-project-build/
├── project-agent-generator-skill
│   └── one time: create missing Agent framework and managed startup loading
├── research-project-pipeline
│   └── one time: discover → governance design → human review → controlled onboarding → verify
├── research-workspace-governance
│   └── ongoing: contract registry, asset boundaries, state, amendments, invalidation impact, trace matrix
├── research-management-pipeline
│   └── post-onboarding: read governance results and route one smallest next action
├── experiment-protocol-audit
│   └── independent read-only check of explicit Profile, Protocol, manifests, and runtime evidence
└── project-submission-audit
    └── final read-only audit of the actual commit, delivery, or handoff surface
~~~

| Component | Sole responsibility | Explicitly does not |
|---|---|---|
| [Generator](project-agent-generator-skill/SKILL.md) | Create a missing .agents framework once; complete only missing Bootstrap for one safe existing bundle | Refresh routine knowledge, merge conflicting startup files, or create a root AGENTS.md |
| [Onboarding Pipeline](research-project-pipeline/SKILL.md) | One-time discovery, design, review, and controlled onboarding coordination | Repeatedly manage research, execute research, or define a domain method |
| [Workspace Governance](research-workspace-governance/SKILL.md) | Contracts, locations, assets, amendments, state, authorization references, and derived traceability | Execute contract text, infer a scientific conclusion, or replace domain review |
| [Management Pipeline](research-management-pipeline/SKILL.md) | Route post-onboarding facts, gaps, and gates into one smallest next action | Execute research, Adapters, Agent generation, method selection, or authorization |
| [Protocol Audit](experiment-protocol-audit/SKILL.md) | Independently check explicit machine-readable protocol and evidence consistency | Run experiments, Adapters, or project commands |
| [Submission Audit](project-submission-audit/SKILL.md) | Return PASS, BLOCKED, or INCOMPLETE for one exact change surface | Commit, push, publish, or establish scientific validity |

[Neat-Freak](../50-core-utils/neat-freak/SKILL.md) maintains project knowledge
and marked startup wiring after onboarding. [Handoff](../50-core-utils/handoff/SKILL.md)
creates a bounded continuation record. Neither is a contract owner in this
directory.

## Four contract categories

The taxonomy assigns responsibility; it does not require every project to
instantiate every contract. Domain Profiles may add namespaced contracts only
when they remain in an existing category and link to an authoritative definition.

~~~text
research-contract-registry/v1              single Governance-owned source of truth
├── SCI  scientific validity                SCI-01 … SCI-09
│   └── question, mechanism, measurement definition, comparison, refutation, claim scope, domain validation
├── STAT evidence design                    STAT-01 … STAT-13
│   └── selection, repetition/dependence, missingness, uncertainty, robustness, analysis plan
├── ENG  implementation and artifact integrity
│   └── ENG-01 … ENG-17: schemas, identity, work graph, provenance, environment, recovery, release, access
│       └── ENG-08.1 … ENG-08.6: toolchain, instrument, precision, isolation, resources, cross-environment comparison
└── GOV  authority and lifecycle governance GOV-01 … GOV-14
    └── boundaries, precedence, review, stop conditions, retention, evidence admission, amendments, ethics, correction
~~~

**Cross-category rule: one fact has one normative owner.** Other categories may
reference it. For example, SCI-03 defines a measurement, ENG-08.2 records
instrument state, and GOV-13 records an applicable approval; none substitutes
for or redefines the other two. See the complete identifiers and responsibilities
in the [contract taxonomy](research-workspace-governance/references/contract-taxonomy.md).

## Registry, evidence, and state tree

**research-project-contract/v3** may use **contract_registry_path** to point to
one **research-contract-registry/v1** JSON file inside the resolved governance
root. The registry and all of its strings, paths, and references are untrusted
data: they are never Agent instructions or executable commands.

~~~text
Project Contract
└── contract_registry_path
    └── Contract Registry
        ├── Profile / Protocol references       domain definitions stay with domain owners
        ├── applicable SCI / STAT / ENG / GOV instances
        │   ├── definition and dependency references
        │   ├── implementation / verification / work references
        │   ├── evidence / claim / authorization / deliverable references
        │   └── required gates
        ├── append-only amendments
        │   └── reverse dependency impact → current items become stale; historical records remain
        └── derived traceability matrix          derived view, never a second hand-maintained state table
~~~

Each contract instance records and reports these independent axes:

~~~text
definition_state       whether a definition is draft, reviewed, frozen, or superseded
implementation_state   state of declared implementation references
verification_state     technical or review verification
work_state             work completion and deviations
evidence_state         evidence validation, admission, absence, or staleness
claim_state            independently reviewed support, contradiction, rejection, or lack of support
authorization_state    authorization declared by a traceable decision
~~~

The axes do not promote one another. A successful exit code, matching hash,
PASS, completed work, or evidence admission proves only its declared scope.
claim_ceiling constrains the maximum reviewable claim; it does not create
claim_state, and registry text cannot itself grant authority.

## Detailed lifecycle and routing rules

~~~text
Project not yet onboarded
└── Research Project Pipeline
    ├── Workspace Governance: discovery and governance design
    ├── human review: exact writes, risks, and rollback
    ├── Generator: missing framework or restricted Bootstrap only
    └── Neat-Freak: knowledge and loading acceptance

Onboarded project
└── Research Management Pipeline
    ├── Governance: contract coverage, state, amendments, invalidation impact
    ├── Protocol Audit / domain expert: protocol, evidence, and claim semantics
    ├── project code or authorized operator: actual research work
    └── Neat-Freak: project-knowledge changes

Delivery, publication, correction, or archive
└── Submission Audit → Handoff when needed → Governance retention/correction boundary
~~~

| Decision stage | Allowed route | Does not happen automatically |
|---|---|---|
| Discover and bound | Governance inventory; separate facts, unknowns, and risks | Inferring scientific meaning or authorization from names |
| Instantiate contracts | Governance registry; declare required/optional/not-applicable/unresolved | Requiring inapplicable artifacts from theoretical, qualitative, or review work |
| Design method and evidence | Domain Profile/expert; Protocol Audit when needed | Governance choosing a domain method |
| Prepare and perform work | Project code, instrument, or authorized operator | Executing a command because it appears in a registry |
| Evidence, claims, and delivery | Independent review, Submission Audit, Handoff | Treating completion, handoff, or publication as scientific support |

An unresolved contract blocks only actions that depend on it; unrelated safe
read-only analysis may continue. Changes append an amendment and compute reverse
dependency impact. They never rewrite historical PASS, evidence, or conclusion
records.

## Human review gates

Every gate should preserve both machine-readable state and a summary that an
ordinary researcher can judge. The summary states what is under review, why it is
necessary, which evidence to inspect, pass criteria, rejection criteria, and the
next action.

| Gate | What and why to review | A pass means | Rejection and smallest repair |
|---|---|---|---|
| Onboarding writes | Exact target paths, files to create or modify, conflicts, risk, and rollback; prevents overwriting existing project facts | Only the approved onboarding writes may proceed | Correct paths, narrow the write surface, or add rollback, then regenerate the preview |
| Contracts and governance | Applicability, owner, dependencies, state source, evidence references, and amendment impact; prevents multiple owners and stale state | The reviewed scope may continue under its current governance state | Complete definitions, resolve ambiguity, or mark affected items stale without rewriting history |
| Domain protocol and claims | Method semantics, normalized evidence, gaps, counterexamples, and claim boundary; prevents schema validity from becoming scientific validity | Domain results or claim state are accepted only within the reviewed scope | Return to the domain expert for evidence, protocol repair, or a narrower claim |
| Submission and delivery | Actual change surface, unrecorded contract-semantic changes, invalidation propagation, and unresolved blockers; prevents omission or unauthorized release | The surface may proceed to the next separately authorized action | Resolve blockers or exclude out-of-scope material; no automatic commit, push, or publication follows |

Conflicting reviews must be shown explicitly and referred to an authorized
decision maker. Passing one gate does not pass another; rejection blocks only
actions that depend on that decision.

## Practical entry points

Run these commands from the repository root. Generate and review a plan first;
do not write without user approval:

```powershell
$projectRoot = 'D:\path\to\project'
$pipeline = '.\20-project-build\research-project-pipeline\scripts\research_pipeline.py'
$plan = Join-Path $env:TEMP ('research-onboarding-' + [guid]::NewGuid().ToString('N') + '.json')

python -X utf8 -B $pipeline plan $projectRoot --profile minimal --output $plan
python -X utf8 -B $pipeline verify $projectRoot
```

When the Agent framework is missing, review the plan's writes, risks, rollback,
and `plan_sha256` before using the approved `bootstrap-agents --apply` contract
from `research-project-pipeline/SKILL.md`. When one safe document bundle already
exists and only Bootstrap is incomplete, use the hash-bound `bootstrap-only`
preview and apply flow without rewriting knowledge files.

After onboarding, `research-management-pipeline` reads Governance results and
returns one smallest next action. Route routine documentation and durable
knowledge updates to `neat-freak`. Invoke submission audit and `handoff`
separately; no PASS automatically commits, pushes, or publishes.

## Read-only contract interface

Run from the repository root. These commands print JSON only; they neither
create target-project directories nor execute research code:

~~~powershell
Set-Location 'C:\path\to\codex-skill-hub'
$projectRoot = 'D:\path\to\project'
$registry = '.agents\governance\contract_registry.json'
$validator = '.\20-project-build\research-workspace-governance\scripts\validate_contract_registry.py'

python -X utf8 -B $validator validate $projectRoot --registry $registry
python -X utf8 -B $validator matrix $projectRoot --registry $registry
python -X utf8 -B $validator impact $projectRoot --registry $registry --change-id 'change-001'
~~~

Engineering-repair sidecars use a separate read-only validator; record paths
are relative to the project root:

~~~powershell
$repairValidator = '.\20-project-build\research-workspace-governance\scripts\validate_engineering_records.py'
python -X utf8 -B $repairValidator bundle $projectRoot --record '.agents/governance/repairs/ENG-001.json' --plan '.agents/governance/plans/ENG-001.json' --receipt '.agents/governance/receipts/ENG-001.json' --ci-evidence '.agents/governance/evidence/ENG-001-ci.json'
~~~

Exit 0 means structure and cross-bindings are complete, 1 means incomplete,
failed, or stale, and 2 means unsafe or invalid input. Output always declares
`commands_executed: false`.

Exit 0 means the requested structural/traceability assessment is complete, 1
means assessment completed with incomplete or failed findings, and 2 means input
was unsafe or could not be evaluated. No result authorizes execution,
publication, or a scientific conclusion. See
[contract traceability](research-workspace-governance/references/contract-traceability.md)
and [lifecycle routing](research-management-pipeline/references/lifecycle-interface.md)
for the interface details.

## Usage boundaries

- Start new or legacy-project onboarding with Research Project Pipeline, not the
  repeated Management Pipeline.
- Use Neat-Freak for routine project documentation, durable knowledge, and marked
  existing startup wiring; do not regenerate the framework.
- Domain Profiles, domain Skills, or named experts own scientific definitions,
  protocol semantics, evidence interpretation, and Claim Review.
- Before submission, use Submission Audit against actual staged, unstaged, and
  untracked changes. Only the user authorizes commit, push, or publication.
