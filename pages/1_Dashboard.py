"""
Page 1: Overview Dashboard with 8 KPI Summary Cards and 13 Interactive Charts.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

# Load Custom CSS
CSS_PATH = Path(__file__).parent.parent / "assets" / "style.css"
if CSS_PATH.exists():
    with open(CSS_PATH, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from database.db import (
    fetch_donors, fetch_hospitals, fetch_blood_stock, 
    fetch_donations, fetch_emergency_requests, fetch_health_screenings
)
from components.sidebar import render_sidebar
from components.cards import render_kpi_cards
from components.charts import (
    build_chart_1_availability,
    build_chart_2_blood_group_dist,
    build_chart_3_stock_by_hospital,
    build_chart_4_frequently_donated,
    build_chart_5_monthly_trends,
    build_chart_6_donation_comparison,
    build_chart_7_stock_heatmap,
    build_chart_8_request_funnel,
    build_chart_9_age_distribution,
    build_chart_10_location_map,
    build_chart_11_health_screening,
    build_chart_12_screening_trends,
    build_chart_13_donor_leaderboard
)
from streamlit_folium import st_folium

st.markdown("""
<div class="section-header">
    <div>
        <h2>📊 AI Emergency Blood Bank Analytics Dashboard</h2>
        <p>Real-time telemetry, donor availability status, hospital blood stock, and pre-donation health screening metrics.</p>
    </div>
    <span class="badge badge-red">LIVE TELEMETRY</span>
</div>
""", unsafe_allow_html=True)

# Fetch data from SQLite
donors_df = fetch_donors()
hospitals_df = fetch_hospitals()
stock_df = fetch_blood_stock()
donations_df = fetch_donations()
requests_df = fetch_emergency_requests()
screenings_df = fetch_health_screenings()

# Render Sidebar & apply filters
filters = render_sidebar(donors_df, hospitals_df)

# Filter DataFrames based on sidebar selections
if not donors_df.empty:
    filtered_donors = donors_df[donors_df['blood_group'].isin(filters['blood_groups'])].copy()
    if filters['city'] != "All Locations":
        filtered_donors = filtered_donors[filtered_donors['city_locality'] == filters['city']]
    if filters['availability'] != "All Statuses":
        filtered_donors = filtered_donors[filtered_donors['availability_status'] == filters['availability']]
else:
    filtered_donors = donors_df

if not stock_df.empty:
    filtered_stock = stock_df[stock_df['blood_group'].isin(filters['blood_groups'])].copy()
    if filters['hospital'] != "All Hospitals & Blood Banks":
        filtered_stock = filtered_stock[filtered_stock['centre_name'] == filters['hospital']]
else:
    filtered_stock = stock_df

if not donations_df.empty:
    filtered_donations = donations_df[donations_df['blood_group'].isin(filters['blood_groups'])].copy()
else:
    filtered_donations = donations_df

if not requests_df.empty:
    filtered_requests = requests_df[requests_df['required_blood_group'].isin(filters['blood_groups'])].copy()
    if filters['hospital'] != "All Hospitals & Blood Banks":
        filtered_requests = filtered_requests[filtered_requests['hospital_name'] == filters['hospital']]
    if filters['urgency'] != "All Priorities":
        filtered_requests = filtered_requests[filtered_requests['urgency_level'] == filters['urgency']]
else:
    filtered_requests = requests_df

if not screenings_df.empty:
    filtered_screenings = screenings_df.copy()
    if filters['screening'] != "All Outcomes":
        filtered_screenings = filtered_screenings[filtered_screenings['preliminary_status'] == filters['screening']]
else:
    filtered_screenings = screenings_df

# Calculate KPI values
tot_donors = len(filtered_donors)
avail_donors = len(filtered_donors[filtered_donors['availability_status'] == 'Available']) if not filtered_donors.empty else 0
tot_stock_units = int(filtered_stock['available_units'].sum()) if not filtered_stock.empty else 0
tot_donations_completed = len(filtered_donations[filtered_donations['status'] == 'Completed']) if not filtered_donations.empty else 0
tot_requests = len(filtered_requests)
fulfilled_requests = len(filtered_requests[filtered_requests['status'] == 'Fulfilled']) if not filtered_requests.empty else 0
medical_review_count = len(filtered_screenings[filtered_screenings['preliminary_status'].isin(['Medical Review Required', 'Temporary Deferral and Reassessment'])]) if not filtered_screenings.empty else 0
tot_centres = len(hospitals_df)

# Render 8 Summary Cards
render_kpi_cards(
    tot_donors,
    avail_donors,
    tot_stock_units,
    tot_donations_completed,
    tot_requests,
    fulfilled_requests,
    medical_review_count,
    tot_centres
)

st.write("")

# Tabs for 13 Interactive Charts
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🩸 Donors & Demographics", 
    "🏥 Blood Stock & Inventory", 
    "📈 Donation Trends & Comparison", 
    "🚨 Emergency & Spatial Map", 
    "🩺 Pre-Donation Health Screening"
])

with tab1:
    st.markdown("#### 🩸 Donor Demographics & Availability Analytics")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(build_chart_1_availability(filtered_donors), use_container_width=True)
        st.plotly_chart(build_chart_9_age_distribution(filtered_donors), use_container_width=True)
    with col2:
        st.plotly_chart(build_chart_2_blood_group_dist(filtered_donors), use_container_width=True)
        st.plotly_chart(build_chart_13_donor_leaderboard(filtered_donors), use_container_width=True)

with tab2:
    st.markdown("#### 🏥 Blood Stock Availability & Hospital Inventory")
    col1, col2 = st.columns([3, 2])
    with col1:
        st.plotly_chart(build_chart_3_stock_by_hospital(filtered_stock), use_container_width=True)
    with col2:
        st.plotly_chart(build_chart_7_stock_heatmap(filtered_stock), use_container_width=True)

with tab3:
    st.markdown("#### 📈 Donation Performance & Temporal Trends")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(build_chart_4_frequently_donated(filtered_donations), use_container_width=True)
        st.plotly_chart(build_chart_5_monthly_trends(filtered_donations), use_container_width=True)
    with col2:
        st.plotly_chart(build_chart_6_donation_comparison(filtered_donors, filtered_donations), use_container_width=True)

with tab4:
    st.markdown("#### 🚨 Emergency Request Workflow & Geographic Distribution")
    col1, col2 = st.columns([2, 3])
    with col1:
        st.plotly_chart(build_chart_8_request_funnel(filtered_requests), use_container_width=True)
    with col2:
        st.markdown("##### 📍 Interactive Map: Hospitals & Donor Geolocations")
        st.caption("🔴 Red = Hospitals | 🔵 Blue = Blood Banks | 🟢 Green Circles = Available Donors (Anonymized coordinates)")
        map_obj = build_chart_10_location_map(filtered_donors, hospitals_df)
        st_folium(map_obj, width="100%", height=420, returned_objects=[])

with tab5:
    st.markdown("#### 🩺 Pre-Donation Health Screening Outcomes & Trends")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(build_chart_11_health_screening(filtered_screenings), use_container_width=True)
    with col2:
        st.plotly_chart(build_chart_12_screening_trends(filtered_screenings), use_container_width=True)
