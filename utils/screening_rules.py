"""
Pre-Donation Health Screening Rule Engine.
Evaluates preliminary sensor readings & questionnaire flags.

SAFETY MANDATE:
Automated rules & sensor readings are preliminary indicators only, NOT medical clearance.
Final donor eligibility must be determined by qualified blood-bank healthcare personnel.
"""

def evaluate_health_screening(
    temperature: float,
    heart_rate: int,
    spo2: int,
    systolic_bp: int,
    diastolic_bp: int,
    questionnaire_passed: bool
) -> dict:
    """
    Evaluates preliminary screening readings against configurable standard reference ranges.
    
    Standard Reference Ranges:
    - Temperature: 36.1°C to 37.5°C (97.0°F - 99.5°F)
    - Heart Rate: 60 - 100 bpm
    - SpO2: 95% - 100%
    - Systolic BP: 90 - 140 mmHg
    - Diastolic BP: 60 - 90 mmHg
    - Questionnaire: All mandatory safety responses must pass
    """
    warnings = []
    requires_medical_review = False
    temporary_deferral = False

    # Temperature check
    if temperature > 37.5:
        warnings.append(f"Elevated body temperature ({temperature:.1f}°C > 37.5°C threshold). Risk of fever/infection.")
        temporary_deferral = True
    elif temperature < 36.0:
        warnings.append(f"Low body temperature ({temperature:.1f}°C < 36.0°C threshold).")
        requires_medical_review = True

    # Heart rate check
    if heart_rate < 60:
        warnings.append(f"Bradycardia detected: Heart rate is {heart_rate} bpm (Normal: 60-100 bpm).")
        requires_medical_review = True
    elif heart_rate > 100:
        warnings.append(f"Tachycardia detected: Heart rate is {heart_rate} bpm (Normal: 60-100 bpm).")
        requires_medical_review = True

    # SpO2 check
    if spo2 < 95:
        warnings.append(f"Sub-optimal oxygen saturation (SpO2: {spo2}% < 95% target).")
        temporary_deferral = True

    # Blood pressure check
    if systolic_bp > 140 or diastolic_bp > 90:
        warnings.append(f"Elevated Blood Pressure: {systolic_bp}/{diastolic_bp} mmHg (Threshold: 140/90 mmHg).")
        temporary_deferral = True
    elif systolic_bp < 90 or diastolic_bp < 60:
        warnings.append(f"Low Blood Pressure: {systolic_bp}/{diastolic_bp} mmHg (Threshold: 90/60 mmHg).")
        requires_medical_review = True

    # Questionnaire check
    if not questionnaire_passed:
        warnings.append("Health questionnaire flagged recent illness, medication, or high-risk travel.")
        requires_medical_review = True

    # Determine status label
    if temporary_deferral:
        status_label = "Temporary Deferral and Reassessment"
    elif requires_medical_review:
        status_label = "Medical Review Required"
    elif len(warnings) == 0:
        status_label = "No Initial Warning Detected"
    else:
        status_label = "Screening Completed"

    return {
        "status_label": status_label,
        "warnings": warnings,
        "requires_medical_review": requires_medical_review or temporary_deferral,
        "temporary_deferral": temporary_deferral,
        "is_normal": len(warnings) == 0,
        "reference_ranges": {
            "temperature": "36.1°C - 37.5°C",
            "heart_rate": "60 - 100 bpm",
            "spo2": "95% - 100%",
            "bp": "90-140 / 60-90 mmHg"
        },
        "disclaimer": "Sensor readings and automated rules are preliminary indicators only, not medical clearance. Final eligibility must be decided by qualified staff."
    }
