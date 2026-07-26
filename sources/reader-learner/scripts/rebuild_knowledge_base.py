#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild reader-learner profile/wiki from raw feedback JSON files."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from audit_knowledge_base import audit_profile, audit_vault, normalize_profile, summarize, write_reports
from export_obsidian_vault import DEFAULT_OBSIDIAN_APP, export_vault
from profile_v2 import (
    VALID_CONCEPT_TYPES,
    VALID_STATUSES,
    concept_id_from_label,
    empty_profile_v2,
    import_feedback,
    normalize_safe_text,
    save_json,
    valid_status,
    validate_concept_label,
)


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def clean_text(value: Any, limit: int = 4000) -> str:
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", str(value or ""))
    return " ".join(text.split()).strip()[:limit]


def find_profile(start: Path) -> Path:
    for parent in [start.resolve(), *start.resolve().parents]:
        candidate = parent / ".agents" / "reader-learner" / "knowledge_profile.json"
        if candidate.exists():
            return candidate
    return Path.cwd() / ".agents" / "reader-learner" / "knowledge_profile.json"


def candidate_feedback_files(roots: list[Path]) -> list[Path]:
    candidates: list[Path] = []
    for root in roots:
        if root.is_file():
            candidates.append(root)
            continue
        if not root.exists():
            continue
        for path in root.rglob("*.json"):
            name = path.name.lower()
            if "feedback" not in name and "nwes" not in name:
                continue
            if "feedback_config" in name or "audit_report" in name:
                continue
            candidates.append(path)
    preferred: dict[Path, Path] = {}
    direct: list[Path] = []
    for path in sorted(set(candidates), key=lambda p: str(p).lower()):
        name = path.name.lower()
        if name == "news_feedback_reader_feedback.json":
            preferred[path.parent] = path
            continue
        if name == "news_feedback.json":
            preferred.setdefault(path.parent, path)
            continue
        direct.append(path)
    selected = direct + list(preferred.values())
    return sorted(set(selected), key=lambda p: str(p).lower())


def source_excerpt(item: dict[str, Any]) -> str:
    parts: list[str] = []
    category = clean_text(item.get("category"), 200)
    title = clean_text(item.get("source_title"), 500)
    url = clean_text(item.get("source_url"), 1000)
    excerpt = clean_text(item.get("source_excerpt") or item.get("excerpt") or item.get("note"), 2400)
    if category:
        parts.append(f"Category: {category}")
    if title:
        parts.append(f"Source title: {title}")
    if url:
        parts.append(f"Source URL: {url}")
    if excerpt:
        parts.append(f"Context: {excerpt}")
    return "\n".join(parts)


def infer_concept_type(item: dict[str, Any]) -> str:
    concept_type = clean_text(item.get("concept_type"), 80)
    if concept_type in VALID_CONCEPT_TYPES:
        return concept_type
    annotation_kind = clean_text(item.get("annotation_kind"), 80)
    if annotation_kind == "freeform":
        return "freeform"
    if annotation_kind == "news_concept":
        return "term"
    return "term"


