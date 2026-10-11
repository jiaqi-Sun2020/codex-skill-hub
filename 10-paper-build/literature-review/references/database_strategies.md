# Domain-appropriate discovery

This adapted reference deliberately does not freeze service quotas or require
new providers. Consult current official documentation before API calls. Use
interfaces/access already available or manual exports; never install/authenticate
a new service as an implicit part of a review.

## Query contract

Define the question and review type, concept/synonym groups, eligibility, and
required evidence depth. Translate operators to each chosen platform. Record
actual query, source/interface, search date, filters/date field, raw page/export
IDs, provider total, retrieved count, pagination, caps and failure status.
A first page or ranked sample is not a complete corpus. Stop at resource/access
bounds and disclose the unassessed remainder. Choose complementary sources for
systematic work; a fixed number of databases cannot guarantee completeness.

## Source options (conditional, not mandatory)

- Biomedical: [PubMed](https://pubmed.ncbi.nlm.nih.gov/advanced/) and
  [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/).
  PubMed records and PMC full-text access differ. Entity databases are not
  bibliographic indexes simply because they list references.
- Preprints: [arXiv API](https://info.arxiv.org/help/api/user-manual.html) and
  [bioRxiv/medRxiv API](https://api.biorxiv.org/). Retain versions and published
  links. Date-range metadata is not an arbitrary keyword-search API.
- Cross-domain: [Semantic Scholar](https://api.semanticscholar.org/api-docs/graph),
  [OpenAlex](https://docs.openalex.org/), institutionally available indexes,
  and relevant primary archives. Respect current access and pagination contracts.
- Citation chaining: reference lists and citation interfaces; ranked Google
  Scholar results are supplementary and do not promise bulk/API completeness.
- DOI identity: [Crossref](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)
  singleton metadata is not literature-search completeness or claim verification.

## Local record processing

Give search_databases.py a normalized JSON array, not a provider envelope:

```json
[{"title":"Illustrative record","authors":"Author, A.","year":null,
  "source":"owner-provided export","doi":null,"record_id":"R1"}]
```

Preserve provider IDs, source/search/date, versions and raw exports. The script
can filter and order the imported sample; unknown years remain pending. Duplicate
groups retain source indices and original records. A matching title/DOI is not a
study ID, and first occurrence is not the authoritative publication version.
Ranking and citation counts are not eligibility or evidence-quality judgments.
BibTeX output is a preview, not an automatic overwrite of manuscript citations.
