# The Prestige Paradox

**Institutional Bibliometric Status and Cybersecurity Media Salience in Global Higher Education, 2020-2024**

**Author:** Shreyansh Chaudhary  
**Student ID:** 001487390  
**Programme:** MSc Business Analytics  
**Institution:** University of Greenwich  
**Module:** BUSI 1783 - Business Analytics Project  
**Supervisor:** Dr Raunak Mishra  
**Submission:** August 2026

---

## Overview

This repository holds the dataset and analytical code for my MSc Business Analytics dissertation. The study asks whether a *prestige paradox* exists in global cybersecurity news coverage of universities: do research-heavy institutions, measured by bibliometric citation counts, appear in cybersecurity journalism more often than research-light ones?

A dataset of 741 universities across 67 countries was built from 552,860 raw GDELT rows and merged with OpenAlex bibliometric data. A Negative Binomial regression models the relationship between institutional prestige and cybersecurity media salience over 2020-2024.

**Headline result:** each one-unit increase in log-transformed citation count is associated with 20.7% more cybersecurity media mentions (IRR = 1.207, 95% CI: 1.185-1.230, p < 0.0001), controlling for country fixed effects.

**What the outcome actually measures.** The dependent variable is cybersecurity media *salience* - how often an institution shows up in cybersecurity-themed articles - not confirmed attack victimisation. GDELT's V2Themes tags are document-level, so a university quoted as an expert source counts the same as one that was breached. This distinction is maintained throughout the analysis.

---

## Key Findings

- **Prestige predicts salience.** The citation effect is positive, highly significant, and stable across four converging optimisers (BFGS, L-BFGS, Powell, Conjugate Gradient).
- **Not a perfect rank-ordering.** Oxford leads on mentions (155) despite not holding the top citation count; Harvard has the highest citations in the sample but ranks 9th on mentions. The effect is probabilistic, consistent with a Matthew-effect continuum rather than a clean elite/non-elite split.
- **Geographically concentrated.** The US contributes 385 of 741 universities (51.9%), partly reflecting GDELT's English-language media bias. No individual country dummy is statistically significant.
- **Honestly bounded.** The 3+ minimum-frequency filter left-truncates the sample, so the headline IRR most plausibly overstates the true population effect. The robustness check adding research volume fails to converge because of near-perfect collinearity (r = 0.985), leaving the impact-vs-volume question genuinely unresolved.

---

## Repository Contents

| File | Description |
|------|-------------|
| `analysis_main.ipynb` | Produces Figures [FILL IN: the 9 figure numbers]. Core pipeline: GDELT extraction, cleaning, OpenAlex merge, Negative Binomial regression, and main visualisations. |
| `analysis_supplementary.ipynb` | Produces Figures [FILL IN: the 2 figure numbers]. [FILL IN: one-line reason they are separate, e.g. "generated from a separate dataframe"]. |
| `gdelt_extraction.sql` | BigQuery extraction query for the GDELT GKG pull. |
| `gdelt_cleaned_dataset.csv` | Cleaned GDELT event dataset (pre-merge). |
| `prestige_paradox_dataset_741.csv` | Final 741-university analytical dataset used for every reported result. |
| `requirements.txt` | Python package dependencies. |
| `README.md` | This file. |

---

## Final Dataset Variables

`prestige_paradox_dataset_741.csv`

| Column | Description |
|--------|-------------|
| `the_official_name` | Institution name as matched in OpenAlex |
| `gdelt_name` | Original GDELT name(s) merged into this record (`;`-separated) |
| `cyber_news_count` | GDELT cybersecurity media mentions, 2020-2024 (dependent variable) |
| `cited_by_count` | Cumulative OpenAlex citation count (raw) |
| `works_count` | Total published works indexed in OpenAlex |
| `log_cited_by_count` | log(cited_by_count + 1) - primary independent variable |
| `log_works_count` | log(works_count + 1) |
| `country` | ISO two-letter country code |
| `match_score` | Fuzzy match score against OpenAlex (>= 90) |
| `prestige_tier` | Elite / High / Medium / Low, by cited_by_count thresholds |

---

## Method in Brief

1. **GDELT BigQuery extraction** - `gdelt-bq.gdeltv2.gkg_partitioned`, 1 Jan 2020 - 31 Dec 2024, filtered for HEI and cybersecurity keywords (552,860 rows).
2. **Eight-stage pipeline** - raw extraction > noise removal > HEI keyword filter > cyber URL filter > URL deduplication > 7-day event-window deduplication > 3+ minimum-frequency filter (11,903 records across 1,280 names) > OpenAlex fuzzy merge at threshold 90/100 (final 741 universities).
3. **OpenAlex merge detail** - an earlier threshold of 80 produced false merges (notably the *He University* collapse of unrelated name-fragments), caught by manual validation and removed before finalising the 741-university dataset.
4. **Modelling** - Negative Binomial regression (overdispersion ratio = 22.81 rules out Poisson), with 20 country dummies and log-citation count as the primary predictor.
5. **Robustness** - five-optimiser stability check plus a collinearity-affected specification adding `log_works_count`.

---

## Why 741 and Not 742

The pre-merge file had 742 rows. Manual validation identified one false merge - seven unrelated GDELT name-fragments collapsed onto a single OpenAlex record (*He University*), attributing 32 spurious events to it. Removing it gives the analytical N = 741.

---

## Reconciling 11,903 vs 10,265 Events

11,903 is the cleaned event count across all 1,280 pre-merge names. The final dataset holds 10,265 events, keeping only the 741 universities that matched to OpenAlex. The difference belongs to the 300 unmatched names and the removed *He University* merge.

---

## Data Sources

**GDELT 2.0 Global Knowledge Graph** - Google BigQuery (`gdelt-bq.gdeltv2.gkg_partitioned`), 2020-2024, accessed June 2025, open research use. <https://www.gdeltproject.org>

**OpenAlex** - REST API (<https://api.openalex.org/institutions>); variables: `cited_by_count`, `works_count`, `country_code`, institution type. CC0 licence, accessed June 2025. <https://openalex.org>

---

## Environment

Python 3. Required packages:

```bash
pip install pandas numpy statsmodels thefuzz requests matplotlib seaborn scipy google-cloud-bigquery
```

---

## Known Limitations

- **Left-truncation bias** - the 3+ frequency filter admits only media-visible universities, so the estimated prestige gradient likely overstates the population effect.
- **300 unmatched universities (23.4%)** excluded at the merge stage; direction of the resulting bias cannot be verified from the available data.
- **GDELT English-language bias** - non-Anglophone institutions are under-represented.
- **Cumulative citations** - `cited_by_count` is all-time as of June 2025, not bounded to 2020-2024.
- **Cross-sectional design** - no causal direction can be established.
- **Pseudo R2 = 0.075** - prestige and country explain roughly 7.5% of deviance.

---

## Citation

Chaudhary, S. (2026) *The Prestige Paradox: Institutional Bibliometric Status and Cybersecurity Media Salience in Global Higher Education, 2020-2024.* MSc Dissertation, University of Greenwich, BUSI 1783.

---

## Licence

Shared for academic assessment under University of Greenwich BUSI 1783 module requirements. Data derived from GDELT (open research use) and OpenAlex (CC0). All original analytical code is the work of the author.
