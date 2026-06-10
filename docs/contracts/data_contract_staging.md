# Data Contract — STAGING Schema

## Schema

`OPPORTUNITY_INDEX.STAGING`

## Purpose

Cleaned, typed, and standardized one-row-per-observation tables, one per
source dataset. Staging models rename SCB codes/labels into consistent
column names and types so that intermediate models can join across
datasets on `municipality_code`.

## Tables

- `stg_population`
- `stg_income`
- `stg_employment`
- `stg_education`
- `stg_commuting`

## Common Column Structure

| Column | Type | Description |
|---|---|---|
| `municipality_code` | VARCHAR | 4-digit SCB municipality code, e.g. `"0114"` |
| `municipality_name` | VARCHAR | Municipality name, e.g. `"Upplands Väsby"` |
| `year` | INTEGER | Snapshot year (`2021` for all rows) |
| `sex` | VARCHAR | One of `'total'`, `'men'`, `'women'`. Defaults to `'total'` for datasets without a sex breakdown |
| `region_of_birth` | VARCHAR | One of `'total'`, `'born_in_sweden'`, `'born_abroad'`. Defaults to `'total'` for datasets without a region-of-birth breakdown |
| `value` | FLOAT | The measure value for this dataset (see per-table description below) |

## Per-Table `value` Definitions

| Table | `value` represents |
|---|---|
| `stg_population` | Population count (number of people) |
| `stg_income` | Median income (SEK) |
| `stg_employment` | Employment rate (%) |
| `stg_education` | Share of population with post-secondary education (%) |
| `stg_commuting` | Out-commuting rate (%) — share of employed residents who work in a different municipality |

## Notes

- One row per `(municipality_code, sex, region_of_birth, year)` combination
  per table.
- Rows where the source value was suppressed/missing (`".."` in `RAW`)
  should be excluded or set to `NULL` in `value` — document the chosen
  approach in `docs/agents/agent3_dbt.md`.

## Read / Write Access

| Schema | Written By | Read By |
|---|---|---|
| `STAGING` | Agent 3 (dbt — staging models) | Agent 3 (dbt — intermediate models) |
