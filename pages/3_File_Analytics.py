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
    generate_ai_summary,
    generate_recommendation_summary
)


st.set_page_config(
    page_title="File Analytics | Power AI",
    page_icon="📁",
    layout="wide"
)

check_authentication("file")
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
        font-size: 40px;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .page-header p {
        color: #9CA3AF !important;
        font-size: 16px;
        margin-bottom: 0;
    }

    .st-key-file_toolbar {
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
        margin-top: 30px;
        margin-bottom: 14px;
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

    .stTextInput label,
    .stTextArea label,
    .stSelectbox label,
    .stMultiSelect label,
    .stSlider label,
    .stFileUploader label {
        color: #E5E7EB !important;
        font-weight: 600 !important;
    }

    .stTextInput input,
    .stTextArea textarea {
        background-color: #111827 !important;
        color: #F9FAFB !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        border-radius: 12px !important;
    }

    details {
        background: #111827 !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
    }

    summary {
        color: #F9FAFB !important;
        font-weight: 700 !important;
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
    "file_uploaded_df": None,
    "file_filtered_df": None,
    "file_ai_summary": "",
    "file_user_query": "",
    "show_file_charts": False,
    "file_recommendation_text": "",
    "file_analysis_done": False,
    "show_file_upload_panel": False,
    "show_file_filters": True,
    "file_active_tab": "Results"
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -------------------------------------------------
# BEFORE FILE UPLOAD
# -------------------------------------------------

if st.session_state.file_uploaded_df is None:

    st.markdown(
        """
        <div class="page-header">
            <h1>▤ File Analytics</h1>
            <p>Upload CSV or Excel files, clean data, analyze KPIs, generate summaries, charts, and recommendations.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">File Upload</div>',
        unsafe_allow_html=True
    )

    uploaded_files = st.file_uploader(
        "Upload CSV or Excel Files",
        type=["csv", "xlsx"],
        accept_multiple_files=True
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

        if len(dataframes) > 0:

            uploaded_df = pd.concat(dataframes, ignore_index=True)
            uploaded_df = clean_dataframe_columns(uploaded_df)

            st.session_state.file_uploaded_df = uploaded_df
            st.session_state.file_filtered_df = uploaded_df
            st.session_state.file_ai_summary = ""
            st.session_state.show_file_charts = False
            st.session_state.file_recommendation_text = ""
            st.session_state.file_analysis_done = False
            st.session_state.file_active_tab = "Results"

            st.success("Files uploaded successfully.")
            st.rerun()

    st.info("Please upload CSV or Excel files first.")
    st.stop()


uploaded_df = st.session_state.file_uploaded_df


# -------------------------------------------------
# FILE STATUS VALUES
# -------------------------------------------------

total_rows = len(uploaded_df)
total_columns = len(uploaded_df.columns)

if "source_file" in uploaded_df.columns:
    total_files = uploaded_df["source_file"].nunique()
else:
    total_files = 1


# -------------------------------------------------
# FIXED EXCEL STYLE RIBBON
# -------------------------------------------------

with st.container(key="file_toolbar"):

    st.markdown(
        f"""
        <div class="ribbon-title">
            ▤ FILE ANALYTICS
            <span>FILES LOADED</span>
            &nbsp; | &nbsp; FILES: {total_files}
            &nbsp; | &nbsp; ROWS: {total_rows}
            &nbsp; | &nbsp; COLUMNS: {total_columns}
        </div>
        """,
        unsafe_allow_html=True
    )

    g1, g2, g3 = st.columns([3, 3, 2])

    with g1:
        st.markdown('<div class="ribbon-group-title">FILE</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)

        with c1:
            if st.button("Upload", use_container_width=True):
                st.session_state.show_file_upload_panel = not st.session_state.show_file_upload_panel

        with c2:
            if st.button("Filters", use_container_width=True):
                st.session_state.show_file_filters = not st.session_state.show_file_filters

        with c3:
            clear_clicked = st.button("Clear", use_container_width=True)

    with g2:
        st.markdown('<div class="ribbon-group-title">AI ENGINE</div>', unsafe_allow_html=True)

        c4, c5, c6 = st.columns(3)

        with c4:
            analyze_clicked = st.button("Analyze", use_container_width=True)

        with c5:
            summary_clicked = st.button("Summary", use_container_width=True)

        with c6:
            reset_clicked = st.button("Reset", use_container_width=True)

    with g3:
        st.markdown('<div class="ribbon-group-title">ANALYTICS</div>', unsafe_allow_html=True)

        c7, c8 = st.columns(2)

        with c7:
            charts_clicked = st.button("Charts", use_container_width=True)

        with c8:
            recommendation_clicked = st.button("Insights", use_container_width=True)


# -------------------------------------------------
# CLEAR / RESET ACTIONS
# -------------------------------------------------

if clear_clicked:
    st.session_state.file_uploaded_df = None
    st.session_state.file_filtered_df = None
    st.session_state.file_ai_summary = ""
    st.session_state.file_user_query = ""
    st.session_state.show_file_charts = False
    st.session_state.file_recommendation_text = ""
    st.session_state.file_analysis_done = False
    st.session_state.file_active_tab = "Results"
    st.success("File data cleared.")
    st.rerun()


if reset_clicked:
    st.session_state.file_filtered_df = uploaded_df
    st.session_state.file_ai_summary = ""
    st.session_state.show_file_charts = False
    st.session_state.file_recommendation_text = ""
    st.session_state.file_analysis_done = False
    st.session_state.file_active_tab = "Results"
    st.success("File filters reset.")
    st.rerun()


# -------------------------------------------------
# UPLOAD / REPLACE PANEL
# -------------------------------------------------

if st.session_state.show_file_upload_panel:

    st.markdown('<div class="section-title">Replace Uploaded Files</div>', unsafe_allow_html=True)

    new_uploaded_files = st.file_uploader(
        "Upload new CSV or Excel Files",
        type=["csv", "xlsx"],
        accept_multiple_files=True,
        key="replace_file_uploader"
    )

    if new_uploaded_files:

        dataframes = []

        for file in new_uploaded_files:

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

        if len(dataframes) > 0:

            uploaded_df = pd.concat(dataframes, ignore_index=True)
            uploaded_df = clean_dataframe_columns(uploaded_df)

            st.session_state.file_uploaded_df = uploaded_df
            st.session_state.file_filtered_df = uploaded_df
            st.session_state.file_ai_summary = ""
            st.session_state.show_file_charts = False
            st.session_state.file_recommendation_text = ""
            st.session_state.file_analysis_done = False
            st.session_state.show_file_upload_panel = False
            st.session_state.file_active_tab = "Results"

            st.success("Files replaced successfully.")
            st.rerun()


# -------------------------------------------------
# FILTER SECTION
# -------------------------------------------------

filtered_df = uploaded_df.copy()

if st.session_state.show_file_filters:

    st.markdown('<div class="section-title">File Filters</div>', unsafe_allow_html=True)

    all_columns = filtered_df.columns.tolist()

    categorical_columns = filtered_df.select_dtypes(
        include=["object"]
    ).columns.tolist()

    numeric_columns = filtered_df.select_dtypes(
        include=["int64", "float64"]
    ).columns.tolist()

    search_text = st.text_input("Search in all columns", key="file_search_text")

    if search_text:

        filtered_df = filtered_df[
            filtered_df.astype(str)
            .apply(
                lambda row: row.str.contains(
                    search_text,
                    case=False,
                    na=False
                ).any(),
                axis=1
            )
        ]

    selected_columns = st.multiselect(
        "Select Columns To Display",
        all_columns,
        default=all_columns,
        key="file_selected_columns"
    )

    if selected_columns:
        filtered_df = filtered_df[selected_columns]

    if categorical_columns:

        category_column = st.selectbox(
            "Select Category Column For Filter",
            ["None"] + categorical_columns,
            key="file_category_column"
        )

        if category_column != "None":

            category_values = uploaded_df[category_column].dropna().unique().tolist()

            selected_values = st.multiselect(
                f"Select values from {category_column}",
                category_values,
                default=category_values,
                key=f"file_category_values_{category_column}"
            )

            if selected_values and category_column in filtered_df.columns:
                filtered_df = filtered_df[
                    filtered_df[category_column].isin(selected_values)
                ]

    if numeric_columns:

        numeric_column = st.selectbox(
            "Select Numeric Column For Range Filter",
            ["None"] + numeric_columns,
            key="file_numeric_column"
        )

        if numeric_column != "None":

            min_value = float(uploaded_df[numeric_column].min())
            max_value = float(uploaded_df[numeric_column].max())

            selected_range = st.slider(
                f"Select range for {numeric_column}",
                min_value,
                max_value,
                (min_value, max_value),
                key=f"file_numeric_range_{numeric_column}"
            )

            if numeric_column in filtered_df.columns:
                filtered_df = filtered_df[
                    (filtered_df[numeric_column] >= selected_range[0])
                    & (filtered_df[numeric_column] <= selected_range[1])
                ]


st.session_state.file_filtered_df = filtered_df


# -------------------------------------------------
# USER QUESTION
# -------------------------------------------------

st.markdown(
    '<div class="section-title">Ask Question About File Data</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="hint-box">
        <b>Example questions:</b><br>
        • Which product category has the highest sales?<br>
        • Which payment method is most used?<br>
        • What are the top customers by revenue?<br>
        • Which rows have missing values?<br>
        • What business improvements can be made?
    </div>
    """,
    unsafe_allow_html=True
)

user_query = st.text_input(
    "Ask question about filtered file data",
    value=st.session_state.file_user_query,
    key="file_user_query_input"
)

st.session_state.file_user_query = user_query


# -------------------------------------------------
# BUTTON ACTIONS
# -------------------------------------------------

if analyze_clicked:

    if filtered_df.empty:
        st.error("Filtered data is empty. Please change filters.")

    else:
        st.session_state.file_analysis_done = True
        st.session_state.file_active_tab = "Results"
        st.success("File analysis completed.")


if summary_clicked:

    if filtered_df.empty:
        st.error("Filtered data is empty. Please change filters.")

    else:
        st.session_state.file_ai_summary = generate_ai_summary(
            client,
            "AI File Business Summary",
            user_query,
            filtered_df,
            st
        )

        st.session_state.file_active_tab = "Summary"
        st.success("AI file summary generated.")


if charts_clicked:

    if filtered_df.empty:
        st.error("Filtered data is empty. Please change filters.")

    else:
        st.session_state.show_file_charts = True
        st.session_state.file_active_tab = "Charts"
        st.success("Charts generated.")


if recommendation_clicked:

    if filtered_df.empty:
        st.error("Filtered data is empty. Please change filters.")

    else:
        st.session_state.file_recommendation_text = generate_recommendation_summary(
            client,
            user_query,
            filtered_df
        )

        st.session_state.file_active_tab = "Insights"
        st.success("File insights generated.")


# -------------------------------------------------
# CUSTOM STABLE WORKSPACE TABS
# -------------------------------------------------

tab1, tab2, tab3, tab4, tab5 = st.columns(5)

if tab1.button("Results", use_container_width=True, key="file_tab_results"):
    st.session_state.file_active_tab = "Results"

if tab2.button("Summary", use_container_width=True, key="file_tab_summary"):
    st.session_state.file_active_tab = "Summary"

if tab3.button("Charts", use_container_width=True, key="file_tab_charts"):
    st.session_state.file_active_tab = "Charts"

if tab4.button("Insights", use_container_width=True, key="file_tab_insights"):
    st.session_state.file_active_tab = "Insights"

if tab5.button("Export", use_container_width=True, key="file_tab_export"):
    st.session_state.file_active_tab = "Export"


# -------------------------------------------------
# RESULTS SECTION
# -------------------------------------------------

if st.session_state.file_active_tab == "Results":

    st.markdown('<div class="section-title">Filtered File Data</div>', unsafe_allow_html=True)

    k1, k2, k3 = st.columns(3)

    with k1:
        st.metric("Filtered Rows", len(filtered_df))

    with k2:
        st.metric("Filtered Columns", len(filtered_df.columns))

    with k3:
        st.metric("Missing Values", int(filtered_df.isnull().sum().sum()))

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

    st.info(
        f"Showing {len(filtered_df)} rows out of {len(uploaded_df)} total rows."
    )


# -------------------------------------------------
# SUMMARY SECTION
# -------------------------------------------------

elif st.session_state.file_active_tab == "Summary":

    st.markdown('<div class="section-title">AI File Business Summary</div>', unsafe_allow_html=True)

    if st.session_state.file_ai_summary:
        st.markdown(
            f"""
            <div class="summary-card">
                {st.session_state.file_ai_summary}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.info("Generate summary to view it here.")


# -------------------------------------------------
# CHARTS SECTION
# -------------------------------------------------

elif st.session_state.file_active_tab == "Charts":

    st.markdown('<div class="section-title">File KPI Cards & Charts</div>', unsafe_allow_html=True)

    if st.session_state.show_file_charts and not filtered_df.empty:

        show_kpi_and_charts(
            filtered_df,
            "File"
        )

    else:
        st.info("Click Charts to view KPI cards and charts here.")


# -------------------------------------------------
# INSIGHTS SECTION
# -------------------------------------------------

elif st.session_state.file_active_tab == "Insights":

    st.markdown('<div class="section-title">File Business Insights</div>', unsafe_allow_html=True)

    if st.session_state.file_recommendation_text:
        st.markdown(
            f"""
            <div class="recommendation-card">
                {st.session_state.file_recommendation_text}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.info("Generate insights to view recommendations here.")


# -------------------------------------------------
# EXPORT SECTION
# -------------------------------------------------

elif st.session_state.file_active_tab == "Export":

    st.markdown('<div class="section-title">Export Filtered File Report</div>', unsafe_allow_html=True)

    if not filtered_df.empty:
        show_download_buttons(
            filtered_df,
            "filtered_file_report",
            "Filtered File Data",
            st.session_state.file_ai_summary
        )
    else:
        st.info("No data available to export.")