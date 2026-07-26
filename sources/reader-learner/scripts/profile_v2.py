#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared v2 learner-profile model helpers."""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


VALID_STATUSES = {"mastered", "known", "learning", "unknown", "unrated"}
STATUS_ORDER = {"unrated": 0, "unknown": 1, "learning": 2, "known": 3, "mastered": 4}
REVIEW_STATUSES = {"unknown", "learning"}
CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
HTML_TAG_RE = re.compile(r"<[^>]+>")
MOJIBAKE_RE = re.compile(r"(Ã|Â|ä¸|æ|å|ðŸ|脙|脗|锟|閿|閳|鑴|娑|缁|鈭|脳|涓|绫|鍥|鐭|噴)")
SOURCE_INDEX_RE = re.compile(r"\b(p\.?\s*\d+|source\s+page|source\s+index|source:\s*p\.)\b", re.I)
SECTION_HEADING_RE = re.compile(r"^(abstract|introduction|related work|method|methods|experiment|experiments|results|conclusion|references|acknowledg(e)?ments|appendix|keywords)\b", re.I)
SENTENCE_PUNCT_RE = re.compile(r"[。！？；：!?;:]")
PDF_HYPHEN_RE = re.compile(r"(?<=[A-Za-z])-\s+(?=[A-Za-z])")
VALID_CONCEPT_TYPES = {
    "model_module",
    "math_object",
    "formula_variable",
    "method_component",
    "figure_element",
    "metric",
    "baseline",
    "ablation",
    "claim",
    "contribution",
    "term",
    "freeform",
}

FACETS = [
    "definition",
    "paper_usage",
    "math_derivation",
    "algorithm_step",
    "assumption",
    "evidence_interpretation",
    "relation",
    "english_term",
    "physical_intuition",
]

CONFUSION_TO_FACET = {
    "term_definition": "definition",
    "paper_usage": "paper_usage",
    "math_step": "math_derivation",
    "algorithm_step": "algorithm_step",
    "assumption": "assumption",
    "evidence": "evidence_interpretation",
    "relation": "relation",
    "english_term": "english_term",
    "physical_intuition": "physical_intuition",
}

BLOCK_CONCEPT_HINTS = {
    "S005": ("two-electron Hamiltonian representation", "双电子哈密顿量表示"),
    "S006": ("two-electron reduced Hamiltonian", "双电子约化哈密顿量"),
    "S009": ("TDCSE-TDSE equivalence", "TDCSE 与 TDSE 等价性"),
    "S011": ("anti-Hermitian two-electron generator", "反厄米双电子生成元"),
    "S016": ("CETE residual-gradient update", "CETE 残差/梯度更新"),
    "S017": ("H2 CETE simulation setup", "H2 的 CETE 模拟设置"),
    "S018": ("Slater determinant qubit mapping", "Slater 行列式到量子比特映射"),
    "F001": ("1-RDM measurement evidence", "1-RDM 测量证据"),
    "F002": ("H2 energy measurement evidence", "H2 能量测量证据"),
    "S022": ("paper acknowledgments", "论文致谢信息"),
}

