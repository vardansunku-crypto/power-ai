import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from groq import Groq

from utils.auth import check_authentication
from utils.style import load_css
from utils.cleaner import clean_dataframe_columns
from utils.exporter import show_download_buttons
from utils.charts import show_kpi_and_charts
from ai.ai_engine import (
    ask_groq,
    generate_ai_summary,
    generate_recommendation_summary
)
from utils.mongo_connector import (
    connect_mongodb,
    get_mongo_databases,
    get_mongo_collections,
    load_collection_as_dataframe
)


st.set_page_config(
    page_title="MongoDB Analytics | Power AI",
    page_icon="🍃",
    layout="wide"
)

check_authentication("mongo")
load_css()
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)


st.markdown(
    """
    <style>
    .stApp {
        background: #0B1020 !important;
        color: #F9FAFB !important;
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    .block-container {
        background: #0B1020 !important;
    }

    .block-container {
        max-width: 1200px;
        margin: auto;
        padding-top: 9rem !important;
        padding-bottom: 3rem;
    }

    .page-header {
        background: #111827;
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 22px;
        box-shadow: 0 14px 35px rgba(0,0,0,0.35);
    }

    .page-header h1 {
        color: #F9FAFB !important;
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .page-header p {
        color: #9CA3AF !important;
        font-size: 16px;
        margin-bottom: 0;
    }

    .st-key-mongo_toolbar {
        position: fixed;
        top: 3.4rem;
        left: 50%;
        transform: translateX(-50%);
        width: 94%;
        max-width: 1300px;
        z-index: 999999;
        background: rgba(17,24,39,0.98);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 12px;
        padding: 8px 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.45);
        backdrop-filter: blur(10px);
    }

    .ribbon-title {
        color: #F9FAFB;
        font-size: 15px;
        font-weight: 900;
        margin-bottom: 6px;
        white-space: nowrap;
    }

    .ribbon-title span {
        color: #22C55E;
        margin-left: 10px;
        font-weight: 800;
    }

    .ribbon-group-title {
        color: #9CA3AF;
        font-size: 10px;
        font-weight: 900;
        text-align: center;
        margin-bottom: 2px;
        letter-spacing: 0.7px;
    }

    .section-title {
        color: #F9FAFB !important;
        font-size: 23px;
        font-weight: 800;
        margin-top: 26px;
        margin-bottom: 14px;
    }

    .summary-card {
        background: rgba(0,245,212,0.08);
        border-left: 4px solid #00F5D4;
        border-radius: 12px;
        padding: 18px;
        color: #E5E7EB !important;
        line-height: 1.7;
        font-size: 16px;
        white-space: pre-wrap;
    }

    .recommendation-card {
        background: rgba(59,130,246,0.12);
        border-left: 4px solid #3B82F6;
        border-radius: 12px;
        padding: 18px;
        color: #E5E7EB !important;
        line-height: 1.7;
        font-size: 16px;
        white-space: pre-wrap;
    }

    .hint-box {
        background: rgba(37,99,235,0.12);
        border: 1px solid rgba(59,130,246,0.25);
        border-radius: 14px;
        padding: 16px;
        color: #D1D5DB !important;
        line-height: 1.7;
        margin-bottom: 18px;
    }

    .stTextInput label,
    .stSelectbox label,
    .stNumberInput label {
        color: #E5E7EB !important;
        font-weight: 600 !important;
    }

    .stTextInput input {
        background-color: #111827 !important;
        color: #F9FAFB !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        border-radius: 12px !important;
    }

    [data-testid="stDataFrame"] {
        background: #111827 !important;
        border-radius: 14px !important;
    }

    [data-testid="stAlert"] {
        border-radius: 12px !important;
    }

    .stButton > button {
        background: #2563EB !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        min-height: 30px !important;
        height: 31px !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        padding: 2px 6px !important;
        white-space: normal !important;
    }

    .stButton > button:hover {
        background: #1D4ED8 !important;
        color: white !important;
        border: none !important;
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


# -------------------------------------------------
# SESSION DEFAULTS
# -------------------------------------------------

defaults = {
    "mongo_client": None,
    "mongo_df": pd.DataFrame(),
    "mongo_uri": "mongodb://localhost:27017/",
    "mongo_selected_db": None,
    "mongo_selected_collection": None,
    "mongo_ai_summary": "",
    "mongo_recommendation_text": "",
    "mongo_ai_answer": "",
    "mongo_user_query": "",
    "show_mongo_charts": False,
    "mongo_active_tab": "Data",
    "mongo_connected": False
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -------------------------------------------------
# STATUS VALUES
# -------------------------------------------------

df = st.session_state.mongo_df
mongo_rows = len(df) if not df.empty else 0
mongo_cols = len(df.columns) if not df.empty else 0
mongo_status = "CONNECTED" if st.session_state.mongo_connected else "NOT CONNECTED"


# -------------------------------------------------
# FIXED CONSISTENT RIBBON
# -------------------------------------------------

with st.container(key="mongo_toolbar"):

    st.markdown(
        f"""
        <div class="ribbon-title">
            🍃 MONGODB ANALYTICS
            <span>{mongo_status}</span>
            &nbsp; | &nbsp; ROWS: {mongo_rows}
            &nbsp; | &nbsp; COLUMNS: {mongo_cols}
        </div>
        """,
        unsafe_allow_html=True
    )

    g1, g2, g3 = st.columns([3, 3, 2])

    with g1:
        st.markdown('<div class="ribbon-group-title">DATA</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)

        with c1:
            connect_clicked = st.button(
                "Connect",
                use_container_width=True,
                key="mongo_connect_btn"
            )

        with c2:
            load_clicked = st.button(
                "Load",
                use_container_width=True,
                key="mongo_load_btn"
            )

        with c3:
            clear_clicked = st.button(
                "Clear",
                use_container_width=True,
                key="mongo_clear_btn"
            )

    with g2:
        st.markdown('<div class="ribbon-group-title">AI ENGINE</div>', unsafe_allow_html=True)

        c4, c5, c6 = st.columns(3)

        with c4:
            ask_clicked = st.button(
                "Ask AI",
                use_container_width=True,
                key="mongo_ask_btn"
            )

        with c5:
            summary_clicked = st.button(
                "Summary",
                use_container_width=True,
                key="mongo_summary_btn"
            )

        with c6:
            reset_clicked = st.button(
                "Reset",
                use_container_width=True,
                key="mongo_reset_btn"
            )

    with g3:
        st.markdown('<div class="ribbon-group-title">ANALYTICS</div>', unsafe_allow_html=True)

        c7, c8 = st.columns(2)

        with c7:
            charts_clicked = st.button(
                "Charts",
                use_container_width=True,
                key="mongo_charts_btn"
            )

        with c8:
            recommendation_clicked = st.button(
                "Insights",
                use_container_width=True,
                key="mongo_insights_btn"
            )


# -------------------------------------------------
# HEADER
# -------------------------------------------------

st.markdown(
    """
    <div class="page-header">
        <h1>🍃 MongoDB Analytics</h1>
        <p>Connect MongoDB collections, preview documents, analyze KPIs, generate AI summaries, charts, insights, and exports.</p>
    </div>
    """,
    unsafe_allow_html=True
)


# -------------------------------------------------
# CONNECTION SECTION
# -------------------------------------------------

st.markdown('<div class="section-title">🔌 MongoDB Connection</div>', unsafe_allow_html=True)

mongo_uri = st.text_input(
    "MongoDB URI",
    value=st.session_state.mongo_uri,
    key="mongo_uri_input"
)

st.session_state.mongo_uri = mongo_uri


# -------------------------------------------------
# BASIC BUTTON ACTIONS
# -------------------------------------------------

if connect_clicked:
    try:
        mongo_client = connect_mongodb(mongo_uri)
        st.session_state.mongo_client = mongo_client
        st.session_state.mongo_connected = True
        st.success("MongoDB connected successfully.")
        st.rerun()
    except Exception as e:
        st.session_state.mongo_connected = False
        st.error(f"MongoDB Connection Error: {e}")


if clear_clicked:
    st.session_state.mongo_client = None
    st.session_state.mongo_df = pd.DataFrame()
    st.session_state.mongo_selected_db = None
    st.session_state.mongo_selected_collection = None
    st.session_state.mongo_ai_summary = ""
    st.session_state.mongo_recommendation_text = ""
    st.session_state.mongo_ai_answer = ""
    st.session_state.show_mongo_charts = False
    st.session_state.mongo_active_tab = "Data"
    st.session_state.mongo_connected = False
    st.success("MongoDB data cleared.")
    st.rerun()


if reset_clicked:
    st.session_state.mongo_ai_summary = ""
    st.session_state.mongo_recommendation_text = ""
    st.session_state.mongo_ai_answer = ""
    st.session_state.show_mongo_charts = False
    st.session_state.mongo_active_tab = "Data"
    st.success("MongoDB analytics reset.")
    st.rerun()


# -------------------------------------------------
# DATABASE AND COLLECTION SELECTION
# -------------------------------------------------

if st.session_state.mongo_client:

    mongo_client = st.session_state.mongo_client

    st.markdown('<div class="section-title">📂 Select Database and Collection</div>', unsafe_allow_html=True)

    databases = get_mongo_databases(mongo_client)
    databases = [db for db in databases if db not in ["admin", "local", "config"]]

    if databases:

        db_index = 0
        if st.session_state.mongo_selected_db in databases:
            db_index = databases.index(st.session_state.mongo_selected_db)

        selected_db = st.selectbox(
            "Select Database",
            databases,
            index=db_index,
            key="mongo_database_select"
        )

        st.session_state.mongo_selected_db = selected_db

        collections = get_mongo_collections(mongo_client, selected_db)

        if collections:

            collection_index = 0
            if st.session_state.mongo_selected_collection in collections:
                collection_index = collections.index(st.session_state.mongo_selected_collection)

            selected_collection = st.selectbox(
                "Select Collection",
                collections,
                index=collection_index,
                key="mongo_collection_select"
            )

            st.session_state.mongo_selected_collection = selected_collection

            limit = st.number_input(
                "Rows Limit",
                min_value=10,
                max_value=10000,
                value=1000,
                step=100,
                key="mongo_rows_limit"
            )

            if load_clicked:
                try:
                    loaded_df = load_collection_as_dataframe(
                        mongo_client,
                        selected_db,
                        selected_collection,
                        limit
                    )

                    if loaded_df is None or loaded_df.empty:
                        st.session_state.mongo_df = pd.DataFrame()
                        st.warning("No data found in this collection.")
                    else:
                        loaded_df = clean_dataframe_columns(loaded_df)
                        st.session_state.mongo_df = loaded_df
                        st.session_state.mongo_ai_summary = ""
                        st.session_state.mongo_recommendation_text = ""
                        st.session_state.mongo_ai_answer = ""
                        st.session_state.show_mongo_charts = False
                        st.session_state.mongo_active_tab = "Data"
                        st.success("Collection loaded successfully.")
                        st.rerun()

                except Exception as e:
                    st.error(f"Load Collection Error: {e}")

        else:
            st.warning("No collections found in this database.")

    else:
        st.warning("No user databases found.")

else:
    st.info("Enter MongoDB URI and click Connect to start analytics.")


# -------------------------------------------------
# DATA PREVIEW AND QUESTION
# -------------------------------------------------

df = st.session_state.mongo_df

if not df.empty:

    st.markdown('<div class="section-title">📊 MongoDB Collection Preview</div>', unsafe_allow_html=True)

    p1, p2, p3 = st.columns(3)

    with p1:
        st.metric("Total Records", len(df))

    with p2:
        st.metric("Total Columns", len(df.columns))

    with p3:
        st.metric("Duplicate Rows", int(df.duplicated().sum()))

    st.dataframe(df.head(1000), use_container_width=True)
    st.info(f"Previewing first 1000 rows out of {len(df)} MongoDB records.")

    st.markdown('<div class="section-title">🧠 Ask Question About MongoDB Data</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="hint-box">
            <b>Example questions:</b><br>
            • Which city has highest sales?<br>
            • Which product category performs best?<br>
            • What are the important business patterns?<br>
            • Which fields have missing values?<br>
            • What improvements can be made?
        </div>
        """,
        unsafe_allow_html=True
    )

    mongo_question = st.text_input(
        "Ask a question about this MongoDB collection",
        value=st.session_state.mongo_user_query,
        key="mongo_user_query_input"
    )

    st.session_state.mongo_user_query = mongo_question


