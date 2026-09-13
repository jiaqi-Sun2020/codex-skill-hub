from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict


def append_history_row(path: str | Path, epoch: int, train_metrics: Dict[str, float], val_metrics: Dict[str, float]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {"epoch": epoch}
    row.update({f"train_{key}": value for key, value in train_metrics.items()})
    row.update({f"val_{key}": value for key, value in val_metrics.items()})

    fieldnames = list(row.keys())
    write_header = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def write_final_metrics(results_dir: str | Path, args, metrics: Dict[str, float], split: str, checkpoint_path: str) -> None:
    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    final_path = results_dir / "final_metrics.csv"
    ablation_path = results_dir / "ablation_ready_metrics.csv"

    rows = []
    for metric_name, metric_value in metrics.items():
        rows.append({
            "experiment": args.experiment.name,
            "variant": args.experiment.variant,
            "seed": args.experiment.seed,
            "dataset": args.data.dataset_name,
            "model": args.model.name,
            "metric_name": metric_name,
            "metric_value": metric_value,
            "split": split,
            "checkpoint_path": checkpoint_path,
        })

    fieldnames = [
        "experiment",
        "variant",
        "seed",
        "dataset",
        "model",
        "metric_name",
        "metric_value",
        "split",
        "checkpoint_path",
    ]

    for path in (final_path, ablation_path):
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
