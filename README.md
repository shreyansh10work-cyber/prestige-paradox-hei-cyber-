# The Prestige Paradox: Institutional Bibliometric Status and Cybersecurity Media Salience in Global Higher Education, 2020–2024

**Author:** Shreyansh Chaudhary
**Programme:** MSc Business Analytics  
**Institution:** University of Greenwich  
**Module:** BUSI 1783 — Business Analytics Project  
**Supervisor:** Dr. Raunak Mishra  
**Submission Date:** August 2026  

---

## Project Overview

This repository contains the dataset and analytical notebook for my MSc Business Analytics 
dissertation. The study investigates whether a 'prestige paradox' exists in global 
cybersecurity media coverage of higher education institutions — specifically, whether 
research-heavy universities measured by bibliometric citation counts receive 
disproportionately higher cybersecurity news coverage than research-light institutions.

A novel dataset of 741 universities across 30 countries was constructed from 552,860 raw 
GDELT rows and merged with OpenAlex bibliometric data. Negative Binomial regression 
was used to model the relationship between institutional prestige and cybersecurity media 
salience between 2020 and 2024.

**Primary Finding:** Each one-unit increase in log-transformed citation count is associated 
with 20.7% more cybersecurity media mentions (IRR = 1.207, 95% CI: 1.185–1.230, 
p < 0.0001), controlling for country fixed effects.

---

## Data Sources

**GDELT 2.0 Global Knowledge Graph (GKG)**  
- Source: Google BigQuery — `gdelt-bq.gdeltv2.gkg_partitioned`  
- Query period: 1 January 2020 to 31 December 2024  
- Access date: June 2025  
- Licence: Open research use  
- Raw extraction: 552,860 rows filtered for HEI keywords and cybersecurity themes  
- After seven-stage cleaning pipeline: 11,903 records across 1,280 unique university names  
- URL: https://www.gdeltproject.org  

**OpenAlex Bibliometric Database**  
- Source: OpenAlex REST API — `https://api.openalex.org/institutions`  
- Variables used: cited_by_count, works_count, country_code, institution type  
- Licence: CC0 (fully open)  
- Access date: June 2025  
- URL: https://openalex.org  

---

## Repository Contents

| File | Description |
|---|---|
| `prestige_paradox_dataset_741.csv` | Final merged analytical dataset. 741 universities across 30 countries with cybersecurity media mention counts and OpenAlex bibliometric variables. |
| `prestige_paradox_analysis.ipynb` | Compiled Python notebook containing the full analytical pipeline: data cleaning, OpenAlex fuzzy matching, descriptive statistics, Negative Binomial regression, optimiser stability checks, robustness specification, and all figures. All cells have been executed and outputs are visible. |
| `README.md` | This file. |

---

## Dataset Variables

| Variable | Description |
|---|---|
| `university_name` | Cleaned institution name as matched to OpenAlex |
| `country_code` | ISO two-letter country code |
| `cyber_news_count` | Total GDELT cybersecurity media mentions, 2020–2024 (dependent variable) |
| `cited_by_count` | Cumulative OpenAlex citation count (raw) |
| `log_cited_by_count` | Log-transformed citation count — primary independent variable |
| `works_count` | Total published works indexed in OpenAlex |
| `log_works_count` | Log-transformed works count |
| `prestige_tier` | Categorical tier: Elite / High / Medium / Low based on cited_by_count thresholds |

---

## Analytical Pipeline Summary

The notebook covers the following stages in order:

1. GDELT data import and noise removal
2. HEI keyword filtering
3. Cybersecurity URL filtering
4. URL deduplication
5. Seven-day event window deduplication
6. Minimum frequency filter (3+ mentions)
7. OpenAlex API querying and fuzzy string matching at threshold 90/100
8. Descriptive statistics and visualisations
9. Prestige tier analysis
10. Negative Binomial regression — primary model (BFGS optimiser)
11. Optimiser stability check across four algorithms
12. Robustness specification including log_works_count

---

## Key Results

| Model | Converged | Coefficient | IRR | p-value |
|---|---|---|---|---|
| Primary (BFGS) | Yes | 0.1882 | 1.207 | < 0.0001 |
| L-BFGS | Yes | 0.1883 | 1.207 | < 0.0001 |
| Powell | Yes | 0.1883 | 1.207 | < 0.0001 |
| Conjugate Gradient | Yes | 0.1882 | 1.207 | < 0.0001 |
| Nelder-Mead | No | 0.1928 | 1.213 | < 0.0001 |

Dispersion parameter alpha = 0.4719 (p < 0.0001), confirming Negative Binomial over Poisson.  
Pseudo R² = 0.0750. N = 741 universities.

---

## Python Environment

The notebook was developed in Python 3. The following libraries are required:
- pandas
- numpy
- statsmodels
- thefuzz
- requests
- matplotlib
- seaborn
- google-cloud-bigquery
