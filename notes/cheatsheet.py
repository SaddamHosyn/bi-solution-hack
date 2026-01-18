import streamlit as st
import pandas as pd
import numpy as np

# 1. FAKE DATA SETUP (So the code below actually works)
# In the real hackathon, you will replace this with: df = pd.read_csv("data.csv")
data = {
    'city_column': ['Mariehamn', 'Mariehamn', 'Jomala', 'Jomala', 'Finström'],
    'value_column': [10, 25, 15, 30, 12],
    'lat': [60.097, 60.100, 60.150, 60.160, 60.250],
    'lon': [19.935, 19.940, 19.950, 19.960, 19.900]
}
df = pd.DataFrame(data)

# ---------------------------------------------------------
# START OF CHEAT SHEET
# ---------------------------------------------------------

st.title("Cheat Sheet: Interactive Dashboard")

# --- SNIPPET A: SIDEBAR FILTER ---
# "city_column" refers to the column name in your data
city_filter = st.sidebar.multiselect(
    "Select City",
    options=df['city_column'].unique(),
    default=df['city_column'].unique()
)

# Crucial: This line actually filters the data based on selection
filtered_df = df[df['city_column'].isin(city_filter)]


# --- SNIPPET B: KPI ROW ---
st.markdown("### Key Metrics")
kpi1, kpi2, kpi3 = st.columns(3)

# We use 'filtered_df' here so the numbers change when you filter!
kpi1.metric("Total Records", len(filtered_df))
kpi2.metric("Average Value", round(filtered_df['value_column'].mean(), 2))
kpi3.metric("Max Value", filtered_df['value_column'].max())


# --- SNIPPET C: 2-COLUMN LAYOUT ---
st.markdown("---") # Adds a horizontal line
col_left, col_right = st.columns([2, 1]) # Left is 2x wider than Right

with col_left:
    st.markdown("### The Map (Left Column)")
    st.map(filtered_df) # Simple built-in map using lat/lon columns

with col_right:
    st.markdown("### The Stats (Right Column)")
    st.dataframe(filtered_df) # Shows the data table


# ---------------------------------------------------------
# END OF CHEAT SHEET
# ---------------------------------------------------------
# Don't run this file directly during the hack.

# Open this file in a separate tab in VS Code.

# When you need a sidebar, copy lines 23-29 and paste them into your main app.py.

# Important: Change city_column to whatever your actual CSV column is called (e.g., location or district).



