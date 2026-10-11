"""
Page 4: Emergency Blood Request, AI Donor Matching & Live Donor Transit Tracking Radar System.
"""

import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from datetime import datetime
from pathlib import Path

# Load Custom CSS
CSS_PATH = Path(__file__).parent.parent / "assets" / "style.css"
if CSS_PATH.exists():
    with open(CSS_PATH, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from database.db import (
    fetch_emergency_requests, fetch_donors, fetch_hospitals, 
    fetch_health_screenings, insert_emergency_request, update_request_status
)
from utils.analytics import compute_ai_donor_matches, BLOOD_COMPATIBILITY_MATRIX

def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate Haversine spatial distance between two points in km."""
    R = 6371.0
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return round(float(R * c), 2)

st.markdown("""
<div class="section-header">
    <div>
        <h2>🚨 Emergency Blood Request & Live Donor Transit Engine</h2>
        <p>Submit emergency requests, identify compatible donors, simulate SMS notifications, and track live donor transit journeys to hospitals.</p>
    </div>
    <span class="badge badge-red">EMERGENCY DISPATCH & RADAR</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="medical-disclaimer">
    ⚠️ <b>Clinical Safety Disclaimer:</b> Potential donor matching is based on blood group compatibility rules, proximity, and preliminary health flags. It does NOT guarantee clinical cross-match compatibility. Standard serological testing must precede transfusion.
</div>
""", unsafe_allow_html=True)

requests_df = fetch_emergency_requests()
donors_df = fetch_donors()
hospitals_df = fetch_hospitals()
screenings_df = fetch_health_screenings()

# Navigation Tabs: Submit Request | AI Donor Matcher | Request Status Tracker | Live Donor Transit Radar
tab_new, tab_match, tab_track, tab_transit = st.tabs([
    "➕ Submit Emergency Request", 
    "🤖 AI Donor Compatibility Matcher", 
    "📋 Track & Update Requests",
    "🛰️ Live Donor Journey Tracker (GPS Transit Radar)"
])

with tab_new:
    st.markdown("##### 📝 Hospital Emergency Dispatch Form")
    with st.form("emergency_request_form"):
        col_r1, col_r2, col_r3 = st.columns(3)

        with col_r1:
            if not hospitals_df.empty:
                h_options = {row['centre_name']: row for _, row in hospitals_df.iterrows()}
                selected_h_name = st.selectbox("Requesting Hospital / Centre *", list(h_options.keys()))
                sel_hosp = h_options[selected_h_name]
                req_centre_id = sel_hosp['centre_id']
                req_loc = sel_hosp['location']
                req_lat = sel_hosp['latitude']
                req_lon = sel_hosp['longitude']
            else:
                selected_h_name = "Karur Govt Medical College"
                req_centre_id = "CTR-01"
                req_loc = "Karur Town"
                req_lat = 10.9601
                req_lon = 78.0766

        with col_r2:
            req_bg = st.selectbox("Required Blood Group *", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            req_units = st.number_input("Required Units *", min_value=1, max_value=20, value=2)

        with col_r3:
            req_urgency = st.selectbox("Urgency Level *", ["Normal", "Urgent", "Emergency"])

        submit_req = st.form_submit_button("🚨 Submit Emergency Dispatch Request", type="primary", use_container_width=True)

        if submit_req:
            now_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            next_req_id = f"REQ-{8000 + len(requests_df) + 1}"
            
            # Compute quick count of compatible donors
            quick_matches = compute_ai_donor_matches(req_bg, req_lat, req_lon, donors_df, screenings_df)
            match_cnt = len(quick_matches)

            req_payload = {
                "request_id": next_req_id,
                "hospital_name": selected_h_name,
                "centre_id": req_centre_id,
                "required_blood_group": req_bg,
                "required_units": int(req_units),
                "urgency_level": req_urgency,
                "request_datetime": now_dt,
                "location": req_loc,
                "latitude": float(req_lat),
                "longitude": float(req_lon),
                "status": "Donor Matched" if match_cnt > 0 else "Received",
                "matched_donors_count": match_cnt
            }
            insert_emergency_request(req_payload)
            st.success(f"Emergency request submitted! Request ID: **{next_req_id}** (Found {match_cnt} potential donor matches).")
            st.rerun()

with tab_match:
    st.markdown("##### 🤖 Interactive AI Donor Matcher & Dispatch Simulator")
    if not requests_df.empty:
        active_req_ids = requests_df['request_id'].tolist()
        sel_match_req = st.selectbox("Select Active Emergency Request ID:", active_req_ids)
        target_req = requests_df[requests_df['request_id'] == sel_match_req].iloc[0]

        st.markdown(f"""
        <div class="alert-card-warning">
            <b>Request Target:</b> {target_req['hospital_name']} | <b>Required Blood Group:</b> <span style="color:#DC2626; font-weight:bold;">{target_req['required_blood_group']}</span> | <b>Units Needed:</b> {target_req['required_units']} | <b>Urgency:</b> {target_req['urgency_level']}
        </div>
        """, unsafe_allow_html=True)

        # Run AI matching
        matches = compute_ai_donor_matches(
            target_req['required_blood_group'],
            target_req['latitude'],
            target_req['longitude'],
            donors_df,
            screenings_df
        )

        st.markdown(f"#### 🎯 Compatible Donors Ranked by AI Match Score ({len(matches)} matches)")
        st.caption("AI Match Score combines Blood Compatibility (30%), Proximity Distance (40%), Pre-donation Screening Flag (20%), and Donation Experience (10%).")

        if not matches.empty:
            st.dataframe(
                matches[[
                    'donor_id', 'name', 'blood_group', 'availability_status', 
                    'distance_km', 'ai_match_score', 'preliminary_status', 
                    'contact_number', 'city_locality'
                ]],
                use_container_width=True,
                hide_index=True
            )

            st.write("")
            st.markdown("##### 📡 Trigger Notification Simulation")
            col_not1, col_not2 = st.columns([3, 1])
            with col_not1:
                max_val = max(1, min(10, len(matches)))
                default_val = min(3, max_val)
                notify_top_n = st.slider(
                    "Select Top N Donors to Notify via Automated SMS/Email Alert:",
                    min_value=1,
                    max_value=max_val,
                    value=default_val
                )
            with col_not2:
                st.write("")
                st.write("")
                if st.button("📲 Dispatch Emergency Alerts", type="primary", use_container_width=True):
                    notified_donors = matches.head(notify_top_n)
                    st.success(f"⚡ Emergency SMS & Push notifications dispatched to top {notify_top_n} donors:")
                    for _, d_row in notified_donors.iterrows():
                        st.write(f"- 📩 Notification sent to **{d_row['name']}** ({d_row['donor_id']}) | Dist: **{d_row['distance_km']} km** | AI Score: **{d_row['ai_match_score']}%**")
                    update_request_status(sel_match_req, "Contacted")
        else:
            st.warning("No compatible available donors found in the immediate area for this blood group.")

with tab_track:
    st.markdown("##### 📋 Emergency Request Status Tracking & Updates")
    st.dataframe(
        requests_df[[
            'request_id', 'hospital_name', 'required_blood_group', 
            'required_units', 'urgency_level', 'request_datetime', 
            'location', 'status', 'matched_donors_count'
        ]],
        use_container_width=True,
        hide_index=True
    )

    st.divider()
    st.markdown("##### 🔄 Update Request Status")
    if not requests_df.empty:
        with st.form("update_req_form"):
            col_st1, col_st2 = st.columns(2)
            with col_st1:
                update_req_id = st.selectbox("Select Request ID:", requests_df['request_id'].tolist())
            with col_st2:
                new_req_status = st.selectbox("New Workflow Status:", ["Received", "Donor Matched", "Contacted", "In Progress", "Fulfilled", "Cancelled"])

            sub_update_req = st.form_submit_button("Update Status", type="primary", use_container_width=True)
            if sub_update_req:
                update_request_status(update_req_id, new_req_status)
                st.success(f"Request **{update_req_id}** updated to status: **{new_req_status}**")
                st.rerun()

with tab_transit:
    st.markdown("##### 🛰️ Real-Time Live Donor Transit Tracking Radar (GPS Journey Engine)")
    st.caption("Track accepted blood donors in real-time as they start their emergency transit journey from their home locality to the hospital donation center.")

    if not requests_df.empty and not donors_df.empty:
        col_tr1, col_tr2 = st.columns([1, 2])

        with col_tr1:
            st.markdown("###### 1️⃣ Select Emergency Dispatch & Accepted Donor")
            sel_trans_req_id = st.selectbox("Active Emergency Request:", requests_df['request_id'].tolist(), key="sel_trans_req")
            curr_req = requests_df[requests_df['request_id'] == sel_trans_req_id].iloc[0]

            # Filter available/compatible donors or select accepted donor
            donor_list = donors_df[donors_df['availability_status'] == 'Available'].copy()
            if donor_list.empty:
                donor_list = donors_df.copy()
            
            donor_options = {f"{r['name']} ({r['donor_id']} - {r['blood_group']})": r for _, r in donor_list.iterrows()}
            selected_donor_label = st.selectbox("Assigned / Accepted Donor:", list(donor_options.keys()), key="sel_trans_donor")
            sel_donor_obj = donor_options[selected_donor_label]

            st.markdown("###### 2️⃣ Control Live Journey Transit Progress")
            journey_pct = st.slider(
                "🚗 Simulate Live Journey Transit Progress (%):",
                min_value=0, max_value=100, value=45, step=5,
                help="Slide to simulate donor traveling along the route to the destination hospital."
            )

            # Spatial math
            d_lat, d_lon = sel_donor_obj['latitude'], sel_donor_obj['longitude']
            h_lat, h_lon = curr_req['latitude'], curr_req['longitude']

            # Interpolate current live position
            fraction = journey_pct / 100.0
            live_lat = d_lat + (h_lat - d_lat) * fraction
            live_lon = d_lon + (h_lon - d_lon) * fraction

            # Calculate remaining distance
            rem_dist = haversine_km(live_lat, live_lon, h_lat, h_lon)
            total_dist = haversine_km(d_lat, d_lon, h_lat, h_lon)
            eta_mins = max(0, int(rem_dist * 2.2))

            st.markdown("###### 3️⃣ Live Transit Telemetry Summary")
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #059669; padding:14px; border-radius:10px; font-size:0.85rem; margin-bottom:12px;">
                <b>🚗 Accepted Donor:</b> {sel_donor_obj['name']} ({sel_donor_obj['donor_id']})<br>
                <b>🏥 Destination:</b> {curr_req['hospital_name']}<br>
                <b>📍 Current GPS Coordinates:</b> <code>{live_lat:.4f}° N, {live_lon:.4f}° E</code><br>
                <b>📏 Distance Remaining:</b> <b style="color:#DC2626;">{rem_dist} km</b> (Total: {total_dist} km)<br>
                <b>⏱️ Estimated ETA:</b> <b style="color:#2563EB;">{eta_mins} minutes</b><br>
                <b>🛣️ Transit Route Progress:</b> <b>{journey_pct}% Completed</b>
            </div>
            """, unsafe_allow_html=True)

            if journey_pct == 100 or rem_dist < 0.2:
                st.markdown("""
                <div class="alert-card-success">
                    <h5 style="margin:0; color:#065F46;">🏁 DONOR HAS ARRIVED AT HOSPITAL!</h5>
                    <p style="margin:4px 0 0 0; font-size:0.82rem;">Donor has safely reached the hospital transfusion depot and is ready for pre-donation vital checks.</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("✅ Log Donor Arrival & Complete Request", type="primary", use_container_width=True):
                    update_request_status(sel_trans_req_id, "Fulfilled")
                    st.success(f"🎉 Emergency Request **{sel_trans_req_id}** updated to **Fulfilled**!")
                    st.rerun()

        with col_tr2:
            st.markdown("###### 🗺️ Live GPS Transit Map & Dynamic Route Tracking Radar")
            st.caption("🔴 Red Car = Live Donor Position | 🔵 Hospital Depot | 🛣️ Blue Dashed Line = Live Transit Route Trail | ⭕ Red Circle = 500m Hospital Perimeter")

            # Build Folium map centered between donor and hospital
            center_lat = (d_lat + h_lat) / 2.0
            center_lon = (d_lon + h_lon) / 2.0

            m_transit = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=12,
                tiles="OpenStreetMap",
                attr="🇮🇳 India Emergency Blood Network - Live Transit Radar | © OpenStreetMap"
            )

            # 1. Donor Starting Point Marker
            folium.Marker(
                location=[d_lat, d_lon],
                popup=f"<b>🏠 DONOR ORIGIN</b><br>{sel_donor_obj['name']}<br>Locality: {sel_donor_obj['city_locality']}",
                tooltip=f"Donor Start Point: {sel_donor_obj['name']}",
                icon=folium.Icon(color="green", icon="home", prefix="fa")
            ).add_to(m_transit)

            # 2. Destination Hospital Marker
            folium.Marker(
                location=[h_lat, h_lon],
                popup=f"<b>🏥 DESTINATION HOSPITAL</b><br>{curr_req['hospital_name']}<br>Required: {curr_req['required_blood_group']} ({curr_req['required_units']}u)",
                tooltip=f"Destination Hospital: {curr_req['hospital_name']}",
                icon=folium.Icon(color="red", icon="hospital-o", prefix="fa")
            ).add_to(m_transit)

            # 500m Hospital Arrival Circle
            folium.Circle(
                location=[h_lat, h_lon],
                radius=500,
                color="#DC2626",
                fill=True,
                fill_color="#DC2626",
                fill_opacity=0.15,
                popup="500m Hospital Arrival Zone"
            ).add_to(m_transit)

            # 3. Live Donor Moving Vehicle Marker
            car_popup = f"""
            <div style="font-family:sans-serif; width:200px; font-size:0.85rem;">
                <b style="color:#DC2626;">🚗 LIVE DONOR IN TRANSIT</b><br>
                <b>Donor:</b> {sel_donor_obj['name']}<br>
                <b>Blood Group:</b> {sel_donor_obj['blood_group']}<br>
                <b>Distance Rem:</b> {rem_dist} km<br>
                <b>ETA:</b> {eta_mins} mins<br>
                <b>Progress:</b> {journey_pct}%
            </div>
            """
            folium.Marker(
                location=[live_lat, live_lon],
                popup=folium.Popup(car_popup, max_width=220),
                tooltip=f"🚗 Live Location: {sel_donor_obj['name']} ({rem_dist} km to hospital)",
                icon=folium.Icon(color="purple", icon="car", prefix="fa")
            ).add_to(m_transit)

            # 4. Route Polyline Trail
            # Traveled route
            folium.PolyLine(
                locations=[[d_lat, d_lon], [live_lat, live_lon]],
                color="#10B981",
                weight=5,
                opacity=0.8,
                tooltip="Path Traveled"
            ).add_to(m_transit)

            # Remaining route
            folium.PolyLine(
                locations=[[live_lat, live_lon], [h_lat, h_lon]],
                color="#2563EB",
                weight=4,
                dash_array="6, 10",
                opacity=0.9,
                tooltip="Remaining Transit Route"
            ).add_to(m_transit)

            st_folium(m_transit, width="100%", height=440, returned_objects=[], key="map_transit")
    else:
        st.info("No active emergency requests or donor records available to track.")
