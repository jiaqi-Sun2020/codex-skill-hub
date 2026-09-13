#!/usr/bin/env python3
"""Create a read-only, metadata-only inventory of a research workspace."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys


SCHEMA_VERSION = "research-workspace-inventory/v1"
DEFAULT_MAX_FILES = 20_000
HARD_MAX_FILES = 100_000
MAX_REPORTED_PATHS_PER_ROLE = 80
MAX_TEMPORARY_CANDIDATES = 100

SKIP_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".next",
    ".turbo",
}

SENSITIVE_TERMS = {
    "secret",
    "secrets",
    "credential",
    "credentials",
    "token",
    "tokens",
    "password",
    "passwords",
    "passwd",
    "cookie",
    "cookies",
    "session",
    "sessions",
    "private",
    "id_rsa",
}
SENSITIVE_SUFFIXES = {".pem", ".p12", ".pfx", ".key", ".keystore"}

ROLE_HINTS = {
    "governance": {
        ".agents", ".agent", ".codex", "governance", "admin", "decisions",
    },
    "protocols": {
        "protocol", "protocols", "study", "studies", "design", "designs",
        "preregistration", "preregistrations",
    },
    "source_records": {
        "raw", "original", "originals", "source", "sources", "input", "inputs",
        "acquisition", "acquisitions", "field-notes",
    },
    "external_references": {
        "external", "reference", "references", "vendor", "benchmarks",
    },
    "derived_data": {
        "derived", "processed", "preprocessed", "prepared", "cleaned", "interim",
        "features", "coded", "calibrated",
    },
    "methods": {
        "src", "code", "lib", "libs", "method", "methods", "model", "models",
        "scripts", "utils", "utilities",
    },
    "experiments_analyses": {
        "experiment", "experiments", "analysis", "analyses", "workflow", "workflows",
        "pipeline", "pipelines", "notebook", "notebooks",
    },
    "run_evidence": {
        "run", "runs", "output", "outputs", "result", "results", "artifact",
        "artifacts", "checkpoints", "logs",
    },
    "reports": {"report", "reports", "docs", "documentation"},
    "deliverables": {
        "publication", "publications", "paper", "papers", "manuscript", "manuscripts",
        "figure", "figures", "figs", "presentation", "presentations", "release", "releases",
    },
    "archive": {"archive", "archives", "archived"},
    "temporary": {".tmp", "tmp", "temp", "temporary", "cache", "caches", "scratch"},
    "data_container": {"data", "dataset", "datasets"},
    "tests": {"test", "tests", "testing", "validation", "validations"},
}

TEMPORARY_FILE_PATTERNS = (
    re.compile(r"(?i)(^|[.])(tmp|temp)([.]|$)"),
    re.compile(r"(?i)[.]staging$"),
    re.compile(r"(?i)[.](bak|swp|swo)$"),
)


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


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


def is_sensitive_path(path: Path, root: Path) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        parts = (path.name,)
    for part in parts:
        lower = part.casefold()
        if lower == ".env" or lower.startswith(".env."):
            return True
        if Path(lower).suffix in SENSITIVE_SUFFIXES:
            return True
        terms = {term for term in re.split(r"[\s._-]+", lower) if term}
        if terms & SENSITIVE_TERMS:
            return True
        if {"api", "key"} <= terms or {"private", "key"} <= terms:
            return True
    return False


def roles_for_path(relative: Path) -> list[str]:
    lowered = [part.casefold() for part in relative.parts]
    roles = [
        role
        for role, names in ROLE_HINTS.items()
        if any(part in names for part in lowered)
    ]
    return roles or ["unknown"]


def is_temporary_candidate(path: Path) -> bool:
    if path.name.casefold() in ROLE_HINTS["temporary"]:
        return True
    return any(pattern.search(path.name) for pattern in TEMPORARY_FILE_PATTERNS)


def safe_stat(path: Path) -> os.stat_result | None:
    try:
        return path.lstat()
    except OSError:
        return None


def build_inventory(root: Path, *, max_files: int = DEFAULT_MAX_FILES) -> dict[str, object]:
    root = root.expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"project root does not exist or is not a directory: {root}")
    if is_link_like(root):
        raise ValueError(f"project root must not be a link or junction: {root}")
    if max_files < 1 or max_files > HARD_MAX_FILES:
        raise ValueError(f"max_files must be between 1 and {HARD_MAX_FILES}")

    digest = hashlib.sha256()
    file_count = 0
    directory_count = 0
    total_bytes = 0
    sensitive_surface_count = 0
    link_count = 0
    unreadable_count = 0
    scan_truncated = False
    extensions: Counter[str] = Counter()
    roles: dict[str, list[str]] = defaultdict(list)
    top_level: list[dict[str, object]] = []
    temporary_candidates: list[str] = []

    stack = [root]
    while stack:
        current = stack.pop()
        try:
            entries = sorted(os.scandir(current), key=lambda entry: entry.name.casefold())
        except OSError:
            unreadable_count += 1
            continue
        child_directories: list[Path] = []
        for entry in entries:
            path = Path(entry.path)
            relative = path.relative_to(root)
            if is_sensitive_path(path, root):
                sensitive_surface_count += 1
                continue
            if is_link_like(path):
                link_count += 1
                continue
            try:
                is_directory = entry.is_dir(follow_symlinks=False)
                is_file = entry.is_file(follow_symlinks=False)
            except OSError:
                unreadable_count += 1
                continue

            role_names = roles_for_path(relative)
            if len(relative.parts) <= 2:
                for role in role_names:
                    if len(roles[role]) < MAX_REPORTED_PATHS_PER_ROLE:
                        roles[role].append(relative.as_posix() + ("/" if is_directory else ""))

            if len(relative.parts) == 1:
                top_level.append({
                    "path": relative.as_posix() + ("/" if is_directory else ""),
                    "kind": "directory" if is_directory else "file",
                    "role_candidates": role_names,
                })

            if is_directory:
                directory_count += 1
                digest.update(f"D\0{relative.as_posix()}\n".encode("utf-8"))
                if is_temporary_candidate(path) and len(temporary_candidates) < MAX_TEMPORARY_CANDIDATES:
                    temporary_candidates.append(relative.as_posix() + "/")
                if path.name.casefold() not in SKIP_DIRECTORIES:
                    child_directories.append(path)
                continue

            if not is_file:
                continue
            stat_result = safe_stat(path)
            if stat_result is None:
                unreadable_count += 1
                continue
            file_count += 1
            total_bytes += int(stat_result.st_size)
            suffix = path.suffix.casefold() or "<none>"
            extensions[suffix] += 1
            digest.update(
                f"F\0{relative.as_posix()}\0{stat_result.st_size}\0{stat_result.st_mtime_ns}\n".encode("utf-8")
            )
            if is_temporary_candidate(path) and len(temporary_candidates) < MAX_TEMPORARY_CANDIDATES:
                temporary_candidates.append(relative.as_posix())
            if file_count >= max_files:
                scan_truncated = True
                break
        if scan_truncated:
            break
        stack.extend(reversed(child_directories))

    role_candidates = {
        role: sorted(dict.fromkeys(paths))
        for role, paths in sorted(roles.items())
    }
    unknown_top_level = sorted(
        row["path"]
        for row in top_level
        if row["role_candidates"] == ["unknown"]
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "inspected",
        "mode": "metadata-only-read",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_root": str(root),
        "workspace_fingerprint_sha256": digest.hexdigest(),
        "scan": {
            "max_files": max_files,
            "file_count": file_count,
            "directory_count": directory_count,
            "total_bytes": total_bytes,
            "scan_truncated": scan_truncated,
            "unreadable_count": unreadable_count,
            "link_or_junction_count": link_count,
            "sensitive_surface_count": sensitive_surface_count,
            "sensitive_contents_inspected": False,
        },
        "top_level": sorted(top_level, key=lambda row: str(row["path"]).casefold()),
        "role_candidates": role_candidates,
        "unknown_top_level": unknown_top_level,
        "temporary_candidates_not_deletion_approval": sorted(temporary_candidates),
        "extension_counts": dict(sorted(extensions.items())),
        "cautions": [
            "Role candidates are name-based hints and require semantic review.",
            "Temporary candidates are not approved deletion targets.",
            "A truncated or unreadable scan cannot support a complete migration or cleanup plan.",
            "The metadata fingerprint detects ordinary drift; it is not a content-integrity signature.",
        ],
    }


def write_json_atomic(path: Path, value: dict[str, object], *, compact: bool) -> None:
    path = path.expanduser().resolve(strict=False)
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"refusing to overwrite inventory output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    if temporary.exists() or temporary.is_symlink():
        raise FileExistsError(f"temporary output already exists: {temporary}")
    text = json.dumps(
        value,
        ensure_ascii=False,
        indent=None if compact else 2,
        separators=(",", ":") if compact else None,
    ) + "\n"
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", help="Research project root to inspect")
    parser.add_argument(
        "--max-files",
        type=int,
        default=DEFAULT_MAX_FILES,
        help=f"Maximum files to inspect, default {DEFAULT_MAX_FILES}, hard limit {HARD_MAX_FILES}",
    )
    parser.add_argument("--output", help="Optional new JSON file; omitted means stdout only")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        payload = build_inventory(Path(args.project), max_files=args.max_files)
        if args.output:
            write_json_atomic(Path(args.output), payload, compact=args.compact)
        else:
            print(json.dumps(
                payload,
                ensure_ascii=False,
                indent=None if args.compact else 2,
                separators=(",", ":") if args.compact else None,
            ))
        return 0
    except (FileExistsError, OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({
            "schema_version": SCHEMA_VERSION,
            "status": "error",
            "error": str(exc),
        }, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
