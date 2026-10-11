"""
Seed Data Script for AI Blood Donor Finder Dashboard.
Updated with user-specified Tamil Nadu cities:
Chennai (Capital City), Coimbatore, Madurai, Tiruchirappalli (Trichy), Tiruppur,
Salem, Erode, Tirunelveli, Vellore, Thoothukudi (Tuticorin), Dindigul, Thanjavur,
Nagercoil, Hosur, Kumbakonam, Karur.
"""

import os
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pathlib import Path

try:
    from database.db import init_db, get_connection
except ModuleNotFoundError:
    from db import init_db, get_connection

# Set seed for reproducibility
random.seed(42)
np.random.seed(42)

DATA_DIR = Path(__file__).parent.parent / "data"

BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
BLOOD_GROUP_WEIGHTS = [0.30, 0.06, 0.25, 0.05, 0.08, 0.02, 0.20, 0.04]

FIRST_NAMES = [
    "Karthik", "Surya", "Anand", "Priya", "Kavitha", "Senthil", "Vijay", "Deepa", "Arun", "Divya",
    "Ganesh", "Lakshmi", "Ramesh", "Meena", "Saravanan", "Nandhini", "Vignesh", "Revathi", "Murugan", "Sangeetha",
    "Santhosh", "Bhuvaneshwari", "Prakash", "Janani", "Dinesh", "Sowmya", "Rajesh", "Gayathri", "Kumar", "Archana",
    "Prabhu", "Aarthi", "Manikandan", "Preethi", "Ashok", "Pavithra", "Balaji", "Nisha", "Suresh", "Swetha"
]

LAST_NAMES = [
    "Raman", "Subramanian", "Natarajan", "Sundaram", "Krishnan", "Venkatesan", "Shanmugam", "Ganesan",
    "Palanisamy", "Murugesan", "Chandrasekaran", "Rajendran", "Viswanathan", "Thangaraj", "Kandasamy",
    "Chettiar", "Gounder", "Naidu", "Pillai", "Mudaliar"
]

TAMILNADU_CITIES_SPECIFIED = [
    ("Karur", 10.9601, 78.0766),
    ("Chennai (Capital City)", 13.0827, 80.2707),
    ("Coimbatore", 11.0168, 76.9558),
    ("Madurai", 9.9252, 78.1198),
    ("Tiruchirappalli (Trichy)", 10.7905, 78.7047),
    ("Tiruppur", 11.1085, 77.3411),
    ("Salem", 11.6643, 78.1460),
    ("Erode", 11.3410, 77.7172),
    ("Tirunelveli", 8.7139, 77.7567),
    ("Vellore", 12.9165, 79.1325),
    ("Thoothukudi (Tuticorin)", 8.7642, 78.1348),
    ("Dindigul", 10.3673, 77.9803),
    ("Thanjavur", 10.7870, 79.1378),
    ("Nagercoil", 8.1833, 77.4119),
    ("Hosur", 12.7409, 77.8253),
    ("Kumbakonam", 10.9602, 79.3782)
]

