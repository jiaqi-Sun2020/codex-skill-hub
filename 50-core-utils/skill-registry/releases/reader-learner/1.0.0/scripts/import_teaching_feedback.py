#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Strictly import an adaptive-teach handoff through the v2 profile writer.

This module deliberately contains no teaching selection, scoring, or scheduling
policy.  It validates a narrow handoff, records actual learner evidence through
``profile_v2.import_feedback``, and persists the already-proposed schedule with
the existing backup + atomic writer.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from profile_v2 import VALID_STATUSES, import_feedback, load_json, normalize_safe_text, save_json, validate_concept_label


EVIDENCE_TYPES = {"self_report", "recognition", "prompted_recall", "unprompted_recall", "direct_application", "transfer", "delayed_recall", "misconception"}


def _text(value: Any, field: str, required: bool = False, limit: int = 1600) -> str:
    if value is None:
        value = ""
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    value = normalize_safe_text(value, field, limit).strip()
    if len(value) > limit:
        raise ValueError(f"{field} exceeds {limit} characters")
    if required and not value:
        raise ValueError(f"{field} is required")
    return value


def validate_teaching_feedback(payload: dict[str, Any], profile: dict[str, Any] | None = None) -> None:
    if not isinstance(payload, dict):
        raise ValueError("teaching feedback must be a JSON object")
    if payload.get("teaching_feedback_version") != 1:
        raise ValueError("teaching_feedback_version must be 1")
    session_id = _text(payload.get("session_id"), "session_id", True, 160)
    if not session_id.startswith("teach-"):
        raise ValueError("session_id must start with 'teach-'")
    concept_id = _text(payload.get("selected_concept_id"), "selected_concept_id", True, 160)
    concept = _text(payload.get("selected_concept_name"), "selected_concept_name", True, 160)
    validate_concept_label(concept, "selected_concept_name")
    if profile is not None and concept_id not in (profile.get("concepts") or {}):
        raise ValueError(f"selected_concept_id is not a stable profile concept: {concept_id}")
    source_refs = payload.get("source_refs")
    if not isinstance(source_refs, list) or not all(isinstance(item, str) and item for item in source_refs):
        raise ValueError("source_refs must be a non-empty list of source IDs")
    if profile is not None and any(item not in (profile.get("sources") or {}) for item in source_refs):
        raise ValueError("source_refs must refer to existing profile sources")
    evidence = payload.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("evidence must be a non-empty list")
    for index, item in enumerate(evidence):
        if not isinstance(item, dict):
            raise ValueError(f"evidence[{index}] must be an object")
        if item.get("evidence_type") not in EVIDENCE_TYPES:
            raise ValueError(f"evidence[{index}].evidence_type is invalid")
        if not isinstance(item.get("prompt_used"), bool):
            raise ValueError(f"evidence[{index}].prompt_used must be boolean")
        _text(item.get("observed_performance"), f"evidence[{index}].observed_performance", True)
        if not isinstance(item.get("confidence"), (int, float)) or not 0 <= item["confidence"] <= 1:
            raise ValueError(f"evidence[{index}].confidence must be in [0, 1]")
    proposed = payload.get("proposed_status_change")
    if proposed not in VALID_STATUSES:
        raise ValueError("proposed_status_change is invalid")
    schedule = payload.get("proposed_review_schedule")
    if not isinstance(schedule, dict):
        raise ValueError("proposed_review_schedule must be an object")
    due_at = _text(schedule.get("due_at"), "proposed_review_schedule.due_at", True, 80)
    try:
        datetime.fromisoformat(due_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("proposed_review_schedule.due_at must be ISO-8601") from exc
    priority = schedule.get("priority")
    if not isinstance(priority, int) or not 0 <= priority <= 100:
        raise ValueError("proposed_review_schedule.priority must be an integer in [0, 100]")
    if _text(payload.get("provenance"), "provenance", True, 500) != "adaptive-teach":
        raise ValueError("provenance must be 'adaptive-teach'")


def handoff_to_profile_feedback(payload: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    concept_id = payload["selected_concept_id"]
    concept = profile["concepts"][concept_id]
    strongest = max(payload["evidence"], key=lambda item: (item["evidence_type"] in {"transfer", "delayed_recall", "direct_application", "unprompted_recall"}, item["confidence"]))
    misconception = _text(payload.get("misconception"), "misconception")
    unresolved = _text(payload.get("unresolved_question"), "unresolved_question")
    source_id = payload["source_refs"][0]
    return {
        "source_kind": "teaching_feedback",
        "paper_title": f"Adaptive teaching session {payload['session_id']}",
        "items": [{
            "feedback_id": f"teaching::{payload['session_id']}::{concept_id}",
            "concept": concept.get("label") or payload["selected_concept_name"],
            "concept_id": concept_id,
            "canonical_concept_id": concept_id,
            "concept_type": "term",
            "status": payload["proposed_status_change"],
            "source_anchor": f"teaching:{payload['session_id']}",
            "annotation_kind": "teaching_evidence",
            "source_excerpt": strongest["observed_performance"],
            "note": f"evidence={strongest['evidence_type']}; prompt_used={str(strongest['prompt_used']).lower()}; confidence={strongest['confidence']}; misconception={misconception}",
            "user_question": unresolved,
            "confusion_type": "term_definition" if misconception else "",
            "action": "teaching_feedback_import",
            "source_id": source_id,
        }],
    }


def persist_schedule(profile: dict[str, Any], payload: dict[str, Any]) -> None:
    concept_id = payload["selected_concept_id"]
    schedule = payload["proposed_review_schedule"]
    concept = profile["concepts"][concept_id]
    queue = profile.setdefault("review_queue", [])
    row = next((item for item in queue if item.get("concept_id") == concept_id and item.get("facet") == "general"), None)
    value = {
        "concept_id": concept_id,
        "label": concept.get("label", concept_id),
        "facet": "general",
        "status": payload["proposed_status_change"],
        "priority": schedule["priority"],
        "reason": "adaptive-teach " + _text(schedule.get("reason"), "proposed_review_schedule.reason", True, 300),
        "due_at": schedule["due_at"],
        "last_event_id": concept.get("event_ids", [""])[-1] if concept.get("event_ids") else "",
        "source_ids": list(payload["source_refs"]),
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }
    if row is None:
        queue.append(value)
    else:
        row.update(value)
    concept["next_review_at"] = value["due_at"]
    concept["review_priority"] = value["priority"]


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--feedback", required=True)
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] = sys.argv[1:]) -> int:
    args = parse_args(argv)
    profile_path, feedback_path = Path(args.profile).resolve(), Path(args.feedback).resolve()
    profile, feedback = load_json(profile_path), load_json(feedback_path)
    validate_teaching_feedback(feedback, profile)
    converted = handoff_to_profile_feedback(feedback, profile)
    updated, changed = import_feedback(profile, converted)
    persist_schedule(updated, feedback)
    save_json(profile_path, updated, backup=True)
    print(json.dumps({"imported": changed, "profile": str(profile_path), "session_id": feedback["session_id"], "review_queue": len(updated.get("review_queue", []))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
