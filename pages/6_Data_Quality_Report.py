import streamlit as st
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from groq import Groq
import plotly.express as px

from utils.auth import check_authentication
from utils.style import load_css
from utils.exporter import show_download_buttons
from ai.ai_engine import generate_recommendation_summary


st.set_page_config(
    page_title="Data Quality Report | Power AI",
    page_icon="🧪",
    layout="wide"
)

check_authentication("quality")
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

    .st-key-quality_toolbar {
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


# -------------------------------------------------
# SESSION DEFAULTS
# -------------------------------------------------

defaults = {
    "quality_df": None,
    "quality_source_name": "",
    "quality_report_df": None,
    "quality_summary_text": "",
    "quality_recommendation_text": "",
    "quality_active_tab": "Overview",
    "quality_score": 0,
    "quality_report_done": False,
    "show_quality_charts": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------

def get_available_sources():
    sources = {}

    if "db_result_df" in st.session_state and st.session_state.db_result_df is not None:
        if isinstance(st.session_state.db_result_df, pd.DataFrame) and not st.session_state.db_result_df.empty:
            sources["Database Result"] = st.session_state.db_result_df

    if "file_filtered_df" in st.session_state and st.session_state.file_filtered_df is not None:
        if isinstance(st.session_state.file_filtered_df, pd.DataFrame) and not st.session_state.file_filtered_df.empty:
            sources["File Data"] = st.session_state.file_filtered_df

    if "mongo_df" in st.session_state and st.session_state.mongo_df is not None:
        if isinstance(st.session_state.mongo_df, pd.DataFrame) and not st.session_state.mongo_df.empty:
            sources["MongoDB Data"] = st.session_state.mongo_df

    if "integrated_df" in st.session_state and st.session_state.integrated_df is not None:
        if isinstance(st.session_state.integrated_df, pd.DataFrame) and not st.session_state.integrated_df.empty:
            sources["Integrated Data"] = st.session_state.integrated_df

    return sources


def detect_outliers_iqr(series):
    numeric_series = pd.to_numeric(series, errors="coerce").dropna()

    if len(numeric_series) < 5:
        return 0

    q1 = numeric_series.quantile(0.25)
    q3 = numeric_series.quantile(0.75)
    iqr = q3 - q1

    if iqr == 0:
        return 0

    lower = q1 - (1.5 * iqr)
    upper = q3 + (1.5 * iqr)

    return int(((numeric_series < lower) | (numeric_series > upper)).sum())


def generate_quality_report(df):
    total_rows = len(df)
    total_columns = len(df.columns)
    total_cells = max(total_rows * total_columns, 1)

    missing_values = int(df.isnull().sum().sum())
    missing_percent = round((missing_values / total_cells) * 100, 2)

    duplicate_rows = int(df.duplicated().sum())
    duplicate_percent = round((duplicate_rows / max(total_rows, 1)) * 100, 2)

    numeric_columns = df.select_dtypes(include=["int64", "float64", "int32", "float32"]).columns.tolist()
    text_columns = df.select_dtypes(include=["object", "string"]).columns.tolist()
    datetime_columns = df.select_dtypes(include=["datetime64[ns]", "datetime64"]).columns.tolist()

    outlier_counts = {}
    total_outliers = 0
    for col in numeric_columns:
        count = detect_outliers_iqr(df[col])
        outlier_counts[col] = count
        total_outliers += count

    outlier_percent = round((total_outliers / max(total_rows * max(len(numeric_columns), 1), 1)) * 100, 2)

    column_report = []

    for col in df.columns:
        missing_count = int(df[col].isnull().sum())
        missing_col_percent = round((missing_count / max(total_rows, 1)) * 100, 2)
        unique_count = int(df[col].nunique(dropna=True))
        unique_percent = round((unique_count / max(total_rows, 1)) * 100, 2)
        dtype = str(df[col].dtype)
        outliers = outlier_counts.get(col, 0)

        if missing_col_percent == 0 and outliers == 0:
            status = "Good"
        elif missing_col_percent <= 10 and outliers <= max(total_rows * 0.05, 1):
            status = "Needs Review"
        else:
            status = "Poor"

        column_report.append({
            "Column": col,
            "Data Type": dtype,
            "Missing Values": missing_count,
            "Missing %": missing_col_percent,
            "Unique Values": unique_count,
            "Unique %": unique_percent,
            "Outliers": outliers,
            "Status": status
        })

    report_df = pd.DataFrame(column_report)

    score = 100
    score -= min(missing_percent * 1.2, 35)
    score -= min(duplicate_percent * 1.0, 25)
    score -= min(outlier_percent * 1.0, 20)

    poor_columns = int((report_df["Status"] == "Poor").sum()) if not report_df.empty else 0
    poor_column_percent = round((poor_columns / max(total_columns, 1)) * 100, 2)
    score -= min(poor_column_percent * 0.4, 15)

    score = int(max(min(score, 100), 0))

    if score >= 90:
        grade = "Excellent"
    elif score >= 80:
        grade = "Good"
    elif score >= 70:
        grade = "Average"
    elif score >= 50:
        grade = "Needs Cleaning"
    else:
        grade = "Poor"

    summary = {
        "Total Rows": total_rows,
        "Total Columns": total_columns,
        "Missing Values": missing_values,
        "Missing %": missing_percent,
        "Duplicate Rows": duplicate_rows,
        "Duplicate %": duplicate_percent,
        "Numeric Columns": len(numeric_columns),
        "Text Columns": len(text_columns),
        "Datetime Columns": len(datetime_columns),
        "Total Outliers": total_outliers,
        "Outlier %": outlier_percent,
        "Poor Columns": poor_columns,
        "Quality Score": score,
        "Quality Grade": grade,
    }

    return summary, report_df


def build_quality_summary_text(source_name, summary):
    return f"""
Data Source: {source_name}

Overall Quality Grade: {summary['Quality Grade']}
Quality Score: {summary['Quality Score']}/100

Dataset Size:
- Rows: {summary['Total Rows']}
- Columns: {summary['Total Columns']}

Issues Found:
- Missing Values: {summary['Missing Values']} ({summary['Missing %']}%)
- Duplicate Rows: {summary['Duplicate Rows']} ({summary['Duplicate %']}%)
- Total Outliers: {summary['Total Outliers']} ({summary['Outlier %']}%)
- Poor Quality Columns: {summary['Poor Columns']}

Column Types:
- Numeric Columns: {summary['Numeric Columns']}
- Text Columns: {summary['Text Columns']}
- Datetime Columns: {summary['Datetime Columns']}
"""


def generate_ai_quality_recommendations(df, source_name, summary, report_df):
    try:
        report_sample = report_df.head(25).to_string(index=False)
        prompt_df = pd.DataFrame([summary])
        prompt_df["Source"] = source_name

        prompt = f"""
You are Power AI, an enterprise data quality analyst.

Analyze the data quality report and give clear business-friendly recommendations.

Data Source: {source_name}

Quality Summary:
{prompt_df.to_string(index=False)}

Column Quality Sample:
{report_sample}

Rules:
- Explain whether the data is safe for analytics.
- Mention missing values, duplicates, and outliers.
- Give practical cleaning steps.
- Keep the answer structured and simple.
- Do not invent columns that are not shown.
"""

        return generate_recommendation_summary(client, prompt, df.head(100))

    except Exception as e:
        return f"AI recommendation generation failed: {e}"


# -------------------------------------------------
# STATUS VALUES
# -------------------------------------------------

current_rows = len(st.session_state.quality_df) if isinstance(st.session_state.quality_df, pd.DataFrame) else 0
current_cols = len(st.session_state.quality_df.columns) if isinstance(st.session_state.quality_df, pd.DataFrame) else 0
current_score = st.session_state.quality_score


# -------------------------------------------------
# FIXED RIBBON
# -------------------------------------------------

with st.container(key="quality_toolbar"):

    st.markdown(
        f"""
        <div class="ribbon-title">
            🧪 DATA QUALITY REPORT
            <span>QUALITY ENGINE</span>
            &nbsp; | &nbsp; ROWS: {current_rows}
            &nbsp; | &nbsp; COLUMNS: {current_cols}
            &nbsp; | &nbsp; SCORE: {current_score}/100
        </div>
        """,
        unsafe_allow_html=True
    )

    g1, g2, g3 = st.columns([3, 3, 2])

    with g1:
        st.markdown('<div class="ribbon-group-title">DATA</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)

        with c1:
            load_clicked = st.button("Load", use_container_width=True, key="quality_load_btn")

        with c2:
            report_clicked = st.button("Report", use_container_width=True, key="quality_report_btn")

        with c3:
            clear_clicked = st.button("Clear", use_container_width=True, key="quality_clear_btn")

    with g2:
        st.markdown('<div class="ribbon-group-title">AI ENGINE</div>', unsafe_allow_html=True)
        c4, c5 = st.columns(2)

        with c4:
            ai_clicked = st.button("AI Summary", use_container_width=True, key="quality_ai_btn")

        with c5:
            reset_clicked = st.button("Reset", use_container_width=True, key="quality_reset_btn")

    with g3:
        st.markdown('<div class="ribbon-group-title">ANALYTICS</div>', unsafe_allow_html=True)
        c6, c7 = st.columns(2)

        with c6:
            charts_clicked = st.button("Charts", use_container_width=True, key="quality_charts_btn")

        with c7:
            export_clicked = st.button("Export", use_container_width=True, key="quality_export_btn")


# -------------------------------------------------
# HEADER
# -------------------------------------------------

st.markdown(
    """
    <div class="page-header">
        <h1>🧪 AI Data Quality Report</h1>
        <p>Check whether your data is clean, reliable, and safe for analytics before generating business insights.</p>
    </div>
    """,
    unsafe_allow_html=True
)


# -------------------------------------------------
# BUTTON ACTIONS
# -------------------------------------------------

if reset_clicked:
    st.session_state.quality_summary_text = ""
    st.session_state.quality_recommendation_text = ""
    st.session_state.show_quality_charts = False
    st.session_state.quality_active_tab = "Overview"
    st.success("Quality report view reset.")
    st.rerun()

if clear_clicked:
    st.session_state.quality_df = None
    st.session_state.quality_source_name = ""
    st.session_state.quality_report_df = None
    st.session_state.quality_summary_text = ""
    st.session_state.quality_recommendation_text = ""
    st.session_state.quality_active_tab = "Overview"
    st.session_state.quality_score = 0
    st.session_state.quality_report_done = False
    st.session_state.show_quality_charts = False
    st.success("Quality data cleared.")
    st.rerun()


# -------------------------------------------------
# DATA SOURCE SELECTION
# -------------------------------------------------

st.markdown('<div class="section-title">Select Data Source</div>', unsafe_allow_html=True)

sources = get_available_sources()

if not sources:
    st.warning("No data found. First run Database Analytics, File Analytics, MongoDB Analytics, or Integrated Analytics.")
    st.stop()

selected_source = st.selectbox(
    "Choose data source for quality check",
    list(sources.keys()),
    key="quality_source_select"
)

selected_df = sources[selected_source]

if load_clicked or st.session_state.quality_df is None:
    st.session_state.quality_df = selected_df.copy()
    st.session_state.quality_source_name = selected_source
    st.session_state.quality_active_tab = "Overview"
    st.success(f"{selected_source} loaded for quality check.")

quality_df = st.session_state.quality_df
source_name = st.session_state.quality_source_name or selected_source


# -------------------------------------------------
# DATA PREVIEW
# -------------------------------------------------

st.markdown('<div class="section-title">Dataset Preview</div>', unsafe_allow_html=True)

p1, p2, p3 = st.columns(3)

with p1:
    st.metric("Rows", len(quality_df))

with p2:
    st.metric("Columns", len(quality_df.columns))

with p3:
    st.metric("Source", source_name)

st.dataframe(quality_df.head(1000), use_container_width=True)
st.info(f"Previewing first 1000 rows out of {len(quality_df)} total rows.")


# -------------------------------------------------
# GENERATE REPORT
# -------------------------------------------------

if report_clicked:
    summary, report_df = generate_quality_report(quality_df)
    st.session_state.quality_report_df = report_df
    st.session_state.quality_score = summary["Quality Score"]
    st.session_state.quality_summary_text = build_quality_summary_text(source_name, summary)
    st.session_state.quality_report_done = True
    st.session_state.quality_active_tab = "Overview"
    st.success("Data quality report generated.")
    st.rerun()

if ai_clicked:
    if st.session_state.quality_report_df is None:
        summary, report_df = generate_quality_report(quality_df)
        st.session_state.quality_report_df = report_df
        st.session_state.quality_score = summary["Quality Score"]
        st.session_state.quality_summary_text = build_quality_summary_text(source_name, summary)
        st.session_state.quality_report_done = True
    else:
        summary, _ = generate_quality_report(quality_df)
        report_df = st.session_state.quality_report_df

    st.session_state.quality_recommendation_text = generate_ai_quality_recommendations(
        quality_df,
        source_name,
        summary,
        report_df
    )
    st.session_state.quality_active_tab = "AI Summary"
    st.success("AI quality summary generated.")

if charts_clicked:
    if st.session_state.quality_report_df is None:
        summary, report_df = generate_quality_report(quality_df)
        st.session_state.quality_report_df = report_df
        st.session_state.quality_score = summary["Quality Score"]
        st.session_state.quality_summary_text = build_quality_summary_text(source_name, summary)
        st.session_state.quality_report_done = True
    st.session_state.show_quality_charts = True
    st.session_state.quality_active_tab = "Charts"
    st.success("Quality charts generated.")

if export_clicked:
    st.session_state.quality_active_tab = "Export"


# -------------------------------------------------
# STABLE WORKSPACE TABS
# -------------------------------------------------

st.markdown('<div class="section-title">Quality Workspace</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.columns(4)

if tab1.button("Overview", use_container_width=True, key="quality_tab_overview"):
    st.session_state.quality_active_tab = "Overview"

if tab2.button("Columns", use_container_width=True, key="quality_tab_columns"):
    st.session_state.quality_active_tab = "Columns"

if tab3.button("Charts", use_container_width=True, key="quality_tab_charts"):
    st.session_state.quality_active_tab = "Charts"

if tab4.button("AI Summary", use_container_width=True, key="quality_tab_ai"):
    st.session_state.quality_active_tab = "AI Summary"


# -------------------------------------------------
# OVERVIEW TAB
# -------------------------------------------------

if st.session_state.quality_active_tab == "Overview":

    st.markdown('<div class="section-title">Quality Overview</div>', unsafe_allow_html=True)

    if st.session_state.quality_report_df is None:
        st.info("Click Report to generate data quality score and issue summary.")
    else:
        summary, _ = generate_quality_report(quality_df)

        q1, q2, q3, q4 = st.columns(4)

        with q1:
            st.metric("Quality Score", f"{summary['Quality Score']}/100")

        with q2:
            st.metric("Grade", summary["Quality Grade"])

        with q3:
            st.metric("Missing Values", summary["Missing Values"])

        with q4:
            st.metric("Duplicate Rows", summary["Duplicate Rows"])

        q5, q6, q7, q8 = st.columns(4)

        with q5:
            st.metric("Outliers", summary["Total Outliers"])

        with q6:
            st.metric("Numeric Columns", summary["Numeric Columns"])

        with q7:
            st.metric("Text Columns", summary["Text Columns"])

        with q8:
            st.metric("Poor Columns", summary["Poor Columns"])

        st.markdown(
            f"""
            <div class="summary-card">
                {st.session_state.quality_summary_text}
            </div>
            """,
            unsafe_allow_html=True
        )


# -------------------------------------------------
# COLUMNS TAB
# -------------------------------------------------

elif st.session_state.quality_active_tab == "Columns":

    st.markdown('<div class="section-title">Column Quality Details</div>', unsafe_allow_html=True)

    if st.session_state.quality_report_df is None:
        st.info("Generate report to view column quality details.")
    else:
        st.dataframe(st.session_state.quality_report_df, use_container_width=True)


# -------------------------------------------------
# CHARTS TAB
# -------------------------------------------------

elif st.session_state.quality_active_tab == "Charts":

    st.markdown('<div class="section-title">Quality Charts</div>', unsafe_allow_html=True)

    if st.session_state.quality_report_df is None:
        st.info("Generate report or click Charts to view quality visualizations.")
    else:
        report_df = st.session_state.quality_report_df

        missing_chart_df = report_df[report_df["Missing Values"] > 0].sort_values(
            "Missing Values",
            ascending=False
        ).head(20)

        if not missing_chart_df.empty:
            fig_missing = px.bar(
                missing_chart_df,
                x="Column",
                y="Missing Values",
                title="Top Missing Values by Column"
            )
            st.plotly_chart(fig_missing, use_container_width=True)
        else:
            st.success("No missing values found.")

        type_counts = report_df["Data Type"].value_counts().reset_index()
        type_counts.columns = ["Data Type", "Count"]

        fig_types = px.pie(
            type_counts,
            names="Data Type",
            values="Count",
            title="Data Type Distribution"
        )
        st.plotly_chart(fig_types, use_container_width=True)

        outlier_chart_df = report_df[report_df["Outliers"] > 0].sort_values(
            "Outliers",
            ascending=False
        ).head(20)

        if not outlier_chart_df.empty:
            fig_outliers = px.bar(
                outlier_chart_df,
                x="Column",
                y="Outliers",
                title="Outliers by Numeric Column"
            )
            st.plotly_chart(fig_outliers, use_container_width=True)
        else:
            st.success("No numeric outliers detected.")


# -------------------------------------------------
# AI SUMMARY TAB
# -------------------------------------------------

elif st.session_state.quality_active_tab == "AI Summary":

    st.markdown('<div class="section-title">AI Quality Summary & Recommendations</div>', unsafe_allow_html=True)

    if st.session_state.quality_recommendation_text:
        st.markdown(
            f"""
            <div class="recommendation-card">
                {st.session_state.quality_recommendation_text}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.info("Click AI Summary to generate quality recommendations.")


# -------------------------------------------------
# EXPORT SECTION
# -------------------------------------------------

if st.session_state.quality_active_tab == "Export":

    st.markdown('<div class="section-title">Export Quality Report</div>', unsafe_allow_html=True)

    if st.session_state.quality_report_df is not None:
        export_df = st.session_state.quality_report_df.copy()
        show_download_buttons(
            export_df,
            "data_quality_report",
            "Data Quality Report",
            st.session_state.quality_summary_text
        )
    else:
        st.info("Generate report first to export data quality report.")
