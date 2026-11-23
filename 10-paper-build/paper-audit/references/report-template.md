# Single mock-review report

Locally adapted on 2026-10-28 from the MIT and Apache-2.0 sources listed in
[LICENSE](../LICENSE). This report shape replaces their multi-file, fixed-panel
and ledger outputs; it does not grant writing permission.

Local content update 2026-11-13: made dependency, figure and bilingual
findings actionable within the existing single-report and stable-ID contract.

Use one report per invocation, inline by default. Include only applicable parts;
do not create empty matrices, supplementary ledgers or separate lens reports.
Write in the user's language and clearly label any illustrative rewrite.

## 1. Review setup and coverage

- Initial whole-manuscript review or revision re-review.
- Manuscript identity and version; prior report/version for re-review.
- Actually read sections, figures, supplied language versions and supplement;
  inaccessible or unreliable content, including extraction problems. For visual
  findings, identify whether the final PDF layout was inspected and any applicable
  author-selected benchmark; a source-image preview alone is not that check.
- Source/evidence boundary, applicable venue criteria or venue fit unchecked.
- Same-agent review passes; any separately authorized isolation and its limits.
- Relevant external checks actually completed, unchecked or failed.

A completed limited report is not a completed whole-manuscript pre-review.

## 2. Work summary and strengths

Briefly reconstruct the actual support relations, not just a list of question,
method and result. In a few sentences or a short arrow chain, explain why this
question matters in the manuscript -> how the method addresses it -> what the
evidence supports -> where the conclusion stops. Mark a missing link as missing,
rather than completing the authors' argument; no full matrix is required.
Distinguish "the authors report" from independent verification. State concrete
strengths only where supported; do not invent compliments to balance concerns.

## 3. Major Concerns / 4. Minor Comments

For each substantive concern:

- **ID:** PA-001 (stable across rounds and severity changes).
- **Location and evidence:** faithful section, page, formula, algorithm line,
  figure/table or quotation, with an inspectable source and what it establishes.
  Mark missing anchors. Anchor a first-use concern to both use and definition,
  a figure/text mismatch to both representations, and a bilingual discrepancy to
  both passages. When using a reviewer comment, keep the exact quotation
  separate from your interpretation; group verified associated markup without
  counting linked popups as further issues.
- **Reader's question:** explain plainly what the reader cannot determine or what
  appears contradictory, such as "Are these the same learned weights?" Avoid
  labels like "notation inconsistency" without saying which meanings conflict.
- **Finding:** distinguish confirmed error, definition ambiguity, insufficient
  evidence/provenance gap, suspected anomaly, local reading problem or an
  unassessable check. State the known fact and label any inference; a reviewer's
  question alone does not prove a defect.
- **Why it matters:** explain the consequence for understanding the method,
  judging the evidence or interpreting the claim. For logic/narrative concerns,
  name the broken relation, not merely "poor flow."
- **Severity / blocking:** major or minor; whether and why it blocks the central
  case, not whether it is easy to fix.
- **Minimum remedy and linked locations:** state the smallest adequate change
  and the other definitions, formulas, algorithms, captions or claims that must
  agree with it. Avoid a generic "clarify" or "unify notation." Preserve correct
  existing detail and state what can remain when that prevents an overbroad fix.
  For the author handoff, distinguish a **confirmed problem** from a **risk to verify** and an **optional suggestion**. A demonstrated counterexample that changes a conclusion needs a located correction or narrower claim, not just a note. For a possible counterexample, identify what is unknown and whether the present claim already depends on resolving it. Keep optional experiments in the report: say what they would distinguish and consider a smaller remedy first. Neither a suspected objection nor an optional extension is a required manuscript disclaimer or permission to edit.
- **Closure condition:** specify observable revised text, definitions or supplied
  evidence that would resolve the issue, including the linked locations. A claim
  that something was fixed is not enough.
- **Counter-review:** decisive reasonable rebuttal and its disposition when
  material; avoid displaying unnecessary debate for minor corrections.

Keep these elements concise; closely related ones may share a sentence or table
cell. For a practical findings list, prefer columns for location/evidence, reader
question, impact, minimum remedy with linked locations, and completion condition;
retain the finding category and severity where relevant. Do not add empty rows.
The report should be usable without technical review jargon. If a short
illustrative rewrite is needed, label it as a suggestion and do not invent missing
scientific facts or expand the report into a rewritten manuscript.

If no grounded concern exists at a level, say so without filling a quota.
One root problem gets one stable ID even when it affects several sections or
both support and readability; list the affected locations together. Merged issues
retain predecessor IDs; important withdrawn criticisms retain their reason.
Do not invent exact page/line positions or hide a material conflict.

## 5. Mock recommendation and author priorities

Give a reasoned mock recommendation: simulated accept, minor revision, major
revision, reject or insufficient basis to judge. Tie it to this version, visible
evidence and the remaining concerns. Do not force a verdict when the central
case cannot be assessed. This is not an actual editorial decision, acceptance
probability, science certification or a prediction of venue fit.

Prioritize the smallest changes that affect the judgment; list decisions or
materials that require the author. Explicitly separate:
- report completion and whole-manuscript coverage;
- support for the central claims and unresolved uncertainty;
- author approval/risk disposition, if actually supplied;
- permission for the next action, if actually supplied.

No single PASS substitutes for these judgments. Stop at author review.

## Revision re-review addition

In this same report, give each prior ID's current status:
**resolved / partly resolved / unresolved / needs verification / withdrawn**.
Cite the current text or evidence satisfying (or failing) its closure condition,
the old report source, and any new dependent concern. A reply saying "fixed" is
not a closure artifact. Preserve history without overwriting an old report.

If the old report/version is missing, state which history and closures cannot be
verified; report current-draft findings without pretending they resolve old IDs.
Note unreviewed portions of a targeted re-review and the impact of substantive
changes. Carry forward only findings whose applicability was checked.

For paragraph moves or compression, apply the
[argument and readability checks](method-checks.md#argument-and-readability) to
the changed context: have premises, qualifiers or inferential dependencies been
lost, hidden or reassigned? Unchanged sentences alone do not prove unchanged
meaning. Identify the affected relation and re-review that part; a verified
purely expressive change reuses prior findings, not an automatic whole-paper
re-review.
