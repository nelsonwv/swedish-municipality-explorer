# Agent 2 — Ingestor

## Role

Pulls the 5 SCB datasets defined in `PROJECT_PLAN.md` from the SCB
PxWebApi v2 for snapshot year 2021, and loads them into the `RAW` schema
in Snowflake according to `docs/contracts/data_contract_raw.md`.

## Inputs Required Before Starting

- `PROJECT_PLAN.md` (API paths, base URL, snapshot year, region-of-birth
  values).
- `docs/contracts/data_contract_raw.md` (target table/column structure).
- A populated `.env` file with valid Snowflake credentials (copy from
  `.env.template`).
- Python virtual environment from Agent 1 with `requirements.txt`
  installed.
- Confirmation that the `RAW` schema exists in the `OPPORTUNITY_INDEX`
  database.

## Outputs

- Python ingestion scripts under `ingestion/` (one per dataset, or a
  shared module + per-dataset configs).
- Populated tables in `OPPORTUNITY_INDEX.RAW`:
  - `raw_population`
  - `raw_income`
  - `raw_employment`
  - `raw_education`
  - `raw_commuting`
- Each table conforms to the column structure in
  `docs/contracts/data_contract_raw.md`, scoped to `time_period = '2021'`.
- Updated status log in this file.

## Constraints

- Do NOT write dbt models — that is Agent 3's responsibility.
- Do NOT write Streamlit code.
- Do NOT write to `STAGING`, `INTERMEDIATE`, or `MARTS` schemas.
- Do NOT hardcode credentials — load all Snowflake connection details from
  environment variables via `.env`.
- Do NOT change the agreed `RAW` table contract without updating
  `docs/contracts/data_contract_raw.md` and noting the change in this log.

## Status Log

<!-- Append updates below as work progresses -->

### 2026-06-10 — Ingestion complete

**Files created:**

- `ingestion/test_connection.py` — smoke test for SCB API + Snowflake
  connectivity.
- `ingestion/ingest_scb.py` — `SCBClient` (PxWebApi v1 POST queries, with
  rate-limit sleeps and cell-limit-aware region chunking),
  `SnowflakeLoader` (create-if-not-exists / truncate / insert into `RAW`),
  and a `main()` that pulls all 5 datasets and loads them.

**Row counts loaded into `OPPORTUNITY_INDEX.RAW` (time_period = '2021'):**

| Table | Rows |
|---|---|
| `raw_population` | 290 |
| `raw_income` | 290 |
| `raw_employment` | 870 |
| `raw_education` | 290 |
| `raw_commuting` | 290 |

Total ingestion time: ~21s. Both `test_connection.py` checks (SCB API,
Snowflake) passed before the full run.

**API quirks / deviations from `PROJECT_PLAN.md`:**

- **Employment table path replaced.** `LE/LE0105/LE0105A/LE0105Sysselsattn02N`
  now returns `400 Bad Request` (SCB has reorganized this table away). Used
  `AM/AM0207/AM0207Z/RamsForvInt04N` ("Gainful employment rate, percent by
  region, born in Sweden/foreign-born, sex, observations and year")
  instead, which still has 2021 data and a `Region` dimension with all 290
  municipalities. Queried `InrikesUtrikes` = `13`/`23`/`83` (born in
  Sweden / foreign-born / total) with `Kon='4'` (men and women) and
  `ContentsCode='000004B8'` (Gainful employment rate, percent), giving
  290 × 3 = 870 rows. `region_of_birth_code`/`region_of_birth_text` carry
  the `InrikesUtrikes` value/label; `sex_code`/`sex_text` are `'4'`/`"men
  and women"`.
- **Education table path replaced.** `UF/UF0506/UF0506B/UtbSUNBefN` has no
  `Region` dimension (national-level only), so it can't satisfy the
  municipality-level contract. Used
  `UF/UF0506/UF0506B/UtbBefRegionR` instead ("Population 16-95+ by region,
  level of education, age and sex, year"), which has `Region` (290 munis)
  and `Tid` including 2021.
  - That table's `UtbildningsNiva`, `Alder`, and `Kon` are all eliminable
    but have **no aggregate "total" value**. `Alder` and `Kon` are omitted
    from the query entirely — PxWeb then returns values summed across all
    ages and both sexes. `UtbildningsNiva` has no combined "post-secondary"
    value either, so levels `5`/`6`/`7` (ISCED97 post-secondary <3yr,
    post-secondary 3yr+, post-graduate) are queried explicitly (290 × 3 =
    870 raw cells) and **summed client-side per municipality** to a single
    "post-secondary population" figure (290 rows).
  - Because this is a derived/aggregated measure rather than a single SCB
    `ContentsCode`, `contents_code` is set to the custom value
    `POST_SECONDARY_POP` (not an SCB code) with a `contents_text`
    describing exactly what was summed. `sex_code`/`region_of_birth_code`
    are `NULL` for this table.
- **Population: no "total" sex/marital-status value.** `BefolkningNy`'s
  `Kon` (men/women) and `Civilstand` (marital status) have no aggregate
  value, but both are eliminable. They're omitted from the query; PxWeb
  returns the value summed across all sexes and marital statuses.
  `Alder='tot'` (which *does* have an explicit total) selects all ages.
  `sex_code`/`sex_text` are `NULL` for `raw_population`.
- **Income: required `Bakgrund` dimension not in original plan.**
  `IntGr5Kom` requires a `Bakgrund` selection (population breakdown: sex,
  age band, education, region of birth, etc.) that wasn't anticipated in
  `PROJECT_PLAN.md`. Used `Bakgrund='TOT'` ("all") to get the
  municipality-wide median with no further breakdown, and
  `ContentsCode='AA0003GJ'` ("Median value of disposable income, number of
  price base amounts"). `sex_code`/`region_of_birth_code` are `NULL` for
  `raw_income` since `'TOT'` represents no breakdown at all.
- No deviations were needed for `raw_commuting`
  (`AM/AM0207/AM0207Z/PendlingKN`, `Kon='4'`, `ContentsCode='00000548'`
  "Commuters leaving the municipality").
- None of the 5 queries approached the 150,000-cell limit (max was 870
  cells for employment/education), so the chunking logic in
  `SCBClient.fetch()` never had to split a request — but it's in place and
  cell-count-aware for future tables.

**Status:** All 5 `RAW.*` tables are populated per
`docs/contracts/data_contract_raw.md` (no contract column changes — only
the dimension-mapping deviations documented above, as the contract
anticipates). `RAW` schema is ready for **Agent 3 (dbt staging models)**.
