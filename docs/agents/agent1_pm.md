# Agent 1 — Project Manager / Scaffolding

## Role

Sets up the entire project structure, defines data contracts, and creates
agent documentation that all subsequent agents rely on. Establishes the
local Python environment and initializes the dbt project skeleton.

## Inputs Required Before Starting

- Project requirements from the user (datasets, snapshot year, Snowflake
  connection details, dashboard scope).

## Outputs

- Full project folder structure (`docs/`, `ingestion/`, `dbt_project/`,
  `dashboard/`).
- `.gitignore`, `requirements.txt`, `.env.template`.
- `PROJECT_PLAN.md` describing data sources, data flow, and agent order.
- All 5 agent documentation files in `docs/agents/`.
- All 4 data contract files in `docs/contracts/`.
- `README.md`.
- A working Python virtual environment (`venv/`) with dependencies
  installed.
- An initialized dbt project under `dbt_project/`.
- `~/.dbt/profiles.yml` configured for Snowflake using environment
  variables.
- Initial commit pushed to GitHub.

## Constraints

- Do NOT write any Python ingestion logic.
- Do NOT write any dbt models.
- Do NOT write any Streamlit code.
- Only create structure, configuration files, and documentation.
- Never commit real credentials — `.env.template` must use placeholders;
  real values live only in the gitignored `.env`.

## Status Log

<!-- Append updates below as work progresses -->

### 2026-06-10 — Scaffolding complete

**Files / directories created:**

- `.gitignore` — excludes `.env`, `venv/`, `__pycache__/`, `*.pyc`,
  `dbt_packages/`, `dbt_project/target/`, `dbt_project/logs/`, `.dbt/`,
  `*.zip`, `.DS_Store`.
- `requirements.txt` — pinned dependencies: `requests`,
  `snowflake-connector-python`, `dbt-snowflake`, `dbt-core`, `streamlit`,
  `pandas`, `plotly`, `python-dotenv`.
- `.env.template` — Snowflake connection template with placeholder
  password.
- `.env` — real Snowflake credentials for local use (gitignored, not
  committed).
- `README.md` — project overview, structure, and setup instructions.
- `PROJECT_PLAN.md` — data sources (5 SCB API paths), data flow, snapshot
  year, region-of-birth values, agent execution order.
- `docs/agents/agent1_pm.md` … `agent5_deployment.md` — role, inputs,
  outputs, constraints, and status log for each agent.
- `docs/contracts/data_contract_raw.md`,
  `data_contract_staging.md`, `data_contract_intermediate.md`,
  `data_contract_marts.md` — full schema definitions for `RAW`,
  `STAGING`, `INTERMEDIATE`, and `MARTS`.
- `ingestion/.gitkeep`, `dashboard/.gitkeep` — placeholders for Agents 2
  and 4.
- `venv/` — Python virtual environment with all dependencies installed.
- `dbt_project/swedish_municipality_explorer/` — initialized dbt project
  (default `models/example/` removed; `models/.gitkeep` added so Agent 3
  starts with an empty `models/` directory).
- `~/.dbt/profiles.yml` — added a `swedish_municipality_explorer` profile
  (Snowflake, target `dev`, schema `STAGING`) using `env_var()` for all
  credentials, alongside the existing `jaffle_shop` profile.

**Issues encountered / deviations from instructions:**

- **Credential safety (flagged to user, resolved):** The original
  instructions specified writing the real Snowflake password directly into
  `.env.template`, which is committed to GitHub. Since `.env.template` is
  *not* gitignored (by design, so it can serve as a reference), this would
  have permanently exposed a live credential in git history. Per user
  confirmation, `.env.template` instead contains a placeholder
  (`SNOWFLAKE_PASSWORD=your_password_here`), and the real password lives
  only in the gitignored `.env`.
- **dbt-core pre-release pin:** `pip install -r requirements.txt` initially
  resolved `dbt-core` to a pre-release (`2.0.0a1`, then `1.12.0b2`) due to
  transitive pre-release identifiers in `dbt-snowflake`'s dependency
  constraints. Added an explicit `dbt-core>=1.8,<1.12` constraint to
  `requirements.txt` to force the latest stable release (`1.11.11`),
  matched with `dbt-snowflake==1.10.5`.
- `dbt init` required `--skip-profile-setup` (not `--skip-profile-prompt`
  as written in the original instructions) for this dbt version.
- Verified the Snowflake connection with `dbt debug` — connection OK.

**Status:** Project structure, contracts, agent docs, environment, and dbt
project are all in place and verified. Ready for **Agent 2 (Ingestor)** to
begin pulling SCB data into the `RAW` schema.
