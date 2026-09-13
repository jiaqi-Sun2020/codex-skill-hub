# Research Lifecycle Governance

Use this reference to manage a research project across inception, execution, synthesis, handoff, and archive. It governs decisions and evidence; it does not choose domain-specific scientific methods or replace required ethics, safety, quality, laboratory, clinical, or regulatory systems.

## Inception

Record a compact charter:

```text
research objective and decision context
research questions or hypotheses
scope and exclusions
evidence and acceptance standard
exploratory, confirmatory, or operational status
stakeholders, roles, and decision owner
ethical, legal, safety, access, and licensing constraints
resources, schedule, and stopping conditions
expected deliverables and archive horizon
```

Separate a scientific target from a delivery target. “Produce a report” is a deliverable; it is not the research question or evidence standard.

## Planning

Break work into independently verifiable work packages. For each package, record:

```text
work_id | objective | owner | inputs | method/protocol
dependencies | expected evidence | validation | status
risks | next decision | completion condition
```

Use milestones only for meaningful state transitions such as protocol frozen, acquisition complete, data locked, analysis validated, claim review complete, release published, or archive verified. Avoid percentage-complete estimates when the remaining uncertainty is not quantifiable.

Maintain a risk register proportional to the project. Include scientific validity, data loss/corruption, provenance gaps, access/privacy, environment drift, resource limits, dependency failure, and schedule risks when applicable. Assign an owner and mitigation or acceptance decision.

## Execution and change control

- Give each acquisition, observation batch, analysis, simulation, or coding round a stable identity.
- Record material decisions with context, alternatives, rationale, evidence, owner, date, and consequences.
- Record protocol or analysis deviations when they occur. State whether they affect exploratory/confirmatory status, comparability, exclusions, or claims.
- Keep unexpected, null, contradictory, and failed results discoverable. Failure evidence may prevent repeated work or unsupported conclusions.
- Update status from observable evidence, not optimism. “Complete” means its stated completion condition and validation passed.
- Do not rewrite earlier records to make the project appear linear. Supersede them with linked corrections.

## Synthesis and claim control

Maintain a claim-evidence map for conclusions that will guide a decision or appear in a formal deliverable:

```text
claim_id
claim text and scope
supporting artifact/version
method/protocol version
population, conditions, or domain of validity
uncertainty and limitations
contradictory evidence
review status and reviewer
deliverables using the claim
```

Distinguish observation, derived result, interpretation, hypothesis, recommendation, and decision. A polished figure or report does not strengthen weak evidence. If evidence was reused during method development, label the resulting claim accordingly rather than presenting it as independent confirmation.

## Review gates

Use only gates justified by the project:

1. **Scope ready:** question, boundaries, evidence standard, ownership, and constraints are explicit.
2. **Protocol ready:** method, inputs, exclusions, validation, and deviation handling are reviewable.
3. **Execution ready:** storage, identities, environment/instrument state, logging, backup, and recovery are adequate.
4. **Evidence ready:** outputs are complete, provenance-bound, validated, and limitations recorded.
5. **Claim ready:** claim-evidence links survive adversarial review and distinguish exploratory from confirmatory support.
6. **Release ready:** deliverable, editable source, manifest, approvals, and archive are complete.

Do not mark a gate passed from a checklist alone; cite the evidence that satisfies it.

## Handoff

A useful handoff states:

- objective, current status, and next decision;
- active protocol and approved deviations;
- canonical source, derived, run, and deliverable identifiers;
- completed and failed work with validation state;
- unresolved questions, risks, and assumptions;
- exact next action, owner, prerequisites, and stopping condition;
- access restrictions and recovery/restore instructions.

Prefer links or stable identifiers over copying mutable facts into multiple handoff documents.

## Closure and archive

- Freeze or version the final claim-evidence map and released deliverables.
- Record what was not answered and why the work stopped.
- Archive required source records, methods, environments or environment specifications, run evidence, decisions, deviations, and approvals.
- Verify integrity, access, restore procedure, ownership, and retention schedule.
- Separate superseded evidence from disposable temporary material; archived does not mean abandoned or safe to delete.
