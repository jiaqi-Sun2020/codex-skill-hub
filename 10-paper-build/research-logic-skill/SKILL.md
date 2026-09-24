---
name: research-logic
description: Use when combining two research methods, models, theories, or mechanisms and needing to diagnose shallow module stacking, find a mechanism-level connection, reconstruct state-transition or principle-level integration, and write disciplined paper claims. Do not use for implementation-only coding unless the user asks for research contribution logic.
---

# Research Logic Integration

Help the user turn a possible combination of two research ideas into a deeper, mechanism-level or principle-level integration. This skill is a general research reasoning framework, not a skill for one specific model.

Use QWTA + TGN only as an example when helpful. Do not treat "Hamiltonian QW-TGN" as the skill itself.

## Goal

Guide the user through this reasoning path:

```text
discover a connection point
-> try a direct integration
-> diagnose shallow fusion
-> return to the underlying principle
-> reconstruct the model logic
```

A strong answer should help the user distinguish whether their idea is merely "A + B" or whether one method changes the internal state, dynamics, assumptions, or transition rule of the other method.

## When to Use

Use this skill when the user asks how to:

- combine two research ideas, models, theories, or mechanisms;
- decide whether a proposed combination is meaningful or only a module-level patch;
- find the true mechanism-level connection between two methods;
- transform a direct engineering fusion into a principled formulation;
- build a research narrative from initial intuition to theoretical reconstruction;
- explain why an integration changes a state, dynamic, assumption, or operator rather than only adding a replaceable module.

Example domains include quantum walks with dynamic graph neural networks, physics-inspired models with deep learning, continuous-time dynamics with event-driven neural systems, graph neural networks with differential equations, and memory models with physical evolution operators.

## Integration Levels

Always distinguish these three levels.

### Level 1: Modular Fusion

One method is inserted into another as a replaceable block.

```text
Model A module -> Model B block -> output
```

This can be useful, but it is often shallow.

### Level 2: Mechanistic Fusion

One method changes how the internal mechanism of the other method operates.

```text
internal state -> mechanism-driven transition -> updated state
```

This is usually the strongest practical target for a paper.

### Level 3: Principle-Level Reconstruction

One method's fundamental principle rewrites the core assumption of the other method.

```text
old assumption -> new principle-governed formulation
```

This is the deepest form of integration, but it requires stronger mathematical and experimental support.

## Workflow

Follow these stages in order unless the user asks for a narrower answer.

### 1. Identify the Native Function of Each Method

Do not start by asking where to insert one method into another. First identify what each method fundamentally does.

For each method, determine:

- input and output;
- core internal state;
- update or propagation rule;
- central mathematical object;
- original problem it was designed to solve;
- assumption it makes about the world.

Use this template:

```text
Method A solves: ...
Method A's state is: ...
Method A's transition rule is: ...
Method A's key mathematical object is: ...
Method A assumes: ...

Method B solves: ...
Method B's state is: ...
Method B's transition rule is: ...
Method B's key mathematical object is: ...
Method B assumes: ...
```

Then infer the first possible connection point.

### 2. Find the First Direct Connection Point

The first connection point often appears at an interface such as:

- input representation;
- message function;
- aggregation layer;
- memory state;
- transition rule;
- embedding module;
- decoder;
- loss function;
- physical operator;
- latent dynamics.

State the direct integration without overclaiming.

Use this pattern:

```text
The first natural connection is that Method A provides ___, while Method B needs ___ at the level of ___.
```

### 3. Build the Shallow Version First

Construct the simplest technically valid fusion. Treat this as a diagnostic baseline, not as the final contribution.

The shallow version should clarify:

- where the two models technically connect;
- the minimal implementation;
- what remains unsatisfactory;
- which part of the host model remains unchanged.

Represent it explicitly, for example:

```text
host state -> inserted method/module -> decoder/output
```

### 4. Diagnose Whether the Fusion Is Shallow

Ask:

```text
Does the inserted method change the host model's core assumption or state transition, or does it only replace one module?
```

Treat the fusion as probably shallow if:

- the original state update of the host model is unchanged;
- the new method appears only after the main state has already been formed;
- the new method could be replaced by attention, MLP, GCN, or sum aggregation without changing the conceptual story;
- the explanation says only "we use A to enhance B";
- the claimed mechanism is not tied to a precise mathematical operator, state variable, or transition rule.

Use this warning when appropriate:

```text
At this stage, the combination is technically valid, but it still treats Method A as a replaceable module rather than as a mechanism that changes Method B's internal logic.
```

### 5. Return to the Essence of the Added Method

Do not ask only where the module can be inserted. Ask what mathematical, physical, statistical, or algorithmic principle makes the added method different.

Identify the principle in one sentence:

```text
Method A is not fundamentally ___; it is ___ governed by ___.
```

Example:

```text
QWTA is not fundamentally a neighbor aggregation layer; it is a continuous-time Hamiltonian evolution operator of the form e^{-iHΔt}.
```

### 6. Return to the Weak Point of the Host Method

A deep integration is convincing when the essence of the added method addresses a structural weakness of the host method.

Ask:

- What assumption in the host method feels limited?
- What does the host method fail to model naturally?
- Where does the host method use an engineering workaround?
- Can the added method replace that workaround with a more principled mechanism?

Then state the deeper target:

```text
Use Method A not merely to ___ after the fact, but to define how ___ evolves/updates/transforms inside Method B.
```

### 7. Reconstruct the Model Around the Essential Principle

Rewrite the model so the added method changes the host model's internal state transition or assumption.

