import streamlit as st


def load_css():
    st.markdown(
        """
        <style>
        .sidebar-title {
            font-size: 26px;
            font-weight: 900;
            color: #F9FAFB;
            margin-bottom: 4px;
        }

        .sidebar-subtitle {
            font-size: 13px;
            color: #9CA3AF;
            margin-bottom: 18px;
        }

        [data-testid="stSidebar"] {
            background: #111827 !important;
        }

        [data-testid="stSidebar"] * {
            color: #E5E7EB;
        }
        </style>
        """,
        unsafe_allow_html=True
    )