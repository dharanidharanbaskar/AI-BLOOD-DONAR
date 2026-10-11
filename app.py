"""
AI Based Emergency Blood Donor Finder with Pre-Donation Health Screening System
Main Application Entry Point - Karur & Tamil Nadu Emergency GPS Dispatch Hub.
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from pathlib import Path

# Set Page Config
st.set_page_config(
    page_title="MediPulse AI - Karur & Tamil Nadu Blood Donor Finder",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS
CSS_PATH = Path(__file__).parent / "assets" / "style.css"
if CSS_PATH.exists():
    with open(CSS_PATH, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Ensure database is initialized and seeded
from database.db import (
    init_db, fetch_donors, fetch_blood_stock, 
    fetch_emergency_requests, fetch_health_screenings, fetch_hospitals
)
from database.seed_data import generate_sample_data
from utils.analytics import get_compatible_donor_types

init_db()

# Fetch live telemetry from SQLite
donors_df = fetch_donors()
stock_df = fetch_blood_stock()
requests_df = fetch_emergency_requests()
screenings_df = fetch_health_screenings()
hospitals_df = fetch_hospitals()

# Compute Conditional Metrics
tot_donors = len(donors_df)
avail_donors = len(donors_df[donors_df['availability_status'] == 'Available']) if not donors_df.empty else 0
tot_stock_units = int(stock_df['available_units'].sum()) if not stock_df.empty else 0

pending_reqs = requests_df[requests_df['status'].isin(['Received', 'Donor Matched', 'Contacted'])] if not requests_df.empty else pd.DataFrame()
emergency_reqs = requests_df[requests_df['urgency_level'] == 'Emergency'] if not requests_df.empty else pd.DataFrame()

flagged_screenings = screenings_df[screenings_df['preliminary_status'].isin(['Medical Review Required', 'Temporary Deferral and Reassessment'])] if not screenings_df.empty else pd.DataFrame()

# Initialize Session State for Live GPS Coordinates (Default: Karur, Tamil Nadu)
if 'user_lat' not in st.session_state:
    st.session_state['user_lat'] = 10.9601 # Karur Central Town
if 'user_lon' not in st.session_state:
    st.session_state['user_lon'] = 78.0766

# --- 1. CONDITIONAL TOP ALERT BANNERS ---
if not emergency_reqs.empty:
    st.markdown(f"""
    <div class="alert-card-emergency">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <h4 style="margin:0; color:#991B1B;">🚨 ACTIVE EMERGENCY BLOOD DISPATCH ALERT</h4>
                <p style="margin:4px 0 0 0; color:#7F1D1D;">
                    There are <b>{len(emergency_reqs)} high-priority emergency blood requests</b> in Karur & surrounding Tamil Nadu districts.
                </p>
            </div>
            <span class="badge badge-red" style="font-size:0.9rem; padding:6px 14px;">IMMEDIATE ACTION REQUIRED</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
elif not pending_reqs.empty:
    st.markdown(f"""
    <div class="alert-card-warning">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <h4 style="margin:0; color:#9A3412;">⚠️ PENDING BLOOD REQUESTS IN WORKFLOW</h4>
                <p style="margin:4px 0 0 0; color:#7C2D12;">
                    Currently tracking <b>{len(pending_reqs)} pending hospital blood requests</b> undergoing donor matching and notification dispatch.
                </p>
            </div>
            <span class="badge badge-orange" style="font-size:0.85rem;">WORKFLOW ACTIVE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="alert-card-success">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <h4 style="margin:0; color:#065F46;">✅ ALL SYSTEM REPOSITORIES OPERATIONAL</h4>
                <p style="margin:4px 0 0 0; color:#047857;">All hospital inventories, donor registries, and pre-donation screening telemetry are fully synchronized.</p>
            </div>
            <span class="badge badge-green" style="font-size:0.85rem;">STATUS: OPTIMAL</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 2. HERO HEADER BANNER ---
st.markdown("""
<div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); padding: 28px 32px; border-radius: 16px; color: white; margin: 15px 0 25px 0; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.15);">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
        <div style="display:flex; align-items:center; gap:20px;">
            <div style="background:#EF4444; width:60px; height:60px; border-radius:14px; display:flex; align-items:center; justify-content:center; font-size:2.2rem; box-shadow:0 4px 12px rgba(239,68,68,0.4);">
                🩸
            </div>
            <div>
                <h1 style="margin:0; color:#FFFFFF; font-size:2.1rem; font-weight:800; letter-spacing:-0.5px;">
                    MediPulse AI - Karur & Tamil Nadu Hub
                </h1>
                <p style="margin:4px 0 0 0; color:#94A3B8; font-size:1.05rem;">
                    Emergency Blood Donor Finder & Pre-Donation Health Screening Dashboard
                </p>
            </div>
        </div>
        <div style="text-align:right;">
            <span style="background:rgba(16, 185, 129, 0.2); color:#34D399; border:1px solid #059669; padding:6px 14px; border-radius:20px; font-weight:700; font-size:0.85rem; display:inline-block;">
                ● KARUR NETWORK LIVE
            </span>
            <div style="color:#64748B; font-size:0.78rem; margin-top:6px;">Region: Karur, Trichy, Erode, Namakkal, Dindigul, Salem</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 3. PRO-LEVEL GPS LIVE LOCATION & PROXIMITY HUB (TAMIL NADU / KARUR FOCUS) ---
