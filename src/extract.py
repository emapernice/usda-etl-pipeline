import requests
import os
import json
from dotenv import load_dotenv

load_dotenv("config/.env")

def fetch_usda_data(commodity="SOYBEANS", year_from=2020, year_to=2024, state="VA"):
    api_key = os.getenv("USDA_API_KEY")
    base_url = "https://quickstats.nass.usda.gov/api/api_GET/"
    
    params = {
        "key": api_key,
        "source_desc": "SURVEY",
        "sector_desc": "CROPS",
        "group_desc": "FIELD CROPS",
        "commodity_desc": commodity,
        "agg_level_desc": "STATE",
        "year__GE": year_from,
        "year__LE": year_to,
        "state_alpha": state,
        "format": "JSON"
    }

    print(f"Fetching data for {commodity} ({state}, {year_from}-{year_to})...")
    response = requests.get(base_url, params=params)

    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code} - {response.text}")

    data = response.json()["data"]
    os.makedirs("data/raw", exist_ok=True)
    file_path = f"data/raw/{commodity.lower()}_{state}_{year_from}_{year_to}.json"

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Data saved to {file_path}")
    return file_path
