from __future__ import annotations

import math
import shutil
from pathlib import Path
from typing import Dict, Iterable, Tuple

import torch

from src.factories import get_model, get_optimizer, get_scheduler, get_task_adapter
from src.utils.checkpoint import save_checkpoint
from src.utils.logger import setup_logger
from src.utils.results import append_history_row, write_final_metrics


def _resolve_device(device_name: str) -> torch.device:
    if device_name == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(device_name)


def _run_name(args) -> str:
    return f"{args.experiment.name}_{args.experiment.variant}_seed{args.experiment.seed}"


def _metric_improved(value: float, best: float, mode: str) -> bool:
    return value < best if mode == "min" else value > best


def train(args) -> Dict[str, float]:
    """Generic, task-agnostic training loop.

    Architecture rule:
    - This function must not assume static graphs, dynamic graphs, tensor shapes, or a specific loss.
    - All task-specific behavior goes through the adapter.
    """

    device = _resolve_device(args.training.device)
    run_dir = Path(args.output.root) / _run_name(args)
    checkpoint_dir = run_dir / "checkpoints"
    log_dir = run_dir / "logs"
    results_dir = run_dir / "results"
    for directory in (checkpoint_dir, log_dir, results_dir):
        directory.mkdir(parents=True, exist_ok=True)

    if getattr(args, "config_path", None):
        shutil.copy2(args.config_path, run_dir / "config.json")

    logger = setup_logger(log_dir / "train.log")
    logger.info("Run directory: %s", run_dir)
    logger.info("Device: %s", device)

    adapter = get_task_adapter(args)
    train_loader, val_loader, test_loader = adapter.build_dataloaders(args)

    sample_batch = next(iter(train_loader))
    specs = adapter.infer_specs(args, sample_batch)
    model = get_model(args, specs).to(device)

    optimizer = get_optimizer(args, model)
    scheduler = get_scheduler(args, optimizer)

    primary_metric = args.task.primary_metric
    primary_mode = args.task.primary_metric_mode
    best_score = math.inf if primary_mode == "min" else -math.inf
    best_checkpoint_path = None
    epochs_without_improvement = 0

    history_path = results_dir / "train_history.csv"

    for epoch in range(1, args.training.num_epochs + 1):
        model.train()
        train_metrics = _run_epoch(model, train_loader, adapter, device, optimizer=optimizer, args=args)

        if scheduler is not None:
            scheduler.step()

        should_validate = epoch % args.training.save_freq == 0 or epoch == args.training.num_epochs
        val_metrics = {}
        if should_validate:
            model.eval()
            with torch.no_grad():
                val_metrics = _run_epoch(model, val_loader, adapter, device, optimizer=None, args=args)

            score = float(val_metrics.get(primary_metric, val_metrics.get("loss", math.inf)))
            if _metric_improved(score, best_score, primary_mode):
                best_score = score
                epochs_without_improvement = 0
                best_checkpoint_path = save_checkpoint(
                    checkpoint_dir / "best.pt",
                    model=model,
                    optimizer=optimizer,
                    scheduler=scheduler,
                    epoch=epoch,
                    metrics=val_metrics,
                    args=args,
                )
            else:
                epochs_without_improvement += 1

        append_history_row(history_path, epoch, train_metrics, val_metrics)
        logger.info("Epoch %d | train=%s | val=%s", epoch, train_metrics, val_metrics)

        if epochs_without_improvement >= args.training.patience:
            logger.info("Early stopping at epoch %d", epoch)
            break

    last_checkpoint_path = save_checkpoint(
        checkpoint_dir / "last.pt",
        model=model,
        optimizer=optimizer,
        scheduler=scheduler,
        epoch=epoch,
        metrics=val_metrics,
        args=args,
    )

    if best_checkpoint_path is not None:
        checkpoint = torch.load(best_checkpoint_path, map_location=device)
        model.load_state_dict(checkpoint["model_state_dict"])

    model.eval()
    with torch.no_grad():
        test_metrics = _run_epoch(model, test_loader, adapter, device, optimizer=None, args=args)

    checkpoint_for_report = best_checkpoint_path or last_checkpoint_path
    write_final_metrics(
        results_dir=results_dir,
        args=args,
        metrics=test_metrics,
        split="test",
        checkpoint_path=str(checkpoint_for_report),
    )
    logger.info("Final test metrics: %s", test_metrics)
    return test_metrics


def _run_epoch(
    model: torch.nn.Module,
    loader: Iterable,
    adapter,
    device: torch.device,
    optimizer: torch.optim.Optimizer | None,
    args,
) -> Dict[str, float]:
    metric_sums: Dict[str, float] = {}
    metric_counts: Dict[str, int] = {}

    for raw_batch in loader:
        prepared_batch = adapter.prepare_batch(raw_batch, device)
        predictions = adapter.forward(model, prepared_batch)
        loss = adapter.compute_loss(predictions, prepared_batch)

        if not torch.isfinite(loss):
            continue

        if optimizer is not None:
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            if args.training.grad_clip_norm is not None:
                torch.nn.utils.clip_grad_norm_(model.parameters(), args.training.grad_clip_norm)
            optimizer.step()

        metrics = {"loss": float(loss.detach().cpu())}
        metrics.update(adapter.compute_metrics(predictions, prepared_batch))
        for key, value in metrics.items():
            metric_sums[key] = metric_sums.get(key, 0.0) + float(value)
            metric_counts[key] = metric_counts.get(key, 0) + 1

    return {key: metric_sums[key] / max(metric_counts[key], 1) for key in metric_sums}
