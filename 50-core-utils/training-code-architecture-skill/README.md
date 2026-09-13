# training-code-architecture skill

This skill captures the **training code architecture** from a user's example project without freezing the example project's concrete task details.

It is designed for cases like:

- current project: QWTA with a static graph
- next project: dynamic graph model
- later project: non-graph sequence model or image model

The architecture stays stable:

```text
main.py -> train(args) -> TaskAdapter + factories -> generic loop -> outputs
```

Task-specific assumptions are isolated in adapters.

## Files

```text
training-code-architecture-skill/
├── SKILL.md
├── README.md
├── scripts/
│   └── create_project.py
└── templates/
    ├── config.json
    ├── main.py
    ├── train.py
    ├── train_all.py
    └── src/
        ├── factories.py
        ├── adapters/
        │   ├── base.py
        │   ├── static_graph_adapter.py
        │   └── dynamic_graph_adapter.py
        └── utils/
            ├── config.py
            ├── seed.py
            ├── checkpoint.py
            ├── logger.py
            └── results.py
```

## Use

Place this folder in your skills directory.

To scaffold a starter architecture:

```bash
python scripts/create_project.py --output ./my_training_project --force
```

Then run:

```bash
cd my_training_project
python main.py --config config.json
```

The starter project uses placeholder toy adapters. Replace the adapter logic with your real dataset/model logic while keeping `main.py` and the generic training loop stable.
