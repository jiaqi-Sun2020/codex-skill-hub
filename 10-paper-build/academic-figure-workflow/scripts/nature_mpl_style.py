"""Shared Matplotlib defaults for Nature-grade academic figures.

Import this helper from project-specific plotting scripts instead of rewriting
rcParams, palette choices, panel labels, and export settings each time.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from style_manifest import load_style_manifest, nested

MM_PER_INCH = 25.4
SINGLE_COLUMN_MM = 89
DOUBLE_COLUMN_MM = 183
MAX_HEIGHT_MM = 170

CJK_SANS_FONTS = [
    "Noto Sans CJK SC",
    "Source Han Sans SC",
    "Microsoft YaHei",
    "SimHei",
    "Arial Unicode MS",
]

CJK_SERIF_FONTS = [
    "Noto Serif CJK SC",
    "Source Han Serif SC",
    "SimSun",
    "STSong",
]

WONG_PALETTE = {
    "black": "#000000",
    "orange": "#E69F00",
    "sky_blue": "#56B4E9",
    "bluish_green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermillion": "#D55E00",
    "reddish_purple": "#CC79A7",
    "grey": "#7A7A7A",
}

DEFAULT_ROLE_COLOURS = {
    "control": WONG_PALETTE["black"],
    "treatment": WONG_PALETTE["blue"],
    "comparison": WONG_PALETTE["orange"],
    "model": WONG_PALETTE["bluish_green"],
    "uncertainty": WONG_PALETTE["grey"],
    "negative": WONG_PALETTE["vermillion"],
    "positive": WONG_PALETTE["bluish_green"],
    "highlight": WONG_PALETTE["reddish_purple"],
}

_ACTIVE_MANIFEST: dict[str, Any] | None = None


def mm_to_inches(width_mm: float, height_mm: float) -> tuple[float, float]:
    return width_mm / MM_PER_INCH, height_mm / MM_PER_INCH


def nature_rcparams(manifest: dict[str, Any] | None = None) -> dict:
    hierarchy = nested(manifest, "typography", "hierarchy_pt", default={}) or {}
    strokes = nested(manifest, "strokes", default={}) or {}
    ticks = nested(manifest, "ticks", default={}) or {}
    charts = nested(manifest, "charts", default={}) or {}
    markers = nested(manifest, "markers", default={}) or {}
    legend = nested(manifest, "legend", default={}) or {}
    grid = nested(manifest, "grid", default={}) or {}
    backgrounds = nested(manifest, "backgrounds", default={}) or {}
    family = nested(manifest, "typography", "family", default={}) or {}
    sans_family = family.get("sans", "Arial")
    return {
        "figure.dpi": 300,
        "savefig.dpi": 450,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        "savefig.transparent": False,
        "font.family": "sans-serif",
        "font.sans-serif": [sans_family, "Arial", "Helvetica", "DejaVu Sans"],
        "font.size": hierarchy.get("body", 6),
        "axes.labelsize": hierarchy.get("axis_label", 6),
        "axes.titlesize": hierarchy.get("title", 6),
        "xtick.labelsize": hierarchy.get("tick", 5),
        "ytick.labelsize": hierarchy.get("tick", 5),
        "legend.fontsize": hierarchy.get("legend", 5),
        "axes.linewidth": strokes.get("axis_pt", 0.5),
        "xtick.major.width": ticks.get("major_width_pt", 0.5),
        "ytick.major.width": ticks.get("major_width_pt", 0.5),
        "xtick.major.size": ticks.get("major_length_pt", 2.5),
        "ytick.major.size": ticks.get("major_length_pt", 2.5),
        "lines.linewidth": charts.get("line_width_pt", strokes.get("line_pt", 1.0)),
        "lines.markersize": markers.get("size_pt", 3.0),
        "patch.linewidth": strokes.get("module_pt", 0.5),
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "axes.unicode_minus": False,
        "axes.grid": bool(grid.get("enabled", False)),
        "legend.frameon": bool(legend.get("frame", False)),
        "figure.facecolor": backgrounds.get("figure", "#FFFFFF"),
        "axes.facecolor": backgrounds.get("panel", "#FFFFFF"),
    }


def available_font_names() -> set[str]:
    try:
        from matplotlib import font_manager  # type: ignore
    except ImportError:
        return set()
    return {font.name for font in font_manager.fontManager.ttflist}


def select_cjk_font(serif: bool = False) -> str | None:
    candidates = CJK_SERIF_FONTS if serif else CJK_SANS_FONTS
    available = available_font_names()
    for font in candidates:
        if font in available:
            return font
    return None


def apply_nature_style(
    matplotlib_module,
    lang: str = "en",
    cjk_serif: bool = False,
    style_manifest_path: str | Path | None = None,
) -> dict[str, str]:
    """Apply publication defaults and return style diagnostics."""
    global _ACTIVE_MANIFEST
    _ACTIVE_MANIFEST = load_style_manifest(style_manifest_path) if style_manifest_path else None
    matplotlib_module.rcParams.update(nature_rcparams(_ACTIVE_MANIFEST))
    diagnostics: dict[str, str] = {}
    if style_manifest_path:
        diagnostics["style_manifest"] = str(Path(style_manifest_path).resolve())
        diagnostics["style_state"] = str(nested(_ACTIVE_MANIFEST, "state", "status", default="unknown"))
    if lang.lower().startswith(("zh", "cn")):
        cjk_font = select_cjk_font(serif=cjk_serif)
        if cjk_font:
            base_fonts = [cjk_font, "Arial", "Helvetica", "DejaVu Sans"]
            matplotlib_module.rcParams["font.sans-serif"] = base_fonts
            matplotlib_module.rcParams["font.family"] = "serif" if cjk_serif else "sans-serif"
            if cjk_serif:
                matplotlib_module.rcParams["font.serif"] = [cjk_font, "Times New Roman", "DejaVu Serif"]
            diagnostics["cjk_font"] = cjk_font
        else:
            diagnostics["cjk_font_warning"] = (
                "No CJK font found. Install Noto Sans CJK SC, Source Han Sans SC, "
                "Microsoft YaHei, SimHei, or SimSun before final Chinese figure export."
            )
    return diagnostics


def figure_size(column: str = "single", height_mm: float | None = None) -> tuple[float, float]:
    width_mm = DOUBLE_COLUMN_MM if column == "double" else SINGLE_COLUMN_MM
    if height_mm is None:
        height_mm = width_mm * 0.62
    height_mm = min(height_mm, MAX_HEIGHT_MM)
    return mm_to_inches(width_mm, height_mm)


def style_axes(ax) -> None:
    axes = nested(_ACTIVE_MANIFEST, "axes", default={}) or {}
    grid = nested(_ACTIVE_MANIFEST, "grid", default={}) or {}
    ax.spines["top"].set_visible(bool(axes.get("show_top", False)))
    ax.spines["right"].set_visible(bool(axes.get("show_right", False)))
    ax.tick_params(direction=axes.get("direction", "out"))
    if grid.get("enabled", False):
        ax.grid(
            True,
            axis=grid.get("axis", "y"),
            linestyle=grid.get("line_style", "solid"),
            alpha=float(grid.get("alpha", 0.3)),
            color=nested(_ACTIVE_MANIFEST, "neutral_colors", "grid", default="#D9D9D9"),
        )


def add_panel_label(ax, label: str, x: float = -0.18, y: float = 1.08) -> None:
    ax.text(
        x,
        y,
        label,
        transform=ax.transAxes,
        fontsize=nested(_ACTIVE_MANIFEST, "typography", "hierarchy_pt", "panel_label", default=8),
        fontweight=nested(_ACTIVE_MANIFEST, "typography", "panel_label_weight", default="bold"),
        va="top",
        ha="left",
    )


def role_colours() -> dict[str, str]:
    colours = dict(DEFAULT_ROLE_COLOURS)
    semantic = nested(_ACTIVE_MANIFEST, "semantic_colors", default={}) or {}
    colours.update({str(key): str(value) for key, value in semantic.items()})
    aliases = {
        "control": "baseline",
        "treatment": "proposed_method",
        "comparison": "baseline",
        "model": "proposed_method",
        "negative": "output",
        "positive": "proposed_method",
    }
    for alias, role in aliases.items():
        if role in semantic:
            colours[alias] = str(semantic[role])
    return colours


def role_colour(role: str) -> str:
    return role_colours().get(role, role_colours().get("proposed_method", WONG_PALETTE["blue"]))


def marker_for_index(index: int) -> str:
    family = nested(_ACTIVE_MANIFEST, "markers", "family", default=["o", "s", "^", "D"]) or ["o"]
    return str(family[index % len(family)])


def line_style_for_index(index: int) -> str:
    family = nested(_ACTIVE_MANIFEST, "charts", "line_styles", default=["solid", "dashed", "dotted", "dashdot"]) or ["solid"]
    return str(family[index % len(family)])


def chart_token(name: str, default: Any) -> Any:
    return nested(_ACTIVE_MANIFEST, "charts", name, default=default)


def neutral_colour(name: str, default: str) -> str:
    return str(nested(_ACTIVE_MANIFEST, "neutral_colors", name, default=default))


def legend_kwargs() -> dict[str, Any]:
    return {
        "loc": nested(_ACTIVE_MANIFEST, "legend", "location", default="best"),
        "ncols": int(nested(_ACTIVE_MANIFEST, "legend", "columns", default=1)),
        "frameon": bool(nested(_ACTIVE_MANIFEST, "legend", "frame", default=False)),
    }


def annotation_font_size() -> float:
    return float(nested(_ACTIVE_MANIFEST, "typography", "hierarchy_pt", "annotation", default=5))


def rendered_text_qa(fig) -> list[str]:
    """Return basic rendered-text QA issues for a Matplotlib figure."""
    issues: list[str] = []
    canvas = fig.canvas
    canvas.draw()
    renderer = canvas.get_renderer()
    figure_box = fig.bbox
    margin_px = 4
    text_items = []
    inactive_tick_labels = set()
    for ax in fig.axes:
        x_min, x_max = sorted(ax.get_xlim())
        y_min, y_max = sorted(ax.get_ylim())
        inactive_tick_labels.update(
            label for value, label in zip(ax.get_xticks(), ax.get_xticklabels())
            if value < x_min or value > x_max
        )
        inactive_tick_labels.update(
            label for value, label in zip(ax.get_yticks(), ax.get_yticklabels())
            if value < y_min or value > y_max
        )
    for text in fig.findobj():
        if not hasattr(text, "get_text") or not hasattr(text, "get_window_extent"):
            continue
        content = str(text.get_text() or "").strip()
        if not content or not text.get_visible():
            continue
        if text in inactive_tick_labels:
            continue
        try:
            box = text.get_window_extent(renderer=renderer)
        except Exception:
            continue
        if box.x1 < figure_box.x0 or box.y1 < figure_box.y0 or box.x0 > figure_box.x1 or box.y0 > figure_box.y1:
            # Matplotlib may keep off-axis auto-tick labels as visible artists even
            # though the axes clip them completely; they are not rendered text.
            continue
        text_items.append((content, box))
        if (
            box.x0 < figure_box.x0 - margin_px
            or box.y0 < figure_box.y0 - margin_px
            or box.x1 > figure_box.x1 + margin_px
            or box.y1 > figure_box.y1 + margin_px
        ):
            issues.append(f"text may be clipped: {content[:40]!r}")
        if "\u25a1" in content or "\ufffd" in content:
            issues.append(f"text contains replacement or box glyph: {content[:40]!r}")
    for index, (left_text, left_box) in enumerate(text_items):
        for right_text, right_box in text_items[index + 1 :]:
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
                issues.append(f"text overlap: {left_text[:24]!r} vs {right_text[:24]!r}")
                if len(issues) >= 30:
                    return issues
    return issues


def save_preview(fig, output_path: str | Path, dpi: int = 150) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi)
    return str(path)


def save_nature_figure(fig, output_stem: str | Path, png_dpi: int = 450, preview_dpi: int = 150) -> dict[str, str]:
    stem = Path(output_stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    paths = {
        "svg": str(stem.with_suffix(".svg")),
        "pdf": str(stem.with_suffix(".pdf")),
        "png": str(stem.with_suffix(".png")),
        "preview_png": str(stem.with_name(stem.name + "_preview").with_suffix(".png")),
    }
    fig.savefig(paths["svg"])
    fig.savefig(paths["pdf"])
    fig.savefig(paths["png"], dpi=png_dpi)
    fig.savefig(paths["preview_png"], dpi=preview_dpi)
    return paths
