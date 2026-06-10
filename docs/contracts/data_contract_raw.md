# Data Contract — RAW Schema

## Schema

`OPPORTUNITY_INDEX.RAW`

## Purpose

Landing zone for data pulled directly from the SCB PxWebApi v2. Tables in
this schema mirror the structure of the SCB API responses as closely as
possible (codes, labels, and raw values), with minimal transformation.
Values are loaded as-is (e.g., as strings) so that no information is lost
before dbt staging models clean and type the data.

## Tables

- `raw_population`
- `raw_income`
- `raw_employment`
- `raw_education`
- `raw_commuting`

## Common Column Structure

Each `raw_*` table follows this common shape, reflecting the dimensions
returned by the corresponding SCB table (see `PROJECT_PLAN.md` for API
paths). Not every dataset uses every dimension column — Agent 2 should
populate the columns that apply to a given dataset and leave the rest
`NULL`, documenting any deviations in `docs/agents/agent2_ingestor.md`.

| Column | Type | Description |
|---|---|---|
| `region_code` | VARCHAR | SCB municipality (or county/national) region code, e.g. `"0114"` |
| `region_text` | VARCHAR | SCB region label, e.g. `"Upplands Väsby"` |
| `sex_code` | VARCHAR | SCB sex/`Kön` code (`"1"`, `"2"`, `"1+2"`), where applicable |
| `sex_text` | VARCHAR | SCB sex label (`"men"`, `"women"`, `"total"`), where applicable |
| `region_of_birth_code` | VARCHAR | SCB region-of-birth (`Födelseregion`) code, where applicable |
| `region_of_birth_text` | VARCHAR | SCB region-of-birth label, where applicable |
| `contents_code` | VARCHAR | SCB `ContentsCode` identifying the measure returned |
| `contents_text` | VARCHAR | SCB measure label, e.g. `"Population"`, `"Median income"` |
| `time_period` | VARCHAR | SCB `Tid` value, e.g. `"2021"` |
| `value` | VARCHAR | Raw value as returned by the API (string; may contain `".."` for suppressed/missing data) |
| `_source_url` | VARCHAR | Full SCB API endpoint URL queried to retrieve this row |
| `_loaded_at` | TIMESTAMP_NTZ | Timestamp when the row was loaded into Snowflake |

## Snapshot Scope

All `raw_*` tables are loaded for `time_period = '2021'` only.

## Read / Write Access

| Schema | Written By | Read By |
|---|---|---|
| `RAW` | Agent 2 (Ingestor) | Agent 3 (dbt — staging models) |
