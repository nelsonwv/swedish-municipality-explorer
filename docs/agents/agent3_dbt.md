# Agent 3 — dbt Transformations

## Role

Builds the dbt Core models that transform `RAW` data into the `STAGING`,
`INTERMEDIATE`, and `MARTS` schemas, implementing the cleaning logic,
joins, and normalized scoring used by the Municipality Opportunity Index.

## Inputs Required Before Starting

- `docs/contracts/data_contract_raw.md`,
  `docs/contracts/data_contract_staging.md`,
  `docs/contracts/data_contract_intermediate.md`, and
  `docs/contracts/data_contract_marts.md`.
- Populated `RAW` tables from Agent 2
  (`raw_population`, `raw_income`, `raw_employment`, `raw_education`,
  `raw_commuting`).
- Initialized dbt project under `dbt_project/` with a working
  `~/.dbt/profiles.yml` Snowflake connection (set up by Agent 1).

## Outputs

- dbt staging models producing:
  - `stg_population`, `stg_income`, `stg_employment`, `stg_education`,
    `stg_commuting` in `STAGING`.
- dbt intermediate models producing:
  - `int_municipality_profiles` in `INTERMEDIATE`.
- dbt mart models producing:
  - `dim_municipality` and `fct_opportunity_scores` in `MARTS`.
- All models conform to the column structures defined in
  `docs/contracts/data_contract_staging.md`,
  `docs/contracts/data_contract_intermediate.md`, and
  `docs/contracts/data_contract_marts.md`.
- Documentation of normalization method (for `*_score` columns) and
  handling of missing/suppressed values, recorded in this status log.
- Updated status log in this file.

## Constraints

- Do NOT write Python ingestion logic — that is Agent 2's responsibility.
- Do NOT write Streamlit code.
- Do NOT modify `RAW` tables — staging models should only `SELECT` from
  them.
- Do NOT change the agreed contracts for `STAGING`, `INTERMEDIATE`, or
  `MARTS` without updating the corresponding contract file and noting the
  change in this log.

## Status Log

<!-- Append updates below as work progresses -->
