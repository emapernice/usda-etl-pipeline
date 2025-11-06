from extract import fetch_usda_data
from transform import process_all_raw
from load import upsert_dataframe
import sys


def main():
    try:
        print("Starting USDA ETL pipeline...\n")

        json_path = fetch_usda_data(
            commodity="SOYBEANS",
            year_from=2020,
            year_to=2024,
            state="IA"
        )

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
