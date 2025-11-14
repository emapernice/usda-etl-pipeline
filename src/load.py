from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv("config/.env")

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

MYSQL_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"
engine = create_engine(MYSQL_URI)


def upsert_dataframe(df, table_name="usda_observations", clean_before_insert=True, chunk_size=1000):

    total = len(df)
    if total == 0:
        print("The DataFrame is empty. No records were inserted.")
        return

    df.columns = [col.lower() for col in df.columns]

    if clean_before_insert:
        try:
            with engine.begin() as conn:
                conn.execute(text(f"DELETE FROM {table_name}"))
            print(f"Deleted ALL previous records from table '{table_name}' before reloading.")
        except Exception as e:
            print(f"Could not clean previous data: {e}")

    for start in range(0, total, chunk_size):
        chunk = df.iloc[start:start + chunk_size].copy()

        chunk = chunk.where(pd.notnull(chunk), None).reset_index(drop=True)

        chunk.to_sql(table_name, con=engine, if_exists="append", index=False)
        print(f"Inserted rows {start} to {start + len(chunk)}")

    print(f"\nUpload completed successfully. Total rows inserted: {total}")


def test_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT NOW()"))
            print(f"Database connection successful! Server time: {result.scalar()}")
    except Exception as e:
        print(f"Database connection failed: {e}")


if __name__ == "__main__":
    test_connection()
    df = pd.read_csv("data/processed/usda_processed.csv")
    upsert_dataframe(df)
