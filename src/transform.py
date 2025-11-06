import os
import json
import pandas as pd


def process_raw_file(json_path):
    with open(json_path, "r") as f:
        raw_data = json.load(f)

    if not raw_data:
        print(f"No data found in {json_path}")
        return pd.DataFrame()

    df = pd.DataFrame(raw_data)

    columns_to_keep = ["year", "state_name", "commodity_desc", "Value"]
    df = df[[col for col in columns_to_keep if col in df.columns]].copy()

    df.rename(columns={"Value": "price"}, inplace=True)

    if "price" in df.columns:
        df["price"] = (
            df["price"]
            .replace({"(D)": None, "(NA)": None, "": None})
            .astype(str)
            .str.replace(",", "", regex=False)
        )
        df["price"] = pd.to_numeric(df["price"], errors="coerce")

        before_rows = len(df)
        df = df[(df["price"] > 0) & (df["price"] < 10000)]
        removed = before_rows - len(df)
        if removed > 0:
            print(f"Removed {removed} rows with invalid or extreme price values.")

    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

    df.dropna(subset=["price", "state_name", "year"], inplace=True)

    print(f"Processed {os.path.basename(json_path)} ({len(df)} valid rows)")
    return df


def process_all_raw(raw_folder="data/raw"):
    all_dfs = []

    if not os.path.exists(raw_folder):
        print(f"Folder not found: {raw_folder}")
        return pd.DataFrame()

    for file_name in os.listdir(raw_folder):
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

    os.makedirs("data/processed", exist_ok=True)
    output_path = "data/processed/usda_processed.csv"
    combined_df.to_csv(output_path, index=False)
    print(f"💾 Saved combined CSV to {output_path}")

    return combined_df


if __name__ == "__main__":
    process_all_raw()
