#!/usr/bin/env python3
"""Create a complete research-paper pipeline workspace."""

from __future__ import annotations

import argparse
import json
import re
import stat
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


def validate_pipeline_output(project: Path) -> None:
    """Reject linked output roots/ancestors and linked existing stage content.

    Check lexical paths before resolve(), otherwise a junction loses its identity.
    This is a local preflight, not a transaction against concurrent path swaps.
    """
    def check(path: Path) -> None:
        for candidate in (path.absolute(), *path.absolute().parents):
            try:
                info = candidate.lstat()
            except FileNotFoundError:
                continue
            if (stat.S_ISLNK(info.st_mode) or
                    getattr(info, 'st_file_attributes', 0) & 0x400):
                raise ValueError(f'linked/reparse pipeline output path is not allowed: {candidate}')

    for destination in (project, project / 'paper_config.json', project / 'pipeline_context.md'):
        check(destination)
    pending = [project / stage for stage in STAGE_DIRS]
    while pending:
        path = pending.pop()
        check(path)  # never traverse a linked directory
        if path.is_dir():
            pending.extend(path.iterdir())


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
    existing_metadata = {name: (manuscript_dir / name).exists()
                         for name in ('preamble.tex', 'frontmatter.tex')}

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

    write_text(manuscript_dir / "preamble.tex", render_preamble(config), force or not existing_metadata['preamble.tex'])
    write_text(manuscript_dir / "frontmatter.tex", render_frontmatter(config), force or not existing_metadata['frontmatter.tex'])


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

This table is a navigation hint, not a second current-state authority. Read the
relevant artifact and approval source before relying on any stage's readiness.

| Stage | Folder | Sibling skill | Status |
|---|---|---|---|
| Intake and inventory | `00_research_logic/` | this skill | TODO |
| Optional literature discovery and synthesis | `00_research_logic/literature/` | `literature-review` | N/A until activated |
| Optional known-set comparison | `00_research_logic/literature/literature_matrix.md` | `literature-triage-matrix` | N/A until activated |
| Research logic | `00_research_logic/research_logic.md` | `research-logic` | TODO |
| Experiment design | `01_experiment_design/experiment_plan.md` | `experiment-design` | TODO |
| Evidence production | `02_training_code/`, `03_results/` | project/domain workflow | TODO/N/A |
| Data integrity and analysis | `03_results/` | `data-analysis` | TODO/N/A |
| HTML research report | `04_reports/` | `research-html-report` | TODO |
| Optional figure-evidence lane | `05_manuscript_zh/figures/` | `academic-figure-workflow` | N/A until activated |
| Chinese LaTeX manuscript | `05_manuscript_zh/` | `latex-paper-build-skill` | TODO |
| Mock pre-review and author gate | `06_review_gate/` | `paper-audit` then author | TODO |
| Polished submission | `07_polished_submission/` | `paper-polishing-skill` | TODO |

## Next Step

Continue the requested stage; reopen only dependencies that cannot support its
next action. Use `00_research_logic/intake.md` for the work goal or its formal
contract pointer, `00_research_logic/research_logic.md` for scientific questions,
and the active stage artifact for local decisions. This context does not copy
goals or maintain their current state. For a blocking ambiguity or material
change, use the installed `latex-paper-build-skill` reference
`references/goal-clarification.md`, then return to the requested stage.

Edit `paper_config.json` before finalizing title, authors, affiliations, correspondence, acknowledgments, and keywords. Activate the figure-evidence lane only when the paper needs figures; do not create empty figure packages for figure-free work. Figure/package QA and scientific claim review remain separate states.

Unknown context routes to literature-review; a known paper set routes to
literature-triage-matrix. Research-logic can form initial candidates and reopen
them after source checks. The generator creates routing/scaffolding only; agents
invoke these literature Skills on demand. It performs no searches or source
appraisal. Create literature artifacts only when requested;
DOI registration, metadata matching, source support, retraction screening,
scientific quality, search coverage and author claim approval
are separate judgments. Theory, qualitative and literature work may use direct
reasoning/synthesis without new experiments, training or numerical analysis.

Completed-manuscript mock review and revision re-review route to `paper-audit`,
then return to the human Stage 6 gate. Before whole-manuscript final delivery,
including a Stage 7 shortcut, follow paper-audit's final-manuscript handoff.
Reference the reviewed version, coverage, unresolved issues and author decision;
this context is not a second review state. The generator does not run reviews
or create an empty `06_review_gate/paper_audit_report.md`. Existing equivalent
reports may be reused; saving a report requires applicable authorization.
"""


def work_goal_section() -> str:
    """Shared intake content; neither a scientific decision nor authorization."""
    return """## Work Goal and Decision Source

- Current requested deliverable/decision and audience: TODO
- Scope and non-goals: TODO
- Observable acceptance: TODO
- Approved formal goal contract, if present: TODO/N/A (reference, not a copy)
- Decision source and applicable action-authority reference: TODO
- Remaining blocker and smallest next action: TODO/N/A

