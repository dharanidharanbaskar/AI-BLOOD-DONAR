"""
Page 2: Donor Management System.
Features: Search, Filter, Add/Edit/Deactivate, Role-Based Privacy Controls.
"""

import streamlit as st
import pandas as pd
import random
from datetime import date, datetime
from pathlib import Path

# Load Custom CSS
CSS_PATH = Path(__file__).parent.parent / "assets" / "style.css"
if CSS_PATH.exists():
    with open(CSS_PATH, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from database.db import fetch_donors, insert_donor, update_donor
from utils.validation import validate_email, validate_phone, validate_donor_age

CITY_COORDINATES = {
    "Karur": (10.9601, 78.0766),
    "Chennai (Capital City)": (13.0827, 80.2707),
    "Coimbatore": (11.0168, 76.9558),
    "Madurai": (9.9252, 78.1198),
    "Tiruchirappalli (Trichy)": (10.7905, 78.7047),
    "Tiruppur": (11.1085, 77.3411),
    "Salem": (11.6643, 78.1460),
    "Erode": (11.3410, 77.7172),
    "Tirunelveli": (8.7139, 77.7567),
    "Vellore": (12.9165, 79.1325),
    "Thoothukudi (Tuticorin)": (8.7642, 78.1348),
    "Dindigul": (10.3673, 77.9803),
    "Thanjavur": (10.7870, 79.1378),
    "Nagercoil": (8.1833, 77.4119),
    "Hosur": (12.7409, 77.8253),
    "Kumbakonam": (10.9602, 79.3782)
}

st.markdown("""
<div class="section-header">
    <div>
        <h2>👥 Emergency Blood Donor Management Directory</h2>
        <p>Search, manage, register new donors, update availability status, and control data privacy.</p>
    </div>
    <span class="badge badge-blue">DONOR DIRECTORY</span>
</div>
""", unsafe_allow_html=True)

donors_df = fetch_donors()

# Check Role Access Mode
user_role = st.session_state.get('user_role', 'Authorized Staff (Full Access)')
is_staff = "Authorized Staff" in user_role

if not is_staff:
    st.markdown("""
    <div class="alert-card-info">
        🔒 <b>Public Privacy Mode Active:</b> Personal contact details (email, phone, full names) are anonymized for privacy compliance. Switch access mode in sidebar if authorized.
    </div>
    """, unsafe_allow_html=True)

# Top Bar Filters & Search
col_s1, col_s2, col_s3 = st.columns([3, 2, 2])

with col_s1:
    search_query = st.text_input("🔍 Search Donor by Name or Donor ID:", placeholder="e.g. DON-1015 or Karthik")

with col_s2:
    bg_filter = st.multiselect("Blood Group:", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], default=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])

with col_s3:
    status_filter = st.selectbox("Availability:", ["All Statuses", "Available", "Unavailable", "Temporarily Unavailable"])

# Filter DataFrame
df_display = donors_df.copy()
if not df_display.empty:
    if search_query:
        df_display = df_display[
            df_display['donor_id'].str.contains(search_query, case=False, na=False) |
            df_display['name'].str.contains(search_query, case=False, na=False)
        ]
    if bg_filter:
        df_display = df_display[df_display['blood_group'].isin(bg_filter)]
    if status_filter != "All Statuses":
        df_display = df_display[df_display['availability_status'] == status_filter]

# Apply Privacy Anonymization if Public Mode
if not is_staff and not df_display.empty:
    df_display['name'] = df_display['name'].apply(lambda x: x[0] + "." + " " + x.split()[-1][0] + "." if len(x.split()) > 1 else x[0] + "***")
    df_display['contact_number'] = "••••••••••"
    df_display['email'] = "••••@anonymized.in"

# Display Directory Table
st.markdown(f"#### Registered Donors ({len(df_display)} records found)")
st.dataframe(
    df_display[[
        'donor_id', 'name', 'blood_group', 'age', 'availability_status', 
        'contact_number', 'email', 'city_locality', 'registration_date', 
        'last_donation_date', 'total_donations'
    ]],
    use_container_width=True,
    hide_index=True
)

if is_staff and not df_display.empty:
    with st.expander("📞 Quick Emergency Contact Launcher (Direct Call & WhatsApp)"):
        c_sel1, c_sel2, c_sel3 = st.columns([2, 1, 1])
        with c_sel1:
            sel_donor_opt = st.selectbox(
                "Select Donor from Directory:", 
                [f"{row['donor_id']} - {row['name']} ({row['blood_group']}) [{row['city_locality']}]" for _, row in df_display.iterrows()]
            )
            selected_id = sel_donor_opt.split(" - ")[0]
            sel_row = df_display[df_display['donor_id'] == selected_id].iloc[0]
        with c_sel2:
            st.markdown(f"**Contact Number:** `{sel_row['contact_number']}`")
            st.markdown(f'<a href="tel:{sel_row["contact_number"]}" target="_blank" style="text-decoration:none;"><button style="background:#0284c7; color:white; border:none; padding:8px 16px; border-radius:6px; font-weight:bold; cursor:pointer;">📞 Call Donor</button></a>', unsafe_allow_html=True)
        with c_sel3:
            raw_phone = "".join(filter(str.isdigit, sel_row['contact_number']))[-10:]
            st.markdown(f"**Availability:** `{sel_row['availability_status']}`")
            st.markdown(f'<a href="https://wa.me/91{raw_phone}?text=Hello%20{sel_row["name"]},%20urgent%20blood%20donation%20requirement%20at%20our%20hospital." target="_blank" style="text-decoration:none;"><button style="background:#16a34a; color:white; border:none; padding:8px 16px; border-radius:6px; font-weight:bold; cursor:pointer;">💬 WhatsApp Chat</button></a>', unsafe_allow_html=True)