HOSPITALS_DATA = [
    ("CTR-01", "Karur Government Medical College Hospital", "Hospital", "Karur", 10.9601, 78.0766, "+91-4324-220101", "+91-4324-290101"),
    ("CTR-02", "Chennai General Hospital Transfusion Depot", "Hospital", "Chennai (Capital City)", 13.0827, 80.2707, "+91-44-220102", "+91-44-290102"),
    ("CTR-03", "Coimbatore Medical College Hospital", "Hospital", "Coimbatore", 11.0168, 76.9558, "+91-422-220103", "+91-422-290103"),
    ("CTR-04", "Madurai Rajaji Government Hospital", "Hospital", "Madurai", 9.9252, 78.1198, "+91-452-220104", "+91-452-290104"),
    ("CTR-05", "Trichy MGM Government Hospital", "Hospital", "Tiruchirappalli (Trichy)", 10.7905, 78.7047, "+91-431-220105", "+91-431-290105"),
    ("CTR-06", "Tiruppur Regional Red Cross Depot", "Blood Bank", "Tiruppur", 11.1085, 77.3411, "+91-421-220106", "+91-421-290106"),
    ("CTR-07", "Salem Mohan Kumaramangalam Hospital", "Hospital", "Salem", 11.6643, 78.1460, "+91-427-220107", "+91-427-290107"),
    ("CTR-08", "Erode District Headquarters Hospital", "Hospital", "Erode", 11.3410, 77.7172, "+91-424-220108", "+91-424-290108"),
    ("CTR-09", "Tirunelveli Medical College Hospital", "Hospital", "Tirunelveli", 8.7139, 77.7567, "+91-462-220109", "+91-462-290109"),
    ("CTR-10", "Vellore CMC Transfusion Center", "Blood Bank", "Vellore", 12.9165, 79.1325, "+91-416-220110", "+91-416-290110"),
    ("CTR-11", "Thoothukudi Government Hospital", "Hospital", "Thoothukudi (Tuticorin)", 8.7642, 78.1348, "+91-461-220111", "+91-461-290111"),
    ("CTR-12", "Dindigul Central Medical Depot", "Blood Bank", "Dindigul", 10.3673, 77.9803, "+91-451-220112", "+91-451-290112"),
    ("CTR-13", "Thanjavur Medical College Hospital", "Hospital", "Thanjavur", 10.7870, 79.1378, "+91-4362-220113", "+91-4362-290113"),
    ("CTR-14", "Nagercoil City Blood Center", "Blood Bank", "Nagercoil", 8.1833, 77.4119, "+91-4652-220114", "+91-4652-290114"),
    ("CTR-15", "Hosur Industrial Medical Hub", "Hospital", "Hosur", 12.7409, 77.8253, "+91-4344-220115", "+91-4344-290115"),
    ("CTR-16", "Kumbakonam Temple Town Hospital", "Hospital", "Kumbakonam", 10.9602, 79.3782, "+91-435-220116", "+91-435-290116")
]