The scientific question belongs in `research_logic.md`. Goal agreement is not
scientific approval or permission for experiments, networking, writes or release.
Use only applicable fields; do not invent missing history. For saved amendments,
retain the prior decision as history and note source/approval, reason, results
already seen, affected artifacts and reviews. Local decisions stay in the active
stage artifact; do not create a question ledger."""


def initialization_entries(inputs: dict[str, Any]) -> dict[str, str]:
    """Render only two paper entry points, without config or venue defaults."""
    section = work_goal_section()
    replacements = {
        "Current requested deliverable/decision and audience: TODO":
            "Current requested deliverable/decision and audience: " + inputs['work_goal'],
        "Observable acceptance: TODO": "Observable acceptance: " + inputs['acceptance'],
        "Approved formal goal contract, if present: TODO/N/A (reference, not a copy)":
            "Approved formal goal contract, if present: " + (inputs['formal_goal_ref'] or 'not located; do not infer approval'),
        "Decision source and applicable action-authority reference: TODO":
            "Decision source: " + inputs['goal_source'] + "; action authority is checked separately at apply",
        "Remaining blocker and smallest next action: TODO/N/A":
            "Remaining blocker and smallest next action: " + inputs['next_action'],
    }
    for old, new in replacements.items():
        section = section.replace(old, new)
    if inputs['formal_goal_ref']:
        section = section.replace(inputs['work_goal'], 'See the formal goal reference; proposed changes require owner confirmation', 1)
    materials = '\n'.join('- `' + p + '`' for p in inputs['references']) or '- No supplied material; scientific evidence remains unknown.'
    intake = f"# Intake\n\n- Paper title: {inputs['title']}\n\n{section}\n\n## Existing Assets\n\n{materials}\n"
    goal_ref = inputs['intake_ref'] or '00_research_logic/intake.md'
    context = (
        '# Paper Pipeline Context\n\n'
        f"- Work-goal source: `{goal_ref}`\n"
        f"- Starting stage: {inputs['start_stage']}\n"
        f"- Next action: {inputs['next_action']}\n\n"
        'This is navigation, not a second goal or current-state authority.\n'
        'Use latex-paper-build-skill for the selected stage; read its sole\n'
        'references/goal-clarification.md only for a blocker or material change.\n'
        'Scientific questions belong to research-logic. Optional literature and\n'
        'figure lanes stay lazy; no search, experiment, writing or publication\n'
        'has been performed or authorized by creating these entries.\n'
        'Missing paper_config.json is allowed until manuscript metadata is needed.\n'
        'Agent framework, persistent Hook and memory are separate approved steps.\n'
    )
    return {'00_research_logic/intake.md': intake, 'pipeline_context.md': context}


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

{work_goal_section()}

## Existing Assets

- Manuscript: TODO
- Bibliography: TODO
- Figures: TODO
- Experiment code: TODO
- Result files: TODO
- Reports/notes: TODO
- Literature set, reviewed source sections and search limits: TODO/N/A

## Missing Decisions

- TODO
"""


def research_logic_template() -> str:
    return """
# Research Logic

Use `research-logic` for this stage.

## Focal Question and Mode

TODO

## Candidate Directions, Assumptions and Rival Explanations

TODO

## Located Support, Counterevidence and Literature Gaps

TODO

## Chosen Direction or Unresolved Decision

TODO

## Claim Discipline

TODO

Use a method-integration reconstruction only when that is the actual question.
Candidate ideas are not validated findings; a simple adequate method is allowed.
"""


def experiment_plan_template() -> str:
    return """
# Experiment Plan

Use `experiment-design` for this stage.

## Central Claim

TODO

## Research Questions

TODO

## Applicable Evidence Sources and Independent Units

TODO

## Rival Explanations and Discriminating Evidence

TODO

## Applicable Controls, Sampling or Proof Obligations

TODO

## Failure Cases, Confounding and Missingness

TODO

## Analysis Plan and Exploratory / Confirmatory Status

TODO

Datasets, baselines, ablations, seeds and numerical metrics are conditional
modules, not required for theoretical, qualitative or literature-only research.
Record any amendment and results already seen; do not invent preregistration.

## Optional Figure Evidence Plan

- Applicable: TODO (yes/no, with reason)
- Figure id and target manuscript section: TODO
- Primary claim anchor: TODO
- Evidence/material sources: TODO
- Evidence readiness: TODO (`unavailable`, `unreviewed`, or `verified_for_figure`)
- Statistics readiness: TODO (`not_applicable`, `unreviewed`, or `verified_for_figure`)
- Panel roles and non-redundant message per panel: TODO
- Target venue and final physical size: TODO
- Required editable source and export formats: TODO
- Open scientific decisions: TODO

This section defines figure intent only. Use `data-analysis` for applicable
data/statistical review and `academic-figure-workflow` for drawing, exports,
captions, evidence trace, and rendered QA.

## Claim Boundaries

TODO
"""


