#!/usr/bin/env python3
"""Generate editable Nature-style multi-panel Matplotlib figures from a panel spec.

Panel spec CSV/JSON fields:
panel,claim,data,plot_type,x,y,yerr,group,color_role,title,xlabel,ylabel,annotation,
x_unit,y_unit,metric_definition,error_source,expected_sample_size

Supported plot_type values: scatter, line, errorbar, bar, hist, image.
Tabular sources: CSV, TSV, JSON, Excel, Parquet, and structured NumPy arrays.
The script writes SVG, PDF, PNG, a QA JSON report, and a Markdown QA summary.
It is intentionally conservative: missing data or duplicate claims are reported
instead of being silently repaired.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import nature_mpl_style as nstyle


@dataclass
class PanelSpec:
    panel: str
    claim: str
    data: str
    plot_type: str
    x: str
    y: str
    yerr: str
    group: str
    color_role: str
    title: str
    xlabel: str
    ylabel: str
    annotation: str
    x_unit: str
    y_unit: str
    metric_definition: str
    error_source: str
    expected_sample_size: int | None

    @classmethod
    def from_row(cls, row: dict[str, Any], index: int) -> "PanelSpec":
        return cls(
            panel=str(row.get("panel") or chr(ord("a") + index)),
            claim=str(row.get("claim") or "").strip(),
            data=str(row.get("data") or "").strip(),
            plot_type=str(row.get("plot_type") or "scatter").strip().lower(),
            x=str(row.get("x") or "").strip(),
            y=str(row.get("y") or "").strip(),
            yerr=str(row.get("yerr") or "").strip(),
            group=str(row.get("group") or "").strip(),
            color_role=str(row.get("color_role") or "treatment").strip(),
            title=str(row.get("title") or "").strip(),
            xlabel=str(row.get("xlabel") or "").strip(),
            ylabel=str(row.get("ylabel") or "").strip(),
            annotation=str(row.get("annotation") or "").strip(),
            x_unit=str(row.get("x_unit") or "").strip(),
            y_unit=str(row.get("y_unit") or "").strip(),
            metric_definition=str(row.get("metric_definition") or "").strip(),
            error_source=str(row.get("error_source") or "").strip(),
            expected_sample_size=(int(row["expected_sample_size"]) if str(row.get("expected_sample_size") or "").strip() else None),
        )


def require_matplotlib():
    try:
        import matplotlib  # type: ignore
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt  # type: ignore
        import matplotlib.text as mtext  # type: ignore
    except ImportError as exc:
        raise SystemExit("Missing dependency: matplotlib. Ask the user before installing it.") from exc
    return matplotlib, plt, mtext


def load_panel_specs(path: Path) -> list[PanelSpec]:
    if not path.exists():
        raise SystemExit(f"Panel spec not found: {path}")
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        rows = payload.get("panels", payload) if isinstance(payload, dict) else payload
    else:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
    if not isinstance(rows, list) or not rows:
        raise SystemExit("Panel spec must contain at least one panel row.")
    return [PanelSpec.from_row(row, index) for index, row in enumerate(rows)]


def resolve_data_path(data_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else data_root / path


def read_data_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    suffix = path.suffix.lower()
    if suffix in {".csv", ".tsv"}:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            return list(csv.DictReader(handle, delimiter="\t" if suffix == ".tsv" else ","))
    if suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        rows = payload.get("records", payload) if isinstance(payload, dict) else payload
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise ValueError("JSON data must be a list of record objects or {'records': [...]}")
        return rows
    if suffix in {".xlsx", ".xls", ".parquet"}:
        try:
            import pandas as pd  # type: ignore
        except ImportError as exc:
            raise RuntimeError(f"{suffix} input requires pandas and its format engine; do not install without user approval") from exc
        try:
            frame = pd.read_parquet(path) if suffix == ".parquet" else pd.read_excel(path)
        except (ImportError, ValueError, OSError) as exc:
            raise RuntimeError(f"Cannot read {suffix} with the available pandas engine: {exc}") from exc
        return frame.where(frame.notna(), None).to_dict(orient="records")
    if suffix in {".npy", ".npz"}:
        try:
            import numpy as np  # type: ignore
        except ImportError as exc:
            raise RuntimeError("NumPy input requires numpy; do not install without user approval") from exc
        loaded = np.load(path, allow_pickle=False)
        array = loaded[loaded.files[0]] if suffix == ".npz" else loaded
        if not getattr(array.dtype, "names", None):
            raise ValueError("NumPy data must use a structured array with named fields")
        return [{name: row[name].item() for name in array.dtype.names} for row in array]
    raise ValueError(f"unsupported data format: {suffix}")


def floats(rows: list[dict[str, Any]], column: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        raw = row.get(column, "")
        try:
            values.append(float(raw))
        except (TypeError, ValueError):
            continue
    return values


def values(rows: list[dict[str, Any]], column: str) -> list[str]:
    return [str(row.get(column, "")) for row in rows]


def grouped_rows(rows: list[dict[str, Any]], group_column: str) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(row.get(group_column, "group"), []).append(row)
    return groups


def role_colour(role: str) -> str:
    return nstyle.role_colour(role)


def plot_panel(ax, panel: PanelSpec, data_root: Path, plt_module) -> tuple[list[str], dict[str, Any]]:
    issues: list[str] = []
    audit: dict[str, Any] = {"panel": panel.panel, "data": panel.data, "columns": [], "row_count": 0, "missing_values": {}, "groups": []}
    nstyle.style_axes(ax)
    nstyle.add_panel_label(ax, panel.panel)
    ax.set_title(panel.title or panel.claim[:48])

    if panel.plot_type == "image":
        if not panel.data:
            issues.append(f"{panel.panel}: image panel missing data path")
            ax.text(0.5, 0.5, "missing image", ha="center", va="center")
        else:
            image_path = resolve_data_path(data_root, panel.data)
            if not image_path.exists():
                issues.append(f"{panel.panel}: image not found: {image_path}")
                ax.text(0.5, 0.5, "image not found", ha="center", va="center")
            else:
                image = plt_module.imread(str(image_path))
                ax.imshow(image)
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_visible(False)
        return issues, audit

    if not panel.data:
        issues.append(f"{panel.panel}: data path missing")
        ax.text(0.5, 0.5, "missing data", ha="center", va="center")
        return issues, audit

    data_path = resolve_data_path(data_root, panel.data)
    try:
        rows = read_data_rows(data_path)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        issues.append(f"{panel.panel}: data file not found: {data_path}")
        if not isinstance(exc, FileNotFoundError):
            issues[-1] = f"{panel.panel}: cannot read data: {exc}"
        ax.text(0.5, 0.5, "data not found", ha="center", va="center")
        return issues, audit

    if not rows:
        issues.append(f"{panel.panel}: data file has no rows")
        return issues, audit

    audit["columns"] = sorted({str(column) for row in rows for column in row})
    audit["row_count"] = len(rows)
    audit["missing_values"] = {
        column: sum(row.get(column) is None or row.get(column) == "" for row in rows)
        for column in audit["columns"]
    }
    required_columns = [column for column in (panel.x, panel.y, panel.yerr, panel.group) if column]
    for column in required_columns:
        if column not in rows[0]:
            issues.append(f"{panel.panel}: missing column: {column}")
    if panel.expected_sample_size is not None and len(rows) != panel.expected_sample_size:
        issues.append(f"{panel.panel}: sample size {len(rows)} != expected {panel.expected_sample_size}")
    if not panel.metric_definition and panel.y:
        issues.append(f"{panel.panel}: metric definition missing for {panel.y}")
    if panel.yerr and not panel.error_source:
        issues.append(f"{panel.panel}: error/SD/CI source missing for {panel.yerr}")
    if any(column not in rows[0] for column in required_columns):
        ax.text(0.5, 0.5, "required column missing", ha="center", va="center")
        return issues, audit

    plot_type = panel.plot_type

    if panel.group and panel.group in audit["columns"]:
        groups = grouped_rows(rows, panel.group)
    else:
        groups = {"": rows}
    audit["groups"] = list(groups)

    requested_roles = [item.strip() for item in panel.color_role.replace("|", ",").split(",") if item.strip()]
    if len(groups) > 1 and len(requested_roles) not in {1, len(groups)}:
        issues.append(f"{panel.panel}: grouped plot needs one shared color_role or one role per group")

    for group_index, (group_name, group_rows) in enumerate(groups.items()):
        label = group_name or None
        selected_role = requested_roles[min(group_index, len(requested_roles) - 1)] if requested_roles else "treatment"
        colour = role_colour(selected_role)
        marker = nstyle.marker_for_index(group_index)
        line_style = nstyle.line_style_for_index(group_index)
        x_numeric: list[float] = []
        y_numeric: list[float] = []
        yerr_numeric: list[float] = []
        x_labels: list[str] = []
        skipped_rows = 0
        for row_index, row in enumerate(group_rows):
            try:
                x_value = float(row.get(panel.x, row_index)) if panel.x else float(row_index)
                y_value = float(row.get(panel.y, "")) if panel.y else math.nan
                error_value = float(row.get(panel.yerr, "")) if panel.yerr else math.nan
            except (TypeError, ValueError):
                skipped_rows += 1
                continue
            if plot_type == "hist":
                if math.isfinite(x_value):
                    x_numeric.append(x_value)
                else:
                    skipped_rows += 1
                continue
            if not math.isfinite(y_value):
                skipped_rows += 1
                continue
            x_numeric.append(x_value)
            y_numeric.append(y_value)
            x_labels.append(str(row.get(panel.x, row_index + 1)) if panel.x else str(row_index + 1))
            if panel.yerr:
                if not math.isfinite(error_value):
                    skipped_rows += 1
                    x_numeric.pop()
                    y_numeric.pop()
                    x_labels.pop()
                    continue
                yerr_numeric.append(error_value)
        if skipped_rows:
            issues.append(f"{panel.panel}: group {group_name or 'all'} skipped {skipped_rows} rows with missing/non-numeric plotted values")

        if plot_type == "scatter":
            ax.scatter(x_numeric, y_numeric, s=float(nstyle.chart_token("scatter_size_pt2", 12)), marker=marker, color=colour, label=label)
        elif plot_type == "line":
            ax.plot(x_numeric, y_numeric, marker=marker, linestyle=line_style, color=colour, label=label)
        elif plot_type == "errorbar":
            yerr = yerr_numeric if panel.yerr else None
            ax.errorbar(x_numeric, y_numeric, yerr=yerr, marker=marker, linestyle=line_style, color=colour, label=label, capsize=float(nstyle.chart_token("errorbar_capsize_pt", 2)))
        elif plot_type == "bar":
            base_positions = list(range(len(y_numeric)))
            width = 0.8 / max(1, len(groups))
            positions = [position + (group_index - (len(groups) - 1) / 2) * width for position in base_positions]
            edge = nstyle.neutral_colour("border", "#172B4D") if nstyle.chart_token("bar_edge", True) else "none"
            ax.bar(positions, y_numeric, width=width, color=colour, edgecolor=edge, label=label)
            ax.set_xticks(base_positions)
            ax.set_xticklabels(x_labels, rotation=35, ha="right")
        elif plot_type == "hist":
            ax.hist(x_numeric, bins="auto", color=colour, label=label, edgecolor="white", alpha=0.75)
        else:
            issues.append(f"{panel.panel}: unsupported plot_type={panel.plot_type}")
            ax.text(0.5, 0.5, f"unsupported: {panel.plot_type}", ha="center", va="center")

    if len(groups) > 1:
        ax.legend(**nstyle.legend_kwargs())
    if panel.xlabel:
        ax.set_xlabel(f"{panel.xlabel} ({panel.x_unit})" if panel.x_unit else panel.xlabel)
    elif plot_type != "hist":
        issues.append(f"{panel.panel}: missing x-axis label")
    if panel.ylabel:
        ax.set_ylabel(f"{panel.ylabel} ({panel.y_unit})" if panel.y_unit else panel.ylabel)
    elif plot_type not in {"hist", "image"}:
        issues.append(f"{panel.panel}: missing y-axis label")
    if panel.annotation:
        ax.text(0.98, 0.98, panel.annotation, transform=ax.transAxes, ha="right", va="top", fontsize=nstyle.annotation_font_size())
    audit["x_unit"] = panel.x_unit
    audit["y_unit"] = panel.y_unit
    audit["metric_definition"] = panel.metric_definition
    audit["error_source"] = panel.error_source
    return issues, audit


def duplicate_claims(panels: list[PanelSpec]) -> list[str]:
    seen: dict[str, str] = {}
    issues: list[str] = []
    for panel in panels:
        claim = " ".join(panel.claim.lower().split())
        if not claim:
            issues.append(f"{panel.panel}: missing non-redundant panel claim")
            continue
        if claim in seen:
            issues.append(f"{panel.panel}: duplicate claim also used by panel {seen[claim]}")
        seen[claim] = panel.panel
    return issues


def text_overlap_issues(fig, text_class) -> list[str]:
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    texts = [
        text
        for text in fig.findobj(match=text_class)
        if text.get_visible() and text.get_text().strip()
    ]
    boxes = []
    for text in texts:
        try:
            boxes.append((text.get_text(), text.get_window_extent(renderer=renderer)))
        except Exception:
            continue
    issues: list[str] = []
    for i, (left_text, left_box) in enumerate(boxes):
        for right_text, right_box in boxes[i + 1 :]:
            if left_text == right_text:
                continue
            if left_box.overlaps(right_box):
                x_overlap = max(0, min(left_box.x1, right_box.x1) - max(left_box.x0, right_box.x0))
                y_overlap = max(0, min(left_box.y1, right_box.y1) - max(left_box.y0, right_box.y0))
                overlap_area = x_overlap * y_overlap
                left_area = max(1, left_box.width * left_box.height)
                right_area = max(1, right_box.width * right_box.height)
                if overlap_area / min(left_area, right_area) < 0.2:
                    continue
                issues.append(f"text overlap: {left_text[:20]!r} vs {right_text[:20]!r}")
                if len(issues) >= 20:
                    return issues
    return issues


def inspect_svg(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "editable_text": False, "text_elements": 0}
    text = path.read_text(encoding="utf-8", errors="replace")
    return {
        "exists": True,
        "editable_text": "<text" in text,
        "text_elements": text.count("<text"),
        "path_elements": text.count("<path"),
    }


def write_report(report: dict[str, Any], output_stem: Path) -> tuple[Path, Path]:
    json_path = output_stem.with_name(output_stem.name + "_qa.json")
    md_path = output_stem.with_name(output_stem.name + "_qa.md")
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Nature Multi-Panel Figure QA",
        "",
        f"- Spec: `{report['spec']}`",
        f"- Outputs: {', '.join(report['outputs'].values())}",
        f"- Editable SVG text: {report['svg'].get('editable_text')}",
        f"- Issues: {len(report['issues'])}",
        "",
    ]
    if report["issues"]:
        lines.append("## Issues")
        lines.extend(f"- {issue}" for issue in report["issues"])
    else:
        lines.append("No blocking structural issues detected by the script.")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path, help="Panel spec CSV or JSON")
    parser.add_argument("--data-root", type=Path, default=Path("."), help="Base directory for relative data paths")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="nature_multipanel")
    parser.add_argument("--column", choices=["single", "double"], default="double")
    parser.add_argument("--height-mm", type=float)
    parser.add_argument("--lang", default="en", help="Figure text language hint, such as en or zh")
    parser.add_argument("--cjk-serif", action="store_true", help="Prefer serif CJK fonts for Chinese thesis/journal figures")
    parser.add_argument("--copy-script", action="store_true", help="Copy this generator next to outputs for provenance")
    parser.add_argument("--style-manifest", type=Path, help="Paper-wide style_manifest.yaml")
    args = parser.parse_args()

    matplotlib, plt, mtext = require_matplotlib()
    style_diagnostics = nstyle.apply_nature_style(
        matplotlib,
        lang=args.lang,
        cjk_serif=args.cjk_serif,
        style_manifest_path=args.style_manifest,
    )

    panels = load_panel_specs(args.spec)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_stem = args.output_dir / args.stem

    cols = min(2, max(1, math.ceil(math.sqrt(len(panels)))))
    rows = math.ceil(len(panels) / cols)
    width, height = nstyle.figure_size(args.column, args.height_mm)
    if args.height_mm is None and rows > 1:
        height = min(height * rows * 0.82, nstyle.MAX_HEIGHT_MM / nstyle.MM_PER_INCH)

    fig, axes = plt.subplots(rows, cols, figsize=(width, height), squeeze=False, constrained_layout=True)
    issues = duplicate_claims(panels)
    data_audit: list[dict[str, Any]] = []
    for index, panel in enumerate(panels):
        ax = axes[index // cols][index % cols]
        panel_issues, panel_audit = plot_panel(ax, panel, args.data_root, plt)
        issues.extend(panel_issues)
        data_audit.append(panel_audit)
    for index in range(len(panels), rows * cols):
        axes[index // cols][index % cols].axis("off")

    issues.extend(text_overlap_issues(fig, mtext.Text))
    issues.extend(nstyle.rendered_text_qa(fig))
    outputs = nstyle.save_nature_figure(fig, output_stem)
    plt.close(fig)

    svg_info = inspect_svg(Path(outputs["svg"]))
    if not svg_info.get("editable_text"):
        issues.append("SVG does not appear to contain editable <text> elements.")

    copied_script = ""
    if args.copy_script:
        copied = args.output_dir / Path(__file__).name
        shutil.copy2(__file__, copied)
        copied_script = str(copied)

    report = {
        "spec": str(args.spec),
        "data_root": str(args.data_root),
        "generator": str(Path(__file__)),
        "copied_generator": copied_script,
        "matplotlib_version": getattr(matplotlib, "__version__", ""),
        "style_diagnostics": style_diagnostics,
        "style_manifest": str(args.style_manifest.resolve()) if args.style_manifest else "",
        "data_audit": data_audit,
        "panel_count": len(panels),
        "figure_size_inches": [width, height],
        "outputs": outputs,
        "rendered_preview": outputs.get("preview_png", ""),
        "svg": svg_info,
        "issues": issues,
    }
    qa_json, qa_md = write_report(report, output_stem)
    print(f"outputs={outputs} qa_json={qa_json} qa_md={qa_md} issues={len(issues)}")
    blocking_terms = (
        "not found",
        "cannot read data",
        "missing data",
        "missing column",
        "sample size",
        "metric definition missing",
        "error/SD/CI source missing",
    )
    return 1 if any(any(term in issue for term in blocking_terms) for issue in issues) else 0


if __name__ == "__main__":
    sys.exit(main())
