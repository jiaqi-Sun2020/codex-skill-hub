#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Migrate a legacy knowledge_profile.json to the v2 split schema."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Iterable

from profile_v2 import ensure_v2, load_json, save_json, utc_now


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
    parser.add_argument("--backup", help="Backup path. Defaults beside the profile with a timestamp.")
    parser.add_argument("--no-backup", action="store_true", help="Do not create a backup before writing.")
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] = sys.argv[1:]) -> int:
    args = parse_args(argv)
    profile_path = Path(args.profile).expanduser().resolve() if args.profile else find_profile(Path.cwd())
    old_profile = load_json(profile_path)
    if not args.no_backup:
        stamp = utc_now().replace(":", "").replace("+", "Z")
        backup_path = Path(args.backup).expanduser().resolve() if args.backup else profile_path.with_name(f"{profile_path.stem}.v1-backup-{stamp}.json")
        shutil.copy2(profile_path, backup_path)
        print(f"Backup: {backup_path}")
    new_profile = ensure_v2(old_profile)
    save_json(profile_path, new_profile)
    print(f"Migrated profile: {profile_path}")
    print(f"Schema version: {new_profile.get('version')}")
    print(f"Concepts: {len(new_profile.get('concepts', {}))}")
    print(f"Evidence signals: {len(new_profile.get('events', []))}")
    print(f"Sources: {len(new_profile.get('sources', {}))}")
    print(f"Review queue: {len(new_profile.get('review_queue', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
