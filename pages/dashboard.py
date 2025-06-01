import streamlit as st
import pandas as pd
from datetime import datetime

# ─────────────────────────────────────────────────────
# Inject custom CSS for metric styling
# ─────────────────────────────────────────────────────
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:ital,wght@0,100..700;1,100..700&family=Tajawal:wght@200;300;400;500;700;800;900&display=swap');

    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        height: 100%;
        width: 100%;
        background-image: url("https://www.wieland.com/var/media/cache/image_header_512/var/dam/celum/15252.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        filter: blur(17px);
    }

    .metric-card {
        padding: 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        text-align: center;
        font-family: 'Roboto Mono', sans-serif;
        background: rgba(255, 255, 255, 0.54);
        border-radius: 16px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(6px);
        border: 1px solid rgba(255, 255, 255, 0.44);
    }
    .metric-title {
        font-size: 14px;
        font-weight: bold;
    }
    .metric-value {
        font-size: 20px;
        font-weight: 600;
    }
    .card-small {
        width: 100%;
        height: 120px;
    }

    .card-large {
        width: 100%;
        height: 120px;
    }

    .card-xlarge {
        width: 100%;
        height: auto;
        font-size: 1.2rem;
    }

    .text-green { color: #4CAF50 !important; }
    .text-red { color: #FF6B6B !important; }
    .text-orange { color: #FFA500 !important; }
    .text-gray { color: #333 !important; }

    h2 {
    color: white !important;
    }

    h6 {
    color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
# Page title
# ─────────────────────────────────────────────────────
st.title("\U0001F4CA Dashboard")

# ─────────────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────────────
company_file = "data/report_details.xlsx"
company_data = pd.read_excel(company_file)

# ─────────────────────────────────────────────────────
# GENERAL MEASURES
# ─────────────────────────────────────────────────────
st.markdown("<h2>Intelligence Overview</h2>", unsafe_allow_html=True)

company_data = company_data.dropna(subset=["company_name"])
total_reports = len(company_data)

# Upcoming visits
visit_dates = []
for d in company_data.get("report_date", []):
    try:
        dt = pd.to_datetime(d)
        if dt > datetime.now():
            visit_dates.append(dt)
    except:
        pass
upcoming = sorted(set(visit_dates))[:3]
upcoming_str = ", ".join(d.strftime("%d %b %Y") for d in upcoming) if upcoming else "27.06.2025"

# Next action
tasks = company_data.get("next_action_item", pd.Series()).dropna()
next_action = tasks.iloc[-1] if len(tasks) else "Review compliance guidelines"

# Red flags
urgent_flags = company_data.get("urgent_signals", pd.Series(dtype=str)).dropna()
red_flags = sum(1 for val in urgent_flags if val.lower() not in ["none detected", "no alerts"])

# First row: 3 evenly spaced cards
c1, c2, c3 = st.columns([1, 2, 1])
with c1:
    st.markdown(f"""
        <div class='metric-card card-small'>
            <div class='metric-title'>Total Visits</div>
            <div class='metric-value'>{total_reports}</div>
        </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
        <div class='metric-card card-large'>
            <div class='metric-title'>Next Visits</div>
            <div class='metric-value'>{upcoming_str}</div>
        </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
        <div class='metric-card card-small'>
            <div class='metric-title'>Red Flags</div>
            <div class='metric-value'>{red_flags}</div>
        </div>
    """, unsafe_allow_html=True)

# Spacer to separate rows
st.markdown("<br>", unsafe_allow_html=True)

# Second row: full-width single card
c_full = st.columns(1)[0]
with c_full:
    st.markdown(f"""
        <div class='metric-card card-xlarge'>
            <div class='metric-title'>Next Action Item</div>
            <div class='metric-value'>{next_action}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────────────
# SPECIFIC MEASURES (Customer Intelligence)
# ─────────────────────────────────────────────────────
st.markdown("<h2>Customer Intelligence </h2>", unsafe_allow_html=True)
st.markdown("<h6>Select a company:</h6>", unsafe_allow_html=True)

company = st.selectbox("", sorted(company_data["company_name"].unique()))
row = company_data[company_data["company_name"] == company].iloc[0]

metrics = {
    "Urgent Signals": row.get("urgent_signals", "N/A"),
    "Customer Satisfaction": row.get("customer_satisfaction", "N/A"),
    "Opportunity Index": row.get("opportunity_index", "N/A"),
    "Risk Score": row.get("risk_score", "N/A"),
    "Forecast Accuracy": row.get("forecast_accuracy", "N/A")
}

def get_color_class(metric_type, value):
    if metric_type == "customer":
        v = value.lower()
        if "very satisfied" in v or "satisfied" in v:
            return "text-green"
        elif "not" in v or "bad" in v:
            return "text-red"
        elif "no feedback" in v:
            return "text-orange"
    elif metric_type == "risk":
        v = value.lower()
        if "low" in v:
            return "text-green"
        elif "moderate" in v:
            return "text-orange"
        elif "high" in v:
            return "text-red"
    return "text-gray"

# First row: 4 metrics
d1, d2, d3, d4 = st.columns(4)
with d1:
    st.markdown(f"""
        <div class='metric-card card-medium'>
            <div class='metric-title'>Urgent Signals</div>
            <div class='metric-value'>{metrics['Urgent Signals']}</div>
        </div>
    """, unsafe_allow_html=True)

cs_value = metrics["Customer Satisfaction"]
cs_color = get_color_class("customer", cs_value)
with d2:
    st.markdown(f"""
        <div class='metric-card card-small'>
            <div class='metric-title'>Customer Satisfaction</div>
            <div class='metric-value {cs_color}'>{cs_value}</div>
        </div>
    """, unsafe_allow_html=True)

rs_value = metrics["Risk Score"]
rs_color = get_color_class("risk", rs_value)
with d3:
    st.markdown(f"""
        <div class='metric-card card-large'>
            <div class='metric-title'>Risk Score</div>
            <div class='metric-value {rs_color}'>{rs_value}</div>
        </div>
    """, unsafe_allow_html=True)

with d4:
    st.markdown(f"""
        <div class='metric-card card-small'>
            <div class='metric-title'>Forecast Accuracy</div>
            <div class='metric-value'>{metrics['Forecast Accuracy']}</div>
        </div>
    """, unsafe_allow_html=True)

# Second row: Opportunity Index on its own line
st.markdown("<br>", unsafe_allow_html=True)
d_full = st.columns(1)[0]

# Bullet-point Opportunity Index
op_text = metrics["Opportunity Index"]
bullet_lines = "".join(f"<li>{line.strip()}</li>" for line in op_text.split(",") if line.strip())

with d_full:
    st.markdown(f"""
        <div class='metric-card card-xlarge'>
            <div class='metric-title'>Opportunity Index</div>
            <ul style='text-align:left; padding-left: 1.5rem;'>{bullet_lines}</ul>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")