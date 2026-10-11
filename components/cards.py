"""
KPI Summary Cards Rendering Component.
Renders 8 summary cards with icons, values, accent colors, and trend indicators.
"""

import streamlit as st

def render_kpi_cards(
    total_donors: int,
    available_donors: int,
    total_blood_units: int,
    total_donations: int,
    emergency_requests: int,
    fulfilled_requests: int,
    medical_reviews: int,
    total_hospitals: int
):
    """
    Renders 8 KPI summary cards in a clean 4x2 grid layout.
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="kpi-card accent-red">
            <div class="kpi-header">
                <span class="kpi-title">Total Donors</span>
                <div class="kpi-icon-wrapper" style="background:#FEE2E2; color:#DC2626;">🩸</div>
            </div>
            <div class="kpi-value">{total_donors:,}</div>
            <div class="kpi-subtext">
                <span class="kpi-trend-up">↑ +12.4%</span> vs last month
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card accent-green">
            <div class="kpi-header">
                <span class="kpi-title">Available Donors</span>
                <div class="kpi-icon-wrapper" style="background:#D1FAE5; color:#059669;">✅</div>
            </div>
            <div class="kpi-value">{available_donors:,}</div>
            <div class="kpi-subtext">
                <span class="kpi-trend-up">{round((available_donors/max(total_donors,1))*100, 1)}%</span> active readiness
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card accent-blue">
            <div class="kpi-header">
                <span class="kpi-title">Blood Units Stock</span>
                <div class="kpi-icon-wrapper" style="background:#DBEAFE; color:#2563EB;">🏥</div>
            </div>
            <div class="kpi-value">{total_blood_units:,}</div>
            <div class="kpi-subtext">
                <span class="kpi-trend-neutral">Across 8 blood groups</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card accent-purple">
            <div class="kpi-header">
                <span class="kpi-title">Donations Done</span>
                <div class="kpi-icon-wrapper" style="background:#EDE9FE; color:#7C3AED;">💉</div>
            </div>
            <div class="kpi-value">{total_donations:,}</div>
            <div class="kpi-subtext">
                <span class="kpi-trend-up">↑ +8%</span> monthly increase
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("") # Spacer

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        st.markdown(f"""
        <div class="kpi-card accent-rose">
            <div class="kpi-header">
                <span class="kpi-title">Emergency Requests</span>
                <div class="kpi-icon-wrapper" style="background:#FFE4E6; color:#E11D48;">🚨</div>
            </div>
            <div class="kpi-value">{emergency_requests:,}</div>
            <div class="kpi-subtext">
                <span class="kpi-trend-alert">Urgent dispatch required</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown(f"""
        <div class="kpi-card accent-emerald">
            <div class="kpi-header">
                <span class="kpi-title">Requests Fulfilled</span>
                <div class="kpi-icon-wrapper" style="background:#D1FAE5; color:#10B981;">🎯</div>
            </div>
            <div class="kpi-value">{fulfilled_requests:,}</div>
            <div class="kpi-subtext">
                <span class="kpi-trend-up">{round((fulfilled_requests/max(emergency_requests,1))*100, 1)}%</span> success rate
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col7:
        st.markdown(f"""
        <div class="kpi-card accent-orange">
            <div class="kpi-header">
                <span class="kpi-title">Medical Review</span>
                <div class="kpi-icon-wrapper" style="background:#FFEDD5; color:#EA580C;">🩺</div>
            </div>
            <div class="kpi-value">{medical_reviews:,}</div>
            <div class="kpi-subtext">
                <span class="kpi-trend-alert">Pre-donation flags</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col8:
        st.markdown(f"""
        <div class="kpi-card accent-cyan">
            <div class="kpi-header">
                <span class="kpi-title">Centres Registered</span>
                <div class="kpi-icon-wrapper" style="background:#CFFAFE; color:#0891B2;">🏢</div>
            </div>
            <div class="kpi-value">{total_hospitals:,}</div>
            <div class="kpi-subtext">
                <span class="kpi-trend-neutral">Hospitals & Blood Banks</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
