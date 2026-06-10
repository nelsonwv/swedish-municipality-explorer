# Data Contract — MARTS Schema

## Schema

`OPPORTUNITY_INDEX.MARTS`

## Purpose

Final, dashboard-ready tables consumed directly by the Streamlit app. This
is the only schema Agent 4 (Dashboard) should query.

## Tables

- `dim_municipality`
- `fct_opportunity_scores`

## `dim_municipality`

One row per municipality per snapshot year.

| Column | Type | Description |
|---|---|---|
| `municipality_code` | VARCHAR | 4-digit SCB municipality code (primary key with `year`) |
| `municipality_name` | VARCHAR | Municipality name |
| `county_name` | VARCHAR | County (län) name, derived from `county_code` |
| `population_category` | VARCHAR | One of `'small'`, `'medium'`, `'large'`, based on `population_total` tertiles/thresholds |
| `year` | INTEGER | Snapshot year (`2021`) |

## `fct_opportunity_scores`

One row per `(municipality_code, region_of_birth, year)`. Scores are
normalized 0–100 across all municipalities for comparability.

| Column | Type | Description |
|---|---|---|
| `municipality_code` | VARCHAR | 4-digit SCB municipality code (foreign key to `dim_municipality`) |
| `region_of_birth` | VARCHAR | One of `'total'`, `'born_in_sweden'`, `'born_abroad'` — drives the dashboard filter |
| `income_score` | FLOAT | Normalized (0–100) median income score |
| `employment_score` | FLOAT | Normalized (0–100) employment rate score |
| `education_score` | FLOAT | Normalized (0–100) post-secondary education score |
| `mobility_score` | FLOAT | Normalized (0–100) commuting/mobility score |
| `year` | INTEGER | Snapshot year (`2021`) |

## Notes

- The overall **Opportunity Index** displayed on the dashboard is computed
  as a combination of `income_score`, `employment_score`,
  `education_score`, and `mobility_score`. Whether this combination is
  precomputed as an additional column or calculated in the dashboard layer
  is decided by Agent 3/Agent 4 and should be documented in their status
  logs.
- Normalization method (e.g. min-max scaling across municipalities) should
  be documented by Agent 3 in `docs/agents/agent3_dbt.md`.

## Read / Write Access

| Schema | Written By | Read By |
|---|---|---|
| `MARTS` | Agent 3 (dbt — mart models) | Agent 4 (Streamlit dashboard) |
