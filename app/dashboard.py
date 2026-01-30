import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import textwrap

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(page_title="Åland Grocery BI", layout="wide", page_icon="🥦")

# ============================================
# CUSTOM CSS: MODERN TEAL THEME
# ============================================
st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    
    /* Headers: Modern Teal */
    h1, h2, h3 {
        color: #009688 !important;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Sidebar: Light Gray Background */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Buttons: Teal */
    .stDownloadButton button {
        background-color: #009688 !important;
        color: white !important;
        border-radius: 20px;
        border: none;
    }
    .stDownloadButton button:hover {
        background-color: #00796b !important;
    }
    
    /* Plotly Chart Containers: Force White with Shadow */
    [data-testid="stPlotlyChart"] {
        background-color: #ffffff !important;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        padding: 10px;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# COLOR PALETTE
# ============================================
COLORS = {
    'primary': '#009688',    # Teal (Modern, professional)
    'secondary': '#FF9800',  # Warm Orange
    'accent': '#26A69A',     # Lighter Teal
    'alert': '#E53935',      # Soft Red
    'neutral': '#546E7A',    # Blue-Grey
    'background': '#FFFFFF',
    'palette': px.colors.qualitative.Prism
}

# ============================================
# DATABASE CONNECTION
# ============================================
@st.cache_resource
def get_connection():
    return duckdb.connect("warehouse/warehouse.duckdb", read_only=True)

con = get_connection()

# ============================================
# HELPER FUNCTIONS
# ============================================
def calculate_yoy_change(current, previous):
    if previous and previous != 0 and current:
        return ((current - previous) / previous) * 100
    return None

def format_delta(value):
    if value is None: return None
    return f"{value:+.1f}%"

def get_metric_value(query):
    result = con.execute(query).fetchone()
    return result[0] if result else None

def simple_forecast(df, value_col, periods=3):
    if len(df) < 2: return None
    df = df.copy()
    df['x'] = range(len(df))
    x_mean = df['x'].mean()
    y_mean = df[value_col].mean()
    
    num = ((df['x'] - x_mean) * (df[value_col] - y_mean)).sum()
    den = ((df['x'] - x_mean) ** 2).sum()
    
    if den == 0: return None
    
    slope = num / den
    intercept = y_mean - slope * x_mean
    future_x = range(len(df), len(df) + periods)
    return [slope * x + intercept for x in future_x], slope

def style_plotly_chart(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#424242'),
        xaxis=dict(gridcolor='#f0f0f0', linecolor='#e0e0e0'),
        yaxis=dict(gridcolor='#f0f0f0', linecolor='#e0e0e0'),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(bgcolor='rgba(0,0,0,0)')
    )
    return fig



def render_custom_metric(label, value, prefix="", suffix="", prev_value=None):
    yoy = calculate_yoy_change(value, prev_value)
    delta_str = format_delta(yoy)
    
    if yoy is not None:
        if yoy > 0:
            status_color = COLORS['primary']
            bg_color = "rgba(0, 150, 136, 0.1)"
            icon = "▲"
        else:
            status_color = COLORS['alert']
            bg_color = "rgba(229, 57, 53, 0.1)"
            icon = "▼"
        
        # NOTE: No indentation inside the HTML string to avoid rendering issues
        delta_html = f"""<div style='background-color: {bg_color}; padding: 2px 8px; border-radius: 12px; display: inline-block; color: {status_color}; font-weight: 600; font-size: 0.8rem;'>{icon} {delta_str} YoY</div>"""
    else:
        delta_html = "<span style='color: #9e9e9e; font-size: 0.8rem;'>No prior data</span>"

    # NOTE: Using textwrap.dedent to strip common leading whitespace
    html_card = f"""
    <div style="background: white; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; border-left: 5px solid {COLORS['primary']}; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <p style="margin: 0; color: {COLORS['neutral']}; font-size: 0.9rem; font-weight: 600;">{label}</p>
        <h2 style="margin: 5px 0; color: {COLORS['primary']}; font-weight: 700;">{prefix}{value:,.0f}{suffix}</h2>
        {delta_html}
    </div>
    """
    
    st.markdown(html_card, unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
col_title, col_badge = st.columns([4, 1])
with col_title:
    st.markdown("# 🥦 Åland Fresh Market BI")
    st.markdown("### Grocery Sales & Demographics Insights")

with col_badge:
    st.markdown(f"""
    <div style='background-color: {COLORS['primary']}; color: white; 
                padding: 8px 15px; border-radius: 20px; text-align: center; 
                font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
        🟢 LIVE DATA
    </div>
    <div style='font-size: 11px; text-align: center; color: #757575; margin-top: 5px;'>
        {datetime.now().strftime('%Y-%m-%d')}
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================
# SIDEBAR FILTERS
# ============================================
st.sidebar.header("🔍 Filter Data")

# Year
available_years = con.execute("""
    SELECT DISTINCT year FROM gold_sales_by_municipality 
    WHERE population IS NOT NULL ORDER BY year DESC
""").df()['year'].tolist()

selected_year = st.sidebar.selectbox("📅 Select Year", available_years)
previous_year = selected_year - 1 if (selected_year - 1) in available_years else None

# Municipality
municipalities = con.execute("SELECT DISTINCT municipality FROM gold_sales_by_municipality ORDER BY municipality").df()['municipality'].tolist()
selected_municipalities = st.sidebar.multiselect("🏘️ Region", municipalities, default=municipalities)
mun_filter_sql = ", ".join([f"'{m}'" for m in selected_municipalities]) if selected_municipalities else "''"

# Info Box
st.sidebar.markdown("---")
st.sidebar.info(f"Showing data for **{len(selected_municipalities)}** regions in **{selected_year}**.")

# ============================================
# METRICS ROW
# ============================================
col1, col2, col3, col4 = st.columns(4)

# Data Queries
current_revenue = get_metric_value(f"SELECT SUM(total_revenue) FROM gold_sales_by_municipality WHERE year={selected_year} AND municipality IN ({mun_filter_sql})")
current_transactions = get_metric_value(f"SELECT SUM(total_transactions) FROM gold_sales_by_municipality WHERE year={selected_year} AND municipality IN ({mun_filter_sql})")
current_population = get_metric_value(f"SELECT SUM(population) FROM gold_sales_by_municipality WHERE year={selected_year} AND municipality IN ({mun_filter_sql})")
top_mun = con.execute(f"SELECT municipality FROM gold_sales_by_municipality WHERE year={selected_year} AND municipality IN ({mun_filter_sql}) ORDER BY revenue_per_capita DESC LIMIT 1").fetchone()

# Previous Year Data
if previous_year:
    prev_revenue = get_metric_value(f"SELECT SUM(total_revenue) FROM gold_sales_by_municipality WHERE year={previous_year} AND municipality IN ({mun_filter_sql})")
    prev_transactions = get_metric_value(f"SELECT SUM(total_transactions) FROM gold_sales_by_municipality WHERE year={previous_year} AND municipality IN ({mun_filter_sql})")
    prev_population = get_metric_value(f"SELECT SUM(population) FROM gold_sales_by_municipality WHERE year={previous_year} AND municipality IN ({mun_filter_sql})")
else:
    prev_revenue = prev_transactions = prev_population = None

# Render Metrics
with col1:
    render_custom_metric("💰 Total Revenue", current_revenue, "€", "", prev_revenue)

with col2:
    render_custom_metric("🧾 Transactions", current_transactions, "", "", prev_transactions)

with col3:
    render_custom_metric("👥 Population", current_population, "", "", prev_population)

with col4:
    st.markdown(f"""
    <div style="background: white; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; 
                border-left: 5px solid #7B1FA2; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <p style="margin: 0; color: {COLORS['neutral']}; font-size: 0.9rem; font-weight: 600;">🏆 Top Spender</p>
        <h2 style="margin: 5px 0; color: #7B1FA2; font-weight: 700;">{top_mun[0] if top_mun else 'N/A'}</h2>
        <div style='background-color: rgba(123, 31, 162, 0.1); padding: 2px 8px; border-radius: 12px; 
                    display: inline-block; color: #7B1FA2; font-weight: 600; font-size: 0.8rem;'>
            ★ Per Capita Leader
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================
# CHART ROW 1: Trend & Scatter
# ============================================
st.subheader("📈 Revenue Trends")
c1, c2 = st.columns(2)

with c1:
    trend_data = con.execute(f"""
        SELECT year, SUM(total_revenue) AS revenue 
        FROM gold_sales_by_municipality 
        WHERE municipality IN ({mun_filter_sql}) AND population IS NOT NULL 
        GROUP BY year ORDER BY year
    """).df()
    
    fig = go.Figure()
    
    # Historical Data (Smooth Spline)
    fig.add_trace(go.Scatter(
        x=trend_data['year'], y=trend_data['revenue'],
        mode='lines+markers', name='Actual',
        line=dict(color=COLORS['primary'], width=4, shape='spline'),
        marker=dict(size=8, color='white', line=dict(width=2, color=COLORS['primary']))
    ))
    
    # Annotate Peak
    if not trend_data.empty:
        max_rev = trend_data['revenue'].max()
        max_year = trend_data.loc[trend_data['revenue'].idxmax(), 'year']
        
        fig.add_annotation(
            x=max_year, y=max_rev,
            text=f"Peak: €{max_rev/1e6:.1f}M",
            showarrow=True, arrowhead=2, ax=0, ay=-40,
            font=dict(color=COLORS['primary'], size=12, weight='bold'),
            bgcolor="rgba(255,255,255,0.8)", bordercolor=COLORS['primary']
        )
    
    # Forecast
    forecast, slope = simple_forecast(trend_data, 'revenue')
    if forecast:
        years = list(range(trend_data['year'].max() + 1, trend_data['year'].max() + 4))
        fig.add_trace(go.Scatter(
            x=years, y=forecast, mode='lines', name='Forecast',
            line=dict(color=COLORS['secondary'], dash='dot', width=3)
        ))
        trend_label = "📈 Upward" if slope > 0 else "📉 Downward"
    else:
        trend_label = ""
        
    fig.update_layout(
        title=f"<b>Revenue Growth Trajectory</b> {trend_label}",
        xaxis_title=None, yaxis_title="Revenue (€)",
        hovermode="x unified",
        height=400
    )
    st.plotly_chart(style_plotly_chart(fig), use_container_width=True)

with c2:
    scatter_data = con.execute(f"SELECT * FROM gold_sales_by_municipality WHERE year={selected_year} AND municipality IN ({mun_filter_sql})").df().dropna(subset=['revenue_per_capita'])
    
    if not scatter_data.empty:
        fig = px.scatter(
            scatter_data, 
            x="population", y="total_revenue", 
            size="revenue_per_capita", color="municipality", 
            color_discrete_sequence=COLORS['palette'], 
            title=f"Revenue vs Population ({selected_year})"
        )
        
        # Interactive Selection
        fig.update_layout(clickmode='event+select')
        fig = style_plotly_chart(fig)
        
        event = st.plotly_chart(fig, use_container_width=True, on_select="rerun", selection_mode="points")
        
        if event and event.selection["points"]:
            selected_indices = [p["point_index"] for p in event.selection["points"]]
            clicked_muns = scatter_data.iloc[selected_indices]["municipality"].unique().tolist()
            if clicked_muns:
                st.toast(f"✅ Selected: {', '.join(clicked_muns)}", icon="🎯")
    else:
        st.warning("No data available")

st.markdown("---")

# ============================================
# CHART ROW 2: Categories & Monthly
# ============================================
st.subheader("🍊 Product & Seasonal Analysis")
c3, c4 = st.columns(2)

with c3:
    cat_data = con.execute(f"SELECT category, total_revenue FROM gold_category_performance WHERE year={selected_year} ORDER BY total_revenue DESC").df()
    fig = px.pie(cat_data, values='total_revenue', names='category', title="Sales by Category", 
                 color_discrete_sequence=COLORS['palette'], hole=0.5)
    fig.update_traces(textinfo='percent+label')
    st.plotly_chart(style_plotly_chart(fig), use_container_width=True)

with c4:
    monthly = con.execute(f"SELECT month, SUM(total_revenue) as rev FROM gold_monthly_sales WHERE year={selected_year} GROUP BY month ORDER BY month").df()
    monthly['month_name'] = monthly['month'].apply(lambda x: datetime(2000, x, 1).strftime('%b'))
    
    fig = px.bar(monthly, x='month_name', y='rev', title="Monthly Seasonality", 
                 color='rev', color_continuous_scale=[(0, "#e0f2f1"), (1, COLORS['primary'])])
    fig.update_layout(showlegend=False)
    st.plotly_chart(style_plotly_chart(fig), use_container_width=True)

st.markdown("---")

# ============================================
# CHART ROW 3: Tourism & Rankings
# ============================================
st.subheader("🏖️ Tourism & Rankings")
c5, c6 = st.columns(2)

with c5:
    tourism_data = con.execute(f"SELECT month, total_revenue, total_visitors FROM gold_tourism_sales WHERE year = {selected_year} ORDER BY month").df()
    if not tourism_data.empty:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=tourism_data['month'], y=tourism_data['total_visitors'], name='Tourists', yaxis='y', marker_color=COLORS['secondary'], opacity=0.6))
        fig.add_trace(go.Scatter(x=tourism_data['month'], y=tourism_data['total_revenue'], name='Revenue', yaxis='y2', line=dict(color=COLORS['primary'], width=3)))
        
        fig.update_layout(
            title="Tourism Impact",
            yaxis=dict(title='Tourists', side='left', showgrid=False),
            yaxis2=dict(title='Revenue (€)', side='right', overlaying='y'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02)
        )
        st.plotly_chart(style_plotly_chart(fig), use_container_width=True)
    else:
        st.info("No tourism data available")

with c6:
    ranking_data = con.execute(f"""
        SELECT municipality, revenue_per_capita FROM gold_sales_by_municipality
        WHERE year = {selected_year} AND municipality IN ({mun_filter_sql}) AND revenue_per_capita IS NOT NULL
        ORDER BY revenue_per_capita DESC
    """).df()
    
    if not ranking_data.empty:
        avg_rpc = ranking_data['revenue_per_capita'].mean()
        ranking_data['color'] = ranking_data['revenue_per_capita'].apply(lambda x: COLORS['primary'] if x >= avg_rpc else COLORS['alert'])
        
        fig = go.Figure(go.Bar(
            x=ranking_data['revenue_per_capita'], y=ranking_data['municipality'], orientation='h', marker_color=ranking_data['color']
        ))
        fig.add_vline(x=avg_rpc, line_dash="dash", line_color=COLORS['neutral'], annotation_text=f"Avg: €{avg_rpc:,.0f}")
        fig.update_layout(title="Revenue Per Capita Ranking", yaxis={'categoryorder': 'total ascending'}, xaxis_title="€")
        st.plotly_chart(style_plotly_chart(fig), use_container_width=True)
    else:
        st.warning("No data")

st.markdown("---")

# ============================================
# DATA TABLE
# ============================================
st.subheader("📋 Regional Breakdown")
df_table = con.execute(f"""
    SELECT municipality, population, total_revenue, revenue_per_capita, total_transactions 
    FROM gold_sales_by_municipality WHERE year={selected_year} AND municipality IN ({mun_filter_sql})
    ORDER BY total_revenue DESC
""").df()

c_table, c_export = st.columns([4, 1])

with c_export:
    st.markdown("#### 📥 Export")
    st.download_button("📄 CSV Report", df_table.to_csv(index=False), f"grocery_report_{selected_year}.csv", "text/csv")
    
    full_data = con.execute(f"SELECT * FROM gold_sales_by_municipality WHERE municipality IN ({mun_filter_sql})").df()
    st.download_button("📊 Full History", full_data.to_csv(index=False), "grocery_full_history.csv", "text/csv")

with c_table:
    st.dataframe(
        df_table.style.format({'total_revenue': '€{:,.0f}', 'revenue_per_capita': '€{:,.0f}', 'population': '{:,.0f}', 'total_transactions': '{:,.0f}'})
        .background_gradient(subset=['total_revenue'], cmap="Greens"),
        use_container_width=True, hide_index=True
    )

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: {COLORS['neutral']}; font-size: 0.9rem;'>
    📊 Data: Grocery Sales (Local) • Population (ÅSUB API) • Tourism (Local)<br>
    Built with ❤️ by Saddam using Streamlit + DuckDB | BI Solutions Hackathon 2026
</div>
""", unsafe_allow_html=True)