def upgrade_item(item: dict[str, Any], idx: int, *, source_kind: str) -> dict[str, Any]:
    concept = clean_text(item.get("concept") or item.get("term") or item.get("topic") or item.get("selected_text"), 600)
    if not concept:
        raise ValueError(f"item {idx} has no concept/term/topic/selected_text")
    block_id = clean_text(
        item.get("source_anchor")
        or item.get("block_id")
        or item.get("bilingual_block_id")
        or item.get("category")
        or f"item-{idx:03d}",
        160,
    )
    source_anchor = clean_text(item.get("source_anchor") or block_id, 160)
    status = valid_status(item.get("status"))
    annotation_kind = clean_text(item.get("annotation_kind") or ("news_concept" if source_kind == "news_briefing" else "concept"), 120)
    concept_type = infer_concept_type(item)
    try:
        concept = normalize_safe_text(concept, f"items[{idx}].concept", 160)
        validate_concept_label(concept, f"items[{idx}].concept")
    except ValueError:
        if annotation_kind != "freeform":
            raise
        concept = f"freeform annotation {source_anchor}"
        concept_type = "freeform"
    upgraded = dict(item)
    upgraded.update({
        "feedback_id": clean_text(item.get("feedback_id") or f"{source_kind}::{concept}::{source_anchor}", 500),
        "concept": concept,
        "concept_id": clean_text(item.get("concept_id") or concept_id_from_label(concept), 160),
        "concept_type": concept_type,
        "status": status if status in VALID_STATUSES else "unrated",
        "source_anchor": source_anchor,
        "block_id": block_id,
        "bilingual_block_id": clean_text(item.get("bilingual_block_id") or block_id, 160),
        "annotation_kind": annotation_kind,
        "source_excerpt": clean_text(item.get("source_excerpt") or source_excerpt(item), 2200),
        "selected_text": clean_text(item.get("selected_text") or "", 1600),
        "selected_language": clean_text(item.get("selected_language") or ("news" if source_kind == "news_briefing" else ""), 80),
        "original_context": clean_text(item.get("original_context") or item.get("source_excerpt") or source_excerpt(item), 2200),
        "translation_context": clean_text(item.get("translation_context"), 2200),
        "note": clean_text(item.get("note"), 1600),
        "user_question": clean_text(item.get("user_question") or item.get("question"), 1600),
        "confusion_type": clean_text(item.get("confusion_type") or item.get("question_type"), 200),
        "explanation_style": clean_text(item.get("explanation_style"), 200),
        "needs_explanation": bool(item.get("needs_explanation") or item.get("user_question") or status in {"unknown", "learning"}),
        "source_kind": source_kind,
    })
    return upgraded


def upgrade_feedback(payload: dict[str, Any], path: Path) -> dict[str, Any] | None:
    if not isinstance(payload.get("items"), list):
        return None
    if not payload.get("items"):
        return None
    source_kind = clean_text(payload.get("source_kind"), 120)
    if not source_kind:
        source_kind = "news_briefing" if payload.get("news_feedback_version") or "news_feedback" in path.name.lower() else "reader_feedback"
    title = clean_text(
        payload.get("paper_title")
        or payload.get("briefing_title")
        or payload.get("title")
        or path.parent.name,
        500,
    )
    reader_path = clean_text(payload.get("reader_path") or payload.get("briefing_path") or str(path), 1000)
    upgraded_items = [upgrade_item(item, idx, source_kind=source_kind) for idx, item in enumerate(payload["items"], start=1) if isinstance(item, dict)]
    return {
        "reader_feedback_version": 2,
        "source_kind": source_kind,
        "paper_title": title,
        "reader_path": reader_path,
        "briefing_title": clean_text(payload.get("briefing_title") or title, 500),
        "date_range": clean_text(payload.get("date_range") or payload.get("date") or "", 120),
        "created_at": clean_text(payload.get("created_at") or payload.get("exported_at") or utc_now(), 120),
        "items": upgraded_items,
    }


