# Statistical Test Selection

Use the experiment design first, then the data distribution.

## Basic Routing

| Situation | Preferred analysis |
|---|---|
| Two independent groups, roughly normal | Welch t-test |
| Two independent groups, non-normal or small n | Mann-Whitney U |
| Two paired conditions | Paired t-test; Wilcoxon if non-normal or ordinal |
| More than two independent groups | One-way ANOVA; Kruskal-Wallis if assumptions fail |
| More than two paired/repeated conditions | Repeated-measures ANOVA; Friedman if assumptions fail |
| Categorical outcome | Chi-square; Fisher exact for small counts |
| Correlation, linear relation | Pearson correlation |
| Correlation, monotonic/non-normal | Spearman correlation |
| Continuous response with covariates | OLS / GLM |
| Binary response | Logistic regression |
| Repeated measures with grouped random effects | Mixed-effects model |

## Effect Sizes

- Two independent means: Cohen's d or Hedges g.
- Paired means: paired Cohen's d or mean paired difference with CI.
- Non-parametric two-group: rank-biserial correlation or Cliff's delta.
- ANOVA: eta squared or partial eta squared.
- Correlation: r with CI.
- Regression: coefficient, standard error, CI, and standardized coefficient when useful.

## Confidence Intervals

- Prefer bootstrap CI when distributional assumptions are unclear and sample size is adequate.
- Report CI level, usually 95%.
- For paired designs, compute CI on paired differences rather than independent group means.

## Multiple Comparisons

- If testing many metrics, datasets, or method pairs, apply Holm, Benjamini-Hochberg, or another justified correction.
- Report both raw p-values and corrected p-values when possible.

## Assumption Checks

Check and report only what matters for the selected analysis:

- Independence or pairing structure.
- Normality of residuals or paired differences when using parametric tests.
- Equal variance; use Welch tests by default for independent two-group means.
- Sample size per group.
- Outliers and missingness handling.

If assumptions are unclear, prefer robust/non-parametric tests and be explicit about limits.
