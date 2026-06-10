"""
Agent 2 — SCB API Ingestor

Pulls 5 datasets (population, income, employment, education, commuting) for
Sweden's 290 municipalities, snapshot year 2021, from the SCB PxWebApi v1,
and loads them into OPPORTUNITY_INDEX.RAW per docs/contracts/data_contract_raw.md.
"""

import os
import time

import pandas as pd
import requests
import snowflake.connector
from dotenv import load_dotenv

YEAR = "2021"


class SCBClient:
    """Reusable client for the SCB PxWebApi v1 (POST-based JSON queries)."""

    BASE_URL = "https://api.scb.se/OV0104/v1/doris/en/ssd/"
    RATE_LIMIT_SLEEP = 0.5  # SCB allows 30 calls / 10s
    CELL_LIMIT = 150_000

    def get_municipalities(self, table_path):
        """Return {region_code: region_text} for the 290 four-digit municipality codes."""
        url = self.BASE_URL + table_path
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        time.sleep(self.RATE_LIMIT_SLEEP)
        for var in resp.json()["variables"]:
            if var["code"] == "Region":
                return {
                    code: text
                    for code, text in zip(var["values"], var["valueTexts"])
                    if len(code) == 4 and code.isdigit()
                }
        raise ValueError(f"No Region variable found in {table_path}")

    def fetch(self, table_path, dimensions, region_codes):
        """
        POST a query for `region_codes` against `table_path`, with extra
        dimension selections given in `dimensions` (list of
        {"code": ..., "values": [...]}, excluding Region).

        Chunks the Region selection if the cell count would exceed
        CELL_LIMIT. Returns (columns, data, source_url) — the raw PxWeb
        response pieces (concatenated across chunks) plus the endpoint URL.
        """
        url = self.BASE_URL + table_path

        cells_per_region = 1
        for dim in dimensions:
            cells_per_region *= len(dim["values"])
        max_regions = max(1, self.CELL_LIMIT // cells_per_region)

        columns = None
        data = []
        for i in range(0, len(region_codes), max_regions):
            chunk = region_codes[i : i + max_regions]
            body = {
                "query": [
                    {"code": "Region", "selection": {"filter": "item", "values": chunk}},
                    *[
                        {"code": dim["code"], "selection": {"filter": "item", "values": dim["values"]}}
                        for dim in dimensions
                    ],
                ],
                "response": {"format": "json"},
            }
            print(f"    POST {table_path} | regions {i + 1}-{i + len(chunk)} of {len(region_codes)}")
            resp = requests.post(url, json=body, timeout=60)
            resp.raise_for_status()
            payload = resp.json()
            if columns is None:
                columns = payload["columns"]
            data.extend(payload["data"])
            time.sleep(self.RATE_LIMIT_SLEEP)

        return columns, data, url


def rows_to_dataframe(columns, data):
    """Turn a PxWeb {columns, data} payload into a long DataFrame: one column
    per dimension code (e.g. Region, Kon, Tid) plus a `value` column."""
    dim_codes = [c["code"] for c in columns if c["type"] in ("d", "t")]
    rows = []
    for entry in data:
        row = dict(zip(dim_codes, entry["key"]))
        row["value"] = entry["values"][0]
        rows.append(row)
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# Per-table pulls — each returns a DataFrame matching data_contract_raw.md:
# region_code, region_text, sex_code, sex_text, region_of_birth_code,
# region_of_birth_text, contents_code, contents_text, time_period, value,
# _source_url
# --------------------------------------------------------------------------


def pull_population(client):
    """BE/BE0101/BE0101A/BefolkningNy — total population per municipality.

    Kon and Civilstand have no "total" value, but both are eliminable, so
    they're omitted from the query entirely; PxWeb then returns the value
    summed across all sexes and marital statuses. Alder='tot' selects the
    "all ages" total.
    """
    table_path = "BE/BE0101/BE0101A/BefolkningNy"
    region_texts = client.get_municipalities(table_path)
    region_codes = list(region_texts.keys())
    dimensions = [
        {"code": "Alder", "values": ["tot"]},
        {"code": "ContentsCode", "values": ["BE0101N1"]},
        {"code": "Tid", "values": [YEAR]},
    ]
    columns, data, url = client.fetch(table_path, dimensions, region_codes)
    df = rows_to_dataframe(columns, data)

    return pd.DataFrame(
        {
            "region_code": df["Region"],
            "region_text": df["Region"].map(region_texts),
            "sex_code": None,
            "sex_text": None,
            "region_of_birth_code": None,
            "region_of_birth_text": None,
            "contents_code": "BE0101N1",
            "contents_text": "Population",
            "time_period": df["Tid"],
            "value": df["value"],
            "_source_url": url,
        }
    )


def pull_income(client):
    """AA/AA0003/AA0003F/IntGr5Kom — median disposable income per municipality.

    `Bakgrund` is required (not eliminable) and selects which population
    breakdown the figure applies to; Bakgrund='TOT' ("all") gives the
    municipality-wide median with no sex/age/education/birth-region split,
    so it doesn't map to any contract dimension column.
    """
    table_path = "AA/AA0003/AA0003F/IntGr5Kom"
    region_texts = client.get_municipalities(table_path)
    region_codes = list(region_texts.keys())
    dimensions = [
        {"code": "Bakgrund", "values": ["TOT"]},
        {"code": "ContentsCode", "values": ["AA0003GJ"]},
        {"code": "Tid", "values": [YEAR]},
    ]
    columns, data, url = client.fetch(table_path, dimensions, region_codes)
    df = rows_to_dataframe(columns, data)

    return pd.DataFrame(
        {
            "region_code": df["Region"],
            "region_text": df["Region"].map(region_texts),
            "sex_code": None,
            "sex_text": None,
            "region_of_birth_code": None,
            "region_of_birth_text": None,
            "contents_code": "AA0003GJ",
            "contents_text": "Median value of disposable income, number of price base amounts",
            "time_period": df["Tid"],
            "value": df["value"],
            "_source_url": url,
        }
    )


def pull_employment(client):
    """AM/AM0207/AM0207Z/RamsForvInt04N — gainful employment rate per municipality,
    split by region of birth (replacement for the discontinued
    LE/LE0105/LE0105A/LE0105Sysselsattn02N path).

    Kon='4' selects "men and women" (total); InrikesUtrikes is queried for
    all 3 values (born in Sweden / foreign-born / total) and stored in
    region_of_birth_code/text.
    """
    table_path = "AM/AM0207/AM0207Z/RamsForvInt04N"
    region_texts = client.get_municipalities(table_path)
    region_codes = list(region_texts.keys())
    dimensions = [
        {"code": "InrikesUtrikes", "values": ["13", "23", "83"]},
        {"code": "Kon", "values": ["4"]},
        {"code": "ContentsCode", "values": ["000004B8"]},
        {"code": "Tid", "values": [YEAR]},
    ]
    columns, data, url = client.fetch(table_path, dimensions, region_codes)
    df = rows_to_dataframe(columns, data)

    birth_text_map = {"13": "born in Sweden", "23": "foreign-born", "83": "total"}

    return pd.DataFrame(
        {
            "region_code": df["Region"],
            "region_text": df["Region"].map(region_texts),
            "sex_code": df["Kon"],
            "sex_text": "men and women",
            "region_of_birth_code": df["InrikesUtrikes"],
            "region_of_birth_text": df["InrikesUtrikes"].map(birth_text_map),
            "contents_code": "000004B8",
            "contents_text": "Gainful employment rate, percent",
            "time_period": df["Tid"],
            "value": df["value"],
            "_source_url": url,
        }
    )


def pull_education(client):
    """UF/UF0506/UF0506B/UtbBefRegionR — post-secondary education population
    per municipality (replacement for UF/UF0506/UF0506B/UtbSUNBefN, which has
    no Region dimension).

    UtbildningsNiva levels 5/6/7 (post-secondary, ISCED97) have no combined
    "post-secondary" value, and Alder/Kon have no "total" value. Alder and
    Kon are omitted (eliminable -> PxWeb returns values summed across all
    ages and both sexes), and the 3 UtbildningsNiva levels are summed
    client-side into a single "post-secondary population" figure per
    municipality. contents_code='POST_SECONDARY_POP' is a custom code (not
    an SCB ContentsCode) for this aggregate measure.
    """
    table_path = "UF/UF0506/UF0506B/UtbBefRegionR"
    region_texts = client.get_municipalities(table_path)
    region_codes = list(region_texts.keys())
    dimensions = [
        {"code": "UtbildningsNiva", "values": ["5", "6", "7"]},
        {"code": "ContentsCode", "values": ["000000I2"]},
        {"code": "Tid", "values": [YEAR]},
    ]
    columns, data, url = client.fetch(table_path, dimensions, region_codes)
    df = rows_to_dataframe(columns, data)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    summed = df.groupby(["Region", "Tid"], as_index=False)["value"].sum()

    return pd.DataFrame(
        {
            "region_code": summed["Region"],
            "region_text": summed["Region"].map(region_texts),
            "sex_code": None,
            "sex_text": None,
            "region_of_birth_code": None,
            "region_of_birth_text": None,
            "contents_code": "POST_SECONDARY_POP",
            "contents_text": (
                "Population with post-secondary education (ISCED97 levels 5-7: "
                "post-secondary <3 years, post-secondary 3+ years, post-graduate), "
                "summed across all ages and both sexes"
            ),
            "time_period": summed["Tid"],
            "value": summed["value"].astype("Int64").astype(str),
            "_source_url": url,
        }
    )


def pull_commuting(client):
    """AM/AM0207/AM0207Z/PendlingKN — outcommuters per municipality.

    Kon='4' selects "men and women" (total). ContentsCode='00000548' is
    "Commuters leaving the municipality" (outcommuters).
    """
    table_path = "AM/AM0207/AM0207Z/PendlingKN"
    region_texts = client.get_municipalities(table_path)
    region_codes = list(region_texts.keys())
    dimensions = [
        {"code": "Kon", "values": ["4"]},
        {"code": "ContentsCode", "values": ["00000548"]},
        {"code": "Tid", "values": [YEAR]},
    ]
    columns, data, url = client.fetch(table_path, dimensions, region_codes)
    df = rows_to_dataframe(columns, data)

    return pd.DataFrame(
        {
            "region_code": df["Region"],
            "region_text": df["Region"].map(region_texts),
            "sex_code": df["Kon"],
            "sex_text": "men and women",
            "region_of_birth_code": None,
            "region_of_birth_text": None,
            "contents_code": "00000548",
            "contents_text": "Commuters leaving the municipality",
            "time_period": df["Tid"],
            "value": df["value"],
            "_source_url": url,
        }
    )


class SnowflakeLoader:
    """Loads RAW DataFrames into OPPORTUNITY_INDEX.RAW, idempotently
    (create-if-not-exists, then truncate + insert)."""

    CONTRACT_COLUMNS = [
        "region_code",
        "region_text",
        "sex_code",
        "sex_text",
        "region_of_birth_code",
        "region_of_birth_text",
        "contents_code",
        "contents_text",
        "time_period",
        "value",
        "_source_url",
    ]

    def __init__(self):
        self.conn = snowflake.connector.connect(
            account=os.environ["SNOWFLAKE_ACCOUNT"],
            user=os.environ["SNOWFLAKE_USER"],
            password=os.environ["SNOWFLAKE_PASSWORD"],
            role=os.environ["SNOWFLAKE_ROLE"],
            warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
            database=os.environ["SNOWFLAKE_DATABASE"],
            schema="RAW",
        )

    def load(self, table_name, df):
        """Create the table if needed, truncate it, insert `df`, and return
        the resulting row count."""
        cur = self.conn.cursor()
        try:
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS RAW.{table_name} (
                    region_code VARCHAR,
                    region_text VARCHAR,
                    sex_code VARCHAR,
                    sex_text VARCHAR,
                    region_of_birth_code VARCHAR,
                    region_of_birth_text VARCHAR,
                    contents_code VARCHAR,
                    contents_text VARCHAR,
                    time_period VARCHAR,
                    value VARCHAR,
                    _source_url VARCHAR,
                    _loaded_at TIMESTAMP_NTZ
                )
                """
            )
            cur.execute(f"TRUNCATE TABLE RAW.{table_name}")

            insert_sql = f"""
                INSERT INTO RAW.{table_name}
                ({", ".join(self.CONTRACT_COLUMNS)}, _loaded_at)
                VALUES ({", ".join(["%s"] * len(self.CONTRACT_COLUMNS))}, CURRENT_TIMESTAMP())
            """
            rows = list(df[self.CONTRACT_COLUMNS].itertuples(index=False, name=None))
            cur.executemany(insert_sql, rows)
            self.conn.commit()

            cur.execute(f"SELECT COUNT(*) FROM RAW.{table_name}")
            return cur.fetchone()[0]
        finally:
            cur.close()

    def close(self):
        self.conn.close()


def main():
    load_dotenv()

    client = SCBClient()
    loader = SnowflakeLoader()

    pulls = [
        ("raw_population", "Population", pull_population),
        ("raw_income", "Income", pull_income),
        ("raw_employment", "Employment", pull_employment),
        ("raw_education", "Education", pull_education),
        ("raw_commuting", "Commuting", pull_commuting),
    ]

    start = time.time()
    results = []
    try:
        for table_name, label, pull_fn in pulls:
            print(f"\n=== {label} -> RAW.{table_name} ===")
            df = pull_fn(client)
            row_count = loader.load(table_name, df)
            results.append((label, table_name, row_count))
            print(f"    Loaded {row_count} rows into RAW.{table_name}")
    finally:
        loader.close()

    elapsed = time.time() - start

    print("\n=== Summary ===")
    for label, table_name, row_count in results:
        print(f"{label:<12} RAW.{table_name:<16} {row_count} rows")
    print(f"\nTotal time: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
