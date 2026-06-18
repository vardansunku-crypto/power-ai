import streamlit as st
import pandas as pd

from utils.auth import check_authentication
from utils.style import load_css


st.set_page_config(
    page_title="Admin & Settings | Power AI",
    page_icon="⚙️",
    layout="wide"
)

check_authentication("admin_settings")
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

    .admin-card {
        background: #111827;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 14px 35px rgba(0,0,0,0.35);
        min-height: 150px;
    }

    .card-title {
        font-size: 20px;
        font-weight: 800;
        color: #F9FAFB;
        margin-bottom: 8px;
    }

    .card-desc {
        color: #9CA3AF;
        font-size: 14px;
        line-height: 1.6;
    }

    .status-ok {
        color: #22C55E;
        font-weight: 800;
        margin-top: 12px;
    }

    .status-warning {
        color: #F59E0B;
        font-weight: 800;
        margin-top: 12px;
    }

    .section-title {
        color: #F9FAFB;
        font-size: 24px;
        font-weight: 800;
        margin-top: 32px;
        margin-bottom: 16px;
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
    <div class="main-title">Admin & Settings</div>
    <div class="main-subtitle">
        Manage system status, access control, configuration, and platform monitoring.
    </div>
    """,
    unsafe_allow_html=True
)


c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        """
        <div class="admin-card">
            <div class="card-title">🔐 Authentication</div>
            <div class="card-desc">Login system is enabled for secure access.</div>
            <div class="status-ok">● Active</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        """
        <div class="admin-card">
            <div class="card-title">🤖 AI Engine</div>
            <div class="card-desc">Groq-powered AI analytics engine is connected.</div>
            <div class="status-ok">● Running</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        """
        <div class="admin-card">
            <div class="card-title">🗄️ Data Sources</div>
            <div class="card-desc">MySQL, MongoDB, CSV, and Excel modules are available.</div>
            <div class="status-ok">● Available</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c4:
    st.markdown(
        """
        <div class="admin-card">
            <div class="card-title">🔌 APIs</div>
            <div class="card-desc">External API integration module is planned.</div>
            <div class="status-warning">● Pending</div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown('<div class="section-title">User Access</div>', unsafe_allow_html=True)

users_table = pd.DataFrame({
    "User": ["Admin", "Analyst", "Viewer"],
    "Role": ["Full Access", "Analytics Access", "Read Only"],
    "Status": ["Active", "Planned", "Planned"]
})

st.dataframe(users_table, use_container_width=True, hide_index=True)


st.markdown('<div class="section-title">Audit Logs</div>', unsafe_allow_html=True)

audit_logs = pd.DataFrame({
    "Activity": [
        "User logged in",
        "Database analytics opened",
        "MongoDB module connected",
        "PDF report generated",
        "AI Copilot accessed"
    ],
    "Module": [
        "Authentication",
        "Database Analytics",
        "MongoDB Analytics",
        "Reports Center",
        "AI Copilot"
    ],
    "Status": [
        "Success",
        "Success",
        "Success",
        "Success",
        "Success"
    ]
})

st.dataframe(audit_logs, use_container_width=True, hide_index=True)


st.markdown('<div class="section-title">Platform Information</div>', unsafe_allow_html=True)

platform_info = pd.DataFrame({
    "Item": [
        "Project Name",
        "Version",
        "Frontend",
        "AI Model",
        "Database Support",
        "Report Support"
    ],
    "Value": [
        "Power AI",
        "Enterprise v2.0",
        "Streamlit",
        "Groq Llama 3.3",
        "MySQL, MongoDB, CSV, Excel",
        "PDF, Excel, CSV"
    ]
})

st.dataframe(platform_info, use_container_width=True, hide_index=True)