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

## Lifecycle and routing

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