st.markdown("### 🛰️ PRO-LEVEL GPS LIVE LOCATION & PROXIMITY SENSOR HUB (KARUR & SURROUNDING DISTRICTS)")
st.caption("Acquire real-time GPS coordinates to calculate spatial Haversine proximity to nearest emergency blood repositories & compatible donors in Karur, Trichy, Erode, Namakkal, etc.")

# HTML5 Geolocation JavaScript Bridge Component
js_geo_code = """
<script>
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition, showError);
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}
function showPosition(position) {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;
    const acc = position.coords.accuracy;
    document.getElementById("status").innerHTML = 
        `<span style="color:#10B981; font-weight:bold;">✅ Live GPS Acquired!</span><br>Lat: <b>${lat.toFixed(5)}</b>, Lon: <b>${lon.toFixed(5)}</b> (Accuracy: ${acc.toFixed(0)}m)`;
}
function showError(error) {
    document.getElementById("status").innerHTML = "<span style='color:#EF4444;'>GPS acquisition prompt rejected or unavailable. Using high-precision Karur locator.</span>";
}
</script>
<div style="background:#0F172A; padding:16px; border-radius:12px; color:white; font-family:sans-serif;">
    <button onclick="getLocation()" style="background:#DC2626; color:white; border:none; padding:10px 18px; border-radius:8px; font-weight:bold; cursor:pointer; font-size:0.9rem;">
        🛰️ Acquire Live Device GPS Coordinates
    </button>
    <div id="status" style="margin-top:10px; font-size:0.85rem; color:#94A3B8;">Click button above to trigger device HTML5 GPS sensor.</div>
</div>
"""

col_gps1, col_gps2 = st.columns([1, 2])