KNOWN_TERM_HINTS = [
    ("correlation-efficient time-evolution (CETE) algorithm", "CETE algorithm", "相关高效时间演化算法"),
    ("time-dependent Schrödinger equation (TDSE)", "TDSE", "含时薛定谔方程"),
    ("time-dependent contracted Schrödinger equation (TDCSE)", "TDCSE", "含时收缩薛定谔方程"),
    ("one-particle reduced density matrix (1-RDM)", "1-RDM", "单粒子约化密度矩阵"),
    ("two-particle reduced density matrix (2-RDM)", "2-RDM", "双粒子约化密度矩阵"),
    ("Pauli-sum tomography", "Pauli-sum tomography", "Pauli 和层析"),
    ("sequential short-time propagators", "sequential short-time propagators", "序列短时传播子"),
    ("two-electron unitary", "two-electron unitary", "双电子酉算符"),
    ("Slater determinant", "Slater determinant", "Slater 行列式"),
    ("ansatz", "ansatz", "拟设"),
    ("ibm_fez", "ibm_fez", "ibm_fez"),
    ("Hamiltonian simulation", "Hamiltonian simulation", "哈密顿量模拟"),
    ("continuous-time quantum walk", "continuous-time quantum walk", "连续时间量子行走"),
    ("CTQWformer", "CTQWformer", "CTQWformer"),
    ("Quantum Walk GNN", "Quantum Walk GNN", "量子行走图神经网络"),
    ("quantum error correction", "quantum error correction", "量子纠错"),
    ("block-encoding", "block-encoding", "块编码"),
    ("QSVT", "QSVT", "量子奇异值变换"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def clean_text(value: Any, limit: int = 4000) -> str:
    return " ".join(str(value or "").split()).strip()[:limit]


def normalize_text(value: Any, limit: int = 4000) -> str:
    text = html.unescape(str(value or ""))
    text = HTML_TAG_RE.sub(" ", text)
    text = PDF_HYPHEN_RE.sub("", text)
    text = " ".join(text.split()).strip()
    return text[:limit]


def reject_bad_text(text: str, field: str) -> None:
    if "\ufffd" in text:
        raise ValueError(f"{field} contains replacement character U+FFFD")
    if CONTROL_CHAR_RE.search(text):
        raise ValueError(f"{field} contains invisible/control characters")
    compact = re.sub(r"\s+", "", text)
    if compact and set(compact) <= {"?"}:
        raise ValueError(f"{field} contains placeholder question marks")
    if MOJIBAKE_RE.search(text):
        raise ValueError(f"{field} contains likely mojibake/PDF extraction noise: {text[:80]}")


def normalize_safe_text(value: Any, field: str, limit: int = 4000) -> str:
    text = normalize_text(value, limit)
    reject_bad_text(text, field)
    return text


def safe_optional_text(value: Any, field: str, limit: int = 4000) -> str:
    try:
        return normalize_safe_text(value, field, limit)
    except ValueError:
        return ""


def is_probably_chinese(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def validate_concept_label(label: str, field: str = "concept") -> None:
    if not label:
        raise ValueError(f"{field} is empty")
    reject_bad_text(label, field)
    lowered = label.lower()
    if HTML_TAG_RE.search(label) or "&lt;" in lowered or "&gt;" in lowered:
        raise ValueError(f"{field} contains HTML fragment")
    if len(label) > 120:
        raise ValueError(f"{field} is too long to be a concept key")
    if len(label.split()) > 10 or SENTENCE_PUNCT_RE.search(label):
        raise ValueError(f"{field} looks like a sentence, not a concept key: {label[:80]}")
    if SOURCE_INDEX_RE.search(label):
        raise ValueError(f"{field} looks like a source/page index")
    if SECTION_HEADING_RE.search(label.strip()):
        raise ValueError(f"{field} looks like a section heading")
    if re.fullmatch(r"[\W_]+", label, flags=re.U):
        raise ValueError(f"{field} is only symbols")


def split_aliases_by_language(values: list[str]) -> tuple[list[str], list[str]]:
    aliases_en: list[str] = []
    aliases_zh: list[str] = []
    for value in values:
        value = normalize_safe_text(value, "alias", 160)
        if not value:
            continue
        if is_probably_chinese(value):
            add_unique(aliases_zh, value)
        else:
            add_unique(aliases_en, value)
    return aliases_en, aliases_zh


def validate_profile_shape(data: dict[str, Any]) -> None:
    if not isinstance(data, dict):
        raise ValueError("profile must be a JSON object")
    if "concepts" in data and not isinstance(data["concepts"], dict):
        raise ValueError("profile.concepts must be an object")
    if "events" in data and not isinstance(data["events"], list):
        raise ValueError("profile.events must be a list")
    for concept_id, info in (data.get("concepts") or {}).items():
        if not isinstance(info, dict):
            raise ValueError(f"profile concept {concept_id} must be an object")
        label = normalize_safe_text(info.get("label") or concept_id, f"profile.concepts.{concept_id}.label", 160)
        validate_concept_label(label, f"profile.concepts.{concept_id}.label")
        for field in ("translation", "ai_explanation", "user_note", "summary"):
            if info.get(field):
                normalize_safe_text(info.get(field), f"profile.concepts.{concept_id}.{field}", 1600)
        for field in ("aliases", "aliases_en", "aliases_zh"):
            values = info.get(field, []) or []
            if not isinstance(values, list):
                raise ValueError(f"profile.concepts.{concept_id}.{field} must be a list")
            for alias in values:
                normalized_alias = normalize_safe_text(alias, f"profile.concepts.{concept_id}.{field}", 160)
                validate_concept_label(normalized_alias, f"profile.concepts.{concept_id}.{field}")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def save_json(path: Path, data: dict[str, Any], *, backup: bool = False) -> None:
    validate_profile_shape(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    tmp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp_path.write_text(payload, encoding="utf-8")
    loaded = load_json(tmp_path)
    validate_profile_shape(loaded)
    if backup and path.exists():
        backup_path = path.with_suffix(path.suffix + f".{datetime.now().strftime('%Y%m%d%H%M%S')}.bak")
        shutil.copy2(path, backup_path)
    tmp_path.replace(path)


def short_hash(text: str, length: int = 12) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="replace")).hexdigest()[:length]


def valid_status(value: Any) -> str:
    status = normalize_text(value, 80).lower()
    return status if status in VALID_STATUSES else "unrated"


def is_long_or_sentence(text: str) -> bool:
    value = clean_text(text)
    if len(value) > 90:
        return True
    if len(value.split()) > 10:
        return True
    return bool(re.search(r"[。；：，。！？]|——|FIG\.|图\s*\d|应用——|理论——", value))


def concept_id_from_label(label: str) -> str:
    label = clean_text(label, 160)
    abbreviations = re.findall(r"\(([A-Za-z0-9-]{2,12})\)", label)
    if abbreviations:
        return abbreviations[-1].lower()
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.+-]{1,24}", label):
        return label.lower().replace("_", "-")
    ascii_text = label.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text).strip("-").lower()
    if slug:
        return slug[:80]
    return "concept-" + short_hash(label)


