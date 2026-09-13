#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit the reader-learner llm-wiki/profile/vault boundary."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from profile_v2 import (
    FACETS,
    VALID_STATUSES,
    ensure_v2,
    load_json,
    normalize_safe_text,
    save_json,
    utc_now,
    validate_concept_label,
    validate_profile_shape,
)


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


MOJIBAKE_MARKERS = (
    "\ufffd",
    "Ã",
    "Â",
    "ä¸",
    "æ",
    "å",
    "ðŸ",
    "鍝",
    "鐨",
    "涓",
    "绋",
    "閫",
    "浣",
    "妯",
    "璇",
    "噴",
    "枃",
)
HTML_TAG_RE = re.compile(r"<[^>]+>")
PLACEHOLDER_RE = re.compile(r"^[?\s/（）()A-Za-z0-9.-]+$")
REQUIRED_VAULT_FILES = (
    "index.md",
    "log.md",
    "00 Home.md",
    "01 Learning Dashboard.md",
    "Wiki/Knowledge Points.md",
    "Wiki/Glossary.md",
    "Reviews/Review Queue.md",
    "Maps/Knowledge Boundary.md",
    "Maps/Concept Relations.md",
    "_meta/concepts.base",
    "_meta/review-queue.base",
    "wiki-export/reader-learner-graph.json",
    "wiki-export/reader-learner-graph.html",
)
KNOWN_TRANSLATIONS = {
    "gnns": "图神经网络",
    "continuous-time-quantum-walk": "连续时间量子行走",
    "qws": "量子行走",
    "complex-graph-neural-networks": "复值图神经网络",
    "qwgnn": "量子行走复值图神经网络",
    "qwgcn": "量子行走图卷积网络",
    "complex-graph-convolution": "复值图卷积",
    "complex-valued-activation-functions": "复值激活函数",
    "complex-weight-update-strategies": "复值权重更新策略",
    "message-passing-neighborhood-aggregation": "消息传递/邻域聚合",
    "hamiltonian": "哈密顿量",
    "adjacency-matrix": "邻接矩阵",
    "degree-matrix": "度矩阵",
    "graph-laplacian": "图拉普拉斯矩阵",
    "unitary-evolution-operator": "酉演化算符",
    "matrix-exponential": "矩阵指数",
    "taylor-approximation": "泰勒近似",
    "phase-information": "相位信息",
    "quantum-superposition": "量子叠加",
    "quantum-interference": "量子干涉",
    "global-evolution": "全局演化",
    "local-k-hop-aggregation": "局部 k 跳聚合",
    "fidelity": "保真度",
    "f1-score": "F1 分数",
    "mse": "均方误差",
    "protein-structure-datasets": "蛋白质结构数据集",
}


def find_profile(start: Path) -> Path:
    for parent in [start.resolve(), *start.resolve().parents]:
        candidate = parent / ".agents" / "reader-learner" / "knowledge_profile.json"
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Could not find .agents/reader-learner/knowledge_profile.json")


def has_bad_marker(value: Any) -> bool:
    text = str(value or "")
    return any(marker in text for marker in MOJIBAKE_MARKERS) or bool(HTML_TAG_RE.search(text))


def is_placeholder_translation(value: Any) -> bool:
    text = " ".join(str(value or "").split())
    if not text:
        return False
    if "?" in text:
        return True
    return bool(PLACEHOLDER_RE.fullmatch(text)) and not re.search(r"[\u4e00-\u9fff]", text)


def add_issue(issues: list[dict[str, Any]], severity: str, path: str, message: str) -> None:
    issues.append({"severity": severity, "path": path, "message": message})


