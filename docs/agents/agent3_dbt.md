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

### 2026-06-10 — dbt pipeline RAW → MARTS complete

**dbt project:** `dbt_project/swedish_municipality_explorer/` (the nested
project initialized by Agent 1; `packages.yml` adds `dbt-labs/dbt_utils
1.3.x`). Custom `generate_schema_name` macro maps `+schema: staging /
intermediate / marts` directly onto the `STAGING`, `INTERMEDIATE`, `MARTS`
schemas (no target-schema prefixing). Staging and intermediate models are
views; marts models are tables.

**Row counts (all match expectations):**

| Model | Schema | Rows |
|---|---|---|
| `stg_population` | STAGING | 290 |
| `stg_income` | STAGING | 290 |
| `stg_employment` | STAGING | 870 |
| `stg_education` | STAGING | 290 |
| `stg_commuting` | STAGING | 290 |
| `int_municipality_profiles` | INTERMEDIATE | 290 |
| `dim_municipality` | MARTS | 290 |
| `fct_opportunity_scores` | MARTS | 870 (290 × 3 region_of_birth values) |

**Test results:** `dbt build` → 8 models built + 53 data tests, **all
PASS, 0 WARN, 0 ERROR**. Tests include `not_null`/`unique` on all primary
keys, `not_null` on `municipality_name`/`year`, `accepted_values` for
`region_of_birth` (`total`/`born_in_sweden`/`born_abroad`) and
`population_category` (`small`/`medium`/`large`), a
`dbt_utils.unique_combination_of_columns` test on
`(municipality_code, region_of_birth, year)` for `fct_opportunity_scores`,
and the custom `assert_scores_between_0_and_100` singular test (all four
`*_score` columns observed in range `[0.0, 100.0]`). `dbt docs generate`
ran successfully.

**Suppressed/missing values:** None of the 5 `RAW` tables contained `'..'`
(suppressed) values for the 2021 snapshot (verified by direct query).
Staging models nonetheless use `try_cast(value as float)` so any future
suppressed/non-numeric value would become `NULL` rather than failing the
run, per the contract's guidance.

**Dimension mappings used in staging:**
- `stg_employment` / `stg_commuting`: `sex_code = '4'` ("men and women") →
  `sex = 'total'`.
- `stg_employment.region_of_birth`: SCB `region_of_birth_text` → `'born in
  Sweden'` → `'born_in_sweden'`, `'foreign-born'` → `'born_abroad'`,
  `'total'` → `'total'` (codes `13`/`23`/`83` respectively).
- All other dimension columns (population, income, education, commuting:
  `sex`, `region_of_birth`) are `NULL` in `RAW` and `COALESCE`d to
  `'total'` in staging, per the contract.

**Data quality / unit deviations from STAGING contract descriptions**
(inherited from Agent 2's documented SCB table-path substitutions —
no `RAW` contract changes, but the *staging* `value` columns for 3 of the
5 datasets carry different units than the contract's per-table
description, all documented inline in each `stg_*.sql` model and
`staging/schema.yml`):
- **`stg_income.value`** is the median expressed in **number of price
  base amounts (prisbasbelopp)**, e.g. `6.4`, not absolute SEK (SCB
  measure `AA0003GJ`). Since `income_score` is min-max normalized across
  municipalities, the unit does not affect the index; no conversion was
  applied (no authoritative prisbasbelopp constant was specified in any
  contract, and the value isn't exposed downstream in `MARTS`).
- **`stg_education.value`** is a **population count** of residents with
  post-secondary education (ISCED97 5-7), not yet a percentage. Converted
  to `pct_post_secondary` in `int_municipality_profiles` as
  `post_secondary_pop / population_total * 100`.
- **`stg_commuting.value`** is a **count of commuters** leaving the
  municipality, not yet a rate. Converted to `out_commute_rate` in
  `int_municipality_profiles` as
  `commuters_out / (population_total * employment_rate_total / 100) * 100`
  (commuters as a share of the estimated employed population).

**Normalization method (MARTS — `fct_opportunity_scores`):**
- `income_score`, `education_score`: standard min-max normalization
  `(value - MIN(value)) / NULLIF(MAX(value) - MIN(value), 0) * 100`,
  computed once per municipality across all 290 municipalities (not
  region-of-birth-specific, since income/education are not broken down by
  region of birth in the source data) and repeated across each
  municipality's 3 `region_of_birth` rows.
- `mobility_score`: **inverse** min-max normalization of
  `out_commute_rate` — `(MAX(out_commute_rate) - out_commute_rate) /
  NULLIF(MAX(out_commute_rate) - MIN(out_commute_rate), 0) * 100` — so
  lower out-commuting yields a higher score. Also computed once per
  municipality and repeated across `region_of_birth` rows.
- `employment_score`: min-max normalization of `stg_employment.value`,
  computed **separately within each `region_of_birth` group** (i.e.
  partitioned), so each score reflects a municipality's relative standing
  among all 290 municipalities *for that population group* specifically.
  This is the only score that varies by `region_of_birth`.
- The overall **Opportunity Index** (combination of the four `*_score`
  columns) is **not precomputed** in `MARTS` — left to Agent 4 to combine
  (e.g. simple average) at the dashboard layer, since the contract leaves
  this decision open and no specific weighting was specified.

**Contract changes (additive, documented per constraints):**
- `data_contract_intermediate.md`: added `population_category` column to
  `int_municipality_profiles` (computed from `population_total`
  thresholds: `<20000` small, `<100000` medium, else large) — needed by
  `dim_municipality` and specified in the Agent 3 task brief but missing
  from the original contract.
- `data_contract_marts.md`: added `county_code` and `population` columns
  to `dim_municipality` — specified in the Agent 3 task brief but missing
  from the original contract; useful for dashboard display. All other
  `dim_municipality`/`fct_opportunity_scores` column names match the
  contract exactly.

**County name lookup:** `dim_municipality.county_name` is derived via a
`county_name()` macro (`macros/county_name.sql`) mapping the 21 standard
SCB county codes (`01`–`25`, excluding `02/11/15/16`) to their Swedish
county (län) names — all 21 codes present in the data are covered.

**Status:** `MARTS.dim_municipality` and `MARTS.fct_opportunity_scores`
are populated, tested, and ready for **Agent 4 (Dashboard)**.
