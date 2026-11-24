#!/usr/bin/env python3
"""Create a modular LaTeX paper framework from an existing manuscript."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


ENCODINGS = ("utf-8-sig", "utf-8", "gb18030", "cp936")
FIGURE_EXTENSIONS = (".pdf", ".png", ".jpg", ".jpeg", ".eps")


@dataclass
class DocumentParts:
    preamble: str
    frontmatter: str
    sections_text: str
    backmatter: str


@dataclass
class SectionFile:
    title: str
    filename: str
    content: str


def read_text(path: Path) -> tuple[str, str]:
    for encoding in ENCODINGS:
        try:
            return path.read_text(encoding=encoding), encoding
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace"), "utf-8-replace"


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def write_text(path: Path, text: str, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"{path} exists; pass --force to overwrite it")
    path.parent.mkdir(parents=True, exist_ok=True)
    clean = normalize_newlines(text).strip() + "\n"
    path.write_text(clean, encoding="utf-8")


def split_document(text: str) -> DocumentParts:
    text = normalize_newlines(text)
    begin = re.search(r"\\begin\{document\}", text)
    if not begin:
        raise ValueError("Could not find \\begin{document}")

    end = re.search(r"\\end\{document\}", text)
    preamble = text[: begin.start()].strip()
    document_body = text[begin.end() : end.start() if end else len(text)]

    maketitle = re.search(r"\\maketitle\b", document_body)
    if maketitle:
        frontmatter = document_body[: maketitle.end()].strip()
        body = document_body[maketitle.end() :].strip()
    else:
        frontmatter = ""
        body = document_body.strip()

    backmatter_start = None
    for pattern in (
        r"(?m)^\s*\\bibliographystyle\b",
        r"(?m)^\s*\\bibliography\b",
        r"(?m)^\s*\\printbibliography\b",
    ):
        match = re.search(pattern, body)
        if match and (backmatter_start is None or match.start() < backmatter_start):
            backmatter_start = match.start()

    if backmatter_start is None:
        sections_text = body.strip()
        backmatter = ""
    else:
        sections_text = body[:backmatter_start].strip()
        backmatter = body[backmatter_start:].strip()

    return DocumentParts(
        preamble=preamble,
        frontmatter=frontmatter,
        sections_text=sections_text,
        backmatter=backmatter,
    )


def clean_title(title: str) -> str:
    title = re.sub(r"\\[A-Za-z]+\*?(?:\[[^\]]*\])?", "", title)
    title = title.replace(r"\_", "_")
    return re.sub(r"\s+", " ", title).strip()


def slug_for_title(title: str, index: int) -> str:
    hints = {
        "introduction": "introduction",
        "theoretical background": "background",
        "background": "background",
        "qwta model": "model",
        "model": "model",
        "experiment": "experiments",
        "experiments": "experiments",
        "conclusion": "conclusion",
    }
    lowered = clean_title(title).lower()
    for key, value in hints.items():
        if key.lower() in lowered or key in title:
            return f"{index:02d}_{value}.tex"

    tokens = re.findall(r"[A-Za-z0-9]+", lowered)
    slug = "_".join(tokens[:4]) if tokens else "section"
    return f"{index:02d}_{slug}.tex"


def split_sections(sections_text: str) -> list[SectionFile]:
    section_re = re.compile(r"(?m)^\\section\*?\{([^}]*)\}")
    matches = list(section_re.finditer(sections_text))

    if not matches:
        return [SectionFile("Body", "01_body.tex", sections_text.strip())]

    files: list[SectionFile] = []
    prefix = sections_text[: matches[0].start()].strip()
    if prefix:
        files.append(SectionFile("Preface", "00_preface.tex", prefix))

    for idx, match in enumerate(matches, start=1):
        next_start = matches[idx].start() if idx < len(matches) else len(sections_text)
        title = clean_title(match.group(1)) or f"Section {idx}"
        files.append(
            SectionFile(
                title=title,
                filename=slug_for_title(title, idx),
                content=sections_text[match.start() : next_start].strip(),
            )
        )
    return files


def extract_packages(text: str) -> list[str]:
    packages: list[str] = []
    for match in re.finditer(r"\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}", text):
        packages.extend(part.strip() for part in match.group(1).split(","))
    return packages


def extract_graphics(text: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", text)]


def extract_bibliographies(text: str) -> list[str]:
    names: list[str] = []
    for match in re.finditer(r"\\bibliography\{([^}]+)\}", text):
        names.extend(part.strip() for part in match.group(1).split(",") if part.strip())
    return names


def extract_style(text: str) -> str:
    match = re.search(r"\\bibliographystyle\{([^}]+)\}", text)
    return match.group(1).strip() if match else "apsrev4-2"


def inspect_report(source: Path, text: str, encoding: str, bib_path: Path | None) -> str:
    docclass = re.search(r"\\documentclass(?:\[[^\]]*\])?\{([^}]+)\}", text)
    class_line = docclass.group(0) if docclass else "(not found)"
    packages = extract_packages(text)
    sections = [clean_title(m.group(1)) for m in re.finditer(r"(?m)^\\section\*?\{([^}]*)\}", text)]
    graphics = extract_graphics(text)
    bibliographies = extract_bibliographies(text)
    labels = re.findall(r"\\label\{([^}]+)\}", text)
    duplicate_labels = sorted({label for label in labels if labels.count(label) > 1})

    warnings: list[str] = []
    if bib_path and bibliographies and bib_path.stem not in bibliographies:
        warnings.append(
            f"Bibliography command uses {', '.join(bibliographies)}, but available bib is {bib_path.name}."
        )
    if duplicate_labels:
        warnings.append(f"Duplicate labels: {', '.join(duplicate_labels)}")
    if "ctex" in packages or "fontspec" in packages:
        warnings.append("Use XeLaTeX or LuaLaTeX because the paper loads ctex/fontspec.")

    lines = [
        "# LaTeX Paper Structure Report",
        "",
        f"- Source: `{source}`",
        f"- Encoding read as: `{encoding}`",
        f"- Document class: `{class_line}`",
        f"- Packages: {', '.join(f'`{p}`' for p in packages) if packages else '(none found)'}",
        f"- Bibliography commands: {', '.join(f'`{b}`' for b in bibliographies) if bibliographies else '(none found)'}",
        f"- Bibliography file used for framework: `{bib_path.name}`" if bib_path else "- Bibliography file used for framework: (none)",
        "",
        "## Top-Level Sections",
        "",
    ]
    lines.extend(f"{idx}. {title}" for idx, title in enumerate(sections, start=1))
    if not sections:
        lines.append("(none found)")

    lines.extend(["", "## Referenced Figures", ""])
    lines.extend(f"- `{item}`" for item in graphics)
    if not graphics:
        lines.append("(none found)")

    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- {warning}" for warning in warnings)
    if not warnings:
        lines.append("- None")

    return "\n".join(lines) + "\n"


def choose_bib_path(source: Path, text: str, provided: str | None) -> Path | None:
    if provided:
        return Path(provided).resolve()

    source_dir = source.parent
    for name in extract_bibliographies(text):
        candidate = source_dir / f"{name}.bib"
        if candidate.exists():
            return candidate.resolve()

    bib_files = sorted(source_dir.glob("*.bib"))
    if len(bib_files) == 1:
        return bib_files[0].resolve()
    return None


def resolve_graphic_path(source_dir: Path, raw_path: str) -> Path | None:
    normalized = raw_path.strip().replace("\\", "/")
    candidates = [source_dir / normalized]
    if normalized.startswith("./"):
        candidates.append(source_dir / normalized[2:])

    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()

    if not Path(normalized).suffix:
        for ext in FIGURE_EXTENSIONS:
            for candidate in candidates:
                with_ext = Path(str(candidate) + ext)
                if with_ext.exists():
                    return with_ext.resolve()
    return None


def rewrite_and_copy_graphics(text: str, source_dir: Path, out_dir: Path, force: bool) -> str:
    copied: dict[str, str] = {}

    def replace(match: re.Match[str]) -> str:
        prefix, raw_path, suffix = match.group(1), match.group(2).strip(), match.group(3)
        if raw_path in copied:
            return f"{prefix}{copied[raw_path]}{suffix}"

        source_graphic = resolve_graphic_path(source_dir, raw_path)
        if not source_graphic:
            copied[raw_path] = raw_path
            return match.group(0)

        destination = out_dir / "figures" / source_graphic.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists() or force:
            shutil.copy2(source_graphic, destination)

        if Path(raw_path).suffix:
            rewritten = f"figures/{source_graphic.name}"
        else:
            rewritten = f"figures/{source_graphic.stem}"
        copied[raw_path] = rewritten
        return f"{prefix}{rewritten}{suffix}"

    return re.sub(r"(\\includegraphics(?:\[[^\]]*\])?\{)([^}]+)(\})", replace, text)


def normalize_backmatter(backmatter: str, bib_path: Path | None, out_dir: Path, force: bool) -> str:
    if not bib_path:
        return backmatter or "% Add bibliography commands here."

    references_dir = out_dir / "references"
    references_dir.mkdir(parents=True, exist_ok=True)
    destination = references_dir / bib_path.name
    if not destination.exists() or force:
        shutil.copy2(bib_path, destination)

    bib_stem = f"references/{bib_path.stem}"
    style = extract_style(backmatter)

    if not backmatter:
        return f"\\bibliographystyle{{{style}}}\n\\bibliography{{{bib_stem}}}"

    updated = re.sub(
        r"\\bibliography\{[^}]+\}",
        lambda _match: f"\\bibliography{{{bib_stem}}}",
        backmatter,
        count=1,
    )
    if updated == backmatter:
        updated = updated.rstrip() + f"\n\\bibliography{{{bib_stem}}}"
    if not re.search(r"\\bibliographystyle\{", updated):
        updated = f"\\bibliographystyle{{{style}}}\n" + updated
    return updated


def latexmkrc() -> str:
    return r"""
