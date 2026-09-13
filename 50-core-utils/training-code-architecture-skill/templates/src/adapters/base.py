from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import torch


@dataclass
class PreparedBatch:
    """Task-neutral container passed from adapters to the training engine."""

    x: torch.Tensor
    y: torch.Tensor
    graph: Optional[Any] = None
    mask: Optional[torch.Tensor] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskAdapter:
    """Base interface for task-specific behavior.

    Keep data shape assumptions, graph assumptions, model call signatures, losses,
    and metrics inside adapter implementations.
    """

    def build_dataloaders(self, args):
        raise NotImplementedError

    def infer_specs(self, args, sample_batch) -> Dict[str, Any]:
        raise NotImplementedError

    def prepare_batch(self, batch, device: torch.device) -> PreparedBatch:
        raise NotImplementedError

    def build_model_inputs(self, prepared_batch: PreparedBatch) -> Dict[str, Any]:
        return {"x": prepared_batch.x}

    def forward(self, model: torch.nn.Module, prepared_batch: PreparedBatch) -> torch.Tensor:
        return model(**self.build_model_inputs(prepared_batch))

    def compute_loss(self, predictions: torch.Tensor, prepared_batch: PreparedBatch) -> torch.Tensor:
        raise NotImplementedError

    def compute_metrics(self, predictions: torch.Tensor, prepared_batch: PreparedBatch) -> Dict[str, float]:
        raise NotImplementedError
