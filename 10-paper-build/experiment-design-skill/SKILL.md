---
name: experiment-design
description: Use when Codex needs to turn a research model idea, algorithmic contribution, or architecture prototype into a paper-grade experimental validation plan; define research questions, hypotheses, datasets, baselines, ablations, metrics, mechanism checks, failure cases, claim boundaries, and experiment tables. Use for ML, graph learning, dynamic graph, physics-inspired models, and method papers where the user asks whether an idea can support a publication or how to design convincing experiments.
---

# Experiment Design

## Purpose

Use this skill to convert a promising research idea into a rigorous experimental plan that can support a paper. Focus on evidence design, not implementation details.

The goal is to answer:

```text
What must be tested so that the paper's central claim is believable?
```

## Core Principle

Do not start from "what can we run easily." Start from the claim.

Use this chain:

```text
claim -> hypothesis -> evidence needed -> datasets -> baselines -> ablations -> metrics -> analysis -> claim boundary
```

If the experiments do not distinguish the proposed mechanism from simpler alternatives, the design is weak.

## Workflow

### 1. State the Central Claim

Rewrite the model idea as one precise claim.

Use:

```text
This paper claims that ___ improves/changes ___ because ___.
```

Prefer mechanism-level claims:

```text
We introduce ___ as a structured transition mechanism for ___, addressing ___.
```

### 2. Define Research Questions

Create 3-5 research questions:

```text
RQ1 Performance: Does the proposed method outperform strong baselines?
RQ2 Mechanism: Is the improvement caused by the proposed mechanism?
RQ3 Robustness: When does the method help or fail?
RQ4 Efficiency: What computational cost does the mechanism introduce?
RQ5 Interpretability: Does the learned mechanism behave as intended?
```

### 3. Choose Datasets by Claim Coverage

Select datasets that stress the claimed weakness of prior methods. For each dataset, specify task type, why it matches the claim, split protocol, metrics, expected difficulty, and limitations.

Do not use only synthetic data unless the paper is explicitly theoretical or diagnostic.

### 4. Select Baselines

Include strong task baselines, simple neural baselines, mechanism-neighbor baselines, and parameter-matched or complexity-matched baselines when possible.

For physics-inspired or structured models, always include a non-physics alternative with similar capacity.

### 5. Design Ablations

Ablations should isolate the actual contribution:

```text
Full model: ...
Remove mechanism: ...
Replace mechanism with generic layer: ...
Simplify operator/state/update: ...
Static vs dynamic version: ...
Parameter/capacity control: ...
```

For CTQW + dynamic graph ideas, consider:

```text
Full: Hamiltonian inter-event evolution + event update
w/o CTQW: event update only
w/o event update: Hamiltonian evolution only
Diffusion: exp(-L delta_t)
MLP transition: learned generic transition
Static H: fixed Hamiltonian
Dynamic H: graph-dependent Hamiltonian
```

### 6. Add Mechanism Checks

Ask whether the learned mechanism responds to the variable it claims to model, whether performance changes under target stress conditions, whether replacing the mechanism removes the advantage, and whether it behaves sensibly under long gaps, sparse events, noise, or distribution shift.

For dynamic graph models, include checks over time gap length, event sparsity, inactive nodes, graph density, new nodes, and temporal extrapolation.

### 7. Define Metrics and Tables

Every metric must map to a research question.

```text
Table 1: Main performance across datasets
Table 2: Ablation study
Table 3: Robustness or stress-test results
Table 4: Efficiency and parameter count
Figure 1: Method overview
Figure 2: Mechanism behavior or sensitivity analysis
```

### 8. Identify Failure Cases

Name where the method may not help: dense graphs, very short time gaps, noisy operator construction, small datasets, or tasks where the proposed mechanism does not match the data-generating process.

### 9. Set Claim Boundaries

Use disciplined conclusions:

```text
If the results show ___, we can claim ___.
If only ___ improves, we can only claim ___.
If ablations show ___, the mechanism claim is unsupported.
```

## Recommended Output Format

When applying this skill, answer in this order:

1. **Central Claim**
2. **Research Questions**
3. **Datasets and Tasks**
4. **Baselines**
5. **Ablations**
6. **Mechanism Checks**
7. **Metrics and Tables**
8. **Failure Cases**
9. **Claim Boundaries**
10. **Minimum Viable Experiment Plan**

## Minimal Invocation Prompt

```text
Use $experiment-design. Turn my model idea into a paper-grade experimental validation plan. Define research questions, datasets, baselines, ablations, metrics, mechanism checks, failure cases, and claim boundaries.
```

## One-Sentence Summary

A publishable experiment plan does not merely show that a model works; it shows why the claimed mechanism is necessary, when it helps, and what claims the evidence truly supports.
