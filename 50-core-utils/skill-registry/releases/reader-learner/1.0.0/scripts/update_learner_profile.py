#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inspect or manually update a v2 reader-learner knowledge profile."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Iterable

from export_obsidian_vault import DEFAULT_OBSIDIAN_APP, export_vault
from profile_v2 import VALID_STATUSES, clean_text, concept_id_from_label, default_concept, ensure_v2, record_feedback_item, save_json, load_json, utc_now


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def find_profile(start: Path) -> Path:
    for parent in [start.resolve(), *start.resolve().parents]:
        candidate = parent / ".agents" / "reader-learner" / "knowledge_profile.json"
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Could not find .agents/reader-learner/knowledge_profile.json from current path")


def profile_path_from_args(args: argparse.Namespace) -> Path:
    return Path(args.profile).expanduser().resolve() if args.profile else find_profile(Path.cwd())


def cmd_list(args: argparse.Namespace) -> int:
    profile_path = profile_path_from_args(args)
    profile = ensure_v2(load_json(profile_path))
    concepts = profile.get("concepts", {})
    print(f"Profile: {profile_path}")
    print(f"Schema version: {profile.get('version')}")
    print(f"Concepts: {len(concepts)}")
    print(f"Evidence signals: {len(profile.get('events', []))}")
    print(f"Sources: {len(profile.get('sources', {}))}")
    print(f"Review queue: {len(profile.get('review_queue', []))}")
    for concept_id, info in sorted(concepts.items(), key=lambda row: row[0]):
        status = info.get("status", "unrated") if isinstance(info, dict) else "unrated"
        label = info.get("label", concept_id) if isinstance(info, dict) else concept_id
        print(f"- {concept_id}: {status} | {label}")
    return 0


def cmd_mark(args: argparse.Namespace) -> int:
    if args.status not in VALID_STATUSES:
        raise ValueError(f"Invalid status {args.status!r}. Choose one of {sorted(VALID_STATUSES)}")
    profile_path = profile_path_from_args(args)
    profile = ensure_v2(load_json(profile_path))
    concept_id = concept_id_from_label(args.concept)
    concept = profile.setdefault("concepts", {}).setdefault(concept_id, default_concept(concept_id, args.concept))
    concept["label"] = args.concept
    concept["status"] = args.status
    if args.confidence is not None:
        concept["confidence"] = args.confidence
    if args.translation is not None:
        concept["translation"] = args.translation
    if args.note is not None:
        concept["user_note"] = clean_text(args.note, 300)
    if args.explanation is not None:
        concept["ai_explanation"] = clean_text(args.explanation, 1200)
    for alias in args.alias:
        if alias and alias not in concept.setdefault("aliases", []):
            concept["aliases"].append(alias)

    record_feedback_item(profile, {
        "source_kind": "manual_update",
        "paper_title": args.source or "manual profile update",
        "reader_path": args.source or "",
    }, {
        "feedback_id": f"manual::{args.concept}::{utc_now()}",
        "concept": args.concept,
        "status": args.status,
        "note": args.note or "",
        "explanation": args.explanation or "",
        "translation": args.translation or "",
        "block_id": args.block_id or "",
        "annotation_kind": "manual_mark",
        "action": "user_marked" if not args.explanation else "ai_explained",
    })
    profile["updated_at"] = utc_now()
    save_json(profile_path, profile)
    print(f"Updated {concept_id}: {args.status} | {args.concept}")
    print(f"Profile: {profile_path}")
    return 0


def cmd_review(args: argparse.Namespace) -> int:
    profile_path = profile_path_from_args(args)
    # Compatibility shim: teaching ordering belongs to adaptive-teach.  This
    # command remains read-only for existing scripts and never mutates profile data.
    adaptive = Path(__file__).resolve().parents[2] / "adaptive-teach" / "scripts" / "adaptive_teach.py"
    if not adaptive.exists():
        raise FileNotFoundError("adaptive-teach is required for review ordering; install skills/adaptive-teach")
    return subprocess.run(
        [sys.executable, str(adaptive), "review", "--profile", str(profile_path), "--limit", str(args.limit)],
        check=False,
    ).returncode


def cmd_obsidian(args: argparse.Namespace) -> int:
    profile_path = profile_path_from_args(args)
    vault_path = Path(args.vault).expanduser().resolve() if args.vault else None
    result = export_vault(
        profile_path,
        vault=vault_path,
        obsidian_app=Path(args.obsidian_app),
        clean=args.clean,
        include_events=args.include_events,
    )
    print(f"Obsidian vault: {result['vault']}")
    print(f"Profile: {result['profile']}")
    print(f"Knowledge points: {result['concepts']}")
    print(f"Evidence signals: {result['events']}")
    print(f"Sources: {result['sources']}")
    print(f"Include evidence detail notes: {result['include_events']}")
    print(f"Generated files: {result['files']}")
    if result["removed"]:
        print(f"Removed stale files: {result['removed']}")
    for script in result["open_scripts"]:
        print(f"Open script: {script}")
    return 0


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", help="Path to knowledge_profile.json. Defaults to nearest project .agents profile.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List concepts and statuses")
    list_parser.set_defaults(func=cmd_list)

    mark_parser = subparsers.add_parser("mark", help="Mark or update one concept")
    mark_parser.add_argument("--concept", required=True)
    mark_parser.add_argument("--status", required=True, choices=sorted(VALID_STATUSES))
    mark_parser.add_argument("--confidence", type=float)
    mark_parser.add_argument("--translation")
    mark_parser.add_argument("--note", help="Short user-facing note or reading boundary")
    mark_parser.add_argument("--explanation", help="Short AI explanation matched to the user")
    mark_parser.add_argument("--alias", action="append", default=[])
    mark_parser.add_argument("--source")
    mark_parser.add_argument("--block-id")
    mark_parser.set_defaults(func=cmd_mark)

    review_parser = subparsers.add_parser("review", help="List review queue items")
    review_parser.add_argument("--limit", type=int, default=20)
    review_parser.set_defaults(func=cmd_review)

    obsidian_parser = subparsers.add_parser("obsidian", help="Export the profile as an Obsidian vault")
    obsidian_parser.add_argument("--vault", help="Output vault path. Defaults to <profile-dir>/obsidian-vault.")
    obsidian_parser.add_argument("--obsidian-app", default=DEFAULT_OBSIDIAN_APP, help="Path to Obsidian.exe for generated open scripts.")
    obsidian_parser.add_argument("--clean", action="store_true", help="Remove stale files from the previous managed export.")
    obsidian_parser.add_argument("--include-events", action="store_true", help="Also export raw evidence notes. Default keeps Obsidian knowledge-point-first.")
    obsidian_parser.set_defaults(func=cmd_obsidian)
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv or [])
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