# -------------------------------------------------
# AI ASK ACTION
# -------------------------------------------------

if ask_clicked:

    if df.empty:
        st.error("Please load MongoDB collection data first.")

    elif st.session_state.mongo_user_query.strip() == "":
        st.warning("Please enter a question.")

    else:
        try:
            sample_data = df.head(50).to_string()

            prompt = f"""
You are Power AI, a business intelligence assistant.

Analyze the MongoDB collection data and answer the user's question.

User Question:
{st.session_state.mongo_user_query}

Data Sample:
{sample_data}

Rules:
- Give clear business answer.
- Mention important numbers if available.
- Do not generate SQL.
- Do not assume columns that are not present.
- Keep answer simple and useful.
"""

            st.session_state.mongo_ai_answer = ask_groq(prompt)
            st.session_state.mongo_active_tab = "Ask AI"
            st.success("Mongo AI answer generated.")

        except Exception as e:
            st.error(f"AI Error: {e}")


# -------------------------------------------------
# SUMMARY ACTION
# -------------------------------------------------

if summary_clicked:

    if df.empty:
        st.error("Please load MongoDB collection data first.")

    else:
        summary_df = df.head(100)

        st.session_state.mongo_ai_summary = generate_ai_summary(
            client,
            "AI MongoDB Business Summary",
            st.session_state.mongo_user_query,
            summary_df,
            st
        )

        st.session_state.mongo_active_tab = "Summary"
        st.success("MongoDB AI summary generated.")


