import streamlit as st
import pandas as pd
from groq import Groq
import os
from dotenv import load_dotenv

from utils.auth import check_authentication
from utils.style import load_css
from database.mysql_connection import get_mysql_engine, get_database_schema
from utils.cleaner import clean_dataframe_columns
from utils.exporter import show_download_buttons
from utils.charts import show_kpi_and_charts
from ai.ai_engine import (
    generate_ai_summary,
    generate_recommendation_summary,
    fix_sql_with_ai,
    explain_sql_with_ai,
    classify_user_intent
)


st.set_page_config(
    page_title="Database Analytics | Power AI",
    page_icon="📊",
    layout="wide"
)

check_authentication("database")
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

    .st-key-db_toolbar {
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
    .stSelectbox label {
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

    pre, code {
        background-color: #020617 !important;
        color: #E5E7EB !important;
        border-radius: 12px !important;
    }

    [data-testid="stDataFrame"] {
        background: #111827 !important;
        border-radius: 14px !important;
    }

    [data-testid="stAlert"] {
        border-radius: 12px !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #111827;
        padding: 8px;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.10);
    }

    .stTabs [data-baseweb="tab"] {
        color: #E5E7EB;
        background: #0B1020;
        border-radius: 10px;
        padding: 8px 14px;
        font-weight: 700;
    }

    .stTabs [aria-selected="true"] {
        background: #2563EB !important;
        color: #FFFFFF !important;
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
    "mysql_connected": False,
    "mysql_engine": None,
    "mysql_host": "localhost",
    "mysql_user": "root",
    "mysql_password": "",
    "selected_db": "power_ai",
    "schema_text": "",
    "db_user_query": "",
    "db_sql_query": "",
    "db_editable_sql": "",
    "db_result_df": None,
    "db_ai_summary": "",
    "show_db_charts": False,
    "db_error_message": "",
    "db_sql_explanation": "",
    "recommendation_text": "",
    "chat_history": [],
    "show_change_db_form": False,
    "show_schema_panel": False
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def is_safe_select_query(sql_query):
    sql_lower = sql_query.strip().lower()

    blocked_words = [
        "update", "delete", "drop", "insert",
        "alter", "truncate", "create", "replace"
    ]

    if not sql_lower.startswith("select"):
        return False

    if any(word in sql_lower for word in blocked_words):
        return False

    return True


if not st.session_state.mysql_connected:

    st.markdown(
        """
        <div class="page-header">
            <h1>Database Analytics</h1>
            <p>AI-powered SQL business intelligence workflow for MySQL analytics.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">Database Connection</div>',
        unsafe_allow_html=True
    )

    with st.form("mysql_connection_form"):

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            mysql_host = st.text_input(
                "MySQL Host",
                value=st.session_state.mysql_host
            )

        with col2:
            mysql_user = st.text_input(
                "MySQL Username",
                value=st.session_state.mysql_user
            )

        with col3:
            mysql_password = st.text_input(
                "MySQL Password",
                type="password",
                value=st.session_state.mysql_password
            )

        with col4:
            selected_db = st.text_input(
                "Database Name",
                value=st.session_state.selected_db
            )

        connect_clicked = st.form_submit_button("Connect Database")

    if connect_clicked:
        try:
            engine = get_mysql_engine(
                mysql_user,
                mysql_password,
                mysql_host,
                selected_db
            )

            schema_text = get_database_schema(engine)

            st.session_state.mysql_engine = engine
            st.session_state.mysql_host = mysql_host
            st.session_state.mysql_user = mysql_user
            st.session_state.mysql_password = mysql_password
            st.session_state.selected_db = selected_db
            st.session_state.schema_text = schema_text
            st.session_state.mysql_connected = True

            st.session_state.db_sql_query = ""
            st.session_state.db_editable_sql = ""
            st.session_state.db_result_df = None
            st.session_state.db_ai_summary = ""
            st.session_state.show_db_charts = False
            st.session_state.db_error_message = ""
            st.session_state.db_sql_explanation = ""

            st.success("Database connected successfully.")
            st.rerun()

        except Exception as e:
            st.session_state.mysql_connected = False
            st.session_state.mysql_engine = None
            st.error(f"Database Connection Error: {e}")

    st.info("Please connect your MySQL database first.")
    st.stop()


try:
    if st.session_state.mysql_engine is None:
        st.session_state.mysql_engine = get_mysql_engine(
            st.session_state.mysql_user,
            st.session_state.mysql_password,
            st.session_state.mysql_host,
            st.session_state.selected_db
        )

    engine = st.session_state.mysql_engine
    schema_text = st.session_state.schema_text

except Exception as e:
    st.session_state.mysql_connected = False
    st.session_state.mysql_engine = None
    st.error(f"Database Engine Error: {e}")
    st.stop()


with st.container(key="db_toolbar"):

    st.markdown(
        f"""
        <div class="ribbon-title">
            ◫ DATABASE ANALYTICS
            <span>CONNECTED</span>
            &nbsp; | &nbsp; DB: {st.session_state.selected_db}
            &nbsp; | &nbsp; HOST: {st.session_state.mysql_host}
        </div>
        """,
        unsafe_allow_html=True
    )

    g1, g2, g3 = st.columns([3, 3, 2])

    with g1:
        st.markdown('<div class="ribbon-group-title">DATABASE</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)

        with c1:
            if st.button("Change DB", use_container_width=True):
                st.session_state.show_change_db_form = not st.session_state.show_change_db_form

        with c2:
            if st.button("Schema", use_container_width=True):
                st.session_state.show_schema_panel = not st.session_state.show_schema_panel

        with c3:
            disconnect_clicked = st.button("Disconnect", use_container_width=True)

    with g2:
        st.markdown('<div class="ribbon-group-title">AI ENGINE</div>', unsafe_allow_html=True)

        c4, c5, c6 = st.columns(3)

        with c4:
            generate_sql_clicked = st.button("Generate SQL", use_container_width=True)

        with c5:
            run_query_clicked = st.button("Run Query", use_container_width=True)

        with c6:
            summary_clicked = st.button("Summary", use_container_width=True)

    with g3:
        st.markdown('<div class="ribbon-group-title">ANALYTICS</div>', unsafe_allow_html=True)

        c7, c8 = st.columns(2)

        with c7:
            charts_clicked = st.button("Charts", use_container_width=True)

        with c8:
            recommendation_clicked = st.button("Insights", use_container_width=True)


if disconnect_clicked:
    st.session_state.mysql_connected = False
    st.session_state.mysql_engine = None
    st.session_state.schema_text = ""
    st.session_state.db_sql_query = ""
    st.session_state.db_editable_sql = ""
    st.session_state.db_result_df = None
    st.session_state.db_ai_summary = ""
    st.session_state.show_db_charts = False
    st.session_state.db_error_message = ""
    st.session_state.db_sql_explanation = ""

    st.success("Database disconnected.")
    st.rerun()


if st.session_state.show_change_db_form:
    with st.form("change_mysql_connection_form"):

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            new_mysql_host = st.text_input(
                "MySQL Host",
                value=st.session_state.mysql_host,
                key="change_mysql_host"
            )

        with col2:
            new_mysql_user = st.text_input(
                "MySQL Username",
                value=st.session_state.mysql_user,
                key="change_mysql_user"
            )

        with col3:
            new_mysql_password = st.text_input(
                "MySQL Password",
                type="password",
                value=st.session_state.mysql_password,
                key="change_mysql_password"
            )

        with col4:
            new_selected_db = st.text_input(
                "Database Name",
                value=st.session_state.selected_db,
                key="change_selected_db"
            )

        reconnect_clicked = st.form_submit_button("Reconnect Database")

    if reconnect_clicked:
        try:
            engine = get_mysql_engine(
                new_mysql_user,
                new_mysql_password,
                new_mysql_host,
                new_selected_db
            )

            schema_text = get_database_schema(engine)

            st.session_state.mysql_engine = engine
            st.session_state.mysql_host = new_mysql_host
            st.session_state.mysql_user = new_mysql_user
            st.session_state.mysql_password = new_mysql_password
            st.session_state.selected_db = new_selected_db
            st.session_state.schema_text = schema_text
            st.session_state.mysql_connected = True

            st.session_state.db_sql_query = ""
            st.session_state.db_editable_sql = ""
            st.session_state.db_result_df = None
            st.session_state.db_ai_summary = ""
            st.session_state.show_db_charts = False
            st.session_state.db_error_message = ""
            st.session_state.db_sql_explanation = ""

            st.session_state.show_change_db_form = False

            st.success("Database reconnected successfully.")
            st.rerun()

        except Exception as e:
            st.error(f"Reconnect Error: {e}")


if st.session_state.show_schema_panel:
    st.markdown('<div class="section-title">Database Schema</div>', unsafe_allow_html=True)
    st.code(schema_text)


st.markdown(
    '<div class="section-title">Ask Business Question</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="hint-box">
        <b>Example questions:</b><br>
        • Total revenue by category<br>
        • Monthly sales trend<br>
        • Top 10 customers by revenue<br>
        • Products hurting profitability<br>
        • Which category should management focus on?
    </div>
    """,
    unsafe_allow_html=True
)

user_query = st.text_input(
    "Enter your business question",
    value=st.session_state.db_user_query,
    key="database_user_question_input"
)

st.session_state.db_user_query = user_query


if generate_sql_clicked:

    if not user_query:
        st.error("Please enter a business question.")

    else:
        try:
            intent = classify_user_intent(user_query)
            st.info(f"Detected Intent: {intent}")

            if intent == "TREND_ANALYSIS":

                sql_prompt = f"""
You are an expert Business Intelligence SQL Generator.

Rules:
- Only SELECT queries
- Trend queries must be chronological
- Monthly trends:
    GROUP BY YEAR(date), MONTH(date)
    ORDER BY YEAR(date), MONTH(date)
- Yearly trends:
    GROUP BY YEAR(date)
    ORDER BY YEAR(date)
- Never order trend queries by revenue DESC
- Never order trend queries by profit DESC
- Return only SQL

Database Schema:
{schema_text}

User Question:
{user_query}
"""

            elif intent == "RECOMMENDATION":

                sql_prompt = f"""
You are an expert Business Intelligence Recommendation SQL Generator.

Convert the user question into ONLY a valid MySQL SELECT query.

Goal:
Find business problems, weak areas, low profit, low margin, high sales with low profit, or underperforming areas.

Rules:
- Only SELECT queries
- Never generate UPDATE, DELETE, DROP, INSERT
- Return only SQL
- No markdown
- No explanation
- Use only tables and columns from this schema

Recommendation Query Rules:
- For profitability questions, include revenue, profit, and profit margin.
- For "hurting profitability", find low profit margin products or categories.
- For "management focus", find weak categories/products using profit margin ASC.
- For "improve profit", show revenue, profit, quantity, and profit margin.
- Profit Margin = SUM(profit) / SUM(total_amount) * 100.
- Sort weak areas by profit_margin ASC or profit ASC.

Current Database:
{st.session_state.selected_db}

Database Schema:
{schema_text}

User Question:
{user_query}
"""

            else:

                sql_prompt = f"""
You are a professional MySQL SQL generator.

Rules:
- Only SELECT queries
- Never generate UPDATE, DELETE, DROP, INSERT
- Return only SQL
- No markdown
- No explanation
- Use only tables and columns from this schema

KPI Formula Rules:
- Average Order Value means:
  First calculate order total using SUM(total_amount) GROUP BY order_id,
  then calculate AVG(order_total).

- Profit Margin means:
  SUM(profit) / SUM(total_amount) * 100.
  Do not rank profit margin using only SUM(profit).

- Growth Rate means:
  (current period value - previous period value) / previous period value * 100.

- Revenue Contribution means:
  grouped revenue / total revenue * 100.

Database Schema:
{schema_text}

User Question:
{user_query}
"""

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": sql_prompt
                    }
                ]
            )

            sql_query = response.choices[0].message.content
            sql_query = sql_query.replace("```sql", "")
            sql_query = sql_query.replace("```", "")
            sql_query = sql_query.strip()

            st.session_state.db_sql_query = sql_query
            st.session_state.db_editable_sql = sql_query

            st.session_state.db_sql_explanation = explain_sql_with_ai(
                client,
                sql_query,
                user_query
            )

            st.session_state.db_result_df = None
            st.session_state.db_ai_summary = ""
            st.session_state.show_db_charts = False
            st.session_state.db_error_message = ""

            st.session_state.chat_history.append(
                {
                    "role": "user",
                    "message": user_query
                }
            )

            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "message": sql_query
                }
            )

            st.success("SQL generated successfully. Open the SQL tab, review or edit, then run query.")

        except Exception as e:
            st.error(f"SQL Generation Error: {e}")


