import re
from datetime import datetime

def validate_email(email: str) -> tuple[bool, str]:
    """Validate email format."""
    if not email:
        return False, "Email address is required."
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(pattern, email):
        return False, "Invalid email address format (e.g., donor@example.com)."
    return True, ""

def validate_phone(phone: str) -> tuple[bool, str]:
    """Validate phone number format."""
    if not phone:
        return False, "Contact number is required."
    # Allow 10 to 15 digits, optionally prefixed with +
    pattern = r"^\+?[0-9]{10,15}$"
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)
    if not re.match(pattern, cleaned):
        return False, "Invalid contact number format (must contain 10-15 digits)."
    return True, ""

def validate_donor_age(age: int) -> tuple[bool, str]:
    """Validate donor age for blood donation eligibility guidelines."""
    if age is None or age < 18:
        return False, "Donor must be at least 18 years old."
    if age > 65:
        return False, "Donor age exceeds general donation threshold (65 years). Medical review required."
    return True, ""

def validate_screening_vitals(temp: float, heart_rate: int, spo2: int, sys_bp: int, dia_bp: int) -> tuple[bool, str]:
    """Validate screening sensor ranges."""
    if temp < 30.0 or temp > 43.0:
        return False, "Body temperature reading out of physiological bounds (30°C - 43°C)."
    if heart_rate < 30 or heart_rate > 220:
        return False, "Heart rate out of physiological bounds (30 - 220 bpm)."
    if spo2 < 50 or spo2 > 100:
        return False, "SpO2 reading must be between 50% and 100%."
    if sys_bp < 60 or sys_bp > 240:
        return False, "Systolic BP reading out of bounds (60 - 240 mmHg)."
    if dia_bp < 40 or dia_bp > 150:
        return False, "Diastolic BP reading out of bounds (40 - 150 mmHg)."
    if sys_bp <= dia_bp:
        return False, "Systolic BP must be strictly greater than Diastolic BP."
    return True, ""
