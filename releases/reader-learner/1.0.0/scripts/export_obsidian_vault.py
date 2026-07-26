#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export reader-learner knowledge_profile.json to an Obsidian vault."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from profile_v2 import ensure_v2, load_json


DEFAULT_OBSIDIAN_APP = r"D:\software\Obsidian\Obsidian.exe"
MANIFEST_NAME = ".reader-learner-vault-manifest.json"
STATUS_ORDER = ["unknown", "learning", "known", "mastered", "unrated"]
STATUS_COLORS = {
    "unknown": "#E15759",
    "learning": "#F28E2B",
    "known": "#59A14F",
    "mastered": "#4E79A7",
    "unrated": "#BAB0AC",
}
STATUS_RGB = {
    "unknown": 14767961,
    "learning": 15896107,
    "known": 5873999,
    "mastered": 5142951,
    "unrated": 12234924,
}
FACET_LABELS = {
    "definition": "Definition",
    "paper_usage": "Paper usage",
    "math_derivation": "Math derivation",
    "algorithm_step": "Algorithm step",
    "assumption": "Assumption",
    "evidence_interpretation": "Evidence interpretation",
    "relation": "Relation",
    "english_term": "English term",
    "physical_intuition": "Physical intuition",
    "general": "General",
}
FACET_ALIASES = {
    "term_definition": "definition",
    "math_step": "math_derivation",
    "evidence": "evidence_interpretation",
}
EDGE_COLORS = {
    "derived_from": "#F28E2B",
    "evidence_for": "#76B7B2",
    "needs_review": "#E15759",
    "related_to": "#BAB0AC",
    "contains": "#4E79A7",
    "has_gap": "#E15759",
    "has_anchor": "#59A14F",
    "belongs_to": "#9C755F",
}
BOUNDARY_BUCKETS = {
    "known_anchor": {
        "label": "Known anchors",
        "summary": "Concepts already usable as foundations for explanations.",
        "color": "#59A14F",
        "rank": 0,
    },
    "active_gap": {
        "label": "Active unknown core",
        "summary": "High-priority unknown or learning concepts blocking fluent reading.",
        "color": "#E15759",
        "rank": 1,
    },
    "probe_gap": {
        "label": "Unrated probes",
        "summary": "Concepts seen in the paper that still need a user judgment.",
        "color": "#F28E2B",
        "rank": 2,
    },
    "peripheral": {
        "label": "Peripheral context",
        "summary": "Low-priority context that should not dominate the map.",
        "color": "#BAB0AC",
        "rank": 3,
    },
}
DOMAIN_RULES = [
    ("equations", "Equations and equivalence", ["tdse", "tdcse", "schrodinger", "equivalence"]),
    ("algorithm", "Algorithm and ansatz", ["cete", "ansatz", "unitary", "anti-hermitian", "generator"]),
    ("many_body", "Many-body objects", ["rdm", "density matrix", "slater", "particle"]),
    ("measurement", "Measurement and experiment", ["tomography", "measurement", "evidence", "h2", "ibm", "sequential", "propagator"]),
    ("hamiltonian", "Hamiltonian formalism", ["hamiltonian", "reduced"]),
    ("meta", "Peripheral metadata", ["acknowledgment", "acknowledgements"]),
]
DOMAIN_COLORS = {
    "equations": "#4E79A7",
    "algorithm": "#9C755F",
    "many_body": "#76B7B2",
    "measurement": "#EDC948",
    "hamiltonian": "#B07AA1",
    "meta": "#BAB0AC",
}


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def clean_text(value: Any, limit: int = 4000) -> str:
    text = " ".join(str(value or "").replace("\r\n", "\n").replace("\r", "\n").split())
    return text.strip()[:limit]


def clip(value: Any, limit: int = 900) -> str:
    text = clean_text(value, limit + 20)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def find_profile(start: Path) -> Path:
    for parent in [start.resolve(), *start.resolve().parents]:
        candidate = parent / ".agents" / "reader-learner" / "knowledge_profile.json"
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Could not find .agents/reader-learner/knowledge_profile.json")


def safe_filename(value: str, fallback: str = "note", limit: int = 96) -> str:
    text = clean_text(value, 180) or fallback
    text = re.sub(r'[<>:"/\\|?*\x00-\x1f]', " ", text)
    text = re.sub(r"\s+", " ", text).strip(" .")
    if not text:
        text = fallback
    return text[:limit].rstrip(" .")