def source_id_for(source: dict[str, Any]) -> str:
    basis = "|".join(
        clean_text(source.get(key), 1000)
        for key in ("source_kind", "title", "path", "url", "date_range")
    )
    return "src-" + short_hash(basis or "unknown-source")


def event_id_for(source_id: str, concept_id: str, item: dict[str, Any]) -> str:
    basis = "|".join(
        [
            source_id,
            concept_id,
            clean_text(item.get("feedback_id"), 500),
            clean_text(item.get("block_id"), 120),
            clean_text(item.get("selected_text") or item.get("concept"), 1000),
            clean_text(item.get("user_question"), 1000),
        ]
    )
    return "evt-" + short_hash(basis, 16)


def default_status_scale() -> dict[str, str]:
    return {
        "mastered": "User can explain and apply the concept without help.",
        "known": "User understands the concept in ordinary context.",
        "learning": "User partly understands and benefits from reminders or examples.",
        "unknown": "User needs explanation before reading fluently.",
        "unrated": "Seen or extracted, but the user has not judged it yet.",
    }


def empty_profile_v2() -> dict[str, Any]:
    now = utc_now()
    return {
        "version": 2,
        "updated_at": now,
        "description": "Personal knowledge boundary for literature reading and AI/quantum news.",
        "status_scale": default_status_scale(),
        "concepts": {},
        "events": [],
        "sources": {},
        "review_queue": [],
        "reading_sessions": [],
        "migrations": [],
    }


def default_concept(concept_id: str, label: str) -> dict[str, Any]:
    return {
        "concept_id": concept_id,
        "label": label,
        "aliases": [],
        "aliases_en": [],
        "aliases_zh": [],
        "translation": "",
        "status": "unrated",
        "confidence": 0.0,
        "facet_status": {facet: "unrated" for facet in FACETS},
        "learning_needs": [],
        "preferred_explanation_styles": [],
        "ai_explanation": "",
        "user_note": "",
        "summary": "",
        "stats": {
            "seen": 0,
            "feedback_events": 0,
            "questions": 0,
            "unknown_marks": 0,
            "learning_marks": 0,
            "known_marks": 0,
            "mastered_marks": 0,
        },
        "source_ids": [],
        "event_ids": [],
        "last_seen_at": "",
        "next_review_at": "",
        "review_priority": 0,
    }


def add_unique(values: list[Any], value: Any) -> None:
    if value and value not in values:
        values.append(value)


def infer_known_term(raw: str) -> tuple[str, str, str] | None:
    folded = clean_text(raw).casefold()
    for full, label, translation in KNOWN_TERM_HINTS:
        if full.casefold() in folded or label.casefold() in folded:
            return label, full, translation
    return None


