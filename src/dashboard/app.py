import streamlit as st
import pandas as pd
import plotly.express as px


# 📌 FORMATTER — Abreviar números grandes (K, M, B)
def format_number(n):
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}B"
    elif n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    else:
        return f"{n:.0f}"


# 🔧 STREAMLIT CONFIG
st.set_page_config(
    page_title="USDA Dashboard",
    page_icon="🌽",
    layout="wide"
)

st.title("🌾 USDA Crop Analytics Dashboard")
st.markdown("Analyze **Prices**, **Production**, and **Yield** from USDA agricultural data.")


# 📥 LOAD DATA FROM CSV
@st.cache_data
def load_data():
    csv_path = "data/processed/usda_processed.csv"
    df = pd.read_csv(csv_path)

    # Ensure correct dtypes
    df["year"] = df["year"].astype(int)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    return df


df = load_data()


# 🎛️ SIDEBAR FILTERS
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


# 📊 KPI SECTION
st.markdown("## 📊 Key Performance Indicators (KPIs)")
col1, col2, col3 = st.columns(3)

# ---- KPI DATA PREP ----
price_df = filtered_df[filtered_df["statisticcat_desc"] == "PRICE RECEIVED"].sort_values("year")
prod_df = filtered_df[filtered_df["statisticcat_desc"] == "PRODUCTION"]
yield_df = filtered_df[filtered_df["statisticcat_desc"] == "YIELD"]


# KPI 1 — YEAR-OVER-YEAR PRICE CHANGE
if not price_df.empty and len(price_df["year"].unique()) >= 2:
    latest_year = price_df["year"].max()
    prev_year = latest_year - 1

    latest_value = price_df[price_df["year"] == latest_year]["value"].mean()
    prev_value = price_df[price_df["year"] == prev_year]["value"].mean()

    if pd.notna(latest_value) and pd.notna(prev_value):
        yoy_change = ((latest_value - prev_value) / prev_value) * 100
    else:
        yoy_change = None
else:
    yoy_change = None

with col1:
    st.metric(
        label="📉 Price YoY Change",
        value=f"{yoy_change:.2f} %" if yoy_change is not None else "N/A"
    )


# KPI 2 — LATEST PRICE
if not price_df.empty:
    latest_year = price_df["year"].max()
    latest_price = price_df[price_df["year"] == latest_year]["value"].mean()
else:
    latest_price = None

with col2:
    st.metric(
        label="💰 Latest Price",
        value=f"{latest_price:.2f}" if latest_price is not None else "N/A"
    )


# KPI 3 — TOP PRODUCING STATE (FORMATTED)
if selected_state == "All":
    prod_rank = prod_df.groupby("state_name")["value"].sum().sort_values(ascending=False)

    if not prod_rank.empty:
        top_state = prod_rank.index[0]
        top_value = prod_rank.iloc[0]
        formatted_value = format_number(top_value)

        kpi3_text = f"{top_state} — {formatted_value}"
    else:
        kpi3_text = "N/A"
else:
    kpi3_text = "State filter applied"

with col3:
    st.metric(label="🥇 Top Producing State", value=kpi3_text)


# 📈 VISUALIZATIONS

# ---- PRICE RECEIVED ----
st.subheader("📈 1️⃣ Price Received by Year (Stacked Area)")

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

# ---- PRODUCTION ----
st.subheader("🌾 2️⃣ Total Production by Year")

if not prod_df.empty:
    fig = px.bar(
        prod_df,
        x="year",
        y="value",
        color="commodity_desc",
        title="Production Volume by Year"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No production data available for selected filters.")

# ---- YIELD ----
st.subheader("🌱 3️⃣ Average Yield (Grouped Bars)")

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


# 📄 RAW DATA TABLE
st.subheader("🧾 Raw Filtered Data")
st.dataframe(filtered_df, use_container_width=True)

st.markdown("---")
st.caption("USDA Data Dashboard — Streamlit + Plotly — CSV Version")