# -------------------------------------------------
# CHARTS ACTION
# -------------------------------------------------

if charts_clicked:

    if df.empty:
        st.error("Please load MongoDB collection data first.")

    else:
        st.session_state.show_mongo_charts = True
        st.session_state.mongo_active_tab = "Charts"
        st.success("MongoDB charts generated.")


# -------------------------------------------------
# RECOMMENDATION ACTION
# -------------------------------------------------

if recommendation_clicked:

    if df.empty:
        st.error("Please load MongoDB collection data first.")

    else:
        recommendation_df = df.head(100)

        st.session_state.mongo_recommendation_text = generate_recommendation_summary(
            client,
            st.session_state.mongo_user_query,
            recommendation_df
        )

        st.session_state.mongo_active_tab = "Insights"
        st.success("MongoDB insights generated.")


# -------------------------------------------------
# CUSTOM STABLE WORKSPACE TABS
# -------------------------------------------------

st.markdown('<div class="section-title">📌 MongoDB Workspace</div>', unsafe_allow_html=True)

w1, w2, w3, w4, w5, w6 = st.columns(6)

if w1.button("Data", use_container_width=True, key="mongo_tab_data"):
    st.session_state.mongo_active_tab = "Data"

if w2.button("Ask AI", use_container_width=True, key="mongo_tab_ask_ai"):
    st.session_state.mongo_active_tab = "Ask AI"

