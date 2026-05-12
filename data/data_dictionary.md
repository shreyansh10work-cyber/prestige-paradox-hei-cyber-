# Data Dictionary – Merged Analysis Dataset

| Variable Name        | Description                                                  | Type    | Source              |
|----------------------|--------------------------------------------------------------|---------|---------------------|
| institution_name     | Standardised university name                                  | String  | GDELT / THE match   |
| country              | Country where the university is located                       | String  | THE Rankings        |
| region               | Geographic region (7 categories)                              | String  | Coded manually      |
| research_score       | THE Research pillar score (0–100)                             | Float   | THE Rankings 2024   |
| gdelt_event_count    | Number of deduplicated GDELT-reported cyberattack events (2020‑2024) | Integer | GDELT 2.0 Events   |
| binary_any_event     | 1 if gdelt_event_count > 0, else 0                            | Binary  | Computed            |
| high_research        | 1 if research_score > median, else 0                         | Binary  | Computed            |

## Notes
- Region categories: North America, Europe, Asia, Middle East and North Africa, Sub-Saharan Africa, Latin America, Oceania.
- Only institutions matched between GDELT and THE are included; unmatched cases are listed in the appendix of the dissertation.
