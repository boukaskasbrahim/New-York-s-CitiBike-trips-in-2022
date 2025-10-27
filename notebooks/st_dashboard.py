# st_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from keplergl import KeplerGl

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="CitiBike NYC 2022 Dashboard",
    page_icon="🚲",
    layout="wide"
)

# --- HEADER ---
st.title("🚲 CitiBike NYC 2022 Dashboard")
st.markdown("""
Explore New York City’s CitiBike activity in 2022 through interactive data visualizations and maps.  
This dashboard combines trip data and weather records to highlight patterns in ridership and temperature throughout the year.
""")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    base_path = os.path.dirname(os.path.abspath(__file__))     # path to notebooks/
    csv_path = os.path.join(base_path, "../temp_storage/data_raw/citibike_weather_2022.csv")
    csv_path = os.path.normpath(csv_path)
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])
    return df

# ✅ Load dataset
df = load_data()

# --- BAR CHART (Top 20 Start Stations) ---
st.subheader("📊 Top 20 Most Popular Start Stations")
top_stations = (
    df.groupby("start_station_name")
    .size()
    .reset_index(name="trip_count")
    .sort_values("trip_count", ascending=False)
    .head(20)
)
fig_bar = px.bar(
    top_stations,
    x="start_station_name",
    y="trip_count",
    title="Top 20 Most Popular Start Stations",
    color="trip_count",
    color_continuous_scale="Blues"
)
fig_bar.update_layout(
    xaxis_title="Station Name",
    yaxis_title="Number of Trips",
    xaxis_tickangle=45,
    template="plotly_white",
    title_x=0.5
)
st.plotly_chart(fig_bar, use_container_width=True)

# --- DUAL AXIS LINE CHART (Trips vs Temperature) ---
st.subheader("📈 Daily Trips vs Average Temperature (2022)")
daily_trips = df.groupby("date").size().reset_index(name="trip_count")
daily_temp = df.groupby("date")["avgTemp"].mean().reset_index()
daily_data = pd.merge(daily_trips, daily_temp, on="date")

fig_dual = go.Figure()
fig_dual.add_trace(go.Scatter(
    x=daily_data["date"],
    y=daily_data["trip_count"],
    name="Daily Trips",
    mode="lines",
    line=dict(color="royalblue")
))
fig_dual.add_trace(go.Scatter(
    x=daily_data["date"],
    y=daily_data["avgTemp"],
    name="Average Temperature (°C)",
    mode="lines",
    line=dict(color="tomato"),
    yaxis="y2"
))
fig_dual.update_layout(
    title="Daily CitiBike Trips vs Temperature (2022)",
    xaxis_title="Date",
    yaxis_title="Trip Count",
    yaxis2=dict(title="Temperature (°C)", overlaying="y", side="right"),
    template="plotly_white",
    title_x=0.5
)
st.plotly_chart(fig_dual, use_container_width=True)

# --- KEPLER MAP (Exercise 2.5 Integration with Custom Config) ---
st.subheader("🌍 Interactive Geospatial Map – CitiBike Routes")
st.markdown(
    """
    This interactive Kepler.gl map visualizes CitiBike trip routes across New York City in 2022.
    It applies your saved configuration (config.json) for customized layers, color palettes, and styling.
    """
)

try:
    import json
    import os
    from keplergl import KeplerGl

    # Define absolute paths based on your setup
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    map_path = os.path.join(project_root, "citibike_aggregated_map.html")
    config_path = os.path.join(project_root, "notebooks", "config.json")

    # If HTML map already exists, display it directly
    if os.path.exists(map_path):
        with open(map_path, "r", encoding="utf-8") as f:
            map_html = f.read()
        st.components.v1.html(map_html, height=600)
        st.success("Loaded your customized Kepler map successfully!")

    # Otherwise, generate a new one using your saved config.json
    else:
        st.warning("⚠️ No existing map found. Generating a new one using config.json...")

        # Prepare the aggregated dataset
        df_map = (
            df.groupby(["start_station_name", "end_station_name", "start_lat", "start_lng", "end_lat", "end_lng"])
            .size()
            .reset_index(name="trip_count")
        )

        # Load the custom Kepler configuration
        with open(config_path, "r", encoding="utf-8") as cfg:
            custom_config = json.load(cfg)["config"]

        # Create and display the map
        map_1 = KeplerGl(height=600, data={"CitiBike 2022": df_map}, config=custom_config)
        map_1.save_to_html(file_name=map_path)
        st.components.v1.html(map_1._repr_html_(), height=600)
        st.success("✅ New map generated and saved using config.json!")

except Exception as e:
    st.error(f"⚠️ Error loading Kepler map: {e}")


# --- FOOTER ---
st.markdown("---")
st.caption("Data Source: CitiBike NYC (2022) + NOAA Weather API | Dashboard by Brahim Boukaskas")
