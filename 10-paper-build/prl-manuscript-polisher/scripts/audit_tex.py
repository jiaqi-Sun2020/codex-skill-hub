#!/usr/bin/env python3
"""Lightweight PRL-oriented LaTeX preflight audit.

This script does not replace APS's official length calculation or scientific review.
It reports prose counts, structure, float/equation counts, and common PRL-style risks.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

SECTION_RE = re.compile(r"\\section\*?\{([^}]*)\}")
HEADER_RE = re.compile(r"\\(?:section|subsection|subsubsection)\*?\{([^}]*)\}")
COMMENT_RE = re.compile(r"(?<!\\)%.*")
COMMAND_RE = re.compile(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})?")
MATH_RE = re.compile(r"\$.*?\$|\\\(.*?\\\)|\\\[.*?\\\]", re.S)
ENV_MATH_RE = re.compile(
    r"\\begin\{(?:equation\*?|align\*?|gather\*?|multline\*?|split)\}.*?"
    r"\\end\{(?:equation\*?|align\*?|gather\*?|multline\*?|split)\}",
    re.S,
)

PATTERNS = {
    "hyphenation: continuous time quantum walk": r"\bcontinuous time quantum walk",
    "spelling: non monotonic": r"\bnon[- ]monotonic\b",
    "promotional: competitive": r"\bcompetitive\b",
    "promotional/ambiguous: significant": r"\bsignificant(?:ly)?\b",
    "absolute contrast: cannot": r"\bcannot\b",
    "repeated framing: physically motivated": r"\bphysically motivated\b",
    "indirect phrasing: the results show": r"\bthe results show\b",
    "roadmap paragraph": r"the remainder of this paper is organized",
    "possible validation-only claim": r"validation (?:MSE|error|set)",
    "possible quantum advantage claim": r"quantum advantage|reducing classical computational burden",
    "fidelity term": r"\bfidelity\b",
}


def strip_tex(text: str) -> str:
    text = COMMENT_RE.sub("", text)
    text = ENV_MATH_RE.sub(" ", text)
    text = MATH_RE.sub(" ", text)
    text = re.sub(r"\\begin\{[^}]+\}|\\end\{[^}]+\}", " ", text)
    text = COMMAND_RE.sub(" ", text)
    text = re.sub(r"[{}~_^&]", " ", text)
    text = re.sub(r"\\.", " ", text)
    return re.sub(r"\s+", " ", text)


def words(text: str) -> int:
    return len(re.findall(r"\b[A-Za-z][A-Za-z'’-]*\b|\b\d+(?:\.\d+)?\b", strip_tex(text)))


def texcount(path: Path) -> str | None:
    if not shutil.which("texcount"):
        return None
    proc = subprocess.run(
        ["texcount", "-inc", "-sum", "-brief", str(path)],
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else None


def section_counts(text: str) -> dict[str, int]:
    matches = list(SECTION_RE.finditer(text))
    output: dict[str, int] = {}
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        output[match.group(1)] = words(text[start:end])
    return output


def audit(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    findings = []
    for label, pattern in PATTERNS.items():
        hits = len(re.findall(pattern, text, flags=re.I))
        if hits:
            findings.append({"check": label, "hits": hits})

    duplicate_labels = []
    labels = re.findall(r"\\label\{([^}]+)\}", text)
    for label in sorted(set(labels)):
        count = labels.count(label)
        if count > 1:
            duplicate_labels.append({"label": label, "count": count})

    return {
        "file": str(path),
        "texcount": texcount(path),
        "approx_plain_words": words(text),
        "section_words_approx": section_counts(text),
        "headers": len(HEADER_RE.findall(text)),
        "display_math_environments": len(re.findall(r"\\begin\{(?:equation\*?|align\*?|gather\*?|multline\*?)\}", text)),
        "figures": len(re.findall(r"\\begin\{figure\*?\}", text)),
        "tables": len(re.findall(r"\\begin\{table\*?\}", text)),
        "algorithms": len(re.findall(r"\\begin\{algorithm\*?\}", text)),
        "citations": len(re.findall(r"\\cite\w*\{", text)),
        "style_risks": findings,
        "duplicate_labels": duplicate_labels,
        "has_data_availability": bool(re.search(r"data availability", text, flags=re.I)),
        "uses_revtex_prl": bool(re.search(r"\\documentclass\[[^\]]*\bprl\b[^\]]*\]\{revtex4-2\}", text)),
        "uses_fontspec": "\\usepackage{fontspec}" in text,
    }


def to_markdown(report: dict) -> str:
    lines = ["# PRL LaTeX preflight audit", "", f"- File: `{report['file']}`"]
    if report["texcount"]:
        lines.append(f"- texcount: `{report['texcount']}`")
    lines.extend([
        f"- Approximate plain words: {report['approx_plain_words']}",
        f"- Headers: {report['headers']}",
        f"- Displayed-math environments: {report['display_math_environments']}",
        f"- Figures: {report['figures']}",
        f"- Tables: {report['tables']}",
        f"- Algorithms: {report['algorithms']}",
        f"- REVTeX PRL option detected: {report['uses_revtex_prl']}",
        f"- Data Availability Statement detected: {report['has_data_availability']}",
        f"- `fontspec` detected: {report['uses_fontspec']}",
        "",
        "## Approximate words by section",
        "",
    ])
    for section, count in report["section_words_approx"].items():
        lines.append(f"- {section}: {count}")
    lines.extend(["", "## Style-risk hits", ""])
    if report["style_risks"]:
        for item in report["style_risks"]:
            lines.append(f"- {item['check']}: {item['hits']}")
    else:
        lines.append("- None detected by the lightweight pattern scan.")
    lines.extend(["", "## Duplicate labels", ""])
    if report["duplicate_labels"]:
        for item in report["duplicate_labels"]:
            lines.append(f"- `{item['label']}`: {item['count']}")
    else:
        lines.append("- None detected.")
    lines.extend([
        "",
        "> This report is a preflight aid. It is not an official APS word-equivalent calculation and does not validate scientific claims.",
    ])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("tex", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit(args.tex)
    output = json.dumps(report, indent=2, ensure_ascii=False) if args.json else to_markdown(report)
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
