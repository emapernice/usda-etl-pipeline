import os
import json
import pandas as pd
import re


# Helper: conversion factors

BUSHELS_PER_TON = {
    "SOYBEANS": 36.743,  
    "CORN": 39.368,      
    "WHEAT": 36.743      
}


def _normalize_unit(unit: str) -> str:
    """Normalize unit_desc string for easier matching."""
    if pd.isna(unit):
        return ""
    return re.sub(r"\s+", " ", unit.strip().upper())


def _convert_price_to_ton(row):
    unit = row.get("unit_desc_norm", "")
    price = row.get("price", None)
    commodity = (row.get("commodity_desc") or "").upper()

    if price is None or pd.isna(price):
        return None

    if "/BU" in unit or "BU" in unit and "$" in unit:
        bupt = BUSHELS_PER_TON.get(commodity)
        if bupt:
            return round(float(price) * bupt, 2)
        else:
            # if commodity not in map, cannot convert reliably
            return None

    # $ / TON or $ / TONNE or $ / T
    if "TON" in unit or "TONNE" in unit or "/T" in unit:
        # price already per ton (approx)
        return round(float(price), 2)

    # $ / KG or $/KILOGRAM
    if "/KG" in unit or "KILOGRAM" in unit:
        return round(float(price) * 1000.0, 2)

    # Unhandled unit -> None
    return None



def process_raw_file(json_path):

    with open(json_path, "r") as f:
        raw_data = json.load(f)

    if not raw_data:
        print(f"No data found in {json_path}")
        return pd.DataFrame()

    df = pd.DataFrame(raw_data)

    metric = df["statisticcat_desc"].iloc[0] if "statisticcat_desc" in df.columns else "UNKNOWN"

    columns_to_keep = [
        "year",
        "state_name",
        "commodity_desc",
        "statisticcat_desc",
        "Value",
        "unit_desc",
    ]
    df = df[[col for col in columns_to_keep if col in df.columns]].copy()

    df["Value"] = (
        df["Value"]
        .replace({"(D)": None, "(NA)": None, "": None})
        .astype(str)
        .str.replace(",", "", regex=False)
    )
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

    metric_map = {
        "PRICE RECEIVED": "price",
        "PRODUCTION": "production",
        "YIELD": "yield",
    }
    metric_col = metric_map.get(str(metric).upper(), "value")

    df.rename(columns={"Value": metric_col}, inplace=True)

    df["metric_type"] = str(metric).upper()

    df["unit_desc_norm"] = df.get("unit_desc", "").apply(_normalize_unit) if "unit_desc" in df.columns else ""

    # ensure year is numeric
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

    # drop rows missing the key fields
    required_cols = [metric_col, "state_name", "year"]
    existing_required = [c for c in required_cols if c in df.columns]
    df.dropna(subset=existing_required, inplace=True)

    # ensure price column exists as numeric if metric is price
    if metric_col == "price" and "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # compute derived price_usd_per_ton if possible
    # only compute when we have a price column
    if "price" in df.columns:
        df["price_usd_per_ton"] = df.apply(_convert_price_to_ton, axis=1)
    else:
        # ensure the column exists downstream even if not computed
        df["price_usd_per_ton"] = None

    # drop temporary normalized unit column (we keep original unit_desc)
    if "unit_desc_norm" in df.columns:
        df.drop(columns=["unit_desc_norm"], inplace=True)

    # final debug log
    print(f"Processed {os.path.basename(json_path)} ({len(df)} valid rows, metric={metric_col})")
    return df


def process_all_raw(raw_folder="data/raw"):
    """
    Process all JSON files under raw_folder and combine into a single DataFrame.
    """
    all_dfs = []

    if not os.path.exists(raw_folder):
        print(f"Folder not found: {raw_folder}")
        return pd.DataFrame()

    for file_name in sorted(os.listdir(raw_folder)):
        if file_name.endswith(".json"):
            file_path = os.path.join(raw_folder, file_name)
            df = process_raw_file(file_path)
            if not df.empty:
                all_dfs.append(df)

    if not all_dfs:
        print("No valid files found to process.")
        return pd.DataFrame()

    combined_df = pd.concat(all_dfs, ignore_index=True)

    print(f"Combined {len(all_dfs)} files: {len(combined_df)} total valid rows")

    expected_cols = ["year", "state_name", "commodity_desc", "price_usd_per_ton"]
    combined_df = combined_df[[c for c in expected_cols if c in combined_df.columns]]

    os.makedirs("data/processed", exist_ok=True)
    output_path = "data/processed/usda_processed.csv"
    combined_df.to_csv(output_path, index=False)
    print(f"Saved cleaned CSV to {output_path}")

    return combined_df


if __name__ == "__main__":
    process_all_raw()