def choose_concept(item: dict[str, Any]) -> tuple[str, str, list[str], str]:
    raw = normalize_safe_text(item.get("concept") or item.get("selected_text") or "unlabeled concept", "concept", 1000)
    block_id = normalize_safe_text(item.get("block_id") or item.get("bilingual_block_id"), "block_id", 80)
    translation = safe_optional_text(item.get("translation") or item.get("alias_zh"), "translation", 300)

    if is_long_or_sentence(raw):
        if block_id in BLOCK_CONCEPT_HINTS:
            label, hint_translation = BLOCK_CONCEPT_HINTS[block_id]
            return concept_id_from_label(label), label, [], translation or safe_optional_text(hint_translation, "translation", 300)
        known = infer_known_term(raw)
        if known:
            label, alias, hint_translation = known
            return concept_id_from_label(label), label, [alias], translation or safe_optional_text(hint_translation, "translation", 300)
        label = f"source annotation {block_id}" if block_id else "freeform news/paper annotation"
        return concept_id_from_label(label), label, [], translation

    known = infer_known_term(raw)
    if known:
        label, alias, hint_translation = known
        aliases = [raw]
        if alias != raw:
            aliases.append(alias)
        return concept_id_from_label(label), label, aliases, translation or safe_optional_text(hint_translation, "translation", 300)
    validate_concept_label(raw)
    return concept_id_from_label(raw), raw, [raw], translation


