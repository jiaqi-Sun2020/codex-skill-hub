#!/usr/bin/env python3
"""Validate the public Knowledge Layer without reading or mutating raw source records."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

from compile_visible_wiki import (
    PUBLIC_TYPES,
    RELATION_TYPES,
    VALID_STATUSES,
    is_public,
    is_stable_profile_concept,
    load_json,
    profile_concept_id_for_page,
    scan_pages,
)


LOCAL_PATH_RE = re.compile(r"(?:[A-Za-z]:[\\/]|\\\\)")
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")
REQUIRED_ROUTES = {
    "Home",
    "index",
    "maps/Knowledge Boundary",
    "maps/Topic Map",
    "maps/Open Questions",
    "maps/Evidence Map",
    "maps/Profile Coverage",
}


def issue(level: str, path: str, message: str) -> dict[str, str]:
    return {"level": level, "path": path, "message": message}


def lint(profile_path: Path, wiki: Path, require_profile_coverage: bool = False) -> list[dict[str, str]]:
    profile = load_json(profile_path)
    pages = scan_pages(wiki)
    findings: list[dict[str, str]] = []
    routes = {page.route: page for page in pages}
    ids: dict[str, str] = {}
    profile_source_ids = set((profile.get("sources") or {}).keys())
    concepts = profile.get("concepts") or {}
    for route in REQUIRED_ROUTES:
        if route not in routes:
            findings.append(issue("error", route, "required generated page is missing"))
    for page in pages:
        public = is_public(page)
        page_id = str(page.data.get("id") or "")
        if not page_id:
            findings.append(issue("error", page.route, "missing stable id"))
            continue
        if page_id in ids:
            findings.append(issue("error", page.route, f"duplicate id also used by {ids[page_id]}"))
        ids[page_id] = page.route
        if not public:
            continue
        page_type = page.data.get("type")
        if page_type not in PUBLIC_TYPES:
            findings.append(issue("error", page.route, f"invalid public type: {page_type!r}"))
        if LOCAL_PATH_RE.search(page.path.read_text(encoding="utf-8")):
            findings.append(issue("error", page.route, "public page contains an absolute local path"))
        profile_source_refs = page.data.get("profile_source_refs", []) or []
        if not isinstance(profile_source_refs, list):
            findings.append(issue("error", page.route, "profile_source_refs must be a JSON-style list"))
        else:
            for source_id in profile_source_refs:
                if source_id not in profile_source_ids:
                    findings.append(issue("error", page.route, f"unknown profile source: {source_id}"))
        relations = page.data.get("relations", []) or []
        if not isinstance(relations, list):
            findings.append(issue("error", page.route, "relations must be a JSON-style list"))
        for relation in relations if isinstance(relations, list) else []:
            if not isinstance(relation, dict):
                findings.append(issue("error", page.route, "relation is not an object"))
                continue
            if relation.get("type") not in RELATION_TYPES:
                findings.append(issue("error", page.route, f"invalid relation type: {relation.get('type')!r}"))
            if not relation.get("target"):
                findings.append(issue("error", page.route, "relation has no target id"))
        if page_type == "concept":
            concept_id = profile_concept_id_for_page(page)
            if concept_id.startswith(("freeform-annotation-", "concept-")):
                findings.append(issue("error", page.route, "raw annotation or opaque candidate is not a stable concept page"))
            profile_concept = concepts.get(concept_id)
            if not isinstance(profile_concept, dict):
                findings.append(issue("error", page.route, f"profile concept is missing: {concept_id}"))
            else:
                expected = profile_concept.get("status", "unrated")
                actual = page.data.get("knowledge_status")
                if actual not in VALID_STATUSES:
                    findings.append(issue("error", page.route, f"invalid knowledge_status: {actual!r}"))
                elif actual != expected:
                    findings.append(issue("error", page.route, f"knowledge_status {actual!r} differs from profile {expected!r}"))
    id_set = set(ids)
    route_set = set(routes)
    outgoing_routes: dict[str, set[str]] = {route: set() for route in routes}
    incoming_routes: dict[str, set[str]] = {route: set() for route in routes}
    for page in pages:
        for target in WIKILINK_RE.findall(page.body):
            target = target.strip().replace("\\", "/")
            if target not in route_set:
                findings.append(issue("error", page.route, f"broken wiki link: {target}"))
            else:
                outgoing_routes[page.route].add(target)
                incoming_routes[target].add(page.route)
        if not is_public(page):
            continue
        source_refs = page.data.get("source_refs", []) or []
        if not isinstance(source_refs, list):
            findings.append(issue("error", page.route, "source_refs must be a JSON-style list"))
        else:
            for source_id in source_refs:
                if source_id not in id_set:
                    findings.append(issue("error", page.route, f"source summary does not exist: {source_id}"))
                elif routes[ids[source_id]].data.get("type") != "source":
                    findings.append(issue("error", page.route, f"source_refs target is not a source page: {source_id}"))
        for relation in page.data.get("relations", []) or []:
            if isinstance(relation, dict) and relation.get("target") not in id_set:
                findings.append(issue("error", page.route, f"relation target does not exist: {relation.get('target')}"))
    for page in pages:
        if is_public(page) and not outgoing_routes[page.route] and not incoming_routes[page.route]:
            findings.append(issue("error", page.route, "public page is isolated from the wiki link graph"))
    if require_profile_coverage:
        stable_concepts = {
            concept_id
            for concept_id in concepts
            if isinstance(concept_id, str) and is_stable_profile_concept(concept_id)
        }
        concept_pages: dict[str, list[str]] = {}
        source_pages: dict[str, list[str]] = {}
        for page in pages:
            if not is_public(page):
                continue
            if page.data.get("type") == "concept":
                concept_pages.setdefault(profile_concept_id_for_page(page), []).append(page.route)
            elif page.data.get("type") == "source":
                for source_id in page.data.get("profile_source_refs", []) or []:
                    if isinstance(source_id, str):
                        source_pages.setdefault(source_id, []).append(page.route)
        for concept_id in sorted(stable_concepts):
            routes_for_concept = concept_pages.get(concept_id, [])
            if not routes_for_concept:
                findings.append(issue("error", "concepts", f"stable profile concept is not projected: {concept_id}"))
            elif len(routes_for_concept) > 1:
                findings.append(issue("error", "concepts", f"stable profile concept has duplicate public pages: {concept_id}"))
        for source_id in sorted(profile_source_ids):
            routes_for_source = source_pages.get(source_id, [])
            if not routes_for_source:
                findings.append(issue("error", "sources", f"profile source is not projected: {source_id}"))
            elif len(routes_for_source) > 1:
                findings.append(issue("error", "sources", f"profile source has duplicate public summaries: {source_id}"))
    return findings


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--wiki", required=True)
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    parser.add_argument(
        "--require-profile-coverage",
        action="store_true",
        help="Require every stable profile concept and source to have exactly one public projection",
    )
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] = sys.argv[1:]) -> int:
    args = parse_args(argv)
    findings = lint(
        Path(args.profile).expanduser().resolve(),
        Path(args.wiki).expanduser().resolve(),
        require_profile_coverage=args.require_profile_coverage,
    )
    errors = [item for item in findings if item["level"] == "error"]
    print(json.dumps({"status": "pass" if not findings else "fail", "errors": len(errors), "findings": findings}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