Use this abstract pattern:

```text
state before interval
-> principle-governed evolution
-> state before event/input
-> event/input-induced update
-> state after event/input
```

The reconstructed logic should name:

- the new or reinterpreted state variable;
- the new transition rule;
- how inputs, events, or observations modify the state;
- the readout or prediction path;
- what is actually implemented versus what remains a future extension.

### 8. Explain the New Research Logic

The final explanation should not sound like module stacking.

Avoid:

```text
We combine A and B to improve performance.
```

Prefer:

```text
We first identify that Method B provides ___ while Method A provides ___. A direct fusion places Method A at ___, but this only uses it as ___. Returning to the essential principle of Method A, we reinterpret ___ as ___. Thus, Method B is no longer modeled only as ___, but as a system whose ___ is governed by ___ and corrected by ___.
```

## Socratic Checkpoints

Before finalizing an integration, check:

1. What is the first obvious connection point?
2. Is that connection only an interface-level match?
3. What core assumption of the host method remains unchanged?
4. What is the mathematical essence of the inserted method?
5. Does the inserted method change a state transition, or only a representation?
6. Can the method still be explained if the inserted block is replaced by attention, MLP, GCN, or another generic layer?
7. What problem of the host method does the inserted method solve at a mechanistic level?
8. What is the new state variable after reconstruction?
9. What is the new transition rule?
10. What should be claimed modestly, and what can be claimed as the true contribution?

## Devil's Advocate Tests

Use these tests to challenge the proposed contribution.

### Replaceability Test

If the inserted method can be replaced by a generic neural layer without changing the research story, the integration is shallow.

### State-Dynamics Test

If the internal state dynamics of the host model are unchanged, the integration is probably modular, not essential.

### Principle Test

If the explanation does not identify the mathematical principle of the inserted method, the contribution is under-theorized.

### Host-Weakness Test

If the added method does not address a specific weakness or limitation of the host method, the integration may lack necessity.

### Overclaim Test

Do not claim principle-level integration if the actual implementation only uses a method as a plug-in layer.

## Recovery Strategies

### If the integration becomes simple module stacking

Move from:

```text
Method A output -> Method B layer -> prediction
```

to:

```text
host state -> Method A-governed transition -> updated host state -> prediction
```

### If the theory is only metaphorical

Require the answer to define:

- state variable;
- operator or mechanism;
- transition equation;
- how events, inputs, or observations modify the state or operator.

### If the deepest version is too hard to implement

Recommend a mechanism-level version first. Use fixed, slowly updated, approximated, or constrained operators if needed. Treat the full principle-level reconstruction as a future extension and describe the gap honestly.

### If the example becomes mistaken for the skill itself

Rename the contribution around the reusable reasoning logic. Move any specific model, such as QWTA + TGN, into an application example.

## Application Example: QWTA + TGN

Use this example only when it helps the user understand the pattern.

### Direct connection

TGN provides event-driven node memories:

```text
s_i(t)
```

QWTA provides continuous-time graph evolution:

```text
U(Δt) = e^{-iHΔt}
```

The first connection is:

```text
TGN memory + QWTA graph propagation
```

### Shallow integration

Use QWTA as a TGN embedding module:

```text
S(t) = [s_1(t), ..., s_N(t)]^T
Z(t) = QWTAEmb(S(t), L, Δt)
```

This is valid but shallow if QWTA only appears after TGN memory has already been updated.

### Essential reconstruction

Return to QWTA's essence:

```text
Ψ(t + Δt) = e^{-iHΔt} Ψ(t)
```

Return to TGN's weakness:

```text
TGN memory is updated only when events occur, so inactive nodes can have stale memory.
```

Reconstruct the model as inter-event memory evolution plus event-induced correction:

```text
Ψ(t_k^-) = e^{-iHΔt_k} Ψ(t_{k-1}^+)
Ψ(t_k^+) = EventUpdate(Ψ(t_k^-), x(t_k))
Z(t_k) = Readout(Ψ(t_k^+))
```

This changes the interpretation from:

```text
event-triggered memory update only
```

to:

```text
continuous inter-event evolution + event-induced local correction
```

## Recommended Output Format

When applying this skill, answer in this order:

1. **Native functions** — what each method originally does.
2. **First connection** — the direct interface-level connection.
3. **Shallow attempt** — the simplest valid integration.
4. **Critical diagnosis** — why it may still be shallow.
5. **Essence return** — the deeper principle of the inserted method.
6. **Host weakness** — the limitation of the host method that this principle addresses.
7. **Essential reconstruction** — the revised state transition or model logic.
8. **Claim discipline** — what can be claimed now and what should remain a future extension.

## Claim Discipline

Use cautious and precise language.

Say:

```text
This formulation moves the integration from a module-level embedding replacement toward a mechanism-level state-evolution design.
```

Do not say:

```text
This fully solves dynamic graph learning through quantum mechanics.
```

Say:

```text
The physical interpretation is grounded in the explicit operator e^{-iHΔt}, provided that the state, Hamiltonian, and event update are clearly defined.
```

Do not say:

```text
The model is quantum because it uses complex numbers.
```

## Minimal Invocation Prompt

```text
Use $research-logic-integration. Help me analyze how two methods can be combined. First identify the direct connection point, then build the shallow integration, then challenge whether it is merely modular, and finally reconstruct a deeper mechanism-level or principle-level integration.
```

## One-Sentence Summary

A deep research integration does not merely insert one method into another; it uses one method's core principle to rewrite the other's internal logic.
