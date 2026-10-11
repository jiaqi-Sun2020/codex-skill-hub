---
name: experiment-design
description: Turn a scoped research claim into an evidence plan with rival explanations, discriminating observations or proof obligations, applicable controls and analysis, failure cases, and claim boundaries. Use before evidence production across empirical, theoretical, qualitative, simulation, and method research; not for executing studies, running adapters, or granting authorization.
---

# Experiment Design

## Purpose

Use this skill to convert a promising research idea into a rigorous evidence plan that can support a paper. Focus on evidence design, not implementation details.

The goal is to answer:

```text
What must be tested so that the paper's central claim is believable?
```

## Core Principle

Do not start from "what can we run easily." Start from the claim.

Use this chain:

```text
claim -> rival explanations -> discriminating evidence -> applicable design -> analysis -> claim boundary
```

For a mechanism claim, evidence should distinguish it from simpler explanations. Theory can use proof obligations or counterexamples; qualitative work can use sampling, triangulation and rival interpretations. Do not force new experiments onto a literature-only or theoretical question.

## Workflow

Apply only the modules needed by the study type. Datasets, training seeds,
baselines, ablations, numerical metrics and plots are not universal gates.

### 1. State the Central Claim

State the scoped research question and one precise claim; distinguish descriptive, predictive and causal intent. If unresolved, keep candidate hypotheses rather than invent a favored mechanism.

Use:

```text
This paper claims that ___ improves/changes ___ because ___.
```

For a method paper that actually claims a mechanism, an example is:

```text
We introduce ___ as a structured transition mechanism for ___, addressing ___.
```

### 2. Define Research Questions

Choose only the research questions needed for the claim; there is no fixed count. These are optional method-paper examples:

```text
RQ1 Performance: Does the proposed method outperform strong baselines?
RQ2 Mechanism: Is the improvement caused by the proposed mechanism?
RQ3 Robustness: When does the method help or fail?
RQ4 Efficiency: What computational cost does the mechanism introduce?
RQ5 Interpretability: Does the learned mechanism behave as intended?
```

### 3. Choose Datasets by Claim Coverage

When datasets are applicable, select those that stress the claimed weakness of prior methods. For each dataset, specify task type, why it matches the claim, split protocol, metrics, expected difficulty, and limitations.

Simulation-only evidence is valid for an explicitly scoped simulation question; explain transfer limits rather than requiring real data for every project.

### 4. Select Baselines

When claiming comparative performance or a unique mechanism, justify relevant strong/simple alternatives and suitable capacity or resource controls; neural baselines are not universal requirements.

For a physics-inspired superiority claim, consider a comparable non-physics alternative when it tests the claimed explanation. State why a proposed comparison is applicable or not.

### 5. Design Ablations

When removal/replacement is meaningful, ablations can isolate the contribution. They are not mandatory for theoretical, qualitative, or literature work:

```text
Full model: ...
Remove mechanism: ...
Replace mechanism with generic layer: ...
Simplify operator/state/update: ...
Static vs dynamic version: ...
Parameter/capacity control: ...
```

Conditional example for CTQW + dynamic graph ideas only:

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

## Design-validity checks

Before advancing the plan, identify the independent sampling/experimental unit,
technical versus independent repetitions, selection/measurement/confounding risks,
missingness handling and dependence where applicable. Predeclare outcomes and
analysis decisions for confirmatory work before inspecting outcomes. Record
amendments, reasons and which outcomes were already known; post-outcome changes
remain disclosed and exploratory, never retroactively preregistered.

For every consequential concern state the object/source, uncertainty, implication
for the claim, smallest design repair, and how it could be checked. A design
cannot grant execution, ethics, publication, or scientific claim approval.

## Recommended Output Format

Use applicable sections only. The following model-experiment format is optional; theoretical/qualitative projects can instead organize proof obligations or source/sampling/interpretation evidence:

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

A defensible evidence plan specifies what could support or challenge the scoped claim and which conclusions would remain unjustified.

Evidence appraisal adaptations: [third-party notices](../THIRD_PARTY_NOTICES.md).