if run_query_clicked:

    sql_to_run = st.session_state.get(
        "db_editable_sql",
        st.session_state.db_sql_query
    ).strip()

    if not sql_to_run:
        st.error("Please generate or enter SQL first.")

    elif not is_safe_select_query(sql_to_run):
        st.error("Only safe SELECT queries are allowed. UPDATE, DELETE, DROP, INSERT, ALTER, CREATE are blocked.")

    else:
        try:
            st.session_state.db_sql_query = sql_to_run

            df = pd.read_sql(
                sql_to_run,
                engine
            )

            df = clean_dataframe_columns(df)

            st.session_state.db_result_df = df
            st.session_state.db_ai_summary = ""
            st.session_state.show_db_charts = False
            st.session_state.db_error_message = ""

            st.success("Query executed successfully. Open the Results tab.")

        except Exception as e:
            st.session_state.db_error_message = str(e)
            st.error(f"Query Execution Error: {e}")


if summary_clicked:

    if st.session_state.db_result_df is None:
        st.error("Please run the query first.")

    else:
        st.session_state.db_ai_summary = generate_ai_summary(
            client,
            "AI Business Summary",
            st.session_state.db_user_query,
            st.session_state.db_result_df,
            st
        )

        st.success("AI summary generated. Open the Summary tab.")