def build_source(feedback: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    source_kind = normalize_safe_text(feedback.get("source_kind") or item.get("source_kind") or "reader_feedback", "source_kind", 120)
    title = normalize_safe_text(
        feedback.get("paper_title")
        or feedback.get("briefing_title")
        or item.get("source_title")
        or "Untitled source",
        "source_title",
        500,
    )
    path = normalize_safe_text(feedback.get("reader_path") or feedback.get("briefing_path") or item.get("source") or "", "source_path", 1000)
    url = normalize_safe_text(item.get("source_url"), "source_url", 1000)
    date_range = normalize_safe_text(feedback.get("date_range") or feedback.get("date") or "", "date_range", 200)
    source = {
        "source_kind": source_kind,
        "title": title,
        "path": path,
        "url": url,
        "date_range": date_range,
    }
    source["source_id"] = source_id_for(source)
    return source


def ensure_source(profile: dict[str, Any], source: dict[str, Any]) -> str:
    source_id = source["source_id"]
    sources = profile.setdefault("sources", {})
    existing = sources.setdefault(source_id, {
        "source_id": source_id,
        "source_kind": source.get("source_kind", ""),
        "title": source.get("title", ""),
        "path": source.get("path", ""),
        "url": source.get("url", ""),
        "date_range": source.get("date_range", ""),
        "first_seen_at": utc_now(),
        "last_seen_at": utc_now(),
        "event_ids": [],
    })
    existing["last_seen_at"] = utc_now()
    for key in ("source_kind", "title", "path", "url", "date_range"):
        if source.get(key) and not existing.get(key):
            existing[key] = source[key]
    return source_id


def should_update_overall(current: str, incoming: str) -> bool:
    if incoming == "unrated":
        return current == "unrated"
    if current in {"known", "mastered"} and incoming in {"unknown", "learning"}:
        return False
    return STATUS_ORDER[incoming] >= STATUS_ORDER.get(current, 0) or current in {"unrated", "unknown", "learning"}


def upsert_review(profile: dict[str, Any], concept: dict[str, Any], event: dict[str, Any], priority: int) -> None:
    queue = profile.setdefault("review_queue", [])
    concept_id = concept["concept_id"]
    facet = event.get("facet") or "general"
    existing = None
    for row in queue:
        if row.get("concept_id") == concept_id and row.get("facet") == facet:
            existing = row
            break
    due_days = 1 if priority >= 90 else 3 if priority >= 70 else 7
    due_at = (datetime.now(timezone.utc) + timedelta(days=due_days)).replace(microsecond=0).isoformat()
    reason = event.get("user_question") or event.get("difficulty_type") or event.get("status") or "needs review"
    payload = {
        "concept_id": concept_id,
        "label": concept.get("label", concept_id),
        "facet": facet,
        "status": event.get("status", concept.get("status", "unrated")),
        "priority": priority,
        "reason": clean_text(reason, 300),
        "due_at": due_at,
        "last_event_id": event.get("event_id", ""),
        "source_ids": [event.get("source_id")] if event.get("source_id") else [],
        "updated_at": utc_now(),
    }
    if existing is None:
        queue.append(payload)
    else:
        existing.update(payload)
    concept["next_review_at"] = due_at
    concept["review_priority"] = max(int(concept.get("review_priority") or 0), priority)


def clear_review_for_concept(profile: dict[str, Any], concept: dict[str, Any]) -> None:
    concept_id = concept.get("concept_id")
    if not concept_id:
        return
    queue = profile.setdefault("review_queue", [])
    profile["review_queue"] = [row for row in queue if row.get("concept_id") != concept_id]
    concept["next_review_at"] = ""
    concept["review_priority"] = 0


def record_feedback_item(profile: dict[str, Any], feedback: dict[str, Any], item: dict[str, Any], timestamp: str | None = None) -> str:
    timestamp = timestamp or utc_now()
    source = build_source(feedback, item)
    source_id = ensure_source(profile, source)
    concept_id, label, aliases, translation = choose_concept(item)
    # A narrow importer may supply an already validated stable profile ID.
    # Reader/news feedback still derives IDs from normalized labels as before.
    canonical_concept_id = normalize_safe_text(item.get("canonical_concept_id"), "canonical_concept_id", 160)
    if canonical_concept_id:
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,159}", canonical_concept_id):
            raise ValueError("canonical_concept_id must be a stable lowercase ID")
        concept_id = canonical_concept_id
    concepts = profile.setdefault("concepts", {})
    concept = concepts.setdefault(concept_id, default_concept(concept_id, label))
    concept["label"] = concept.get("label") or label
    concept["translation"] = concept.get("translation") or translation
    aliases_en, aliases_zh = split_aliases_by_language(aliases)
    for alias in aliases:
        if alias and len(alias) <= 120:
            add_unique(concept.setdefault("aliases", []), alias)
    for alias in aliases_en:
        add_unique(concept.setdefault("aliases_en", []), alias)
    for alias in aliases_zh:
        add_unique(concept.setdefault("aliases_zh", []), alias)

    raw_concept = normalize_safe_text(item.get("concept"), "concept", 1000)
    if raw_concept and raw_concept != label and len(raw_concept) <= 120:
        validate_concept_label(raw_concept, "concept")
        add_unique(concept.setdefault("aliases", []), raw_concept)
        raw_en, raw_zh = split_aliases_by_language([raw_concept])
        for alias in raw_en:
            add_unique(concept.setdefault("aliases_en", []), alias)
        for alias in raw_zh:
            add_unique(concept.setdefault("aliases_zh", []), alias)

    status = valid_status(item.get("status"))
    current = valid_status(concept.get("status"))
    if should_update_overall(current, status):
        concept["status"] = status

    difficulty_type = normalize_safe_text(item.get("confusion_type") or item.get("question_type"), "confusion_type", 120)
    facet = CONFUSION_TO_FACET.get(difficulty_type, "")
    if facet and status != "unrated":
        concept.setdefault("facet_status", {f: "unrated" for f in FACETS})[facet] = status
    if difficulty_type:
        add_unique(concept.setdefault("learning_needs", []), difficulty_type)
    explanation_style = normalize_safe_text(item.get("explanation_style"), "explanation_style", 120)
    if explanation_style:
        add_unique(concept.setdefault("preferred_explanation_styles", []), explanation_style)

    event = {
        "event_id": "",
        "timestamp": timestamp,
        "source_id": source_id,
        "concept_id": concept_id,
        "raw_concept": raw_concept,
        "status": status,
        "event_type": normalize_safe_text(feedback.get("source_kind") or item.get("source_kind") or "reader_feedback", "event_type", 120),
        "action": normalize_safe_text(item.get("action") or "reader_feedback", "action", 120),
        "annotation_kind": normalize_safe_text(item.get("annotation_kind") or "concept", "annotation_kind", 120),
        "difficulty_type": difficulty_type,
        "facet": facet,
        "explanation_style": explanation_style,
        "user_question": normalize_safe_text(item.get("user_question") or item.get("question"), "user_question", 1600),
        "note": normalize_safe_text(item.get("note"), "note", 1600),
        "selected_text": normalize_safe_text(item.get("selected_text"), "selected_text", 2200),
        "selected_language": normalize_safe_text(item.get("selected_language"), "selected_language", 80),
        "source_excerpt": normalize_safe_text(item.get("source_excerpt"), "source_excerpt", 2200),
        "contexts": {
            "original": normalize_safe_text(item.get("original_context"), "original_context", 2200),
            "translation": normalize_safe_text(item.get("translation_context"), "translation_context", 2200),
        },
        "block_id": normalize_safe_text(item.get("block_id"), "block_id", 120),
        "bilingual_block_id": normalize_safe_text(item.get("bilingual_block_id"), "bilingual_block_id", 120),
        "source_anchor": normalize_safe_text(item.get("source_anchor"), "source_anchor", 160),
        "concept_type": normalize_safe_text(item.get("concept_type"), "concept_type", 80),
        "alias_zh": normalize_safe_text(item.get("alias_zh"), "alias_zh", 160),
            "concept_id_from_reader": normalize_safe_text(item.get("concept_id"), "concept_id", 160),
            "canonical_concept_id": canonical_concept_id,
        "source_title": normalize_safe_text(item.get("source_title"), "source_title", 500),
        "source_url": normalize_safe_text(item.get("source_url"), "source_url", 1000),
        "category": normalize_safe_text(item.get("category"), "category", 200),
        "needs_explanation": bool(item.get("needs_explanation")),
    }
    event["event_id"] = event_id_for(source_id, concept_id, item)

    events = profile.setdefault("events", [])
    existing_index = next((i for i, row in enumerate(events) if row.get("event_id") == event["event_id"]), None)
    is_new_event = existing_index is None
    if existing_index is None:
        events.append(event)
    else:
        events[existing_index].update(event)

    add_unique(concept.setdefault("event_ids", []), event["event_id"])
    add_unique(concept.setdefault("source_ids", []), source_id)
    add_unique(profile["sources"][source_id].setdefault("event_ids", []), event["event_id"])
    concept["last_seen_at"] = timestamp

    stats = concept.setdefault("stats", {})
    stats["seen"] = len(concept.get("event_ids", []))
    stats["feedback_events"] = len(concept.get("event_ids", []))
    if is_new_event:
        if event.get("user_question"):
            stats["questions"] = int(stats.get("questions") or 0) + 1
        if status == "unknown":
            stats["unknown_marks"] = int(stats.get("unknown_marks") or 0) + 1
        elif status == "learning":
            stats["learning_marks"] = int(stats.get("learning_marks") or 0) + 1
        elif status == "known":
            stats["known_marks"] = int(stats.get("known_marks") or 0) + 1
        elif status == "mastered":
            stats["mastered_marks"] = int(stats.get("mastered_marks") or 0) + 1

    if event.get("user_question"):
        concept["user_note"] = "Latest question: " + clean_text(event["user_question"], 260)
    elif event.get("note"):
        concept["user_note"] = "Latest note: " + clean_text(event["note"], 260)
    if item.get("explanation"):
        concept["ai_explanation"] = clean_text(item.get("explanation"), 1200)

    priority = 0
    if status == "unknown":
        priority = 90
    elif status == "learning":
        priority = 70
    if facet == "math_derivation":
        priority += 8
    if event.get("user_question"):
        priority += 5
    if priority:
        upsert_review(profile, concept, event, min(priority, 100))
    elif status not in REVIEW_STATUSES and valid_status(concept.get("status")) not in REVIEW_STATUSES:
        clear_review_for_concept(profile, concept)
    return event["event_id"]


