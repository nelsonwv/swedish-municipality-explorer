# Data Contract — INTERMEDIATE Schema

## Schema

`OPPORTUNITY_INDEX.INTERMEDIATE`

## Purpose

Wide, one-row-per-municipality table that joins all five staging datasets
together and derives composite metrics needed by the marts layer (e.g. the
employment gap between total and foreign-born populations).

## Tables

- `int_municipality_profiles`

## Column Structure

| Column | Type | Description |
|---|---|---|
| `municipality_code` | VARCHAR | 4-digit SCB municipality code |
| `municipality_name` | VARCHAR | Municipality name |
| `county_code` | VARCHAR | 2-digit SCB county (län) code, derived from `municipality_code` |
| `population_total` | FLOAT | Total population (`region_of_birth = 'total'`, `sex = 'total'`) |
| `median_income` | FLOAT | Median income, SEK (`region_of_birth = 'total'`, `sex = 'total'`) |
| `employment_rate_total` | FLOAT | Employment rate (%) for the total population (`region_of_birth = 'total'`) |
| `employment_rate_foreign_born` | FLOAT | Employment rate (%) for `region_of_birth = 'born_abroad'` |
| `employment_gap` | FLOAT | `employment_rate_total - employment_rate_foreign_born` (percentage points) |
| `pct_post_secondary` | FLOAT | Share of population with post-secondary education (%) (`region_of_birth = 'total'`) |
| `out_commute_rate` | FLOAT | Out-commuting rate (%) |
| `year` | INTEGER | Snapshot year (`2021`) |

## Notes

- One row per `municipality_code` per `year`.
- `county_code` is derived as the first two digits of `municipality_code`
  (e.g. `"0114"` → county `"01"` = Stockholm county).
- Region-of-birth-specific cuts beyond `employment_rate_foreign_born` /
  `employment_gap` are handled in the `MARTS` layer
  (`fct_opportunity_scores`), not here.

## Read / Write Access

| Schema | Written By | Read By |
|---|---|---|
| `INTERMEDIATE` | Agent 3 (dbt — intermediate models) | Agent 3 (dbt — mart models) |
