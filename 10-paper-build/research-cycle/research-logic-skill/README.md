# Research Logic Skill: From Connection Discovery to Essential Integration

A reusable research-thinking skill for moving from an initial idea of combining two methods to a deeper, principle-driven integration.

This README describes the purpose, workflow, usage examples, and acknowledgement for the skill package. The detailed operational instructions are in [`SKILL.md`](./SKILL.md).

---

## 1. What This Skill Is

This skill is a reasoning framework for research ideation and model design. It helps you avoid stopping at a superficial combination such as:

```text
Method A + Method B = new model
```

Instead, it guides you to ask:

```text
Can the core principle of Method A rewrite the internal logic of Method B?
```

The central reasoning path is:

\[
\boxed{
\text{discover a connection point}
\rightarrow
\text{try a direct integration}
\rightarrow
\text{diagnose shallow fusion}
\rightarrow
\text{return to the underlying principle}
\rightarrow
\text{reconstruct the model logic}
}
\]

---

## 2. What This Skill Is Not

This skill is **not** a single-model template.

In particular, it should not be treated as a "Hamiltonian QW-TGN" skill. QWTA + TGN is only an application example used to demonstrate the reasoning pattern.

The reusable skill is the research logic:

```text
from connection discovery to essential integration
```

not any one specific model name.

---

## 3. When to Use It

Use this skill when you want to:

- combine two research methods without making the result look like arbitrary module stacking;
- identify whether a proposed integration is shallow or fundamental;
- turn a first fusion idea into a stronger theoretical narrative;
- find the internal state, transition rule, or assumption that should be changed;
- write a paper contribution that moves from engineering combination to mechanism-level design;
- explain why a new architecture is necessary rather than merely convenient.

---

## 4. Core Workflow

### Stage 1: Discover the Connection Point

Ask what each method does natively.

```text
Method A solves what problem?
Method B solves what problem?
Where do their states, operators, inputs, or outputs naturally meet?
```

The goal is to identify the first plausible bridge.

---

### Stage 2: Try the Direct Integration

Build the most obvious valid combination.

This may be a module-level connection:

```text
memory -> embedding layer -> decoder
```

or:

```text
representation -> propagation block -> prediction head
```

This step is useful, but it is not yet the final research contribution.

---

### Stage 3: Diagnose Shallow Fusion

Ask whether the new method truly changes the host model.

A fusion may be shallow if:

- it only replaces a layer;
- the host model's original state update remains unchanged;
- the inserted module could be replaced by attention, MLP, GCN, or sum pooling without changing the research story;
- the contribution can only be described as "we add A to B."

---

### Stage 4: Return to the Underlying Principle

Ask what the added method is really about.

For example, in the QWTA + TGN case:

```text
QWTA is not fundamentally an aggregation module; its essence is continuous-time Hamiltonian evolution e^{-iH\Delta t}.
```

This step turns a module into a principle.

---

### Stage 5: Reconstruct the Model Logic

Use the principle to rewrite a core assumption of the host method.

The general pattern is:

\[
\text{state before interval}
\rightarrow
\text{principle-driven evolution}
\rightarrow
\text{state before event}
\rightarrow
\text{event or input correction}
\rightarrow
\text{state after event}
\]

This is where the integration becomes essential.

---

## 5. Three-Level Integration Ladder

### Level 1: Modular Fusion

One method is inserted into another as a module.

```text
A-output -> B-layer -> prediction
```

This is easy to implement but often shallow.

---

### Level 2: Mechanistic Fusion

One method changes an internal mechanism of the other method.

```text
state -> new transition rule -> updated state
```

This is usually the best target for a strong model paper.

---

### Level 3: Principle-Level Reconstruction

One method's core principle rewrites the assumption of the other method.

```text
old assumption -> new principle-governed formulation
```

This is the deepest form of integration, but it requires careful mathematical and experimental support.

---

## 6. Application Example: QWTA + TGN

This example illustrates the skill. It is not the name or boundary of the skill.

### 6.1 Discover the Connection

TGN provides event-driven node memory:

\[
s_i(t)
\]

QWTA provides continuous-time graph propagation:

\[
U(\Delta t)=e^{-iH\Delta t}
\]

The first connection is:

```text
TGN memory + QWTA graph propagation
```

---

### 6.2 Try the Direct Integration

A natural first model is:

\[
S(t)=[s_1(t),\dots,s_N(t)]^\top
\]

\[
Z(t)=\operatorname{QWTAEmb}(S(t),L,\Delta t)
\]

This places QWTA inside the TGN embedding module.

It is valid, but it still treats QWTA as a graph aggregation or embedding block.

---

### 6.3 Diagnose the Shallow Fusion

If the model is only:

```text
TGN memory -> QWTA embedding -> decoder
```

