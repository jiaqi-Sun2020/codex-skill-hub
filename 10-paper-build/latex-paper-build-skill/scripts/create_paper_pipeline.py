#!/usr/bin/env python3
"""Create a complete research-paper pipeline workspace."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any


STAGE_DIRS = (
    "00_research_logic",
    "01_experiment_design",
    "02_training_code",
    "03_results",
    "04_reports",
    "05_manuscript_zh",
    "06_review_gate",
    "07_polished_submission",
)


DEFAULT_ABSTRACT = "Write the abstract here."


def slugify(text: str) -> str:
    tokens = re.findall(r"[A-Za-z0-9]+", text.lower())
    return "-".join(tokens[:8]) if tokens else "paper-project"


def latex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in str(text))


def write_text(path: Path, text: str, force: bool) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def default_paper_config(title: str, project_key: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "project_key": project_key,
        "title": title,
        "short_title": "TODO: short running title",
        "venue": "PRA",
        "language": "zh-CN",
        "date": r"\today",
        "authors": [
            {
                "name": "Author One",
                "affiliations": ["aff1"],
                "email": "corresponding.author@example.edu",
                "corresponding": True,
                "orcid": "TODO",
            },
            {
                "name": "Author Two",
                "affiliations": ["aff1"],
                "email": "TODO",
                "corresponding": False,
                "orcid": "TODO",
            },
        ],
        "affiliations": [
            {
                "id": "aff1",
                "name": "TODO: Department or Institute",
                "address": "TODO: University, City, Country",
            }
        ],
        "correspondence": {
            "name": "Author One",
            "email": "corresponding.author@example.edu",
            "address": "TODO: full correspondence address",
        },
        "keywords": [
            "quantum walk",
            "coin-state tomography",
            "sparse measurement",
        ],
        "abstract": DEFAULT_ABSTRACT,
        "acknowledgments": "TODO: funding and acknowledgments",
        "notes": "Edit this file first; generated frontmatter should follow this config.",
    }


def load_paper_config(path: Path, title: str, project_key: str) -> dict[str, Any]:
    config = default_paper_config(title, project_key)
    if not path.exists():
        return config
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("paper_config.json must contain a JSON object")
    merged = dict(config)
    merged.update(loaded)
    if "title" not in loaded or not loaded["title"]:
        merged["title"] = title
    if "project_key" not in loaded or not loaded["project_key"]:
        merged["project_key"] = project_key
    return merged


def write_paper_config(project: Path, title: str, project_key: str, provided: Path | None, force: bool) -> dict[str, Any]:
    destination = project / "paper_config.json"
    if provided:
        if not provided.exists():
            raise FileNotFoundError(f"paper config not found: {provided}")
        config = load_paper_config(provided, title, project_key)
        if not destination.exists() or force:
            destination.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return config

    config = load_paper_config(destination, title, project_key)
    if not destination.exists() or force:
        destination.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return config


def affiliation_lookup(config: dict[str, Any]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for item in config.get("affiliations", []):
        if not isinstance(item, dict):
            continue
        key = str(item.get("id", "")).strip()
        if not key:
            continue
        name = str(item.get("name", "")).strip()
        address = str(item.get("address", "")).strip()
        joined = ", ".join(part for part in (name, address) if part)
        lookup[key] = joined or key
    return lookup


def render_frontmatter(config: dict[str, Any]) -> str:
    lines: list[str] = [f"\\title{{{latex_escape(config.get('title', 'Paper Title'))}}}", ""]
    affiliations = affiliation_lookup(config)
    authors = config.get("authors") or []
    if not isinstance(authors, list) or not authors:
        authors = default_paper_config(str(config.get("title", "Paper Title")), str(config.get("project_key", "paper-project")))["authors"]

    for author in authors:
        if not isinstance(author, dict):
            continue
        name = str(author.get("name", "TODO Author")).strip() or "TODO Author"
        lines.append(f"\\author{{{latex_escape(name)}}}")
        if author.get("email") and author.get("email") != "TODO":
            lines.append(f"\\email{{{latex_escape(author['email'])}}}")
        author_affiliations = author.get("affiliations") or []
        if isinstance(author_affiliations, str):
            author_affiliations = [author_affiliations]
        if not author_affiliations:
            lines.append(r"\affiliation{TODO: Affiliation}")
        for aff_key in author_affiliations:
            aff_text = affiliations.get(str(aff_key), str(aff_key))
            lines.append(f"\\affiliation{{{latex_escape(aff_text)}}}")
        lines.append("")

    date_value = str(config.get("date", r"\today"))
    if date_value == r"\today":
        lines.append(r"\date{\today}")
    else:
        lines.append(f"\\date{{{latex_escape(date_value)}}}")
    lines.append("")

    abstract = str(config.get("abstract") or DEFAULT_ABSTRACT).strip()
    lines.extend([r"\begin{abstract}", abstract, r"\end{abstract}", ""])

    keywords = config.get("keywords") or []
    if keywords:
        if isinstance(keywords, list):
            keyword_text = "; ".join(str(item) for item in keywords)
        else:
            keyword_text = str(keywords)
        lines.append(f"\\keywords{{{latex_escape(keyword_text)}}}")
        lines.append("")

    correspondence = config.get("correspondence") or {}
    if isinstance(correspondence, dict):
        email = correspondence.get("email")
        address = correspondence.get("address")
        if email or address:
            lines.append("% Correspondence")
            if email:
                lines.append(f"% Email: {email}")
            if address:
                lines.append(f"% Address: {address}")
            lines.append("")

    lines.append(r"\maketitle")
    return "\n".join(lines).rstrip() + "\n"


def revtex_journal(config: dict[str, Any]) -> str:
    venue = str(config.get("venue", "PRA")).strip().lower()
    if "prl" in venue:
        return "prl"
    return "pra"


def render_preamble(config: dict[str, Any]) -> str:
    journal = revtex_journal(config)
    language = str(config.get("language", "zh-CN")).strip().lower()
    is_chinese = language.startswith("zh") or "chinese" in language

    if is_chinese:
        return f"""