with col_gps1:
    components.html(js_geo_code, height=125)
    
    st.markdown("##### 📍 Karur & Surrounding Tamil Nadu Presets")
    preset = st.selectbox("Quick GPS Locality Presets:", [
        "Karur (10.9601, 78.0766)",
        "Chennai (Capital City) (13.0827, 80.2707)",
        "Coimbatore (11.0168, 76.9558)",
        "Madurai (9.9252, 78.1198)",
        "Tiruchirappalli (Trichy) (10.7905, 78.7047)",
        "Tiruppur (11.1085, 77.3411)",
        "Salem (11.6643, 78.1460)",
        "Erode (11.3410, 77.7172)",
        "Tirunelveli (8.7139, 77.7567)",
        "Vellore (12.9165, 79.1325)",
        "Thoothukudi (Tuticorin) (8.7642, 78.1348)",
        "Dindigul (10.3673, 77.9803)",
        "Thanjavur (10.7870, 79.1378)",
        "Nagercoil (8.1833, 77.4119)",
        "Hosur (12.7409, 77.8253)",
        "Kumbakonam (10.9602, 79.3782)"
    ])

    if preset == "Karur (10.9601, 78.0766)":
        st.session_state['user_lat'], st.session_state['user_lon'] = 10.9601, 78.0766
    elif preset == "Chennai (Capital City) (13.0827, 80.2707)":
        st.session_state['user_lat'], st.session_state['user_lon'] = 13.0827, 80.2707
    elif preset == "Coimbatore (11.0168, 76.9558)":
        st.session_state['user_lat'], st.session_state['user_lon'] = 11.0168, 76.9558
    elif preset == "Madurai (9.9252, 78.1198)":
        st.session_state['user_lat'], st.session_state['user_lon'] = 9.9252, 78.1198
    elif preset == "Tiruchirappalli (Trichy) (10.7905, 78.7047)":
        st.session_state['user_lat'], st.session_state['user_lon'] = 10.7905, 78.7047
    elif preset == "Tiruppur (11.1085, 77.3411)":
        st.session_state['user_lat'], st.session_state['user_lon'] = 11.1085, 77.3411
    elif preset == "Salem (11.6643, 78.1460)":
        st.session_state['user_lat'], st.session_state['user_lon'] = 11.6643, 78.1460
    elif preset == "Erode (11.3410, 77.7172)":
        st.session_state['user_lat'], st.session_state['user_lon'] = 11.3410, 77.7172
    elif preset == "Tirunelveli (8.7139, 77.7567)":
        st.session_state['user_lat'], st.session_state['user_lon'] = 8.7139, 77.7567
    elif preset == "Vellore (12.9165, 79.1325)":
        st.session_state['user_lat'], st.session_state['user_lon'] = 12.9165, 79.1325
    elif preset == "Thoothukudi (Tuticorin) (8.7642, 78.1348)":
        st.session_state['user_lat'], st.session_state['user_lon'] = 8.7642, 78.1348
    elif preset == "Dindigul (10.3673, 77.9803)":
        st.session_state['user_lat'], st.session_state['user_lon'] = 10.3673, 77.9803
    elif preset == "Thanjavur (10.7870, 79.1378)":
        st.session_state['user_lat'], st.session_state['user_lon'] = 10.7870, 79.1378
    elif preset == "Nagercoil (8.1833, 77.4119)":
        st.session_state['user_lat'], st.session_state['user_lon'] = 8.1833, 77.4119
    elif preset == "Hosur (12.7409, 77.8253)":
        st.session_state['user_lat'], st.session_state['user_lon'] = 12.7409, 77.8253
    elif preset == "Kumbakonam (10.9602, 79.3782)":
        st.session_state['user_lat'], st.session_state['user_lon'] = 10.9602, 79.3782

    cur_lat = st.number_input("Latitude:", value=float(st.session_state['user_lat']), format="%.5f")
    cur_lon = st.number_input("Longitude:", value=float(st.session_state['user_lon']), format="%.5f")
    req_bg_gps = st.selectbox("Required Blood Group for Live Matching:", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])

user_lat = cur_lat
user_lon = cur_lon

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return (R * c).round(2)

if not hospitals_df.empty:
    hosp_calc = hospitals_df.copy()
    hosp_calc['distance_km'] = haversine_km(user_lat, user_lon, hosp_calc['latitude'], hosp_calc['longitude'])
    hosp_calc = hosp_calc.sort_values('distance_km').head(3)
else:
    hosp_calc = pd.DataFrame()

compat_bg_list = get_compatible_donor_types(req_bg_gps)

if not donors_df.empty:
    donor_calc = donors_df[
        (donors_df['blood_group'].isin(compat_bg_list)) & 
        (donors_df['availability_status'] == 'Available')
    ].copy()
    if not donor_calc.empty:
        donor_calc['distance_km'] = haversine_km(user_lat, user_lon, donor_calc['latitude'], donor_calc['longitude'])
        donor_calc = donor_calc.sort_values('distance_km').head(5)
else:
    donor_calc = pd.DataFrame()

with col_gps2:
    st.markdown("##### 🏥 Top 3 Nearest Hospitals & Emergency Contact")
    if not hosp_calc.empty:
        for _, h_row in hosp_calc.iterrows():
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #2563EB; padding:10px 14px; border-radius:8px; margin-bottom:8px;">
                <div style="display:flex; justify-content:space-between;">
                    <b>🏥 {h_row['centre_name']} ({h_row['centre_type']})</b>
                    <span class="badge badge-blue">📍 {h_row['distance_km']} km away</span>
                </div>
                <div style="font-size:0.82rem; color:#475569; margin-top:4px;">
                    District/Zone: {h_row['location']} | 📞 Emergency Contact: <b style="color:#DC2626;">{h_row['emergency_contact']}</b> | Estimated ETA: <b>{int(h_row['distance_km']*2.5)} mins</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(f"##### 🩸 Nearest Compatible Available Donors ({len(donor_calc)} Found for {req_bg_gps})")
    if not donor_calc.empty:
        st.dataframe(
            donor_calc[['donor_id', 'name', 'blood_group', 'distance_km', 'city_locality', 'contact_number']],
            use_container_width=True,
            hide_index=True
        )

