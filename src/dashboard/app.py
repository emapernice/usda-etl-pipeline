import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import plotly.express as px

# Load environment variables
load_dotenv("config/.env")

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

MYSQL_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"
engine = create_engine(MYSQL_URI)

# Streamlit Configuration
st.set_page_config(
    page_title="USDA Dashboard",
    page_icon="🌽",
    layout="wide"
)

st.title("🌾 USDA Crop Analytics Dashboard")
st.markdown("Analyze **Prices**, **Production**, and **Yield** from USDA data.")

# Load data from MySQL
@st.cache_data
def load_data():
    query = """
        SELECT 
            year,
            state_name,
            commodity_desc,
            statisticcat_desc,
            unit_desc,
            value
        FROM usda_observations
        WHERE value IS NOT NULL
        ORDER BY year ASC
    """
    df = pd.read_sql(query, engine)
    return df

df = load_data()

# Sidebar Filters
st.sidebar.header("🔍 Filters")

states = sorted(df["state_name"].dropna().unique())
commodities = sorted(df["commodity_desc"].dropna().unique())
years = sorted(df["year"].dropna().unique())

selected_state = st.sidebar.selectbox("State", ["All"] + states)
selected_commodity = st.sidebar.selectbox("Commodity", ["All"] + commodities)
selected_year = st.sidebar.selectbox("Year", ["All"] + [str(y) for y in years])

filtered_df = df.copy()
if selected_state != "All":
    filtered_df = filtered_df[filtered_df["state_name"] == selected_state]
if selected_commodity != "All":
    filtered_df = filtered_df[filtered_df["commodity_desc"] == selected_commodity]
if selected_year != "All":
    filtered_df = filtered_df[filtered_df["year"] == int(selected_year)]

# Report Sections
st.subheader("📈 1️⃣ Price Received by Year (Stacked Area)")

price_df = filtered_df[filtered_df["statisticcat_desc"] == "PRICE RECEIVED"]

if not price_df.empty:
    fig = px.area(
        price_df,
        x="year",
        y="value",
        color="commodity_desc",
        title="Price Received Over Time (Stacked Area)"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No price data available for selected filters.")


st.subheader("🌾 2️⃣ Total Production by Year")
prod_df = filtered_df[filtered_df["statisticcat_desc"] == "PRODUCTION"]

if not prod_df.empty:
    fig = px.bar(
        prod_df,
        x="year",
        y="value",
        color="commodity_desc",
        title="Production Volume by Year"
    )
    st.plotly_chart(fig, width="stretch")
else:
    st.info("No production data available for selected filters.")

st.subheader("🌱 3️⃣ Average Yield (Grouped Bars)")
yield_df = filtered_df[filtered_df["statisticcat_desc"] == "YIELD"]

if not yield_df.empty:
    fig = px.bar(
        yield_df,
        x="year",
        y="value",
        color="commodity_desc",
        barmode="group",
        title="Yield by Year and Commodity"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No yield data available for selected filters.")


# Data Table
st.subheader("🧾 Raw Filtered Data")
st.dataframe(filtered_df, width="stretch")

st.markdown("---")
st.caption("USDA Data Dashboard — Streamlit + SQLAlchemy + Plotly")
