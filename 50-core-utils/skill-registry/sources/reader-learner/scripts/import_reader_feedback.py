#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Import reader/news feedback into .agents/reader-learner/knowledge_profile.json."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

from export_obsidian_vault import DEFAULT_OBSIDIAN_APP, export_vault
from profile_v2 import import_feedback, load_json, save_json


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def find_profile(start: Path) -> Path:
    for parent in [start.resolve(), *start.resolve().parents]:
        candidate = parent / ".agents" / "reader-learner" / "knowledge_profile.json"
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Could not find .agents/reader-learner/knowledge_profile.json")


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", help="Path to knowledge_profile.json. Defaults to nearest project profile.")
    parser.add_argument("--feedback", required=True, help="Path to feedback JSON exported from reader/news HTML.")
    parser.add_argument("--sync-obsidian", action="store_true", help="Also export the profile to an Obsidian vault after import.")
    parser.add_argument("--obsidian-vault", help="Vault path. Defaults to <profile-dir>/obsidian-vault when --sync-obsidian is used.")
    parser.add_argument("--obsidian-app", default=DEFAULT_OBSIDIAN_APP, help="Path to Obsidian.exe for generated open scripts.")
    parser.add_argument("--obsidian-clean", action="store_true", help="Remove stale files from the previous managed Obsidian export.")
    parser.add_argument("--obsidian-include-events", action="store_true", help="Also export raw evidence notes. Default keeps Obsidian knowledge-point-first.")
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] = sys.argv[1:]) -> int:
    args = parse_args(argv)
    feedback_path = Path(args.feedback).expanduser().resolve()
    profile_path = Path(args.profile).expanduser().resolve() if args.profile else find_profile(Path.cwd())
    profile = load_json(profile_path)
    feedback = load_json(feedback_path)
    profile, changed = import_feedback(profile, feedback)
    save_json(profile_path, profile, backup=True)
    print(f"Imported {changed} feedback items")
    print(f"Profile: {profile_path}")
    print(f"Schema version: {profile.get('version')}")
    print(f"Knowledge points: {len(profile.get('concepts', {}))}")
    print(f"Evidence signals: {len(profile.get('events', []))}")
    print(f"Sources: {len(profile.get('sources', {}))}")
    print(f"Review queue: {len(profile.get('review_queue', []))}")
    if args.sync_obsidian or args.obsidian_vault:
        vault_path = Path(args.obsidian_vault).expanduser().resolve() if args.obsidian_vault else None
        result = export_vault(
            profile_path,
            vault=vault_path,
            obsidian_app=Path(args.obsidian_app),
            clean=args.obsidian_clean,
            include_events=args.obsidian_include_events,
        )
        print(f"Obsidian vault: {result['vault']}")
        print(f"Include evidence detail notes: {result['include_events']}")
        print(f"Obsidian files: {result['files']}")
        for script in result["open_scripts"]:
            print(f"Open script: {script}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
