"""
Agent 2 — connectivity smoke test.

Checks that the SCB PxWebApi is reachable and that Snowflake credentials in
.env work, before running the full ingest_scb.py pull.
"""

import os

import requests
import snowflake.connector
from dotenv import load_dotenv


def test_scb_api():
    """Small POST query against the population table for a single municipality."""
    url = "https://api.scb.se/OV0104/v1/doris/en/ssd/BE/BE0101/BE0101A/BefolkningNy"
    body = {
        "query": [
            {"code": "Region", "selection": {"filter": "item", "values": ["0114"]}},
            {"code": "Alder", "selection": {"filter": "item", "values": ["tot"]}},
            {"code": "ContentsCode", "selection": {"filter": "item", "values": ["BE0101N1"]}},
            {"code": "Tid", "selection": {"filter": "item", "values": ["2021"]}},
        ],
        "response": {"format": "json"},
    }
    resp = requests.post(url, json=body, timeout=30)
    resp.raise_for_status()
    data = resp.json()["data"]
    if not data:
        raise ValueError("SCB API returned no data rows")
    print(f"  SCB API OK — sample row: {data[0]}")


def test_snowflake():
    """Connect to Snowflake and confirm the RAW schema is reachable."""
    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema="RAW",
    )
    try:
        cur = conn.cursor()
        cur.execute("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_WAREHOUSE()")
        row = cur.fetchone()
        print(f"  Snowflake OK — database={row[0]}, schema={row[1]}, warehouse={row[2]}")
        cur.close()
    finally:
        conn.close()


def main():
    load_dotenv()

    checks = [
        ("SCB API", test_scb_api),
        ("Snowflake", test_snowflake),
    ]

    results = {}
    for name, check in checks:
        print(f"Testing {name}...")
        try:
            check()
            results[name] = True
        except Exception as exc:
            print(f"  FAILED: {exc}")
            results[name] = False

    print("\n=== Results ===")
    for name, ok in results.items():
        print(f"{name}: {'PASS' if ok else 'FAIL'}")

    if not all(results.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