def ensure_v2(profile: dict[str, Any]) -> dict[str, Any]:
    if int(profile.get("version") or 1) == 2 and isinstance(profile.get("events"), list) and isinstance(profile.get("sources"), dict):
        profile.setdefault("review_queue", [])
        profile.setdefault("migrations", [])
        profile.setdefault("status_scale", default_status_scale())
        return profile
    return migrate_legacy_profile(profile)


def legacy_items_for_concept(term: str, info: dict[str, Any]) -> list[dict[str, Any]]:
    status = valid_status(info.get("status"))
    items: list[dict[str, Any]] = []
    seen_feedback_ids: set[str] = set()
    for question in info.get("questions", []) or []:
        if not isinstance(question, dict):
            continue
        feedback_id = clean_text(question.get("feedback_id"), 300)
        if feedback_id:
            seen_feedback_ids.add(feedback_id)
        items.append({
            "feedback_id": feedback_id or f"legacy-question::{term}::{short_hash(json.dumps(question, ensure_ascii=False))}",
            "concept": term,
            "status": status,
            "note": "",
            "user_question": question.get("question", ""),
            "confusion_type": question.get("confusion_type", ""),
            "explanation_style": question.get("explanation_style", ""),
            "needs_explanation": status in REVIEW_STATUSES or bool(question.get("question")),
            "block_id": question.get("block_id", ""),
            "bilingual_block_id": question.get("bilingual_block_id", ""),
            "annotation_kind": "legacy_question",
            "source_excerpt": question.get("source_excerpt", ""),
            "selected_text": question.get("selected_text", ""),
            "selected_language": question.get("selected_language", ""),
            "original_context": question.get("original_context", ""),
            "translation_context": question.get("translation_context", ""),
            "source": question.get("source", ""),
            "source_kind": question.get("source_kind", ""),
            "source_title": question.get("source_title", ""),
            "source_url": question.get("source_url", ""),
            "category": question.get("category", ""),
            "translation": info.get("translation", ""),
            "explanation": info.get("ai_explanation", ""),
            "legacy_user_note": info.get("user_note", ""),
            "timestamp": question.get("timestamp", ""),
        })
    for evidence in info.get("evidence", []) or []:
        if not isinstance(evidence, dict):
            continue
        feedback_id = clean_text(evidence.get("feedback_id"), 300)
        if feedback_id and feedback_id in seen_feedback_ids:
            continue
        items.append({
            "feedback_id": feedback_id or f"legacy-evidence::{term}::{short_hash(json.dumps(evidence, ensure_ascii=False))}",
            "concept": term,
            "status": status,
            "note": info.get("user_note", "") if not items else "",
            "user_question": evidence.get("user_question", ""),
            "confusion_type": evidence.get("confusion_type", ""),
            "explanation_style": evidence.get("explanation_style", ""),
            "needs_explanation": bool(evidence.get("needs_explanation")) or status in REVIEW_STATUSES,
            "block_id": evidence.get("block_id", ""),
            "bilingual_block_id": evidence.get("bilingual_block_id", ""),
            "annotation_kind": evidence.get("annotation_kind", "legacy_evidence"),
            "source_excerpt": "",
            "selected_text": "",
            "selected_language": evidence.get("selected_language", ""),
            "source": evidence.get("source", ""),
            "source_kind": evidence.get("source_kind", ""),
            "source_title": evidence.get("source_title", ""),
            "source_url": evidence.get("source_url", ""),
            "category": evidence.get("category", ""),
            "translation": info.get("translation", ""),
            "explanation": info.get("ai_explanation", ""),
            "legacy_user_note": info.get("user_note", ""),
            "timestamp": evidence.get("timestamp", ""),
            "action": evidence.get("action", "legacy_evidence"),
        })
    if not items:
        items.append({
            "feedback_id": f"legacy-concept::{term}",
            "concept": term,
            "status": status,
            "note": info.get("user_note", ""),
            "translation": info.get("translation", ""),
            "explanation": info.get("ai_explanation", ""),
            "annotation_kind": "legacy_concept",
        })
    return items


