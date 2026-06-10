# Agent 5 — Deployment

## Role

Packages and deploys the completed pipeline and dashboard, ensuring the
project is reproducible and documented for end users.

## Inputs Required Before Starting

- A working Streamlit dashboard from Agent 4 (`dashboard/`).
- A working dbt project from Agent 3 (`dbt_project/`) that can run
  successfully against Snowflake.
- `requirements.txt` and `.env.template` from Agent 1.
- `README.md` from Agent 1 (to be extended with run/deploy instructions).

## Outputs

- Deployment configuration as needed (e.g. Streamlit Community Cloud
  config, `Procfile`, or Dockerfile — choice to be documented in this log).
- Updated `README.md` with end-to-end setup and run instructions:
  - environment setup
  - running ingestion
  - running dbt
  - running the dashboard
- Final verification notes confirming the dashboard runs against the
  deployed `MARTS` tables.
- Updated status log in this file.

## Constraints

- Do NOT change pipeline logic (ingestion scripts, dbt models, or
  dashboard code) beyond what is strictly required for deployment
  (e.g. config files, environment variable wiring).
- Do NOT commit real credentials anywhere — deployment configs must
  reference environment variables/secrets, never literal values.

## Status Log

<!-- Append updates below as work progresses -->
