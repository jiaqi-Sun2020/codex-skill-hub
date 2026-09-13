#!/usr/bin/env python3
"""Adversarial smoke tests for the persistent visible-wiki projection."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "skills" / "reader-learner" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from compile_visible_wiki import sync  # noqa: E402
from lint_visible_wiki import lint  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def page(
    page_id: str,
    page_type: str,
    title: str,
    source_refs: list[str],
    profile_source_refs: list[str] | None = None,
    body: str = "# Test\n",
) -> str:
    return "\n".join([
        "---",
        f'id: "{page_id}"',
        f'type: "{page_type}"',
        f'title: "{title}"',
        'visibility: "public-wiki"',
        f"source_refs: {json.dumps(source_refs)}",
        f"profile_source_refs: {json.dumps(profile_source_refs or [])}",
        "relations: []",
        'updated: "2026-07-13"',
        "---",
        "",
        body,
    ])


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="visible_wiki_", dir=ROOT) as temp:
        root = Path(temp)
        profile_path = root / "knowledge_profile.json"
        profile_path.write_text(json.dumps({
            "version": 2,
            "updated_at": "2026-07-13T00:00:00Z",
            "concepts": {
                "ansatz": {
                    "concept_id": "ansatz",
                    "status": "unknown",
                    "last_seen_at": "2026-07-13T00:00:00Z",
                    "source_ids": ["src-paper"],
                    "review_priority": 90,
                }
            },
            "sources": {
                "src-paper": {"source_kind": "reader_feedback", "last_seen_at": "2026-07-13T00:00:00Z"}
            },
        }, ensure_ascii=False), encoding="utf-8")
        profile_snapshot = profile_path.read_text(encoding="utf-8")
        wiki = root / "wiki"
        write(wiki / "concepts" / "ansatz.md", page("concept.ansatz", "concept", "ansatz", ["source.paper"]))
        write(wiki / "sources" / "paper.md", page("source.paper", "source", "Paper", [], ["src-paper"]))
        result = sync(profile_path, wiki, apply=True)
        if result["warnings"]:
            raise AssertionError(result["warnings"])
        if profile_path.read_text(encoding="utf-8") != profile_snapshot:
            raise AssertionError("visible-wiki projection mutated the learner profile")
        findings = lint(profile_path, wiki)
        if findings:
            raise AssertionError(findings)
        text = (wiki / "concepts" / "ansatz.md").read_text(encoding="utf-8")
        if 'knowledge_status: "unknown"' not in text or "BEGIN PROFILE PROJECTION" not in text:
            raise AssertionError("profile projection was not written")
        manifest = (wiki / "_internal" / "projection_manifest.json").read_text(encoding="utf-8")
        if "knowledge_profile.json" in manifest or "C:\\" in manifest:
            raise AssertionError("manifest leaked a local absolute path")
        write(
            wiki / "concepts" / "bad.md",
            page(
                "concept.freeform-annotation-s001",
                "concept",
                "bad",
                ["source.paper"],
                body="# Test\nC:\\raw-source\\feedback.json\n",
            ),
        )
        findings = lint(profile_path, wiki)
        messages = {item["message"] for item in findings}
        if not any("raw annotation" in message for message in messages):
            raise AssertionError("raw freeform annotation was accepted as a public concept")
        if not any("absolute local path" in message for message in messages):
            raise AssertionError("absolute local path was accepted in a public page")
        if not any("isolated" in message for message in messages):
            raise AssertionError("isolated public page was accepted")
    print("visible wiki tests: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
