---
type: project
---

# Skill hub governance

## Durable decisions

- `My_skills` is the canonical local source and navigation hub for reusable Codex skills.
- Its public GitHub repository is `jiaqi-Sun2020/codex-skill-hub`.
- `README.md` and `README.en.md` are the Chinese and English human-facing entrypoints. They must explain the eight Skills whose canonical source is stored in this repository in detail, while external S Paper Skills and PaperTrace Skills receive only a concise overview and canonical links.
- README acknowledgements must identify confirmed open-source Skill influences with the author or maintainer, project link, scope of influence, and license when known. Do not infer unrecorded provenance.
- Confirmed Skill influences currently include `nature-figure`, `scipilot-figure-skill`, and KKKKhazix's `neat-freak`; preserve these acknowledgements in both root READMEs.
- Original or otherwise relicensable hub content is published under the permissive MIT License. Third-party license, copyright, and notice obligations remain in force and are not overridden by the root license.
- The hub directly maintains the six core utility skills under `50-core-utils/`, `academic-figure-workflow` under `10-paper-build/`, and `logic-chain-tutor` under `90-personal/`.
- `50-core-utils/skill-registry` is integrated version-management infrastructure inside the hub, not a separate GitHub repository and not one of the direct active skills.
- The registry's central `reader-learner` `1.0.0` release is retained as historical reproducibility material. PaperTrace owns its current project-specific `reader-learner` fork because that implementation depends on PaperTrace chat-profile integration and reader-v3 recovery behavior.
- Project-owned skills remain in their canonical projects and are linked from the hub; do not copy them into this repository merely for publication.
- `S_paper_skills/util_skills/project-agent-generator-skill` is retired. The canonical implementation is `50-core-utils/project-agent-generator-skill`.
- The retired `skill-audit-refactor` and `training-code-architecture-skill` copies under `S_paper_skills/util_skills/` are also removed in favor of their canonical hub sources.
- `research-workspace-governance` owns research-workspace architecture, evidence traceability, artifact-lifecycle policy, and typed equivalence declarations. It validates declaration shape, evidence metadata, invalidation drift, and allowed inferences but does not perform scientific comparison.
- `research-project-pipeline` orchestrates governance, project-Agent generation, knowledge/bootstrap audit, and adversarial verification without absorbing component ownership. It can discover nested execution roots and validate a supplied policy topology but must not infer mandatory prose or scientific equivalence.
- Mandatory-policy topology binds canonical policy files and SHA-256 hashes to each applicable execution root through an explicit reference, verified loader evidence, or owner-approved isolation. An isolation remains conditional; it is not evidence of policy reachability.
- Equivalence records distinguish `matrix_exact`, `matrix_global_phase`, `observational_protocol`, and `metric_only`. A weaker relation must never be promoted to a stronger claim without new domain evidence.
- `academic-figure-workflow` remains a central paper-building skill and does not receive a separate project-level `.agents/` bundle.
- Personal skill source lives directly under `90-personal/`; `logic-chain-tutor` is maintained there as a single canonical source.
- `project-agent-generator-skill` initializes or preserves project-local `.agents/memory/` by default; `--without-project-knowledge` is an explicit opt-out.
- `.agents/AGENTS.md` is the single project Agent entrypoint. Trusted project-local `.codex/` hooks load it on startup, resume, clear, compact, and subagent start.
- `project-agent-generator-skill` owns bootstrap generation and safe repair; `neat-freak bootstrap-audit` independently verifies the loading contract and, when supplied, the reviewed policy topology.
- `neat-freak` is the canonical audit and reconciliation workflow for project knowledge. Durable topic changes use its hash-bound `plan` / `apply` flow.

### Publication contract

- Before publishing, validate all JSON, scan tracked files for secrets and machine-specific paths, and run the relevant skill tests or validators.
- Compare every linked project against its fetched upstream immediately before committing; never force-push.
- Keep generated backups, local inbox material, shortcut files, caches, credentials, and private environment files out of the public repository.
- Preserve the independent registry history when integrating it into the hub, and retain a recoverable local backup until the remote push is verified.

### Evidence

- `README.md`
- `README.en.md`
- `LICENSE`
- `.gitignore`
- `.agents/DECISIONS.md`
- `50-core-utils/skill-registry/README.md`
- `50-core-utils/skill-registry/MIGRATION_AUDIT.md`
- `50-core-utils/research-workspace-governance/SKILL.md`
- `50-core-utils/research-workspace-governance/references/equivalence-contract.md`
- `50-core-utils/research-workspace-governance/scripts/validate_equivalence_records.py`
- `50-core-utils/research-project-pipeline/SKILL.md`
- `50-core-utils/research-project-pipeline/references/policy-topology.md`
- `50-core-utils/project-agent-generator-skill/SKILL.md`
- `50-core-utils/neat-freak/SKILL.md`
- `10-paper-build/academic-figure-workflow/SKILL.md`
- `10-paper-build/academic-figure-workflow/references/publisher-visual-source-map.md`
- `90-personal/logic-chain-tutor/SKILL.md`
