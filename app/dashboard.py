import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# PAGE CONFIG
st.set_page_config(page_title="Åland Grocery BI", layout="wide", page_icon="🛒")


# CONNECT TO WAREHOUSE
@st.cache_resource
def get_connection():
    return duckdb.connect("warehouse/warehouse.duckdb", read_only=True)


con = get_connection()


# ============================================
# HEADER WITH LIVE DATA BADGE
# ============================================
col_title, col_badge = st.columns([4, 1])
with col_title:
    st.title("🛒 Åland Grocery Sales Dashboard")
with col_badge:
    st.markdown("""
    <div style='background-color: #00c853; color: white; padding: 8px 16px; 
                border-radius: 20px; text-align: center; margin-top: 10px;'>
        🟢 LIVE DATA
    </div>
    <div style='font-size: 12px; text-align: center; color: gray;'>
        Population: ÅSUB API
    </div>
    """, unsafe_allow_html=True)

st.markdown("Analysis of sales performance vs. population demographics.")
st.markdown("---")


# ============================================
# SIDEBAR FILTERS
# ============================================
st.sidebar.header("🔍 Filters")

# Year filter
years = con.execute("SELECT DISTINCT year FROM gold_monthly_sales ORDER BY year").df()['year'].tolist()
available_years = list(range(2000, 2025))  # Only include years with population data
selected_year = st.sidebar.selectbox("📅 Select Year", available_years, index=len(available_years)-1)

# Municipality filter
municipalities = con.execute("SELECT DISTINCT municipality FROM gold_sales_by_municipality ORDER BY municipality").df()['municipality'].tolist()
selected_municipalities = st.sidebar.multiselect(
    "Select Municipalities", 
    municipalities, 
    default=municipalities
)


# ============================================
# METRICS ROW
# ============================================
st.subheader(f"📊 Key Metrics ({selected_year})")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_rev = con.execute(f"SELECT SUM(total_revenue) FROM gold_sales_by_municipality WHERE year={selected_year}").fetchone()[0]
    st.metric("💰 Total Revenue", f"€{total_rev:,.0f}" if total_rev else "N/A")

with col2:
    total_transactions = con.execute(f"SELECT SUM(total_transactions) FROM gold_sales_by_municipality WHERE year={selected_year}").fetchone()[0]
    st.metric("🧾 Transactions", f"{total_transactions:,.0f}" if total_transactions else "N/A")

with col3:
    total_pop = con.execute(f"""
        SELECT SUM(population) FROM silver_population_total 
        WHERE year={selected_year} AND municipality_name != 'Åland'
    """).fetchone()[0]
    st.metric("👥 Population (Live)", f"{total_pop:,.0f}" if total_pop else "N/A")

with col4:
    top_mun_result = con.execute(f"""
        SELECT municipality FROM gold_sales_by_municipality 
        WHERE year={selected_year} AND revenue_per_capita IS NOT NULL
        ORDER BY revenue_per_capita DESC LIMIT 1
    """).fetchone()
    top_mun = top_mun_result[0] if top_mun_result else "N/A"
    st.metric("🏆 Top Per Capita", top_mun)


st.markdown("---")


# ============================================
# CHARTS ROW 1: Geographic Performance
# ============================================
st.subheader("🗺️ Geographic Performance")

df_map = con.execute(f"SELECT * FROM gold_sales_by_municipality WHERE year={selected_year}").fetchdf()

col_map, col_bar = st.columns([2, 1])