def generate_sample_data():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    for table in ["donors", "hospitals_blood_banks", "blood_stock", "donations", "emergency_requests", "health_screenings"]:
        cursor.execute(f"DELETE FROM {table}")

    end_date = datetime(2026, 10, 10)

    # 1. Seed 16 Hospitals / Blood Banks
    hospitals_df = pd.DataFrame(HOSPITALS_DATA, columns=[
        "centre_id", "centre_name", "centre_type", "location", "latitude", "longitude", "contact_phone", "emergency_contact"
    ])
    hospitals_df.to_sql("hospitals_blood_banks", conn, if_exists="append", index=False)

    # 2. Seed 160 Donors across the 16 specified cities
    donors_list = []
    availabilities = ["Available", "Available", "Available", "Unavailable", "Temporarily Unavailable"]
    
    for i in range(1, 161):
        donor_id = f"DON-{1000 + i}"
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        name = f"{fn} {ln}"
        blood_group = np.random.choice(BLOOD_GROUPS, p=BLOOD_GROUP_WEIGHTS)
        age = random.randint(18, 62)
        phone = f"+91-9842{random.randint(10000, 99999)}"
        email = f"{fn.lower()}.{ln.lower()}{random.randint(10,99)}@example.in"
        
        city_tuple = TAMILNADU_CITIES_SPECIFIED[(i - 1) % len(TAMILNADU_CITIES_SPECIFIED)]
        locality, base_lat, base_lon = city_tuple
        lat = base_lat + random.uniform(-0.02, 0.02)
        lon = base_lon + random.uniform(-0.02, 0.02)
        
        reg_days = random.randint(30, 365)
        reg_date = (end_date - timedelta(days=reg_days)).strftime("%Y-%m-%d")
        
        status = random.choice(availabilities)
        tot_donations = random.randint(0, 14)
        
        if tot_donations > 0:
            last_don_days = random.randint(10, reg_days - 5) if reg_days > 15 else 10
            last_don_date = (end_date - timedelta(days=last_don_days)).strftime("%Y-%m-%d")
        else:
            last_don_date = None

        donors_list.append({
            "donor_id": donor_id,
            "name": name,
            "blood_group": blood_group,
            "age": age,
            "contact_number": phone,
            "email": email,
            "city_locality": locality,
            "latitude": round(lat, 5),
            "longitude": round(lon, 5),
            "registration_date": reg_date,
            "availability_status": status,
            "last_donation_date": last_don_date,
            "total_donations": tot_donations
        })

    donors_df = pd.DataFrame(donors_list)
    donors_df.to_sql("donors", conn, if_exists="append", index=False)

    # 3. Seed Blood Stock for all 16 centers (128 records)
    stock_list = []
    for h in HOSPITALS_DATA:
        centre_id = h[0]
        for bg in BLOOD_GROUPS:
            base_units = random.randint(5, 35)
            if bg in ["O+", "A+"]:
                base_units = random.randint(15, 50)
            elif bg in ["AB-", "B-"]:
                base_units = random.randint(2, 15)
                
            last_update = (end_date - timedelta(hours=random.randint(1, 48))).strftime("%Y-%m-%d %H:%M:%S")
            stock_list.append({
                "centre_id": centre_id,
                "blood_group": bg,
                "available_units": base_units,
                "last_stock_update": last_update
            })

    stock_df = pd.DataFrame(stock_list)
    stock_df.to_sql("blood_stock", conn, if_exists="append", index=False)

    # 4. Seed 200 Donations
    donations_list = []
    statuses = ["Completed", "Completed", "Completed", "Processing", "Cancelled"]
    donors_with_donations = donors_df[donors_df['total_donations'] > 0]
    
    for i in range(1, 201):
        donation_id = f"DONAT-{5000 + i}"
        donor_row = donors_with_donations.sample(1).iloc[0]
        d_id = donor_row['donor_id']
        bg = donor_row['blood_group']
        centre = random.choice(HOSPITALS_DATA)[0]
        
        days_ago = random.randint(1, 360)
        don_date = (end_date - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        units = 1
        st = random.choice(statuses)

        donations_list.append({
            "donation_id": donation_id,
            "donor_id": d_id,
            "blood_group": bg,
            "centre_id": centre,
            "donation_date": don_date,
            "units_donated": units,
            "status": st
        })

    donations_df = pd.DataFrame(donations_list)
    donations_df.to_sql("donations", conn, if_exists="append", index=False)

    # 5. Seed 100 Emergency Requests
    requests_list = []
    req_statuses = ["Fulfilled", "Fulfilled", "Fulfilled", "Contacted", "Donor Matched", "Received", "Cancelled"]
    urgencies = ["Normal", "Urgent", "Emergency"]

    for i in range(1, 101):
        req_id = f"REQ-{8000 + i}"
        hosp = random.choice(HOSPITALS_DATA)
        h_id, h_name, _, loc, h_lat, h_lon, _, _ = hosp
        bg = np.random.choice(BLOOD_GROUPS, p=BLOOD_GROUP_WEIGHTS)
        units = random.randint(1, 6)
        urgency = np.random.choice(urgencies, p=[0.4, 0.35, 0.25])
        
        hours_ago = random.randint(2, 720)
        req_dt = (end_date - timedelta(hours=hours_ago)).strftime("%Y-%m-%d %H:%M:%S")
        status = random.choice(req_statuses)
        matched_cnt = random.randint(2, 12) if status != "Received" else 0

        requests_list.append({
            "request_id": req_id,
            "hospital_name": h_name,
            "centre_id": h_id,
            "required_blood_group": bg,
            "required_units": units,
            "urgency_level": urgency,
            "request_datetime": req_dt,
            "location": loc,
            "latitude": h_lat,
            "longitude": h_lon,
            "status": status,
            "matched_donors_count": matched_cnt
        })

    requests_df = pd.DataFrame(requests_list)
    requests_df.to_sql("emergency_requests", conn, if_exists="append", index=False)

    # 6. Seed 160 Health Screenings
    screenings_list = []
    evaluators = ["Dr. K. Senthil Kumar", "Nurse S. Revathi", "Technician M. Balaji", "Dr. R. Kavitha"]

    for i in range(1, 161):
        scr_id = f"SCR-{9000 + i}"
        d_row = donors_df.iloc[i-1]
        d_id = d_row['donor_id']
        d_name = d_row['name']
        
        hours_ago = random.randint(1, 300)
        scr_dt = (end_date - timedelta(hours=hours_ago)).strftime("%Y-%m-%d %H:%M:%S")

        is_normal = random.random() > 0.25
        
        if is_normal:
            temp = round(random.uniform(36.3, 37.3), 1)
            hr = random.randint(62, 92)
            spo2 = random.randint(96, 100)
            sys_bp = random.randint(108, 135)
            dia_bp = random.randint(68, 85)
            quest_pass = 1
            status_label = random.choice(["No Initial Warning Detected", "Screening Completed"])
            notes = "Vital signs within normal physiological ranges. Donor fit for standard donation."
        else:
            outcome_type = random.choice(["temp", "hr", "bp", "spo2", "quest"])
            temp = round(random.uniform(36.3, 37.3), 1)
            hr = random.randint(65, 90)
            spo2 = random.randint(96, 100)
            sys_bp = random.randint(110, 130)
            dia_bp = random.randint(70, 84)
            quest_pass = 1

            if outcome_type == "temp":
                temp = round(random.uniform(37.8, 38.6), 1)
                status_label = "Temporary Deferral and Reassessment"
                notes = f"Fever flag detected (Temp: {temp}°C). Temporarily deferred for 14 days."
            elif outcome_type == "hr":
                hr = random.randint(104, 125)
                status_label = "Medical Review Required"
                notes = f"Tachycardia flag ({hr} bpm). Physician evaluation required prior to phlebotomy."
            elif outcome_type == "bp":
                sys_bp = random.randint(145, 168)
                dia_bp = random.randint(94, 105)
                status_label = "Temporary Deferral and Reassessment"
                notes = f"Hypertension flag ({sys_bp}/{dia_bp} mmHg). Rest period suggested."
            elif outcome_type == "spo2":
                spo2 = random.randint(90, 94)
                status_label = "Temporary Deferral and Reassessment"
                notes = f"SpO2 below target ({spo2}%). Deferral recommended."
            else:
                quest_pass = 0
                status_label = "Medical Review Required"
                notes = "Recent medication / travel flag in health questionnaire. Requires medical clearance."

        screenings_list.append({
            "screening_id": scr_id,
            "donor_id": d_id,
            "donor_name": d_name,
            "screening_datetime": scr_dt,
            "temperature": temp,
            "heart_rate": hr,
            "spo2": spo2,
            "systolic_bp": sys_bp,
            "diastolic_bp": dia_bp,
            "health_questionnaire_passed": quest_pass,
            "preliminary_status": status_label,
            "review_notes": notes,
            "evaluated_by": random.choice(evaluators)
        })

    screenings_df = pd.DataFrame(screenings_list)
    screenings_df.to_sql("health_screenings", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()

    os.makedirs(DATA_DIR, exist_ok=True)
    donors_df.to_csv(DATA_DIR / "sample_donors.csv", index=False)
    hospitals_df.to_csv(DATA_DIR / "sample_hospitals.csv", index=False)
    stock_df.to_csv(DATA_DIR / "sample_blood_stock.csv", index=False)
    donations_df.to_csv(DATA_DIR / "sample_donations.csv", index=False)
    requests_df.to_csv(DATA_DIR / "sample_requests.csv", index=False)
    screenings_df.to_csv(DATA_DIR / "sample_screenings.csv", index=False)

    print("Updated 16 Specified Tamil Nadu Cities dataset saved to SQLite & CSVs.")

if __name__ == "__main__":
    generate_sample_data()
