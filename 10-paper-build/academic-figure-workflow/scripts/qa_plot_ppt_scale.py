"""Validate shared plot-to-PPT geometry and final-size readability metrics."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layout", type=Path, required=True, help="Shared plot/PPT layout JSON")
    parser.add_argument(
        "--report",
        type=Path,
        help="Optional JSON report path; defaults to stdout only",
    )
    parser.add_argument("--strict", action="store_true", help="Return non-zero when any issue is found")
    parser.add_argument(
        "--require-visual-grammar",
        action="store_true",
        help="Require a declared font family and legend/marker/direct-label visual grammar",
    )
    return parser.parse_args()


def svg_viewbox(path: Path) -> tuple[float, float]:
    head = path.read_text(encoding="utf-8")[:4096]
    match = re.search(rf'viewBox="\s*({NUMBER})\s+({NUMBER})\s+({NUMBER})\s+({NUMBER})\s*"', head)
    if not match:
        raise ValueError(f"SVG lacks a numeric viewBox: {path}")
    width = float(match.group(3))
    height = float(match.group(4))
    if width <= 0 or height <= 0:
        raise ValueError(f"SVG viewBox is not positive: {path}")
    return width, height


def main() -> int:
    args = parse_args()
    layout_path = args.layout.resolve()
    layout = json.loads(layout_path.read_text(encoding="utf-8"))
    slide = layout["slide_px"]
    target_width_mm = float(layout["target_publication_width_mm"])
    qa = layout["qa_thresholds"]
    tolerance = float(qa.get("aspect_anisotropy_max", 0.01))
    minimum_text = float(qa.get("minimum_final_text_pt", 6.5))
    minimum_context_stroke = float(qa.get("minimum_context_stroke_pt", 0.55))
    minimum_primary_stroke = float(qa.get("minimum_primary_stroke_pt", 1.0))
    axes_aspect_min = float(qa.get("axes_aspect_min", 0.95))
    axes_aspect_max = float(qa.get("axes_aspect_max", 1.30))
    peer_axes_difference_max = float(
        qa.get("peer_axes_aspect_relative_difference_max", 0.10)
    )
    issues: list[str] = []
    panels: dict[str, dict] = {}
    typography_contract = layout.get("typography_final_pt", {})
    visual_grammar = layout.get("visual_grammar", {})
    required_visual_keys = {
        "line_policy",
        "marker_policy",
        "legend_policy",
        "direct_label_policy",
    }
    if args.require_visual_grammar:
        if not str(typography_contract.get("family", "")).strip():
            issues.append("visual grammar: typography_final_pt.family is missing")
        missing_visual_keys = sorted(required_visual_keys - set(visual_grammar))
        if missing_visual_keys:
            issues.append(
                "visual grammar: missing " + ", ".join(missing_visual_keys)
            )

    for panel_id, panel in layout["panels"].items():
        asset = (layout_path.parent / panel["asset"]).resolve()
        if not asset.exists():
            issues.append(f"panel {panel_id}: missing asset {asset}")
            continue
        view_width, view_height = svg_viewbox(asset)
        slot = panel["slot_px"]
        scale_x = float(slot["width"]) / view_width
        scale_y = float(slot["height"]) / view_height
        anisotropy = max(scale_x / scale_y, scale_y / scale_x) - 1.0
        final_width_mm = target_width_mm * float(slot["width"]) / float(slide["width"])
        final_height_mm = target_width_mm * float(slot["height"]) / float(slide["width"])
        canvas = panel["source_canvas_mm"]
        canvas_error = max(
            abs(float(canvas["width"]) - final_width_mm) / final_width_mm,
            abs(float(canvas["height"]) - final_height_mm) / final_height_mm,
        )
        metrics = panel["final_metrics_pt"]
        subplot = panel.get("subplot")
        axes_aspect_exempt = panel.get("axes_aspect_exempt")
        axes_width_mm = None
        axes_height_mm = None
        axes_aspect = None
        if subplot:
            axes_width_mm = float(canvas["width"]) * (
                float(subplot["right"]) - float(subplot["left"])
            )
            axes_height_mm = float(canvas["height"]) * (
                float(subplot["top"]) - float(subplot["bottom"])
            )
            if axes_width_mm <= 0 or axes_height_mm <= 0:
                issues.append(f"panel {panel_id}: main data-axes geometry is not positive")
            else:
                axes_aspect = axes_width_mm / axes_height_mm
                if not axes_aspect_exempt and not axes_aspect_min <= axes_aspect <= axes_aspect_max:
                    issues.append(
                        f"panel {panel_id}: main axes aspect {axes_aspect:.4f} is outside "
                        f"{axes_aspect_min:.2f}-{axes_aspect_max:.2f}"
                    )
        elif not axes_aspect_exempt:
            issues.append(f"panel {panel_id}: missing subplot geometry for axes-aspect QA")
        minimum_panel_text = min(float(value) for value in metrics["text"].values())
        context_stroke = float(metrics["strokes"]["context"])
        primary_stroke = float(metrics["strokes"]["primary"])
        if anisotropy > tolerance:
            issues.append(
                f"panel {panel_id}: SVG/PPT anisotropy {anisotropy:.4f} exceeds {tolerance:.4f}"
            )
        if canvas_error > tolerance:
            issues.append(
                f"panel {panel_id}: source canvas differs from final slot by {canvas_error:.4f}"
            )
        if minimum_panel_text < minimum_text:
            issues.append(
                f"panel {panel_id}: minimum final text {minimum_panel_text:.2f} pt is below {minimum_text:.2f} pt"
            )
        if context_stroke < minimum_context_stroke:
            issues.append(
                f"panel {panel_id}: context stroke {context_stroke:.2f} pt is below {minimum_context_stroke:.2f} pt"
            )
        if primary_stroke < minimum_primary_stroke:
            issues.append(
                f"panel {panel_id}: primary stroke {primary_stroke:.2f} pt is below {minimum_primary_stroke:.2f} pt"
            )
        panels[panel_id] = {
            "asset": str(asset),
            "svg_viewbox": [view_width, view_height],
            "slot_px": slot,
            "scale_x": scale_x,
            "scale_y": scale_y,
            "anisotropy": anisotropy,
            "final_size_mm": [final_width_mm, final_height_mm],
            "source_canvas_mm": canvas,
            "canvas_error": canvas_error,
            "axes_size_mm": [axes_width_mm, axes_height_mm],
            "axes_aspect": axes_aspect,
            "axes_aspect_exempt": axes_aspect_exempt,
            "colorbar": panel.get("colorbar"),
            "minimum_final_text_pt": minimum_panel_text,
            "context_stroke_pt": context_stroke,
            "primary_stroke_pt": primary_stroke,
        }

    peer_aspects = [
        float(panel["axes_aspect"])
        for panel in panels.values()
        if panel.get("axes_aspect") is not None and not panel.get("axes_aspect_exempt")
    ]
    peer_axes_difference = None
    if len(peer_aspects) >= 2:
        peer_axes_difference = max(peer_aspects) / min(peer_aspects) - 1.0
        if peer_axes_difference > peer_axes_difference_max:
            issues.append(
                "peer panels: relative axes-aspect difference "
                f"{peer_axes_difference:.4f} exceeds {peer_axes_difference_max:.4f}"
            )

    report = {
        "layout": str(layout_path),
        "status": "pass" if not issues else "fail",
        "panels": panels,
        "peer_axes_aspect_relative_difference": peer_axes_difference,
        "typography_contract": typography_contract,
        "visual_grammar": visual_grammar,
        "visual_grammar_required": args.require_visual_grammar,
        "issues": issues,
    }
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 1 if args.strict and issues else 0


if __name__ == "__main__":
    sys.exit(main())