with col_map:
    # Filter out rows with null values for the scatter plot
    df_map_clean = df_map.dropna(subset=['revenue_per_capita', 'population', 'total_revenue'])
    
    if not df_map_clean.empty:
        fig = px.scatter(
            df_map_clean, 
            x="population", 
            y="total_revenue", 
            size="revenue_per_capita", 
            color="municipality",
            hover_name="municipality",
            log_x=True, 
            title="Revenue vs. Population (Bubble Size = Rev/Capita)"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for scatter plot")


with col_bar:
    df_top = df_map.sort_values("revenue_per_capita", ascending=False).head(10)
    fig_bar = px.bar(
        df_top, 
        x="revenue_per_capita", 
        y="municipality", 
        orientation='h',
        title="Top 10 by Sales Per Capita",
        color="revenue_per_capita",
        color_continuous_scale="Viridis"
    )
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=400, showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")


# ============================================
# CHARTS ROW 2: Revenue Trend + Category Performance
# ============================================
st.subheader("📈 Trends & Categories")

col_trend, col_cat = st.columns(2)

with col_trend:
    monthly_data = con.execute(f"""
        SELECT month, SUM(total_revenue) AS revenue
        FROM gold_monthly_sales
        WHERE year = {selected_year}
        GROUP BY month
        ORDER BY month
    """).df()
    
    fig = px.line(
        monthly_data, 
        x='month', 
        y='revenue',
        markers=True,
        title=f"Monthly Revenue Trend ({selected_year})",
        labels={'month': 'Month', 'revenue': 'Revenue (€)'}
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with col_cat:
    category_data = con.execute(f"""
        SELECT category, total_revenue
        FROM gold_category_performance
        WHERE year = {selected_year}
        ORDER BY total_revenue DESC
    """).df()
    
    fig = px.pie(
        category_data,
        values='total_revenue',
        names='category',
        title="Sales by Category",
        hole=0.4
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")


# ============================================
# CHARTS ROW 3: Tourism Correlation + Per Capita Comparison
# ============================================
st.subheader("🏖️ Tourism Impact & Per Capita Analysis")

col_tourism, col_percapita = st.columns(2)

with col_tourism:
    tourism_data = con.execute(f"""
        SELECT month, total_revenue, total_visitors
        FROM gold_tourism_sales
        WHERE year = {selected_year}
        ORDER BY month
    """).df()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=tourism_data['month'],
        y=tourism_data['total_visitors'],
        name='Tourists',
        yaxis='y',
        marker_color='lightblue'
    ))
    fig.add_trace(go.Scatter(
        x=tourism_data['month'],
        y=tourism_data['total_revenue'],
        name='Grocery Revenue',
        yaxis='y2',
        line=dict(color='red', width=3)
    ))
    
    fig.update_layout(
        title="Tourism vs Grocery Sales",
        yaxis=dict(title='Tourists', side='left'),
        yaxis2=dict(title='Revenue (€)', side='right', overlaying='y'),
        height=400,
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

with col_percapita:
    if selected_municipalities:
        mun_filter = ", ".join([f"'{m}'" for m in selected_municipalities])
        percapita_data = con.execute(f"""
            SELECT municipality, revenue_per_capita, population
            FROM gold_sales_by_municipality
            WHERE year = {selected_year} 
            AND municipality IN ({mun_filter})
            AND revenue_per_capita IS NOT NULL
            ORDER BY revenue_per_capita DESC
        """).df()
        
        fig = px.bar(
            percapita_data,
            x='municipality',
            y='revenue_per_capita',
            color='revenue_per_capita',
            color_continuous_scale='Viridis',
            title="Revenue Per Capita by Municipality",
            labels={'municipality': 'Municipality', 'revenue_per_capita': 'Revenue Per Capita (€)'}
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Please select at least one municipality in the sidebar")

st.markdown("---")


# ============================================
# DATA TABLE
# ============================================
st.subheader("📋 Detailed Per-Capita Data")

detailed_data = con.execute(f"""
    SELECT 
        municipality,
        population,
        total_revenue,
        revenue_per_capita,
        total_transactions,
        transactions_per_capita
    FROM gold_sales_by_municipality
    WHERE year = {selected_year} AND population IS NOT NULL
    ORDER BY revenue_per_capita DESC
""").df()

st.dataframe(
    detailed_data.style.format({
        'population': '{:,.0f}',
        'total_revenue': '€{:,.2f}',
        'revenue_per_capita': '€{:,.2f}',
        'total_transactions': '{:,.0f}',
        'transactions_per_capita': '{:.4f}'
    }),
    use_container_width=True,
    hide_index=True
)


# ============================================
# RAW DATA EXPANDER
# ============================================
with st.expander("🔍 See Raw Data"):
    st.dataframe(df_map)


# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    📊 Data Sources: Grocery Sales (Local) | Population (ÅSUB API - Live) | Tourism (Local)<br>
    Built with Streamlit + DuckDB | BI Solutions Hackathon 2026
</div>
""", unsafe_allow_html=True)