# Render Proximity Map
m_gps = folium.Map(
    location=[user_lat, user_lon], 
    zoom_start=11, 
    tiles="OpenStreetMap",
    attr="🇮🇳 India Emergency Blood Network - Karur | © OpenStreetMap"
)

# Live User GPS Marker
folium.Marker(
    location=[user_lat, user_lon],
    popup=f"<b>🛰️ YOUR GPS LOCATION (KARUR/TN)</b><br>Lat: {user_lat:.4f}, Lon: {user_lon:.4f}",
    tooltip="🛰️ Your Detected GPS Location",
    icon=folium.Icon(color="darkred", icon="crosshairs", prefix="fa")
).add_to(m_gps)

# 10km Radius Circle
folium.Circle(
    location=[user_lat, user_lon],
    radius=10000,
    color="#DC2626",
    fill=True,
    fill_color="#DC2626",
    fill_opacity=0.10,
    popup="10 km Emergency Response Radius"
).add_to(m_gps)

# Plot Hospitals
if not hosp_calc.empty:
    for _, h_row in hosp_calc.iterrows():
        folium.Marker(
            location=[h_row['latitude'], h_row['longitude']],
            popup=f"<b>{h_row['centre_name']}</b><br>Distance: {h_row['distance_km']} km<br>Phone: {h_row['emergency_contact']}",
            tooltip=f"{h_row['centre_name']} ({h_row['distance_km']} km)",
            icon=folium.Icon(color="blue", icon="hospital-o", prefix="fa")
        ).add_to(m_gps)

        folium.PolyLine(
            locations=[[user_lat, user_lon], [h_row['latitude'], h_row['longitude']]],
            color="#2563EB",
            weight=2,
            dash_array="5, 10"
        ).add_to(m_gps)

st.markdown("##### 🗺️ Karur & Surrounding Tamil Nadu Districts Proximity Map")
st_folium(m_gps, width="100%", height=400, returned_objects=[])

st.divider()