$pdf_mode = 5;
$out_dir = 'build';
$xelatex = 'xelatex -interaction=nonstopmode -file-line-error %O %S';
$bibtex = 'bibtex %O %B';
"""


def main_tex(section_files: list[SectionFile]) -> str:
    section_inputs = "\n".join(
        f"\\input{{sections/{Path(section.filename).stem}}}" for section in section_files
    )
    return f"""
% Auto-generated modular entry point.
\\input{{preamble}}

\\begin{{document}}

\\input{{frontmatter}}

{section_inputs}

\\input{{backmatter}}

\\end{{document}}
"""


def ensure_output_dir(out_dir: Path, force: bool) -> None:
    if out_dir.exists() and any(out_dir.iterdir()) and not force:
        raise FileExistsError(f"{out_dir} is not empty; pass --force or choose a new --out")
    out_dir.mkdir(parents=True, exist_ok=True)
    for child in ("sections", "figures", "references", "notes", "build"):
        (out_dir / child).mkdir(parents=True, exist_ok=True)


def scaffold(args: argparse.Namespace) -> None:
    source = Path(args.source).resolve()
    text, encoding = read_text(source)
    bib_path = choose_bib_path(source, text, args.bib)
    report = inspect_report(source, text, encoding, bib_path)

    if args.inspect_only:
        print(report, end="")
        return

    out_dir = Path(args.out).resolve()
    ensure_output_dir(out_dir, args.force)

    parts = split_document(text)
    section_files = split_sections(parts.sections_text)

    if args.copy_figures:
        parts = DocumentParts(
            preamble=parts.preamble,
            frontmatter=rewrite_and_copy_graphics(parts.frontmatter, source.parent, out_dir, args.force),
            sections_text=rewrite_and_copy_graphics(parts.sections_text, source.parent, out_dir, args.force),
            backmatter=rewrite_and_copy_graphics(parts.backmatter, source.parent, out_dir, args.force),
        )
        section_files = split_sections(parts.sections_text)

    backmatter = normalize_backmatter(parts.backmatter, bib_path, out_dir, args.force)

    write_text(out_dir / "preamble.tex", parts.preamble, args.force)
    write_text(out_dir / "frontmatter.tex", parts.frontmatter, args.force)
    write_text(out_dir / "backmatter.tex", backmatter, args.force)
    write_text(out_dir / "main.tex", main_tex(section_files), args.force)
    write_text(out_dir / "latexmkrc", latexmkrc(), args.force)
    write_text(out_dir / "notes" / "paper_context.md", report, args.force)

    for section in section_files:
        write_text(out_dir / "sections" / section.filename, section.content, args.force)

    print(f"Created LaTeX framework: {out_dir}")
    print(f"Sections: {len(section_files)}")
    print(f"Report: {out_dir / 'notes' / 'paper_context.md'}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="Path to the source .tex file.")
    parser.add_argument("--bib", help="Path to the bibliography file to use in the generated framework.")
    parser.add_argument("--out", required=False, help="Output directory for the generated framework.")
    parser.add_argument("--paper-key", help="Reserved for future project-specific profiles.")
    parser.add_argument("--copy-figures", action="store_true", help="Copy referenced graphics into figures/.")
    parser.add_argument("--inspect-only", action="store_true", help="Print an inspection report without writing files.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated files.")
    args = parser.parse_args(argv)
    if not args.inspect_only and not args.out:
        parser.error("--out is required unless --inspect-only is used")
    return args


if __name__ == "__main__":
    try:
        scaffold(parse_args(sys.argv[1:]))
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
