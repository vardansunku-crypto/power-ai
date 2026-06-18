import streamlit as st
import pandas as pd
import plotly.express as px

from utils.auth import check_authentication
from utils.style import load_css


st.set_page_config(
    page_title="Executive Overview | Power AI",
    page_icon="⚡",
    layout="wide"
)


check_authentication("home")

load_css()


st.markdown(
    """
    <style>
    .stApp {
        background: #0B1020 !important;
        color: #F9FAFB !important;
    }

    [data-testid="stAppViewContainer"] {
        background: #0B1020 !important;
    }

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
        color: #F9FAFB !important;
        margin-bottom: 6px;
    }

    .main-subtitle {
        font-size: 17px;
        color: #9CA3AF !important;
        margin-bottom: 30px;
    }

    .overview-card {
        background: #111827;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 14px 35px rgba(0,0,0,0.35);
        min-height: 135px;
    }

    .kpi-icon {
        font-size: 26px;
        margin-bottom: 12px;
    }

    .kpi-label {
        color: #9CA3AF;
        font-size: 15px;
        font-weight: 600;
    }

    .kpi-value {
        color: #F9FAFB;
        font-size: 34px;
        font-weight: 800;
        margin-top: 8px;
    }

    .kpi-note {
        color: #22C55E;
        font-size: 13px;
        margin-top: 6px;
        font-weight: 600;
    }

    .section-title {
        color: #F9FAFB !important;
        font-size: 24px;
        font-weight: 800;
        margin-top: 32px;
        margin-bottom: 16px;
    }

    .status-row {
        display: flex;
        justify-content: space-between;
        padding: 14px 0;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        color: #E5E7EB;
        font-size: 16px;
    }

    .status-badge {
        color: #22C55E;
        font-weight: 800;
    }

    .activity-item {
        padding: 14px 0;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        color: #E5E7EB;
        font-size: 16px;
        font-weight: 600;
    }

    .activity-muted {
        color: #9CA3AF;
        font-size: 14px;
        margin-top: 5px;
        font-weight: 400;
    }

    .recommendation-item {
        background: rgba(37,99,235,0.13);
        border-left: 4px solid #3B82F6;
        padding: 14px 16px;
        border-radius: 12px;
        margin-bottom: 14px;
        color: #E5E7EB;
        font-size: 16px;
        line-height: 1.5;
    }

    .stButton > button {
        background: #2563EB;
        color: white;
        border: none;
        border-radius: 12px;
        height: 46px;
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
    <div class="main-title">Executive Overview</div>
    <div class="main-subtitle">
        Monitor your data sources, AI analytics activity, reports, and business intelligence performance.
    </div>
    """,
    unsafe_allow_html=True
)


# KPI CARDS

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        """
        <div class="overview-card">
            <div class="kpi-icon">🗄️</div>
            <div class="kpi-label">Connected Databases</div>
            <div class="kpi-value">3</div>
            <div class="kpi-note">MySQL + MongoDB active</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="overview-card">
            <div class="kpi-icon">📁</div>
            <div class="kpi-label">Uploaded Files</div>
            <div class="kpi-value">12</div>
            <div class="kpi-note">CSV / Excel ready</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class="overview-card">
            <div class="kpi-icon">📄</div>
            <div class="kpi-label">Reports Generated</div>
            <div class="kpi-value">8</div>
            <div class="kpi-note">PDF / Excel exports</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        """
        <div class="overview-card">
            <div class="kpi-icon">🤖</div>
            <div class="kpi-label">AI Insights</div>
            <div class="kpi-value">25</div>
            <div class="kpi-note">Recommendations enabled</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ANALYTICS + SYSTEM HEALTH

left, right = st.columns([2, 1])

with left:
    st.markdown(
        '<div class="section-title">Analytics Activity</div>',
        unsafe_allow_html=True
    )

    activity_data = pd.DataFrame({
        "Module": [
            "Database Analytics",
            "File Analytics",
            "Integrated Analytics",
            "MongoDB Analytics",
            "Reports"
        ],
        "Usage": [32, 24, 18, 16, 8]
    })

    fig = px.bar(
        activity_data,
        x="Module",
        y="Usage",
        title="Module Usage Overview",
        text="Usage"
    )

    fig.update_traces(
        textposition="outside"
    )

    fig.update_layout(
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font_color="#F9FAFB",
        title_font_color="#F9FAFB",
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.08)"
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.08)"
        ),
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown(
        '<div class="section-title">System Health</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="overview-card">
            <div class="status-row">
                <span>MySQL Engine</span>
                <span class="status-badge">● Connected</span>
            </div>
            <div class="status-row">
                <span>MongoDB Engine</span>
                <span class="status-badge">● Connected</span>
            </div>
            <div class="status-row">
                <span>AI Engine</span>
                <span class="status-badge">● Active</span>
            </div>
            <div class="status-row">
                <span>File Analytics</span>
                <span class="status-badge">● Ready</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# QUICK ACTIONS

st.markdown(
    '<div class="section-title">Quick Actions</div>',
    unsafe_allow_html=True
)

q1, q2, q3, q4 = st.columns(4)

with q1:
    if st.button("🗄️ Database Analytics", use_container_width=True):
        st.switch_page("pages/2_Database_Analytics.py")

with q2:
    if st.button("🍃 MongoDB Analytics", use_container_width=True):
        st.switch_page("pages/5_MongoDB_Analytics.py")

with q3:
    if st.button("📁 File Analytics", use_container_width=True):
        st.switch_page("pages/3_File_Analytics.py")

with q4:
    if st.button("🔗 Integrated Analytics", use_container_width=True):
        st.switch_page("pages/4_Integrated_Analytics.py")


# RECENT ACTIVITY + RECOMMENDATIONS

bottom_left, bottom_right = st.columns(2)

with bottom_left:
    st.markdown(
        '<div class="section-title">Recent Activity</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="overview-card">
            <div class="activity-item">
                MongoDB analytics module connected
                <div class="activity-muted">NoSQL analytics enabled</div>
            </div>
            <div class="activity-item">
                Integrated analytics tested successfully
                <div class="activity-muted">Database + File merge completed</div>
            </div>
            <div class="activity-item">
                PDF report export completed
                <div class="activity-muted">Reports module verified</div>
            </div>
            <div class="activity-item">
                AI recommendation engine enabled
                <div class="activity-muted">Business insights available</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with bottom_right:
    st.markdown(
        '<div class="section-title">AI Recommendations</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="overview-card">
            <div class="recommendation-item">
                Focus on improving trend intelligence and growth analysis.
            </div>
            <div class="recommendation-item">
                Add API integration to support real-time business data.
            </div>
            <div class="recommendation-item">
                Upgrade reporting center with executive PDF reports.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )