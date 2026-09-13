#!/usr/bin/env python3
"""Import reviewed feedback into the learner profile, then project it into the visible wiki.

The pipeline deliberately keeps source-layer mutation and knowledge-layer projection separate:
the existing importer validates feedback and creates a profile backup; this wrapper only runs a
full, safe wiki projection after that import succeeds.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable

from compile_visible_wiki import sync
from lint_visible_wiki import lint


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PROFILE = PROJECT_ROOT / ".agents" / "reader-learner" / "knowledge_profile.json"
DEFAULT_WIKI = PROJECT_ROOT / ".agents" / "wiki"
READER_IMPORTER = PROJECT_ROOT / "skills" / "reader-learner" / "scripts" / "import_reader_feedback.py"
NEWS_IMPORTER = PROJECT_ROOT / "skills" / "ai-quantum-news-briefing" / "scripts" / "import_news_feedback.py"
TEACHING_IMPORTER = PROJECT_ROOT / "skills" / "reader-learner" / "scripts" / "import_teaching_feedback.py"


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["sync", "reader-feedback", "news-feedback", "teaching-feedback"])
    parser.add_argument("--profile", default=str(DEFAULT_PROFILE), help="Schema-v2 learner profile")
    parser.add_argument("--wiki", default=str(DEFAULT_WIKI), help="Persistent visible wiki root")
    parser.add_argument("--feedback", help="Reader or news feedback JSON for an import command")
    parser.add_argument(
        "--no-bootstrap",
        action="store_true",
        help="Sync only existing public pages instead of creating missing stable projections",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview sync output without writing. Valid only with the sync command.",
    )
    return parser.parse_args(list(argv))


def run_import(command: str, profile: Path, feedback: Path) -> int:
    if command == "reader-feedback":
        importer = READER_IMPORTER
        args = ["--profile", str(profile), "--feedback", str(feedback)]
    elif command == "news-feedback":
        importer = NEWS_IMPORTER
        args = ["--feedback", str(feedback), "--profile", str(profile)]
    else:
        importer = TEACHING_IMPORTER
        args = ["--feedback", str(feedback), "--profile", str(profile)]
    if not importer.exists():
        raise FileNotFoundError(f"Required importer is missing: {importer}")
    completed = subprocess.run(
        [sys.executable, str(importer), *args],
        cwd=str(PROJECT_ROOT),
        check=False,
    )
    return completed.returncode


def project(profile: Path, wiki: Path, bootstrap: bool, apply: bool) -> tuple[int, dict[str, object]]:
    result = sync(profile, wiki, apply=apply, bootstrap_profile=bootstrap)
    output: dict[str, object] = {
        "applied": apply,
        "bootstrap_profile": bootstrap,
        "changed": result["changed"],
        "coverage": result["manifest"]["coverage"],
        "warnings": result["warnings"],
    }
    if not apply:
        output["validation"] = "deferred until an applied sync"
        return (0 if not result["warnings"] else 2), output
    findings = lint(profile, wiki, require_profile_coverage=bootstrap)
    output["lint_findings"] = findings
    if result["warnings"]:
        return 2, output
    return (0 if not findings else 1), output


def main(argv: Iterable[str] = sys.argv[1:]) -> int:
    args = parse_args(argv)
    if args.dry_run and args.command != "sync":
        raise ValueError("--dry-run is only valid with the sync command")
    if args.command != "sync" and not args.feedback:
        raise ValueError("--feedback is required for a feedback import command")
    profile = Path(args.profile).expanduser().resolve()
    wiki = Path(args.wiki).expanduser().resolve()
    if not profile.exists():
        raise FileNotFoundError(f"Learner profile is missing: {profile}")
    if args.command != "sync":
        feedback = Path(args.feedback).expanduser().resolve()
        if not feedback.exists():
            raise FileNotFoundError(f"Feedback JSON is missing: {feedback}")
        imported = run_import(args.command, profile, feedback)
        if imported:
            return imported
    code, output = project(profile, wiki, bootstrap=not args.no_bootstrap, apply=not args.dry_run)
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
