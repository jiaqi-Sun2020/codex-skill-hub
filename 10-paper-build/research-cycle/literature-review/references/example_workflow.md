# Bounded example: qualitative research context

This is an illustrative recipe, not an executed review or empirical finding.
Suppose the user supplies four interview-method reports for a narrative comparison.

1. Record the supplied set, question, versions and source sections available.
   Do not claim systematic coverage or invent search counts.
2. Use literature-triage-matrix to compare methods and transferability with the
   user's requested columns. Abstract-only claims remain provisional; locate
   full-text passages for consequential claims or mark them unassessed.
3. Link two reports from the same participant cohort to one study. Compare
   rival interpretations and retain negative evidence, not four independent votes.
4. If synthesis is requested, write literature_review.md by question/theme and
   keep search/material limits and appraisal in review_protocol.md. No seeds,
   model training, p-values, PRISMA chart or new experiment is forced.
5. Reopen candidate questions in research-logic. Evidence design can propose
   a discriminating interview strategy; it does not execute participant research.
6. Verify references manually; optional DOI checks need approved public network
   access. Return to the author for scientific interpretation and manuscript use.

For exported records, run from this Skill directory (input must already exist):

```powershell
python -X utf8 -B .\scripts\search_databases.py "path\to\records.json" --deduplicate --format json --summary
```

No output file or paid service is needed. Existing artifacts are reused, and
replacement requires approval. See [core_workflow.md](core_workflow.md) for
systematic/scoping adaptations rather than applying that extra ceremony here.
