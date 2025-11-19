from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv("config/.env")

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

if not all([MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DATABASE]):
    raise ValueError("Missing MySQL environment variables in config/.env")

# Create SQLAlchemy engine
MYSQL_URI = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}/{MYSQL_DATABASE}"
)
engine = create_engine(MYSQL_URI)

REQUIRED_COLUMNS = [
    "year",
    "state_name",
    "commodity_desc",
    "statisticcat_desc",
    "unit_desc",
    "value"
]


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize the DataFrame before loading it into MySQL:
    - Convert column names to lowercase
    - Validate required columns
    - Clean column types
    - Replace NaN → None for SQL compatibility
    """

    df.columns = [col.lower() for col in df.columns]

    # Defensive validation
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Keep only required columns
    df = df[REQUIRED_COLUMNS].copy()

    # Normalize types
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # Replace NaN with None before sending to SQL
    df = df.where(pd.notnull(df), None)

    return df


def upsert_dataframe(
    df: pd.DataFrame,
    table_name="usda_observations",
    clean_before_insert=True,
    chunk_size=1000
):
    """
    Insert the DataFrame into MySQL in chunks.
    If clean_before_insert=True, the destination table is cleared before loading data.
    """
    total = len(df)
    if total == 0:
        print("DataFrame is empty → no records inserted.")
        return

    df = clean_dataframe(df)

    # Optionally clear the table before loading
    if clean_before_insert:
        try:
            with engine.begin() as conn:
                conn.execute(text(f"DELETE FROM {table_name}"))
            print(f"Cleared destination table: {table_name}")
        except Exception as e:
            print(f"[ERROR] Could not clear table {table_name}: {e}")
            return

    # Insert data in chunks
    for start in range(0, total, chunk_size):
        chunk = df.iloc[start:start + chunk_size].copy()

        try:
            chunk.to_sql(table_name, con=engine, if_exists="append", index=False)
            print(f"Inserted rows {start} → {start + len(chunk)}")
        except Exception as e:
            print(f"[ERROR] Failed inserting chunk {start}: {e}")
            return

    print(f"\nLoad completed! Total rows inserted: {total}")


def test_connection():
    """Simple test to verify the database connection."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT NOW()"))
            print(f"Connected to MySQL — Server time: {result.scalar()}")
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")


if __name__ == "__main__":
    test_connection()

    try:
        df = pd.read_csv("data/processed/usda_processed.csv")
        print(f"Loaded processed CSV → {len(df)} rows")
    except Exception as e:
        print(f"[ERROR] Could not read processed CSV: {e}")
        exit()

    upsert_dataframe(df)