def migrate_legacy_profile(old_profile: dict[str, Any]) -> dict[str, Any]:
    new_profile = empty_profile_v2()
    new_profile["description"] = old_profile.get("description") or new_profile["description"]
    new_profile["reading_sessions"] = list(old_profile.get("reading_sessions", []) or [])
    migrated_at = utc_now()
    concepts = old_profile.get("concepts", {}) or {}
    for term, info in concepts.items():
        if not isinstance(info, dict):
            continue
        for item in legacy_items_for_concept(str(term), info):
            source_label = clean_text(item.get("source") or "", 1000)
            feedback = {
                "source_kind": item.get("source_kind") or "legacy_profile",
                "paper_title": source_label or "legacy learner profile",
                "reader_path": source_label,
            }
            if item.get("source_title"):
                feedback["paper_title"] = item["source_title"]
            record_feedback_item(new_profile, feedback, item, item.get("timestamp") or migrated_at)
    new_profile["migrations"].append({
        "from_version": old_profile.get("version", 1),
        "to_version": 2,
        "migrated_at": migrated_at,
        "legacy_concepts": len(concepts),
        "events": len(new_profile.get("events", [])),
        "sources": len(new_profile.get("sources", {})),
        "notes": "Migrated legacy concept-shaped profile into concepts/events/sources/review_queue.",
    })
    new_profile["updated_at"] = migrated_at
    return new_profile


def require_string(item: dict[str, Any], field: str, idx: int, *, allow_empty: bool = False, limit: int = 4000) -> str:
    if field not in item:
        raise ValueError(f"feedback.items[{idx}].{field} is required")
    if not isinstance(item[field], str):
        raise ValueError(f"feedback.items[{idx}].{field} must be a string")
    value = normalize_safe_text(item[field], f"feedback.items[{idx}].{field}", limit)
    if not allow_empty and not value:
        raise ValueError(f"feedback.items[{idx}].{field} must not be empty")
    return value