if charts_clicked:

    if st.session_state.db_result_df is None:
        st.error("Please run the query first.")

    else:
        st.session_state.show_db_charts = True
        st.success("Charts enabled. Open the Charts tab.")


if recommendation_clicked:

    if st.session_state.db_result_df is None:
        st.error("Please run query first.")

    else:
        st.session_state.recommendation_text = generate_recommendation_summary(
            client,
            st.session_state.db_user_query,
            st.session_state.db_result_df
        )

        st.success("Business insights generated. Open the Insights tab.")


if st.session_state.db_error_message:

    st.warning("SQL query failed. You can ask AI to fix it.")

    if st.button("Fix SQL with AI"):

        fixed_sql = fix_sql_with_ai(
            client,
            st.session_state.db_sql_query,
            st.session_state.db_error_message,
            schema_text,
            st.session_state.db_user_query
        )

        if fixed_sql:
            fixed_sql = fixed_sql.replace("```sql", "")
            fixed_sql = fixed_sql.replace("```", "")
            fixed_sql = fixed_sql.strip()

            st.session_state.db_sql_query = fixed_sql
            st.session_state.db_editable_sql = fixed_sql

            st.session_state.db_sql_explanation = explain_sql_with_ai(
                client,
                fixed_sql,
                st.session_state.db_user_query
            )

            st.session_state.db_error_message = ""
            st.session_state.db_result_df = None
            st.session_state.db_ai_summary = ""
            st.session_state.show_db_charts = False

            st.success("SQL fixed by AI. Open the SQL tab, review/edit, and run again.")
            st.rerun()

        else:
            st.error("AI could not fix the SQL.")


