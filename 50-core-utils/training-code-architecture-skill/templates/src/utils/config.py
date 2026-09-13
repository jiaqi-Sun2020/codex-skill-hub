from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def _to_namespace(value: Any) -> Any:
    if isinstance(value, dict):
        return SimpleNamespace(**{k: _to_namespace(v) for k, v in value.items()})
    if isinstance(value, list):
        return [_to_namespace(v) for v in value]
    return value


def load_config(path: str | Path):
    with Path(path).open("r", encoding="utf-8") as f:
        data = json.load(f)
    return _to_namespace(data)
