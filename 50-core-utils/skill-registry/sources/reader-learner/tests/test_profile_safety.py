#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Safety tests for reader-learner profile imports."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "skills" / "reader-learner" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from profile_v2 import (  # noqa: E402
    empty_profile_v2,
    import_feedback,
    load_json,
    normalize_safe_text,
    save_json,
    validate_concept_label,
)
from audit_knowledge_base import audit_profile, normalize_profile  # noqa: E402


def provenance() -> dict:
    return {
        "source_map": {"path": r"C:\reader\source_map.json", "sha256": "a" * 64},
        "completion_ledger": {"path": r"C:\reader\reader_wiki\completion_ledger.json", "sha256": "b" * 64},
        "reader_manifest": {"path": r"C:\reader\reader_wiki\reader_manifest.json", "sha256": "c" * 64},
        "structure_validation_report": {"path": r"C:\reader\reader_wiki\structure_validation_report.json", "sha256": "d" * 64},
    }


def valid_feedback() -> dict:
    return {
        "reader_feedback_version": 2,
        "paper_title": "Clean Reader",
        "reader_path": r"C:\reader",
        "bundle_provenance": provenance(),
        "items": [
            {
                "feedback_id": "concept::Hamiltonian::S001",
                "concept": "Hamiltonian",
                "concept_id": "hamiltonian",
                "concept_type": "math_object",
                "alias_zh": "哈密顿量",
                "status": "learning",
                "source_anchor": "S001",
                "block_id": "S001",
                "bilingual_block_id": "S001",
                "annotation_kind": "concept",
                "source_excerpt": "Hamiltonian directly generates graph dynamics.",
                "selected_text": "",
                "selected_language": "original",
                "original_context": "Hamiltonian directly generates graph dynamics.",
                "translation_context": "哈密顿量直接生成图动力学。",
                "note": "Need paper-specific usage.",
                "user_question": "How is it made learnable here?",
            }
        ],
    }


def expect_value_error(fn, needle: str) -> None:
    try:
        fn()
    except ValueError as exc:
        if needle not in str(exc):
            raise AssertionError(f"expected {needle!r}, got {exc}") from exc
        return
    raise AssertionError(f"expected ValueError containing {needle!r}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="reader_profile_", dir=ROOT) as tmp:
        base = Path(tmp)
        profile_path = base / "knowledge_profile.json"
        profile = empty_profile_v2()
        profile["concepts"]["hamiltonian"] = {
            "concept_id": "hamiltonian",
            "label": "Hamiltonian",
            "aliases": ["Hamiltonian"],
            "aliases_en": ["Hamiltonian"],
            "aliases_zh": ["哈密顿量"],
            "translation": "哈密顿量",
            "status": "known",
        }
        save_json(profile_path, profile)
        raw = profile_path.read_text(encoding="utf-8")
        if "\\u54c8" in raw or "哈密顿量" not in raw:
            raise AssertionError("save_json did not preserve UTF-8 Chinese with ensure_ascii=False")
        loaded = load_json(profile_path)

        normalized = normalize_safe_text("Trans- former &lt;b&gt;attention&lt;/b&gt;", "concept", 120)
        if normalized != "Transformer attention":
            raise AssertionError(f"normalizer failed: {normalized}")
        validate_concept_label("TLS 1.3", "concept")

        imported, changed = import_feedback(loaded, valid_feedback())
        if changed != 1:
            raise AssertionError("valid feedback was not imported")
        concept = imported["concepts"]["hamiltonian"]
        if "Hamiltonian" not in concept.get("aliases_en", []):
            raise AssertionError("aliases_en was not maintained")
        if "哈密顿量" not in concept.get("aliases_zh", []):
            raise AssertionError("aliases_zh was not maintained")

        missing_provenance = valid_feedback()
        del missing_provenance["bundle_provenance"]
        expect_value_error(lambda: import_feedback(empty_profile_v2(), missing_provenance), "bundle_provenance")

        bad_status = valid_feedback()
        bad_status["items"][0]["status"] = "maybe"
        expect_value_error(lambda: import_feedback(empty_profile_v2(), bad_status), "status is invalid")

        missing_anchor = valid_feedback()
        del missing_anchor["items"][0]["source_anchor"]
        expect_value_error(lambda: import_feedback(empty_profile_v2(), missing_anchor), "source_anchor is required")

        missing_metadata = valid_feedback()
        del missing_metadata["items"][0]["concept_type"]
        expect_value_error(lambda: import_feedback(empty_profile_v2(), missing_metadata), "concept_type is required")

        mojibake = valid_feedback()
        mojibake["items"][0]["concept"] = "脙 quantum"
        expect_value_error(lambda: import_feedback(empty_profile_v2(), mojibake), "mojibake")

        control = valid_feedback()
        control["items"][0]["concept"] = "Bad\x01Concept"
        expect_value_error(lambda: import_feedback(empty_profile_v2(), control), "control")

        html_fragment = valid_feedback()
        html_fragment["items"][0]["concept"] = "<span>Hamiltonian</span>"
        expect_value_error(lambda: import_feedback(empty_profile_v2(), html_fragment), "HTML")

        sentence = valid_feedback()
        sentence["items"][0]["concept"] = "Why does this Hamiltonian work?"
        expect_value_error(lambda: import_feedback(empty_profile_v2(), sentence), "sentence")

        before = json.dumps(empty_profile_v2(), ensure_ascii=False, sort_keys=True)
        profile_for_bad = empty_profile_v2()
        expect_value_error(lambda: import_feedback(profile_for_bad, mojibake), "mojibake")
        after = json.dumps(profile_for_bad, ensure_ascii=False, sort_keys=True)
        if before != after:
            raise AssertionError("invalid feedback mutated profile")

        dirty_profile = empty_profile_v2()
        dirty_profile["concepts"]["hamiltonian"] = {
            "concept_id": "hamiltonian",
            "label": "Hamiltonian",
            "status": "learning",
            "translation": "????",
            "aliases": ["Hamiltonian", "This is a whole sentence, not an alias:"],
            "aliases_en": ["Hamiltonian"],
            "aliases_zh": [],
            "event_ids": ["missing-event"],
            "source_ids": ["missing-source"],
        }
        issues = audit_profile(dirty_profile)
        if not any("translation" in issue["path"] for issue in issues):
            raise AssertionError("audit did not catch placeholder translation")
        cleanup = normalize_profile(dirty_profile, issues)
        if cleanup.get("translations_repaired") != 1:
            raise AssertionError("normalize_profile did not repair known translation")
        if dirty_profile["concepts"]["hamiltonian"]["translation"] != "哈密顿量":
            raise AssertionError("known translation repair wrote wrong value")
        if len(dirty_profile["concepts"]["hamiltonian"]["aliases"]) != 1:
            raise AssertionError("dirty sentence alias was not removed")
        if dirty_profile["concepts"]["hamiltonian"]["event_ids"]:
            raise AssertionError("broken event reference was not pruned")

    print("reader-learner safety passed: UTF-8, normalization, provenance, schema validation, and fail-fast imports.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
