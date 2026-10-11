"""
Analytics and Insights Generator with AI Donor Matching & Demand Analytics.
"""

import pandas as pd
import numpy as np

# Medical Compatibility Matrix for Packed Red Blood Cells
BLOOD_COMPATIBILITY_MATRIX = {
    "O-": ["O-"],
    "O+": ["O-", "O+"],
    "A-": ["O-", "A-"],
    "A+": ["O-", "O+", "A-", "A+"],
    "B-": ["O-", "B-"],
    "B+": ["O-", "O+", "B-", "B+"],
    "AB-": ["O-", "A-", "B-", "AB-"],
    "AB+": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"]
}

def get_compatible_donor_types(required_blood_group: str) -> list:
    """Return list of blood groups compatible for a recipient."""
    return BLOOD_COMPATIBILITY_MATRIX.get(required_blood_group, [required_blood_group])

def compute_ai_donor_matches(
    request_blood_group: str,
    request_lat: float,
    request_lon: float,
    donors_df: pd.DataFrame,
    screenings_df: pd.DataFrame = None,
    max_distance_km: float = 50.0
) -> pd.DataFrame:
    """
    AI-assisted donor matching algorithm based on:
    1. Biological Blood Compatibility
    2. Availability Status ('Available')
    3. Haversine Geographic Distance
    4. Health Screening Flag Status
    """
    if donors_df.empty:
        return pd.DataFrame()

    compatible_groups = get_compatible_donor_types(request_blood_group)
    
    # Filter available donors with compatible blood group
    matches = donors_df[
        (donors_df['blood_group'].isin(compatible_groups)) & 
        (donors_df['availability_status'] == 'Available')
    ].copy()

    if matches.empty:
        return matches

    # Merge health screening status if available
    if screenings_df is not None and not screenings_df.empty:
        # Get latest screening per donor
        latest_screenings = screenings_df.sort_values('screening_datetime').groupby('donor_id').last().reset_index()
        matches = matches.merge(
            latest_screenings[['donor_id', 'preliminary_status', 'health_questionnaire_passed']], 
            on='donor_id', 
            how='left'
        )
        matches['screening_clear'] = matches['preliminary_status'].isin(['No Initial Warning Detected', 'Screening Completed']) | matches['preliminary_status'].isna()
    else:
        matches['screening_clear'] = True
        matches['preliminary_status'] = 'Not Screened'

    # Compute Haversine distance
    R = 6371.0 # Earth radius in km
    lat1 = np.radians(request_lat)
    lon1 = np.radians(request_lon)
    lat2 = np.radians(matches['latitude'])
    lon2 = np.radians(matches['longitude'])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    matches['distance_km'] = (R * c).round(2)

    # Calculate AI Compatibility & Readiness Score (0 - 100%)
    # Factors: Exact blood match (30%), Distance proximity (40%), Screening clearance (20%), Total donation experience (10%)
    def calculate_score(row):
        score = 0.0
        # Exact blood match bonus
        if row['blood_group'] == request_blood_group:
            score += 30.0
        else:
            score += 15.0 # Compatible match

        # Distance score (decay as distance increases)
        dist = row['distance_km']
        dist_score = max(0.0, 40.0 * (1.0 - (dist / max_distance_km)))
        score += dist_score

        # Screening score
        if row['screening_clear']:
            score += 20.0
        else:
            score += 5.0

        # Experience score
        exp_score = min(10.0, row.get('total_donations', 0) * 2.0)
        score += exp_score

        return round(score, 1)

    matches['ai_match_score'] = matches.apply(calculate_score, axis=1)
    
    # Sort by highest score and shortest distance
    matches = matches.sort_values(by=['ai_match_score', 'distance_km'], ascending=[False, True])
    return matches

