#!/usr/bin/env python3
"""Project a reviewed learner profile into a stable, human-facing Obsidian wiki.

This script never mutates knowledge_profile.json. It only updates managed projection
blocks, generated navigation pages, and a compact provenance manifest in the target wiki.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


VALID_STATUSES = {"mastered", "known", "learning", "unknown", "unrated"}
PUBLIC_TYPES = {"concept", "entity", "theme", "question", "synthesis", "claim", "source"}
RELATION_TYPES = {
    "prerequisite",
    "supports",
    "contradicts",
    "extends",
    "example-of",
    "evidence-for",
    "about",
}
MANAGED_START = "<!-- BEGIN PROFILE PROJECTION -->"
MANAGED_END = "<!-- END PROFILE PROJECTION -->"
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?(.*)\Z", re.DOTALL)
LOCAL_PATH_RE = re.compile(r"(?:[A-Za-z]:[\\/]|\\\\)")


@dataclass
class Page:
    path: Path
    route: str
    data: dict[str, Any]
    body: str


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def parse_value(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value.startswith(("[", "{")):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    if value.startswith('"'):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value.strip('"')
    return value


def parse_markdown(path: Path, wiki: Path) -> Page:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"{path.relative_to(wiki)} has no YAML frontmatter")
    data: dict[str, Any] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = parse_value(value)
    route = path.relative_to(wiki).with_suffix("").as_posix()
    return Page(path=path, route=route, data=data, body=match.group(2).lstrip("\r\n"))


def dump_value(value: Any) -> str:
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return json.dumps(str(value), ensure_ascii=False)


def render_document(data: dict[str, Any], body: str) -> str:
    lines = ["---"]
    for key, value in data.items():
        lines.append(f"{key}: {dump_value(value)}")
    lines.extend(["---", "", body.rstrip(), ""])
    return "\n".join(lines)


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    temp.replace(path)


def scan_pages(wiki: Path) -> list[Page]:
    pages: list[Page] = []
    for path in sorted(wiki.rglob("*.md")):
        relative = path.relative_to(wiki)
        if relative.parts[0] in {"_internal", ".obsidian"}:
            continue
        pages.append(parse_markdown(path, wiki))
    return pages


def is_public(page: Page) -> bool:
    return page.data.get("visibility") == "public-wiki" and page.data.get("type") in PUBLIC_TYPES


def page_link(page: Page) -> str:
    return f"[[{page.route}|{page.data.get('title', page.data.get('id', page.route))}]]"


def status_order(status: str) -> tuple[int, str]:
    order = {"mastered": 0, "known": 1, "learning": 2, "unknown": 3, "unrated": 4}
    return (order.get(status, 99), status)


def replace_managed_block(body: str, block: str) -> str:
    replacement = f"{MANAGED_START}\n{block.rstrip()}\n{MANAGED_END}"
    pattern = re.compile(re.escape(MANAGED_START) + r".*?" + re.escape(MANAGED_END), re.DOTALL)
    if pattern.search(body):
        return pattern.sub(replacement, body)
    suffix = "\n\n" if body.rstrip() else ""
    return body.rstrip() + suffix + replacement + "\n"


def source_page_map(pages: Iterable[Page]) -> dict[str, Page]:
    result: dict[str, Page] = {}
    for page in pages:
        if page.data.get("type") != "source":
            continue
        for source_id in page.data.get("profile_source_refs", []) or []:
            if isinstance(source_id, str):
                result[source_id] = page
    return result


def is_stable_profile_concept(concept_id: str) -> bool:
    """Return whether a profile record is safe to expose as a reusable concept."""
    return bool(concept_id) and not concept_id.startswith(("freeform-annotation-", "concept-"))


def profile_concept_id_for_page(page: Page) -> str:
    page_id = str(page.data.get("id") or "")
    derived = page_id[len("concept."):] if page_id.startswith("concept.") else page_id
    return str(page.data.get("profile_concept_id") or derived)


def visible_text(value: Any, fallback: str, limit: int = 160) -> str:
    """Keep generated labels compact and prevent raw local paths entering the wiki."""
    text = " ".join(str(value or "").split())
    if not text or len(text) > limit or LOCAL_PATH_RE.search(text):
        return fallback
    return text


def slugify(value: str, fallback: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not re.search(r"[a-z]", slug):
        return fallback
    return slug[:96].rstrip("-")


def unique_route(directory: str, value: str, existing_routes: set[str], fallback: str) -> str:
    base = slugify(value, fallback)
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]
    route_base = base if base != fallback else f"{fallback}-{digest}"
    candidate = f"{directory}/{route_base}"
    if candidate not in existing_routes:
        return candidate
    return f"{candidate}-{digest}"


def unique_page_id(prefix: str, value: str, existing_ids: set[str], fallback: str) -> str:
    candidate = f"{prefix}.{slugify(value, fallback)}"
    if candidate == f"{prefix}.{fallback}":
        candidate = f"{candidate}-{hashlib.sha1(value.encode('utf-8')).hexdigest()[:8]}"
    if candidate not in existing_ids:
        return candidate
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]
    return f"{candidate}-{digest}"


def generated_source_title(source_id: str, source: dict[str, Any]) -> str:
    for field in ("title", "source_title", "paper_title", "briefing_title"):
        title = visible_text(source.get(field), "")
        if title:
            return title
    return f"Profile source {source_id[-12:]}"


def default_source_page(wiki: Path, route: str, page_id: str, source_id: str, source: dict[str, Any]) -> Page:
    title = generated_source_title(source_id, source)
    body = "\n".join([
        f"# {title}",
        "",
        "## Scope",
        "This concise source summary links stable learner-profile concepts to an immutable source record.",
        "",
        "## Curation",
        "Add a bounded citation or evidence anchor here during review. Raw excerpts, local paths, and event payloads remain in the source layer.",
    ])
    return Page(
        path=wiki / (route + ".md"),
        route=route,
        data={
            "id": page_id,
            "type": "source",
            "title": title,
            "aliases": [],
            "status": "active",
            "visibility": "public-wiki",
            "source_refs": [],
            "profile_source_refs": [source_id],
            "relations": [],
            "updated": str(source.get("last_seen_at") or "")[:10],
            "managed_by": "visible-wiki-bootstrap",
        },
        body=body,
    )


def default_concept_page(
    wiki: Path,
    route: str,
    page_id: str,
    concept_id: str,
    concept: dict[str, Any],
    source_pages: dict[str, Page],
) -> Page:
    title = visible_text(concept.get("label"), concept_id)
    aliases = []
    for alias in concept.get("aliases", []) or []:
        alias_text = visible_text(alias, "")
        if alias_text and alias_text != title and alias_text not in aliases:
            aliases.append(alias_text)
    source_refs = []
    for source_id in concept.get("source_ids", []) or []:
        source_page = source_pages.get(str(source_id))
        if source_page:
            source_page_id = str(source_page.data.get("id") or "")
            if source_page_id and source_page_id not in source_refs:
                source_refs.append(source_page_id)
    body = "\n".join([
        f"# {title}",
        "",
        "## Scope",
        "This is a stable learner-profile concept projection. Add a source-grounded definition during curation.",
        "",
        "## Curation",
        "The profile projection below records the explicit knowledge boundary only; it does not infer understanding from exposure.",
        "",
        "## Relations",
        "Add typed, evidence-backed links here when the relationship is reviewed.",
    ])
    return Page(
        path=wiki / (route + ".md"),
        route=route,
        data={
            "id": page_id,
            "type": "concept",
            "title": title,
            "aliases": aliases,
            "status": "active",
            "profile_concept_id": concept_id,
            "knowledge_status": str(concept.get("status") or "unrated"),
            "visibility": "public-wiki",
            "source_refs": source_refs,
            "profile_source_refs": [],
            "relations": [],
            "updated": str(concept.get("last_seen_at") or "")[:10],
            "managed_by": "visible-wiki-bootstrap",
        },
        body=body,
    )


def bootstrap_profile_pages(profile: dict[str, Any], wiki: Path, pages: list[Page], apply: bool) -> list[str]:
    """Create minimal public pages for all stable profile concepts and source summaries.

    This intentionally skips raw annotations and opaque candidates. Their provenance stays in
    the learner profile, where it can be reviewed and normalized before entering the wiki.
    """
    created: list[str] = []
    existing_routes = {page.route for page in pages}
    existing_ids = {str(page.data.get("id") or "") for page in pages}
    public = [page for page in pages if is_public(page)]
    sources = profile.get("sources") or {}
    mapped_sources = source_page_map(public)

    for source_id, source in sorted(sources.items()):
        if not isinstance(source_id, str) or not isinstance(source, dict) or source_id in mapped_sources:
            continue
        route = unique_route("sources", source_id, existing_routes, "profile-source")
        page_id = unique_page_id("source", source_id, existing_ids, "profile-source")
        page = default_source_page(wiki, route, page_id, source_id, source)
        if write_page(page, wiki, apply):
            created.append(route)
        pages.append(page)
        public.append(page)
        mapped_sources[source_id] = page
        existing_routes.add(route)
        existing_ids.add(page_id)

    concepts = profile.get("concepts") or {}
    mapped_concepts = {
        profile_concept_id_for_page(page)
        for page in public
        if page.data.get("type") == "concept"
    }
    for concept_id, concept in sorted(concepts.items()):
        if (
            not isinstance(concept_id, str)
            or not isinstance(concept, dict)
            or not is_stable_profile_concept(concept_id)
            or concept_id in mapped_concepts
        ):
            continue
        route = unique_route("concepts", concept_id, existing_routes, "profile-concept")
        page_id = unique_page_id("concept", concept_id, existing_ids, "profile-concept")
        page = default_concept_page(wiki, route, page_id, concept_id, concept, mapped_sources)
        if write_page(page, wiki, apply):
            created.append(route)
        pages.append(page)
        public.append(page)
        mapped_concepts.add(concept_id)
        existing_routes.add(route)
        existing_ids.add(page_id)
    return created


def update_concept_page(page: Page, profile: dict[str, Any], source_pages: dict[str, Page]) -> str | None:
    concept_id = profile_concept_id_for_page(page)
    concept = (profile.get("concepts") or {}).get(concept_id)
    if not isinstance(concept, dict):
        return f"{page.route}: profile concept {concept_id!r} is missing"
    status = str(concept.get("status") or "unrated")
    if status not in VALID_STATUSES:
        return f"{page.route}: profile concept {concept_id!r} has invalid status {status!r}"
    page.data["profile_concept_id"] = concept_id
    page.data["knowledge_status"] = status
    page.data["updated"] = str(concept.get("last_seen_at") or profile.get("updated_at") or "")[:10]
    sources = []
    for source_id in concept.get("source_ids", []) or []:
        source_page = source_pages.get(str(source_id))
        sources.append(page_link(source_page) if source_page else f"`{source_id}`")
    lines = [
        "## Profile Projection",
        f"- Knowledge boundary: **{status}**",
        f"- Last seen: {concept.get('last_seen_at') or 'not recorded'}",
        f"- Review priority: {concept.get('review_priority', 0)}",
        "- Profile sources: " + (", ".join(sources) if sources else "not linked to a public source summary"),
    ]
    page.body = replace_managed_block(page.body, "\n".join(lines))
    return None


def update_source_page(page: Page, profile: dict[str, Any]) -> str | None:
    source_ids = [item for item in page.data.get("profile_source_refs", []) or [] if isinstance(item, str)]
    sources = profile.get("sources") or {}
    matched = [sources.get(source_id) for source_id in source_ids if isinstance(sources.get(source_id), dict)]
    if len(matched) != len(source_ids):
        missing = [source_id for source_id in source_ids if source_id not in sources]
        return f"{page.route}: missing profile source ids: {', '.join(missing)}"
    page.data["updated"] = max((str(item.get("last_seen_at") or "")[:10] for item in matched), default="")
    kinds = sorted({str(item.get("source_kind") or "") for item in matched if item.get("source_kind")})
    lines = [
        "## Profile Provenance",
        "- Profile linkage: validated against immutable learner-profile source records.",
        "- Source kinds: " + (", ".join(kinds) if kinds else "not recorded"),
        "- Raw paths, event records, and feedback payloads remain outside this wiki.",
    ]
    page.body = replace_managed_block(page.body, "\n".join(lines))
    return None


def generated_page(route: str, title: str, page_type: str, body: str, updated: str) -> Page:
    return Page(
        path=Path(route + ".md"),
        route=route,
        data={
            "id": f"map.{route.lower().replace('/', '.').replace(' ', '-')}",
            "type": page_type,
            "title": title,
            "visibility": "public-wiki",
            "updated": updated,
            "managed_by": "visible-wiki",
        },
        body=body,
    )


def append_page_links(lines: list[str], pages: Iterable[Page], empty: str) -> None:
    rendered = [f"- {page_link(page)}" for page in pages]
    lines.extend(rendered if rendered else [empty])


def build_home(pages: list[Page], updated: str) -> Page:
    public = [page for page in pages if is_public(page)]
    concepts = [page for page in public if page.data.get("type") == "concept"]
    claims = [page for page in public if page.data.get("type") == "claim"]
    gaps = [page for page in concepts if page.data.get("knowledge_status") in {"learning", "unknown"}]
    core = [page for page in concepts if page.data.get("knowledge_status") in {"mastered", "known"}]
    lines = [
        "# Knowledge Home",
        "",
        "## Maps",
        "- [[maps/Knowledge Boundary|Knowledge Boundary]]",
        "- [[maps/Topic Map|Topic Map]]",
        "- [[maps/Open Questions|Open Questions]]",
        "- [[maps/Evidence Map|Evidence Map]]",
        "- [[maps/Profile Coverage|Profile Coverage]]",
        "",
        "## Current Core",
    ]
    append_page_links(lines, core, "- No curated known/mastered concept pages yet.")
    lines.extend(["", "## Active Gaps"])
    append_page_links(lines, gaps, "- No curated learning/unknown concept pages yet.")
    lines.extend(["", "## Evidence-bearing Claims"])
    append_page_links(lines, claims, "- No curated claims yet.")
    lines.extend([
        "",
        "## Scope",
        f"- Stable public pages: {len(public)}",
        "- Raw PDFs, bundles, feedback, events, pipelines, and profile scheduling remain outside this vault.",
    ])
    return generated_page("Home", "Knowledge Home", "home", "\n".join(lines), updated)


def build_index(pages: list[Page], updated: str) -> Page:
    public = sorted((page for page in pages if is_public(page)), key=lambda page: (str(page.data.get("type")), str(page.data.get("title"))))
    lines = ["# Knowledge Index", ""]
    for page_type in ("concept", "entity", "theme", "question", "synthesis", "claim", "source"):
        group = [page for page in public if page.data.get("type") == page_type]
        lines.extend([f"## {page_type.title()}s", ""])
        append_page_links(lines, group, "- None yet.")
        lines.append("")
    return generated_page("index", "Knowledge Index", "index", "\n".join(lines), updated)


def build_boundary_map(pages: list[Page], updated: str) -> Page:
    concepts = [page for page in pages if is_public(page) and page.data.get("type") == "concept"]
    by_status = {status: sorted((page for page in concepts if page.data.get("knowledge_status") == status), key=lambda page: page.data.get("title", "")) for status in VALID_STATUSES}
    lines = [
        "# Knowledge Boundary",
        "",
        "This map projects only explicit learner-profile ratings. Exposure never upgrades a status.",
        "",
        "```mermaid",
        "flowchart LR",
        f'  M["Mastered ({len(by_status["mastered"])})"]',
        f'  K["Known ({len(by_status["known"])})"]',
        f'  L["Learning ({len(by_status["learning"])})"]',
        f'  U["Unknown ({len(by_status["unknown"])})"]',
        f'  R["Unrated ({len(by_status["unrated"])})"]',
        "  L --> U",
        "  U --> R",
        "```",
        "",
    ]
    for status in ("mastered", "known", "learning", "unknown", "unrated"):
        lines.extend([f"## {status}", ""])
        append_page_links(lines, by_status[status], "- None in the curated wiki.")
        lines.append("")
    lines.extend([
        "## Prerequisite Gaps",
        "- Follow `prerequisite` relations from each learning or unknown concept. Do not infer prerequisites from co-occurrence.",
        "",
        "## Open Questions",
        "- [[maps/Open Questions|Open Questions]]",
    ])
    return generated_page("maps/Knowledge Boundary", "Knowledge Boundary", "map", "\n".join(lines), updated)


def build_topic_map(pages: list[Page], updated: str) -> Page:
    themes = [page for page in pages if is_public(page) and page.data.get("type") == "theme"]
    lines = ["# Topic Map", "", "## Themes", ""]
    append_page_links(lines, sorted(themes, key=lambda item: item.data.get("title", "")), "- No curated themes yet.")
    lines.extend(["", "## Syntheses", ""])
    syntheses = [page for page in pages if is_public(page) and page.data.get("type") == "synthesis"]
    append_page_links(lines, syntheses, "- No curated syntheses yet.")
    return generated_page("maps/Topic Map", "Topic Map", "map", "\n".join(lines), updated)


def build_questions_map(pages: list[Page], updated: str) -> Page:
    questions = [page for page in pages if is_public(page) and page.data.get("type") == "question"]
    lines = ["# Open Questions", "", "Only normalized, source-traceable questions belong here; raw interaction text stays in the learner profile.", ""]
    append_page_links(lines, questions, "- No normalized open questions yet.")
    return generated_page("maps/Open Questions", "Open Questions", "map", "\n".join(lines), updated)


def build_evidence_map(pages: list[Page], updated: str) -> Page:
    claims = [page for page in pages if is_public(page) and page.data.get("type") == "claim"]
    sources = {str(page.data.get("id")): page for page in pages if is_public(page) and page.data.get("type") == "source"}
    lines = ["# Evidence Map", "", "Claims link to concise evidence anchors and source summaries. Raw excerpts and event records are intentionally excluded.", ""]
    for claim in claims:
        refs = [sources[source_id] for source_id in claim.data.get("source_refs", []) or [] if source_id in sources]
        lines.append(f"- {page_link(claim)}")
        if refs:
            lines.extend(f"  - Evidence: {page_link(source)}" for source in refs)
        else:
            lines.append("  - Evidence: source summary pending")
    if not claims:
        lines.append("- No curated claims yet.")
    return generated_page("maps/Evidence Map", "Evidence Map", "map", "\n".join(lines), updated)


def profile_coverage(profile: dict[str, Any], pages: list[Page]) -> dict[str, int]:
    concepts = profile.get("concepts") or {}
    sources = profile.get("sources") or {}
    stable_concepts = {
        concept_id
        for concept_id in concepts
        if isinstance(concept_id, str) and is_stable_profile_concept(concept_id)
    }
    projected_concepts = {
        profile_concept_id_for_page(page)
        for page in pages
        if is_public(page) and page.data.get("type") == "concept"
    }
    projected_sources = set(source_page_map(page for page in pages if is_public(page)))
    return {
        "all_profile_concepts": len(concepts),
        "stable_profile_concepts": len(stable_concepts),
        "mapped_stable_concepts": len(stable_concepts & projected_concepts),
        "freeform_annotations_retained": sum(
            isinstance(concept_id, str) and concept_id.startswith("freeform-annotation-")
            for concept_id in concepts
        ),
        "opaque_candidates_retained": sum(
            isinstance(concept_id, str) and concept_id.startswith("concept-")
            for concept_id in concepts
        ),
        "profile_sources": len(sources),
        "mapped_sources": len(set(sources) & projected_sources),
        "events_retained": len(profile.get("events") or []),
        "review_queue_retained": len(profile.get("review_queue") or []),
        "reading_sessions_retained": len(profile.get("reading_sessions") or []),
    }


def build_profile_coverage_map(profile: dict[str, Any], pages: list[Page], updated: str) -> Page:
    coverage = profile_coverage(profile, pages)
    lines = [
        "# Profile Coverage",
        "",
        "This map makes the complete learner profile auditable without turning raw events or unreviewed text into knowledge nodes.",
        "",
        "## Visible Projection",
        f"- Stable profile concepts: {coverage['stable_profile_concepts']}",
        f"- Visible stable concept pages: {coverage['mapped_stable_concepts']} / {coverage['stable_profile_concepts']}",
        f"- Profile source records: {coverage['profile_sources']}",
        f"- Visible concise source summaries: {coverage['mapped_sources']} / {coverage['profile_sources']}",
        "",
        "## Knowledge Boundary",
        "- [[maps/Knowledge Boundary|Knowledge Boundary]]",
        "- [[maps/Open Questions|Open Questions]]",
        "",
        "## Retained Source-Layer Records",
        f"- All profile concept records: {coverage['all_profile_concepts']}",
        f"- Freeform annotations retained outside the Wiki: {coverage['freeform_annotations_retained']}",
        f"- Opaque candidates retained outside the Wiki: {coverage['opaque_candidates_retained']}",
        f"- Raw events retained in the learner profile: {coverage['events_retained']}",
        f"- Review scheduling records retained in the learner profile: {coverage['review_queue_retained']}",
        f"- Reading-session records retained in the learner profile: {coverage['reading_sessions_retained']}",
        "",
        "No record is discarded by this projection. A raw annotation becomes visible only after it is normalized into a stable concept or a source-traceable question.",
    ]
    return generated_page("maps/Profile Coverage", "Profile Coverage", "map", "\n".join(lines), updated)


def write_page(page: Page, wiki: Path, apply: bool) -> bool:
    path = wiki / (page.route + ".md")
    text = render_document(page.data, page.body)
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == text:
        return False
    if apply:
        atomic_write(path, text)
    return True


def sync(profile_path: Path, wiki: Path, apply: bool, bootstrap_profile: bool = False) -> dict[str, Any]:
    profile = load_json(profile_path)
    if profile.get("version") != 2:
        raise ValueError("visible wiki requires learner profile schema v2")
    wiki.mkdir(parents=True, exist_ok=True)
    pages = scan_pages(wiki)
    changed: list[str] = []
    if bootstrap_profile:
        changed.extend(bootstrap_profile_pages(profile, wiki, pages, apply))
    public_pages = [page for page in pages if is_public(page)]
    source_pages = source_page_map(public_pages)
    warnings: list[str] = []
    for page in public_pages:
        issue = None
        if page.data.get("type") == "concept":
            issue = update_concept_page(page, profile, source_pages)
        elif page.data.get("type") == "source":
            issue = update_source_page(page, profile)
        if issue:
            warnings.append(issue)
        elif page.data.get("type") in {"concept", "source"} and write_page(page, wiki, apply):
            changed.append(page.route)
    public_pages = [page for page in pages if is_public(page)]
    updated = str(profile.get("updated_at") or now_utc())[:10]
    generated = [
        build_home(public_pages, updated),
        build_index(public_pages, updated),
        build_boundary_map(public_pages, updated),
        build_topic_map(public_pages, updated),
        build_questions_map(public_pages, updated),
        build_evidence_map(public_pages, updated),
        build_profile_coverage_map(profile, public_pages, updated),
    ]
    for page in generated:
        if write_page(page, wiki, apply):
            changed.append(page.route)
    manifest = {
        "version": 1,
        "generated_at": now_utc(),
        "profile_version": profile.get("version"),
        "profile_updated_at": profile.get("updated_at"),
        "page_count": len(public_pages),
        "coverage": profile_coverage(profile, public_pages),
        "pages": [
            {
                "id": page.data.get("id"),
                "route": page.route,
                "type": page.data.get("type"),
                "knowledge_status": page.data.get("knowledge_status"),
                "source_refs": page.data.get("source_refs", []),
                "profile_source_refs": page.data.get("profile_source_refs", []),
            }
            for page in sorted(public_pages, key=lambda item: item.route)
        ],
        "warnings": warnings,
    }
    manifest_path = wiki / "_internal" / "projection_manifest.json"
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    if apply:
        atomic_write(manifest_path, manifest_text)
    return {
        "changed": sorted(set(changed)),
        "warnings": warnings,
        "manifest": manifest,
        "applied": apply,
        "bootstrap_profile": bootstrap_profile,
    }


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["sync"], help="Projection operation to run")
    parser.add_argument("--profile", required=True, help="Schema-v2 knowledge_profile.json")
    parser.add_argument("--wiki", required=True, help="Visible wiki root")
    parser.add_argument("--apply", action="store_true", help="Write changes; omit for a dry-run")
    parser.add_argument(
        "--bootstrap-profile",
        action="store_true",
        help="Create concise public pages for all stable profile concepts and source summaries",
    )
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] = sys.argv[1:]) -> int:
    args = parse_args(argv)
    result = sync(
        Path(args.profile).expanduser().resolve(),
        Path(args.wiki).expanduser().resolve(),
        args.apply,
        bootstrap_profile=args.bootstrap_profile,
    )
    print(json.dumps({
        "applied": result["applied"],
        "bootstrap_profile": result["bootstrap_profile"],
        "changed": result["changed"],
        "coverage": result["manifest"]["coverage"],
        "warnings": result["warnings"],
    }, ensure_ascii=False, indent=2))
    return 0 if not result["warnings"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
