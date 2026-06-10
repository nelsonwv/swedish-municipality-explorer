"""
Agent 4 — Snowflake data access for the Streamlit dashboard.

Reads only from OPPORTUNITY_INDEX.MARTS (dim_municipality,
fct_opportunity_scores), per docs/contracts/data_contract_marts.md.
Credentials are loaded from environment variables via .env — never
hardcoded.
"""

import os
from pathlib import Path

import pandas as pd
import snowflake.connector
import streamlit as st
from dotenv import load_dotenv

# .env lives at the repo root (one level up from dashboard/).
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Maps the sidebar "Population group" dropdown labels to the
# region_of_birth values used in MARTS.fct_opportunity_scores.
REGION_OF_BIRTH_MAP = {
    "All residents": "total",
    "Born in Sweden": "born_in_sweden",
    "Born abroad": "born_abroad",
}


def _get_connection():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema="MARTS",
    )


@st.cache_data(ttl=3600)
def get_opportunity_data(region_of_birth: str) -> pd.DataFrame:
    """
    Return one row per municipality for the given region_of_birth
    ('total', 'born_in_sweden', or 'born_abroad'), joining
    fct_opportunity_scores with dim_municipality.
    """
    query = """
        select
            d.municipality_code,
            d.municipality_name,
            d.county_code,
            d.county_name,
            d.population,
            d.population_category,
            d.year,
            f.region_of_birth,
            f.income_score,
            f.employment_score,
            f.education_score,
            f.mobility_score
        from fct_opportunity_scores f
        inner join dim_municipality d
            on f.municipality_code = d.municipality_code
            and f.year = d.year
        where f.region_of_birth = %(region_of_birth)s
        order by d.municipality_name
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, {"region_of_birth": region_of_birth})
        columns = [c[0].lower() for c in cur.description]
        rows = cur.fetchall()
    finally:
        conn.close()

    return pd.DataFrame(rows, columns=columns)
