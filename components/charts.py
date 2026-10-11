"""
Advanced Plotly & Folium Interactive Visualization Engine.
Global Overlap Fix: Reduced title sizes, dedicated top padding, repositioned legends (bottom/right),
and clean spacing across all 13 visualizations.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import streamlit as st
import folium
from folium.plugins import MarkerCluster, HeatMap, MiniMap
from streamlit_folium import st_folium

# Color Palette Definitions
COLOR_MAP = {
    "O+": "#DC2626",   # Bright Crimson
    "O-": "#991B1B",   # Dark Red
    "A+": "#2563EB",   # Royal Blue
    "A-": "#1D4ED8",   # Dark Blue
    "B+": "#059669",   # Emerald Green
    "B-": "#047857",   # Dark Emerald
    "AB+": "#7C3AED",  # Deep Purple
    "AB-": "#6D28D9"   # Dark Purple
}

STATUS_COLORS = {
    "Available": "#10B981",
    "Unavailable": "#94A3B8",
    "Temporarily Unavailable": "#F97316"
}

SCREENING_COLORS = {
    "No Initial Warning Detected": "#10B981",
    "Screening Completed": "#3B82F6",
    "Medical Review Required": "#F59E0B",
    "Temporary Deferral and Reassessment": "#EF4444"
}

CHART_FONT = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
TITLE_FONT_SIZE = 12
AXIS_FONT_SIZE = 10.5

def shorten_hospital_name(name: str) -> str:
    """Shorten long hospital names for clean axis tick rendering."""
    short_map = {
        "Karur Government Medical College Hospital": "Karur Govt Med College",
        "St. Joseph Blood Bank & Transfusion": "St. Joseph Blood Bank",
        "Chennai General Hospital Transfusion Depot": "Chennai General Hosp",
        "Coimbatore Medical College Hospital": "Coimbatore Med College",
        "Madurai Rajaji Government Hospital": "Madurai Rajaji Hosp",
        "Trichy MGM Government Hospital": "Trichy MGM Govt Hosp",
        "Tiruppur Regional Red Cross Depot": "Tiruppur Red Cross",
        "Salem Mohan Kumaramangalam Hospital": "Salem Mohan Hosp",
        "Erode District Headquarters Hospital": "Erode District Hosp",
        "Tirunelveli Medical College Hospital": "Tirunelveli Med College",
        "Vellore CMC Transfusion Center": "Vellore CMC Center",
        "Thoothukudi Government Hospital": "Thoothukudi Govt Hosp",
        "Dindigul Central Medical Depot": "Dindigul Med Depot",
        "Thanjavur Medical College Hospital": "Thanjavur Med College",
        "Nagercoil City Blood Center": "Nagercoil Blood Center",
        "Hosur Industrial Medical Hub": "Hosur Medical Hub",
        "Kumbakonam Temple Town Hospital": "Kumbakonam Hospital"
    }
    return short_map.get(name, name[:22] + "..." if len(name) > 24 else name)

# --- CHART 1: Donut Chart - Donor Availability ---
def build_chart_1_availability(donors_df: pd.DataFrame):
    if donors_df.empty:
        return go.Figure()
    
    counts = donors_df['availability_status'].value_counts().reset_index()
    counts.columns = ['status', 'count']
    
    tot_donors = len(donors_df)
    avail_cnt = donors_df[donors_df['availability_status'] == 'Available'].shape[0]
    avail_pct = round((avail_cnt / max(tot_donors, 1)) * 100, 1)

    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        labels=counts['status'],
        values=counts['count'],
        hole=0.62,
        marker=dict(
            colors=[STATUS_COLORS.get(s, "#64748B") for s in counts['status']],
            line=dict(color='#FFFFFF', width=2)
        ),
        textinfo='label+percent',
        textposition='outside',
        pull=[0.05 if s == 'Temporarily Unavailable' else 0 for s in counts['status']],
        hovertemplate='<b>Status:</b> %{label}<br><b>Donors:</b> %{value:,}<br><b>Percentage:</b> %{percent}<extra></extra>'
    ))

    fig.add_annotation(
        text=f"<b style='font-size:16px; color:#0F172A;'>{avail_pct}%</b><br><span style='font-size:10px; color:#64748B;'>Active Readiness</span><br><b style='font-size:11px; color:#10B981;'>{avail_cnt:,} / {tot_donors:,}</b>",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(family=CHART_FONT, size=11)
    )

    fig.update_layout(
        title=dict(
            text="<b>Blood Donor Availability Status & Readiness</b>", 
            font=dict(family=CHART_FONT, size=TITLE_FONT_SIZE, color="#0F172A"),
            y=0.97, x=0.01, xanchor='left', yanchor='top'
        ),
        font=dict(family=CHART_FONT, size=AXIS_FONT_SIZE),
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
        margin=dict(t=50, b=50, l=20, r=20),
        height=380
    )
    return fig

# --- CHART 2: Horizontal Bar Chart - Blood Group Distribution ---
def build_chart_2_blood_group_dist(donors_df: pd.DataFrame):
    if donors_df.empty:
        return go.Figure()

    counts = donors_df['blood_group'].value_counts().reset_index()
    counts.columns = ['blood_group', 'count']
    total_cnt = counts['count'].sum()
    counts['pct'] = (counts['count'] / total_cnt * 100).round(1)
    
    counts = counts.sort_values(by='count', ascending=True)
    max_row = counts.iloc[-1]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=counts['blood_group'],
        x=counts['count'],
        orientation='h',
        text=[f"<b>{c:,}</b> ({p}%)" for c, p in zip(counts['count'], counts['pct'])],
        textposition='outside',
        marker=dict(
            color=[COLOR_MAP.get(bg, '#2563EB') for bg in counts['blood_group']],
            line=dict(color='#0F172A', width=1)
        ),
        customdata=counts['pct'],
        hovertemplate='<b>Blood Group:</b> %{y}<br><b>Registered Donors:</b> %{x:,}<br><b>Share of Total:</b> %{customdata}%<extra></extra>'
    ))

    fig.add_annotation(
        x=max_row['count'],
        y=max_row['blood_group'],
        text=f" 🏆 Highest: <b>{max_row['blood_group']}</b>",
        showarrow=True,
        arrowhead=2,
        ax=55, ay=-10,
        font=dict(family=CHART_FONT, size=9.5, color="#DC2626"),
        bgcolor="#FEE2E2",
        bordercolor="#DC2626"
    )

    fig.update_layout(
        title=dict(
            text="<b>Blood Group Registration Share</b>", 
            font=dict(family=CHART_FONT, size=TITLE_FONT_SIZE, color="#0F172A"),
            y=0.97, x=0.01, xanchor='left', yanchor='top'
        ),
        font=dict(family=CHART_FONT, size=AXIS_FONT_SIZE),
        xaxis=dict(title="Registered Donors", showgrid=True, gridcolor="#E2E8F0"),
        yaxis=dict(title="Blood Group"),
        margin=dict(t=50, b=35, l=35, r=90),
        height=380
    )
    return fig

# --- CHART 3: Stacked Bar Chart - Available Blood Stock by Hospital ---
def build_chart_3_stock_by_hospital(stock_df: pd.DataFrame):
    if stock_df.empty:
        return go.Figure()

    df = stock_df.copy()
    df['short_name'] = df['centre_name'].apply(shorten_hospital_name)
    pivot_stock = df.pivot_table(index='short_name', columns='blood_group', values='available_units', aggfunc='sum', fill_value=0)
    centre_totals = pivot_stock.sum(axis=1)

    fig = go.Figure()

    for bg in [g for g in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"] if g in pivot_stock.columns]:
        fig.add_trace(go.Bar(
            name=bg,
            x=pivot_stock.index,
            y=pivot_stock[bg],
            marker_color=COLOR_MAP.get(bg, "#2563EB"),
            hovertemplate=f"<b>Hospital:</b> %{{x}}<br><b>Blood Group:</b> {bg}<br><b>Units:</b> %{{y}}<extra></extra>"
        ))

    # Add Total Units labels above stacked bars
    for short_name, tot in centre_totals.items():
        fig.add_annotation(
            x=short_name,
            y=tot + 2,
            text=f"<b>{int(tot)}u</b>",
            showarrow=False,
            font=dict(family=CHART_FONT, size=8, color="#0F172A")
        )

    avg_units = centre_totals.mean()
    fig.add_hline(
        y=avg_units,
        line_dash="dash",
        line_color="#EF4444",
        annotation_text=f"Mean Stock ({int(avg_units)}u)",
        annotation_position="bottom right"
    )

    fig.update_layout(
        title=dict(
            text="<b>Hospital Inventory Stacked Breakdown & Safety Baseline</b>", 
            font=dict(family=CHART_FONT, size=TITLE_FONT_SIZE, color="#0F172A"),
            y=0.97, x=0.01, xanchor='left', yanchor='top'
        ),
        barmode='stack',
        font=dict(family=CHART_FONT, size=AXIS_FONT_SIZE),
        xaxis=dict(title="Hospital / Blood Bank", tickangle=-35, tickfont=dict(size=8.5)),
        yaxis=dict(title="Available Stock (Units)"),
        legend=dict(
            title=dict(text="Blood Group", font=dict(size=9)),
            orientation="h", yanchor="top", y=-0.35, xanchor="center", x=0.5
        ),
        margin=dict(t=60, b=125, l=40, r=30),
        height=450
    )
    return fig

# --- CHART 4: Vertical Column Chart - Most Frequently Donated Blood Groups ---
def build_chart_4_frequently_donated(donations_df: pd.DataFrame):
    if donations_df.empty:
        return go.Figure()

    completed = donations_df[donations_df['status'] == 'Completed']
    counts = completed['blood_group'].value_counts().reset_index()
    counts.columns = ['blood_group', 'count']
    total_donations = counts['count'].sum()
    counts['pct'] = (counts['count'] / max(total_donations, 1) * 100).round(1)
    counts = counts.sort_values(by='count', ascending=False)
    
    mean_val = counts['count'].mean()

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=counts['blood_group'],
        y=counts['count'],
        text=[f"<b>{c:,}</b><br>({p}%)" for c, p in zip(counts['count'], counts['pct'])],
        textposition='outside',
        marker=dict(
            color=[COLOR_MAP.get(bg, '#2563EB') for bg in counts['blood_group']],
            line=dict(color='#0F172A', width=1)
        ),
        customdata=counts['pct'],
        hovertemplate='<b>Blood Group:</b> %{x}<br><b>Completed Donations:</b> %{y:,}<br><b>Share:</b> %{customdata}%<extra></extra>'
    ))

    fig.add_hline(
        y=mean_val,
        line_dash="dot",
        line_color="#64748B",
        annotation_text=f"Mean ({int(mean_val)})",
        annotation_position="bottom right"
    )

    fig.update_layout(
        title=dict(
            text="<b>Completed Donations Volume by Blood Group</b>", 
            font=dict(family=CHART_FONT, size=TITLE_FONT_SIZE, color="#0F172A"),
            y=0.97, x=0.01, xanchor='left', yanchor='top'
        ),
        font=dict(family=CHART_FONT, size=AXIS_FONT_SIZE),
        xaxis=dict(title="Blood Group"),
        yaxis=dict(title="Completed Donation Count", showgrid=True, gridcolor="#E2E8F0"),
        margin=dict(t=50, b=35, l=35, r=30),
        height=380
    )
    return fig

# --- CHART 5: Area Chart - Monthly Donation Trends ---
def build_chart_5_monthly_trends(donations_df: pd.DataFrame):
    if donations_df.empty:
        return go.Figure()

    df = donations_df.copy()
    df['month_dt'] = pd.to_datetime(df['donation_date']).dt.to_period('M').dt.to_timestamp()
    monthly = df.groupby('month_dt').size().reset_index(name='donation_count')
    monthly = monthly.sort_values('month_dt')
    
    monthly['moving_avg'] = monthly['donation_count'].rolling(window=3, min_periods=1).mean().round(1)
    peak_row = monthly.loc[monthly['donation_count'].idxmax()]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=monthly['month_dt'],
        y=monthly['donation_count'],
        mode='lines+markers',
        name='Actual Monthly Donations',
        fill='tozeroy',
        fillcolor='rgba(225, 29, 72, 0.15)',
        line=dict(color='#DC2626', width=2.5, shape='spline'),
        marker=dict(size=7, color='#DC2626'),
        hovertemplate='<b>Month:</b> %{x|%B %Y}<br><b>Donations:</b> %{y:,}<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=monthly['month_dt'],
        y=monthly['moving_avg'],
        mode='lines',
        name='3-Month Moving Avg',
        line=dict(color='#2563EB', width=2, dash='dash'),
        hovertemplate='<b>Trend (3M Avg):</b> %{y:.1f}<extra></extra>'
    ))

    fig.add_annotation(
        x=peak_row['month_dt'],
        y=peak_row['donation_count'],
        text=f"📌 Peak: <b>{peak_row['month_dt'].strftime('%b %Y')}</b> ({peak_row['donation_count']})",
        showarrow=True,
        arrowhead=2,
        ax=0, ay=-28,
        font=dict(family=CHART_FONT, size=9.5, color="#FFFFFF"),
        bgcolor="#DC2626",
        bordercolor="#991B1B"
    )

    fig.update_layout(
        title=dict(
            text="<b>Monthly Donation Telemetry & Trend Moving Average</b>", 
            font=dict(family=CHART_FONT, size=TITLE_FONT_SIZE, color="#0F172A"),
            y=0.97, x=0.01, xanchor='left', yanchor='top'
        ),
        font=dict(family=CHART_FONT, size=AXIS_FONT_SIZE),
        xaxis=dict(
            title="Date",
            rangeselector=dict(
                buttons=list([
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(step="all", label="All")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        ),
        yaxis=dict(title="Donation Count"),
        legend=dict(orientation="h", yanchor="top", y=-0.35, xanchor="center", x=0.5),
        margin=dict(t=55, b=85, l=35, r=30),
        height=420
    )
    return fig

# --- CHART 6: Grouped Bar Chart - Multi-Metric Conversion Comparison ---
def build_chart_6_donation_comparison(donors_df: pd.DataFrame, donations_df: pd.DataFrame):
    if donors_df.empty:
        return go.Figure()

    reg = donors_df['blood_group'].value_counts().reset_index(name='registered')
    avail = donors_df[donors_df['availability_status'] == 'Available']['blood_group'].value_counts().reset_index(name='available')
    donated = donations_df[donations_df['status'] == 'Completed']['blood_group'].value_counts().reset_index(name='donated')

    merged = reg.merge(avail, on='blood_group', how='left').merge(donated, on='blood_group', how='left').fillna(0)
    merged['avail_rate'] = (merged['available'] / np.maximum(merged['registered'], 1) * 100).round(1)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=merged['blood_group'], y=merged['registered'],
        name='Registered Donors', marker_color='#2563EB',
        hovertemplate='<b>Blood Group:</b> %{x}<br><b>Registered:</b> %{y:,}<extra></extra>'
    ))
    fig.add_trace(go.Bar(
        x=merged['blood_group'], y=merged['available'],
        name='Available Donors', marker_color='#10B981',
        customdata=merged['avail_rate'],
        hovertemplate='<b>Blood Group:</b> %{x}<br><b>Available:</b> %{y:,}<br><b>Readiness Rate:</b> %{customdata}%<extra></extra>'
    ))
    fig.add_trace(go.Bar(
        x=merged['blood_group'], y=merged['donated'],
        name='Donations Completed', marker_color='#E11D48',
        hovertemplate='<b>Blood Group:</b> %{x}<br><b>Completed Donations:</b> %{y:,}<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text="<b>Registered vs Available vs Completed Donations Matrix</b>", 
            font=dict(family=CHART_FONT, size=TITLE_FONT_SIZE, color="#0F172A"),
            y=0.97, x=0.01, xanchor='left', yanchor='top'
        ),
        barmode='group',
        font=dict(family=CHART_FONT, size=AXIS_FONT_SIZE),
        xaxis_title="Blood Group",
        yaxis_title="Volume Count",
        legend=dict(orientation="h", yanchor="top", y=-0.20, xanchor="center", x=0.5),
        margin=dict(t=50, b=60, l=35, r=30),
        height=400
    )
    return fig

# --- CHART 7: Heatmap Matrix - Blood Stock by Hospital ---
def build_chart_7_stock_heatmap(stock_df: pd.DataFrame):
    if stock_df.empty:
        return go.Figure()

    df = stock_df.copy()
    df['short_name'] = df['centre_name'].apply(shorten_hospital_name)
    pivot = df.pivot_table(index='short_name', columns='blood_group', values='available_units', aggfunc='sum', fill_value=0)

    text_matrix = []
    for r in pivot.index:
        row_txt = []
        for c in pivot.columns:
            val = int(pivot.loc[r, c])
            if val < 8:
                row_txt.append(f"⚠️{val}")
            else:
                row_txt.append(f"{val}")
        text_matrix.append(row_txt)

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='Reds',
        text=text_matrix,
        texttemplate="%{text}",
        textfont={"size": 9, "family": CHART_FONT},
        colorbar=dict(title="Units Stock", len=0.8, y=0.45)
    ))

    fig.update_layout(
        title=dict(
            text="<b>Inventory Heatmap Matrix (⚠️ Flags Stock < 8 Units)</b>", 
            font=dict(family=CHART_FONT, size=TITLE_FONT_SIZE, color="#0F172A"),
            y=0.97, x=0.01, xanchor='left', yanchor='top'
        ),
        font=dict(family=CHART_FONT, size=AXIS_FONT_SIZE),
        xaxis_title="Blood Group",
        yaxis=dict(title="Hospital / Blood Bank", tickfont=dict(size=9)),
        margin=dict(t=55, b=40, l=155, r=20),
        height=450
    )
    return fig

# --- CHART 8: Funnel Chart - Emergency Request Workflow ---
def build_chart_8_request_funnel(requests_df: pd.DataFrame):
    if requests_df.empty:
        return go.Figure()

    tot_received = len(requests_df)
    matched = len(requests_df[requests_df['status'].isin(['Donor Matched', 'Contacted', 'In Progress', 'Fulfilled'])])
    contacted = len(requests_df[requests_df['status'].isin(['Contacted', 'In Progress', 'Fulfilled'])])
    in_progress = len(requests_df[requests_df['status'].isin(['In Progress', 'Fulfilled'])])
    fulfilled = len(requests_df[requests_df['status'] == 'Fulfilled'])

    stages = ["1. Reqs Received", "2. Compatible Donors Identified", "3. Donors Contacted", "4. Donation In-Progress", "5. Requests Fulfilled"]
    values = [tot_received, matched, contacted, in_progress, fulfilled]

    step_retention = [100.0]
    for i in range(1, len(values)):
        ret = (values[i] / max(values[i-1], 1) * 100)
        step_retention.append(round(ret, 1))

    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textinfo="value+percent initial",
        customdata=step_retention,
        hovertemplate='<b>Stage:</b> %{y}<br><b>Count:</b> %{x:,}<br><b>Step Conversion:</b> %{customdata}%<extra></extra>',
        marker={"color": ["#DC2626", "#EA580C", "#F59E0B", "#2563EB", "#10B981"]}
    ))

    fig.update_layout(
        title=dict(
            text="<b>Emergency Request Fulfillment Workflow Funnel</b>", 
            font=dict(family=CHART_FONT, size=TITLE_FONT_SIZE, color="#0F172A"),
            y=0.97, x=0.01, xanchor='left', yanchor='top'
        ),
        font=dict(family=CHART_FONT, size=AXIS_FONT_SIZE),
        margin=dict(t=50, b=30, l=40, r=40),
        height=380
    )
    return fig

# --- CHART 9: Histogram - Donor Age Distribution ---
def build_chart_9_age_distribution(donors_df: pd.DataFrame):
    if donors_df.empty:
        return go.Figure()

    ages = donors_df['age'].dropna()
    mean_age = ages.mean()

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=ages,
        nbinsx=12,
        name='Donor Count',
        marker=dict(color='#2563EB', line=dict(color='#0F172A', width=1)),
        opacity=0.85,
        hovertemplate='<b>Age Bin:</b> %{x} yrs<br><b>Donor Count:</b> %{y}<extra></extra>'
    ))

    if len(ages) > 1:
        kde_x = np.linspace(ages.min(), ages.max(), 100)
        std = ages.std()
        n = len(ages)
        bandwidth = 1.06 * std * (n ** (-1/5))
        kde_y = np.sum([np.exp(-0.5 * ((kde_x - x) / bandwidth) ** 2) for x in ages], axis=0)
        kde_y = kde_y / (n * bandwidth * np.sqrt(2 * np.pi))
        counts, _ = np.histogram(ages, bins=12)
        scale_factor = counts.max() / max(kde_y.max(), 0.001)
        
        fig.add_trace(go.Scatter(
            x=kde_x,
            y=kde_y * scale_factor,
            mode='lines',
            name='Age Density (KDE)',
            line=dict(color='#DC2626', width=2.5, shape='spline'),
            hovertemplate='<b>Age:</b> %{x:.1f} yrs<extra></extra>'
        ))

    fig.add_vline(
        x=mean_age,
        line_dash="dash",
        line_color="#EF4444",
        annotation_text=f"Mean: {mean_age:.1f} Yrs",
        annotation_position="top right"
    )

    fig.update_layout(
        title=dict(
            text="<b>Registered Donor Age Distribution & Density Curve</b>", 
            font=dict(family=CHART_FONT, size=TITLE_FONT_SIZE, color="#0F172A"),
            y=0.97, x=0.01, xanchor='left', yanchor='top'
        ),
        font=dict(family=CHART_FONT, size=AXIS_FONT_SIZE),
        xaxis=dict(title="Age (Years)"),
        yaxis=dict(title="Donor Frequency"),
        legend=dict(orientation="h", yanchor="top", y=-0.20, xanchor="center", x=0.5),
        margin=dict(t=50, b=60, l=35, r=30),
        height=380
    )
    return fig

# --- CHART 10: Advanced Folium Map ---
def build_chart_10_location_map(donors_df: pd.DataFrame, hospitals_df: pd.DataFrame):
    if hospitals_df.empty:
        center_lat, center_lon = 10.9601, 78.0766
    else:
        center_lat = hospitals_df['latitude'].mean()
        center_lon = hospitals_df['longitude'].mean()

    m = folium.Map(
        location=[center_lat, center_lon], 
        zoom_start=11, 
        tiles="OpenStreetMap",
        attr="🇮🇳 India Emergency Blood Network - Tamil Nadu | © OpenStreetMap"
    )

    MiniMap(toggle_display=True).add_to(m)

    hosp_group = folium.FeatureGroup(name="🏥 Hospitals & Blood Banks")
    for _, row in hospitals_df.iterrows():
        icon_color = "red" if row['centre_type'] == "Hospital" else "blue"
        popup_html = f"""
        <div style="font-family:sans-serif; width:220px; font-size:0.85rem;">
            <b style="color:#0F172A; font-size:1rem;">{row['centre_name']}</b><br>
            <span style="color:#64748B;">Facility Type: <b>{row['centre_type']}</b></span><br>
            <span style="color:#64748B;">Locality: {row['location']}</span><br>
            <hr style="margin:6px 0;">
            <span style="color:#DC2626; font-weight:bold;">📞 Emergency Contact:</span><br>
            <a href="tel:{row['emergency_contact']}" style="color:#2563EB; font-weight:bold;">{row['emergency_contact']}</a>
        </div>
        """
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{row['centre_name']} ({row['centre_type']})",
            icon=folium.Icon(color=icon_color, icon="hospital-o", prefix="fa")
        ).add_to(hosp_group)
    hosp_group.add_to(m)

    if not donors_df.empty:
        donor_cluster = MarkerCluster(name="👥 Donor Locations (Clustered)").add_to(m)
        heat_data = []

        for _, row in donors_df.iterrows():
            circle_color = "#10B981" if row['availability_status'] == "Available" else "#94A3B8"
            heat_data.append([row['latitude'], row['longitude'], 1.0])
            
            popup_html = f"""
            <div style="font-family:sans-serif; width:180px; font-size:0.82rem;">
                <b>Donor ID:</b> {row['donor_id']}<br>
                <b>Blood Group:</b> <span style="color:#DC2626; font-weight:bold;">{row['blood_group']}</span><br>
                <b>Status:</b> <span style="color:{circle_color}; font-weight:bold;">{row['availability_status']}</span><br>
                <b>Locality:</b> {row['city_locality']}<br>
                <b>Completed Donations:</b> {row['total_donations']}
            </div>
            """
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=6,
                color=circle_color,
                fill=True,
                fill_color=circle_color,
                fill_opacity=0.75,
                popup=folium.Popup(popup_html, max_width=200),
                tooltip=f"Donor {row['donor_id']} ({row['blood_group']})"
            ).add_to(donor_cluster)

        heat_layer = HeatMap(heat_data, name="🔥 Donor Density Heatmap", radius=15, blur=10, min_opacity=0.4)
        heat_layer.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    return m

# --- CHART 11: Pre-Donation Health Screening Outcomes ---
def build_chart_11_health_screening(screenings_df: pd.DataFrame):
    if screenings_df.empty:
        return go.Figure()

    counts = screenings_df['preliminary_status'].value_counts().reset_index()
    counts.columns = ['status', 'count']
    tot = counts['count'].sum()
    counts['pct'] = (counts['count'] / max(tot, 1) * 100).round(1)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=counts['status'],
        y=counts['count'],
        text=[f"<b>{c:,}</b> ({p}%)" for c, p in zip(counts['count'], counts['pct'])],
        textposition='outside',
        marker=dict(
            color=[SCREENING_COLORS.get(s, '#2563EB') for s in counts['status']],
            line=dict(color='#0F172A', width=1)
        ),
        customdata=counts['pct'],
        hovertemplate='<b>Outcome Status:</b> %{x}<br><b>Screening Count:</b> %{y:,}<br><b>Share:</b> %{customdata}%<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text="<b>Pre-Donation Health Screening Outcomes</b>", 
            font=dict(family=CHART_FONT, size=TITLE_FONT_SIZE, color="#0F172A"),
            y=0.97, x=0.01, xanchor='left', yanchor='top'
        ),
        font=dict(family=CHART_FONT, size=AXIS_FONT_SIZE),
        xaxis=dict(title="Screening Status"),
        yaxis=dict(title="Evaluation Count"),
        margin=dict(t=50, b=40, l=35, r=30),
        height=380
    )
    return fig

# --- CHART 12: Line Chart - Screening Outcome Trends ---
def build_chart_12_screening_trends(screenings_df: pd.DataFrame):
    if screenings_df.empty:
        return go.Figure()

    df = screenings_df.copy()
    df['date'] = pd.to_datetime(df['screening_datetime']).dt.date
    daily = df.groupby(['date', 'preliminary_status']).size().reset_index(name='count')

    fig = go.Figure()

    for st_name in daily['preliminary_status'].unique():
        sub_df = daily[daily['preliminary_status'] == st_name]
        fig.add_trace(go.Scatter(
            x=sub_df['date'],
            y=sub_df['count'],
            mode='lines+markers',
            name=st_name,
            line=dict(color=SCREENING_COLORS.get(st_name, '#2563EB'), width=2.5, shape='spline'),
            marker=dict(size=6),
            hovertemplate=f'<b>{st_name}:</b> %{{y}} screenings<extra></extra>'
        ))

    fig.update_layout(
        title=dict(
            text="<b>Daily Screening Outcome Telemetry Trends</b>", 
            font=dict(family=CHART_FONT, size=TITLE_FONT_SIZE, color="#0F172A"),
            y=0.97, x=0.01, xanchor='left', yanchor='top'
        ),
        font=dict(family=CHART_FONT, size=AXIS_FONT_SIZE),
        hovermode="x unified",
        xaxis=dict(title="Date", showgrid=True, gridcolor="#E2E8F0"),
        yaxis=dict(title="Screenings Evaluated"),
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="center", x=0.5),
        margin=dict(t=55, b=60, l=35, r=30),
        height=380
    )
    return fig

# --- CHART 13: Horizontal Leaderboard - Donor Contribution Ranking ---
def build_chart_13_donor_leaderboard(donors_df: pd.DataFrame):
    if donors_df.empty:
        return go.Figure()

    top_donors = donors_df.sort_values(by='total_donations', ascending=False).head(10).copy()
    top_donors = top_donors.sort_values(by='total_donations', ascending=True)

    ranks = list(range(len(top_donors), 0, -1))
    badges = []
    for r in ranks:
        if r == 1: badges.append("🥇 Top 1")
        elif r == 2: badges.append("🥈 Top 2")
        elif r == 3: badges.append("🥉 Top 3")
        else: badges.append(f"🏅 Rank #{r}")

    top_donors['rank_badge'] = badges

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=top_donors['donor_id'],
        x=top_donors['total_donations'],
        orientation='h',
        text=[f"<b>{c} Dons</b> ({r})" for c, r in zip(top_donors['total_donations'], top_donors['rank_badge'])],
        textposition='outside',
        marker=dict(
            color=[COLOR_MAP.get(bg, '#2563EB') for bg in top_donors['blood_group']],
            line=dict(color='#0F172A', width=1)
        ),
        customdata=np.stack((top_donors['blood_group'], top_donors['last_donation_date'].fillna('N/A'), top_donors['city_locality']), axis=-1),
        hovertemplate='<b>Donor ID:</b> %{y}<br><b>Blood Group:</b> %{customdata[0]}<br><b>Completed Donations:</b> %{x}<br><b>Last Donation:</b> %{customdata[1]}<br><b>Locality:</b> %{customdata[2]}<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text="<b>Top 10 Donor Contribution Leaderboard</b>", 
            font=dict(family=CHART_FONT, size=TITLE_FONT_SIZE, color="#0F172A"),
            y=0.97, x=0.01, xanchor='left', yanchor='top'
        ),
        font=dict(family=CHART_FONT, size=AXIS_FONT_SIZE),
        xaxis=dict(title="Total Completed Donations"),
        yaxis=dict(title="Anonymized Donor ID"),
        margin=dict(t=50, b=40, l=35, r=100),
        height=400
    )
    return fig