sql_tab, results_tab, summary_tab, charts_tab, insights_tab, export_tab = st.tabs(
    [
        "SQL",
        "Results",
        "Summary",
        "Charts",
        "Insights",
        "Export"
    ]
)


with sql_tab:

    st.markdown('<div class="section-title">Generated / Editable SQL</div>', unsafe_allow_html=True)

    if st.session_state.db_sql_query:

        st.session_state.db_editable_sql = st.text_area(
            "Review and Edit SQL Before Running",
            value=st.session_state.get("db_editable_sql", st.session_state.db_sql_query),
            height=220,
            key="db_editable_sql_box"
        )

        st.info("You can edit the SQL query here. Only SELECT queries are allowed for safety.")

        st.code(
            st.session_state.db_editable_sql,
            language="sql"
        )

    else:
        st.info("Generate SQL to view and edit it here.")

    if st.session_state.db_sql_explanation:
        st.markdown('<div class="section-title">SQL Explanation</div>', unsafe_allow_html=True)
        st.info(st.session_state.db_sql_explanation)


with results_tab:

    st.markdown('<div class="section-title">Database Results</div>', unsafe_allow_html=True)

    if st.session_state.db_result_df is not None:

        result_df = st.session_state.db_result_df

        r1, r2 = st.columns(2)

        with r1:
            st.metric("Rows Returned", len(result_df))

        with r2:
            st.metric("Columns Returned", len(result_df.columns))

        st.dataframe(
            result_df,
            use_container_width=True
        )

    else:
        st.info("Run query to view results here.")


with summary_tab:

    st.markdown('<div class="section-title">AI Business Summary</div>', unsafe_allow_html=True)

    if st.session_state.db_ai_summary:
        st.markdown(
            f"""
            <div class="summary-card">
                {st.session_state.db_ai_summary}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.info("Generate summary to view it here.")


with charts_tab:

    st.markdown('<div class="section-title">Charts</div>', unsafe_allow_html=True)

    if st.session_state.show_db_charts and st.session_state.db_result_df is not None:
        show_kpi_and_charts(
            st.session_state.db_result_df,
            "Database"
        )
    else:
        st.info("Run query and click Charts to view charts here.")


with insights_tab:

    st.markdown('<div class="section-title">Business Insights</div>', unsafe_allow_html=True)

    if st.session_state.recommendation_text:
        st.markdown(
            f"""
            <div class="recommendation-card">
                {st.session_state.recommendation_text}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.info("Generate insights to view recommendations here.")


with export_tab:

    st.markdown('<div class="section-title">Export Report</div>', unsafe_allow_html=True)

    if st.session_state.db_result_df is not None:
        show_download_buttons(
            st.session_state.db_result_df,
            "database_results",
            "Database Results",
            st.session_state.db_ai_summary
        )
    else:
        st.info("Run query first to enable export.")