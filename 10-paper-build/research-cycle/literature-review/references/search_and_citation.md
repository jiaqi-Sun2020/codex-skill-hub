# Search and citation boundaries

Search with available tools or manual exports. Record source, query, date,
filters, returned/exported counts, caps and errors. Citation chaining is a
supplementary discovery method: record seed papers and apply the same criteria.
Web excerpts and generated summaries never establish full-text assessment.

## Optional DOI registration checks

Run from this Skill directory, after approved network access:

```powershell
python -X utf8 -B .\scripts\verify_citations.py "path\to\review.md"
python -X utf8 -B .\scripts\verify_citations.py "path\to\review.md" --output "path\to\new_report.json"
```

No automatic report file is created. Outputs reject existing files and linked
paths. Optional --email is an explicitly supplied contact, not a discovered secret.
The helper checks Handle registration and Crossref metadata identity. Requests
transmit DOI identifiers, not the manuscript body. No API credentials are needed.

Read verified as **registration confirmed**, failed as **unresolved**, and
metadata_unavailable as **manual follow-up needed**. No DOI produces an
incomplete result, not proof non-DOI references are invalid. Missing dependency,
timeouts, throttling and unavailable metadata require manual work, not reference
deletion. The helper does not check source truth, claim support or retractions.
Each `citation_checks` entry separates registration, retrieved metadata and DOI
identity from `metadata_match_state`, `claim_support_state`, `retraction_state`
and `scientific_quality_state`. Those last four remain `unassessed`: retrieving
matching DOI metadata is not comparing a citation's title/authors/version against
the intended source. Preserve the legacy `verified` list as registration only.

DOI extraction is heuristic, especially punctuation and old parenthesized suffixes.
Verify citation identity against the original document. Locate the actual passage
supporting the statement and record its version; inspect corrections/retractions
where available. A valid identifier can point to an irrelevant or contradicted work.

Sources: [Handle API](https://www.handle.net/proxy_servlet.html),
[Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/).

## Manuscript references

Preserve existing keys in the active .bib; do not create a second bibliography
from a metadata preview. Use complete verified metadata and actual venue rules;
[citation_styles.md](citation_styles.md) contains illustrative examples only.
The LaTeX Skill owns assembly and rendering. Successful compilation does not
establish that a citation supports a scientific claim.
