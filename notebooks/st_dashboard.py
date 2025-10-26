# st_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_keplergl import keplergl_static

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="CitiBike NYC 2022 Dashboard",
    page_icon="🚲",
    layout="wide"
)

# --- PAGE TITLE ---
st.title("🚲 CitiBike NYC 2022 Dashboard")
st.markdown(
    """
    This dashboard visualizes New York City CitiBike activity in 2022.  
    It combines trip data and weather information to show how temperature and location influence ridership patterns.
    """
)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv("../temp_storage/data_raw/citibike_weather_2022.csv")

    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()

# --- BAR CHART: TOP 20 START STATIONS ---
top_stations = (

    df["start_station_name"]
    .value_counts()
    .reset_index()
    .rename(columns={"index": "station_name", "start_station_name": "trip_count"})
    .head(20)

)

fig_bar = px.bar(
    top_stations,
    x="station_name",
    y="count",
    title="Top 20 Most Popular Start Stations",
    color="count",
    color_continuous_scale="Blues",
)

st.plotly_chart(fig_bar, use_container_width=True)

# --- DUAL AXIS LINE CHART: TRIPS VS TEMPERATURE ---
daily_trips = df.groupby("date").size().reset_index(name="trip_count")
daily_temp = df.groupby("date")["avgTemp"].mean().reset_index()
daily_data = pd.merge(daily_trips, daily_temp, on="date")

fig_dual = go.Figure()
fig_dual.add_trace(go.Scatter(x=daily_data["date"], y=daily_data["trip_count"],
                              name="Daily Trips", mode="lines", line=dict(color="royalblue")))
fig_dual.add_trace(go.Scatter(x=daily_data["date"], y=daily_data["avgTemp"],
                              name="Avg Temp (°C)", mode="lines", line=dict(color="tomato"), yaxis="y2"))

fig_dual.update_layout(
    title="Daily CitiBike Trips vs Temperature (2022)",
    xaxis_title="Date",
    yaxis_title="Trip Count",
    yaxis2=dict(title="Temperature (°C)", overlaying="y", side="right"),
    template="plotly_white",
    title_x=0.5
)
st.plotly_chart(fig_dual, use_container_width=True)

# --- KEPLER MAP (FROM EXERCISE 2.5) ---
st.subheader("Interactive Map of CitiBike Trips (Kepler.gl)")
st.markdown("Below is the interactive Kepler.gl map showing the busiest routes in NYC.")
keplergl_static("temp_storage/citibike_aggregated_map.html")
