---
type: project
---

# Skill hub governance

## Durable decisions

- `My_skills` is the canonical local source and navigation hub for reusable Codex Skills. Its public repository is `jiaqi-Sun2020/codex-skill-hub`.
- `README.md` and `README.en.md` are the bilingual repository-wide entrypoints. They explain all twenty active Skills whose canonical source is stored here and provide only concise navigation for PaperTrace's external project-owned Skills.
- `10-paper-build/README.md` and `README.en.md` are the bilingual category map for nine peer paper-build Skills. `20-project-build/README.md` and `README.en.md` remain the technical architecture map for the six project-build Skills, SCI/STAT/ENG/GOV contracts, independent state axes, and lifecycle routing.
- README acknowledgements identify confirmed open-source Skill influences with author or maintainer, project link, scope of influence, and license when known. Do not infer unrecorded provenance.
- Original or otherwise relicensable hub content is MIT licensed. Third-party license, copyright, and notice obligations remain in force.
- The hub directly maintains nine paper-build Skills under `10-paper-build/`, six project-build Skills under `20-project-build/`, four reusable core Skills under `50-core-utils/`, and `logic-chain-tutor` under `90-personal/`.
- The nine paper-build Skills are `academic-figure-workflow`, `research-logic`, `experiment-design`, `data-analysis`, `research-html-report`, `latex-paper-build-skill`, `paper-polishing-skill`, `prl-manuscript-polisher`, and `interactive-skill-builder`.
- On 2026-09-24, eight paper-build Skills were imported as a source snapshot from `S_paper_skills` commit `dcd573b1768e48e794975100f8548dc0f1bcb50e`. The old directory typo `data-analsys-skill/` is normalized to `data-analysis/`; the old wrapper and `util_skills/` layer are not retained. The old repository's full refs are preserved in an external verified bundle with SHA-256 `261B5C3496DABC7BBE3087F40B626C0499606827672E3458599E619B7BE0C521` before retirement.
- The imported paper-build Skills are direct hub source, not immutable Skill Registry releases and not components of the six-Skill `20-project-build/` architecture.
- `experiment-design` owns research questions, hypotheses, evidence gaps, datasets, baselines, ablations, metrics, controls, and claim boundaries. It does not implement experiment execution, runners, adapters, or runtime gates and grants no execution or publication authority.
- `S_PAPER_SKILLS_LICENSE` preserves the imported source repository's MIT notice. The root MIT license does not override retained third-party obligations.
- `project-agent-generator-skill`, `research-project-pipeline`, and `research-workspace-governance` moved to `20-project-build/` on 2026-09-16; their former `50-core-utils/` paths are retired.
- `experiment-protocol-audit` validates explicit project-contained normalized protocol and evidence contracts and emits evidence-bound records. It never runs project commands or adapters, chooses a method, or establishes a scientific claim.
- `project-submission-audit` is an independent read-only gate over an exact change surface. It reports `PASS`, `BLOCKED`, or `INCOMPLETE` and never commits, pushes, publishes, or establishes scientific validity.
- `research-management-pipeline` is the repeated post-onboarding lifecycle entry. It summarizes governance coverage, independent state axes, gates, gaps, and amendment impact, then routes one smallest next action without executing research, creating `.agents`, choosing methods, or granting authority.
- `handoff` writes a compact evidence-linked continuation note outside the project by default. It neither establishes completion nor expands mutation authority.
- `50-core-utils/skill-registry` is integrated version-governance infrastructure, not a separate repository or active Skill. Its `reader-learner` `1.0.0` release remains immutable historical material; PaperTrace owns its current project-specific fork.
- Project-owned Skills remain in their canonical projects and are linked from the hub. Do not copy them into this repository merely for publication.
- Former utility duplicates under `S_paper_skills/util_skills/` remain retired in favor of their canonical hub sources.
- Generator and Onboarding Pipeline are one-time onboarding components. Generator creates missing Agent scaffolding; forced refresh is break-glass recovery. Its restricted bootstrap-only path creates only missing managed startup files around one safe existing Agent bundle and requires a current hash-bound preview.
- `neat-freak` owns routine post-onboarding project-information maintenance. It uses a hash-bound `plan` / `apply` flow and may repair only existing marked Bootstrap wiring with explicit authorization; it does not regenerate a framework.
- `research-workspace-governance` owns domain-neutral asset roles, locations, SCI/STAT/ENG/GOV contracts, state axes, provenance, evidence, amendments, invalidation, migration, retention, deletion boundaries, project contracts, relocation maps, and derived traceability. It validates metadata and review boundaries without performing domain science.
- Project contracts and topology declarations are untrusted data. Mandatory-policy topology binds canonical policy hashes to applicable execution roots through explicit references, verified loader evidence, or owner-approved isolation; Pipeline boundary-checks and Neat-Freak audits content.
- Relocation maps preserve historical paths without rewriting history. Comparison semantics come from a domain Profile or authorized reviewer; governance preserves evidence, review, invalidation, allowed uses, and forbidden inferences.
- `logic-chain-tutor` remains the single canonical personal Skill source under `90-personal/`.
- `.agents/AGENTS.md` is the single project Agent entrypoint. Trusted project-local `.codex/` hooks load it at supported lifecycle events; do not add a root `AGENTS.md`.

### Publication contract

- Before publishing, validate all twenty active Skills, compile relevant Python scripts, smoke-test documented entry points, check links and unique Skill names, scan tracked files for secrets and machine-specific paths, run Neat-Freak and Bootstrap audits, run the Registry check and tests, and perform a read-only submission audit.
- Compare linked external projects against fetched upstream before committing; never force-push.
- Keep generated backups, local inbox material, shortcut files, caches, credentials, private environment files, and migration bundles out of the public repository.
- Do not delete a migrated remote or local source until the hub commit is pushed, new public paths are verified, and a complete external bundle is verified.

### Evidence

- `README.md`
- `README.en.md`
- `10-paper-build/README.md`
- `10-paper-build/README.en.md`
- `10-paper-build/S_PAPER_SKILLS_LICENSE`
- `10-paper-build/experiment-design-skill/SKILL.md`
- `20-project-build/README.md`
- `20-project-build/README.en.md`
- `.agents/DECISIONS.md`
- `50-core-utils/skill-registry/README.md`
- `20-project-build/experiment-protocol-audit/SKILL.md`
- `20-project-build/project-submission-audit/SKILL.md`
- `20-project-build/research-management-pipeline/SKILL.md`
- `20-project-build/research-project-pipeline/SKILL.md`
- `20-project-build/research-workspace-governance/SKILL.md`
- `20-project-build/project-agent-generator-skill/SKILL.md`
- `50-core-utils/handoff/SKILL.md`
- `50-core-utils/neat-freak/SKILL.md`
- `90-personal/logic-chain-tutor/SKILL.md`