# --- 4. LIVE SYSTEM TELEMETRY MINI-CARDS ---
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    readiness_pct = round((avail_donors / max(tot_donors, 1)) * 100, 1)
    st.markdown(f"""
    <div class="kpi-card accent-green" style="padding:16px;">
        <div class="kpi-header">
            <span class="kpi-title">Active Donors Ready</span>
            <span style="font-size:1.3rem;">✅</span>
        </div>
        <div class="kpi-value">{avail_donors:,}</div>
        <div class="kpi-subtext">
            <span class="kpi-trend-up"><b>{readiness_pct}%</b> of {tot_donors:,} registered donors</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown(f"""
    <div class="kpi-card accent-blue" style="padding:16px;">
        <div class="kpi-header">
            <span class="kpi-title">Total Blood Stock</span>
            <span style="font-size:1.3rem;">🏥</span>
        </div>
        <div class="kpi-value">{tot_stock_units:,} u</div>
        <div class="kpi-subtext">
            <span class="kpi-trend-neutral">Across 10 hospital centers</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_m3:
    req_color_class = "kpi-trend-alert" if len(emergency_reqs) > 0 else "kpi-trend-neutral"
    st.markdown(f"""
    <div class="kpi-card accent-red" style="padding:16px;">
        <div class="kpi-header">
            <span class="kpi-title">Pending Requests</span>
            <span style="font-size:1.3rem;">🚨</span>
        </div>
        <div class="kpi-value">{len(pending_reqs):,}</div>
        <div class="kpi-subtext">
            <span class="{req_color_class}"><b>{len(emergency_reqs)}</b> emergency urgency</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_m4:
    review_pct = round((len(flagged_screenings) / max(len(screenings_df), 1)) * 100, 1)
    st.markdown(f"""
    <div class="kpi-card accent-orange" style="padding:16px;">
        <div class="kpi-header">
            <span class="kpi-title">Screening Flags</span>
            <span style="font-size:1.3rem;">🩺</span>
        </div>
        <div class="kpi-value">{len(flagged_screenings):,}</div>
        <div class="kpi-subtext">
            <span class="kpi-trend-alert"><b>{review_pct}%</b> require medical review</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# --- 5. INTERACTIVE MODULE ACCESS CARDS GRID ---
st.markdown("### 🚀 System Modules & Dashboard Capabilities")

row1_col1, row1_col2, row1_col3 = st.columns(3)

with row1_col1:
    st.markdown("""
    <div class="kpi-card accent-red" style="padding:22px; height:240px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:2rem;">📊</span>
            <span class="badge badge-red">CORE DASHBOARD</span>
        </div>
        <h3 style="margin:10px 0 6px 0; color:#0F172A;">Overview Analytics</h3>
        <p style="font-size:0.88rem; color:#475569; margin-bottom:15px; line-height:1.4;">
            8 summary KPI cards & 13 interactive Plotly and Folium visualizations covering donor availability, stock heatmaps, and screening telemetry.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚀 Open Overview Dashboard", key="btn_dash", type="primary", use_container_width=True):
        st.switch_page("pages/1_Dashboard.py")

with row1_col2:
    st.markdown("""
    <div class="kpi-card accent-blue" style="padding:22px; height:240px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:2rem;">👥</span>
            <span class="badge badge-blue">DONOR DIRECTORY</span>
        </div>
        <h3 style="margin:10px 0 6px 0; color:#0F172A;">Donor Management</h3>
        <p style="font-size:0.88rem; color:#475569; margin-bottom:15px; line-height:1.4;">
            Search 150+ donor profiles, register new donors, update status, and switch between Staff view and Public Anonymized Privacy view.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("👥 Open Donor Management", key="btn_donor", use_container_width=True):
        st.switch_page("pages/2_Donor_Management.py")

with row1_col3:
    st.markdown("""
    <div class="kpi-card accent-green" style="padding:22px; height:240px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:2rem;">🏥</span>
            <span class="badge badge-green">INVENTORY CONTROL</span>
        </div>
        <h3 style="margin:10px 0 6px 0; color:#0F172A;">Blood Stock Inventory</h3>
        <p style="font-size:0.88rem; color:#475569; margin-bottom:15px; line-height:1.4;">
            Track blood unit availability across 10 hospital repositories, trigger low-stock alert thresholds, and log stock level updates.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🏥 Open Blood Stock", key="btn_stock", use_container_width=True):
        st.switch_page("pages/3_Blood_Stock.py")

st.write("")

row2_col1, row2_col2, row2_col3 = st.columns(3)

with row2_col1:
    st.markdown("""
    <div class="kpi-card accent-rose" style="padding:22px; height:240px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:2rem;">🚨</span>
            <span class="badge badge-red">AI MATCHING ENGINE</span>
        </div>
        <h3 style="margin:10px 0 6px 0; color:#0F172A;">Emergency Request Matcher</h3>
        <p style="font-size:0.88rem; color:#475569; margin-bottom:15px; line-height:1.4;">
            Submit emergency requests, compute Haversine spatial distance & biological compatibility scores, and simulate SMS notification alerts.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚨 Open Emergency Matcher", key="btn_req", use_container_width=True):
        st.switch_page("pages/4_Emergency_Requests.py")

with row2_col2:
    st.markdown("""
    <div class="kpi-card accent-purple" style="padding:22px; height:240px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:2rem;">🩺</span>
            <span class="badge badge-purple">PRE-DONATION SAFETY</span>
        </div>
        <h3 style="margin:10px 0 6px 0; color:#0F172A;">Pre-Donation Health Screening</h3>
        <p style="font-size:0.88rem; color:#475569; margin-bottom:15px; line-height:1.4;">
            Evaluate preliminary vital sensors (Temp, HR, SpO2, BP) against physiological reference ranges with physician manual override.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🩺 Open Health Screening", key="btn_scr", use_container_width=True):
        st.switch_page("pages/5_Health_Screening.py")

with row2_col3:
    st.markdown("""
    <div class="kpi-card accent-orange" style="padding:22px; height:240px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:2rem;">💡</span>
            <span class="badge badge-orange">INTELLIGENCE & EXPORT</span>
        </div>
        <h3 style="margin:10px 0 6px 0; color:#0F172A;">Analytics & AI Forecasting</h3>
        <p style="font-size:0.88rem; color:#475569; margin-bottom:15px; line-height:1.4;">
            Review real-time dynamic text insights, AI 30-day demand prediction forecasting models, and download raw database CSV files.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("💡 Open Intelligence & CSV Export", key="btn_ana", use_container_width=True):
        st.switch_page("pages/6_Analytics.py")

st.markdown("---")
st.caption("ℹ️ *Medical Disclaimer: Sensor readings and rule evaluations serve strictly as preliminary indicators. Final donor clearance must be performed by qualified healthcare personnel.*")
