import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

st.set_page_config(page_title="Hackathon Ready", layout="wide")
st.title("✅ System Ready")

# Test Data
data = pd.DataFrame({'lat': [60.097], 'lon': [19.935], 'val': [10]})

# Test Chart
st.subheader("Chart Test")
fig = px.bar(data, x='lat', y='val', title="If you see this, Plotly is working")
st.plotly_chart(fig)

# Test Map
st.subheader("Map Test")
st.pydeck_chart(pdk.Deck(
    initial_view_state=pdk.ViewState(latitude=60.097, longitude=19.935, zoom=12),
    layers=[pdk.Layer('ScatterplotLayer', data, get_position='[lon, lat]', get_color='[200, 30, 0, 160]', get_radius=200)]
))
