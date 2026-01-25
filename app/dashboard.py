import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

# PAGE CONFIG
st.set_page_config(page_title="Åland Grocery BI", layout="wide")

# CONNECT TO WAREHOUSE
# Note: We use read_only=True so the dashboard doesn't lock the DB
@st.cache_resource
def get_connection():
    return duckdb.connect("warehouse/warehouse.duckdb", read_only=True)

con = get_connection()

# TITLE
st.title("🛒 Åland Grocery Sales Dashboard")
st.markdown("Analysis of sales performance vs. population demographics.")

# METRICS ROW
col1, col2, col3 = st.columns(3)
latest_year = 2024

with col1:
    total_rev = con.execute(f"SELECT SUM(total_revenue) FROM gold_sales_by_municipality WHERE year={latest_year}").fetchone()[0]
    st.metric("Total Revenue (2024)", f"€{total_rev:,.0f}")

with col2:
    top_mun = con.execute(f"SELECT municipality_name FROM gold_sales_by_municipality WHERE year={latest_year} ORDER BY revenue_per_capita DESC LIMIT 1").fetchone()[0]
    st.metric("Top Municipality (Per Capita)", top_mun)

with col3:
    total_pop = con.execute(f"SELECT SUM(population) FROM silver_population WHERE year={latest_year}").fetchone()[0]
    st.metric("Total Population", f"{total_pop:,.0f}")

# CHARTS ROW 1
st.markdown("### 🗺️ Geographic Performance")
df_map = con.execute("SELECT * FROM gold_sales_by_municipality WHERE year=2024").fetchdf()

col_map, col_bar = st.columns([2, 1])

with col_map:
    # Scatter plot on map would require lat/lon, so we'll do a nice bubble chart instead
    fig = px.scatter(
        df_map, 
        x="population", 
        y="total_revenue", 
        size="revenue_per_capita", 
        color="municipality_name",
        hover_name="municipality_name",
        log_x=True, 
        title="Revenue vs. Population (Bubble Size = Rev/Capita)"
    )
    st.plotly_chart(fig, use_container_width=True)

with col_bar:
    # Bar chart of top sales per capita
    df_top = df_map.sort_values("revenue_per_capita", ascending=False).head(10)
    fig_bar = px.bar(
        df_top, 
        x="revenue_per_capita", 
        y="municipality_name", 
        orientation='h',
        title="Top 10 Muni's by Sales Per Capita"
    )
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_bar, use_container_width=True)

# CHARTS ROW 2
st.markdown("### 📈 Trends Over Time")
df_trends = con.execute("SELECT * FROM gold_monthly_sales WHERE month_year >= '2023-01'").fetchdf()

fig_line = px.line(
    df_trends, 
    x="month_year", 
    y="total_revenue", 
    color="product_category", 
    title="Monthly Revenue by Category (Last 2 Years)"
)
st.plotly_chart(fig_line, width="stretch")

# RAW DATA
with st.expander("See Raw Data"):
    st.dataframe(df_map)
