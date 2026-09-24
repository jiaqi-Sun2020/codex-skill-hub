# Chinese-To-English Translation Workflow

Do not translate Chinese scientific prose clause by clause. First recover the argument, then write English prose that serves the target venue. Prefer paragraph-level academic argumentation over short, compressed literal sentences.

Encoding rule: read Chinese source, LaTeX source, and terminology ledgers as UTF-8 by default. On Windows, set `PYTHONUTF8=1` for Python-based extraction or validation so Chinese text is not decoded as GBK.

## Pass 1: Proposition Extraction

For each paragraph, identify:

- the core claim;
- the evidence or equation supporting it;
- the contrast with prior work or baseline;
- the boundary, limitation, or TODO;
- terms that must enter the terminology ledger.

## Pass 2: Logic Reconstruction

Chinese academic drafts often leave links implicit. Rebuild only the links that are already supported by the source:

- contrast: however, by contrast, whereas;
- cause or mechanism: because, this reflects, this arises from;
- consequence: therefore, as a result, this enables;
- boundary: under this condition, within this parameter regime, for the tested cases.

Do not add a new premise to make a paragraph sound smoother.

## Pass 2.5: Paragraph Argumentation

When a Chinese paragraph carries a hidden argumentative chain, rewrite it as a coherent English paragraph rather than a sequence of short translated sentences. Preserve the source logic, but make the progression readable:

- scene or phenomenon;
- cause or operational mechanism;
- resulting data form or modeling condition;
- task reformulation;
- model requirement.

For example, traffic-sensing prose should read as a problem reformulation chain: real deployment scenario -> sensor/communication/roadwork missingness -> sparse uneven observation records -> forecasting is no longer regular graph-signal prediction -> models must capture spatiotemporal patterns from irregular valid records.

Use richer academic phrasing when it stays faithful, such as `real urban traffic sensing scenarios`, `communication breakdowns`, `sparse sequences with uneven gaps between valid records`, `cannot be reduced to`, `is better viewed as`, and `capture spatial and temporal dependency patterns`.

Avoid semantic drift from over-explanation:

- Do not turn `originally sampled at fixed intervals` into `should have been sampled` unless the source implies an obligation.
- Do not turn variable or uncertain valid observation positions into `unknown timestamps` unless the model truly lacks timestamp information.
- Do not turn `missing observations` into missing ground-truth values if the source only means missing historical inputs.
- Do not add new task categories, statistical claims, or causal mechanisms.


## Pass 3: Venue Rewrite

- For Nature, broaden the opening frame and reduce specialist density.
- For PRL, compress toward one result and one evidence chain.
- For PRA, keep the mathematical and procedural details needed for trust.

## Pass 4: Sentence Polish

- Use direct subject-verb sentences where possible.
- Split comma-linked chains into smaller sentences.
- Keep technical terms stable rather than using synonyms.
- Match hedge strength to evidence strength.
- Avoid rhetorical flourishes that are not supported by the results.