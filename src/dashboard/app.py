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


# Streamlit App Configuration

st.set_page_config(
    page_title="USDA Crop Prices Dashboard",
    page_icon="🌽",
    layout="wide"
)

st.title("🌾 USDA Crop Prices Dashboard")
st.markdown("Visualize agricultural price trends processed from the USDA Quick Stats API.")


# Load Data from MySQL

@st.cache_data
def load_data():
    query = """
        SELECT year, state_name, commodity_desc, price
        FROM usda_observations
        WHERE price IS NOT NULL
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

selected_state = st.sidebar.selectbox("State", options=["All"] + states)
selected_commodity = st.sidebar.selectbox("Commodity", options=["All"] + commodities)
selected_year = st.sidebar.selectbox("Year", options=["All"] + [str(y) for y in years])

filtered_df = df.copy()
if selected_state != "All":
    filtered_df = filtered_df[filtered_df["state_name"] == selected_state]
if selected_commodity != "All":
    filtered_df = filtered_df[filtered_df["commodity_desc"] == selected_commodity]
if selected_year != "All":
    filtered_df = filtered_df[filtered_df["year"] == int(selected_year)]


# Summary Statistics

st.subheader("📊 Summary Statistics")

if not filtered_df.empty:
    avg_price = filtered_df["price"].mean()
    max_price = filtered_df["price"].max()
    min_price = filtered_df["price"].min()

    col1, col2, col3 = st.columns(3)
    col1.metric("Average Price", f"${avg_price:,.2f}")
    col2.metric("Maximum", f"${max_price:,.2f}")
    col3.metric("Minimum", f"${min_price:,.2f}")
else:
    st.warning("No data available for the selected filters.")


# Chart Visualization

if not filtered_df.empty:
    # Line Chart: Price Trend Over Years
    fig = px.line(
        filtered_df,
        x="year",
        y="price",
        color="commodity_desc",
        title="Price Trends by Year",
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)

    # Box Plot: Price Distribution by Commodity
    fig_box = px.box(
        filtered_df,
        x="commodity_desc",
        y="price",
        title="Price Distribution by Commodity"
    )
    st.plotly_chart(fig_box, use_container_width=True)


# Data Table

st.subheader("🧾 Filtered Data")
st.dataframe(filtered_df, use_container_width=True)

st.markdown("---")
st.caption("Built using Streamlit, Plotly, and SQLAlchemy.")
