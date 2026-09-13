#!/usr/bin/env python3
"""Validate a paper-wide style manifest and optionally emit normalized JSON."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from style_manifest import StyleManifestError, load_style_manifest, normalized_json, validate_style_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path, help="Path to style_manifest.yaml")
    parser.add_argument("--emit-json", type=Path, help="Write normalized JSON for backends that do not parse full YAML")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    args = parser.parse_args()

    try:
        manifest = load_style_manifest(args.manifest)
    except StyleManifestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    errors, warnings = validate_style_manifest(manifest)
    for item in errors:
        print(f"error: {item}")
    for item in warnings:
        print(f"warning: {item}")

    if not errors and args.emit_json:
        args.emit_json.parent.mkdir(parents=True, exist_ok=True)
        args.emit_json.write_text(normalized_json(manifest), encoding="utf-8")
        print(f"normalized_json={args.emit_json}")

    print(f"manifest={args.manifest} errors={len(errors)} warnings={len(warnings)}")
    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