def repair_known_translations(profile: dict[str, Any], issues: list[dict[str, Any]]) -> int:
    repaired = 0
    concepts = profile.get("concepts", {}) or {}
    for concept_id, translation in KNOWN_TRANSLATIONS.items():
        info = concepts.get(concept_id)
        if not isinstance(info, dict):
            continue
        current = info.get("translation", "")
        if is_placeholder_translation(current) or has_bad_marker(current):
            info["translation"] = translation
            aliases_zh = info.setdefault("aliases_zh", [])
            if isinstance(aliases_zh, list) and translation not in aliases_zh:
                aliases_zh.append(translation)
            repaired += 1
            add_issue(issues, "info", f"concepts.{concept_id}.translation", f"repaired known translation -> {translation}")
    return repaired


def unique_list(values: Iterable[Any]) -> list[Any]:
    seen: set[str] = set()
    result: list[Any] = []
    for value in values or []:
        key = json.dumps(value, ensure_ascii=False, sort_keys=True) if isinstance(value, (dict, list)) else str(value)
        if key not in seen:
            seen.add(key)
            result.append(value)
    return result


def normalize_profile(profile: dict[str, Any], issues: list[dict[str, Any]]) -> dict[str, int]:
    """Compact redundant derived data without discarding canonical concept state."""
    concepts = profile.setdefault("concepts", {})
    events = profile.setdefault("events", [])
    sources = profile.setdefault("sources", {})
    review_queue = profile.setdefault("review_queue", [])
    stats = Counter()

    repaired = repair_known_translations(profile, issues)
    stats["translations_repaired"] += repaired

    deduped_events: list[dict[str, Any]] = []
    seen_event_ids: set[str] = set()
    for idx, event in enumerate(events):
        if not isinstance(event, dict):
            stats["events_removed"] += 1
            add_issue(issues, "info", f"events[{idx}]", "removed non-object event")
            continue
        event_id = str(event.get("event_id") or "").strip()
        if not event_id:
            event_id = f"evt-normalized-{idx:04d}"
            event["event_id"] = event_id
            stats["events_assigned_id"] += 1
        if event_id in seen_event_ids:
            stats["events_removed"] += 1
            add_issue(issues, "info", f"events[{idx}]", f"removed duplicate event {event_id}")
            continue
        seen_event_ids.add(event_id)
        deduped_events.append(event)
    profile["events"] = deduped_events
    event_ids = {event.get("event_id") for event in deduped_events if isinstance(event, dict)}
    source_ids = set(sources)

    for concept_id, info in list(concepts.items()):
        if not isinstance(info, dict):
            concepts.pop(concept_id, None)
            stats["concepts_removed"] += 1
            add_issue(issues, "info", f"concepts.{concept_id}", "removed non-object concept")
            continue
        info["concept_id"] = concept_id
        if info.get("status") not in VALID_STATUSES:
            info["status"] = "unrated"
            stats["statuses_repaired"] += 1
        for field in ("aliases", "aliases_en", "aliases_zh", "learning_needs", "preferred_explanation_styles"):
            if not isinstance(info.get(field, []), list):
                info[field] = []
                stats["list_fields_repaired"] += 1
            cleaned_values: list[Any] = []
            for value in unique_list(info.get(field, [])):
                if field.startswith("aliases"):
                    try:
                        normalized = normalize_safe_text(value, f"concepts.{concept_id}.{field}", 160)
                        validate_concept_label(normalized, f"concepts.{concept_id}.{field}")
                    except ValueError:
                        stats["dirty_aliases_removed"] += 1
                        continue
                    cleaned_values.append(normalized)
                else:
                    cleaned_values.append(value)
            info[field] = cleaned_values
        info["event_ids"] = [event_id for event_id in unique_list(info.get("event_ids", [])) if event_id in event_ids]
        info["source_ids"] = [source_id for source_id in unique_list(info.get("source_ids", [])) if source_id in source_ids]
        for field, limit in (("user_note", 300), ("summary", 1200), ("ai_explanation", 1600)):
            if info.get(field):
                try:
                    info[field] = normalize_safe_text(info[field], f"concepts.{concept_id}.{field}", limit)
                except ValueError:
                    info[field] = ""
                    stats["dirty_text_cleared"] += 1
        if is_placeholder_translation(info.get("translation", "")) and concept_id not in KNOWN_TRANSLATIONS:
            info["translation"] = ""
            stats["placeholder_translations_cleared"] += 1

    for source_id, source in list(sources.items()):
        if not isinstance(source, dict):
            sources.pop(source_id, None)
            stats["sources_removed"] += 1
            continue
        source["event_ids"] = [event_id for event_id in unique_list(source.get("event_ids", [])) if event_id in event_ids]

    compact_queue: dict[tuple[str, str], dict[str, Any]] = {}
    for item in review_queue:
        if not isinstance(item, dict):
            stats["review_items_removed"] += 1
            continue
        concept_id = item.get("concept_id")
        if concept_id not in concepts:
            stats["review_items_removed"] += 1
            continue
        status = item.get("status")
        if status not in {"unknown", "learning"}:
            stats["review_items_removed"] += 1
            continue
        facet = item.get("facet") or "general"
        key = (str(concept_id), str(facet))
        existing = compact_queue.get(key)
        if not existing or int(item.get("priority") or 0) > int(existing.get("priority") or 0):
            item["source_ids"] = [source_id for source_id in unique_list(item.get("source_ids", [])) if source_id in source_ids]
            if item.get("last_event_id") not in event_ids:
                item["last_event_id"] = ""
            compact_queue[key] = item
    stats["review_items_removed"] += max(0, len(review_queue) - len(compact_queue))
    profile["review_queue"] = sorted(compact_queue.values(), key=lambda item: (-int(item.get("priority") or 0), str(item.get("concept_id"))))

    profile["updated_at"] = utc_now()
    return dict(stats)