then the original TGN memory dynamics remain unchanged.

QWTA is helpful, but it is not yet changing the core event-driven memory assumption.

---

### 6.4 Return to the Essence of QWTA

The essence of QWTA is:

\[
\Psi(t+\Delta t)=e^{-iH\Delta t}\Psi(t)
\]

So the deeper question becomes:

```text
Can QWTA define how TGN memory evolves between events?
```

---

### 6.5 Reconstruct the Integration

Define a complex-valued dynamic node memory:

\[
\Psi(t)\in\mathbb{C}^{N\times d}
\]

Inter-event evolution:

\[
\Psi(t_k^-)=e^{-iH\Delta t_k}\Psi(t_{k-1}^+)
\]

Event-induced correction:

\[
\Psi(t_k^+)=\operatorname{EventUpdate}(\Psi(t_k^-),x(t_k))
\]

This changes the model from:

```text
memory updates only when events occur
```

to:

```text
memory evolves continuously between events and is locally corrected by events
```

That is the essential integration in this example.

---

## 7. Socratic Questions

Use these questions when applying the skill:

1. What does each method do before any integration?
2. What is the first obvious connection point?
3. Is the first connection only an interface-level match?
4. What core assumption of the host model remains unchanged?
5. What is the mathematical or physical essence of the inserted method?
6. Can that essence change the host model's internal state transition?
7. What is the new state variable?
8. What is the new transition rule?
9. What part is implemented now, and what part remains a future extension?
10. How can the contribution be stated without overclaiming?

---

## 8. Devil's Advocate Checklist

Before claiming a deep contribution, check:

- Can the inserted module be replaced by attention or MLP without changing the story?
- Does the host model's state update actually change?
- Is the core principle expressed as an equation, operator, or explicit transition rule?
- Does the added method solve a real weakness of the host method?
- Are the claims consistent with the actual implementation?

---

## 9. Common Failure Modes

### Failure Mode 1: The model becomes simple module stacking

Recovery:

- identify the host model's core state;
- move the added method into the state transition;
- define the before-state and after-state explicitly.

### Failure Mode 2: The explanation is only metaphorical

Recovery:

- define the state;
- define the operator;
- define the transition equation;
- define how inputs or events affect the state.

### Failure Mode 3: The deepest version is computationally too expensive

Recovery:

- begin with a mechanism-level version;
- use fixed or slowly updated operators;
- describe the full principle-level version as a future extension.

### Failure Mode 4: The example becomes mistaken for the skill

Recovery:

- rename the skill around the reasoning path;
- move the concrete model into an application example;
- keep the reusable logic separate from the domain-specific case.

---

## 10. Recommended Research Statement Template

Use this template when writing a paper or proposal:

```text
We begin from the observation that Method A and Method B meet at [connection point]. A direct integration would place Method A inside [module of Method B], which gives a valid but primarily modular fusion. To obtain a deeper integration, we return to the core principle of Method A: [principle]. We then identify a limitation of Method B: [limitation]. This leads us to reinterpret [state/module] of Method B through [principle], resulting in a model where [new state transition]. Thus, the contribution is not merely adding Method A to Method B, but using Method A's core mechanism to rewrite the internal logic of Method B.
```

For the QWTA + TGN example:

```text
We begin from the observation that TGN provides event-driven node memory, while QWTA provides continuous-time graph propagation. A direct integration would place QWTA inside the TGN embedding module, which is valid but primarily modular. Returning to the core principle of QWTA, namely Hamiltonian evolution through e^{-iH\Delta t}, we identify a limitation of TGN: node memories are updated only when events occur. We therefore reinterpret node memory as a complex-valued graph state that evolves between events and is locally corrected by event updates. The resulting design moves from module-level embedding replacement to mechanism-level memory evolution.
```

---

## 11. Acknowledgements

This skill-package style was inspired by the open-source project **Imbad0202/academic-research-skills-codex**, a Codex-native Academic Research Skills suite for human-in-the-loop academic research workflows.

We gratefully acknowledge that repository for its structured skill-packaging philosophy, workflow-oriented README organization, Socratic reasoning pattern, and practical emphasis on research integrity checkpoints.

This repository does not copy that project. It adapts the general idea of a research skill into a focused reasoning framework for moving from connection discovery to essential integration.

---

## 12. Minimal Invocation Prompt

```text
Use the Research Logic Skill: From Connection Discovery to Essential Integration. Help me analyze how two methods can be combined. First identify the direct connection point, then build the shallow integration, then challenge whether it is merely modular, and finally reconstruct a deeper mechanism-level or principle-level integration.
```

---

## 13. One-Sentence Summary

\[
\boxed{
\text{A deep research integration does not merely insert one method into another; it uses one method's core principle to rewrite the other's internal logic.}
}
\]
