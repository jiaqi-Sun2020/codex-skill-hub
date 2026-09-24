# PRL Manuscript Polisher Skill

This package contains a reusable PRL manuscript-auditing and polishing skill.

## Contents

- `SKILL.md`: full workflow and quality gates;
- `references/prl-rules.md`: official-rule summary and source URLs;
- `templates/execution-checklist.md`: reusable checklist template;
- `scripts/audit_tex.py`: lightweight LaTeX preflight audit.

## Example

```bash
python scripts/audit_tex.py manuscript.tex --output PRL_AUDIT.md
```

Then provide `SKILL.md`, the manuscript, and the generated audit to the editing agent. Request one of: audit, structural PRL rewrite, language polish, or tracked LaTeX revision.
