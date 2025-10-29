# st_dashboard_part_2.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIG ---
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

# --- LOAD DATA FUNCTION ---
@st.cache_data
def load_data():
    try:
        # ✅ Dropbox direct download link
        url = "https://www.dropbox.com/scl/fi/8q9mvx7nawv6w0jyd1weg/citibike_weather_2022.csv?rlkey=1ror146lz3rofxchwwqpsxn2l&st=k4e5zsue&dl=1"

        df = pd.read_csv(url, low_memory=False, on_bad_lines="skip")

        # --- Normalize column names ---
        df.columns = [c.strip().replace(" ", "_").lower() for c in df.columns]

        # --- Create a consistent 'date' column ---
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        elif "started_at" in df.columns:
            df["date"] = pd.to_datetime(df["started_at"], errors="coerce").dt.date
        else:
            df["date"] = pd.NaT

        # Drop rows missing essential info
        df = df.dropna(subset=["date"])

        st.success(f"✅ Data loaded successfully — {len(df):,} rows.")
        return df

    except Exception as e:
        st.error(f"❌ Failed to load data: {e}")
        # Return an empty DataFrame with all expected columns
        cols = [
            "date", "start_station_name", "start_lat", "start_lng", "avgtemp",
            "ride_id", "rideable_type", "member_casual"
        ]
        return pd.DataFrame(columns=cols)

# --- SAFETY NET: Load Data ---
try:
    df = load_data()
except Exception as e:
    st.error(f"Unexpected error while loading data: {e}")
    df = pd.DataFrame(columns=["date"])

# --- PAGE 1: INTRODUCTION ---
if page == "Introduction":
    st.title("CitiBike NYC 2022 Dashboard")
    st.markdown("""
    This dashboard explores **New York City’s CitiBike system (2022)** —  
    showing how weather affects ridership, which stations are busiest,  
    and where expansion could be most effective.
    """)

    st.markdown("""
    **Sections**
    - Weather and Bike Usage  
    - Most Popular Stations  
    - Interactive Map  
    - Recommendations
    """)

    if df.empty:
        st.warning("⚠️ No data loaded yet. Please check your dataset link.")
    else:
        st.subheader("Preview of Loaded Data")
        st.dataframe(df.head())

# --- PAGE 2: WEATHER AND BIKE USAGE ---
elif page == "Weather and Bike Usage":
    st.header("Weather and Bike Usage")

    if df.empty:
        st.warning("⚠️ No data available for analysis.")
    else:
        daily_trips = df.groupby("date").size().reset_index(name="trip_count")

        if "avgtemp" in df.columns:
            daily_temp = df.groupby("date")["avgtemp"].mean().reset_index()
            daily_data = pd.merge(daily_trips, daily_temp, on="date", how="left")
        else:
            daily_data = daily_trips.copy()
            daily_data["avgtemp"] = None

        fig_dual = go.Figure()
        fig_dual.add_trace(go.Scatter(
            x=daily_data["date"],
            y=daily_data["trip_count"],
            name="Daily Trips",
            mode="lines",
            line=dict(color="royalblue")
        ))

        if daily_data["avgtemp"].notna().any():
            fig_dual.add_trace(go.Scatter(
                x=daily_data["date"],
                y=daily_data["avgtemp"],
                name="Average Temperature (°C)",
                mode="lines",
                line=dict(color="tomato"),
                yaxis="y2"
            ))
            fig_dual.update_layout(
                yaxis2=dict(title="Temperature (°C)", overlaying="y", side="right")
            )

        fig_dual.update_layout(
            title="Daily CitiBike Trips vs Temperature (2022)",
            xaxis_title="Date",
            yaxis_title="Trip Count",
            template="plotly_white",
            title_x=0.5
        )
        st.plotly_chart(fig_dual, use_container_width=True)
        st.markdown("**Observation:** Ridership rises with temperature and declines in colder months.")

# --- PAGE 3: MOST POPULAR STATIONS ---
elif page == "Most Popular Stations":
    st.header("Most Popular Start Stations")

    if df.empty or "start_station_name" not in df.columns:
        st.warning("⚠️ Missing column 'start_station_name' in dataset.")
    else:
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
            color="value",
            color_continuous_scale="Blues",
            title="Top 20 Start Stations (2022)"
        )
        fig_bar.update_layout(
            xaxis_title="Station Name",
            yaxis_title="Trip Count",
            xaxis_tickangle=45,
            template="plotly_white",
            title_x=0.5
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("**Insight:** Busiest stations cluster in Manhattan — strong commuter and tourist flow.")

# --- PAGE 4: INTERACTIVE MAP ---
elif page == "Interactive Map":
    st.header("Interactive Map – CitiBike Stations and Routes")
    st.markdown("Each point represents a start station sized by total trip count.")

    if df.empty or not {"start_station_name", "start_lat", "start_lng"}.issubset(df.columns):
        st.warning("⚠️ Missing required columns for map visualization.")
    else:
        df_map = (
            df.groupby(["start_station_name", "start_lat", "start_lng"], as_index=False)
            .size()
            .rename(columns={"size": "trip_count"})
        )

        fig_map = px.scatter_mapbox(
            df_map,
            lat="start_lat",
            lon="start_lng",
            size="trip_count",
            hover_name="start_station_name",
            color="trip_count",
            color_continuous_scale="Viridis",
            zoom=11,
            height=600
        )
        fig_map.update_layout(
            mapbox_style="open-street-map",
            title="CitiBike Start Stations (2022)",
            margin={"r":0, "t":40, "l":0, "b":0}
        )
        st.plotly_chart(fig_map, use_container_width=True)

# --- PAGE 5: RECOMMENDATIONS ---
elif page == "Recommendations":
    st.header("Recommendations and Next Steps")
    st.markdown("""
    ### Key Takeaways
    - Expand docking stations near high-demand and waterfront zones.  
    - Adjust fleet dynamically based on weather & events.  
    - Use predictive analytics for restocking and maintenance.  
    - Anticipate ridership drops below 10 °C.

    ### Presentation Insights
    **1. Seasonal Scaling** — Reduce fleet ~25–30 % from Nov to Apr.  
    **2. Waterfront Growth** — Add stations using geospatial clustering + demand forecasting.  
    **3. Stock Balance** — Predictive rebalancing & user incentives keep busy stations filled.
    """)

# --- FOOTER ---
st.markdown("---")
st.caption("Data Source: CitiBike NYC (2022) | NOAA Weather Data | Dashboard by Brahim Boukaskas")
