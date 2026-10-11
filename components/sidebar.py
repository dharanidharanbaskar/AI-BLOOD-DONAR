"""
Sidebar Navigation & Global Filtering Controls.
"""

import streamlit as st
import pandas as pd

def render_sidebar(donors_df: pd.DataFrame, hospitals_df: pd.DataFrame) -> dict:
    """
    Renders sidebar branding, access role toggle, and global filter controls.
    Returns dictionary of active filter criteria.
    """
    with st.sidebar:
        # Branding Card
        st.markdown("""
        <div class="sidebar-brand-card">
            <div class="sidebar-brand-title">
                🩸 MediPulse AI
            </div>
            <div style="font-weight:600; color:#FFFFFF; font-size:0.9rem; margin-top:4px;">
                Emergency Blood Donor & Screening System
            </div>
            <div class="sidebar-brand-sub" style="margin-top:6px;">
                College Capstone Project Demo | v2.4
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🔐 User Role & Access")
        role = st.selectbox(
            "Select Access Mode:",
            ["Authorized Staff (Full Access)", "Public / Student View (Anonymized)"],
            index=0,
            help="Authorized Staff can view donor contact information. Public view anonymizes personal identifying data."
        )
        st.session_state['user_role'] = role

        st.divider()
        st.markdown("### 🔍 Global Dashboard Filters")

        # Blood Group Filter
        all_bg = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        selected_bg = st.multiselect(
            "Filter Blood Group:",
            options=all_bg,
            default=all_bg,
            help="Filter analytics and donor lists by blood group"
        )

        # Hospital Filter
        hosp_options = ["All Hospitals & Blood Banks"] + (list(hospitals_df['centre_name'].unique()) if not hospitals_df.empty else [])
        selected_hosp = st.selectbox("Select Hospital / Blood Bank:", hosp_options)

        # Location Filter
        city_options = ["All Locations"] + (list(donors_df['city_locality'].unique()) if not donors_df.empty else [])
        selected_city = st.selectbox("Filter Location / City:", city_options)

        # Availability Filter
        avail_options = ["All Statuses", "Available", "Unavailable", "Temporarily Unavailable"]
        selected_avail = st.selectbox("Donor Availability:", avail_options)

        # Urgency Level Filter
        urgency_options = ["All Priorities", "Normal", "Urgent", "Emergency"]
        selected_urgency = st.selectbox("Emergency Priority:", urgency_options)

        # Screening Outcome Filter
        screening_options = ["All Outcomes", "No Initial Warning Detected", "Screening Completed", "Medical Review Required", "Temporary Deferral and Reassessment"]
        selected_screening = st.selectbox("Screening Outcome:", screening_options)

        st.write("")
        if st.button("🔄 Reset All Filters", use_container_width=True):
            st.rerun()

        st.markdown("---")
        st.caption("ℹ️ *Data strictly generated for college project demonstration. Medical screening rules are preliminary indicators.*")

    return {
        "blood_groups": selected_bg if selected_bg else all_bg,
        "hospital": selected_hosp,
        "city": selected_city,
        "availability": selected_avail,
        "urgency": selected_urgency,
        "screening": selected_screening,
        "role": role
    }
