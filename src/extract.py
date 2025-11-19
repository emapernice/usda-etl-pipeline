import os
import json
import requests
from time import sleep
from dotenv import load_dotenv

load_dotenv("config/.env")

API_KEY = os.getenv("USDA_API_KEY")
BASE_URL = "https://quickstats.nass.usda.gov/api/api_GET/"

# Query parameters
COMMODITIES = ["SOYBEANS", "CORN", "WHEAT"]
STATES = ["IA", "IL", "MN", "NE", "SD"]
METRICS = ["PRICE RECEIVED", "PRODUCTION", "YIELD"]

YEAR_FROM = 2020
YEAR_TO = 2024


def fetch_usda_data(commodity, metric, state, year_from=YEAR_FROM, year_to=YEAR_TO):
    """
    Fetch USDA QuickStats data for a specific commodity, metric, and state.
    Saves normalized JSON under data/raw/, keeping only the keys needed
    for the Transform step.
    """

    if not API_KEY:
        raise ValueError("Missing USDA_API_KEY in config/.env")

    params = {
        "key": API_KEY,
        "source_desc": "SURVEY",
        "sector_desc": "CROPS",
        "group_desc": "FIELD CROPS",
        "commodity_desc": commodity,
        "statisticcat_desc": metric,
        "agg_level_desc": "STATE",
        "state_alpha": state,
        "year__GE": year_from,
        "year__LE": year_to,
        "format": "JSON",
    }

    print(f"→ Fetching {commodity} | {metric} | {state} ({year_from}-{year_to})...")

    try:
        response = requests.get(BASE_URL, params=params, timeout=20)
        response.raise_for_status()
    except Exception as e:
        print(f"Request error for {commodity}-{state}-{metric}: {e}")
        return None

    try:
        raw_data = response.json().get("data", [])
    except Exception as e:
        print(f"JSON decode error for {commodity}-{state}-{metric}: {e}")
        return None

    if not raw_data:
        print(f"No data found for {commodity}-{state}-{metric}")
        return None

    os.makedirs("data/raw", exist_ok=True)

    cleaned = []
    for row in raw_data:
        try:
            value_clean = (
                None if row.get("Value") in ["(D)", "(NA)", None]
                else float(str(row.get("Value")).replace(",", ""))
            )

            cleaned.append({
                "year": int(row.get("year")),
                "state_name": row.get("state_name"),
                "commodity_desc": row.get("commodity_desc"),
                "statisticcat_desc": row.get("statisticcat_desc"),
                "unit_desc": row.get("unit_desc"),
                "value": value_clean,
            })
        except Exception:
            continue

    if not cleaned:
        print(f"No valid numeric rows for {commodity}-{metric}-{state}")
        return None

    filename = f"{commodity.lower()}_{state}_{metric.replace(' ', '_').lower()}_{year_from}_{year_to}.json"
    file_path = os.path.join("data/raw", filename)

    with open(file_path, "w") as f:
        json.dump(cleaned, f, indent=2)

    print(f"Saved {len(cleaned)} normalized records → {file_path}")
    return file_path


def fetch_all():
    """Fetch all combinations of commodities, metrics, and states."""
    downloaded_files = []
    total = len(COMMODITIES) * len(METRICS) * len(STATES)
    c = 1

    print(f"Starting extraction for {total} combinations...\n")

    for commodity in COMMODITIES:
        for metric in METRICS:
            for state in STATES:
                print(f"[{c}/{total}]")
                result = fetch_usda_data(commodity, metric, state)
                if result:
                    downloaded_files.append(result)
                c += 1
                sleep(1)

    print(f"\nCompleted extraction: {len(downloaded_files)} files saved to data/raw/")
    return downloaded_files


if __name__ == "__main__":
    fetch_all()
