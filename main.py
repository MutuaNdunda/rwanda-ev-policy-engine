import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="SmartDash MVP – Kigali EV Dashboard",
    layout="wide"
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# ---------------------------------------------------
# LOAD DATASETS
# ---------------------------------------------------
BASE_URL = "https://raw.githubusercontent.com/MutuaNdunda/smartdash_mvp/refs/heads/main/data"

@st.cache_data
def load(name):
    url = f"{BASE_URL}/{name}"
    return pd.read_csv(url)

# Load all datasets from GitHub raw URLs
ev = load("ev_adoption.csv")
stations = load("charging_stations.csv")
tariffs = load("tariffs.csv")
grid = load("grid_load_week.csv")
sessions = load("charging_sessions.csv")
policies = load("policy_timeline.csv")
investment = load("charging_investment.csv")
imports = load("ev_imports.csv")
sectors = load("sector_consumption.csv")
districts = load("districts.csv")
feedback = load("user_feedback.csv")

# ---------------------------------------------------
# SIDEBAR FILTERS (GLOBAL)
# ---------------------------------------------------
st.sidebar.title("Filters")

year_selected = st.sidebar.selectbox(
    "Select Year",
    sorted(ev["Year"].unique())
)

district_selected = st.sidebar.multiselect(
    "Select Districts",
    stations["District"].unique(),
    default=list(stations["District"].unique())
)

# ---------------------------------------------------
# MAIN HEADER
# ---------------------------------------------------
st.title("SmartDash MVP – Kigali EV Dashboard")
st.caption("Demonstration using simulated datasets.")

# ---------------------------------------------------
# TABS
# ---------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Overview",
    "EV Adoption",
    "Charging Infrastructure",
    "Energy & Grid",
    "Policy & Investment",
    "User Feedback"
])

# ===================================================
# TAB 1: OVERVIEW
# ===================================================
with tab1:
    st.header("Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    selected_row = ev[ev["Year"] == year_selected].iloc[0]

    col1.metric("Total EVs", f"{int(selected_row['EV_Total']):,}")
    col2.metric("EV 2-Wheelers", f"{int(selected_row['EV_2W']):,}")
    col3.metric("Charging Stations", len(stations))
    col4.metric(
        "EV Tariff (RWF/kWh)",
        int(tariffs[tariffs["Tariff_Type"] == "EV_Tariff"]["Price_RWF_per_kWh"].values[0])
    )

    st.subheader("EV Adoption Trend")
    fig = px.line(ev, x="Year", y="EV_Total", markers=True)
    st.plotly_chart(fig, width="stretch")

    st.subheader("Charging Station Map")

    filtered_map = stations[stations["District"].isin(district_selected)].copy()
    filtered_map = filtered_map.rename(columns={"Latitude": "latitude", "Longitude": "longitude"})
    st.map(filtered_map[["latitude", "longitude"]])

    st.subheader("Quick Insights")
    st.write("""
    - EV growth is dominated by 2-wheelers.  
    - Charging infrastructure is concentrated in Kigali.  
    - Evening charging significantly increases grid load.  
    """)
    st.subheader("Demo Video")
    st.video("https://youtu.be/TdP2X5-MQ08")


# ===================================================
# TAB 2: EV ADOPTION
# ===================================================
with tab2:
    st.header("EV Adoption Analysis")

    st.subheader("EV by Category (Annual)")
    fig_ev_cat = px.line(
        ev,
        x="Year",
        y=["EV_2W", "EV_3W", "EV_Cars", "EV_Buses"],
        markers=True
    )
    st.plotly_chart(fig_ev_cat, width="stretch")

    st.subheader("EV Imports (Simulated)")
    fig_imports = px.bar(imports, x="Year", y="Imported_EV_Count")
    st.plotly_chart(fig_imports, width="stretch")

    st.subheader("District-Level Attributes")
    st.dataframe(districts, use_container_width=True)

# ===================================================
# TAB 3: CHARGING INFRASTRUCTURE
# ===================================================
with tab3:
    st.header("Charging Infrastructure")

    st.subheader("Station Overview")
    st.dataframe(stations.head(50), use_container_width=True)

    st.subheader("Stations per District")
    fig_dist = px.bar(
        stations.groupby("District").size().reset_index(name="Count"),
        x="District",
        y="Count"
    )
    st.plotly_chart(fig_dist, width="stretch")

    st.subheader("Charging Network Map")
    map_df = stations.copy().rename(columns={
        "Latitude": "latitude",
        "Longitude": "longitude"
    })
    st.map(map_df[["latitude", "longitude"]])

    st.subheader("Charger Types")
    fig_types = px.pie(stations, names="Charger_Type")
    st.plotly_chart(fig_types, width="stretch")

# ===================================================
# TAB 4: ENERGY & GRID
# ===================================================
with tab4:
    st.header("Energy Pricing & Grid Load")

    st.subheader("Energy Tariffs")
    st.dataframe(tariffs, use_container_width=True)

    st.subheader("Grid Load Curve (Daily Average)")
    daily = grid.groupby("Hour").mean().reset_index()
    fig_grid = px.line(
        daily,
        x="Hour",
        y=["Baseline_Load_kWh", "EV_Load_kWh", "Total_Load_kWh"]
    )
    st.plotly_chart(fig_grid, width="stretch")

    st.subheader("Charging Session Energy Distribution")
    fig_hist = px.histogram(sessions, x="Energy_Consumed_kWh", nbins=40)
    st.plotly_chart(fig_hist, width="stretch")

    st.subheader("Electricity Consumption by Sector")
    fig_sector = px.bar(sectors, x="Sector", y="Annual_Consumption_GWh")
    st.plotly_chart(fig_sector, width="stretch")

# ===================================================
# TAB 5: POLICY & INVESTMENT
# ===================================================
with tab5:
    st.header("Policy Timeline & Investment Costs")

    st.subheader("Policy Timeline")
    st.dataframe(policies, use_container_width=True)

    st.subheader("Charging Investment Costs")
    st.dataframe(investment, use_container_width=True)

# ===================================================
# TAB 6: USER FEEDBACK
# ===================================================
with tab6:
    st.header("User Feedback (Simulated)")

    colA, colB = st.columns(2)
    colA.metric("Avg Usability Rating", round(feedback["Usability_Rating"].mean(), 2))
    colB.metric("Avg Clarity Rating", round(feedback["Clarity_Rating"].mean(), 2))

    st.subheader("Responses")
    st.dataframe(feedback, use_container_width=True)

    st.subheader("Comments")
    for _, r in feedback.iterrows():
        st.write(f"- {r['Comments']}")
