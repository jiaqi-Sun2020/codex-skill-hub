---
name: training-code-architecture
# Keep this description architecture-first. The trigger is code architecture/template generation, not a specific task such as QWTA, static graph, traffic forecasting, or MSE regression.
description: Use this skill when the user asks to create, refactor, or standardize a reusable machine-learning training code architecture from an existing code example. Trigger for requests about preserving project architecture, main.py to train(args) workflow, config-driven training, factories, adapters, training loops, checkpoint/log/result saving, experiment reproducibility, static/dynamic graph compatibility, or making a template that can be reused across different model/data/task types.
---

# Training Code Architecture Skill

## Core principle

This skill preserves **code architecture**, not a concrete data-processing mode.

The user's example project should be treated as evidence of architectural preferences:

- config-driven execution
- a small `main.py` entrypoint
- `main.py -> train(args)` control flow
- separate dataset/model construction from the training loop
- checkpointing, logging, and result saving
- reusable experiment output layout
- batch running for multiple experiment configs

The following are **task-specific details**, not architecture, and must not be hard-coded into the template unless the user explicitly asks:

- QWTA/QWAT model names
- traffic forecasting
- static graph assumptions
- fixed `edge_index` usage
- fixed tensor shapes such as `[B, T, N, F]`
- MSE/MAE-only regression
- NaN-masked loss as the only loss pattern
- PyTorch-Geometric as a required dependency
- any dataset-specific preprocessing rule

When generating code from this skill, always separate:

1. **Architecture layer**: entrypoint, config, training engine, factories, adapters, logging, checkpointing, metrics saving.
2. **Task adapter layer**: how to load batches, how to build graph inputs, how to call the model, how to compute loss/metrics.
3. **Concrete experiment layer**: QWTA static graph, dynamic graph, image classification, sequence modeling, etc.

## Default architecture extracted from the user's code

Preserve these architectural conventions:

### Entrypoint

Use a thin entrypoint:

```python
# main.py
args = load_config_as_namespace(config_path)
set_seed(args.seed)
train(args)
```

`main.py` should not contain dataset logic, model logic, graph logic, loss logic, or metric logic.

### Config-driven execution

Use JSON by default because the user's code is JSON-driven. YAML may be used only if requested.

The config should be sectioned:

```json
{
  "experiment": {},
  "data": {},
  "model": {},
  "training": {},
  "task": {},
  "output": {}
}
```

Do not flatten every field into one long namespace unless compatibility with old code is required.

### Training engine

`train.py` should implement a reusable training engine:

1. Load task adapter.
2. Build dataloaders through the adapter.
3. Infer batch/model specs through the adapter.
4. Build model through a model factory.
5. Build optimizer/scheduler/loss/metrics.
6. Run train/validation/test loops.
7. Save checkpoints, logs, copied config, history CSV, and final metrics CSV.

The training loop must call adapter hooks rather than directly assuming a static graph, fixed tensor shape, or fixed loss.

### Adapter boundary

All task-specific logic should live behind a `TaskAdapter` interface.

The adapter is responsible for:

- building dataloaders
- preparing a raw batch for the device
- exposing graph inputs if any
- calling the model if the call signature is task-specific
- aligning predictions and targets if needed
- computing loss
- computing metrics
- deciding whether higher/lower metric values are better

This is the main rule that makes the template reusable for static graph today and dynamic graph tomorrow.

## Required project structure

When generating a new reusable template, prefer this tree:

```text
project_name/
├── config.json
├── main.py
├── train.py
├── train_all.py
├── src/
│   ├── __init__.py
│   ├── factories.py
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── static_graph_adapter.py
│   │   └── dynamic_graph_adapter.py
│   └── utils/
│       ├── __init__.py
│       ├── config.py
│       ├── seed.py
│       ├── checkpoint.py
│       ├── logger.py
│       └── results.py
├── outputs/
│   └── runs/
└── README.md
```

