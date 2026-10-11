"""
Page 5: Pre-Donation Health Screening Module & Override Workflow.
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

from database.db import (
    fetch_health_screenings, fetch_donors, 
    insert_health_screening, update_screening_status
)
from utils.screening_rules import evaluate_health_screening
from utils.validation import validate_screening_vitals

st.markdown("""
<div class="section-header">
    <div>
        <h2>🩺 Pre-Donation Health Screening Module</h2>
        <p>Evaluate preliminary donor vitals, rule-based screening indicators, safety warnings, and physician review overrides.</p>
    </div>
    <span class="badge badge-purple">PRE-DONATION SAFETY</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="medical-disclaimer">
    🔴 <b>IMPORTANT SAFETY MANDATE:</b> Sensor readings and automated rule evaluations are preliminary indicators only, NOT medical clearance. Final donor eligibility must be determined by qualified blood-bank personnel using clinical guidelines.
</div>
""", unsafe_allow_html=True)

screenings_df = fetch_health_screenings()
donors_df = fetch_donors()

# Navigation Tabs: New Screening Form | Screening Log & Manual Override
tab_eval, tab_log = st.tabs(["📝 Evaluate New Screening Readings", "📜 Screening History & Physician Override"])

with tab_eval:
    st.markdown("##### 🩺 Enter Preliminary Sensor Readings & Questionnaire")
    with st.form("new_screening_form"):
        col_s1, col_s2 = st.columns(2)

        with col_s1:
            if not donors_df.empty:
                donor_choices = {f"{row['name']} ({row['donor_id']})": row for _, row in donors_df.iterrows()}
                selected_donor_str = st.selectbox("Select Registered Donor *", list(donor_choices.keys()))
                sel_donor = donor_choices[selected_donor_str]
                scr_donor_id = sel_donor['donor_id']
                scr_donor_name = sel_donor['name']
            else:
                scr_donor_id = "DON-1001"
                scr_donor_name = "Jane Doe"

            temp_input = st.number_input("Body Temperature (°C) *", min_value=32.0, max_value=42.0, value=36.8, step=0.1, help="Normal: 36.1°C - 37.5°C")
            hr_input = st.number_input("Heart Rate (bpm) *", min_value=30, max_value=200, value=74, step=1, help="Normal: 60 - 100 bpm")
            spo2_input = st.number_input("Oxygen Saturation (SpO2 %) *", min_value=70, max_value=100, value=98, step=1, help="Normal: 95% - 100%")

        with col_s2:
            sys_bp_input = st.number_input("Systolic Blood Pressure (mmHg) *", min_value=60, max_value=220, value=120, step=1, help="Normal: 90 - 140 mmHg")
            dia_bp_input = st.number_input("Diastolic Blood Pressure (mmHg) *", min_value=40, max_value=140, value=80, step=1, help="Normal: 60 - 90 mmHg")
            
            quest_pass_input = st.checkbox("Health Questionnaire Passed (No fever, recent infection, medication, or high-risk travel)", value=True)
            evaluator_name = st.text_input("Evaluator / Staff Operator Name", value="Nurse Operator")

        submit_screening = st.form_submit_button("🩺 Run Screening Rule Engine", type="primary", use_container_width=True)

        if submit_screening:
            is_valid_vitals, err_vitals = validate_screening_vitals(temp_input, hr_input, spo2_input, sys_bp_input, dia_bp_input)
            if not is_valid_vitals:
                st.error(err_vitals)
            else:
                # Run Rule Engine
                eval_res = evaluate_health_screening(
                    temp_input, hr_input, spo2_input, sys_bp_input, dia_bp_input, quest_pass_input
                )

                st.markdown("#### 📊 Rule Engine Preliminary Evaluation Results")
                
                status_lbl = eval_res['status_label']
                if eval_res['is_normal']:
                    st.markdown(f"""
                    <div class="alert-card-success">
                        <h4 style="margin:0; color:#065F46;">✅ Preliminary Outcome: {status_lbl}</h4>
                        <p style="margin:4px 0 0 0;">All sensor readings are within configured reference ranges.</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif eval_res['temporary_deferral']:
                    st.markdown(f"""
                    <div class="alert-card-emergency">
                        <h4 style="margin:0; color:#991B1B;">⛔ Preliminary Outcome: {status_lbl}</h4>
                        <p style="margin:4px 0 0 0;">Warning flags detected. Temporary deferral and reassessment suggested.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="alert-card-warning">
                        <h4 style="margin:0; color:#9A3412;">🩺 Preliminary Outcome: {status_lbl}</h4>
                        <p style="margin:4px 0 0 0;">Physician review required prior to donation clearance.</p>
                    </div>
                    """, unsafe_allow_html=True)

                if eval_res['warnings']:
                    st.write("##### ⚠️ Detected Warning Flags:")
                    for w in eval_res['warnings']:
                        st.write(f"- 🔸 {w}")

                # Save record to database
                scr_id = f"SCR-{9000 + len(screenings_df) + 1}"
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                scr_payload = {
                    "screening_id": scr_id,
                    "donor_id": scr_donor_id,
                    "donor_name": scr_donor_name,
                    "screening_datetime": now_str,
                    "temperature": float(temp_input),
                    "heart_rate": int(hr_input),
                    "spo2": int(spo2_input),
                    "systolic_bp": int(sys_bp_input),
                    "diastolic_bp": int(dia_bp_input),
                    "health_questionnaire_passed": 1 if quest_pass_input else 0,
                    "preliminary_status": status_lbl,
                    "review_notes": "; ".join(eval_res['warnings']) if eval_res['warnings'] else "Normal screening.",
                    "evaluated_by": evaluator_name
                }
                insert_health_screening(scr_payload)
                st.success(f"Screening saved with ID: **{scr_id}**")

with tab_log:
    st.markdown("##### 📜 Pre-Donation Screening History & Manual Override")
    st.dataframe(
        screenings_df[[
            'screening_id', 'donor_id', 'donor_name', 'screening_datetime', 
            'temperature', 'heart_rate', 'spo2', 'systolic_bp', 'diastolic_bp', 
            'preliminary_status', 'review_notes', 'evaluated_by'
        ]],
        use_container_width=True,
        hide_index=True
    )

    st.divider()
    st.markdown("##### 👩‍⚕️ Authorized Medical Officer Manual Override")
    st.caption("Authorized staff may override automated rule outcomes after clinical consultation.")

    if not screenings_df.empty:
        with st.form("override_form"):
            col_o1, col_o2 = st.columns(2)
            with col_o1:
                sel_scr_id = st.selectbox("Select Screening ID to Override:", screenings_df['screening_id'].tolist())
            with col_o2:
                override_status = st.selectbox("Override Status:", [
                    "Screening Completed", 
                    "No Initial Warning Detected", 
                    "Medical Review Required", 
                    "Temporary Deferral and Reassessment"
                ])
            override_notes = st.text_area("Physician Override Rationale / Medical Notes:", placeholder="e.g. Physician evaluated donor, cleared for standard donation despite mild heart rate elevation.")

            sub_override = st.form_submit_button("Submit Physician Override", type="primary", use_container_width=True)

            if sub_override:
                if not override_notes.strip():
                    st.error("Please provide clinical rationale in the notes field for manual override.")
                else:
                    update_screening_status(sel_scr_id, override_status, f"[PHYSICIAN OVERRIDE]: {override_notes.strip()}")
                    st.success(f"Screening **{sel_scr_id}** status updated to: **{override_status}**")
                    st.rerun()