def generate_dynamic_analytics_insights(
    donors_df: pd.DataFrame,
    stock_df: pd.DataFrame,
    donations_df: pd.DataFrame,
    requests_df: pd.DataFrame,
    screenings_df: pd.DataFrame,
    hospitals_df: pd.DataFrame
) -> list[dict]:
    """Generate dynamic textual analytics insights from database tables."""
    insights = []

    # Insight 1: Most registered blood group
    if not donors_df.empty:
        bg_counts = donors_df['blood_group'].value_counts()
        top_bg = bg_counts.index[0]
        top_bg_cnt = bg_counts.iloc[0]
        pct = (top_bg_cnt / len(donors_df)) * 100
        insights.append({
            "category": "Donor Distribution",
            "title": "Highest Registered Blood Group",
            "text": f"Blood Group **{top_bg}** has the highest donor registration with **{top_bg_cnt} donors** ({pct:.1f}% of all registered donors).",
            "icon": "🩸",
            "type": "info"
        })

    # Insight 2: Highest completed donation count group
    if not donations_df.empty:
        completed = donations_df[donations_df['status'] == 'Completed']
        if not completed.empty:
            top_don_bg = completed['blood_group'].value_counts().index[0]
            top_don_cnt = completed['blood_group'].value_counts().iloc[0]
            insights.append({
                "category": "Donation Trends",
                "title": "Most Frequently Donated Blood Group",
                "text": f"Blood Group **{top_don_bg}** accounts for the most completed donations, totaling **{top_don_cnt} successful donations**.",
                "icon": "🏆",
                "type": "success"
            })

    # Insight 3: Lowest stock blood group
    if not stock_df.empty:
        bg_stock = stock_df.groupby('blood_group')['available_units'].sum()
        lowest_bg = bg_stock.idxmin()
        lowest_units = bg_stock.min()
        insights.append({
            "category": "Inventory Alert",
            "title": "Lowest Available Blood Stock",
            "text": f"Blood Group **{lowest_bg}** currently has the lowest combined stock across all centres with only **{lowest_units} units available**.",
            "icon": "⚠️",
            "type": "warning" if lowest_units < 15 else "info"
        })

    # Insight 4: Top hospital by available stock
    if not stock_df.empty:
        hosp_stock = stock_df.groupby('centre_name')['available_units'].sum()
        top_hosp = hosp_stock.idxmax()
        top_units = hosp_stock.max()
        insights.append({
            "category": "Hospital Inventory",
            "title": "Largest Stock Repository",
            "text": f"**{top_hosp}** holds the largest inventory with **{top_units} total blood units** on standby.",
            "icon": "🏥",
            "type": "info"
        })

    # Insight 5: Peak donation month
    if not donations_df.empty:
        donations_df['month'] = pd.to_datetime(donations_df['donation_date']).dt.strftime('%B %Y')
        month_counts = donations_df['month'].value_counts()
        if not month_counts.empty:
            top_month = month_counts.index[0]
            top_month_cnt = month_counts.iloc[0]
            insights.append({
                "category": "Temporal Analytics",
                "title": "Peak Donation Period",
                "text": f"**{top_month}** recorded the highest donation activity with **{top_month_cnt} donations** processed.",
                "icon": "📅",
                "type": "info"
            })

    # Insight 6: Emergency Requests Fulfillment Rate
    if not requests_df.empty:
        total_reqs = len(requests_df)
        fulfilled_reqs = len(requests_df[requests_df['status'] == 'Fulfilled'])
        pending_reqs = len(requests_df[requests_df['status'].isin(['Received', 'Donor Matched', 'Contacted'])])
        fulfill_rate = (fulfilled_reqs / total_reqs * 100) if total_reqs > 0 else 0
        insights.append({
            "category": "Emergency Response",
            "title": "Request Fulfillment Rate",
            "text": f"**{fulfill_rate:.1f}%** of emergency blood requests ({fulfilled_reqs}/{total_reqs}) have been successfully fulfilled. Currently, **{pending_reqs} requests are pending active matching**.",
            "icon": "🚨",
            "type": "emergency" if pending_reqs > 5 else "success"
        })

    # Insight 7: Pre-donation Medical Review Rate
    if not screenings_df.empty:
        total_screen = len(screenings_df)
        review_cnt = len(screenings_df[screenings_df['preliminary_status'].isin(['Medical Review Required', 'Temporary Deferral and Reassessment'])])
        review_pct = (review_cnt / total_screen * 100) if total_screen > 0 else 0
        insights.append({
            "category": "Health Screening",
            "title": "Preliminary Deferral & Review Rate",
            "text": f"**{review_pct:.1f}%** of pre-donation health screenings ({review_cnt}/{total_screen}) flagged readings requiring physician review or temporary deferral.",
            "icon": "🩺",
            "type": "warning" if review_pct > 20 else "info"
        })

    return insights