st.divider()

# Management Action Tabs: Add Donor | Edit/Deactivate Donor
tab_add, tab_edit = st.tabs(["➕ Register New Donor", "✏️ Edit / Deactivate Donor Record"])

with tab_add:
    st.markdown("##### 📝 New Donor Registration Form")
    with st.form("add_donor_form", clear_on_submit=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            new_name = st.text_input("Full Name *", placeholder="Karthik Subramanian")
            new_bg = st.selectbox("Blood Group *", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            new_age = st.number_input("Age (Years) *", min_value=18, max_value=75, value=25)
        with col_f2:
            new_phone = st.text_input("Contact Phone *", placeholder="+91-98420-12345")
            new_email = st.text_input("Email Address *", placeholder="karthik.s@example.in")
            TAMILNADU_CITIES = list(CITY_COORDINATES.keys())
            new_city = st.selectbox("City / Locality *", TAMILNADU_CITIES)
        with col_f3:
            new_status = st.selectbox("Initial Availability *", ["Available", "Unavailable", "Temporarily Unavailable"])

        submit_add = st.form_submit_button("Register Donor Record", type="primary", use_container_width=True)

        if submit_add:
            is_valid_email, err_email = validate_email(new_email)
            is_valid_phone, err_phone = validate_phone(new_phone)
            is_valid_age, err_age = validate_donor_age(new_age)

            if not new_name.strip():
                st.error("Donor name cannot be blank.")
            elif not is_valid_email:
                st.error(err_email)
            elif not is_valid_phone:
                st.error(err_phone)
            elif not is_valid_age:
                st.error(err_age)
            else:
                next_id = f"DON-{1000 + len(donors_df) + 1}"
                
                # Automatically derive coordinates from selected city + micro jitter
                base_lat, base_lon = CITY_COORDINATES.get(new_city, (10.9601, 78.0766))
                auto_lat = round(base_lat + random.uniform(-0.01, 0.01), 5)
                auto_lon = round(base_lon + random.uniform(-0.01, 0.01), 5)

                new_donor_dict = {
                    "donor_id": next_id,
                    "name": new_name.strip(),
                    "blood_group": new_bg,
                    "age": int(new_age),
                    "contact_number": new_phone.strip(),
                    "email": new_email.strip(),
                    "city_locality": new_city,
                    "latitude": auto_lat,
                    "longitude": auto_lon,
                    "registration_date": date.today().strftime("%Y-%m-%d"),
                    "availability_status": new_status,
                    "last_donation_date": None,
                    "total_donations": 0
                }
                insert_donor(new_donor_dict)
                st.success(f"🎉 Donor successfully registered with ID: **{next_id}** (Assigned to {new_city})")
                st.rerun()

with tab_edit:
    st.markdown("##### ✏️ Update Existing Donor Record")
    if not donors_df.empty:
        donor_ids = donors_df['donor_id'].tolist()
        selected_id = st.selectbox("Select Donor ID to Update:", donor_ids)
        current_donor = donors_df[donors_df['donor_id'] == selected_id].iloc[0]

        with st.form("edit_donor_form"):
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                edit_name = st.text_input("Name", value=current_donor['name'])
                edit_bg = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], index=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].index(current_donor['blood_group']))
                edit_status = st.selectbox("Availability Status", ["Available", "Unavailable", "Temporarily Unavailable"], index=["Available", "Unavailable", "Temporarily Unavailable"].index(current_donor['availability_status']))
            with col_e2:
                edit_phone = st.text_input("Phone Number", value=current_donor['contact_number'])
                edit_email = st.text_input("Email", value=current_donor['email'])
                edit_donations = st.number_input("Completed Donations Count", value=int(current_donor['total_donations']), min_value=0)

            submit_edit = st.form_submit_button("Save Changes", type="primary", use_container_width=True)

            if submit_edit:
                update_payload = {
                    "name": edit_name.strip(),
                    "blood_group": edit_bg,
                    "availability_status": edit_status,
                    "contact_number": edit_phone.strip(),
                    "email": edit_email.strip(),
                    "total_donations": int(edit_donations)
                }
                update_donor(selected_id, update_payload)
                st.success(f"Record updated successfully for **{selected_id}**.")
                st.rerun()
