import os
import shutil
import sys
from extract import fetch_usda_data
from transform import process_all_raw
from load import upsert_dataframe


def clean_old_data():
    """Remove previous raw and processed data before running a new ETL."""
    raw_folder = "data/raw"
    if os.path.exists(raw_folder):
        shutil.rmtree(raw_folder)
        print("Removed old raw data folder: data/raw")

    processed_file = "data/processed/usda_processed.csv"
    if os.path.exists(processed_file):
        os.remove(processed_file)
        print("Removed old processed file: data/processed/usda_processed.csv")


def main():
    try:
        print("Starting USDA ETL pipeline...\n")

        clean_old_data()

        commodities = ["SOYBEANS", "CORN", "WHEAT"]
        metrics = ["PRICE RECEIVED", "PRODUCTION", "YIELD"]
        states = ["IA", "IL", "MN", "NE", "SD"]

        print(f"Starting extraction for {len(commodities) * len(metrics) * len(states)} combinations...\n")

        for i, (commodity, metric, state) in enumerate(
            [(c, m, s) for c in commodities for m in metrics for s in states], start=1
        ):
            print(f"[{i}/{len(commodities) * len(metrics) * len(states)}]")
            fetch_usda_data(
                commodity=commodity,
                metric=metric,
                state=state,
                year_from=2020,
                year_to=2024
            )

        print("\nCompleted extraction.\n")

        df = process_all_raw()
        if df.empty:
            print("No valid data to load. Exiting pipeline.")
            return

        upsert_dataframe(df, clean_before_insert=True)

        print("\nETL pipeline completed successfully!")

    except Exception as e:
        print(f"\nError running ETL pipeline: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()