def review_gate_template() -> str:
    return """
# Author Review Checklist

Before whole-manuscript final delivery via `paper-polishing-skill` or
`prl-manuscript-polisher`, the author should check:

- [ ] An applicable whole-manuscript pre-review from `paper-audit` or an equivalent human review is located with its version, coverage, unresolved issues and author disposition; a limited report is not whole-paper coverage.
- [ ] Revision concerns are verified against current text/evidence, not closed merely because an author says they were fixed; prior IDs and history remain identifiable.
- [ ] The mock recommendation is separate from scientific support, author approval and next-action authority. Local edits and explicitly pending-review drafts do not require whole-paper pre-review.

- [ ] The requested deliverable matches the approved goal source in intake or its formal contract; unresolved changes are proposals, not concurrent goals.
- [ ] Goal, method, data, source-evidence and figure-meaning changes since the reviewed version have an impact check, including formulas, scope and claim strength; re-review affected portions even if conclusion wording is unchanged. Apply this after polishing too; pure wording/layout changes reuse review after a meaning check.
- [ ] Post-outcome amendments and their reasons are disclosed; historical approvals are not silently rewritten.
- [ ] Author approval is separate from action authority; the intended next action has an applicable authorization source, not merely goal agreement.
- [ ] `paper_config.json` has the correct title, authors, affiliations, correspondence address, email, and acknowledgments.
- [ ] Abstract and introduction follow `latex-paper-build-skill/references/qct-writing-methodology.md` when the paper is QCT/QWCT.
- [ ] Abstract and introduction match the demonstrated scope; a theorem is claimed only when its assumptions and proof justify it.
- [ ] Project-specific distinctions (e.g. influence versus invertibility in QCT) are checked only when applicable.
- [ ] Internal process IDs/status labels are not mistaken for scientific prose; legitimate scientific terms such as claim are allowed.
- [ ] Load-bearing citations have located source/version support, not only DOI registration or abstract screening.
- [ ] Search coverage, duplicate/overlapping studies, unavailable reports and review limitations are disclosed where applicable.
- [ ] Exploratory and confirmatory reasoning, rival explanations and unresolved scientific decisions are explicit.
- [ ] The Chinese scientific claim is correct and appropriately bounded.
- [ ] Completed, partial, and planned experiments are clearly separated.
- [ ] Figure/table intent and captions are correct.
- [ ] Each applicable figure traces its claim, labels, values, and annotations to reviewed source material; missing evidence remains draft or blocked.
- [ ] Applicable statistical findings, units, uncertainty, and exclusions agree with the `data-analysis` output or documented human review.
- [ ] Each applicable figure has the required editable source or approved exception, exports, `caption.md`, evidence trace, and final-size QA under `05_manuscript_zh/figures/`.
- [ ] Final-size readability, clipping, typography, colour accessibility, editability, and scientific consistency have been reviewed.
- [ ] A visual/package PASS has not been interpreted as scientific claim approval. Mark these figure checks `N/A` with a reason when the manuscript has no figure work.
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
| Requested deliverable against approved goal source | TODO | Reference intake or formal contract; do not duplicate current goal state |
| Review impact of method/data/evidence/figure changes | TODO/N/A | After polishing too: include formulas, scope and claim strength; reuse unaffected review after a meaning check, re-review affected portions; unchanged conclusion text is not sufficient |
| Authority for the proposed next action | TODO | Goal/content approval and a successful build do not authorize execution or release |
| Applicable whole-manuscript pre-review | TODO | Reference report/version/coverage and unresolved issues; no duplicate review state |
| Author disposition of review | TODO | Mock recommendation and permission to continue a draft do not imply scientific approval or submission readiness |
| PDF builds | TODO | |
| Undefined references | TODO | |
| Undefined citations | TODO | |
| Citation identity and located statement support | TODO/N/A | DOI registration is not claim support |
| Literature coverage, versions and unresolved checks | TODO/N/A | Reuse review_protocol.md; do not infer completeness from a tool exit code |
| Figure lane applicable | TODO/N/A | Give a reason when N/A |
| Missing figures or broken paths | TODO/N/A | All applicable paths remain under `05_manuscript_zh/figures/` |
| Editable figure sources or approved exceptions | TODO/N/A | |
| Required figure exports and final formats | TODO/N/A | |
| Figure captions and manuscript references | TODO/N/A | |
| Figure evidence/source trace | TODO/N/A | |
| Rendered final-size and accessibility QA | TODO/N/A | Visual QA does not approve the scientific claim |
| Bibliography drift | TODO | |
| Page count | TODO | |
| Anonymization | TODO | |
| Paper config applied | TODO | `paper_config.json` -> `05_manuscript_zh/frontmatter.tex` |
"""


def create_pipeline(args: argparse.Namespace) -> None:
    skill_dir = Path(__file__).resolve().parents[1]
    original_project = Path(args.project)
    validate_pipeline_output(original_project)
    project = original_project.resolve()
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
        existing_metadata = {name: (manuscript_dir / name).exists()
                             for name in ('preamble.tex', 'frontmatter.tex')}
        run_latex_scaffold(skill_dir, latex_source, bib, manuscript_dir, args.copy_figures, args.force)
        write_text(manuscript_dir / "preamble.tex", render_preamble(config), args.force or not existing_metadata['preamble.tex'])
        write_text(manuscript_dir / "frontmatter.tex", render_frontmatter(config), args.force or not existing_metadata['frontmatter.tex'])
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