if w3.button("Summary", use_container_width=True, key="mongo_tab_summary"):
    st.session_state.mongo_active_tab = "Summary"

if w4.button("Charts", use_container_width=True, key="mongo_tab_charts"):
    st.session_state.mongo_active_tab = "Charts"

if w5.button("Insights", use_container_width=True, key="mongo_tab_insights"):
    st.session_state.mongo_active_tab = "Insights"

if w6.button("Export", use_container_width=True, key="mongo_tab_export"):
    st.session_state.mongo_active_tab = "Export"


# -------------------------------------------------
# DATA TAB
# -------------------------------------------------

if st.session_state.mongo_active_tab == "Data":

    st.markdown('<div class="section-title">🍃 MongoDB Data</div>', unsafe_allow_html=True)

    if not df.empty:

        k1, k2, k3 = st.columns(3)

        with k1:
            st.metric("Total Records", len(df))

        with k2:
            st.metric("Total Columns", len(df.columns))

        with k3:
            st.metric("Missing Values", int(df.isnull().sum().sum()))

        row_limit = st.selectbox(
            "Rows to Display",
            [1000, 5000, 10000, "All"],
            key="mongo_display_row_limit"
        )

        if row_limit == "All":
            st.warning("Showing all rows may slow or crash the app for large datasets.")
            display_df = df
        else:
            display_df = df.head(row_limit)

        st.dataframe(display_df, use_container_width=True)

        st.markdown('<div class="section-title">📋 Column Details</div>', unsafe_allow_html=True)

        column_info = pd.DataFrame({
            "Column": df.columns,
            "Data Type": df.dtypes.astype(str),
            "Missing Values": df.isnull().sum().values
        })

        st.dataframe(column_info, use_container_width=True)

    else:
        st.info("Connect MongoDB and load a collection to view data here.")


