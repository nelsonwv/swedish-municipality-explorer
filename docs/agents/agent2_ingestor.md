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