If the user's existing project has `model/`, `dataset/`, and `utils/` directories, keep those names for compatibility, but still preserve the adapter/factory boundary.

## Adapter interface

Generate or preserve an interface similar to this:

```python
class TaskAdapter:
    def build_dataloaders(self, args):
        raise NotImplementedError

    def infer_specs(self, args, sample_batch):
        raise NotImplementedError

    def prepare_batch(self, batch, device):
        raise NotImplementedError

    def build_model_inputs(self, prepared_batch):
        raise NotImplementedError

    def forward(self, model, prepared_batch):
        model_inputs = self.build_model_inputs(prepared_batch)
        return model(**model_inputs)

    def compute_loss(self, predictions, prepared_batch):
        raise NotImplementedError

    def compute_metrics(self, predictions, prepared_batch):
        raise NotImplementedError
```

The trainer should use this adapter, not task-specific code.

## Static graph vs dynamic graph rule

Static and dynamic graph support must be handled through adapters or graph providers.

### Static graph

A static graph adapter may store one graph object for all batches:

```python
prepared_batch.graph = static_edge_index
```

This is appropriate for QWTA-style static traffic networks or any task where graph connectivity is fixed across samples.

### Dynamic graph

A dynamic graph adapter must assume graph inputs can vary by sample, time step, or batch:

```python
prepared_batch.graph = batch["edge_index"]
prepared_batch.edge_weight = batch.get("edge_weight")
prepared_batch.graph_time = batch.get("graph_time")
```

The training engine must not care whether the graph is static or dynamic. Only the adapter and model factory should care.

## Factories

Use factories to isolate construction logic:

```python
adapter = get_task_adapter(args)
model = get_model(args, specs).to(device)
optimizer = get_optimizer(args, model)
scheduler = get_scheduler(args, optimizer)
```

The factory may dispatch by string names in config, but the architecture should not depend on any one model name.

## Output contract

Every training run should create:

```text
outputs/runs/{run_name}/
├── config.json
├── checkpoints/
│   ├── best.pt
│   └── last.pt
├── logs/
│   └── train.log
└── results/
    ├── train_history.csv
    ├── final_metrics.csv
    └── ablation_ready_metrics.csv
```

The final metrics file should support downstream ablation analysis:

```csv
experiment,variant,seed,dataset,model,metric_name,metric_value,split,checkpoint_path
exp001,Full,42,my_dataset,my_model,MAE,2.345,test,outputs/runs/exp001/checkpoints/best.pt
```

This schema is architectural because it standardizes outputs across tasks.

## Code generation rules

When using this skill, the generated code must:

- keep `main.py` thin
- keep `train.py` task-agnostic
- put task-specific logic in adapters
- put model construction in factories
- save reproducible outputs
- save copied configs and CSV metrics
- avoid hard-coded absolute paths
- use `pathlib.Path`
- set seeds for reproducibility
- include clear placeholders for user-specific dataset/model code

## Anti-patterns

Do not generate a template that:

- assumes static graph everywhere
- passes `edge_index` directly through the entire trainer unless hidden behind an adapter
- assumes every batch is `[B, T, N, F]`
- assumes every target is `[B, N, S]`
- assumes all tasks use MSE/MAE
- names the skill or template after QWTA unless the user specifically requests a QWTA template
- mixes dataset preprocessing into the training loop
- mixes model-specific forward signatures into the training loop
- stores only printed logs without CSV metrics

## How to adapt to a new task

For a new task, change only:

1. `config.json` task/model/data sections
2. one adapter under `src/adapters/`
3. `get_model()` dispatch if a new model is added
4. metric/loss functions used by the adapter

Do not rewrite:

- `main.py`
- generic training loop structure
- checkpoint utilities
- logging utilities
- result CSV utilities
- batch experiment runner

## Response style when user asks for modification

If the user corrects that they want architecture instead of a concrete mode, explicitly separate:

- what should be kept as architecture
- what should be moved into adapters
- what should be deleted from the skill
- what files need to be regenerated

Then provide the updated skill or patch.