def is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def yaml_value(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def frontmatter(values: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in values.items():
        lines.append(f"{key}: {yaml_value(value)}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        cells = [("" if cell is None else str(cell)).replace("\n", " ").replace("|", "\\|") for cell in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def rel_no_suffix(rel_path: Path) -> str:
    return rel_path.with_suffix("").as_posix()


def obsidian_link(rel_path: Path, label: str) -> str:
    return f"[[{rel_no_suffix(rel_path)}|{label}]]"


def obsidian_target(rel_path: Path) -> str:
    return f"[[{rel_no_suffix(rel_path)}]]"


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def status_tag(status: str) -> str:
    return "status/" + (clean_text(status, 40) or "unrated").replace(" ", "-")


def facet_tag(facet: str) -> str:
    return "facet/" + (clean_text(normalize_facet(facet), 80) or "general").replace(" ", "-")


def normalize_facet(value: Any) -> str:
    facet = clean_text(value, 80) or "general"
    return FACET_ALIASES.get(facet, facet)


def unique_clean(values: Iterable[Any], limit: int = 120) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = clean_text(value, limit)
        if text and text not in seen:
            result.append(text)
            seen.add(text)
    return result


def concept_summary(concept: dict[str, Any], limit: int = 190) -> str:
    for key in ("summary", "ai_explanation", "user_note", "translation"):
        text = clip(concept.get(key), limit)
        if text:
            return text
    return "Personal learner concept generated from reader feedback."


def concept_tier(concept: dict[str, Any]) -> str:
    priority = int_value(concept.get("review_priority"))
    seen = int_value((concept.get("stats") or {}).get("seen"))
    if priority >= 90 or seen >= 5:
        return "core"
    if priority == 0 and seen <= 1:
        return "peripheral"
    return "supporting"


def concept_confidence(concept: dict[str, Any]) -> float:
    confidence = float_value(concept.get("confidence"))
    if confidence:
        return round(max(0.0, min(confidence, 1.0)), 2)
    status = clean_text(concept.get("status") or "unrated", 40)
    return {"mastered": 0.9, "known": 0.72, "learning": 0.45, "unknown": 0.2}.get(status, 0.1)


def concept_boundary_bucket(concept: dict[str, Any]) -> str:
    status = clean_text(concept.get("status") or "unrated", 40)
    priority = int_value(concept.get("review_priority"))
    if status in {"known", "mastered"}:
        return "known_anchor"
    if status in {"unknown", "learning"} and priority >= 50:
        return "active_gap"
    if priority > 0 or concept.get("learning_needs"):
        return "probe_gap"
    return "peripheral"


def concept_primary_facet(concept: dict[str, Any]) -> str:
    needs = concept.get("learning_needs", []) or []
    if needs:
        return normalize_facet(needs[0])
    facet_status = concept.get("facet_status", {}) or {}
    for facet, status in facet_status.items():
        if clean_text(status, 40) in {"unknown", "learning"}:
            return normalize_facet(facet)
    return "general"


def concept_domain(concept_id: str, concept: dict[str, Any]) -> str:
    primary_text = " ".join(
        [
            concept_id,
            clean_text(concept.get("label"), 160),
            clean_text(concept.get("translation"), 160),
        ]
    ).casefold()
    alias_text = " ".join(clean_text(item, 120) for item in concept.get("aliases", []) or []).casefold()
    scores: dict[str, int] = {}
    for domain_id, _label, needles in DOMAIN_RULES:
        score = 0
        for needle in needles:
            if needle in primary_text:
                score += 3
            if needle in alias_text:
                score += 1
        if score:
            scores[domain_id] = score
    if scores:
        return max(scores.items(), key=lambda item: (item[1], -[row[0] for row in DOMAIN_RULES].index(item[0])))[0]
    return "meta" if "paper acknowledgment" in primary_text else "algorithm"


def domain_label(domain_id: str) -> str:
    for candidate, label, _needles in DOMAIN_RULES:
        if candidate == domain_id:
            return label
    return domain_id.replace("_", " ").title()


def plain_link_label(value: str) -> str:
    text = clean_text(value, 300)
    match = re.fullmatch(r"\[\[[^|\]]+\|([^\]]+)\]\]", text)
    if match:
        return match.group(1)
    match = re.fullmatch(r"\[\[([^\]]+)\]\]", text)
    if match:
        return match.group(1).split("/")[-1]
    return text


def status_callout(status: str) -> str:
    return {
        "unknown": "danger",
        "learning": "warning",
        "known": "success",
        "mastered": "tip",
    }.get(status, "info")


def slug_fragment(value: str) -> str:
    text = clean_text(value, 120).lower().replace("/", "-")
    text = re.sub(r"[^a-z0-9_.+-]+", "-", text)
    return text.strip("-") or "item"


def mermaid_label(value: Any, limit: int = 42) -> str:
    return clip(value, limit).replace("\\", "\\\\").replace('"', '\\"')


def write_file(vault: Path, rel_path: Path, text: str, written: set[str]) -> None:
    target = vault / rel_path
    if not is_relative_to(target, vault):
        raise ValueError(f"Refusing to write outside vault: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    written.add(rel_path.as_posix())


def write_json_file(vault: Path, rel_path: Path, data: Any, written: set[str]) -> None:
    write_file(vault, rel_path, json.dumps(data, ensure_ascii=False, indent=2), written)


def load_manifest(vault: Path) -> set[str]:
    path = vault / MANIFEST_NAME
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    return {str(item) for item in data.get("files", []) if isinstance(item, str)}


def cleanup_old_files(vault: Path, old_files: set[str], new_files: set[str]) -> int:
    removed = 0
    for rel in sorted(old_files - new_files):
        target = vault / rel
        if not is_relative_to(target, vault):
            continue
        if target.exists() and target.is_file():
            target.unlink()
            removed += 1
            parent = target.parent
            while parent != vault and is_relative_to(parent, vault):
                try:
                    parent.rmdir()
                except OSError:
                    break
                parent = parent.parent
    return removed


def concept_rel_path(concept_id: str, concept: dict[str, Any]) -> Path:
    label = clean_text(concept.get("label") or concept_id, 120)
    return Path("Concepts") / f"{safe_filename(concept_id + ' - ' + label)}.md"


def source_rel_path(source_id: str, source: dict[str, Any]) -> Path:
    title = clean_text(source.get("title") or source_id, 120)
    return Path("Sources") / f"{safe_filename(source_id + ' - ' + title)}.md"


def event_rel_path(event_id: str) -> Path:
    return Path("Evidence") / f"{safe_filename(event_id, 'evidence')}.md"


def compact_evidence_label(event: dict[str, Any]) -> str:
    block = clean_text(event.get("block_id") or event.get("bilingual_block_id"), 60)
    timestamp = clean_text(event.get("timestamp"), 80)
    if block and timestamp:
        return f"{block} / {timestamp}"
    return block or timestamp or clean_text(event.get("event_id"), 120) or "evidence"


def evidence_signal(event: dict[str, Any], limit: int = 180) -> str:
    return clip(
        event.get("user_question")
        or event.get("note")
        or event.get("source_excerpt")
        or event.get("selected_text"),
        limit,
    ) or "Feedback signal recorded."


def evidence_counts(events: list[dict[str, Any]]) -> str:
    status_counts = Counter(clean_text(event.get("status") or "unrated", 40) for event in events)
    facet_counts = Counter(normalize_facet(event.get("facet") or event.get("difficulty_type") or "general") for event in events)
    status_text = ", ".join(f"{key}: {value}" for key, value in sorted(status_counts.items())) or "none"
    facet_text = ", ".join(f"{key}: {value}" for key, value in sorted(facet_counts.items())) or "none"
    return f"Status signals: {status_text}. Facet signals: {facet_text}."


def build_concept_note(
    concept_id: str,
    concept: dict[str, Any],
    concept_links: dict[str, str],
    source_links: dict[str, str],
    event_links: dict[str, str],
    events_by_concept: dict[str, list[dict[str, Any]]],
) -> str:
    label = clean_text(concept.get("label") or concept_id, 160)
    status = clean_text(concept.get("status") or "unrated", 40)
    aliases = [clean_text(item, 120) for item in concept.get("aliases", []) or [] if clean_text(item, 120)]
    tags = ["reader-learner", "type/concept", status_tag(status)]
    for need in concept.get("learning_needs", []) or []:
        tags.append(facet_tag(str(need)))
    tags = unique_clean(tags)
    relationships = [
        {"target": source_id, "type": "derived_from"}
        for source_id in concept.get("source_ids", []) or []
        if source_id in source_links
    ]

    rows = []
    for facet, value in (concept.get("facet_status", {}) or {}).items():
        rows.append([facet, value])

    source_rows = []
    for source_id in concept.get("source_ids", []) or []:
        source_rows.append([source_links.get(source_id, source_id)])

    event_rows = []
    for event in events_by_concept.get(concept_id, [])[-8:]:
        event_id = event.get("event_id", "")
        facet = normalize_facet(event.get("facet") or event.get("difficulty_type") or "general")
        event_rows.append([
            event_links.get(event_id, compact_evidence_label(event)),
            event.get("status", ""),
            facet,
            event.get("block_id") or event.get("bilingual_block_id") or "",
            evidence_signal(event, 180),
        ])

    body = [
        frontmatter({
            "type": "concept",
            "category": "concept",
            "concept_id": concept_id,
            "title": label,
            "label": label,
            "translation": clean_text(concept.get("translation"), 160),
            "summary": concept_summary(concept),
            "status": status,
            "aliases": aliases,
            "tags": tags,
            "relationships": relationships,
            "boundary_bucket": concept_boundary_bucket(concept),
            "primary_facet": concept_primary_facet(concept),
            "domain": concept_domain(concept_id, concept),
            "sources": list(concept.get("source_ids", []) or []),
            "base_confidence": concept_confidence(concept),
            "lifecycle": "draft",
            "tier": concept_tier(concept),
            "review_priority": int_value(concept.get("review_priority")),
            "next_review_at": clean_text(concept.get("next_review_at"), 80),
            "updated": clean_text(concept.get("last_seen_at") or concept.get("next_review_at"), 80),
            "updated_from": "knowledge_profile.json",
        }),
        f"# {label}\n",
        f"> [!info] Knowledge point",
        f"> This page is the organized concept-level view. Raw feedback is kept only as compact evidence unless `--include-events` is used.",
        "",
        "> Managed export from `knowledge_profile.json`. Treat JSON as the source of truth.\n",
        f"> [!{status_callout(status)}] Current boundary",
        f"> Status: **{status}** | Review priority: **{concept.get('review_priority', 0)}** | Next review: **{concept.get('next_review_at') or 'not scheduled'}**",
        "",
        "## Boundary\n",
        md_table(
            ["Field", "Value"],
            [
                ["Status", status],
                ["Translation", clean_text(concept.get("translation"), 160)],
                ["Confidence", concept.get("confidence", "")],
                ["Review priority", concept.get("review_priority", "")],
                ["Next review", concept.get("next_review_at", "")],
                ["Last seen", concept.get("last_seen_at", "")],
            ],
        ),
        "\n## Facets\n",
        md_table(["Facet", "Status"], rows) if rows else "No facet status yet.",
        "\n## Notes\n",
        f"- User note: {clip(concept.get('user_note'), 500) or 'None'}",
        f"- AI explanation: {clip(concept.get('ai_explanation'), 900) or 'None'}",
        f"- Learning needs: {', '.join(clean_text(item, 80) for item in concept.get('learning_needs', []) or []) or 'None'}",
        "\n## Related\n",
        f"- Boundary bucket: {BOUNDARY_BUCKETS[concept_boundary_bucket(concept)]['label']}",
        f"- Knowledge domain: {domain_label(concept_domain(concept_id, concept))}",
        f"- Primary facet: {FACET_LABELS.get(concept_primary_facet(concept), concept_primary_facet(concept))}",
        "\n## Sources\n",
        "\n".join(f"- {plain_link_label(row[0])}" for row in source_rows) if source_rows else "No sources yet.",
        "\n## Evidence Signals\n",
        md_table(["Evidence", "Status", "Facet", "Block", "Signal"], event_rows) if event_rows else "No evidence signals yet.",
    ]
    return "\n".join(body).rstrip() + "\n"


def build_event_note(
    event: dict[str, Any],
    concept_links: dict[str, str],
    source_links: dict[str, str],
) -> str:
    event_id = clean_text(event.get("event_id"), 120)
    concept_id = clean_text(event.get("concept_id"), 120)
    source_id = clean_text(event.get("source_id"), 120)
    status = clean_text(event.get("status") or "unrated", 40)
    facet = normalize_facet(event.get("facet") or event.get("difficulty_type") or "general")
    tags = unique_clean(["reader-learner", "type/evidence", "evidence", status_tag(status), facet_tag(facet)])
    contexts = event.get("contexts", {}) if isinstance(event.get("contexts"), dict) else {}
    relationships = []
    if concept_id in concept_links:
        relationships.append({"target": concept_links[concept_id], "type": "evidence_for"})
    if source_id in source_links:
        relationships.append({"target": source_links[source_id], "type": "derived_from"})
    body = [
        frontmatter({
            "type": "evidence",
            "category": "evidence",
            "event_id": event_id,
            "title": f"Evidence {event_id}",
            "concept_id": concept_id,
            "source_id": source_id,
            "summary": clip(event.get("user_question") or event.get("note") or event.get("selected_text") or "Reader feedback event.", 190),
            "status": status,
            "facet": facet,
            "tags": tags,
            "relationships": relationships,
            "sources": [source_id] if source_id else [],
            "base_confidence": 0.6 if event.get("user_question") or event.get("note") else 0.4,
            "lifecycle": "draft",
            "tier": "supporting",
            "updated": clean_text(event.get("timestamp"), 80),
        }),
        f"# Evidence {event_id}\n",
        f"> [!{status_callout(status)}] Feedback signal",
        f"> This event marks {concept_links.get(concept_id, concept_id)} as **{status}** for `{facet}`.",
        "",
        md_table(
            ["Field", "Value"],
            [
                ["Knowledge point", concept_links.get(concept_id, concept_id)],
                ["Source", source_links.get(source_id, source_id)],
                ["Time", event.get("timestamp", "")],
                ["Status", status],
                ["Facet", facet],
                ["Block", event.get("block_id") or event.get("bilingual_block_id") or ""],
                ["Kind", event.get("annotation_kind", "")],
            ],
        ),
        "\n## User Question\n",
        clip(event.get("user_question"), 1200) or "None",
        "\n## Note\n",
        clip(event.get("note"), 1200) or "None",
        "\n## Selected Text\n",
        clip(event.get("selected_text"), 1600) or "None",
        "\n## Source Excerpt\n",
        clip(event.get("source_excerpt"), 1800) or "None",
        "\n## Contexts\n",
        f"### Original\n{clip(contexts.get('original'), 1800) or 'None'}\n",
        f"### Translation\n{clip(contexts.get('translation'), 1800) or 'None'}",
    ]
    return "\n".join(body).rstrip() + "\n"


def build_source_note(
    source_id: str,
    source: dict[str, Any],
    concept_links: dict[str, str],
    event_links: dict[str, str],
    events_by_source: dict[str, list[dict[str, Any]]],
) -> str:
    title = clean_text(source.get("title") or source_id, 300)
    events = events_by_source.get(source_id, [])
    concept_ids = sorted({clean_text(event.get("concept_id"), 120) for event in events if event.get("concept_id")})
    relationships = [
        {"target": concept_id, "type": "related_to"}
        for concept_id in concept_ids
        if concept_id in concept_links
    ]
    rows = []
    for event in events[-20:]:
        event_id = event.get("event_id", "")
        concept_id = event.get("concept_id", "")
        facet = normalize_facet(event.get("facet") or event.get("difficulty_type") or "general")
        rows.append([
            plain_link_label(concept_links.get(concept_id, concept_id)),
            event.get("status", ""),
            facet,
            event.get("block_id") or event.get("bilingual_block_id") or "",
            evidence_signal(event, 140),
        ])
    body = [
        frontmatter({
            "type": "source",
            "category": "source",
            "source_id": source_id,
            "source_kind": source.get("source_kind", ""),
            "summary": f"{len(concept_ids)} knowledge points and {len(events)} compact evidence signals from this source.",
            "title": title,
            "tags": ["reader-learner", "type/source", "source"],
            "relationships": relationships,
            "base_confidence": 0.75,
            "lifecycle": "draft",
            "tier": "core" if events else "supporting",
            "updated": clean_text(source.get("last_seen_at"), 80),
        }),
        f"# {title}\n",
        "> [!info] Source hub",
        "> This page connects the original reading or briefing source to the knowledge points extracted from it.",
        "",
        md_table(
            ["Field", "Value"],
            [
                ["Source kind", source.get("source_kind", "")],
                ["Path", source.get("path", "")],
                ["URL", source.get("url", "")],
                ["Date range", source.get("date_range", "")],
                ["First seen", source.get("first_seen_at", "")],
                ["Last seen", source.get("last_seen_at", "")],
            ],
        ),
        "\n## Knowledge Points\n",
        "\n".join(f"- {plain_link_label(concept_links.get(concept_id, concept_id))}" for concept_id in concept_ids) if concept_ids else "No knowledge points yet.",
        "\n## Evidence Summary\n",
        evidence_counts(events),
        "\n## Compact Evidence Signals\n",
        md_table(["Knowledge point", "Status", "Facet", "Block", "Signal"], rows) if rows else "No evidence signals yet.",
    ]
    return "\n".join(body).rstrip() + "\n"


def build_home_note(profile: dict[str, Any], concept_links: dict[str, str]) -> str:
    concepts = profile.get("concepts", {}) or {}
    status_counts = Counter(clean_text(row.get("status") if isinstance(row, dict) else "unrated", 40) for row in concepts.values())
    priority = sorted(
        (row for row in concepts.values() if isinstance(row, dict)),
        key=lambda row: (-int(row.get("review_priority") or 0), row.get("label", "")),
    )[:12]
    priority_lines = []
    for row in priority:
        concept_id = row.get("concept_id", "")
        priority_lines.append(
            f"- P{row.get('review_priority', 0)} {concept_links.get(concept_id, concept_id)} "
            f"({row.get('status', 'unrated')}, due {row.get('next_review_at') or 'none'})"
        )
    body = [
        frontmatter({
            "type": "home",
            "tags": ["reader-learner", "home"],
            "updated_at": profile.get("updated_at", ""),
        }),
        "# Reader Learner Vault\n",
        "> This vault is generated from `.agents/reader-learner/knowledge_profile.json`.\n",
        "## Start Here\n",
        "- [[01 Learning Dashboard|Learning Dashboard]]",
        "- [[Wiki/Knowledge Points|Knowledge Points]]",
        "- [[index|Reader Learner Index]]",
        "- [[hot|Hot Cache]]",
        "- [[Wiki/Glossary|Glossary]]",
        "- [[_meta/taxonomy|Tag Taxonomy]]",
        "\n## Visual Maps\n",
        "- [[Maps/Knowledge Graph.canvas|Knowledge Graph Canvas]]",
        "- [[Maps/Concept Relations|Core Knowledge Boundary]]",
        "- [[wiki-export/reader-learner-graph.html|Standalone Graph HTML]]",
        "## Maps\n",
        "- [[Maps/Knowledge Boundary|Knowledge Boundary]]",
        "- [[Reviews/Review Queue|Review Queue]]",
        "- [[Maps/Sources Index|Sources Index]]",
        "\n## Counts\n",
        md_table(
            ["Metric", "Value"],
            [
                ["Knowledge points", len(concepts)],
                ["Evidence signals", len(profile.get("events", []) or [])],
                ["Sources", len(profile.get("sources", {}) or {})],
                ["Review queue", len(profile.get("review_queue", []) or [])],
                ["Unknown", status_counts.get("unknown", 0)],
                ["Learning", status_counts.get("learning", 0)],
                ["Known", status_counts.get("known", 0)],
                ["Mastered", status_counts.get("mastered", 0)],
            ],
        ),
        "\n## Highest Priority\n",
        "\n".join(priority_lines) if priority_lines else "No review items yet.",
    ]
    return "\n".join(body).rstrip() + "\n"


def build_boundary_map(profile: dict[str, Any], concept_links: dict[str, str]) -> str:
    concepts = profile.get("concepts", {}) or {}
    groups: dict[str, list[str]] = defaultdict(list)
    for concept_id, concept in concepts.items():
        if not isinstance(concept, dict):
            continue
        status = clean_text(concept.get("status") or "unrated", 40)
        groups[status].append(concept_links.get(concept_id, concept_id))
    lines = [
        frontmatter({"type": "map", "tags": ["reader-learner", "map"]}),
        "# Knowledge Boundary\n",
    ]
    for status in ["unknown", "learning", "known", "mastered", "unrated"]:
        lines.append(f"## {status}")
        values = sorted(groups.get(status, []))
        lines.append("\n".join(f"- {value}" for value in values) if values else "None")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_review_note(profile: dict[str, Any], concept_links: dict[str, str], event_links: dict[str, str]) -> str:
    rows = []
    for item in sorted(profile.get("review_queue", []) or [], key=lambda row: (-int(row.get("priority") or 0), row.get("due_at") or "")):
        concept_id = item.get("concept_id", "")
        rows.append([
            item.get("priority", ""),
            concept_links.get(concept_id, concept_id),
            item.get("facet", ""),
            item.get("status", ""),
            item.get("due_at", ""),
            item.get("reason", ""),
            event_links.get(item.get("last_event_id", ""), "tracked in profile"),
        ])
    return "\n".join([
        frontmatter({"type": "review_queue", "tags": ["reader-learner", "review"]}),
        "# Review Queue\n",
        md_table(["Priority", "Knowledge point", "Facet", "Status", "Due", "Reason", "Evidence"], rows) if rows else "No review items yet.",
    ]).rstrip() + "\n"


def build_sources_index(profile: dict[str, Any], source_links: dict[str, str]) -> str:
    rows = []
    for source_id, source in sorted((profile.get("sources", {}) or {}).items()):
        rows.append([
            source_links.get(source_id, source_id),
            source.get("source_kind", ""),
            source.get("date_range", ""),
            len(source.get("event_ids", []) or []),
        ])
    return "\n".join([
        frontmatter({"type": "sources_index", "tags": ["reader-learner", "source"]}),
        "# Sources Index\n",
        md_table(["Source", "Kind", "Date range", "Evidence signals"], rows) if rows else "No sources yet.",
    ]).rstrip() + "\n"


def build_index_note(profile: dict[str, Any], concept_links: dict[str, str], source_links: dict[str, str]) -> str:
    concepts = profile.get("concepts", {}) or {}
    sources = profile.get("sources", {}) or {}
    concept_rows = []
    for concept_id, concept in sorted(concepts.items()):
        if not isinstance(concept, dict):
            continue
        status = clean_text(concept.get("status") or "unrated", 40)
        concept_rows.append([
            concept_links.get(concept_id, concept_id),
            status,
            clean_text(concept.get("translation"), 120),
            concept_summary(concept, 140),
        ])
    source_rows = []
    for source_id, source in sorted(sources.items()):
        if not isinstance(source, dict):
            continue
        source_rows.append([
            source_links.get(source_id, source_id),
            source.get("source_kind", ""),
            len(source.get("event_ids", []) or []),
        ])
    return "\n".join([
        frontmatter({
            "type": "index",
            "title": "Reader Learner Index",
            "summary": "Catalog of generated knowledge points and sources.",
            "tags": ["reader-learner", "index"],
            "updated": profile.get("updated_at", ""),
        }),
        "# Reader Learner Index\n",
        "## Knowledge Points\n",
        md_table(["Knowledge point", "Status", "Translation", "Summary"], concept_rows) if concept_rows else "No knowledge points yet.",
        "\n## Sources\n",
        md_table(["Source", "Kind", "Evidence signals"], source_rows) if source_rows else "No sources yet.",
    ]).rstrip() + "\n"


def build_hot_note(profile: dict[str, Any], concept_links: dict[str, str]) -> str:
    concepts = profile.get("concepts", {}) or {}
    events = profile.get("events", []) or []
    review_queue = profile.get("review_queue", []) or []
    status_counts = Counter(
        clean_text(row.get("status") if isinstance(row, dict) else "unrated", 40)
        for row in concepts.values()
    )
    priority = sorted(
        (row for row in concepts.values() if isinstance(row, dict)),
        key=lambda row: (-int_value(row.get("review_priority")), row.get("label", "")),
    )[:8]
    lines = [
        frontmatter({
            "type": "hot_cache",
            "title": "Hot Cache",
            "summary": "Short current snapshot of the learner profile.",
            "tags": ["reader-learner", "hot-cache"],
            "updated": profile.get("updated_at", ""),
        }),
        "# Hot Cache\n",
        "> [!summary] Current shape",
        f"> {len(concepts)} knowledge points, {len(events)} evidence signals, {len(review_queue)} review items. "
        f"Unknown: {status_counts.get('unknown', 0)}, learning: {status_counts.get('learning', 0)}, "
        f"known: {status_counts.get('known', 0)}, mastered: {status_counts.get('mastered', 0)}.",
        "",
        "## Active Threads\n",
    ]
    if priority:
        for concept in priority:
            concept_id = concept.get("concept_id", "")
            lines.append(
                f"- {concept_links.get(concept_id, concept_id)}: "
                f"{concept.get('status', 'unrated')} / P{concept.get('review_priority', 0)}"
            )
    else:
        lines.append("No active review items.")
    lines.extend([
        "\n## Recent Activity\n",
        f"- Generated from `knowledge_profile.json` at {profile.get('updated_at', 'unknown time')}.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def build_log_note(profile: dict[str, Any]) -> str:
    return "\n".join([
        frontmatter({
            "type": "log",
            "title": "Reader Learner Log",
            "summary": "Append-style generated operation log for this vault export.",
            "tags": ["reader-learner", "log"],
            "updated": profile.get("updated_at", ""),
        }),
        "# Reader Learner Log\n",
        f"## [{profile.get('updated_at', '')}] export | Obsidian vault\n",
        f"- knowledge_points: {len(profile.get('concepts', {}) or {})}",
        f"- evidence_signals: {len(profile.get('events', []) or [])}",
        f"- sources: {len(profile.get('sources', {}) or {})}",
        f"- review_queue: {len(profile.get('review_queue', []) or [])}",
    ]).rstrip() + "\n"


def build_learning_dashboard(
    profile: dict[str, Any],
    concept_links: dict[str, str],
    status_links: dict[str, str],
    facet_links: dict[str, str],
) -> str:
    concepts = profile.get("concepts", {}) or {}
    status_counts = Counter(
        clean_text(row.get("status") if isinstance(row, dict) else "unrated", 40)
        for row in concepts.values()
    )
    priority_rows = []
    for item in sorted(profile.get("review_queue", []) or [], key=lambda row: (-int_value(row.get("priority")), row.get("due_at") or ""))[:16]:
        concept_id = item.get("concept_id", "")
        priority_rows.append([
            item.get("priority", ""),
            concept_links.get(concept_id, concept_id),
            item.get("facet", ""),
            item.get("status", ""),
            item.get("due_at", ""),
            clip(item.get("reason"), 90),
        ])
    status_lines = []
    for status in STATUS_ORDER:
        status_lines.append(f"- {status_links.get(status, status)}: {status_counts.get(status, 0)}")
    facet_counts: Counter[str] = Counter()
    for concept in concepts.values():
        if not isinstance(concept, dict):
            continue
        for need in concept.get("learning_needs", []) or []:
            facet_counts[normalize_facet(need)] += 1
    facet_lines = []
    for facet, count in facet_counts.most_common():
        facet_lines.append(f"- {facet_links.get(facet, facet)}: {count}")
    return "\n".join([
        frontmatter({
            "type": "dashboard",
            "title": "Learning Dashboard",
            "summary": "Status, review, Bases, and graph entry point for the reader learner vault.",
            "tags": ["reader-learner", "dashboard"],
            "updated": profile.get("updated_at", ""),
        }),
        "# Learning Dashboard\n",
        "> [!summary] Knowledge boundary",
        f"> Unknown: **{status_counts.get('unknown', 0)}** | Learning: **{status_counts.get('learning', 0)}** | "
        f"Known: **{status_counts.get('known', 0)}** | Mastered: **{status_counts.get('mastered', 0)}**",
        "",
        "## Status Map\n",
        "\n".join(status_lines),
        "\n## Facet Map\n",
        "\n".join(facet_lines) if facet_lines else "No facet tags yet.",
        "\n## Review Queue\n",
        md_table(["Priority", "Knowledge point", "Facet", "Status", "Due", "Reason"], priority_rows) if priority_rows else "No review items yet.",
        "\n## Live Views\n",
        "- [[Wiki/Knowledge Points|Knowledge Points]]\n",
        "![[_meta/concepts.base]]\n",
        "![[_meta/review-queue.base]]\n",
        "## Visual Maps\n",
        "- [[Maps/Knowledge Graph.canvas|Knowledge Graph Canvas]]",
        "- [[Maps/Concept Relations|Core Knowledge Boundary]]",
        "- [[wiki-export/reader-learner-graph.html|Standalone Graph HTML]]",
    ]).rstrip() + "\n"


def build_glossary_note(profile: dict[str, Any], concept_links: dict[str, str]) -> str:
    rows = []
    for concept_id, concept in sorted((profile.get("concepts", {}) or {}).items()):
        if not isinstance(concept, dict):
            continue
        rows.append([
            concept_links.get(concept_id, concept_id),
            clean_text(concept.get("translation"), 120),
            concept.get("status", "unrated"),
            ", ".join(clean_text(item, 60) for item in concept.get("learning_needs", []) or []),
            concept_summary(concept, 120),
        ])
    return "\n".join([
        frontmatter({
            "type": "glossary",
            "title": "Glossary",
            "summary": "Bilingual glossary of learner knowledge points.",
            "tags": ["reader-learner", "glossary"],
            "updated": profile.get("updated_at", ""),
        }),
        "# Glossary\n",
        md_table(["Knowledge point", "Translation", "Status", "Facets", "Summary"], rows) if rows else "No knowledge points yet.",
    ]).rstrip() + "\n"


def build_knowledge_points_note(profile: dict[str, Any], concept_links: dict[str, str]) -> str:
    rows = []
    concepts = [
        (concept_id, concept)
        for concept_id, concept in (profile.get("concepts", {}) or {}).items()
        if isinstance(concept, dict)
    ]
    concepts.sort(key=lambda item: (-int_value(item[1].get("review_priority")), item[1].get("status", ""), item[1].get("label", "")))
    for concept_id, concept in concepts:
        stats = concept.get("stats", {}) or {}
        rows.append([
            concept_links.get(concept_id, concept_id),
            BOUNDARY_BUCKETS[concept_boundary_bucket(concept)]["label"],
            domain_label(concept_domain(concept_id, concept)),
            concept.get("status", "unrated"),
            concept.get("review_priority", ""),
            concept.get("next_review_at", ""),
            ", ".join(FACET_LABELS.get(normalize_facet(item), normalize_facet(item)) for item in concept.get("learning_needs", []) or []) or "General",
            stats.get("seen", len(concept.get("event_ids", []) or [])),
            concept_summary(concept, 140),
        ])
    return "\n".join([
        frontmatter({
            "type": "knowledge_points",
            "title": "Knowledge Points",
            "summary": "Knowledge-point-centered map of the user's reading boundary.",
            "tags": ["reader-learner", "knowledge-points"],
            "updated": profile.get("updated_at", ""),
        }),
        "# Knowledge Points\n",
        "> [!summary] Knowledge-point-centered view",
        "> This page is the main organized layer. Evidence signals remain attached to knowledge points and are not first-class notes unless exported with `--include-events`.",
        "",
        md_table(["Knowledge point", "Boundary", "Domain", "Status", "Priority", "Next review", "Facet needs", "Signals", "Summary"], rows) if rows else "No knowledge points yet.",
    ]).rstrip() + "\n"


def build_status_moc_note(status: str, profile: dict[str, Any], concept_links: dict[str, str]) -> str:
    rows = []
    for concept_id, concept in sorted((profile.get("concepts", {}) or {}).items()):
        if not isinstance(concept, dict) or clean_text(concept.get("status") or "unrated", 40) != status:
            continue
        rows.append([
            concept_links.get(concept_id, concept_id),
            concept.get("review_priority", ""),
            concept.get("next_review_at", ""),
            concept_summary(concept, 150),
        ])
    return "\n".join([
        frontmatter({
            "type": "moc",
            "title": f"Status - {status}",
            "summary": f"Knowledge points currently marked {status}.",
            "tags": ["reader-learner", "moc", status_tag(status)],
            "updated": profile.get("updated_at", ""),
        }),
        f"# Status: {status}\n",
        f"> [!{status_callout(status)}] Boundary slice",
        f"> This page collects knowledge points whose current overall status is `{status}`.",
        "",
        md_table(["Knowledge point", "Priority", "Next review", "Summary"], rows) if rows else "No knowledge points in this status.",
    ]).rstrip() + "\n"


def build_facet_moc_note(facet: str, profile: dict[str, Any], concept_links: dict[str, str]) -> str:
    rows = []
    for concept_id, concept in sorted((profile.get("concepts", {}) or {}).items()):
        if not isinstance(concept, dict):
            continue
        needs = {normalize_facet(item) for item in concept.get("learning_needs", []) or []}
        facet_status_map = concept.get("facet_status", {}) or {}
        facet_status = facet_status_map.get(facet, "")
        if not facet_status:
            for raw_facet, raw_status in facet_status_map.items():
                if normalize_facet(raw_facet) == facet:
                    facet_status = raw_status
                    break
        if facet not in needs and facet_status in {"", "unrated"}:
            continue
        rows.append([
            concept_links.get(concept_id, concept_id),
            concept.get("status", ""),
            facet_status or "needs review",
            concept_summary(concept, 140),
        ])
    title = FACET_LABELS.get(facet, facet)
    return "\n".join([
        frontmatter({
            "type": "moc",
            "title": f"Facet - {title}",
            "summary": f"Knowledge points touching the {title} learning facet.",
            "tags": ["reader-learner", "moc", facet_tag(facet)],
            "updated": profile.get("updated_at", ""),
        }),
        f"# Facet: {title}\n",
        "> [!question] Learning facet",
        "> Use this page when the problem is not the concept name itself, but the way you need to understand or use it.",
        "",
        md_table(["Knowledge point", "Overall", "Facet status", "Summary"], rows) if rows else "No knowledge points in this facet.",
    ]).rstrip() + "\n"


def build_concept_relations_note(profile: dict[str, Any], concept_links: dict[str, str]) -> str:
    concepts = [
        (concept_id, concept)
        for concept_id, concept in (profile.get("concepts", {}) or {}).items()
        if isinstance(concept, dict)
    ]
    concepts.sort(key=lambda item: (
        BOUNDARY_BUCKETS[concept_boundary_bucket(item[1])]["rank"],
        -int_value(item[1].get("review_priority")),
        item[1].get("label", ""),
    ))
    bucket_counts = Counter(concept_boundary_bucket(concept) for _concept_id, concept in concepts)
    domain_counts = Counter(concept_domain(concept_id, concept) for concept_id, concept in concepts)
    facet_counts = Counter(concept_primary_facet(concept) for _concept_id, concept in concepts if concept_boundary_bucket(concept) in {"active_gap", "probe_gap"})
    lines = [
        frontmatter({
            "type": "map",
            "title": "Core Knowledge Boundary",
            "summary": "Mermaid overview of the user's known anchors, active gaps, domains, and facet-level blockers.",
            "tags": ["reader-learner", "map", "graph"],
            "updated": profile.get("updated_at", ""),
        }),
        "# Core Knowledge Boundary\n",
        "> [!summary] What this map means",
        "> The center is the reading boundary: known anchors support explanation, active gaps block fluent reading, and probe gaps are concepts seen but not yet judged.",
        "",
        "```mermaid",
        "flowchart TB",
        '  Boundary["Reading Knowledge Boundary"]',
    ]
    for bucket_id, info in BOUNDARY_BUCKETS.items():
        count = bucket_counts.get(bucket_id, 0)
        lines.append(f'  Boundary --> B_{bucket_id}["{info["label"]} ({count})"]')
    lines.append('  B_active_gap --> DomainSummary["Knowledge domains"]')
    lines.append('  B_active_gap --> FacetSummary["Why it blocks reading"]')
    for domain_id, _label, _needles in DOMAIN_RULES:
        if domain_counts.get(domain_id, 0):
            lines.append(f'  DomainSummary --> D_{domain_id}["{domain_label(domain_id)} ({domain_counts[domain_id]})"]')
    for facet, count in facet_counts.most_common():
        facet_node = f"F_{slug_fragment(facet)}"
        lines.append(f'  FacetSummary --> {facet_node}["{FACET_LABELS.get(facet, facet)} gap ({count})"]')
    lines.append("```")
    known_rows = []
    gap_rows = []
    probe_rows = []
    for concept_id, concept in concepts:
        row = [
            concept_links.get(concept_id, concept_id),
            domain_label(concept_domain(concept_id, concept)),
            FACET_LABELS.get(concept_primary_facet(concept), concept_primary_facet(concept)),
            concept.get("status", "unrated"),
            concept.get("review_priority", 0),
        ]
        bucket = concept_boundary_bucket(concept)
        if bucket == "known_anchor":
            known_rows.append(row)
        elif bucket == "active_gap":
            gap_rows.append(row)
        elif bucket == "probe_gap":
            probe_rows.append(row)
    lines.extend([
        "\n## Boundary Summary\n",
        md_table(
            ["Boundary", "Count", "Meaning"],
            [
                [info["label"], bucket_counts.get(bucket_id, 0), info["summary"]]
                for bucket_id, info in BOUNDARY_BUCKETS.items()
            ],
        ),
        "\n## Known Anchors\n",
        md_table(["Knowledge point", "Domain", "Facet", "Status", "Priority"], known_rows) if known_rows else "No known anchors yet.",
        "\n## Core Gaps\n",
        md_table(["Knowledge point", "Domain", "Facet", "Status", "Priority"], gap_rows) if gap_rows else "No active gaps yet.",
        "\n## Unrated Probes\n",
        md_table(["Knowledge point", "Domain", "Facet", "Status", "Priority"], probe_rows) if probe_rows else "No unrated probes yet.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def build_taxonomy_note(profile: dict[str, Any]) -> str:
    concepts = profile.get("concepts", {}) or {}
    facet_counts: Counter[str] = Counter()
    for concept in concepts.values():
        if not isinstance(concept, dict):
            continue
        for need in concept.get("learning_needs", []) or []:
            facet_counts[normalize_facet(need)] += 1
    facet_lines = []
    for facet, label in FACET_LABELS.items():
        tag = facet_tag(facet)
        facet_lines.append(f"- `{tag}` - {label}; used by {facet_counts.get(facet, 0)} knowledge points.")
    return "\n".join([
        frontmatter({
            "type": "taxonomy",
            "title": "Reader Learner Tag Taxonomy",
            "summary": "Controlled tags used by the generated vault.",
            "tags": ["reader-learner", "taxonomy"],
            "updated": profile.get("updated_at", ""),
        }),
        "# Reader Learner Tag Taxonomy\n",
        "## Rules\n",
        "- Keep tags lowercase and slash-scoped.",
        "- `status/*` marks the user's current boundary.",
        "- `facet/*` marks why a concept needs review.",
        "- `type/*` marks the generated note class.\n",
        "## Status Tags\n",
        "\n".join(f"- `{status_tag(status)}` - {status}" for status in STATUS_ORDER),
        "\n## Facet Tags\n",
        "\n".join(facet_lines),
        "\n## Type Tags\n",
        "- `type/concept`\n- `type/source`\n- `type/evidence`",
    ]).rstrip() + "\n"


def build_concepts_base() -> str:
    return """filters:
  and:
    - file.inFolder("Concepts")
properties:
  file.name:
    displayName: Knowledge Point
  note.status:
    displayName: Status
  note.boundary_bucket:
    displayName: Boundary
  note.domain:
    displayName: Domain
  note.translation:
    displayName: Translation
  note.review_priority:
    displayName: Priority
  note.next_review_at:
    displayName: Next Review
  note.summary:
    displayName: Summary
views:
  - type: table
    name: By Status
    groupBy:
      property: status
      direction: ASC
    order:
      - file.name
      - boundary_bucket
      - domain
      - translation
      - review_priority
      - next_review_at
      - summary
  - type: cards
    name: Cards
    order:
      - file.name
      - status
      - boundary_bucket
      - domain
      - summary
"""


def build_review_base() -> str:
    return """filters:
  and:
    - note.review_priority > 0
    - or:
        - file.inFolder("Reviews")
        - file.inFolder("Concepts")
properties:
  file.name:
    displayName: Page
  note.status:
    displayName: Status
  note.review_priority:
    displayName: Priority
  note.next_review_at:
    displayName: Due
  note.summary:
    displayName: Summary
views:
  - type: table
    name: Review Items
    order:
      - file.name
      - status
      - review_priority
      - next_review_at
      - summary
"""


def build_evidence_base() -> str:
    return """filters:
  and:
    - file.inFolder("Evidence")
properties:
  file.name:
    displayName: Evidence
  note.status:
    displayName: Status
  note.facet:
    displayName: Facet
  note.summary:
    displayName: Signal
  note.updated:
    displayName: Time
views:
  - type: table
    name: Evidence Timeline
    groupBy:
      property: facet
      direction: ASC
    order:
      - file.name
      - status
      - summary
      - updated
"""


def build_templates() -> dict[Path, str]:
    return {
        Path("Templates") / "Concept Note Template.md": "\n".join([
            "---",
            'type: "concept"',
            'category: "concept"',
            'status: "unrated"',
            "tags: [reader-learner, type/concept, status/unrated]",
            'summary: ""',
            "---",
            "# {{title}}\n",
            "> [!info] Boundary\n> Status, facet, and review fields are managed in `knowledge_profile.json`.\n",
            "## Key Idea\n\n## Sources\n\n## Open Questions\n",
        ]),
        Path("Templates") / "Evidence Signal Template.md": "\n".join([
            "---",
            'type: "evidence"',
            "tags: [reader-learner, type/evidence]",
            'summary: ""',
            "---",
            "# Evidence Signal\n",
            "## Signal\n\n## Selected Text\n\n## Question\n",
        ]),
    }


def build_css_snippet() -> str:
    return """.markdown-preview-view .callout[data-callout="danger"] {
  --callout-color: 225, 87, 89;
}
.markdown-preview-view .callout[data-callout="warning"] {
  --callout-color: 242, 142, 43;
}
.markdown-preview-view .callout[data-callout="success"] {
  --callout-color: 89, 161, 79;
}
.markdown-preview-view table {
  font-size: 0.92em;
}
.markdown-preview-view h1,
.markdown-preview-view h2 {
  letter-spacing: 0;
}
"""


def build_canvas(
    profile: dict[str, Any],
    concept_rel: dict[str, Path],
    source_rel: dict[str, Path],
    concept_links: dict[str, str],
) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    def add_file_node(node_id: str, rel_path: Path, x: int, y: int, width: int = 360, height: int = 220, color: str | None = None) -> None:
        node = {
            "id": node_id,
            "type": "file",
            "file": rel_path.as_posix(),
            "x": x,
            "y": y,
            "width": width,
            "height": height,
        }
        if color:
            node["color"] = color
        nodes.append(node)

    def add_text_node(node_id: str, text: str, x: int, y: int, width: int = 260, height: int = 150, color: str | None = None) -> None:
        node = {
            "id": node_id,
            "type": "text",
            "text": text,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
        }
        if color:
            node["color"] = color
        nodes.append(node)

    def add_group_node(node_id: str, label: str, x: int, y: int, width: int, height: int, color: str | None = None) -> None:
        node = {
            "id": node_id,
            "type": "group",
            "label": label,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
        }
        if color:
            node["color"] = color
        nodes.append(node)

    def add_edge(edge_id: str, from_node: str, to_node: str, label: str = "") -> None:
        edge = {
            "id": edge_id,
            "fromNode": from_node,
            "fromSide": "right",
            "toNode": to_node,
            "toSide": "left",
        }
        if label:
            edge["label"] = label
        edges.append(edge)

    concepts = [
        (concept_id, concept)
        for concept_id, concept in (profile.get("concepts", {}) or {}).items()
        if isinstance(concept, dict) and concept_id in concept_rel
    ]
    concepts.sort(key=lambda item: (
        BOUNDARY_BUCKETS[concept_boundary_bucket(item[1])]["rank"],
        -int_value(item[1].get("review_priority")),
        item[1].get("label", ""),
    ))
    by_bucket: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    by_facet: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    for concept_id, concept in concepts:
        bucket = concept_boundary_bucket(concept)
        by_bucket[bucket].append((concept_id, concept))
        if bucket in {"active_gap", "probe_gap"}:
            by_facet[concept_primary_facet(concept)].append((concept_id, concept))

    add_text_node(
        "legend",
        "Core boundary view\nRead left to right: navigation -> known anchors -> active unknown core -> unrated probes -> facet blockers. Only top cards are shown here; use Knowledge Points for the full table.",
        -980,
        -500,
        720,
        150,
        "#BAB0AC",
    )
    add_file_node("dashboard", Path("01 Learning Dashboard.md"), -980, -280, 320, 180, "#4E79A7")
    add_file_node("knowledge-points", Path("Wiki") / "Knowledge Points.md", -980, -40, 320, 180, "#4E79A7")
    add_file_node("core-boundary", Path("Maps") / "Concept Relations.md", -980, 200, 320, 180, "#4E79A7")
    add_edge("dashboard-knowledge-points", "dashboard", "knowledge-points", "table")
    add_edge("knowledge-points-boundary", "knowledge-points", "core-boundary", "map")

    def card_text(concept_id: str, concept: dict[str, Any]) -> str:
        label = clean_text(concept.get("label") or concept_id, 60)
        domain = domain_label(concept_domain(concept_id, concept))
        facet = FACET_LABELS.get(concept_primary_facet(concept), concept_primary_facet(concept))
        return f"{concept_links.get(concept_id, label)}\n{concept.get('status', 'unrated')} P{concept.get('review_priority', 0)}\n{domain} / {facet}"

    group_specs = {
        "known_anchor": (-560, -420, 360, 520, 4),
        "active_gap": (-120, -420, 760, 760, 8),
        "probe_gap": (720, -420, 380, 520, 5),
        "peripheral": (720, 160, 380, 260, 3),
    }
    for bucket_id, (x, y, width, height, limit) in group_specs.items():
        info = BOUNDARY_BUCKETS[bucket_id]
        values = by_bucket.get(bucket_id, [])
        add_group_node(f"group-{bucket_id}", f"{info['label']} ({len(values)})", x, y, width, height, info["color"])
        add_edge(f"nav-{bucket_id}", "core-boundary", f"group-{bucket_id}", "boundary")
        if bucket_id == "active_gap":
            card_w, card_h = 330, 92
            for index, (concept_id, concept) in enumerate(values[:limit]):
                col = index % 2
                row = index // 2
                add_text_node(
                    f"card-{bucket_id}-{index}",
                    card_text(concept_id, concept),
                    x + 30 + col * 365,
                    y + 80 + row * 122,
                    card_w,
                    card_h,
                    STATUS_COLORS.get(clean_text(concept.get("status") or "unrated", 40), info["color"]),
                )
            if len(values) > limit:
                add_text_node(
                    f"more-{bucket_id}",
                    f"+ {len(values) - limit} more active gaps\nSee [[Wiki/Knowledge Points|Knowledge Points]]",
                    x + 30,
                    y + 80 + 4 * 122,
                    695,
                    90,
                    "#BAB0AC",
                )
        else:
            for index, (concept_id, concept) in enumerate(values[:limit]):
                add_text_node(
                    f"card-{bucket_id}-{index}",
                    card_text(concept_id, concept),
                    x + 25,
                    y + 80 + index * 116,
                    width - 50,
                    92,
                    STATUS_COLORS.get(clean_text(concept.get("status") or "unrated", 40), info["color"]),
                )

    facet_x, facet_y = 1180, -420
    facet_values = sorted(by_facet.items(), key=lambda item: (-len(item[1]), item[0]))
    add_group_node("group-facets", "Facet blockers", facet_x, facet_y, 400, 640, "#F28E2B")
    add_edge("nav-facets", "core-boundary", "group-facets", "facet")
    for index, (facet, values) in enumerate(facet_values[:6]):
        add_text_node(
            f"facet-{slug_fragment(facet)}",
            f"{FACET_LABELS.get(facet, facet)}\n{len(values)} gaps",
            facet_x + 30,
            facet_y + 80 + index * 88,
            340,
            70,
            "#F28E2B",
        )
    return {"nodes": nodes, "edges": edges}


def build_graph_export(
    profile: dict[str, Any],
    concept_rel: dict[str, Path],
    source_rel: dict[str, Path],
    event_rel: dict[str, Path],
    include_events: bool = False,
) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    links: list[dict[str, Any]] = []
    concepts = [
        (concept_id, concept)
        for concept_id, concept in (profile.get("concepts", {}) or {}).items()
        if isinstance(concept, dict) and concept_id in concept_rel
    ]
    concepts.sort(key=lambda item: (
        BOUNDARY_BUCKETS[concept_boundary_bucket(item[1])]["rank"],
        -int_value(item[1].get("review_priority")),
        item[1].get("label", ""),
    ))
    bucket_counts = Counter(concept_boundary_bucket(concept) for _concept_id, concept in concepts)
    domain_counts = Counter(concept_domain(concept_id, concept) for concept_id, concept in concepts)
    facet_counts = Counter(concept_primary_facet(concept) for _concept_id, concept in concepts if concept_boundary_bucket(concept) in {"active_gap", "probe_gap"})

    nodes.append({
        "id": "boundary/root",
        "label": "Reading Knowledge Boundary",
        "category": "boundary",
        "status": "boundary",
        "tags": ["reader-learner", "boundary"],
        "summary": "Known anchors, active gaps, probe gaps, domains, and facet-level blockers.",
        "community": 10,
        "level": 0,
    })
    for bucket_id, info in BOUNDARY_BUCKETS.items():
        nodes.append({
            "id": f"boundary/{bucket_id}",
            "label": f"{info['label']} ({bucket_counts.get(bucket_id, 0)})",
            "category": "boundary",
            "status": bucket_id,
            "tags": ["reader-learner", f"boundary/{bucket_id}"],
            "summary": info["summary"],
            "community": info["rank"],
            "level": 1,
        })
        links.append({
            "source": "boundary/root",
            "target": f"boundary/{bucket_id}",
            "relation": "contains",
            "confidence": "DERIVED",
            "typed": True,
        })
    for domain_id, _label, _needles in DOMAIN_RULES:
        if not domain_counts.get(domain_id):
            continue
        nodes.append({
            "id": f"domain/{domain_id}",
            "label": f"{domain_label(domain_id)} ({domain_counts[domain_id]})",
            "category": "domain",
            "status": "domain",
            "tags": ["reader-learner", f"domain/{domain_id}"],
            "summary": "Knowledge-chain domain used to group related reading blockers.",
            "community": 20,
            "level": 1,
        })
        links.append({
            "source": "boundary/root",
            "target": f"domain/{domain_id}",
            "relation": "contains",
            "confidence": "DERIVED",
            "typed": True,
        })
    for facet, count in facet_counts.most_common():
        nodes.append({
            "id": f"facet/{facet}",
            "label": f"{FACET_LABELS.get(facet, facet)} gap ({count})",
            "category": "facet",
            "status": "facet",
            "tags": ["reader-learner", facet_tag(facet)],
            "summary": "Why the knowledge point blocks reading: definition, math derivation, paper usage, etc.",
            "community": 30,
            "level": 1,
        })
        links.append({
            "source": "boundary/root",
            "target": f"facet/{facet}",
            "relation": "contains",
            "confidence": "DERIVED",
            "typed": True,
        })

    for concept_id, concept in concepts:
        status = clean_text(concept.get("status") or "unrated", 40)
        bucket = concept_boundary_bucket(concept)
        domain = concept_domain(concept_id, concept)
        facet = concept_primary_facet(concept)
        concept_node = rel_no_suffix(concept_rel[concept_id])
        nodes.append({
            "id": concept_node,
            "label": clean_text(concept.get("label") or concept_id, 160),
            "category": "concept",
            "status": status,
            "boundary_bucket": bucket,
            "domain": domain,
            "primary_facet": facet,
            "priority": int_value(concept.get("review_priority")),
            "tags": unique_clean([
                "reader-learner",
                status_tag(status),
                f"boundary/{bucket}",
                f"domain/{domain}",
                facet_tag(facet),
            ]),
            "summary": concept_summary(concept, 200),
            "community": BOUNDARY_BUCKETS[bucket]["rank"],
            "level": 2,
        })
        links.append({
            "source": f"boundary/{bucket}",
            "target": concept_node,
            "relation": "has_anchor" if bucket == "known_anchor" else "has_gap",
            "confidence": "DERIVED",
            "typed": True,
        })

    if include_events:
        for source_id, source in sorted((profile.get("sources", {}) or {}).items()):
            if not isinstance(source, dict) or source_id not in source_rel:
                continue
            nodes.append({
                "id": rel_no_suffix(source_rel[source_id]),
                "label": clean_text(source.get("title") or source_id, 160),
                "category": "source",
                "status": "source",
                "tags": ["reader-learner", "source"],
                "summary": f"{len(source.get('event_ids', []) or [])} evidence signals.",
                "community": 40,
                "level": 3,
            })
        for event in profile.get("events", []) or []:
            if not isinstance(event, dict) or event.get("event_id") not in event_rel:
                continue
            event_id = event.get("event_id", "")
            concept_id = event.get("concept_id", "")
            source_id = event.get("source_id", "")
            nodes.append({
                "id": rel_no_suffix(event_rel[event_id]),
                "label": event_id,
                "category": "evidence",
                "status": event.get("status", "unrated"),
                "tags": unique_clean(["reader-learner", "evidence", status_tag(event.get("status", "unrated"))]),
                "summary": clip(event.get("user_question") or event.get("note") or event.get("selected_text"), 180),
                "community": 7,
            })
            if concept_id in concept_rel:
                links.append({
                    "source": rel_no_suffix(event_rel[event_id]),
                    "target": rel_no_suffix(concept_rel[concept_id]),
                    "relation": "evidence_for",
                    "confidence": "EXTRACTED",
                    "typed": True,
                })
            if source_id in source_rel:
                links.append({
                    "source": rel_no_suffix(event_rel[event_id]),
                    "target": rel_no_suffix(source_rel[source_id]),
                    "relation": "derived_from",
                    "confidence": "EXTRACTED",
                    "typed": True,
                })

    return {
        "directed": False,
        "multigraph": False,
        "graph": {
            "exported_at": profile.get("updated_at", ""),
            "total_nodes": len(nodes),
            "total_edges": len(links),
            "source": "reader-learner",
            "view": "core-knowledge-boundary" if not include_events else "core-knowledge-boundary-with-evidence",
        },
        "nodes": nodes,
        "links": links,
    }


def build_graph_html(graph: dict[str, Any]) -> str:
    degrees: Counter[str] = Counter()
    for link in graph.get("links", []):
        degrees[link.get("source", "")] += 1
        degrees[link.get("target", "")] += 1
    nodes = []
    for node in graph.get("nodes", []):
        status = node.get("status", "unrated")
        category = node.get("category", "")
        if category == "boundary" and str(status) in BOUNDARY_BUCKETS:
            color = BOUNDARY_BUCKETS[str(status)]["color"]
        elif category == "boundary":
            color = "#4E79A7"
        elif category == "domain":
            domain_id = str(node.get("id", "")).split("/", 1)[-1]
            color = DOMAIN_COLORS.get(domain_id, "#9C755F")
        elif category == "facet":
            color = "#F28E2B"
        else:
            color = STATUS_COLORS.get(status, "#BAB0AC")
        nodes.append({
            "id": node.get("id"),
            "label": node.get("label"),
            "color": color,
            "size": min(56, 14 + degrees[node.get("id", "")] * 3 + (10 if category in {"boundary", "domain", "facet"} else 0)),
            "level": node.get("level", 2),
            "shape": "box" if category in {"boundary", "domain", "facet"} else "dot",
            "title": f"{category} | {', '.join(node.get('tags', []))}<br>{node.get('summary', '')}",
        })
    edges = []
    for link in graph.get("links", []):
        relation = link.get("relation", "related_to")
        edges.append({
            "from": link.get("source"),
            "to": link.get("target"),
            "label": relation if link.get("typed") else "",
            "color": EDGE_COLORS.get(relation, "#666666"),
        })
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Reader Learner Boundary Graph</title>
  <style>
    body {{ margin: 0; font-family: system-ui, -apple-system, Segoe UI, sans-serif; background: #111827; color: #f9fafb; }}
    header {{ padding: 16px 20px; border-bottom: 1px solid #374151; }}
    #graph {{ width: 100vw; height: calc(100vh - 74px); }}
    .legend {{ font-size: 13px; color: #d1d5db; }}
  </style>
</head>
<body>
  <header>
    <strong>Reader Learner Boundary Graph</strong>
    <div class="legend">Boundary buckets, knowledge domains, and facet blockers are explicit nodes. Sources are omitted unless exported with --include-events.</div>
  </header>
  <div id="graph"></div>
  <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
  <script>
    const nodes = new vis.DataSet({json.dumps(nodes, ensure_ascii=False)});
    const edges = new vis.DataSet({json.dumps(edges, ensure_ascii=False)});
    new vis.Network(document.getElementById("graph"), {{nodes, edges}}, {{
      layout: {{ hierarchical: {{ enabled: true, direction: "LR", sortMethod: "directed", levelSeparation: 260, nodeSpacing: 170 }} }},
      nodes: {{ font: {{ color: "#f9fafb", size: 13 }} }},
      edges: {{ arrows: "to", font: {{ color: "#d1d5db", size: 10, strokeWidth: 0 }}, smooth: true }},
      physics: false,
      interaction: {{ hover: true, tooltipDelay: 80 }}
    }});
  </script>
</body>
</html>
"""


def powershell_single_quote(value: str) -> str:
    return value.replace("'", "''")


def vault_id_for(vault: Path) -> str:
    return hashlib.sha1(str(vault).casefold().encode("utf-8", errors="replace")).hexdigest()[:16]


def write_open_scripts(profile_dir: Path, vault: Path, obsidian_app: Path) -> list[Path]:
    ps1_path = profile_dir / "open_reader_learner_obsidian.ps1"
    restart_ps1_path = profile_dir / "restart_reader_learner_obsidian.ps1"
    diagnose_ps1_path = profile_dir / "diagnose_reader_learner_obsidian.ps1"
    cmd_path = profile_dir / "open_reader_learner_obsidian.cmd"
    vault_id = vault_id_for(vault)
    ps1 = "\n".join([
        "param([switch]$Restart)",
        "$ErrorActionPreference = 'Stop'",
        f"$Obsidian = '{powershell_single_quote(str(obsidian_app))}'",
        f"$Vault = '{powershell_single_quote(str(vault))}'",
        f"$VaultId = '{vault_id}'",
        "if (-not (Test-Path -LiteralPath $Obsidian)) { throw \"Obsidian.exe not found: $Obsidian\" }",
        "if (-not (Test-Path -LiteralPath $Vault)) { throw \"Vault not found: $Vault\" }",
        "$ConfigDir = Join-Path $env:APPDATA 'Obsidian'",
        "$ConfigPath = Join-Path $ConfigDir 'obsidian.json'",
        "New-Item -ItemType Directory -Force -Path $ConfigDir | Out-Null",
        "if (Test-Path -LiteralPath $ConfigPath) {",
        "  $Config = Get-Content -Encoding UTF8 -Raw -LiteralPath $ConfigPath | ConvertFrom-Json",
        "} else {",
        "  $Config = [pscustomobject]@{ vaults = [pscustomobject]@{} }",
        "}",
        "if (-not $Config.PSObject.Properties['vaults']) {",
        "  $Config | Add-Member -NotePropertyName 'vaults' -NotePropertyValue ([pscustomobject]@{})",
        "}",
        "$ExistingId = $null",
        "foreach ($Prop in $Config.vaults.PSObject.Properties) {",
        "  if ($Prop.Value.path -eq $Vault) { $ExistingId = $Prop.Name }",
        "}",
        "if ($ExistingId) { $VaultId = $ExistingId }",
        "$NowMs = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()",
        "$VaultEntry = [pscustomobject]@{ path = $Vault; ts = $NowMs; open = $true }",
        "if ($Config.vaults.PSObject.Properties[$VaultId]) {",
        "  $Config.vaults.$VaultId = $VaultEntry",
        "} else {",
        "  $Config.vaults | Add-Member -NotePropertyName $VaultId -NotePropertyValue $VaultEntry",
        "}",
        "foreach ($Prop in $Config.vaults.PSObject.Properties) {",
        "  if ($Prop.Name -ne $VaultId -and $Prop.Value.PSObject.Properties['open']) { $Prop.Value.open = $false }",
        "}",
        "$Config | ConvertTo-Json -Depth 12 | Set-Content -Encoding UTF8 -LiteralPath $ConfigPath",
        "if ($Restart) {",
        "  Get-Process -Name Obsidian -ErrorAction SilentlyContinue | Stop-Process -Force",
        "  Start-Sleep -Seconds 2",
        "  Start-Process -FilePath $Obsidian",
        "  return",
        "}",
        "$Running = Get-Process -Name Obsidian -ErrorAction SilentlyContinue",
        "if ($Running) {",
        "  Write-Host 'reader-learner vault registered. Obsidian is already running; run restart_reader_learner_obsidian.ps1 if it is not visible.'",
        "} else {",
        "  Start-Process -FilePath $Obsidian",
        "}",
        "",
    ])
    restart_ps1 = "\n".join([
        "$ErrorActionPreference = 'Stop'",
        "$Script = Join-Path $PSScriptRoot 'open_reader_learner_obsidian.ps1'",
        "& $Script -Restart",
        "",
    ])
    diagnose_ps1 = "\n".join([
        "$ErrorActionPreference = 'Continue'",
        f"$Obsidian = '{powershell_single_quote(str(obsidian_app))}'",
        f"$Vault = '{powershell_single_quote(str(vault))}'",
        "$Cli = Join-Path (Split-Path -Parent $Obsidian) 'Obsidian.com'",
        "Write-Host \"Vault path: $Vault\"",
        "Write-Host \"Obsidian app: $Obsidian\"",
        "Write-Host \"Obsidian CLI: $Cli\"",
        "Write-Host \"Vault exists: $(Test-Path -LiteralPath $Vault)\"",
        "Write-Host \"App exists: $(Test-Path -LiteralPath $Obsidian)\"",
        "Write-Host \"CLI exists: $(Test-Path -LiteralPath $Cli)\"",
        "Write-Host 'Registered vaults:'",
        "$ConfigPath = Join-Path (Join-Path $env:APPDATA 'Obsidian') 'obsidian.json'",
        "if (Test-Path -LiteralPath $ConfigPath) { Get-Content -Encoding UTF8 -Raw -LiteralPath $ConfigPath } else { Write-Host 'No obsidian.json found.' }",
        "Write-Host 'Running Obsidian processes:'",
        "Get-Process -Name Obsidian -ErrorAction SilentlyContinue | Select-Object ProcessName,Id,StartTime | Format-Table | Out-String | Write-Host",
        "if (Test-Path -LiteralPath $Cli) {",
        "  Write-Host 'CLI probe: version'",
        "  & $Cli version",
        "  Write-Host 'CLI probe: vaults'",
        "  & $Cli vaults",
        "} else {",
        "  Write-Host 'CLI probe skipped: Obsidian.com not found.'",
        "}",
        "",
    ])
    cmd = "\n".join([
        "@echo off",
        "powershell -ExecutionPolicy Bypass -File \"%~dp0open_reader_learner_obsidian.ps1\"",
        "",
    ])
    with ps1_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(ps1)
    with restart_ps1_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(restart_ps1)
    with diagnose_ps1_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(diagnose_ps1)
    with cmd_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(cmd)
    return [ps1_path, restart_ps1_path, diagnose_ps1_path, cmd_path]


def export_vault(
    profile_path: Path,
    vault: Path | None = None,
    obsidian_app: Path | None = None,
    clean: bool = False,
    include_events: bool = False,
) -> dict[str, Any]:
    profile_path = profile_path.expanduser().resolve()
    profile = ensure_v2(load_json(profile_path))
    vault = (vault or profile_path.parent / "obsidian-vault").expanduser().resolve()
    obsidian_app = (obsidian_app or Path(DEFAULT_OBSIDIAN_APP)).expanduser()
    vault.mkdir(parents=True, exist_ok=True)

    written: set[str] = set()
    concepts = profile.get("concepts", {}) or {}
    sources = profile.get("sources", {}) or {}
    events = profile.get("events", []) or []

    concept_rel = {
        concept_id: concept_rel_path(concept_id, concept)
        for concept_id, concept in concepts.items()
        if isinstance(concept, dict)
    }
    source_rel = {
        source_id: source_rel_path(source_id, source)
        for source_id, source in sources.items()
        if isinstance(source, dict)
    }
    event_rel = {
        event.get("event_id", ""): event_rel_path(event.get("event_id", "event"))
        for event in events
        if include_events and isinstance(event, dict) and event.get("event_id")
    }
    status_rel = {
        status: Path("Wiki") / "Status" / f"{safe_filename(status)}.md"
        for status in STATUS_ORDER
    }
    facet_names: set[str] = set(FACET_LABELS)
    for concept in concepts.values():
        if not isinstance(concept, dict):
            continue
        for need in concept.get("learning_needs", []) or []:
            facet_names.add(normalize_facet(need))
        for facet, value in (concept.get("facet_status", {}) or {}).items():
            if clean_text(value, 40) != "unrated":
                facet_names.add(normalize_facet(facet))
    facet_rel = {
        facet: Path("Wiki") / "Facets" / f"{safe_filename(slug_fragment(facet))}.md"
        for facet in sorted(facet_names)
    }
    concept_links = {
        concept_id: obsidian_link(path, clean_text(concepts[concept_id].get("label") or concept_id, 160))
        for concept_id, path in concept_rel.items()
    }
    source_links = {
        source_id: obsidian_link(path, clean_text(sources[source_id].get("title") or source_id, 160))
        for source_id, path in source_rel.items()
    }
    event_links = {
        event_id: obsidian_link(path, event_id)
        for event_id, path in event_rel.items()
    }
    status_links = {
        status: obsidian_link(path, status)
        for status, path in status_rel.items()
    }
    facet_links = {
        facet: obsidian_link(path, FACET_LABELS.get(facet, facet))
        for facet, path in facet_rel.items()
    }

    events_by_concept: dict[str, list[dict[str, Any]]] = defaultdict(list)
    events_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        if not isinstance(event, dict):
            continue
        events_by_concept[clean_text(event.get("concept_id"), 120)].append(event)
        events_by_source[clean_text(event.get("source_id"), 120)].append(event)

    graph_color_groups = [
        {"query": f"tag:#{status_tag(status)}", "color": {"a": 1, "rgb": STATUS_RGB[status]}}
        for status in STATUS_ORDER
    ]
    graph_color_groups.append({"query": 'path:"Sources"', "color": {"a": 1, "rgb": 7780786}})
    if include_events:
        graph_color_groups.append({"query": 'path:"Evidence"', "color": {"a": 1, "rgb": 11565217}})

    write_json_file(vault, Path(".obsidian") / "app.json", {
        "alwaysUpdateLinks": True,
        "newFileLocation": "current",
        "useMarkdownLinks": False,
        "showFrontmatter": False,
        "livePreview": True,
    }, written)
    write_json_file(vault, Path(".obsidian") / "appearance.json", {
        "theme": "obsidian",
        "baseFontSize": 16,
        "enabledCssSnippets": ["reader-learner"],
    }, written)
    write_json_file(vault, Path(".obsidian") / "core-plugins.json", [
        "file-explorer",
        "global-search",
        "switcher",
        "graph",
        "backlink",
        "outgoing-link",
        "tag-pane",
        "page-preview",
        "templates",
        "canvas",
        "properties",
        "bookmarks",
        "note-composer",
        "command-palette",
    ], written)
    write_json_file(vault, Path(".obsidian") / "templates.json", {"folder": "Templates"}, written)
    write_json_file(vault, Path(".obsidian") / "graph.json", {
        "collapse-filter": True,
        "search": "",
        "showTags": True,
        "showAttachments": False,
        "hideUnresolved": False,
        "showOrphans": True,
        "collapse-color-groups": False,
        "colorGroups": graph_color_groups,
        "collapse-display": True,
        "showArrow": True,
        "textFadeMultiplier": 0,
        "nodeSizeMultiplier": 1.08,
        "lineSizeMultiplier": 1.15,
        "collapse-forces": True,
        "centerStrength": 0.52,
        "repelStrength": 10,
        "linkStrength": 1,
        "linkDistance": 250,
        "scale": 1,
        "close": True,
    }, written)
    write_file(vault, Path(".obsidian") / "snippets" / "reader-learner.css", build_css_snippet(), written)

    write_file(vault, Path("index.md"), build_index_note(profile, concept_links, source_links), written)
    write_file(vault, Path("hot.md"), build_hot_note(profile, concept_links), written)
    write_file(vault, Path("log.md"), build_log_note(profile), written)
    write_file(vault, Path("00 Home.md"), build_home_note(profile, concept_links), written)
    write_file(vault, Path("01 Learning Dashboard.md"), build_learning_dashboard(profile, concept_links, status_links, facet_links), written)
    write_file(vault, Path("Wiki") / "Knowledge Points.md", build_knowledge_points_note(profile, concept_links), written)
    write_file(vault, Path("Wiki") / "Glossary.md", build_glossary_note(profile, concept_links), written)
    write_file(vault, Path("_meta") / "taxonomy.md", build_taxonomy_note(profile), written)
    write_file(vault, Path("_meta") / "concepts.base", build_concepts_base(), written)
    write_file(vault, Path("_meta") / "review-queue.base", build_review_base(), written)
    if include_events:
        write_file(vault, Path("_meta") / "evidence.base", build_evidence_base(), written)
    write_file(vault, Path("Maps") / "Knowledge Boundary.md", build_boundary_map(profile, concept_links), written)
    write_file(vault, Path("Maps") / "Sources Index.md", build_sources_index(profile, source_links), written)
    write_file(vault, Path("Maps") / "Concept Relations.md", build_concept_relations_note(profile, concept_links), written)
    write_file(vault, Path("Reviews") / "Review Queue.md", build_review_note(profile, concept_links, event_links), written)
    for rel_path, text in build_templates().items():
        write_file(vault, rel_path, text, written)
    for status, rel_path in status_rel.items():
        write_file(vault, rel_path, build_status_moc_note(status, profile, concept_links), written)
    for facet, rel_path in facet_rel.items():
        write_file(vault, rel_path, build_facet_moc_note(facet, profile, concept_links), written)

    for concept_id, concept in sorted(concepts.items()):
        if isinstance(concept, dict) and concept_id in concept_rel:
            write_file(
                vault,
                concept_rel[concept_id],
                build_concept_note(concept_id, concept, concept_links, source_links, event_links, events_by_concept),
                written,
            )
    for source_id, source in sorted(sources.items()):
        if isinstance(source, dict) and source_id in source_rel:
            write_file(vault, source_rel[source_id], build_source_note(source_id, source, concept_links, event_links, events_by_source), written)
    if include_events:
        for event in events:
            if isinstance(event, dict) and event.get("event_id") in event_rel:
                write_file(vault, event_rel[event["event_id"]], build_event_note(event, concept_links, source_links), written)

    write_json_file(
        vault,
        Path("Maps") / "Knowledge Graph.canvas",
        build_canvas(profile, concept_rel, source_rel, concept_links),
        written,
    )
    graph_export = build_graph_export(profile, concept_rel, source_rel, event_rel, include_events=include_events)
    write_json_file(vault, Path("wiki-export") / "reader-learner-graph.json", graph_export, written)
    write_file(vault, Path("wiki-export") / "reader-learner-graph.html", build_graph_html(graph_export), written)

    old_files = load_manifest(vault)
    removed = cleanup_old_files(vault, old_files, written) if clean else 0
    manifest = {
        "profile": str(profile_path),
        "vault": str(vault),
        "generated_files": len(written),
        "files": sorted(written),
    }
    with (vault / MANIFEST_NAME).open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(manifest, ensure_ascii=False, indent=2))
    scripts = write_open_scripts(profile_path.parent, vault, obsidian_app)
    return {
        "profile": profile_path,
        "vault": vault,
        "concepts": len(concepts),
        "events": len(events),
        "sources": len(sources),
        "files": len(written),
        "removed": removed,
        "include_events": include_events,
        "open_scripts": scripts,
    }


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", help="Path to knowledge_profile.json. Defaults to nearest project profile.")
    parser.add_argument("--vault", help="Output Obsidian vault. Defaults to <profile-dir>/obsidian-vault.")
    parser.add_argument("--obsidian-app", default=DEFAULT_OBSIDIAN_APP, help="Path to Obsidian.exe for generated open scripts.")
    parser.add_argument("--clean", action="store_true", help="Remove files from the previous managed export that are no longer generated.")
    parser.add_argument("--include-events", action="store_true", help="Also export raw evidence notes. Default is knowledge-point-first and compact evidence only.")
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] = sys.argv[1:]) -> int:
    args = parse_args(argv)
    profile_path = Path(args.profile).expanduser().resolve() if args.profile else find_profile(Path.cwd())
    vault = Path(args.vault).expanduser().resolve() if args.vault else None
    result = export_vault(profile_path, vault=vault, obsidian_app=Path(args.obsidian_app), clean=args.clean, include_events=args.include_events)
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


if __name__ == "__main__":
    raise SystemExit(main())