def rebuild_profile(feedback_files: list[Path], normalized_dir: Path | None = None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    profile = empty_profile_v2()
    imports: list[dict[str, Any]] = []
    for path in feedback_files:
        payload = load_json(path)
        upgraded = upgrade_feedback(payload, path)
        if upgraded is None:
            imports.append({"path": str(path), "status": "skipped", "reason": "not a feedback payload with items"})
            continue
        if normalized_dir:
            path_hash = hashlib.sha1(str(path).encode("utf-8", errors="replace")).hexdigest()[:10]
            out = normalized_dir / f"{path.stem.replace(' ', '_')}_{path_hash}_normalized_reader_feedback.json"
            write_json(out, upgraded)
        before_events = len(profile.get("events", []))
        profile, changed = import_feedback(profile, upgraded)
        imports.append({
            "path": str(path),
            "status": "imported",
            "source_kind": upgraded.get("source_kind"),
            "items": len(upgraded["items"]),
            "changed": changed,
            "events_added": len(profile.get("events", [])) - before_events,
        })
    issues: list[dict[str, Any]] = []
    normalize_profile(profile, issues)
    return profile, imports


def write_rebuild_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Reader Learner Rebuild Report",
        "",
        f"- status: `{report['status']}`",
        f"- feedback files imported: {report['imported_files']}",
        f"- feedback files skipped: {report['skipped_files']}",
        f"- concepts: {report['stats']['concepts']}",
        f"- events: {report['stats']['events']}",
        f"- sources: {report['stats']['sources']}",
        f"- review_queue: {report['stats']['review_queue']}",
        "",
        "## Imports",
        "",
    ]
    for item in report["imports"]:
        lines.append(f"- `{item['status']}` `{item['path']}` items={item.get('items', 0)} changed={item.get('changed', 0)}")
        if item.get("reason"):
            lines.append(f"  reason: {item['reason']}")
    path.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", help="Path to knowledge_profile.json. Defaults to nearest project profile.")
    parser.add_argument("--feedback-root", action="append", default=[], help="Feedback file or directory. Can be repeated.")
    parser.add_argument("--normalized-dir", help="Optional directory for upgraded normalized feedback payloads.")
    parser.add_argument("--report", help="Rebuild report JSON path. Defaults to <profile-dir>/knowledge_base_rebuild_report.json.")
    parser.add_argument("--sync-obsidian", action="store_true", help="Regenerate Obsidian vault after rebuild.")
    parser.add_argument("--obsidian-clean", action="store_true", help="Remove stale managed vault files during Obsidian export.")
    parser.add_argument("--obsidian-app", default=DEFAULT_OBSIDIAN_APP)
    parser.add_argument("--audit", action="store_true", help="Run final audit report after rebuild/export.")
    parser.add_argument("--fail-on-warning", action="store_true", help="Final audit fails on warnings.")
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] = sys.argv[1:]) -> int:
    args = parse_args(argv)
    profile_path = Path(args.profile).expanduser().resolve() if args.profile else find_profile(Path.cwd())
    roots = [Path(value).expanduser().resolve() for value in args.feedback_root]
    if not roots:
        raise ValueError("At least one --feedback-root is required")
    feedback_files = candidate_feedback_files(roots)
    normalized_dir = Path(args.normalized_dir).expanduser().resolve() if args.normalized_dir else None
    profile, imports = rebuild_profile(feedback_files, normalized_dir)
    save_json(profile_path, profile, backup=True)
    vault_result: dict[str, Any] | None = None
    if args.sync_obsidian:
        vault_result = export_vault(profile_path, obsidian_app=Path(args.obsidian_app), clean=args.obsidian_clean)
    profile_dir = profile_path.parent
    report_path = Path(args.report).expanduser().resolve() if args.report else profile_dir / "knowledge_base_rebuild_report.json"
    imported = [item for item in imports if item["status"] == "imported"]
    skipped = [item for item in imports if item["status"] == "skipped"]
    report = {
        "status": "pass",
        "profile": str(profile_path),
        "feedback_roots": [str(root) for root in roots],
        "imports": imports,
        "imported_files": len(imported),
        "skipped_files": len(skipped),
        "stats": {
            "concepts": len(profile.get("concepts", {}) or {}),
            "events": len(profile.get("events", []) or []),
            "sources": len(profile.get("sources", {}) or {}),
            "review_queue": len(profile.get("review_queue", []) or []),
        },
        "vault": {key: str(value) for key, value in (vault_result or {}).items() if key in {"profile", "vault"}},
    }
    write_rebuild_report(report_path, report)
    print(json.dumps({key: report[key] for key in ("status", "imported_files", "skipped_files", "stats")}, ensure_ascii=False, indent=2))
    print(f"Rebuild report: {report_path}")
    if args.audit:
        final_profile = load_json(profile_path)
        audit_issues = audit_profile(final_profile)
        vault = profile_dir / "obsidian-vault"
        audit_issues.extend(audit_vault(vault, final_profile))
        summary = summarize(audit_issues)
        audit_stats = dict(report["stats"])
        audit_stats.update({"repaired_known_translations": 0, "cleanup": {}})
        audit_report = {
            "status": "fail" if summary["errors"] or (args.fail_on_warning and summary["warnings"]) else "pass",
            "profile": str(profile_path),
            "vault": str(vault),
            "stats": audit_stats,
            "summary": summary,
            "issues": audit_issues,
        }
        audit_path = profile_dir / "knowledge_base_audit_report.json"
        write_reports(audit_path, audit_report)
        print(json.dumps({key: audit_report[key] for key in ("status", "summary")}, ensure_ascii=False, indent=2))
        print(f"Audit report: {audit_path}")
        if audit_report["status"] == "fail":
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
