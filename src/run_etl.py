import os
import shutil
import sys
from extract import fetch_usda_data
from transform import process_all_raw
from load import upsert_dataframe


def clean_old_data():
    """
    Deletes old ETL data before running a new pipeline.
    This ensures the process always works with fresh files.
    """
    raw_folder = "data/raw"
    processed_file = "data/processed/usda_processed.csv"

    # Delete data/raw folder if it exists
    if os.path.exists(raw_folder):
        shutil.rmtree(raw_folder)
        print("Removed data/raw folder")

    # Delete the processed CSV if it exists
    if os.path.exists(processed_file):
        os.remove(processed_file)
        print("Removed usda_processed.csv")


def main():
    print("     USDA ETL PIPELINE")

    try:
        # Clean previous data before starting
        clean_old_data()

        # Parameters used for API requests
        commodities = ["SOYBEANS", "CORN", "WHEAT"]
        metrics = ["PRICE RECEIVED", "PRODUCTION", "YIELD"]
        states = ["IA", "IL", "MN", "NE", "SD"]

        # Create all possible combinations
        combinations = [
            (c, m, s) for c in commodities for m in metrics for s in states
        ]

        print(f"Starting extraction for {len(combinations)} combinations...\n")

        # EXTRACTION
        for i, (commodity, metric, state) in enumerate(combinations, start=1):
            print(f"({i}/{len(combinations)}) Fetching {commodity} - {metric} - {state}")

            try:
                # API request
                fetch_usda_data(
                    commodity=commodity,
                    metric=metric,
                    state=state,
                    year_from=2020,
                    year_to=2024
                )
            except Exception as error:
                # A failure in one combination does not stop the whole ETL
                print(f"Error fetching {commodity}-{metric}-{state}: {error}")
                continue

        print("\nExtraction completed.\n")

        # TRANSFORMATION
        df = process_all_raw()

        if df.empty:
            print("No valid data processed. ETL finished with no load.")
            return

        # LOAD
        print("Loading data into MySQL...\n")
        upsert_dataframe(df, clean_before_insert=True)

        print("        ETL DONE")

    except Exception as e:
        print(f"\nGeneral ETL error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