# -------------------------------------------------
# ASK AI TAB
# -------------------------------------------------

elif st.session_state.mongo_active_tab == "Ask AI":

    st.markdown('<div class="section-title">💬 Mongo AI Answer</div>', unsafe_allow_html=True)

    if st.session_state.mongo_ai_answer:
        st.markdown(
            f"""
            <div class="summary-card">
                {st.session_state.mongo_ai_answer}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.info("Ask AI to view the MongoDB answer here.")


# -------------------------------------------------
# SUMMARY TAB
# -------------------------------------------------

elif st.session_state.mongo_active_tab == "Summary":

    st.markdown('<div class="section-title">AI MongoDB Business Summary</div>', unsafe_allow_html=True)

    if st.session_state.mongo_ai_summary:
        st.markdown(
            f"""
            <div class="summary-card">
                {st.session_state.mongo_ai_summary}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.info("Generate summary to view it here.")


# -------------------------------------------------
# CHARTS TAB
# -------------------------------------------------

elif st.session_state.mongo_active_tab == "Charts":

    st.markdown('<div class="section-title">📈 MongoDB KPI Cards & Charts</div>', unsafe_allow_html=True)

    if st.session_state.show_mongo_charts and not df.empty:

        chart_df = df.head(5000)

        show_kpi_and_charts(
            chart_df,
            "MongoDB"
        )

    else:
        st.info("Click Charts to view MongoDB KPI cards and charts here.")


# -------------------------------------------------
# INSIGHTS TAB
# -------------------------------------------------

elif st.session_state.mongo_active_tab == "Insights":

    st.markdown('<div class="section-title">🎯 MongoDB Business Recommendations</div>', unsafe_allow_html=True)

    if st.session_state.mongo_recommendation_text:
        st.markdown(
            f"""
            <div class="recommendation-card">
                {st.session_state.mongo_recommendation_text}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.info("Generate insights to view recommendations here.")


# -------------------------------------------------
# EXPORT TAB
# -------------------------------------------------

elif st.session_state.mongo_active_tab == "Export":

    st.markdown('<div class="section-title">Export MongoDB Report</div>', unsafe_allow_html=True)

    if not df.empty:

        show_download_buttons(
            df,
            "mongodb_report",
            "MongoDB Data",
            st.session_state.mongo_ai_summary
        )

    else:
        st.info("Load MongoDB collection data first to export report.")