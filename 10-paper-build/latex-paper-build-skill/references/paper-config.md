# Paper Config Contract

Use this reference when creating or updating a paper pipeline that needs stable author, affiliation, correspondence, venue, abstract, keyword, funding, or acknowledgment metadata.

## File Name

Use a root-level `paper_config.json` file in every generated pipeline. Prefer JSON over YAML so the pipeline script can parse it with the Python standard library and no extra dependency.

## Required Shape

```json
{
  "schema_version": 1,
  "project_key": "qct-sparse-coin-tomography",
  "title": "Sparse-position quantum-walk coin-state tomography",
  "short_title": "Sparse QW Coin-State Tomography",
  "venue": "PRA",
  "language": "zh-CN",
  "date": "\\today",
  "authors": [
    {
      "name": "Author One",
      "affiliations": ["aff1"],
      "email": "corresponding.author@example.edu",
      "corresponding": true,
      "orcid": "TODO"
    }
  ],
  "affiliations": [
    {
      "id": "aff1",
      "name": "TODO: Department or Institute",
      "address": "TODO: University, City, Country"
    }
  ],
  "correspondence": {
    "name": "Author One",
    "email": "corresponding.author@example.edu",
    "address": "TODO: full correspondence address"
  },
  "keywords": ["quantum walk", "coin-state tomography"],
  "abstract": "TODO: Chinese author-review abstract.",
  "acknowledgments": "TODO: funding and acknowledgments"
}
```

## Rules

- Treat `paper_config.json` as the source of truth for title, authors, affiliations, correspondence email/address, keywords, and acknowledgments.
- Generate `frontmatter.tex` from the config when creating a new template pipeline.
- When scaffolding from an existing manuscript, preserve the manuscript body but regenerate `frontmatter.tex` from `paper_config.json` if the user provided or requested config-driven metadata.
- Keep private or uncertain information as `TODO` rather than inventing names, addresses, funding, or emails.
- Do not store secrets in `paper_config.json`; contact email and public affiliation are acceptable manuscript metadata.
- For APS/REVTeX output, map authors to repeated `\author`, optional `\email`, and `\affiliation` commands.
- For Chinese author-review manuscripts, keep title/abstract editable in Chinese while preserving PRL/PRA logic.

## Borrowed Writing-Workflow Principle

The external `research-writing-skill` pattern is useful as a staged-writing reminder: separate literature/context, outline, section drafting, polishing, figure/table captions, result interpretation, and reviewer simulation. In this skill, those stages become durable pipeline artifacts rather than chat-only prompts.