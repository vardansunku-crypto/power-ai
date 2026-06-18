import streamlit as st
import pandas as pd

from utils.auth import check_authentication
from utils.style import load_css


st.set_page_config(
    page_title="Reports Center | Power AI",
    page_icon="📄",
    layout="wide"
)

check_authentication("reports_center")

load_css()


st.markdown(
    """
    <style>
    .stApp {
        background: #0B1020 !important;
        color: #F9FAFB !important;
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"] {
        background: #0B1020 !important;
    }

    .block-container {
        background: #0B1020 !important;
        padding-top: 2rem;
        max-width: 1400px;
    }

    .main-title {
        font-size: 42px;
        font-weight: 800;
        color: #F9FAFB;
        margin-bottom: 6px;
    }

    .main-subtitle {
        font-size: 17px;
        color: #9CA3AF;
        margin-bottom: 30px;
    }

    .report-card {
        background: #111827;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 14px 35px rgba(0,0,0,0.35);
        min-height: 160px;
    }

    .report-icon {
        font-size: 30px;
        margin-bottom: 12px;
    }

    .report-title {
        font-size: 20px;
        font-weight: 800;
        color: #F9FAFB;
        margin-bottom: 8px;
    }

    .report-desc {
        font-size: 14px;
        color: #9CA3AF;
        line-height: 1.5;
    }

    .section-title {
        color: #F9FAFB;
        font-size: 24px;
        font-weight: 800;
        margin-top: 32px;
        margin-bottom: 16px;
    }

    .status-ready {
        color: #22C55E;
        font-weight: 800;
        font-size: 14px;
        margin-top: 12px;
    }

    .status-pending {
        color: #F59E0B;
        font-weight: 800;
        font-size: 14px;
        margin-top: 12px;
    }

    .stButton > button {
        background: #2563EB;
        color: white;
        border: none;
        border-radius: 12px;
        height: 44px;
        font-weight: 700;
    }

    .stButton > button:hover {
        background: #1D4ED8;
        color: white;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.sidebar.markdown(
    """
    <div class="sidebar-title">
        ⚡ Power AI
    </div>

    <div class="sidebar-subtitle">
        Enterprise AI Business Intelligence
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="main-title">Reports Center</div>
    <div class="main-subtitle">
        Generate, manage, and export business intelligence reports from Power AI.
    </div>
    """,
    unsafe_allow_html=True
)


# REPORT CARDS

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        """
        <div class="report-card">
            <div class="report-icon">📄</div>
            <div class="report-title">PDF Reports</div>
            <div class="report-desc">
                Generate executive-ready PDF reports with KPIs, charts, AI summaries, and recommendations.
            </div>
            <div class="status-ready">● Available</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        """
        <div class="report-card">
            <div class="report-icon">📊</div>
            <div class="report-title">Excel Exports</div>
            <div class="report-desc">
                Export analytics results, cleaned data, and business tables into Excel format.
            </div>
            <div class="status-ready">● Available</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        """
        <div class="report-card">
            <div class="report-icon">📁</div>
            <div class="report-title">CSV Downloads</div>
            <div class="report-desc">
                Download query results, file analytics output, and integrated datasets as CSV files.
            </div>
            <div class="status-ready">● Available</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c4:
    st.markdown(
        """
        <div class="report-card">
            <div class="report-icon">⏱️</div>
            <div class="report-title">Scheduled Reports</div>
            <div class="report-desc">
                Future module for automated weekly and monthly report generation.
            </div>
            <div class="status-pending">● Planned</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# QUICK REPORT ACTIONS

st.markdown('<div class="section-title">Quick Report Actions</div>', unsafe_allow_html=True)

q1, q2, q3, q4 = st.columns(4)

with q1:
    if st.button("Open Database Reports", use_container_width=True):
        st.switch_page("pages/2_Database_Analytics.py")

with q2:
    if st.button("Open File Reports", use_container_width=True):
        st.switch_page("pages/3_File_Analytics.py")

with q3:
    if st.button("Open Integrated Reports", use_container_width=True):
        st.switch_page("pages/4_Integrated_Analytics.py")

with q4:
    if st.button("Open MongoDB Reports", use_container_width=True):
        st.switch_page("pages/5_MongoDB_Analytics.py")


# REPORT HISTORY TABLE

st.markdown('<div class="section-title">Report History</div>', unsafe_allow_html=True)

report_history = pd.DataFrame({
    "Report Name": [
        "Database Analytics Report",
        "File Analytics Summary",
        "Integrated Analytics Report",
        "MongoDB Collection Summary",
        "Executive Overview Report"
    ],
    "Module": [
        "Database Analytics",
        "File Analytics",
        "Integrated Analytics",
        "MongoDB Analytics",
        "Executive Overview"
    ],
    "Format": [
        "PDF",
        "Excel / CSV",
        "PDF",
        "AI Summary",
        "PDF"
    ],
    "Status": [
        "Generated",
        "Generated",
        "Generated",
        "Available",
        "Planned"
    ]
})

st.dataframe(
    report_history,
    use_container_width=True,
    hide_index=True
)


# REPORT FLOW

st.markdown('<div class="section-title">Power AI Reporting Flow</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="report-card">
        <div style="font-size:18px; color:#E5E7EB; line-height:1.9;">
            Data Sources
            <br>
            ↓
            <br>
            Analytics Engine + AI Insights
            <br>
            ↓
            <br>
            <b style="color:#00F5D4;">PDF • Excel • CSV • Executive Summaries</b>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