\\documentclass[aps,{journal},reprint,groupedaddress]{{revtex4-2}}

\\usepackage[UTF8, heading=true]{{ctex}}
\\usepackage{{fontspec}}
\\usepackage{{amsmath,amssymb,bm}}
\\usepackage{{graphicx}}
\\usepackage{{xcolor}}

\\newcommand{{\\ket}}[1]{{\\left|#1\\right\\rangle}}
\\newcommand{{\\bra}}[1]{{\\left\\langle#1\\right|}}
\\newcommand{{\\braket}}[2]{{\\left\\langle #1 \\middle| #2 \\right\\rangle}}
\\newcommand{{\\Tr}}{{\\mathrm{{Tr}}}}
\\newcommand{{\\TODO}}[1]{{\\textcolor{{red}}{{[TODO: #1]}}}}
""".strip() + "\n"

    return f"""
\\documentclass[aps,{journal},reprint,superscriptaddress]{{revtex4-2}}

\\usepackage{{amsmath,amssymb,bm}}
\\usepackage{{graphicx}}
\\usepackage{{xcolor}}

\\newcommand{{\\ket}}[1]{{\\left|#1\\right\\rangle}}
\\newcommand{{\\bra}}[1]{{\\left\\langle#1\\right|}}
\\newcommand{{\\braket}}[2]{{\\left\\langle #1 \\middle| #2 \\right\\rangle}}
\\newcommand{{\\Tr}}{{\\mathrm{{Tr}}}}
""".strip() + "\n"

def copy_template(skill_dir: Path, manuscript_dir: Path, config: dict[str, Any], force: bool) -> None:
    template_dir = skill_dir / "assets" / "revtex-qwct-template"
    if not template_dir.exists():
        return

    for source in template_dir.rglob("*"):
        relative = source.relative_to(template_dir)
        destination = manuscript_dir / relative
        if source.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            continue
        if destination.exists() and not force:
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    write_text(manuscript_dir / "preamble.tex", render_preamble(config), True)
    write_text(manuscript_dir / "frontmatter.tex", render_frontmatter(config), True)


def run_latex_scaffold(
    skill_dir: Path,
    latex_source: Path,
    bib: Path | None,
    manuscript_dir: Path,
    copy_figures: bool,
    force: bool,
) -> None:
    script = skill_dir / "scripts" / "scaffold_latex_paper.py"
    command = [
        sys.executable,
        str(script),
        "--source",
        str(latex_source),
        "--out",
        str(manuscript_dir),
    ]
    if bib:
        command.extend(["--bib", str(bib)])
    if copy_figures:
        command.append("--copy-figures")
    if force:
        command.append("--force")
    subprocess.run(command, check=True)


def pipeline_context(title: str, project_key: str, latex_source: Path | None, config: dict[str, Any]) -> str:
    source_line = f"- LaTeX source: `{latex_source}`" if latex_source else "- LaTeX source: TODO"
    authors = config.get("authors") or []
    author_names = ", ".join(str(a.get("name")) for a in authors if isinstance(a, dict) and a.get("name")) or "TODO"
    venue = config.get("venue", "TODO")
    return f"""
# Paper Pipeline Context

- Title: {title}
- Project key: {project_key}
- Created: {date.today().isoformat()}
- Target venue: {venue}
- Authors: {author_names}
- Paper config: `paper_config.json`
{source_line}

## Stage Map

| Stage | Folder | Sibling skill | Status |
|---|---|---|---|
| Intake and inventory | `00_research_logic/` | this skill | TODO |
| Research logic | `00_research_logic/research_logic.md` | `research-logic` | TODO |
| Experiment design | `01_experiment_design/experiment_plan.md` | `experiment-design` | TODO |
| Training code/results | `02_training_code/`, `03_results/` | `training-code-architecture` | TODO |
| HTML research report | `04_reports/` | `research-html-report` | TODO |
| Chinese LaTeX manuscript | `05_manuscript_zh/` | `latex-paper-build-skill` | TODO |
| Author review gate | `06_review_gate/` | this skill | TODO |
| Polished submission | `07_polished_submission/` | `paper-polishing-skill` | TODO |

## Next Step

Start at the first TODO stage whose artifact is missing or too weak to support the later stages. Edit `paper_config.json` before finalizing title, authors, affiliations, correspondence, acknowledgments, and keywords.
"""


def intake_template(title: str) -> str:
    return f"""
# Intake

- Paper title: {title}
- One-sentence identity: TODO
- Target venue: TODO
- Language: TODO
- Page limit: TODO
- Blind-review constraints: TODO
- Paper config: `../paper_config.json`

## Existing Assets

- Manuscript: TODO
- Bibliography: TODO
- Figures: TODO
- Experiment code: TODO
- Result files: TODO
- Reports/notes: TODO

## Missing Decisions

- TODO
"""


def research_logic_template() -> str:
    return """
# Research Logic

Use `research-logic` for this stage.

## Central Mechanism

TODO

## Native Functions

TODO

## Direct Connection

TODO

## Mechanism-Level Reconstruction

TODO

## Claim Discipline

TODO
"""


def experiment_plan_template() -> str:
    return """
# Experiment Plan

Use `experiment-design` for this stage.

## Central Claim

TODO

## Research Questions

TODO

## Datasets and Tasks

TODO

## Baselines

TODO

## Ablations

TODO

## Mechanism Checks

TODO

## Metrics and Tables

TODO

## Claim Boundaries

TODO
"""


def review_gate_template() -> str:
    return """
# Author Review Checklist

Before using `paper-polishing-skill`, the author should check:

- [ ] `paper_config.json` has the correct title, authors, affiliations, correspondence address, email, and acknowledgments.
- [ ] Abstract and introduction follow `latex-paper-build-skill/references/qct-writing-methodology.md` when the paper is QCT/QWCT.
- [ ] The first abstract sentence is setting-qualified, not a universal theorem.
- [ ] The introduction explains why influence does not imply invertibility.
- [ ] No internal workflow terms such as pipeline, eval, checkpoint, author-review, or claim appear in formal manuscript prose.
- [ ] The Chinese scientific claim is correct and appropriately bounded.
- [ ] Completed, partial, and planned experiments are clearly separated.
- [ ] Figure/table intent and captions are correct.
- [ ] TODO markers are either resolved or deliberately retained.
"""


def build_report_template() -> str:
    return """
# Build and Submission Report

## Build Command

```powershell
latexmk -xelatex -bibtex -interaction=nonstopmode -file-line-error -outdir=build main.tex
```

## Checks

| Check | Status | Notes |
|---|---|---|
| PDF builds | TODO | |
| Undefined references | TODO | |
| Undefined citations | TODO | |
| Missing figures | TODO | |
| Bibliography drift | TODO | |
| Page count | TODO | |
| Anonymization | TODO | |
| Paper config applied | TODO | `paper_config.json` -> `05_manuscript_zh/frontmatter.tex` |
"""


def create_pipeline(args: argparse.Namespace) -> None:
    skill_dir = Path(__file__).resolve().parents[1]
    project = Path(args.project).resolve()
    title = args.title
    project_key = args.project_key or slugify(title)
    latex_source = Path(args.latex_source).resolve() if args.latex_source else None
    bib = Path(args.bib).resolve() if args.bib else None
    provided_config = Path(args.paper_config).resolve() if args.paper_config else None

    project.mkdir(parents=True, exist_ok=True)
    config = write_paper_config(project, title, project_key, provided_config, args.force)
    title = str(config.get("title") or title)
    project_key = str(config.get("project_key") or project_key)

    for stage in STAGE_DIRS:
        (project / stage).mkdir(parents=True, exist_ok=True)

    write_text(project / "pipeline_context.md", pipeline_context(title, project_key, latex_source, config), args.force)
    write_text(project / "00_research_logic" / "intake.md", intake_template(title), args.force)
    write_text(project / "00_research_logic" / "research_logic.md", research_logic_template(), args.force)
    write_text(project / "01_experiment_design" / "experiment_plan.md", experiment_plan_template(), args.force)
    write_text(project / "06_review_gate" / "author_review_checklist.md", review_gate_template(), args.force)
    write_text(project / "07_polished_submission" / "build_report.md", build_report_template(), args.force)

    manuscript_dir = project / "05_manuscript_zh"
    if latex_source:
        run_latex_scaffold(skill_dir, latex_source, bib, manuscript_dir, args.copy_figures, args.force)
        write_text(manuscript_dir / "preamble.tex", render_preamble(config), True)
        write_text(manuscript_dir / "frontmatter.tex", render_frontmatter(config), True)
    elif not args.no_template:
        copy_template(skill_dir, manuscript_dir, config, args.force)

    print(f"Created paper pipeline: {project}")
    print(f"Paper config: {project / 'paper_config.json'}")
    print(f"Pipeline context: {project / 'pipeline_context.md'}")
    print(f"Manuscript folder: {manuscript_dir}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="Output project/pipeline directory.")
    parser.add_argument("--title", required=True, help="Paper title used in generated context and template.")
    parser.add_argument("--project-key", help="Stable short key for reports and artifacts.")
    parser.add_argument("--paper-config", help="Existing paper_config.json to merge/copy into the pipeline.")
    parser.add_argument("--latex-source", help="Existing .tex file to scaffold into 05_manuscript_zh/.")
    parser.add_argument("--bib", help="Bibliography file to use when --latex-source is provided.")
    parser.add_argument("--copy-figures", action="store_true", help="Copy referenced figures when scaffolding LaTeX.")
    parser.add_argument("--no-template", action="store_true", help="Do not copy the default LaTeX template when no source is provided.")
    parser.add_argument("--force", action="store_true", help="Overwrite generated files.")
    return parser.parse_args(argv)


if __name__ == "__main__":
    try:
        create_pipeline(parse_args(sys.argv[1:]))
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
