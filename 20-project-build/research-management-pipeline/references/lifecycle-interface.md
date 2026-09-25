# Research Management Lifecycle Interface

This is an iterative decision map, not a requirement to create one file or ask
for one approval at every step.

| Decision | Minimum input | Route | Completion evidence |
|---|---|---|---|
| Discover and bound | objective, current sources, unknowns, risks, authority | Governance inventory | facts and unresolved items are separated |
| Instantiate contracts | applicable taxonomy, Profile/Protocol, owners | Governance registry | required/optional/not-applicable/unresolved decisions are traceable |
| Design method and evidence | scientific definition, evidence units, comparisons, stopping and missingness policy | Domain owner plus Protocol Audit where machine rules apply | reviewed method and explicit limitations |
| Prepare implementation | work graph, environment, identities, provenance, recovery | project implementation plus applicable ENG/GOV reviews | current verification and real authorization preconditions |
| Repair an engineering defect | failure evidence, exact SHA, reproduction, diagnosis, repair state and plan hash | Governance records; authorized project operator implements; Management routes | execution receipt, local verification, exact-SHA CI evidence, and independent closure |
| Perform authorized work | exact scope, inputs, budget, decision reference | project code, instrument, operator, or formal derivation | raw results, events, failures, and deviations retained |
| Validate and synthesize evidence | normalized evidence, provenance, quality and contradiction | Protocol Audit and/or named expert | evidence validation and admission remain distinct |
| Review claims | supporting and contradictory evidence, ceiling, limitations | independent domain reviewer | current claim review with reviewer and evidence references |
| Deliver, correct, or archive | current claim and evidence links, editable deliverable, retention duties | Submission Audit, Handoff, Governance | delivery points to current valid records; notifications need separate authority |

## Routing rules

- Missing Agent scaffolding: return to the one-time onboarding Pipeline; only the
  Generator may create it.
- Changed project information or Agent knowledge: use Neat-Freak independently.
- Contract structure, amendment, status, or traceability: use Governance.
- Profile/Protocol machine checks: use Protocol Audit; Adapter execution remains
  project-owned.
- Scientific adequacy or claim support: use a Domain Skill or named expert.
- Commit, PR, release, delivery, or handoff surface: use Submission Audit, then
  Handoff when continuation is needed.
- Engineering repair: Governance owns records and state; project code or an
  authorized operator owns diagnosis and implementation; Management selects one
  next action. A repair closure never advances scientific-run authorization.

## Independent engineering and run lanes

```text
repair: reported → reproduced → diagnosed → planned → approved → fixed
        → locally_verified → ci_verified → closed

run:    not_started → awaiting_authorization → prepared
        → awaiting_authorization → canary_passed
        → awaiting_authorization → full_authorized
```

`blocked`, `stale`, and `rolled_back` are explicit repair exceptions; `stale` is
also an explicit run state. Code, Profile, campaign, input, or environment drift
invalidates only dependent evidence and routes back to the earliest affected
decision. Read [engineering-operations.md](engineering-operations.md) before any
Git or Actions step.

Every gate summary answers: what is reviewed, why, evidence to inspect, pass and
reject conditions, what becomes allowed, minimum repair, and what remains
unvalidated. Use the user's current language.
