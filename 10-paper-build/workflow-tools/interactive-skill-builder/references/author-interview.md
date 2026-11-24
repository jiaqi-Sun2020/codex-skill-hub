# Author Interview

Use this question bank before creating or updating a skill. Ask at most three questions per round; do not dump the full list on the author.

## Essential Questions

Start with these when the request is underspecified:

1. What exact task should this skill make Codex better at?
2. What should trigger the skill? Give 2-3 example user requests.
3. Where should the skill be created or updated?

## Scope Questions

Ask when the skill boundary is unclear:

- What should the skill explicitly not do?
- Is this a single workflow, several modes in one domain, or a bundle of related tools?
- Should this be a new skill, an update to an existing skill, or a reference inside another skill?
- Who is the future user: you, another Codex session, a team, or a public audience?

## Workflow Questions

Ask when the sequence matters:

- What are the required steps before the skill acts?
- Where should the skill ask for confirmation?
- What decisions can Codex infer, and what decisions must always be approved by the author?
- Are there risky actions such as deleting files, overwriting outputs, sending messages, spending money, or using network access?

## Resource Questions

Ask when reusable materials may be needed:

- Does the skill need scripts for deterministic operations?
- Does it need reference files for detailed policies, schemas, templates, examples, or domain rules?
- Does it need assets such as boilerplate projects, document templates, images, fonts, or prompt templates?
- Are there existing local files or skills to borrow from?

## Output Questions

Ask when the final artifact is unclear:

- What files should the skill create?
- What should the final response include?
- What validation must run before completion?
- What should happen if validation fails?

## Interview Rules

- Ask questions in the author's language when practical.
- Ask the fewest questions needed to reduce design risk.
- Infer routine defaults from local conventions, but state those assumptions in the specification.
- Prefer concrete examples over abstract preferences.
- Stop interviewing once the skill specification can be written and audited.
