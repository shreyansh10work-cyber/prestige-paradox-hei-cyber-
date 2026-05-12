# The Prestige Paradox: Media-Driven Distortion in Higher Education Cyber Threat Visibility

**Author:** [Shreyansh Chaudhary]  
**Student ID:** [001487390 ]  
**Programme:** MSc Business Analytics, University of Greenwich  
**Module:** BUSI1783 – Business Analytics Project  
**Supervisor:** [Dr Raunak Mishra]  

## Overview
This repository contains the complete code and data for the dissertation project investigating the "prestige paradox" in global media reporting of cyberattacks on universities. The study tests whether research-intensive institutions appear more frequently in GDELT‑captured cyber incident news than less research‑intensive ones, and how this pattern varies across geographic regions (2020‑2024).

## Data Sources
- **GDELT 2.0 Events** (Google BigQuery): Global news‑reported events filtered for cyberattacks on educational organisations.
- **Times Higher Education World University Rankings (2021‑2024)**: Research pillar scores for over 1,900 institutions.
- **No Kaggle datasets are used.**

## Repository Structure
- `data/` – Cleaned, merged dataset and data dictionary.
- `notebooks/` – Step‑by‑step analytical notebooks (extraction → modelling → robustness).
- `src/` – Reusable Python modules for querying and matching.
- `outputs/` – Final figures and formatted tables.
- `docs/` – Supplementary documentation.

## How to Reproduce
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Access GDELT via BigQuery (see `docs/gdelt_setup.md`).
4. Download THE rankings from [THE website](https://www.timeshighereducation.com).
5. Run notebooks 01 through 08 in order.

## Ethics
All data is publicly available and aggregated. No personal information is processed.

## License
This project is licensed under the MIT License.# prestige-paradox-hei-cyber-
