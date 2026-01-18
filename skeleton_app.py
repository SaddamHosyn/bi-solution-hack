import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

# ==========================================
# 1. CONFIG SECTION (CHANGE THIS ON HACK DAY)
# ==========================================
# Just change these variable names to match the CSV Matts gives you.
FILE_PATH = "data/your_file.csv"  # Put the file in data folder
DATE_COL = "timestamp"            # The column with dates/times
CAT_COL  = "category"             # The column for grouping (e.g., 'Type', 'City')
VAL_COL  = "amount"               # The column with numbers (e.g., 'Price', 'Count')
LAT_COL  = "latitude"             # Latitude column (if applicable)
LON_COL  = "longitude"            # Longitude column (if applicable)

# ==========================================
# 2. DATA LOADER (DO NOT TOUCH)
# ==========================================
st.set_page_config(layout="wide", page_title="Insight Dashboard")

@st.cache_data
def load_data():
    # Try to load standard CSV
    try:
        df = pd.read_csv(FILE_PATH)
    except:
        # Fallback if file doesn't exist yet (Testing mode)
        return pd.DataFrame({
            DATE_COL: pd.date_range(start='1/1/2025', periods=100),
            CAT_COL: ['A', 'B', 'A', 'C'] * 25,
            VAL_COL: [x * 10 for x in range(100)],
            LAT_COL: [60.100 + x*0.001 for x in range(100)],
            LON_COL: [19.900 + x*0.001 for x in range(100)]
        })

    # Smart Date Conversion
    if DATE_COL in df.columns:
        df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors='coerce')
    
    return df

df = load_data()

# ==========================================
# 3. SIDEBAR FILTERS (GENERIC)
# ==========================================
st.sidebar.header("🔍 Filters")

# Date Filter
min_date = df[DATE_COL].min()
max_date = df[DATE_COL].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])

# Category Filter
if CAT_COL in df.columns:
    selected_cats = st.sidebar.multiselect("Select Category", df[CAT_COL].unique(), df[CAT_COL].unique())
    # Apply Filter
    mask = (df[CAT_COL].isin(selected_cats)) & \
           (df[DATE_COL].dt.date >= date_range[0]) & \
           (df[DATE_COL].dt.date <= date_range[1])
    filtered_df = df[mask]
else:
    filtered_df = df

# ==========================================
# 4. DASHBOARD LAYOUT (The Story)
# ==========================================
st.title("📊 The Data Story")

# Top KPI Row
k1, k2, k3 = st.columns(3)
k1.metric("Total Volume", f"{filtered_df[VAL_COL].sum():,.0f}")
k2.metric("Average Value", f"{filtered_df[VAL_COL].mean():,.2f}")
k3.metric("Record Count", len(filtered_df))

st.markdown("---")

# Row 2: Time Series & Breakdown
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("📈 Trends Over Time")
    # Aggregating by day automatically
    daily_data = filtered_df.groupby(filtered_df[DATE_COL].dt.date)[VAL_COL].sum().reset_index()
    fig_line = px.line(daily_data, x=DATE_COL, y=VAL_COL, markers=True, template="plotly_white")
    st.plotly_chart(fig_line, use_container_width=True)

with c2:
    st.subheader("🥧 Breakdown")
    if CAT_COL in df.columns:
        fig_pie = px.pie(filtered_df, names=CAT_COL, values=VAL_COL, hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

# Row 3: Map (Only shows if Lat/Lon exists)
if LAT_COL in df.columns and LON_COL in df.columns:
    st.markdown("---")
    st.subheader("🗺️ Geographic Distribution")
    
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=filtered_df[LAT_COL].mean(),
            longitude=filtered_df[LON_COL].mean(),
            zoom=11,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
               'HexagonLayer',
               data=filtered_df,
               get_position=f'[{LON_COL}, {LAT_COL}]',
               radius=200,
               elevation_scale=4,
               elevation_range=[0, 1000],
               pickable=True,
               extruded=True,
            ),
        ],
    ))
# ==========================================



# Matts gives you traffic_data_2024.csv.

#Open skeleton_app.py.

#Change line 10 to: FILE_PATH = "traffic_data_2024.csv"

#Change line 11 to: DATE_COL = "Time" (or whatever the CSV header says).

# Change line 12 to: CAT_COL = "VehicleType".
