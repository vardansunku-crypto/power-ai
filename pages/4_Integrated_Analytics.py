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
from utils.mongo_connector import (
    connect_mongodb,
    get_mongo_databases,
    get_mongo_collections,
    load_collection_as_dataframe
)
from ai.ai_engine import generate_ai_summary, generate_recommendation_summary


st.set_page_config(
    page_title="Integrated Analytics",
    page_icon="🔗",
    layout="wide"
)

check_authentication("integrated")
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

    .st-key-integrated_toolbar {
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


defaults = {
    "integrated_file_df": None,
    "integrated_mongo_df": None,
    "integrated_mongo_client": None,
    "integrated_df": None,
    "integrated_ai_summary": "",
    "integrated_recommendation_text": "",
    "integrated_user_query": "",
    "integrated_merge_type": "inner",
    "integrated_source_mode": "Database + File",
    "show_integrated_charts": False,
    "integrated_active_tab": "Data",
    "show_integrated_upload_panel": True,
    "show_integrated_mongo_panel": False,
    "integrated_mongo_uri": "mongodb://localhost:27017/"
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


if "db_result_df" not in st.session_state or st.session_state.db_result_df is None:
    st.warning("Please run a database query first from Database Analytics page.")
    st.stop()

db_df = clean_dataframe_columns(st.session_state.db_result_df.copy())

api_df = None
if st.session_state.get("api_filtered_df") is not None:
    api_df = clean_dataframe_columns(st.session_state.api_filtered_df.copy())
elif st.session_state.get("api_loaded_df") is not None:
    api_df = clean_dataframe_columns(st.session_state.api_loaded_df.copy())


db_rows = len(db_df)
file_rows = len(st.session_state.integrated_file_df) if st.session_state.integrated_file_df is not None else 0
mongo_rows = len(st.session_state.integrated_mongo_df) if st.session_state.integrated_mongo_df is not None else 0
api_rows = len(api_df) if api_df is not None else 0
integrated_rows = len(st.session_state.integrated_df) if st.session_state.integrated_df is not None else 0


with st.container(key="integrated_toolbar"):

    st.markdown(
        f"""
        <div class="ribbon-title">
            🔗 INTEGRATED ANALYTICS
            <span>MULTI-SOURCE READY</span>
            &nbsp; | &nbsp; DB: {db_rows}
            &nbsp; | &nbsp; FILE: {file_rows}
            &nbsp; | &nbsp; MONGO: {mongo_rows}
            &nbsp; | &nbsp; API: {api_rows}
            &nbsp; | &nbsp; MERGED: {integrated_rows}
        </div>
        """,
        unsafe_allow_html=True
    )

    g1, g2, g3 = st.columns([4, 2, 2])

    with g1:
        st.markdown('<div class="ribbon-group-title">DATA</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            upload_clicked = st.button("Upload", use_container_width=True, key="integrated_upload_btn")

        with c2:
            mongo_clicked = st.button("MongoDB", use_container_width=True, key="integrated_mongo_btn")

        with c3:
            merge_clicked = st.button("Merge", use_container_width=True, key="integrated_merge_btn")

        with c4:
            clear_clicked = st.button("Clear", use_container_width=True, key="integrated_clear_btn")

    with g2:
        st.markdown('<div class="ribbon-group-title">AI ENGINE</div>', unsafe_allow_html=True)
        c5, c6 = st.columns(2)

        with c5:
            summary_clicked = st.button("Summary", use_container_width=True, key="integrated_summary_btn")

        with c6:
            reset_clicked = st.button("Reset", use_container_width=True, key="integrated_reset_btn")

    with g3:
        st.markdown('<div class="ribbon-group-title">ANALYTICS</div>', unsafe_allow_html=True)
        c7, c8 = st.columns(2)

        with c7:
            charts_clicked = st.button("Charts", use_container_width=True, key="integrated_charts_btn")

        with c8:
            recommendation_clicked = st.button("Insights", use_container_width=True, key="integrated_insights_btn")


st.markdown(
    """
    <div class="page-header">
        <h1>🔗 Integrated Analytics</h1>
        <p>Combine MySQL database results with CSV, Excel, MongoDB, and REST API data for integrated business intelligence.</p>
    </div>
    """,
    unsafe_allow_html=True
)


if upload_clicked:
    st.session_state.show_integrated_upload_panel = not st.session_state.show_integrated_upload_panel

if mongo_clicked:
    st.session_state.show_integrated_mongo_panel = not st.session_state.show_integrated_mongo_panel

if reset_clicked:
    st.session_state.integrated_ai_summary = ""
    st.session_state.integrated_recommendation_text = ""
    st.session_state.show_integrated_charts = False
    st.session_state.integrated_active_tab = "Data"
    st.success("Integrated analytics reset.")
    st.rerun()

if clear_clicked:
    st.session_state.integrated_file_df = None
    st.session_state.integrated_mongo_df = None
    st.session_state.integrated_df = None
    st.session_state.integrated_ai_summary = ""
    st.session_state.integrated_recommendation_text = ""
    st.session_state.show_integrated_charts = False
    st.session_state.integrated_active_tab = "Data"
    st.session_state.show_integrated_upload_panel = True
    st.session_state.show_integrated_mongo_panel = False
    st.success("Integrated data cleared.")
    st.rerun()


st.markdown('<div class="section-title">🗄️ Database Result Preview</div>', unsafe_allow_html=True)

db_col1, db_col2 = st.columns(2)

with db_col1:
    st.metric("Database Rows", len(db_df))

with db_col2:
    st.metric("Database Columns", len(db_df.columns))

st.dataframe(db_df.head(1000), use_container_width=True)
st.info(f"Previewing first 1000 rows out of {len(db_df)} database rows.")


if st.session_state.show_integrated_upload_panel:

    st.markdown('<div class="section-title">📁 CSV / Excel Data Source</div>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Upload CSV or Excel Files",
        type=["csv", "xlsx"],
        accept_multiple_files=True,
        key="integrated_file_uploader"
    )

    if uploaded_files:
        dataframes = []

        for file in uploaded_files:
            try:
                if file.name.endswith(".csv"):
                    temp_df = pd.read_csv(file)
                elif file.name.endswith(".xlsx"):
                    temp_df = pd.read_excel(file)
                else:
                    continue

                temp_df = clean_dataframe_columns(temp_df)
                temp_df["source_file"] = file.name
                dataframes.append(temp_df)

            except Exception as e:
                st.error(f"File Error in {file.name}: {e}")

        if dataframes:
            file_df = pd.concat(dataframes, ignore_index=True)
            file_df = clean_dataframe_columns(file_df)

            st.session_state.integrated_file_df = file_df
            st.session_state.integrated_df = None
            st.session_state.integrated_ai_summary = ""
            st.session_state.integrated_recommendation_text = ""
            st.session_state.show_integrated_charts = False
            st.session_state.integrated_active_tab = "Data"
            st.session_state.show_integrated_upload_panel = False

            st.success("Files uploaded successfully.")
            st.rerun()


file_df = st.session_state.integrated_file_df

if file_df is not None:

    st.markdown('<div class="section-title">📄 File Data Preview</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("File Rows", len(file_df))

    with col2:
        st.metric("File Columns", len(file_df.columns))

    with col3:
        if "source_file" in file_df.columns:
            st.metric("Uploaded Files", file_df["source_file"].nunique())
        else:
            st.metric("Uploaded Files", 1)

    st.dataframe(file_df.head(1000), use_container_width=True)
    st.info(f"Previewing first 1000 rows out of {len(file_df)} file rows.")

else:
    st.info("CSV/Excel source not loaded yet.")


if st.session_state.show_integrated_mongo_panel:

    st.markdown('<div class="section-title">🍃 MongoDB Data Source</div>', unsafe_allow_html=True)

    mongo_uri = st.text_input(
        "MongoDB URI",
        value=st.session_state.integrated_mongo_uri,
        key="integrated_mongo_uri_input"
    )

    st.session_state.integrated_mongo_uri = mongo_uri

    m1, m2 = st.columns([1, 3])

    with m1:
        connect_mongo_clicked = st.button(
            "Connect MongoDB",
            use_container_width=True,
            key="integrated_connect_mongo_btn"
        )

    with m2:
        st.caption("Default local URI: mongodb://localhost:27017/")

    if connect_mongo_clicked:
        try:
            mongo_client = connect_mongodb(mongo_uri)
            st.session_state.integrated_mongo_client = mongo_client
            st.success("MongoDB connected successfully.")
        except Exception as e:
            st.error(e)

    if st.session_state.integrated_mongo_client is not None:

        mongo_client = st.session_state.integrated_mongo_client

        mongo_databases = get_mongo_databases(mongo_client)
        mongo_databases = [
            db for db in mongo_databases
            if db not in ["admin", "local", "config"]
        ]

        if mongo_databases:

            mc1, mc2, mc3 = st.columns(3)

            with mc1:
                selected_mongo_db = st.selectbox(
                    "MongoDB Database",
                    mongo_databases,
                    key="integrated_selected_mongo_db"
                )

            mongo_collections = get_mongo_collections(mongo_client, selected_mongo_db)

            with mc2:
                if mongo_collections:
                    selected_mongo_collection = st.selectbox(
                        "MongoDB Collection",
                        mongo_collections,
                        key="integrated_selected_mongo_collection"
                    )
                else:
                    selected_mongo_collection = None
                    st.warning("No collections found in this database.")

            with mc3:
                mongo_limit = st.number_input(
                    "Mongo Rows Limit",
                    min_value=10,
                    max_value=10000,
                    value=1000,
                    step=100,
                    key="integrated_mongo_limit"
                )

            if selected_mongo_collection:
                if st.button("Load MongoDB Collection", use_container_width=True, key="integrated_load_mongo_collection"):
                    try:
                        mongo_df = load_collection_as_dataframe(
                            mongo_client,
                            selected_mongo_db,
                            selected_mongo_collection,
                            mongo_limit
                        )
                        mongo_df = clean_dataframe_columns(mongo_df)

                        if mongo_df.empty:
                            st.warning("No data found in this MongoDB collection.")
                        else:
                            st.session_state.integrated_mongo_df = mongo_df
                            st.session_state.integrated_df = None
                            st.session_state.integrated_ai_summary = ""
                            st.session_state.integrated_recommendation_text = ""
                            st.session_state.show_integrated_charts = False
                            st.session_state.integrated_active_tab = "Data"
                            st.success("MongoDB collection loaded successfully.")
                            st.rerun()

                    except Exception as e:
                        st.error(f"MongoDB Load Error: {e}")
        else:
            st.warning("No user databases found in MongoDB.")


mongo_df = st.session_state.integrated_mongo_df

if mongo_df is not None:

    st.markdown('<div class="section-title">🍃 MongoDB Data Preview</div>', unsafe_allow_html=True)

    mg1, mg2, mg3 = st.columns(3)

    with mg1:
        st.metric("MongoDB Rows", len(mongo_df))

    with mg2:
        st.metric("MongoDB Columns", len(mongo_df.columns))

    with mg3:
        st.metric("MongoDB Missing Values", int(mongo_df.isnull().sum().sum()))

    st.dataframe(mongo_df.head(1000), use_container_width=True)
    st.info(f"Previewing first 1000 rows out of {len(mongo_df)} MongoDB rows.")

else:
    st.info("MongoDB source not loaded yet.")


if api_df is not None:

    st.markdown('<div class="section-title">🌐 API Data Preview</div>', unsafe_allow_html=True)

    api1, api2, api3 = st.columns(3)

    with api1:
        st.metric("API Rows", len(api_df))

    with api2:
        st.metric("API Columns", len(api_df.columns))

    with api3:
        st.metric("API Missing Values", int(api_df.isnull().sum().sum()))

    st.dataframe(api_df.head(1000), use_container_width=True)
    st.info(f"Previewing first 1000 rows out of {len(api_df)} API rows.")

else:
    st.info("API source not loaded yet. First fetch API data from API Analytics page.")


st.markdown('<div class="section-title">🔑 Select Integration Mode & Merge Columns</div>', unsafe_allow_html=True)

integration_options = [
    "Database + File",
    "Database + MongoDB",
    "Database + API",
    "Database + File + MongoDB",
    "Database + File + API",
    "Database + MongoDB + API",
    "Database + File + MongoDB + API"
]

integration_mode = st.selectbox(
    "Integration Source",
    integration_options,
    index=integration_options.index(st.session_state.integrated_source_mode)
    if st.session_state.integrated_source_mode in integration_options else 0,
    key="integrated_source_mode_select"
)

st.session_state.integrated_source_mode = integration_mode

merge_type = st.selectbox(
    "Merge Type",
    ["inner", "left", "right", "outer"],
    index=0,
    key="integrated_merge_type_select"
)

st.session_state.integrated_merge_type = merge_type

db_columns = db_df.columns.tolist()
file_columns = file_df.columns.tolist() if file_df is not None else []
mongo_columns = mongo_df.columns.tolist() if mongo_df is not None else []
api_columns = api_df.columns.tolist() if api_df is not None else []


db_merge_column = None
file_merge_column = None
mongo_merge_column = None
api_merge_column = None


if integration_mode == "Database + File":

    if file_df is None:
        st.warning("Upload CSV/Excel files first for Database + File integration.")
    else:
        common_columns = list(set(db_columns).intersection(set(file_columns)))

        if common_columns:
            st.success(f"Database/File common columns found: {', '.join(common_columns)}")
        else:
            st.warning("No exact common column names found between Database and File. Select columns manually.")

        col4, col5 = st.columns(2)

        with col4:
            db_merge_column = st.selectbox(
                "Database Merge Column",
                db_columns,
                index=db_columns.index(common_columns[0]) if common_columns else 0,
                key="integrated_db_merge_column_file"
            )

        with col5:
            file_merge_column = st.selectbox(
                "File Merge Column",
                file_columns,
                index=file_columns.index(common_columns[0]) if common_columns else 0,
                key="integrated_file_merge_column"
            )


elif integration_mode == "Database + MongoDB":

    if mongo_df is None:
        st.warning("Load MongoDB collection first for Database + MongoDB integration.")
    else:
        common_columns = list(set(db_columns).intersection(set(mongo_columns)))

        if common_columns:
            st.success(f"Database/MongoDB common columns found: {', '.join(common_columns)}")
        else:
            st.warning("No exact common column names found between Database and MongoDB. Select columns manually.")

        col4, col5 = st.columns(2)

        with col4:
            db_merge_column = st.selectbox(
                "Database Merge Column",
                db_columns,
                index=db_columns.index(common_columns[0]) if common_columns else 0,
                key="integrated_db_merge_column_mongo"
            )

        with col5:
            mongo_merge_column = st.selectbox(
                "MongoDB Merge Column",
                mongo_columns,
                index=mongo_columns.index(common_columns[0]) if common_columns else 0,
                key="integrated_mongo_merge_column"
            )


elif integration_mode == "Database + API":

    if api_df is None:
        st.warning("Fetch API data first from API Analytics page.")
    else:
        common_columns = list(set(db_columns).intersection(set(api_columns)))

        if common_columns:
            st.success(f"Database/API common columns found: {', '.join(common_columns)}")
        else:
            st.warning("No exact common column names found between Database and API. Select columns manually.")

        col4, col5 = st.columns(2)

        with col4:
            db_merge_column = st.selectbox(
                "Database Merge Column",
                db_columns,
                index=db_columns.index(common_columns[0]) if common_columns else 0,
                key="integrated_db_merge_column_api"
            )

        with col5:
            api_merge_column = st.selectbox(
                "API Merge Column",
                api_columns,
                index=api_columns.index(common_columns[0]) if common_columns else 0,
                key="integrated_api_merge_column"
            )


elif integration_mode == "Database + File + MongoDB":

    if file_df is None or mongo_df is None:
        st.warning("Upload CSV/Excel and load MongoDB collection first.")
    else:
        common_file_columns = list(set(db_columns).intersection(set(file_columns)))
        common_mongo_columns = list(set(db_columns).intersection(set(mongo_columns)))

        col4, col5, col6 = st.columns(3)

        with col4:
            db_merge_column = st.selectbox(
                "Database Merge Column",
                db_columns,
                index=db_columns.index(common_file_columns[0]) if common_file_columns else 0,
                key="integrated_db_merge_column_full"
            )

        with col5:
            file_merge_column = st.selectbox(
                "File Merge Column",
                file_columns,
                index=file_columns.index(common_file_columns[0]) if common_file_columns else 0,
                key="integrated_file_merge_column_full"
            )

        with col6:
            mongo_merge_column = st.selectbox(
                "MongoDB Merge Column",
                mongo_columns,
                index=mongo_columns.index(common_mongo_columns[0]) if common_mongo_columns else 0,
                key="integrated_mongo_merge_column_full"
            )


elif integration_mode == "Database + File + API":

    if file_df is None or api_df is None:
        st.warning("Upload CSV/Excel and fetch API data first.")
    else:
        common_file_columns = list(set(db_columns).intersection(set(file_columns)))
        common_api_columns = list(set(db_columns).intersection(set(api_columns)))

        col4, col5, col6 = st.columns(3)

        with col4:
            db_merge_column = st.selectbox(
                "Database Merge Column",
                db_columns,
                index=db_columns.index(common_file_columns[0]) if common_file_columns else 0,
                key="integrated_db_merge_column_file_api"
            )

        with col5:
            file_merge_column = st.selectbox(
                "File Merge Column",
                file_columns,
                index=file_columns.index(common_file_columns[0]) if common_file_columns else 0,
                key="integrated_file_merge_column_api_mode"
            )

        with col6:
            api_merge_column = st.selectbox(
                "API Merge Column",
                api_columns,
                index=api_columns.index(common_api_columns[0]) if common_api_columns else 0,
                key="integrated_api_merge_column_file_api_mode"
            )


elif integration_mode == "Database + MongoDB + API":

    if mongo_df is None or api_df is None:
        st.warning("Load MongoDB collection and fetch API data first.")
    else:
        common_mongo_columns = list(set(db_columns).intersection(set(mongo_columns)))
        common_api_columns = list(set(db_columns).intersection(set(api_columns)))

        col4, col5, col6 = st.columns(3)

        with col4:
            db_merge_column = st.selectbox(
                "Database Merge Column",
                db_columns,
                index=db_columns.index(common_mongo_columns[0]) if common_mongo_columns else 0,
                key="integrated_db_merge_column_mongo_api"
            )

        with col5:
            mongo_merge_column = st.selectbox(
                "MongoDB Merge Column",
                mongo_columns,
                index=mongo_columns.index(common_mongo_columns[0]) if common_mongo_columns else 0,
                key="integrated_mongo_merge_column_api_mode"
            )

        with col6:
            api_merge_column = st.selectbox(
                "API Merge Column",
                api_columns,
                index=api_columns.index(common_api_columns[0]) if common_api_columns else 0,
                key="integrated_api_merge_column_mongo_api_mode"
            )


elif integration_mode == "Database + File + MongoDB + API":

    if file_df is None or mongo_df is None or api_df is None:
        st.warning("Upload CSV/Excel, load MongoDB collection, and fetch API data first.")
    else:
        common_file_columns = list(set(db_columns).intersection(set(file_columns)))
        common_mongo_columns = list(set(db_columns).intersection(set(mongo_columns)))
        common_api_columns = list(set(db_columns).intersection(set(api_columns)))

        col4, col5, col6, col7 = st.columns(4)

        with col4:
            db_merge_column = st.selectbox(
                "Database Merge Column",
                db_columns,
                index=db_columns.index(common_file_columns[0]) if common_file_columns else 0,
                key="integrated_db_merge_column_all"
            )

        with col5:
            file_merge_column = st.selectbox(
                "File Merge Column",
                file_columns,
                index=file_columns.index(common_file_columns[0]) if common_file_columns else 0,
                key="integrated_file_merge_column_all"
            )

        with col6:
            mongo_merge_column = st.selectbox(
                "MongoDB Merge Column",
                mongo_columns,
                index=mongo_columns.index(common_mongo_columns[0]) if common_mongo_columns else 0,
                key="integrated_mongo_merge_column_all"
            )

        with col7:
            api_merge_column = st.selectbox(
                "API Merge Column",
                api_columns,
                index=api_columns.index(common_api_columns[0]) if common_api_columns else 0,
                key="integrated_api_merge_column_all"
            )


if merge_clicked:

    try:
        if integration_mode == "Database + File":

            if file_df is None:
                st.error("Please upload CSV/Excel files first.")
            else:
                db_merge_temp = db_df.copy()
                file_merge_temp = file_df.copy()

                db_merge_temp[db_merge_column] = db_merge_temp[db_merge_column].astype(str)
                file_merge_temp[file_merge_column] = file_merge_temp[file_merge_column].astype(str)

                integrated_df = pd.merge(
                    db_merge_temp,
                    file_merge_temp,
                    left_on=db_merge_column,
                    right_on=file_merge_column,
                    how=merge_type,
                    suffixes=("_db", "_file")
                )

                integrated_df = clean_dataframe_columns(integrated_df)
                st.session_state.integrated_df = integrated_df
                st.session_state.integrated_merge_type = merge_type
                st.session_state.integrated_ai_summary = ""
                st.session_state.integrated_recommendation_text = ""
                st.session_state.show_integrated_charts = False
                st.session_state.integrated_active_tab = "Data"
                st.success("Database + File data merged successfully.")

        elif integration_mode == "Database + MongoDB":

            if mongo_df is None:
                st.error("Please load MongoDB collection first.")
            else:
                db_merge_temp = db_df.copy()
                mongo_merge_temp = mongo_df.copy()

                db_merge_temp[db_merge_column] = db_merge_temp[db_merge_column].astype(str)
                mongo_merge_temp[mongo_merge_column] = mongo_merge_temp[mongo_merge_column].astype(str)

                integrated_df = pd.merge(
                    db_merge_temp,
                    mongo_merge_temp,
                    left_on=db_merge_column,
                    right_on=mongo_merge_column,
                    how=merge_type,
                    suffixes=("_db", "_mongo")
                )

                integrated_df = clean_dataframe_columns(integrated_df)
                st.session_state.integrated_df = integrated_df
                st.session_state.integrated_merge_type = merge_type
                st.session_state.integrated_ai_summary = ""
                st.session_state.integrated_recommendation_text = ""
                st.session_state.show_integrated_charts = False
                st.session_state.integrated_active_tab = "Data"
                st.success("Database + MongoDB data merged successfully.")

        elif integration_mode == "Database + API":

            if api_df is None:
                st.error("Please fetch API data first from API Analytics page.")
            else:
                db_merge_temp = db_df.copy()
                api_merge_temp = api_df.copy()

                db_merge_temp[db_merge_column] = db_merge_temp[db_merge_column].astype(str)
                api_merge_temp[api_merge_column] = api_merge_temp[api_merge_column].astype(str)

                integrated_df = pd.merge(
                    db_merge_temp,
                    api_merge_temp,
                    left_on=db_merge_column,
                    right_on=api_merge_column,
                    how=merge_type,
                    suffixes=("_db", "_api")
                )

                integrated_df = clean_dataframe_columns(integrated_df)
                st.session_state.integrated_df = integrated_df
                st.session_state.integrated_merge_type = merge_type
                st.session_state.integrated_ai_summary = ""
                st.session_state.integrated_recommendation_text = ""
                st.session_state.show_integrated_charts = False
                st.session_state.integrated_active_tab = "Data"
                st.success("Database + API data merged successfully.")

        elif integration_mode == "Database + File + MongoDB":

            if file_df is None or mongo_df is None:
                st.error("Please upload CSV/Excel and load MongoDB collection first.")
            else:
                db_merge_temp = db_df.copy()
                file_merge_temp = file_df.copy()
                mongo_merge_temp = mongo_df.copy()

                db_merge_temp[db_merge_column] = db_merge_temp[db_merge_column].astype(str)
                file_merge_temp[file_merge_column] = file_merge_temp[file_merge_column].astype(str)
                mongo_merge_temp[mongo_merge_column] = mongo_merge_temp[mongo_merge_column].astype(str)

                db_file_df = pd.merge(
                    db_merge_temp,
                    file_merge_temp,
                    left_on=db_merge_column,
                    right_on=file_merge_column,
                    how=merge_type,
                    suffixes=("_db", "_file")
                )

                db_file_df = clean_dataframe_columns(db_file_df)

                temp_merge_column = db_merge_column
                if temp_merge_column not in db_file_df.columns:
                    possible_db_key = f"{db_merge_column}_db"
                    if possible_db_key in db_file_df.columns:
                        temp_merge_column = possible_db_key
                    else:
                        st.error("Could not find database merge column after Database + File merge.")
                        st.stop()

                db_file_df[temp_merge_column] = db_file_df[temp_merge_column].astype(str)

                integrated_df = pd.merge(
                    db_file_df,
                    mongo_merge_temp,
                    left_on=temp_merge_column,
                    right_on=mongo_merge_column,
                    how=merge_type,
                    suffixes=("", "_mongo")
                )

                integrated_df = clean_dataframe_columns(integrated_df)
                st.session_state.integrated_df = integrated_df
                st.session_state.integrated_merge_type = merge_type
                st.session_state.integrated_ai_summary = ""
                st.session_state.integrated_recommendation_text = ""
                st.session_state.show_integrated_charts = False
                st.session_state.integrated_active_tab = "Data"
                st.success("Database + File + MongoDB data merged successfully.")

        elif integration_mode == "Database + File + API":

            if file_df is None or api_df is None:
                st.error("Please upload CSV/Excel and fetch API data first.")
            else:
                db_merge_temp = db_df.copy()
                file_merge_temp = file_df.copy()
                api_merge_temp = api_df.copy()

                db_merge_temp[db_merge_column] = db_merge_temp[db_merge_column].astype(str)
                file_merge_temp[file_merge_column] = file_merge_temp[file_merge_column].astype(str)

                db_file_df = pd.merge(
                    db_merge_temp,
                    file_merge_temp,
                    left_on=db_merge_column,
                    right_on=file_merge_column,
                    how=merge_type,
                    suffixes=("_db", "_file")
                )

                db_file_df = clean_dataframe_columns(db_file_df)

                temp_merge_column = db_merge_column
                if temp_merge_column not in db_file_df.columns:
                    possible_db_key = f"{db_merge_column}_db"
                    if possible_db_key in db_file_df.columns:
                        temp_merge_column = possible_db_key
                    else:
                        st.error("Could not find database merge column after Database + File merge.")
                        st.stop()

                db_file_df[temp_merge_column] = db_file_df[temp_merge_column].astype(str)
                api_merge_temp[api_merge_column] = api_merge_temp[api_merge_column].astype(str)

                integrated_df = pd.merge(
                    db_file_df,
                    api_merge_temp,
                    left_on=temp_merge_column,
                    right_on=api_merge_column,
                    how=merge_type,
                    suffixes=("", "_api")
                )

                integrated_df = clean_dataframe_columns(integrated_df)
                st.session_state.integrated_df = integrated_df
                st.session_state.integrated_merge_type = merge_type
                st.session_state.integrated_ai_summary = ""
                st.session_state.integrated_recommendation_text = ""
                st.session_state.show_integrated_charts = False
                st.session_state.integrated_active_tab = "Data"
                st.success("Database + File + API data merged successfully.")

        elif integration_mode == "Database + MongoDB + API":

            if mongo_df is None or api_df is None:
                st.error("Please load MongoDB collection and fetch API data first.")
            else:
                db_merge_temp = db_df.copy()
                mongo_merge_temp = mongo_df.copy()
                api_merge_temp = api_df.copy()

                db_merge_temp[db_merge_column] = db_merge_temp[db_merge_column].astype(str)
                mongo_merge_temp[mongo_merge_column] = mongo_merge_temp[mongo_merge_column].astype(str)

                db_mongo_df = pd.merge(
                    db_merge_temp,
                    mongo_merge_temp,
                    left_on=db_merge_column,
                    right_on=mongo_merge_column,
                    how=merge_type,
                    suffixes=("_db", "_mongo")
                )

                db_mongo_df = clean_dataframe_columns(db_mongo_df)

                temp_merge_column = db_merge_column
                if temp_merge_column not in db_mongo_df.columns:
                    possible_db_key = f"{db_merge_column}_db"
                    if possible_db_key in db_mongo_df.columns:
                        temp_merge_column = possible_db_key
                    else:
                        st.error("Could not find database merge column after Database + MongoDB merge.")
                        st.stop()

                db_mongo_df[temp_merge_column] = db_mongo_df[temp_merge_column].astype(str)
                api_merge_temp[api_merge_column] = api_merge_temp[api_merge_column].astype(str)

                integrated_df = pd.merge(
                    db_mongo_df,
                    api_merge_temp,
                    left_on=temp_merge_column,
                    right_on=api_merge_column,
                    how=merge_type,
                    suffixes=("", "_api")
                )

                integrated_df = clean_dataframe_columns(integrated_df)
                st.session_state.integrated_df = integrated_df
                st.session_state.integrated_merge_type = merge_type
                st.session_state.integrated_ai_summary = ""
                st.session_state.integrated_recommendation_text = ""
                st.session_state.show_integrated_charts = False
                st.session_state.integrated_active_tab = "Data"
                st.success("Database + MongoDB + API data merged successfully.")

        elif integration_mode == "Database + File + MongoDB + API":

            if file_df is None or mongo_df is None or api_df is None:
                st.error("Please upload CSV/Excel, load MongoDB collection, and fetch API data first.")
            else:
                db_merge_temp = db_df.copy()
                file_merge_temp = file_df.copy()
                mongo_merge_temp = mongo_df.copy()
                api_merge_temp = api_df.copy()

                db_merge_temp[db_merge_column] = db_merge_temp[db_merge_column].astype(str)
                file_merge_temp[file_merge_column] = file_merge_temp[file_merge_column].astype(str)
                mongo_merge_temp[mongo_merge_column] = mongo_merge_temp[mongo_merge_column].astype(str)

                db_file_df = pd.merge(
                    db_merge_temp,
                    file_merge_temp,
                    left_on=db_merge_column,
                    right_on=file_merge_column,
                    how=merge_type,
                    suffixes=("_db", "_file")
                )

                db_file_df = clean_dataframe_columns(db_file_df)

                temp_merge_column = db_merge_column
                if temp_merge_column not in db_file_df.columns:
                    possible_db_key = f"{db_merge_column}_db"
                    if possible_db_key in db_file_df.columns:
                        temp_merge_column = possible_db_key
                    else:
                        st.error("Could not find database merge column after Database + File merge.")
                        st.stop()

                db_file_df[temp_merge_column] = db_file_df[temp_merge_column].astype(str)

                db_file_mongo_df = pd.merge(
                    db_file_df,
                    mongo_merge_temp,
                    left_on=temp_merge_column,
                    right_on=mongo_merge_column,
                    how=merge_type,
                    suffixes=("", "_mongo")
                )

                db_file_mongo_df = clean_dataframe_columns(db_file_mongo_df)

                temp_merge_column = db_merge_column
                if temp_merge_column not in db_file_mongo_df.columns:
                    possible_db_key = f"{db_merge_column}_db"
                    if possible_db_key in db_file_mongo_df.columns:
                        temp_merge_column = possible_db_key

                db_file_mongo_df[temp_merge_column] = db_file_mongo_df[temp_merge_column].astype(str)
                api_merge_temp[api_merge_column] = api_merge_temp[api_merge_column].astype(str)

                integrated_df = pd.merge(
                    db_file_mongo_df,
                    api_merge_temp,
                    left_on=temp_merge_column,
                    right_on=api_merge_column,
                    how=merge_type,
                    suffixes=("", "_api")
                )

                integrated_df = clean_dataframe_columns(integrated_df)
                st.session_state.integrated_df = integrated_df
                st.session_state.integrated_merge_type = merge_type
                st.session_state.integrated_ai_summary = ""
                st.session_state.integrated_recommendation_text = ""
                st.session_state.show_integrated_charts = False
                st.session_state.integrated_active_tab = "Data"
                st.success("Database + File + MongoDB + API data merged successfully.")

    except Exception as e:
        st.error(f"Merge Error: {e}")


st.markdown('<div class="section-title">🧠 Ask Question About Integrated Data</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="hint-box">
        <b>Example questions:</b><br>
        • What combined business insight is visible after merging?<br>
        • Which product has high database sales and high API activity?<br>
        • Which customer/category performs best after integrating all sources?<br>
        • What improvements can be made using MySQL, CSV/Excel, MongoDB, and API data?
    </div>
    """,
    unsafe_allow_html=True
)

user_query = st.text_input(
    "Ask question about integrated data",
    value=st.session_state.integrated_user_query,
    key="integrated_user_query_input"
)

st.session_state.integrated_user_query = user_query


if summary_clicked:

    if st.session_state.integrated_df is None:
        st.error("Please merge data first.")

    else:
        summary_df = st.session_state.integrated_df.head(100)

        st.session_state.integrated_ai_summary = generate_ai_summary(
            client,
            "AI Integrated Multi-Source Business Summary",
            user_query,
            summary_df,
            st
        )

        st.session_state.integrated_active_tab = "Summary"
        st.success("Integrated AI summary generated.")


if charts_clicked:

    if st.session_state.integrated_df is None:
        st.error("Please merge data first.")

    else:
        st.session_state.show_integrated_charts = True
        st.session_state.integrated_active_tab = "Charts"
        st.success("Integrated charts generated.")


if recommendation_clicked:

    if st.session_state.integrated_df is None:
        st.error("Please merge data first.")

    else:
        recommendation_df = st.session_state.integrated_df.head(100)

        st.session_state.integrated_recommendation_text = generate_recommendation_summary(
            client,
            user_query,
            recommendation_df
        )

        st.session_state.integrated_active_tab = "Insights"
        st.success("Integrated recommendations generated.")


st.markdown('<div class="section-title">📌 Integrated Workspace</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.columns(5)

if tab1.button("Data", use_container_width=True, key="integrated_tab_data"):
    st.session_state.integrated_active_tab = "Data"

if tab2.button("Summary", use_container_width=True, key="integrated_tab_summary"):
    st.session_state.integrated_active_tab = "Summary"

if tab3.button("Charts", use_container_width=True, key="integrated_tab_charts"):
    st.session_state.integrated_active_tab = "Charts"

if tab4.button("Insights", use_container_width=True, key="integrated_tab_insights"):
    st.session_state.integrated_active_tab = "Insights"

if tab5.button("Export", use_container_width=True, key="integrated_tab_export"):
    st.session_state.integrated_active_tab = "Export"


if st.session_state.integrated_active_tab == "Data":

    st.markdown('<div class="section-title">🔗 Integrated Data</div>', unsafe_allow_html=True)

    if st.session_state.integrated_df is not None:

        integrated_df = st.session_state.integrated_df

        col7, col8, col9, col10 = st.columns(4)

        with col7:
            st.metric("Integrated Rows", len(integrated_df))

        with col8:
            st.metric("Integrated Columns", len(integrated_df.columns))

        with col9:
            st.metric("Merge Type", st.session_state.integrated_merge_type)

        with col10:
            st.metric("Source Mode", st.session_state.integrated_source_mode)

        row_limit = st.selectbox(
            "Rows to Display",
            [1000, 5000, 10000, "All"],
            key="integrated_row_limit"
        )

        if row_limit == "All":
            st.warning("Showing all rows may slow or crash the app for large datasets.")
            display_df = integrated_df
        else:
            display_df = integrated_df.head(row_limit)

        st.dataframe(display_df, use_container_width=True)

        if row_limit != "All":
            st.info(f"Previewing {row_limit} rows out of {len(integrated_df)} total rows.")

    else:
        st.info("Merge data to view integrated results here.")


elif st.session_state.integrated_active_tab == "Summary":

    st.markdown('<div class="section-title">AI Integrated Business Summary</div>', unsafe_allow_html=True)

    if st.session_state.integrated_ai_summary:
        st.markdown(
            f"""
            <div class="summary-card">
                {st.session_state.integrated_ai_summary}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.info("Generate summary to view it here.")


elif st.session_state.integrated_active_tab == "Charts":

    st.markdown('<div class="section-title">📈 Integrated KPI Cards & Charts</div>', unsafe_allow_html=True)

    if st.session_state.show_integrated_charts and st.session_state.integrated_df is not None:

        chart_df = st.session_state.integrated_df.head(5000)

        show_kpi_and_charts(
            chart_df,
            "Integrated"
        )

    else:
        st.info("Click Charts to view integrated KPI cards and charts here.")


elif st.session_state.integrated_active_tab == "Insights":

    st.markdown('<div class="section-title">🎯 Integrated Business Recommendations</div>', unsafe_allow_html=True)

    if st.session_state.integrated_recommendation_text:
        st.markdown(
            f"""
            <div class="recommendation-card">
                {st.session_state.integrated_recommendation_text}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.info("Generate insights to view recommendations here.")


elif st.session_state.integrated_active_tab == "Export":

    st.markdown('<div class="section-title">Export Integrated Report</div>', unsafe_allow_html=True)

    if st.session_state.integrated_df is not None:

        show_download_buttons(
            st.session_state.integrated_df,
            "integrated_multisource_report",
            "Integrated Multi-Source Data",
            st.session_state.integrated_ai_summary
        )

    else:
        st.info("Merge data first to export integrated report.")