# st_dashboard_part_2.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from keplergl import KeplerGl
from PIL import Image
import json

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="CitiBike NYC 2022 Dashboard",
    layout="wide"
)

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Dashboard Navigation")
page = st.sidebar.radio(
    "Choose a section:",
    [
        "Introduction",
        "Weather and Bike Usage",
        "Most Popular Stations",
        "Interactive Map",
        "Recommendations"
    ]
)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    base_path = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_path, "../temp_storage/data_raw/citibike_weather_2022.csv")
    csv_path = os.path.normpath(csv_path)
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()

# --- PAGE 1: INTRODUCTION ---
if page == "Introduction":
    st.title("CitiBike NYC 2022 Dashboard")
    st.markdown("""
    This dashboard presents an analysis of **New York City’s CitiBike system in 2022**.  
    It visualizes how weather impacts ridership, identifies the most active stations,  
    and maps aggregated trips throughout the city using **Kepler.gl**.

    **Sections included:**
    - Weather and Bike Usage  
    - Most Popular Stations  
    - Interactive Map  
    - Recommendations
    """)

# --- PAGE 2: WEATHER AND BIKE USAGE ---
elif page == "Weather and Bike Usage":
    st.header("Weather and Bike Usage")

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

    st.markdown("""
    **Observation:**  
    Warmer months show significantly higher ridership, while colder months see a noticeable decline.
    """)

# --- PAGE 3: MOST POPULAR STATIONS ---
elif page == "Most Popular Stations":
    st.header("Most Popular Start Stations")

    df["value"] = 1
    top_stations = (
        df.groupby("start_station_name", as_index=False)
        .agg({"value": "sum"})
        .nlargest(20, "value")
    )

    fig_bar = px.bar(
        top_stations,
        x="start_station_name",
        y="value",
        title="Top 20 Most Popular Start Stations (2022)",
        color="value",
        color_continuous_scale="Blues"
    )
    fig_bar.update_layout(
        xaxis_title="Station Name",
        yaxis_title="Trip Count",
        xaxis_tickangle=45,
        template="plotly_white",
        title_x=0.5
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("""
    **Insight:**  
    The top stations are concentrated in Manhattan, indicating strong commuter and tourist activity.
    """)

# --- PAGE 4: INTERACTIVE MAP ---
elif page == "Interactive Map":
    st.header("Interactive Geospatial Map – CitiBike Routes")
    st.markdown("""
    This interactive Kepler.gl map visualizes CitiBike trip routes across New York City in 2022.  
    It uses your saved configuration file (**config.json**) to render layers and styles.
    """)

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    map_path = os.path.join(project_root, "citibike_aggregated_map.html")
    config_path = os.path.join(project_root, "notebooks", "config.json")

    if os.path.exists(map_path):
        with open(map_path, "r", encoding="utf-8") as f:
            map_html = f.read()
        st.components.v1.html(map_html, height=600)
    else:
        if os.path.exists(config_path):
            df_map = (
                df.groupby(["start_station_name", "end_station_name", "start_lat", "start_lng", "end_lat", "end_lng"])
                .size()
                .reset_index(name="trip_count")
            )
            with open(config_path, "r", encoding="utf-8") as cfg:
                custom_config = json.load(cfg)["config"]

            map_1 = KeplerGl(height=600, data={"CitiBike 2022": df_map}, config=custom_config)
            map_1.save_to_html(file_name=map_path)
            st.components.v1.html(map_1._repr_html_(), height=600)
        else:
            st.error("Configuration or map file not found. Please check your project paths.")

# --- PAGE 5: RECOMMENDATIONS ---
elif page == "Recommendations":
    st.header("Recommendations and Next Steps")
    st.markdown("""
    ### 📊 Key Takeaways
    - Expand docking stations near high-demand commercial and waterfront zones.  
    - Adjust fleet deployment dynamically based on weather and event forecasts.  
    - Introduce predictive analytics for restocking and maintenance scheduling.  
    - Use temperature thresholds to anticipate ridership drops in colder months.

    ---

    ### 🚲 Presentation Insights

    **1. Scaling bikes between November and April**  
    Based on the *Weather and Bike Usage* analysis, ridership declines sharply in colder months.  
    I recommend **scaling the fleet back by around 25–30%** from November to April, while monitoring weekly usage to stay flexible.

    **2. Adding more stations along the water**  
    From the *Interactive Map* insights, high trip density is visible near waterfront areas.  
    To decide how many stations to add, we can:
    - Use **geospatial clustering** to detect underserved zones  
    - Apply **demand forecasting** using historical trip data  
    - Measure **distance gaps** between current and potential new stations

    **3. Ensuring popular stations stay stocked**  
    Using data from the *Most Popular Stations* section, I suggest:
    - **Predictive rebalancing:** forecast when stations will run empty or full  
    - **Dynamic redistribution:** trigger staff actions based on real-time data  
    - **Incentivized returns:** give small credits to riders who drop bikes at low-stock stations
    """)

# --- FOOTER ---
st.markdown("---")
st.caption("Data Source: CitiBike NYC (2022) | NOAA Weather Data | Dashboard by Brahim Boukaskas")
