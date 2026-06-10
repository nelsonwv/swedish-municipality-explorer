# Project Plan — Swedish Municipality Explorer

## 1. Overview

The Swedish Municipality Explorer is a data pipeline and dashboard project that
builds a **Municipality Opportunity Index** for all Swedish municipalities,
based on a 2021 snapshot of public statistics from Statistics Sweden (SCB).

The index combines four dimensions — income, employment, education, and
mobility (commuting) — into normalized scores that can be explored on a
Streamlit dashboard. The dashboard allows users to filter the index by
**region of birth** (All / Born in Sweden / Born abroad) to surface
disparities in opportunity across municipalities.

## 2. Goal

Produce a reproducible pipeline that:

1. Pulls 5 datasets from the SCB PxWebApi v2.
2. Loads the raw responses into Snowflake (`RAW` schema).
3. Transforms the raw data through dbt Core into clean, modeled layers
   (`STAGING` → `INTERMEDIATE` → `MARTS`).
4. Serves a Streamlit dashboard that reads from the `MARTS` schema and
   visualizes the Opportunity Index per municipality, with a filter for
   region of birth.

## 3. Source Data — SCB PxWebApi v2

**API base URL:** `https://api.scb.se/OV0104/v1/doris/en/ssd/`

**Snapshot year:** `2021` (used consistently across all 5 datasets)

| # | Dataset | API Path | Notes |
|---|---------|----------|-------|
| 1 | Population | `BE/BE0101/BE0101A/BefolkningNy` | Population by municipality, sex, and (where available) region of birth |
| 2 | Income (median) | `AA/AA0003/AA0003F/IntGr5Kom` | Median income by municipality |
| 3 | Employment | `LE/LE0105/LE0105A/LE0105Sysselsattn02N` | Employment rate by municipality, sex, and region of birth |
| 4 | Education | `UF/UF0506/UF0506B/UtbSUNBefN` | Educational attainment (post-secondary share) by municipality |
| 5 | Commuting | `AM/AM0207/AM0207Z/PendlingKN` | Out-commuting rate by municipality |

Full API endpoints are formed as:
`https://api.scb.se/OV0104/v1/doris/en/ssd/<API Path>`

### Region of birth values

Used as a filter dimension throughout staging, intermediate, and marts layers:

- `total` — all residents, regardless of region of birth
- `born_in_sweden` — residents born in Sweden
- `born_abroad` — residents born outside Sweden

## 4. Data Flow

```
SCB PxWebApi v2
      │
      ▼
  RAW schema            (raw_population, raw_income, raw_employment,
                          raw_education, raw_commuting)
      │  dbt: staging models
      ▼
  STAGING schema        (stg_population, stg_income, stg_employment,
                          stg_education, stg_commuting)
      │  dbt: intermediate models
      ▼
  INTERMEDIATE schema   (int_municipality_profiles)
      │  dbt: mart models
      ▼
  MARTS schema          (dim_municipality, fct_opportunity_scores)
      │
      ▼
  Streamlit Dashboard   (Municipality Opportunity Index, filterable
                          by region of birth)
```

See `docs/contracts/` for full schema definitions of each layer.

## 5. Agent Execution Order & Dependencies

| Order | Agent | Responsibility | Depends On |
|-------|-------|-----------------|------------|
| 1 | **Agent 1 — PM / Scaffolding** | Project structure, contracts, agent docs, environment setup, dbt init | — |
| 2 | **Agent 2 — Ingestor** | Pull 5 datasets from SCB PxWebApi v2, load into `RAW` schema in Snowflake | Agent 1 |
| 3 | **Agent 3 — dbt Transformations** | Build dbt models for `STAGING`, `INTERMEDIATE`, and `MARTS` schemas | Agent 2 |
| 4 | **Agent 4 — Dashboard** | Build Streamlit dashboard reading from `MARTS` schema | Agent 3 |
| 5 | **Agent 5 — Deployment** | Package, document, and deploy the dashboard | Agent 4 |

Each agent must read the relevant data contract(s) in `docs/contracts/`
before starting, and must record progress in its status log in
`docs/agents/`.

## 6. Snapshot & Scope

- **Snapshot year:** 2021 (single point-in-time snapshot, no time series)
- **Geographic grain:** Swedish municipality (kommun)
- **Filter dimension:** Region of birth (`total`, `born_in_sweden`, `born_abroad`)