def audit_profile(profile: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    try:
        validate_profile_shape(profile)
    except Exception as exc:  # noqa: BLE001 - report exact validator failure
        add_issue(issues, "error", "profile", f"profile shape validation failed: {exc}")

    concepts = profile.get("concepts", {}) or {}
    events = profile.get("events", []) or []
    sources = profile.get("sources", {}) or {}
    review_queue = profile.get("review_queue", []) or []
    event_ids = {event.get("event_id") for event in events if isinstance(event, dict)}
    source_ids = set(sources)
    labels = Counter()

    if not concepts:
        add_issue(issues, "error", "concepts", "profile has no concepts")
    if not isinstance(events, list):
        add_issue(issues, "error", "events", "events must be a list")
    if not isinstance(sources, dict):
        add_issue(issues, "error", "sources", "sources must be an object")

    for concept_id, info in concepts.items():
        if not isinstance(info, dict):
            add_issue(issues, "error", f"concepts.{concept_id}", "concept entry must be an object")
            continue
        label = str(info.get("label") or concept_id)
        labels[label.casefold()] += 1
        try:
            validate_concept_label(normalize_safe_text(label, f"concepts.{concept_id}.label", 160), f"concepts.{concept_id}.label")
        except Exception as exc:  # noqa: BLE001
            add_issue(issues, "error", f"concepts.{concept_id}.label", str(exc))
        status = info.get("status", "unrated")
        if status not in VALID_STATUSES:
            add_issue(issues, "error", f"concepts.{concept_id}.status", f"invalid status: {status}")
        translation = info.get("translation", "")
        if is_placeholder_translation(translation):
            add_issue(issues, "error", f"concepts.{concept_id}.translation", "translation is placeholder or question marks")
        elif has_bad_marker(translation):
            add_issue(issues, "error", f"concepts.{concept_id}.translation", "translation contains mojibake/HTML markers")
        for field in ("aliases", "aliases_en", "aliases_zh"):
            values = info.get(field, []) or []
            if not isinstance(values, list):
                add_issue(issues, "error", f"concepts.{concept_id}.{field}", "aliases must be a list")
                continue
            for idx, alias in enumerate(values):
                if has_bad_marker(alias):
                    add_issue(issues, "error", f"concepts.{concept_id}.{field}[{idx}]", "alias contains mojibake/HTML markers")
        for event_id in info.get("event_ids", []) or []:
            if event_id not in event_ids:
                add_issue(issues, "warning", f"concepts.{concept_id}.event_ids", f"missing event: {event_id}")
        for source_id in info.get("source_ids", []) or []:
            if source_id not in source_ids:
                add_issue(issues, "warning", f"concepts.{concept_id}.source_ids", f"missing source: {source_id}")

    for label, count in labels.items():
        if count > 1:
            add_issue(issues, "warning", "concepts", f"duplicate concept label: {label}")

    concept_ids = set(concepts)
    for idx, event in enumerate(events):
        if not isinstance(event, dict):
            add_issue(issues, "error", f"events[{idx}]", "event must be an object")
            continue
        concept_id = event.get("concept_id")
        if concept_id and concept_id not in concept_ids:
            add_issue(issues, "warning", f"events[{idx}].concept_id", f"missing concept: {concept_id}")
        source_id = event.get("source_id")
        if source_id and source_id not in source_ids:
            add_issue(issues, "warning", f"events[{idx}].source_id", f"missing source: {source_id}")
        if has_bad_marker(event.get("raw_concept", "")):
            add_issue(issues, "warning", f"events[{idx}].raw_concept", "raw concept contains mojibake/HTML markers")

    for source_id, source in sources.items():
        if not isinstance(source, dict):
            add_issue(issues, "error", f"sources.{source_id}", "source must be an object")
            continue
        for event_id in source.get("event_ids", []) or []:
            if event_id not in event_ids:
                add_issue(issues, "warning", f"sources.{source_id}.event_ids", f"missing event: {event_id}")

    valid_facets = set(FACETS) | {"general"}
    for idx, item in enumerate(review_queue):
        if not isinstance(item, dict):
            add_issue(issues, "error", f"review_queue[{idx}]", "review item must be an object")
            continue
        concept_id = item.get("concept_id")
        if concept_id not in concept_ids:
            add_issue(issues, "warning", f"review_queue[{idx}].concept_id", f"missing concept: {concept_id}")
        if item.get("status") not in VALID_STATUSES:
            add_issue(issues, "error", f"review_queue[{idx}].status", f"invalid status: {item.get('status')}")
        facet = item.get("facet") or "general"
        if facet not in valid_facets:
            add_issue(issues, "warning", f"review_queue[{idx}].facet", f"unknown facet: {facet}")

    return issues


def audit_vault(vault: Path, profile: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    if not vault.exists():
        add_issue(issues, "warning", "obsidian-vault", "vault does not exist; run obsidian export")
        return issues
    for rel in REQUIRED_VAULT_FILES:
        if not (vault / rel).exists():
            add_issue(issues, "error", f"obsidian-vault/{rel}", "required wiki file is missing")
    index_text = (vault / "index.md").read_text(encoding="utf-8", errors="replace") if (vault / "index.md").exists() else ""
    log_text = (vault / "log.md").read_text(encoding="utf-8", errors="replace") if (vault / "log.md").exists() else ""
    if "[[" not in index_text:
        add_issue(issues, "error", "obsidian-vault/index.md", "index has no wiki links")
    if "## [" not in log_text:
        add_issue(issues, "warning", "obsidian-vault/log.md", "log lacks parseable chronological entries")
    manifest = vault / ".reader-learner-vault-manifest.json"
    if manifest.exists():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            files = data.get("files", [])
            if len(files) < 10:
                add_issue(issues, "warning", "obsidian-vault/.reader-learner-vault-manifest.json", "manifest file count looks too small")
        except json.JSONDecodeError as exc:
            add_issue(issues, "error", "obsidian-vault/.reader-learner-vault-manifest.json", f"manifest JSON is invalid: {exc}")
    else:
        add_issue(issues, "warning", "obsidian-vault/.reader-learner-vault-manifest.json", "managed export manifest missing")
    concept_count = len(profile.get("concepts", {}) or {})
    concept_notes = list((vault / "Concepts").glob("*.md")) if (vault / "Concepts").exists() else []
    if concept_count and len(concept_notes) < max(1, concept_count // 2):
        add_issue(issues, "warning", "obsidian-vault/Concepts", "concept note coverage is unexpectedly low")
    return issues


def summarize(issues: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(issue["severity"] for issue in issues)
    return {"errors": counts.get("error", 0), "warnings": counts.get("warning", 0), "info": counts.get("info", 0)}


def write_reports(report_path: Path, report: dict[str, Any]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path = report_path.with_suffix(".md")
    lines = [
        "# Reader Learner Knowledge Base Audit",
        "",
        f"- status: `{report['status']}`",
        f"- errors: {report['summary']['errors']}",
        f"- warnings: {report['summary']['warnings']}",
        f"- info: {report['summary']['info']}",
        f"- concepts: {report['stats']['concepts']}",
        f"- events: {report['stats']['events']}",
        f"- sources: {report['stats']['sources']}",
        f"- review_queue: {report['stats']['review_queue']}",
        "",
        "## Issues",
        "",
    ]
    if not report["issues"]:
        lines.append("No issues found.")
    for issue in report["issues"][:200]:
        lines.append(f"- `{issue['severity']}` `{issue['path']}`: {issue['message']}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", help="Path to knowledge_profile.json. Defaults to nearest project profile.")
    parser.add_argument("--vault", help="Path to Obsidian vault. Defaults to <profile-dir>/obsidian-vault.")
    parser.add_argument("--report", help="Audit report JSON path. Defaults to <profile-dir>/knowledge_base_audit_report.json.")
    parser.add_argument("--repair-known-translations", action="store_true", help="Repair known placeholder translations using a fixed whitelist.")
    parser.add_argument("--normalize-profile", action="store_true", help="Repair known translations, drop broken references, deduplicate lists/events/review queue, and atomically save a backup.")
    parser.add_argument("--fail-on-warning", action="store_true", help="Exit non-zero on warnings as well as errors.")
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] = sys.argv[1:]) -> int:
    args = parse_args(argv)
    profile_path = Path(args.profile).expanduser().resolve() if args.profile else find_profile(Path.cwd())
    vault = Path(args.vault).expanduser().resolve() if args.vault else profile_path.parent / "obsidian-vault"
    report_path = Path(args.report).expanduser().resolve() if args.report else profile_path.parent / "knowledge_base_audit_report.json"
    profile = ensure_v2(load_json(profile_path))
    issues = audit_profile(profile)
    cleanup_stats: dict[str, int] = {}
    repaired = 0
    if args.normalize_profile:
        cleanup_stats = normalize_profile(profile, issues)
        repaired = cleanup_stats.get("translations_repaired", 0)
    elif args.repair_known_translations:
        repaired = repair_known_translations(profile, issues)
    if args.normalize_profile or repaired:
        save_json(profile_path, profile, backup=True)
        issues = audit_profile(profile) + [issue for issue in issues if issue["severity"] == "info"]
    issues.extend(audit_vault(vault, profile))
    summary = summarize(issues)
    report = {
        "status": "fail" if summary["errors"] or (args.fail_on_warning and summary["warnings"]) else "pass",
        "profile": str(profile_path),
        "vault": str(vault),
        "stats": {
            "concepts": len(profile.get("concepts", {}) or {}),
            "events": len(profile.get("events", []) or []),
            "sources": len(profile.get("sources", {}) or {}),
            "review_queue": len(profile.get("review_queue", []) or []),
            "repaired_known_translations": repaired,
            "cleanup": cleanup_stats,
        },
        "summary": summary,
        "issues": issues,
    }
    write_reports(report_path, report)
    print(json.dumps({k: report[k] for k in ("status", "stats", "summary")}, ensure_ascii=False, indent=2))
    print(f"Audit report: {report_path}")
    print(f"Audit markdown: {report_path.with_suffix('.md')}")
    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
