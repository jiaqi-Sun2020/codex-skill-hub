#!/usr/bin/env python3
"""Read-only structural and secret-risk audit for a project Markdown knowledge base."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Iterable


INDEX_NAME = "MEMORY.md"
SOFT_LINES = 150
SOFT_BYTES = 20 * 1024
HARD_LINES = 200
HARD_BYTES = 25 * 1024
MAX_SCAN_BYTES = 5 * 1024 * 1024

SECRET_PATTERNS = [
    (
        "private-key block",
        re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----"),
    ),
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    (
        "provider token",
        re.compile(
            r"\b(?:sk-(?:proj-)?[A-Za-z0-9_-]{16,}|"
            r"gh[pousr]_[A-Za-z0-9]{20,}|"
            r"github_pat_[A-Za-z0-9_]{20,})\b"
        ),
    ),
    (
        "bearer token",
        re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{12,}"),
    ),
    (
        "JWT-like token",
        re.compile(
            r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\."
            r"[A-Za-z0-9_-]{8,}\b"
        ),
    ),
    (
        "secret assignment",
        re.compile(
            r"(?i)\b(api[_-]?key|access[_-]?token|auth[_-]?token|"
            r"refresh[_-]?token|client[_-]?secret|password|passwd|cookie)\b"
            r"\s*[:=]\s*[\"']?[^\s\"']{8,}"
        ),
    ),
    (
        "credential URL",
        re.compile(r"(?i)\b[A-Za-z][A-Za-z0-9+.-]*://[^/\s:@]+:[^/\s@]+@"),
    ),
    (
        "connection string credential",
        re.compile(
            r"(?i)\b(?:mongodb(?:\+srv)?|postgres(?:ql)?|mysql|redis|amqp)"
            r"://[^/\s:@]+:[^/\s@]+@"
        ),
    ),
]

INDEX_ENTRY = re.compile(
    r"^\s*[-*+]\s+\[([^\]]+)\]\(([^)\s]+\.md)(?:#[^)]*)?\)"
    r"(?:\s+[—-]\s+\S.*)?\s*$"
)
HEADING = re.compile(r"^\s{0,3}#{1,6}\s+")
LIST_ENTRY = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+\S")
FRONTMATTER_TYPE = re.compile(r"(?im)^\s*type\s*:\s*([A-Za-z0-9_-]+)\s*$")
ALLOWED_TYPES = {"user", "feedback", "project", "reference"}
INJECTION_PATTERNS = [
    re.compile(r"(?i)\bignore\s+(?:all\s+)?(?:previous|prior)\s+instructions?\b"),
    re.compile(r"(?i)\bdisregard\s+(?:the\s+)?(?:system|developer|user)\b"),
    re.compile(r"(?i)\breveal\s+(?:the\s+)?(?:system|developer)\s+prompt\b"),
    re.compile(r"忽略(?:之前|以上|所有).{0,8}(?:指令|提示)"),
]
INACTIVE_DIRS = {"archive", "retired"}


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
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
        return bool(attributes & 0x400)
    except OSError:
        return True


def first_link_component(path: Path) -> Path | None:
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        if current.exists() and is_link_like(current):
            return current
    return None


def sensitive_name_reason(path: Path, root: Path | None = None) -> str | None:
    try:
        parts = path.relative_to(root).parts if root is not None else (path.name,)
    except ValueError:
        parts = (path.name,)
    for part in parts:
        lower = part.casefold()
        stem = Path(lower).stem
        if lower == ".env" or lower.startswith(".env."):
            return "environment file"
        if Path(lower).suffix in {".pem", ".p12", ".pfx", ".key", ".keystore"}:
            return "key/certificate filename"
        if stem in {
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
            "id_rsa",
        }:
            return "credential-like filename"
    return None


def safe_file_id(path: Path, root: Path) -> str:
    relative = path.relative_to(root).as_posix()
    if sensitive_name_reason(path, root):
        digest = hashlib.sha256(relative.encode("utf-8")).hexdigest()[:12]
        return f"<sensitive-path:{digest}>"
    return relative


def read_utf8(path: Path) -> tuple[int, int, str | None, bool]:
    size = path.stat().st_size
    if size > MAX_SCAN_BYTES:
        with path.open("rb") as fh:
            line_count = sum(1 for _ in fh)
        return size, line_count, None, True
    data = path.read_bytes()
    try:
        return len(data), len(data.splitlines()), data.decode("utf-8-sig"), False
    except UnicodeDecodeError:
        return len(data), len(data.splitlines()), None, False


def safe_reference(raw_reference: str) -> str:
    candidate = Path(raw_reference)
    if sensitive_name_reason(candidate):
        digest = hashlib.sha256(raw_reference.encode("utf-8")).hexdigest()[:12]
        return f"<sensitive-reference:{digest}>"
    for _, pattern in SECRET_PATTERNS:
        if pattern.search(raw_reference):
            digest = hashlib.sha256(raw_reference.encode("utf-8")).hexdigest()[:12]
            return f"<sensitive-reference:{digest}>"
    return raw_reference


def secret_findings(text: str, file_id: str) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for kind, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                findings.append(
                    {"file": file_id, "line": line_number, "kind": kind}
                )
    return findings


def injection_findings(text: str, file_id: str) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if any(pattern.search(line) for pattern in INJECTION_PATTERNS):
            findings.append(
                {"file": file_id, "line": line_number, "kind": "prompt injection"}
            )
    return findings


def frontmatter_type(text: str) -> str | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for end in range(1, min(len(lines), 100)):
        if lines[end].strip() == "---":
            match = FRONTMATTER_TYPE.search("\n".join(lines[1:end]))
            return match.group(1) if match else None
    return None


def is_inactive(path: Path, root: Path) -> bool:
    try:
        return any(part.casefold() in INACTIVE_DIRS for part in path.relative_to(root).parts)
    except ValueError:
        return False


def parse_index_entries(text: str) -> tuple[
    list[tuple[int, str, str]], list[int], list[int]
]:
    entries: list[tuple[int, str, str]] = []
    prose_lines: list[int] = []
    pointerless_list_lines: list[int] = []
    in_comment = False
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if in_comment:
            if "-->" in stripped:
                in_comment = False
            continue
        if stripped.startswith("<!--"):
            if "-->" not in stripped:
                in_comment = True
            continue
        if not stripped or HEADING.match(line):
            continue
        match = INDEX_ENTRY.match(line)
        if match:
            entries.append((line_number, match.group(1).strip(), match.group(2)))
        elif LIST_ENTRY.match(line):
            pointerless_list_lines.append(line_number)
        else:
            prose_lines.append(line_number)
    return entries, prose_lines, pointerless_list_lines


def issue_exit_code(issues: list[dict[str, object]]) -> int:
    severe = {
        "index-hard-limit-exceeded",
        "invalid-utf8",
        "invalid-index-reference",
        "possible-secret-content",
        "possible-prompt-injection",
        "invalid-memory-type",
        "file-too-large-to-scan",
        "unsafe-entry-skipped",
    }
    return 2 if any(item.get("kind") in severe for item in issues) else (1 if issues else 0)


def iter_markdown(root: Path) -> Iterable[Path]:
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            entries = sorted(
                os.scandir(current),
                key=lambda entry: entry.name.casefold(),
            )
        except OSError:
            continue
        child_dirs: list[Path] = []
        for entry in entries:
            try:
                attributes = getattr(
                    entry.stat(follow_symlinks=False),
                    "st_file_attributes",
                    0,
                )
                if entry.is_symlink() or attributes & 0x400:
                    continue
                path = Path(entry.path)
                if entry.is_dir(follow_symlinks=False):
                    child_dirs.append(path)
                elif (
                    entry.is_file(follow_symlinks=False)
                    and path.suffix.casefold() == ".md"
                ):
                    yield path
            except OSError:
                continue
        stack.extend(reversed(child_dirs))


def count_link_entries(root: Path) -> int:
    count = 0
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            entries = list(os.scandir(current))
        except OSError:
            continue
        for entry in entries:
            try:
                attributes = getattr(
                    entry.stat(follow_symlinks=False), "st_file_attributes", 0
                )
                if entry.is_symlink() or attributes & 0x400:
                    count += 1
                elif entry.is_dir(follow_symlinks=False):
                    stack.append(Path(entry.path))
            except OSError:
                count += 1
    return count


def audit_memory(memory_dir: Path) -> dict[str, object]:
    requested_root = memory_dir.expanduser().absolute()
    if is_link_like(requested_root):
        raise ValueError("memory root must be a real directory, not a link or junction")
    root = requested_root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("memory root must be a real directory, not a link or junction")

    index = root / INDEX_NAME
    if not index.is_file() or is_link_like(index):
        raise FileNotFoundError(f"{INDEX_NAME} is missing or not a regular file")

    index_bytes, index_lines, index_text, index_too_large = read_utf8(index)
    report: dict[str, object] = {
        "memory_directory": str(root),
        "index": {
            "path": INDEX_NAME,
            "lines": index_lines,
            "bytes": index_bytes,
            "soft_limit": {"lines": SOFT_LINES, "bytes": SOFT_BYTES},
            "hard_limit": {"lines": HARD_LINES, "bytes": HARD_BYTES},
        },
        "files": [],
        "references": [],
        "issues": [],
        "secret_risks": [],
    }
    issues: list[dict[str, object]] = report["issues"]  # type: ignore[assignment]
    references_report: list[dict[str, object]] = report["references"]  # type: ignore[assignment]
    file_report: list[dict[str, object]] = report["files"]  # type: ignore[assignment]
    risks: list[dict[str, object]] = report["secret_risks"]  # type: ignore[assignment]

    linked_entry_count = count_link_entries(root)
    if linked_entry_count:
        issues.append(
            {
                "kind": "unsafe-entry-skipped",
                "count": linked_entry_count,
            }
        )

    if index_lines > HARD_LINES or index_bytes > HARD_BYTES:
        issues.append({"kind": "index-hard-limit-exceeded"})
    elif index_lines > SOFT_LINES or index_bytes > SOFT_BYTES:
        issues.append({"kind": "index-soft-limit-exceeded"})

    if index_too_large:
        issues.append({"kind": "file-too-large-to-scan", "file": INDEX_NAME})
        index_text = ""
    elif index_text is None:
        issues.append({"kind": "invalid-utf8", "file": INDEX_NAME})
        index_text = ""
    else:
        risks.extend(secret_findings(index_text, INDEX_NAME))

    entries, non_entry_lines, pointerless_lines = parse_index_entries(index_text)
    if non_entry_lines:
        issues.append(
            {
                "kind": "index-prose-or-multiline-entry",
                "lines": non_entry_lines,
            }
        )
    if pointerless_lines:
        issues.append(
            {"kind": "index-entry-without-pointer", "lines": pointerless_lines}
        )

    labels: dict[str, list[int]] = {}
    targets: dict[str, list[int]] = {}
    for line_number, label, raw_reference in entries:
        labels.setdefault(re.sub(r"\s+", " ", label).casefold(), []).append(line_number)
        targets.setdefault(raw_reference.replace("\\", "/").casefold(), []).append(line_number)
    duplicate_labels = [lines for lines in labels.values() if len(lines) > 1]
    duplicate_targets = [lines for lines in targets.values() if len(lines) > 1]
    if duplicate_labels:
        issues.append(
            {"kind": "duplicate-index-entry", "line_groups": duplicate_labels}
        )
    if duplicate_targets:
        issues.append(
            {"kind": "duplicate-index-target", "line_groups": duplicate_targets}
        )

    referenced_files: set[Path] = set()
    for line_number, _label, raw_reference in entries:
        candidate = Path(raw_reference)
        item: dict[str, object] = {
            "line": line_number,
            "reference": safe_reference(raw_reference),
        }
        if candidate.is_absolute():
            item["status"] = "outside-memory-root"
        else:
            unresolved = root / candidate
            resolved = unresolved.resolve(strict=False)
            if first_link_component(unresolved.absolute()) is not None:
                item["status"] = "missing-or-link"
            elif not is_relative_to(resolved, root):
                item["status"] = "outside-memory-root"
            elif not resolved.is_file() or is_link_like(resolved):
                item["status"] = "missing-or-link"
            elif is_inactive(resolved, root):
                item["status"] = "inactive-topic"
            elif sensitive_name_reason(resolved, root):
                item["status"] = "sensitive-path-skipped"
                item["reference"] = safe_file_id(resolved, root)
            else:
                item["status"] = "ok"
                referenced_files.add(resolved)
        references_report.append(item)
        if item["status"] != "ok":
            issues.append(
                {
                    "kind": "invalid-index-reference",
                    "line": line_number,
                    "status": item["status"],
                }
            )

    all_topics: set[Path] = set()
    skipped_sensitive_count = 0
    injection_risks: list[dict[str, object]] = []
    for path in iter_markdown(root):
        if path == index:
            continue
        if sensitive_name_reason(path, root):
            skipped_sensitive_count += 1
            continue
        if not is_inactive(path, root):
            all_topics.add(path.resolve())
        byte_count, line_count, text, too_large = read_utf8(path)
        file_id = safe_file_id(path, root)
        item = {
            "path": file_id,
            "lines": line_count,
            "bytes": byte_count,
        }
        if too_large:
            item["scanned"] = False
            issues.append({"kind": "file-too-large-to-scan", "file": file_id})
        elif text is None:
            item["utf8"] = False
            issues.append({"kind": "invalid-utf8", "file": file_id})
        else:
            item["utf8"] = True
            h1_count = sum(
                1 for line in text.splitlines() if re.match(r"^#\s+\S", line)
            )
            if h1_count > 1:
                issues.append(
                    {
                        "kind": "multiple-top-level-topics",
                        "file": file_id,
                        "heading_count": h1_count,
                    }
                )
            h2_count = sum(
                1 for line in text.splitlines() if re.match(r"^##\s+\S", line)
            )
            if h2_count > 1:
                issues.append(
                    {
                        "kind": "multiple-peer-sections-review",
                        "file": file_id,
                        "heading_count": h2_count,
                    }
                )
            memory_type = frontmatter_type(text)
            if memory_type and memory_type.casefold() not in ALLOWED_TYPES:
                issues.append(
                    {
                        "kind": "invalid-memory-type",
                        "file": file_id,
                        "type": memory_type,
                    }
                )
            risks.extend(secret_findings(text, file_id))
            injection_risks.extend(injection_findings(text, file_id))
        file_report.append(item)

    orphans = sorted(
        path.relative_to(root).as_posix()
        for path in all_topics - referenced_files
    )
    if orphans:
        issues.append({"kind": "unindexed-topic-files", "files": orphans})
    if skipped_sensitive_count:
        issues.append(
            {
                "kind": "sensitive-filename-files-skipped",
                "count": skipped_sensitive_count,
            }
        )
    if risks:
        issues.append({"kind": "possible-secret-content", "count": len(risks)})
    if injection_risks:
        issues.append(
            {"kind": "possible-prompt-injection", "count": len(injection_risks)}
        )
        report["injection_risks"] = injection_risks

    exit_code = issue_exit_code(issues)
    report["summary"] = {
        "status": "issues_found" if issues else "clean",
        "markdown_files": len(file_report) + 1,
        "referenced_topic_files": len(referenced_files),
        "issue_count": len(issues),
        "secret_risk_count": len(risks),
        "injection_risk_count": len(injection_risks),
        "exit_code": exit_code,
    }
    return report


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("memory_directory", help="Verified memory directory")
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Emit compact JSON instead of indented JSON",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        report = audit_memory(Path(args.memory_directory))
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"error: memory audit could not start: {type(exc).__name__}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=None if args.compact else 2,
            sort_keys=True,
        )
    )
    return int(report["summary"]["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
