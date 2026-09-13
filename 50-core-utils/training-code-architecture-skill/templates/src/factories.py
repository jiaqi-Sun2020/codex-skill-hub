from __future__ import annotations

from typing import Any, Dict

import torch

from src.adapters import DynamicGraphAdapter, StaticGraphAdapter, TaskAdapter


class ToyMLP(torch.nn.Module):
    """Placeholder model.

    Its forward signature accepts `graph` to demonstrate that graph handling is
    routed through adapters, but this toy model intentionally ignores it.
    Replace this with your real static-graph, dynamic-graph, or non-graph model.
    """

    def __init__(self, input_dim: int, hidden_dim: int, target_dim: int) -> None:
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(input_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_dim, target_dim),
        )

    def forward(self, x: torch.Tensor, graph: Any = None) -> torch.Tensor:
        return self.net(x)


def get_task_adapter(args) -> TaskAdapter:
    adapter_name = args.task.adapter
    if adapter_name == "static_graph":
        return StaticGraphAdapter()
    if adapter_name == "dynamic_graph":
        return DynamicGraphAdapter()
    raise ValueError(f"Unknown task adapter: {adapter_name}")


def get_model(args, specs: Dict[str, Any]) -> torch.nn.Module:
    model_name = args.model.name
    if model_name == "toy_mlp":
        return ToyMLP(
            input_dim=specs["input_dim"],
            hidden_dim=args.model.hidden_dim,
            target_dim=specs["target_dim"],
        )
    raise ValueError(f"Unknown model: {model_name}")


def get_optimizer(args, model: torch.nn.Module) -> torch.optim.Optimizer:
    return torch.optim.AdamW(
        model.parameters(),
        lr=args.training.lr,
        weight_decay=args.training.weight_decay,
    )


def get_scheduler(args, optimizer: torch.optim.Optimizer):
    return torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=max(args.training.num_epochs, 1),
    )
