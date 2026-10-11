"""
SQLite Database Connection and Data Access Layer for Blood Bank Management System.
"""

import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent / "blood_bank.db"

def get_connection():
    """Establish and return SQLite database connection."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database schema if tables do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Donors table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS donors (
        donor_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        age INTEGER NOT NULL,
        contact_number TEXT NOT NULL,
        email TEXT NOT NULL,
        city_locality TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        registration_date TEXT NOT NULL,
        availability_status TEXT NOT NULL,
        last_donation_date TEXT,
        total_donations INTEGER DEFAULT 0
    )
    """)

    # Hospitals / Blood Banks table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hospitals_blood_banks (
        centre_id TEXT PRIMARY KEY,
        centre_name TEXT NOT NULL,
        centre_type TEXT NOT NULL,
        location TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        contact_phone TEXT NOT NULL,
        emergency_contact TEXT NOT NULL
    )
    """)

    # Blood Stock table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blood_stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        centre_id TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        available_units INTEGER NOT NULL DEFAULT 0,
        last_stock_update TEXT NOT NULL,
        FOREIGN KEY (centre_id) REFERENCES hospitals_blood_banks (centre_id),
        UNIQUE(centre_id, blood_group)
    )
    """)

    # Donations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS donations (
        donation_id TEXT PRIMARY KEY,
        donor_id TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        centre_id TEXT NOT NULL,
        donation_date TEXT NOT NULL,
        units_donated INTEGER DEFAULT 1,
        status TEXT NOT NULL,
        FOREIGN KEY (donor_id) REFERENCES donors (donor_id),
        FOREIGN KEY (centre_id) REFERENCES hospitals_blood_banks (centre_id)
    )
    """)

    # Emergency Requests table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emergency_requests (
        request_id TEXT PRIMARY KEY,
        hospital_name TEXT NOT NULL,
        centre_id TEXT NOT NULL,
        required_blood_group TEXT NOT NULL,
        required_units INTEGER NOT NULL,
        urgency_level TEXT NOT NULL,
        request_datetime TEXT NOT NULL,
        location TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        status TEXT NOT NULL,
        matched_donors_count INTEGER DEFAULT 0
    )
    """)

    # Health Screenings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS health_screenings (
        screening_id TEXT PRIMARY KEY,
        donor_id TEXT NOT NULL,
        donor_name TEXT NOT NULL,
        screening_datetime TEXT NOT NULL,
        temperature REAL NOT NULL,
        heart_rate INTEGER NOT NULL,
        spo2 INTEGER NOT NULL,
        systolic_bp INTEGER NOT NULL,
        diastolic_bp INTEGER NOT NULL,
        health_questionnaire_passed INTEGER NOT NULL,
        preliminary_status TEXT NOT NULL,
        review_notes TEXT,
        evaluated_by TEXT DEFAULT 'Staff Operator',
        FOREIGN KEY (donor_id) REFERENCES donors (donor_id)
    )
    """)

    conn.commit()
    conn.close()

# Data fetching functions returning Pandas DataFrames

def fetch_table_df(table_name: str) -> pd.DataFrame:
    """Fetch complete table as Pandas DataFrame."""
    conn = get_connection()
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    except Exception as e:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

def fetch_donors() -> pd.DataFrame:
    return fetch_table_df("donors")

def fetch_hospitals() -> pd.DataFrame:
    return fetch_table_df("hospitals_blood_banks")

def fetch_blood_stock() -> pd.DataFrame:
    conn = get_connection()
    query = """
    SELECT bs.*, h.centre_name, h.centre_type, h.location
    FROM blood_stock bs
    JOIN hospitals_blood_banks h ON bs.centre_id = h.centre_id
    """
    try:
        df = pd.read_sql_query(query, conn)
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

def fetch_donations() -> pd.DataFrame:
    return fetch_table_df("donations")

def fetch_emergency_requests() -> pd.DataFrame:
    return fetch_table_df("emergency_requests")

def fetch_health_screenings() -> pd.DataFrame:
    return fetch_table_df("health_screenings")

# CRUD Operations

def insert_donor(donor_dict: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO donors (donor_id, name, blood_group, age, contact_number, email, city_locality, latitude, longitude, registration_date, availability_status, last_donation_date, total_donations)
    VALUES (:donor_id, :name, :blood_group, :age, :contact_number, :email, :city_locality, :latitude, :longitude, :registration_date, :availability_status, :last_donation_date, :total_donations)
    """, donor_dict)
    conn.commit()
    conn.close()

def update_donor(donor_id: str, update_dict: dict):
    conn = get_connection()
    cursor = conn.cursor()
    set_clause = ", ".join([f"{k} = :{k}" for k in update_dict.keys()])
    update_dict['donor_id'] = donor_id
    cursor.execute(f"UPDATE donors SET {set_clause} WHERE donor_id = :donor_id", update_dict)
    conn.commit()
    conn.close()

def update_stock_units(centre_id: str, blood_group: str, new_units: int, timestamp: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO blood_stock (centre_id, blood_group, available_units, last_stock_update)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(centre_id, blood_group) DO UPDATE SET
        available_units = excluded.available_units,
        last_stock_update = excluded.last_stock_update
    """, (centre_id, blood_group, new_units, timestamp))
    conn.commit()
    conn.close()

def insert_emergency_request(req_dict: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO emergency_requests (request_id, hospital_name, centre_id, required_blood_group, required_units, urgency_level, request_datetime, location, latitude, longitude, status, matched_donors_count)
    VALUES (:request_id, :hospital_name, :centre_id, :required_blood_group, :required_units, :urgency_level, :request_datetime, :location, :latitude, :longitude, :status, :matched_donors_count)
    """, req_dict)
    conn.commit()
    conn.close()

def update_request_status(request_id: str, new_status: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE emergency_requests SET status = ? WHERE request_id = ?", (new_status, request_id))
    conn.commit()
    conn.close()

def insert_health_screening(screening_dict: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO health_screenings (screening_id, donor_id, donor_name, screening_datetime, temperature, heart_rate, spo2, systolic_bp, diastolic_bp, health_questionnaire_passed, preliminary_status, review_notes, evaluated_by)
    VALUES (:screening_id, :donor_id, :donor_name, :screening_datetime, :temperature, :heart_rate, :spo2, :systolic_bp, :diastolic_bp, :health_questionnaire_passed, :preliminary_status, :review_notes, :evaluated_by)
    """, screening_dict)
    conn.commit()
    conn.close()

def update_screening_status(screening_id: str, new_status: str, notes: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE health_screenings SET preliminary_status = ?, review_notes = ? WHERE screening_id = ?", (new_status, notes, screening_id))
    conn.commit()
    conn.close()
