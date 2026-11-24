#!/usr/bin/env python3
"""Structurally inspect a figure-kit PPTX and update its manifest QA record."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any

from validate_figure_contract import load_contract, sha256_file, validate_contract

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}


def media_inventory(package: zipfile.ZipFile) -> list[dict[str, Any]]:
    records = []
    for name in package.namelist():
        if not name.startswith("ppt/media/") or name.endswith("/"):
            continue
        payload = package.read(name)
        records.append({"name": name, "extension": Path(name).suffix.lower(), "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)})
    return records


def presentation_size(package: zipfile.ZipFile) -> tuple[int, int]:
    root = ET.fromstring(package.read("ppt/presentation.xml"))
    node = root.find("p:sldSz", NS)
    if node is None:
        return 0, 0
    return int(node.attrib.get("cx", 0)), int(node.attrib.get("cy", 0))


def slide_records(package: zipfile.ZipFile, slide_size: tuple[int, int]) -> tuple[list[dict[str, Any]], list[str]]:
    slides: list[dict[str, Any]] = []
    out_of_bounds: list[str] = []
    slide_names = sorted(name for name in package.namelist() if name.startswith("ppt/slides/slide") and name.endswith(".xml"))
    max_x, max_y = slide_size
    for name in slide_names:
        root = ET.fromstring(package.read(name))
        shapes = root.findall(".//p:sp", NS)
        pictures = root.findall(".//p:pic", NS)
        text_nodes = root.findall(".//a:t", NS)
        object_count = 0
        for node in [*shapes, *pictures]:
            xfrm = node.find(".//a:xfrm", NS)
            if xfrm is None:
                continue
            offset = xfrm.find("a:off", NS)
            extent = xfrm.find("a:ext", NS)
            if offset is None or extent is None:
                continue
            object_count += 1
            x, y = int(offset.attrib.get("x", 0)), int(offset.attrib.get("y", 0))
            cx, cy = int(extent.attrib.get("cx", 0)), int(extent.attrib.get("cy", 0))
            if x < 0 or y < 0 or x + cx > max_x or y + cy > max_y:
                out_of_bounds.append(f"{name}: object at ({x},{y},{cx},{cy}) outside ({max_x},{max_y})")
        object_names = sorted(
            {
                node.attrib.get("name", "")
                for node in root.findall(".//p:cNvPr", NS)
                if node.attrib.get("name")
            }
        )
        slides.append({"name": name, "native_shape_count": len(shapes), "picture_count": len(pictures), "editable_text_runs": len(text_nodes), "positioned_objects_checked": object_count, "object_names": object_names})
    return slides, out_of_bounds


def notes_text(package: zipfile.ZipFile) -> str:
    text: list[str] = []
    for name in sorted(
        item
        for item in package.namelist()
        if item.startswith("ppt/notesSlides/notesSlide") and item.endswith(".xml")
    ):
        root = ET.fromstring(package.read(name))
        text.extend(node.text or "" for node in root.findall(".//a:t", NS))
    return "\n".join(text)


def append_unique(items: list[Any], additions: list[Any]) -> None:
    existing = {json.dumps(item, ensure_ascii=False, sort_keys=True) for item in items}
    for item in additions:
        key = json.dumps(item, ensure_ascii=False, sort_keys=True)
        if key not in existing:
            items.append(item)
            existing.add(key)


def normalized_text(value: str) -> str:
    return " ".join(value.split())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pptx", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--report", type=Path, help="Optional standalone QA JSON path")
    parser.add_argument("--scale-layout", type=Path, help="Optional plot-to-PPT layout contract")
    parser.add_argument("--figure-contract", type=Path, help="Optional academic-figure-contract/v1 record")
    parser.add_argument("--check-only", action="store_true", help="Do not update the manifest in place")
    parser.add_argument("--strict", action="store_true", help="Fail on unresolved structural issues")
    parser.add_argument(
        "--require-caption-delivery",
        action="store_true",
        help="Require caption.md, speaker notes, visible caption slides, and panel annotation mappings",
    )
    parser.add_argument(
        "--require-visual-grammar",
        action="store_true",
        help="Require the scale layout to declare font and legend/marker/direct-label policies",
    )
    args = parser.parse_args()

    if not args.pptx.exists() or not zipfile.is_zipfile(args.pptx):
        print(f"error: PPTX is missing or not a valid ZIP package: {args.pptx}")
        return 2
    manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    contract_path: Path | None = None
    contract: dict[str, Any] | None = None
    contract_report: dict[str, Any] | None = None
    contract_issues: list[str] = []
    contract_ppt: dict[str, Any] = {}
    if args.figure_contract:
        contract_path = args.figure_contract.resolve(strict=True)
        contract = load_contract(contract_path)
        validation_errors, _, contract_report = validate_contract(contract, contract_path)
        contract_issues.extend(validation_errors)
        contract_surfaces = contract.get("surfaces", {})
        if isinstance(contract_surfaces, dict) and isinstance(contract_surfaces.get("ppt"), dict):
            contract_ppt = contract_surfaces["ppt"]
        expected_hash = manifest.get("figure_contract_sha256")
        actual_hash = sha256_file(contract_path)
        if not expected_hash:
            contract_issues.append("figure contract hash is missing from manifest")
        elif expected_hash != actual_hash:
            contract_issues.append("figure contract hash differs from manifest")
        manifest_contract = manifest.get("figure_contract")
        if not isinstance(manifest_contract, str) or not manifest_contract.strip():
            contract_issues.append("figure contract path is missing from manifest")
        else:
            declared_contract_path = (args.manifest.parent / manifest_contract).resolve(strict=False)
            if declared_contract_path != contract_path:
                contract_issues.append("manifest figure contract path differs from --figure-contract")

    with zipfile.ZipFile(args.pptx) as package:
        media = media_inventory(package)
        slide_size = presentation_size(package)
        slides, out_of_bounds = slide_records(package, slide_size)
        notes_slide_count = sum(
            name.startswith("ppt/notesSlides/notesSlide") and name.endswith(".xml")
            for name in package.namelist()
        )
        combined_notes_text = notes_text(package)

    media_hashes = {item["sha256"] for item in media}
    missing_vector_assets = [
        asset["id"] for asset in manifest.get("assets", [])
        if asset.get("editability") == "B" and asset.get("sha256") not in media_hashes
    ]
    unexpected_svg_types = [
        asset["id"] for asset in manifest.get("assets", [])
        if asset.get("editability") == "B" and asset.get("content_type") != "image/svg+xml"
    ]
    declared_size = manifest.get("slide_size", {})
    expected_emu = {
        "width": int(float(declared_size.get("width", 0)) * 9525),
        "height": int(float(declared_size.get("height", 0)) * 9525),
    }
    qa = {
        "pptx_opens_as_zip": True,
        "slide_size_emu": {"width": slide_size[0], "height": slide_size[1]},
        "slide_size_matches_manifest": slide_size == (expected_emu["width"], expected_emu["height"]),
        "slides": slides,
        "media": media,
        "svg_media_count": sum(item["extension"] == ".svg" for item in media),
        "raster_media_count": sum(item["extension"] in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"} for item in media),
        "declared_raster_object_count": manifest.get("editability", {}).get("raster_objects", 0),
        "missing_vector_asset_hashes": missing_vector_assets,
        "unexpected_vector_content_types": unexpected_svg_types,
        "out_of_bounds": out_of_bounds,
        "native_text_present": any(slide["editable_text_runs"] > 0 for slide in slides),
        "independent_object_count": sum(slide["native_shape_count"] + slide["picture_count"] for slide in slides),
        "notes_slide_count": notes_slide_count,
        "manual_preview_checks_required": ["unexpected overlap", "clipped text", "font substitution", "aspect-ratio appearance", "semantic-colour match"],
    }
    scale_issue_count = 0
    if args.scale_layout:
        scale_script = Path(__file__).with_name("qa_plot_ppt_scale.py")
        scale_command = [
            sys.executable,
            str(scale_script),
            "--layout",
            str(args.scale_layout),
            "--strict",
        ]
        if args.require_visual_grammar:
            scale_command.append("--require-visual-grammar")
        if args.figure_contract:
            scale_command.extend(["--figure-contract", str(args.figure_contract)])
        completed = subprocess.run(
            scale_command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        try:
            qa["plot_to_ppt_scale"] = json.loads(completed.stdout)
        except json.JSONDecodeError:
            qa["plot_to_ppt_scale"] = {"status": "fail", "issues": [completed.stderr or completed.stdout]}
        scale_issue_count = 0 if completed.returncode == 0 else 1
    caption_issues: list[str] = []
    caption_delivery = manifest.get("caption_delivery", {})
    caption_delivery_required = args.require_caption_delivery or contract_ppt.get("required") is True
    visible_delivery_required = (
        args.require_caption_delivery
        or contract_ppt.get("visible_explanations_required") is True
    )
    if caption_delivery_required:
        caption_path_value = caption_delivery.get("caption_md")
        caption_path = (
            (args.manifest.parent / caption_path_value).resolve()
            if isinstance(caption_path_value, str) and caption_path_value.strip()
            else None
        )
        if caption_path is None or not caption_path.exists():
            caption_issues.append("caption delivery: caption_md is missing or unresolved")
        else:
            actual_caption_hash = sha256_file(caption_path)
            declared_caption_hash = caption_delivery.get("caption_sha256")
            declared_notes_hash = caption_delivery.get("speaker_notes_caption_sha256")
            if declared_caption_hash and declared_caption_hash != actual_caption_hash:
                caption_issues.append("caption delivery: caption.md hash differs from manifest")
            if declared_caption_hash and declared_notes_hash and declared_caption_hash != declared_notes_hash:
                caption_issues.append("caption delivery: caption and notes hashes differ")
            caption_text = caption_path.read_text(encoding="utf-8-sig").strip()
            if caption_text and normalized_text(caption_text) not in normalized_text(combined_notes_text):
                caption_issues.append("caption delivery: caption.md text is not present in speaker notes")
        if caption_delivery.get("speaker_notes") is not True or notes_slide_count < 1:
            caption_issues.append("caption delivery: speaker notes are not declared and present")
    if visible_delivery_required:
        visible_slides = caption_delivery.get("visible_caption_slides", [])
        if not isinstance(visible_slides, list) or not visible_slides:
            caption_issues.append("caption delivery: visible_caption_slides is empty")
        elif any(not isinstance(item, int) or item < 1 or item > len(slides) for item in visible_slides):
            caption_issues.append("caption delivery: visible caption slide index is invalid")
        annotation_map = caption_delivery.get("panel_annotation_map", {})
        if not isinstance(annotation_map, dict) or not annotation_map:
            caption_issues.append("caption delivery: panel_annotation_map is empty")
        elif any(not str(panel).strip() or not str(object_id).strip() for panel, object_id in annotation_map.items()):
            caption_issues.append("caption delivery: panel annotation mapping contains a blank key or object id")
        if not qa["native_text_present"]:
            caption_issues.append("caption delivery: no native editable text was detected")
    if contract is not None:
        all_object_names = {
            object_name for slide in slides for object_name in slide.get("object_names", [])
        }
        manifest_ids_by_kind: dict[str, set[str]] = {}
        for slide in manifest.get("slides", []):
            kind = str(slide.get("kind", "figure_assembly"))
            manifest_ids_by_kind.setdefault(kind, set()).update(
                str(item.get("id"))
                for item in slide.get("objects", [])
                if isinstance(item, dict) and item.get("id")
            )
        surfaces = contract.get("surfaces", {})
        ppt = surfaces.get("ppt", {}) if isinstance(surfaces.get("ppt", {}), dict) else {}
        for binding in surfaces.get("bindings", []):
            element_id = binding.get("element_id", "<unknown>")
            for field in ("ppt_main", "component_board", "visible_explanation"):
                object_id = binding.get(field)
                required = field == "ppt_main" and ppt.get("required") is True
                required = required or (
                    field in {"component_board", "visible_explanation"}
                    and ppt.get("visible_explanations_required") is True
                )
                if required:
                    allowed_kinds = {
                        "ppt_main": {"figure_assembly"},
                        "component_board": {"component_board"},
                        "visible_explanation": {"caption_interpretation", "component_board"},
                    }[field]
                    declared_ids = set().union(
                        *(manifest_ids_by_kind.get(kind, set()) for kind in allowed_kinds)
                    )
                    if object_id not in declared_ids:
                        contract_issues.append(
                            f"contract element {element_id}: {object_id!r} is not declared on the required {field} surface"
                        )
                    if object_id not in all_object_names:
                        contract_issues.append(
                            f"contract element {element_id}: PPT object {object_id!r} for {field} was not found"
                        )
        qa["figure_contract"] = contract_report
    qa["caption_delivery_required"] = caption_delivery_required
    qa["visible_caption_delivery_required"] = visible_delivery_required
    qa["caption_delivery"] = caption_delivery
    qa["caption_delivery_issues"] = caption_issues
    qa["figure_contract_issues"] = contract_issues
    if qa["svg_media_count"] and qa["raster_media_count"] and qa["declared_raster_object_count"] == 0:
        qa["raster_media_note"] = "The PPTX backend stores PNG compatibility previews beside SVG media; these are not declared Level C objects while the matching SVG hashes remain present."
    manifest["structural_qa"] = qa
    if missing_vector_assets:
        append_unique(
            manifest.setdefault("raster_fallbacks", []),
            [{"object_id": item, "reason": "source SVG hash not found in PPT media"} for item in missing_vector_assets],
        )
    append_unique(
        manifest.setdefault("unresolved_issues", []),
        [f"PPT object outside slide: {item}" for item in out_of_bounds],
    )
    if not args.check_only:
        args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    issue_count = len(missing_vector_assets) + len(unexpected_svg_types) + len(out_of_bounds) + len(caption_issues) + len(contract_issues) + (0 if qa["slide_size_matches_manifest"] else 1) + scale_issue_count
    print(f"pptx={args.pptx} slides={len(slides)} svg_media={qa['svg_media_count']} raster_media={qa['raster_media_count']} issues={issue_count}")
    return 1 if args.strict and issue_count else 0


if __name__ == "__main__":
    sys.exit(main())
