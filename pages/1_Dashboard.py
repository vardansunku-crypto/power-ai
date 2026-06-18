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

check_authentication("dashboard")
load_css()


# -------------------------------------------------
# ENTERPRISE UI STYLE
# -------------------------------------------------

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
        max-width: 1400px;
        padding-top: 2rem;
    }

    .page-title {
        font-size: 42px;
        font-weight: 800;
        color: #F9FAFB;
        margin-bottom: 6px;
    }

    .page-subtitle {
        font-size: 17px;
        color: #9CA3AF;
        margin-bottom: 30px;
    }

    .metric-card {
        background: #111827;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 14px 35px rgba(0,0,0,0.35);
        min-height: 135px;
    }

    .metric-label {
        color: #9CA3AF;
        font-size: 15px;
        font-weight: 600;
    }

    .metric-value {
        color: #F9FAFB;
        font-size: 34px;
        font-weight: 800;
        margin-top: 10px;
    }

    .metric-note {
        color: #22C55E;
        font-size: 13px;
        margin-top: 8px;
        font-weight: 600;
    }

    .section-title {
        color: #F9FAFB;
        font-size: 24px;
        font-weight: 800;
        margin-top: 32px;
        margin-bottom: 16px;
    }

    .panel-card {
        background: #111827;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 14px 35px rgba(0,0,0,0.35);
    }

    .status-row {
        display: flex;
        justify-content: space-between;
        padding: 14px 0;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        color: #E5E7EB;
        font-size: 15px;
    }

    .status-ok {
        color: #22C55E;
        font-weight: 800;
    }

    .status-warning {
        color: #F59E0B;
        font-weight: 800;
    }

    .activity-item {
        padding: 14px 0;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        color: #E5E7EB;
        font-size: 15px;
        font-weight: 600;
    }

    .activity-muted {
        color: #9CA3AF;
        font-size: 13px;
        margin-top: 5px;
        font-weight: 400;
    }

    .summary-box {
        background: rgba(37,99,235,0.14);
        border-left: 4px solid #3B82F6;
        border-radius: 12px;
        padding: 16px;
        color: #E5E7EB;
        line-height: 1.6;
        font-size: 15px;
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


# -------------------------------------------------
# SIDEBAR BRAND
# -------------------------------------------------

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


# -------------------------------------------------
# READ REAL SESSION DATA
# -------------------------------------------------

db_connected = st.session_state.get("mysql_connected", False)
selected_db = st.session_state.get("selected_db", "Not Connected")

db_rows = 0
if st.session_state.get("db_result_df") is not None:
    db_rows = len(st.session_state.db_result_df)

file_rows = 0
file_count = 0
if st.session_state.get("file_uploaded_df") is not None:
    file_df = st.session_state.file_uploaded_df
    file_rows = len(file_df)

    if "source_file" in file_df.columns:
        file_count = file_df["source_file"].nunique()
    else:
        file_count = 1

integrated_rows = 0
if st.session_state.get("integrated_df") is not None:
    integrated_rows = len(st.session_state.integrated_df)

mongo_rows = 0
if st.session_state.get("mongo_df") is not None:
    mongo_rows = len(st.session_state.mongo_df)

latest_summary = ""
if st.session_state.get("db_ai_summary"):
    latest_summary = st.session_state.db_ai_summary
elif st.session_state.get("file_ai_summary"):
    latest_summary = st.session_state.file_ai_summary
elif st.session_state.get("integrated_ai_summary"):
    latest_summary = st.session_state.integrated_ai_summary


health_score = 0

if db_connected:
    health_score += 25

if db_rows > 0:
    health_score += 20

if file_rows > 0:
    health_score += 20

if integrated_rows > 0:
    health_score += 20

if latest_summary:
    health_score += 15


# -------------------------------------------------
# PAGE HEADER
# -------------------------------------------------

st.markdown(
    """
    <div class="page-title">Executive Overview</div>
    <div class="page-subtitle">
        Real-time overview of Power AI analytics activity, connected data, insights, and system readiness.
    </div>
    """,
    unsafe_allow_html=True
)


# -------------------------------------------------
# KPI CARDS
# -------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    status_text = "Connected" if db_connected else "Not Connected"

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Database Status</div>
            <div class="metric-value">{status_text}</div>
            <div class="metric-note">{selected_db}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Database Rows</div>
            <div class="metric-value">{db_rows}</div>
            <div class="metric-note">Latest query result</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Uploaded File Rows</div>
            <div class="metric-value">{file_rows}</div>
            <div class="metric-note">{file_count} file(s) loaded</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Integrated Rows</div>
            <div class="metric-value">{integrated_rows}</div>
            <div class="metric-note">Database + file merge</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# -------------------------------------------------
# HEALTH + SYSTEM STATUS
# -------------------------------------------------

left, right = st.columns([2, 1])

with left:
    st.markdown('<div class="section-title">Power AI Health</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)

    if health_score >= 90:
        st.success("Power AI Status: Excellent")
    elif health_score >= 70:
        st.info("Power AI Status: Good")
    elif health_score >= 40:
        st.warning("Power AI Status: Partial Setup")
    else:
        st.error("Power AI Status: Setup Required")

    st.progress(health_score / 100)

    health_data = pd.DataFrame({
        "Module": [
            "Database",
            "Query Results",
            "File Analytics",
            "Integrated Analytics",
            "AI Summary"
        ],
        "Score": [
            25 if db_connected else 0,
            20 if db_rows > 0 else 0,
            20 if file_rows > 0 else 0,
            20 if integrated_rows > 0 else 0,
            15 if latest_summary else 0
        ]
    })

    fig = px.bar(
        health_data,
        x="Module",
        y="Score",
        title="Module Readiness Score",
        text="Score"
    )

    fig.update_layout(
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font_color="#F9FAFB",
        title_font_color="#F9FAFB",
        margin=dict(l=20, r=20, t=45, b=20),
        yaxis=dict(range=[0, 30], gridcolor="rgba(255,255,255,0.08)"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.08)")
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-title">System Status</div>', unsafe_allow_html=True)

    mysql_status = "● Connected" if db_connected else "● Not Connected"
    mysql_class = "status-ok" if db_connected else "status-warning"

    file_status = "● Ready" if file_rows > 0 else "● No Files"
    file_class = "status-ok" if file_rows > 0 else "status-warning"

    integrated_status = "● Available" if integrated_rows > 0 else "● Pending"
    integrated_class = "status-ok" if integrated_rows > 0 else "status-warning"

    ai_status = "● Active" if latest_summary else "● Waiting"
    ai_class = "status-ok" if latest_summary else "status-warning"

    st.markdown(
        f"""
        <div class="panel-card">
            <div class="status-row">
                <span>MySQL Analytics</span>
                <span class="{mysql_class}">{mysql_status}</span>
            </div>
            <div class="status-row">
                <span>File Analytics</span>
                <span class="{file_class}">{file_status}</span>
            </div>
            <div class="status-row">
                <span>Integrated Analytics</span>
                <span class="{integrated_class}">{integrated_status}</span>
            </div>
            <div class="status-row">
                <span>AI Insight Engine</span>
                <span class="{ai_class}">{ai_status}</span>
            </div>
            <div class="status-row">
                <span>MongoDB Rows</span>
                <span class="status-ok">{mongo_rows}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# -------------------------------------------------
# QUICK ACTIONS
# -------------------------------------------------

st.markdown('<div class="section-title">Quick Actions</div>', unsafe_allow_html=True)

q1, q2, q3, q4 = st.columns(4)

with q1:
    if st.button("📊 Database Analytics", use_container_width=True):
        st.switch_page("pages/2_Database_Analytics.py")

with q2:
    if st.button("📁 File Analytics", use_container_width=True):
        st.switch_page("pages/3_File_Analytics.py")

with q3:
    if st.button("🔗 Integrated Analytics", use_container_width=True):
        st.switch_page("pages/4_Integrated_Analytics.py")

with q4:
    if st.button("🍃 MongoDB Analytics", use_container_width=True):
        st.switch_page("pages/5_MongoDB_Analytics.py")


# -------------------------------------------------
# RECENT ACTIVITY + AI SUMMARY
# -------------------------------------------------

bottom_left, bottom_right = st.columns(2)

with bottom_left:
    st.markdown('<div class="section-title">Recent Activity</div>', unsafe_allow_html=True)

    recent_query = st.session_state.get("db_user_query", "")

    activity_html = ""

    if db_connected:
        activity_html += """
        <div class="activity-item">
            Database connected
            <div class="activity-muted">MySQL analytics is available</div>
        </div>
        """

    if recent_query:
        activity_html += f"""
        <div class="activity-item">
            Recent business question
            <div class="activity-muted">{recent_query}</div>
        </div>
        """

    if file_rows > 0:
        activity_html += f"""
        <div class="activity-item">
            File analytics loaded
            <div class="activity-muted">{file_rows} rows available</div>
        </div>
        """

    if integrated_rows > 0:
        activity_html += f"""
        <div class="activity-item">
            Integrated analytics completed
            <div class="activity-muted">{integrated_rows} merged rows</div>
        </div>
        """

    if not activity_html:
        activity_html = """
        <div class="activity-item">
            No activity yet
            <div class="activity-muted">Start with Database Analytics or File Analytics</div>
        </div>
        """

    st.markdown(
        f"""
        <div class="panel-card">
            {activity_html}
        </div>
        """,
        unsafe_allow_html=True
    )

with bottom_right:
    st.markdown('<div class="section-title">Latest AI Summary</div>', unsafe_allow_html=True)

    if latest_summary:
        st.markdown(
            f"""
            <div class="panel-card">
                <div class="summary-box">
                    {latest_summary}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div class="panel-card">
                <div class="summary-box">
                    No AI summary generated yet. Run Database, File, or Integrated Analytics to generate insights.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )