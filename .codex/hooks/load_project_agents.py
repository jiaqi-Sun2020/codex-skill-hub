#!/usr/bin/env python3
"""Inject the canonical bundle-local AGENTS.md into Codex startup context."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


MANAGED_MARKER = "project-agent-bootstrap/v1"
AGENT_BUNDLE = Path(".agents")
MAX_INSTRUCTION_BYTES = 12 * 1024
SUPPORTED_EVENTS = {"SessionStart", "SubagentStart"}


def is_link_like(path: Path) -> bool:
    try:
        if path.is_symlink():
            return True
        junction_check = getattr(path, "is_junction", None)
        if junction_check and junction_check():
            return True
        return bool(getattr(path.lstat(), "st_file_attributes", 0) & 0x400)
    except OSError:
        return True


def first_link_component(path: Path) -> Path | None:
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if current.exists() and is_link_like(current):
            return current
    return None


def response(event: str, *, context: str | None = None, error: str | None = None) -> dict:
    payload: dict[str, object] = {}
    if error is not None:
        payload.update(
            {"continue": False, "stopReason": error, "systemMessage": error}
        )
    if context is not None:
        payload["hookSpecificOutput"] = {
            "hookEventName": event,
            "additionalContext": context,
        }
    return payload


def main() -> int:
    try:
        event_input = json.load(sys.stdin)
        event = str(event_input.get("hook_event_name", ""))
        if event not in SUPPORTED_EVENTS:
            raise ValueError(f"unsupported bootstrap event: {event or '<missing>'}")
        project_root = Path(__file__).resolve(strict=True).parents[2]
        target = project_root / AGENT_BUNDLE / "AGENTS.md"
        if first_link_component(target.absolute()) is not None:
            raise ValueError("refusing linked or junction-based bundle AGENTS.md")
        if not target.is_file() or is_link_like(target):
            raise FileNotFoundError(
                f"canonical project instructions are missing: {AGENT_BUNDLE.as_posix()}/AGENTS.md"
            )
        size = target.stat().st_size
        if size == 0:
            raise ValueError("canonical project instructions are empty")
        if size > MAX_INSTRUCTION_BYTES:
            raise ValueError(
                "canonical project instructions exceed the 12-KiB bootstrap limit"
            )
        content = target.read_text(encoding="utf-8-sig")
        source = f"{AGENT_BUNDLE.as_posix()}/AGENTS.md"
        context = (
            f"[{MANAGED_MARKER}] Canonical project instructions loaded from "
            f"{source}. Apply them for this session.\n\n{content.rstrip()}"
        )
        print(json.dumps(response(event, context=context), ensure_ascii=False))
        return 0
    except (IndexError, OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        event = "SessionStart"
        try:
            parsed_event = str(event_input.get("hook_event_name", ""))
            if parsed_event in SUPPORTED_EVENTS:
                event = parsed_event
        except (NameError, AttributeError):
            pass
        message = f"Project instruction bootstrap failed: {exc}"
        print(json.dumps(response(event, error=message), ensure_ascii=False))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
