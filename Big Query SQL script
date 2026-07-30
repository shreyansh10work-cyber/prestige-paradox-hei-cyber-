-- ============================================================
-- The Prestige Paradox (BUSI 1783)
-- Data Source 1: GDELT 2.0 Global Knowledge Graph
-- Extraction of HEI cybersecurity media mentions, 2020-2024
-- Table: gdelt-bq.gdeltv2.gkg_partitioned
-- ============================================================

SELECT
  DATE,                    -- GKG timestamp (YYYYMMDDHHMMSS)
  DocumentIdentifier,      -- source article URL
  V2Organizations,         -- named organisations extracted from the article
  V2Themes,                -- thematic tags (used for cyber filtering)
  V2Locations,             -- geographic references
  V2Tone                   -- sentiment / tone vector
FROM
  `gdelt-bq.gdeltv2.gkg_partitioned`
WHERE
  -- Partition filter: 1 Jan 2020 - 31 Dec 2024
  _PARTITIONTIME BETWEEN TIMESTAMP('2020-01-01') AND TIMESTAMP('2024-12-31')

  -- HEI keyword filter on organisation names
  AND (
       LOWER(V2Organizations) LIKE '%university%'
    OR LOWER(V2Organizations) LIKE '%college%'
    OR LOWER(V2Organizations) LIKE '%polytechnic%'
  )

  -- Cybersecurity keyword filter on themes
  AND (
       LOWER(V2Themes) LIKE '%cyber%'
    OR LOWER(V2Themes) LIKE '%ransomware%'
    OR LOWER(V2Themes) LIKE '%data breach%'
    OR LOWER(V2Themes) LIKE '%hacking%'
    OR LOWER(V2Themes) LIKE '%infosecurity%'
  );
