# Data Integrity Checklist

Use this checklist before turning analysis into paper claims.

## A. Provenance

- Identify every source file used.
- Confirm whether the file is raw data, generated data, cached output, or manually edited summary.
- Trace each metric to the script or pipeline that generated it when possible.
- Verify ground truth comes from the dataset, simulator specification, or labeled reference, not from model predictions unless explicitly labeled as proxy evaluation.

## B. Result Existence

- Check that every claimed number appears in an existing file.
- Check that metric keys and method names match exactly.
- Check row counts and filtering rules before extracting numbers.
- If a table aggregates multiple files, list all included files and exclusions.

## C. Metric Validity

- Confirm whether larger or smaller is better.
- Confirm units, scale, and normalization.
- Flag any metric normalized by the model's own maximum, minimum, or mean.
- Report raw values alongside normalized values when available.

## D. Scope

- Count datasets, tasks, scenes, seeds, folds, and runs.
- Compare actual scope with claim language such as comprehensive, robust, extensive, state-of-the-art, or general.
- If scope is narrow, downgrade claims to pilot, preliminary, case study, or simulation evidence.

## E. Leakage and Split Hygiene

- Check train/validation/test split boundaries.
- Check whether hyperparameters were selected on the test set.
- Check duplicate samples or near-duplicates across splits if identifiers exist.
- Check whether preprocessing statistics were fit only on training data.

## F. Audit Verdict

Use:

- `pass`: evidence is traceable and metrics are valid for the claim.
- `warn`: analysis is useful but has scope, assumption, or provenance limitations.
- `fail`: numbers are missing, ground truth is invalid, metrics are self-referential, or claims contradict the files.

Never hide a `warn` or `fail` verdict in prose. Put it near the claim.
