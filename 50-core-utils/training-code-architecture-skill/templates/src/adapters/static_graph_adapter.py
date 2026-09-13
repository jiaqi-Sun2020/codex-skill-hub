from __future__ import annotations

from typing import Any, Dict, Tuple

import torch
from torch.utils.data import DataLoader, TensorDataset, random_split

from .base import PreparedBatch, TaskAdapter


class StaticGraphAdapter(TaskAdapter):
    """Example adapter for tasks with one graph shared by all batches.

    Replace the toy dataset and graph with your real static-graph data loader.
    The generic trainer does not know this graph is static.
    """

    def __init__(self) -> None:
        self.static_graph = None

    def build_dataloaders(self, args):
        x = torch.randn(args.data.num_samples, args.data.input_dim)
        y = x[:, : args.data.target_dim].sum(dim=1, keepdim=True)
        dataset = TensorDataset(x, y)

        n_train = int(0.7 * len(dataset))
        n_val = int(0.15 * len(dataset))
        n_test = len(dataset) - n_train - n_val
        train_ds, val_ds, test_ds = random_split(
            dataset,
            [n_train, n_val, n_test],
            generator=torch.Generator().manual_seed(args.experiment.seed),
        )

        # Placeholder static graph. Swap with your real edge_index/adjacency object.
        self.static_graph = torch.tensor([[0, 1], [1, 0]], dtype=torch.long)

        batch_size = args.data.batch_size
        return (
            DataLoader(train_ds, batch_size=batch_size, shuffle=True),
            DataLoader(val_ds, batch_size=batch_size, shuffle=False),
            DataLoader(test_ds, batch_size=batch_size, shuffle=False),
        )

    def infer_specs(self, args, sample_batch) -> Dict[str, Any]:
        x, y = sample_batch
        return {
            "input_dim": x.shape[-1],
            "target_dim": y.shape[-1],
            "graph_mode": "static",
        }

    def prepare_batch(self, batch, device: torch.device) -> PreparedBatch:
        x, y = batch
        graph = self.static_graph.to(device) if isinstance(self.static_graph, torch.Tensor) else self.static_graph
        return PreparedBatch(x=x.to(device), y=y.to(device), graph=graph)

    def build_model_inputs(self, prepared_batch: PreparedBatch) -> Dict[str, Any]:
        return {"x": prepared_batch.x, "graph": prepared_batch.graph}

    def compute_loss(self, predictions: torch.Tensor, prepared_batch: PreparedBatch) -> torch.Tensor:
        return torch.nn.functional.mse_loss(predictions, prepared_batch.y)

    def compute_metrics(self, predictions: torch.Tensor, prepared_batch: PreparedBatch) -> Dict[str, float]:
        mae = torch.mean(torch.abs(predictions - prepared_batch.y))
        return {"mae": float(mae.detach().cpu())}
