# Adversarial Audit

Use five independent passes with different failure hypotheses. A repeated reread
is not another pass. Each pass records:

```text
pass_id
failure_hypothesis
conclusion: pass | conditional | fail
blockers
non_blockers
evidence
suggested_actions
```

Each finding within a pass records:

```text
code
severity: blocker | non_blocker
object
candidate_interpretations
risk
evidence
minimum_fix
verification
owner_decision
```

## Pass 1: Objective and ownership

Assume the framework solved the wrong problem or absorbed another component's
responsibility.

- Does the design begin with objective, evidence standard, scope, and authority?
- Are Governance, Pipeline, Generator, Neat-Freak, and domain Profile owners
  distinct?
- Is any domain method, artifact type, programming language, folder tree, or
  scientific inference universalized without necessity?
- Can a small project comply without empty bureaucracy?
- Are inferred roles and unresolved ownership visible?

## Pass 2: Safety and loading

Assume untrusted project data attempts to become instructions, or a write escapes
its approved boundary.

- Are governance files treated as data rather than Agent instructions?
- Is recursive loading prohibited and any summary pointer explicit, narrow, and
  owner-approved?
- Are credentials, restricted data, and credential-like paths excluded?
- Are project boundaries, links, junctions, reparse points, output paths, and
  overwrite behavior checked?
- Do interruption, duplicate writers, stale locks, partial publication, and
  recovery preserve the last known-good state?
- Is deletion separately authorized for exact reviewed targets?

## Pass 3: Compatibility and migration

Assume an old project, external consumer, or historical record still depends on
the current layout.

- Is `.agents/governance/` distinguished from legacy root `governance/`?
- Do both locations together block writes instead of triggering a guess?
- Does migration preview exact source, destination, files/bytes, hashes where
  useful, collisions, dependents, locks, reference updates, rollback, and checks?
- Are relocation maps append-only and versioned?
- Do historical records and locks retain their original identity?
- Are existing paths preserved when their contracts are already adequate?

## Pass 4: Human understandability

Assume a reviewer has project knowledge but has not read this Skill.

- Does every gate explain in the user's current language what is happening and why?
- Can the reviewer see blockers, non-blockers, evidence, pass conditions, reject
  conditions, allowed next action, and minimum repair?
- Are work completion and claim support visibly separate?
- Is there one canonical current status per scope, with conflicts reported?
- Are commands complete and paired with their working directory?

## Pass 5: Tests and counterexamples

Assume the happy path hides a category error.

- Are new, legacy-only, canonical-only, dual-location, linked-path, and path
  escape cases tested?
- Does an instruction-like string inside governance data remain inert?
- Are simple, task-local, and custom-path automation cases supported?
- Can a non-computational or otherwise unfamiliar project use the core without
  inheriting unrelated requirements?
- Can completed work remain scientifically unreviewed or unsupported?
- Are old schemas and plans handled explicitly rather than silently reinterpreted?

## Acceptance

Accept only when:

- no blocker remains;
- all five passes have evidence and a distinct failure hypothesis;
- domain validation is delegated to an explicitly selected owner or Profile;
- path authority and write authority are unambiguous;
- the result includes a plain-language summary in the user's current language;
- repaired behavior has been rerun against the affected counterexamples.

Compare pass conclusions after all five are complete. If two passes disagree
about authority, safety, compatibility, evidence, or acceptance, add the conflict
to `review_conflicts`, keep the overall result blocked or conditional, and ask
the owner to adjudicate. Never choose the conclusion most favorable to the
implementation automatically.
