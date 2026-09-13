from __future__ import annotations

from typing import Any, Dict, List

import torch
from torch.utils.data import DataLoader, Dataset, random_split

from .base import PreparedBatch, TaskAdapter


class ToyDynamicGraphDataset(Dataset):
    """Placeholder dynamic-graph dataset.

    Each sample has its own graph. Replace this with your real dynamic graph data.
    """

    def __init__(self, num_samples: int, input_dim: int, target_dim: int) -> None:
        self.x = torch.randn(num_samples, input_dim)
        self.y = self.x[:, :target_dim].sum(dim=1, keepdim=True)

    def __len__(self) -> int:
        return len(self.x)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        edge_index = torch.tensor([[0, 1], [1, 0]], dtype=torch.long)
        edge_weight = torch.rand(edge_index.shape[1])
        return {
            "x": self.x[idx],
            "y": self.y[idx],
            "edge_index": edge_index,
            "edge_weight": edge_weight,
        }


def collate_dynamic_graph(batch: List[Dict[str, torch.Tensor]]) -> Dict[str, Any]:
    return {
        "x": torch.stack([item["x"] for item in batch]),
        "y": torch.stack([item["y"] for item in batch]),
        # Keep graph data as a list because graph structure can vary per sample.
        "graphs": [
            {"edge_index": item["edge_index"], "edge_weight": item["edge_weight"]}
            for item in batch
        ],
    }


class DynamicGraphAdapter(TaskAdapter):
    """Example adapter for tasks whose graph changes by sample/time/batch."""

    def build_dataloaders(self, args):
        dataset = ToyDynamicGraphDataset(
            num_samples=args.data.num_samples,
            input_dim=args.data.input_dim,
            target_dim=args.data.target_dim,
        )
        n_train = int(0.7 * len(dataset))
        n_val = int(0.15 * len(dataset))
        n_test = len(dataset) - n_train - n_val
        train_ds, val_ds, test_ds = random_split(
            dataset,
            [n_train, n_val, n_test],
            generator=torch.Generator().manual_seed(args.experiment.seed),
        )
        batch_size = args.data.batch_size
        return (
            DataLoader(train_ds, batch_size=batch_size, shuffle=True, collate_fn=collate_dynamic_graph),
            DataLoader(val_ds, batch_size=batch_size, shuffle=False, collate_fn=collate_dynamic_graph),
            DataLoader(test_ds, batch_size=batch_size, shuffle=False, collate_fn=collate_dynamic_graph),
        )

    def infer_specs(self, args, sample_batch) -> Dict[str, Any]:
        return {
            "input_dim": sample_batch["x"].shape[-1],
            "target_dim": sample_batch["y"].shape[-1],
            "graph_mode": "dynamic",
        }

    def prepare_batch(self, batch, device: torch.device) -> PreparedBatch:
        graphs = []
        for graph in batch["graphs"]:
            graphs.append({
                key: value.to(device) if isinstance(value, torch.Tensor) else value
                for key, value in graph.items()
            })
        return PreparedBatch(
            x=batch["x"].to(device),
            y=batch["y"].to(device),
            graph=graphs,
        )

    def build_model_inputs(self, prepared_batch: PreparedBatch) -> Dict[str, Any]:
        return {"x": prepared_batch.x, "graph": prepared_batch.graph}

    def compute_loss(self, predictions: torch.Tensor, prepared_batch: PreparedBatch) -> torch.Tensor:
        return torch.nn.functional.mse_loss(predictions, prepared_batch.y)

    def compute_metrics(self, predictions: torch.Tensor, prepared_batch: PreparedBatch) -> Dict[str, float]:
        mae = torch.mean(torch.abs(predictions - prepared_batch.y))
        return {"mae": float(mae.detach().cpu())}