def validate_feedback_payload(feedback: dict[str, Any]) -> None:
    if not isinstance(feedback, dict):
        raise ValueError("feedback must be a JSON object")
    items = feedback.get("items")
    if not isinstance(items, list):
        raise ValueError("feedback.items must be a list")
    source_kind = normalize_safe_text(feedback.get("source_kind"), "feedback.source_kind", 120)
    is_reader_feedback = (
        ("reader_feedback_version" in feedback or "reader_path" in feedback)
        and source_kind != "news_briefing"
    )
    if is_reader_feedback:
        version = feedback.get("reader_feedback_version")
        if version != 2:
            raise ValueError("reader feedback must declare reader_feedback_version=2; migrate old feedback explicitly")
        paper_title = normalize_safe_text(feedback.get("paper_title"), "feedback.paper_title", 500)
        reader_path = normalize_safe_text(feedback.get("reader_path"), "feedback.reader_path", 1000)
        if not paper_title:
            raise ValueError("reader feedback paper_title is required")
        if not reader_path:
            raise ValueError("reader feedback reader_path is required")
        provenance = feedback.get("bundle_provenance")
        if not isinstance(provenance, dict):
            raise ValueError("reader feedback bundle_provenance is required")
        for key in ("source_map", "completion_ledger", "reader_manifest", "structure_validation_report"):
            entry = provenance.get(key)
            if not isinstance(entry, dict):
                raise ValueError(f"reader feedback bundle_provenance.{key} is required")
            normalize_safe_text(entry.get("path"), f"bundle_provenance.{key}.path", 1000)
            digest = normalize_safe_text(entry.get("sha256"), f"bundle_provenance.{key}.sha256", 80)
            if not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise ValueError(f"bundle_provenance.{key}.sha256 must be a SHA-256 hex digest")
    else:
        normalize_safe_text(feedback.get("paper_title") or feedback.get("briefing_title") or "Untitled source", "feedback.paper_title", 500)
        normalize_safe_text(feedback.get("reader_path") or feedback.get("briefing_path") or "", "feedback.reader_path", 1000)
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"feedback.items[{idx}] must be an object")
        status = require_string(item, "status", idx, limit=80).lower()
        if status not in VALID_STATUSES:
            raise ValueError(f"feedback.items[{idx}].status is invalid: {status}")
        annotation_kind = normalize_safe_text(item.get("annotation_kind") or "concept", f"feedback.items[{idx}].annotation_kind", 80)
        source_anchor = require_string(item, "source_anchor", idx, limit=160)
        if SOURCE_INDEX_RE.search(source_anchor):
            raise ValueError(f"feedback.items[{idx}].source_anchor looks like source page noise")
        concept_type = require_string(item, "concept_type", idx, limit=80)
        if concept_type not in VALID_CONCEPT_TYPES:
            raise ValueError(f"feedback.items[{idx}].concept_type is invalid: {concept_type}")
        if annotation_kind == "concept":
            if HTML_TAG_RE.search(str(item.get("concept") or "")):
                raise ValueError(f"feedback.items[{idx}].concept contains HTML fragment")
            concept = require_string(item, "concept", idx, limit=160)
            validate_concept_label(concept, f"feedback.items[{idx}].concept")
            require_string(item, "concept_id", idx, limit=160)
        else:
            text = normalize_safe_text(item.get("selected_text") or item.get("source_excerpt") or item.get("concept"), f"feedback.items[{idx}].selected_text", 2200)
            if not text:
                raise ValueError(f"feedback.items[{idx}] freeform annotation needs selected_text or source_excerpt")
        for optional in (
            "alias_zh",
            "note",
            "user_question",
            "source_excerpt",
            "selected_text",
            "original_context",
            "translation_context",
            "block_id",
            "bilingual_block_id",
            "canonical_concept_id",
        ):
            if optional in item:
                normalize_safe_text(item.get(optional), f"feedback.items[{idx}].{optional}", 2200)


def import_feedback(profile: dict[str, Any], feedback: dict[str, Any]) -> tuple[dict[str, Any], int]:
    validate_feedback_payload(feedback)
    profile = ensure_v2(profile)
    items = feedback.get("items", [])
    changed = 0
    for idx, item in enumerate(items):
        concept = normalize_safe_text(item.get("concept") or item.get("selected_text"), f"feedback.items[{idx}].concept", 1000)
        if not concept:
            raise ValueError(f"feedback.items[{idx}] has no concept or selected_text")
        record_feedback_item(profile, feedback, item)
        changed += 1
    profile.setdefault("reading_sessions", []).append({
        "title": feedback.get("paper_title") or feedback.get("briefing_title") or "",
        "path": feedback.get("reader_path") or feedback.get("briefing_path") or "",
        "source_kind": feedback.get("source_kind") or "reader_feedback",
        "feedback_items": changed,
        "timestamp": utc_now(),
    })
    profile["updated_at"] = utc_now()
    return profile, changed
