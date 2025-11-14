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

# Default range of years
YEAR_FROM = 2020
YEAR_TO = 2024


def fetch_usda_data(commodity, metric, state, year_from=YEAR_FROM, year_to=YEAR_TO):
    """
    Fetch USDA QuickStats data for a specific commodity, metric, and state.
    Saves the result as a JSON file under data/raw/.
    Returns the path of the saved file or None if failed.
    """
    if not API_KEY:
        raise ValueError("Missing USDA_API_KEY in config/.env file")

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
    except requests.RequestException as e:
        print(f"Request error for {commodity}-{state}-{metric}: {e}")
        return None

    if response.status_code != 200:
        print(f"API error {response.status_code} for {commodity}-{state}-{metric}")
        return None

    try:
        data = response.json().get("data", [])
    except Exception as e:
        print(f"JSON decode error for {commodity}-{state}-{metric}: {e}")
        return None

    if not data:
        print(f"No data found for {commodity}-{state}-{metric}")
        return None

    os.makedirs("data/raw", exist_ok=True)
    filename = f"{commodity.lower()}_{state}_{metric.replace(' ', '_').lower()}_{year_from}_{year_to}.json"
    file_path = os.path.join("data/raw", filename)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Saved {len(data)} records → {file_path}")
    return file_path


def fetch_all():
    """Fetch all combinations of commodities, metrics, and states."""
    downloaded_files = []
    total_tasks = len(COMMODITIES) * len(METRICS) * len(STATES)
    counter = 1

    print(f"Starting extraction for {total_tasks} combinations...\n")

    for commodity in COMMODITIES:
        for metric in METRICS:
            for state in STATES:
                print(f"[{counter}/{total_tasks}]")
                result = fetch_usda_data(commodity, metric, state)
                if result:
                    downloaded_files.append(result)
                counter += 1
                sleep(1.0)  

    print(f"\nCompleted extraction: {len(downloaded_files)} files saved to data/raw/")
    return downloaded_files


if __name__ == "__main__":
    fetch_all()
