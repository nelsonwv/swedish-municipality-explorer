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

### 2026-06-11 — Deployment to Streamlit Community Cloud

- Deployed `dashboard/app.py` to Streamlit Community Cloud.
- `dashboard/.streamlit/secrets.toml.template` added as the credential
  reference for Streamlit Cloud's secrets manager (real secrets entered
  via the Cloud dashboard, never committed — see
  `dashboard/snowflake_connector.py` for the `st.secrets` /
  `.env` fallback logic).
- `runtime.txt` added at repo root to pin Python 3.11 (commit `bcab707`),
  resolving a build failure on Streamlit Cloud's default Python version.
- Verified the deployed app connects to Snowflake `MARTS` (
  `dim_municipality`, `fct_opportunity_scores`) and all four tabs
  (Rankings, Compare, Map, About) render correctly.

### 2026-06-12 — Final pass (v2)

- **Live URL confirmed:** https://swedish-municipality-explorer.streamlit.app
- **PowerPoint updated** (`presentations/swedish_municipality_explorer.pptx`):
  Slide 1 split into a left-column narrative + right-column choropleth
  screenshot placeholder with caption; Slide 2 screenshot placeholder and
  live URL updated; Slide 3 gained a second note documenting Agent 2's
  table-ID replacements; Slide 6 gained an accent-color percentile callout;
  Slide 7 gained a new large accent opening line and a callout-box closing
  statement; Slide 8 closing cards updated with the live URL, GitHub label,
  and LinkedIn handle.
- **README updated:** live dashboard link, personal-hook project
  description, tech stack, text architecture diagram, full data-source
  table (with Agent 2's replacement note), local run instructions, author,
  and links (live dashboard / GitHub / LinkedIn).
- **All 5 agents complete** — scaffolding (Agent 1), SCB ingestion
  (Agent 2), dbt RAW→MARTS pipeline (Agent 3), Streamlit dashboard +
  v2 follow-up (Agent 4), deployment + documentation (Agent 5).

**Project status: SHIPPED**
