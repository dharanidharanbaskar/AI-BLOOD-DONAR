"""
Page 3: Blood Stock & Inventory Management Page.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

# Load Custom CSS
CSS_PATH = Path(__file__).parent.parent / "assets" / "style.css"
if CSS_PATH.exists():
    with open(CSS_PATH, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from database.db import fetch_blood_stock, fetch_hospitals, update_stock_units

st.markdown("""
<div class="section-header">
    <div>
        <h2>🏥 Hospital & Blood Bank Stock Inventory</h2>
        <p>Monitor real-time blood unit availability, trigger low-stock alerts, and update hospital supply status.</p>
    </div>
    <span class="badge badge-green">INVENTORY CONTROL</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="alert-card-info" style="font-size:0.85rem;">
    ℹ️ <b>Demonstration Notice:</b> Stock levels represent simulated hospital repository inventory (blood units) and are distinct from registered donor counts.
</div>
""", unsafe_allow_html=True)

stock_df = fetch_blood_stock()
hospitals_df = fetch_hospitals()

# Configurable Low-Stock Threshold
col_t1, col_t2 = st.columns([3, 1])
with col_t2:
    low_stock_threshold = st.slider("⚠️ Low-Stock Threshold (Units):", min_value=5, max_value=30, value=12)

# Top Bar Search & Filters
col_f1, col_f2, col_f3 = st.columns([3, 2, 2])
with col_f1:
    hosp_search = st.text_input("🔍 Search Centre Name:", placeholder="e.g. City General")
with col_f2:
    loc_filter = st.selectbox("Location:", ["All Locations"] + (list(hospitals_df['location'].unique()) if not hospitals_df.empty else []))
with col_f3:
    bg_filter = st.selectbox("Blood Group:", ["All Blood Groups", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])

# Filter DataFrame
df_display = stock_df.copy()
if not df_display.empty:
    if hosp_search:
        df_display = df_display[df_display['centre_name'].str.contains(hosp_search, case=False, na=False)]
    if loc_filter != "All Locations":
        df_display = df_display[df_display['location'] == loc_filter]
    if bg_filter != "All Blood Groups":
        df_display = df_display[df_display['blood_group'] == bg_filter]

    # Calculate stock status tag
    def get_stock_status(units):
        if units < low_stock_threshold / 2:
            return "🔴 Critical Low"
        elif units < low_stock_threshold:
            return "🟠 Low Stock"
        else:
            return "🟢 Adequate"

    df_display['stock_status'] = df_display['available_units'].apply(get_stock_status)

# Highlight Cards for Highest & Lowest Stock
col_hi, col_lo = st.columns(2)
if not stock_df.empty:
    with col_hi:
        top_row = stock_df.sort_values('available_units', ascending=False).iloc[0]
        st.markdown(f"""
        <div class="alert-card-success">
            <b>🏆 Highest Stock Repository:</b> {top_row['centre_name']} ({top_row['blood_group']}) - <b>{top_row['available_units']} Units</b>
        </div>
        """, unsafe_allow_html=True)
    with col_lo:
        low_row = stock_df.sort_values('available_units', ascending=True).iloc[0]
        st.markdown(f"""
        <div class="alert-card-emergency">
            <b>⚠️ Lowest Stock Repository:</b> {low_row['centre_name']} ({low_row['blood_group']}) - <b>{low_row['available_units']} Units</b>
        </div>
        """, unsafe_allow_html=True)

st.write("")

# Display Inventory Table
st.markdown("#### 📦 Current Stock Inventory")
st.dataframe(
    df_display[[
        'centre_id', 'centre_name', 'centre_type', 'location', 
        'blood_group', 'available_units', 'stock_status', 'last_stock_update'
    ]],
    use_container_width=True,
    hide_index=True
)

st.divider()

# Update Stock Form
st.markdown("#### 🔄 Update Inventory Stock Level")
with st.form("update_stock_form"):
    col_u1, col_u2, col_u3 = st.columns(3)
    with col_u1:
        if not hospitals_df.empty:
            centre_choices = {row['centre_name']: row['centre_id'] for _, row in hospitals_df.iterrows()}
            selected_centre_name = st.selectbox("Select Centre:", list(centre_choices.keys()))
            selected_centre_id = centre_choices[selected_centre_name]
        else:
            selected_centre_id = "CTR-01"
            selected_centre_name = "Default Centre"

    with col_u2:
        u_bg = st.selectbox("Select Blood Group:", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])

    with col_u3:
        u_units = st.number_input("New Available Units:", min_value=0, max_value=200, value=25)

    submit_stock_update = st.form_submit_button("Update Stock Record", type="primary", use_container_width=True)

    if submit_stock_update:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        update_stock_units(selected_centre_id, u_bg, int(u_units), now_str)
        st.success(f"Successfully updated **{selected_centre_name}** stock for **{u_bg}** to **{u_units} units**.")
        st.rerun()
