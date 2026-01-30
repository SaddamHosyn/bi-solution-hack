import streamlit as st
import duckdb
import plotly.express as px
import plotly.graph_objects as go
from streamlit_extras.metric_cards import style_metric_cards

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(page_title="Municipality Deep Dive", layout="wide", page_icon="🏘️")

# Reusing your Fresh Market Theme CSS
st.markdown("""
<style>
    .main .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    h1, h2, h3 { color: #2e7d32 !important; font-family: 'Segoe UI', sans-serif; }
    [data-testid="stMetric"] {
        background-color: #ffffff; border: 1px solid #e0e0e0;
        border-left: 5px solid #2e7d32; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border-radius: 8px; padding: 15px;
    }
    [data-testid="stMetricValue"] { color: #2e7d32 !important; font-weight: 700; }
    [data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #e0e0e0; }
    [data-testid="stPlotlyChart"] {
        background-color: #ffffff; border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); padding: 10px; border: 1px solid #f0f0f0;
    }
</style>
""", unsafe_allow_html=True)

COLORS = {'primary': '#2e7d32', 'secondary': '#ff8f00', 'neutral': '#757575'}

# ============================================
# DATA CONNECTION
# ============================================
@st.cache_resource
def get_connection():
    # Note: Adjust path if needed depending on where you run streamlit from
    return duckdb.connect("warehouse/warehouse.duckdb", read_only=True)

con = get_connection()

# ============================================
# SIDEBAR SELECTION
# ============================================
st.sidebar.header("🔍 Filter")

# Get list of municipalities
all_muns = con.execute("SELECT DISTINCT municipality FROM gold_sales_by_municipality ORDER BY municipality").df()['municipality'].tolist()

# Default to first one or use session state if available
selected_mun = st.sidebar.selectbox("Select Municipality", all_muns)

st.sidebar.info(f"Analyzing: **{selected_mun}**")

# ============================================
# MAIN CONTENT
# ============================================
st.title(f"🏘️ {selected_mun}: Deep Dive Analysis")

# Fetch data for this municipality
df = con.execute(f"""
    SELECT * FROM gold_sales_by_municipality 
    WHERE municipality = '{selected_mun}' 
    ORDER BY year
""").df()

if df.empty:
    st.error("No data found for this municipality.")
    st.stop()

# 1. TOP ROW METRICS (Latest Year)
latest_year = df['year'].max()
latest_data = df[df['year'] == latest_year].iloc[0]
prev_data = df[df['year'] == (latest_year - 1)].iloc[0] if (latest_year - 1) in df['year'].values else None

col1, col2, col3, col4 = st.columns(4)

def calc_delta(curr, prev):
    return f"{((curr - prev) / prev) * 100:+.1f}%" if prev else None

with col1:
    st.metric("📅 Latest Year", latest_year)
with col2:
    delta = calc_delta(latest_data['total_revenue'], prev_data['total_revenue'] if prev_data is not None else None)
    st.metric("💰 Revenue", f"€{latest_data['total_revenue']:,.0f}", delta)
with col3:
    delta = calc_delta(latest_data['population'], prev_data['population'] if prev_data is not None else None)
    st.metric("👥 Population", f"{latest_data['population']:,.0f}", delta)
with col4:
    st.metric("💳 Rev/Capita", f"€{latest_data['revenue_per_capita']:,.2f}")

style_metric_cards(border_left_color=COLORS['primary'], background_color="#ffffff", border_color="#e0e0e0")

st.markdown("---")

# 2. REVENUE TREND CHART
st.subheader("📈 Revenue History")
fig = px.line(df, x='year', y='total_revenue', markers=True, 
              title=f"Total Revenue Trend ({df['year'].min()} - {latest_year})")
fig.update_traces(line_color=COLORS['primary'], line_width=3)
fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
    xaxis_title="Year", yaxis_title="Revenue (€)",
    font=dict(color='#424242')
)
st.plotly_chart(fig, use_container_width=True)

# 3. SPLIT VIEW: TRANSACTIONS & PER CAPITA
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🧾 Transactions per Capita")
    fig2 = px.bar(df, x='year', y='transactions_per_capita',
                  title="Avg Transactions per Person",
                  color_discrete_sequence=[COLORS['secondary']])
    fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#424242'))
    st.plotly_chart(fig2, use_container_width=True)

with col_right:
    st.subheader("📊 Population Growth")
    fig3 = px.area(df, x='year', y='population',
                   title="Population Trend",
                   color_discrete_sequence=['#0288d1'])
    fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#424242'))
    st.plotly_chart(fig3, use_container_width=True)

# 4. RAW DATA TABLE
with st.expander("📄 View Raw Data"):
    st.dataframe(df.style.format({
        'total_revenue': '€{:,.0f}', 
        'revenue_per_capita': '€{:,.2f}',
        'population': '{:,.0f}'
    }), use_container_width=True)
# ============================================
