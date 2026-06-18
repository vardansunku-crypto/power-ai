import ast
import os

from dotenv import load_dotenv
from groq import Groq


# -------------------------------------------------
# AI SUMMARY GENERATOR
# -------------------------------------------------

def generate_ai_summary(
    client,
    title,
    user_query,
    dataframe,
    st
):

    try:

        if dataframe is None or dataframe.empty:
            return "No data available for AI summary."

        limited_df = dataframe.head(30)

        summary_prompt = f"""
You are a professional business intelligence analyst.

Analyze the business data and generate a professional report.

User Question:
{user_query}

Data:
{limited_df.to_string()}

Generate output in this exact format:

Overview:
Write 2 short lines explaining the business data.

Key Insights:
- Write insight 1
- Write insight 2
- Write insight 3

Business Recommendations:
- Write recommendation 1
- Write recommendation 2

Rules:
- Use simple business English
- Keep response short and professional
- Do not use markdown symbols
- Do not use ** symbols
- Do not generate long paragraphs
- Focus on trends and business meaning
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": summary_prompt
                }
            ]
        )

        ai_summary = response.choices[0].message.content

        return ai_summary

    except Exception as error:

        st.error(f"AI Summary Error: {error}")

        return "Unable to generate AI summary."


# -------------------------------------------------
# AI COLUMN MAPPING
# -------------------------------------------------

def get_ai_column_mapping(
    db_columns,
    file_columns,
    client
):

    mapping_prompt = f"""
You are a data integration assistant.

Match uploaded file columns to database columns.

Database Columns:
{db_columns}

Uploaded File Columns:
{file_columns}

Return ONLY a Python dictionary where:
- key = uploaded file column
- value = database column

Example:
{{
    "item_name": "product_name",
    "sales_amount": "revenue"
}}

Do not explain.
Do not use markdown.
"""

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": mapping_prompt
                }
            ]
        )

        mapping_text = response.choices[0].message.content

        mapping_text = mapping_text.replace("```python", "")
        mapping_text = mapping_text.replace("```json", "")
        mapping_text = mapping_text.replace("```", "")
        mapping_text = mapping_text.strip()

        mapping = ast.literal_eval(mapping_text)

        if isinstance(mapping, dict):
            return mapping

        return {}

    except Exception:
        return {}
# -------------------------------------------------
# AI SQL AUTO FIX
# -------------------------------------------------

def fix_sql_with_ai(
    client,
    original_sql,
    error_message,
    schema_text,
    user_query
):

    try:

        fix_prompt = f"""
You are a MySQL SQL expert.

User Question:
{user_query}

Database Schema:
{schema_text}

Failed SQL:
{original_sql}

Error:
{error_message}

Fix the SQL query.

Rules:
- Return only corrected SELECT query
- No explanation
- No markdown
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": fix_prompt
                }
            ]
        )

        fixed_sql = response.choices[0].message.content

        fixed_sql = fixed_sql.replace(
            "```sql",
            ""
        )

        fixed_sql = fixed_sql.replace(
            "```",
            ""
        )

        return fixed_sql.strip()

    except Exception:

        return ""
# -------------------------------------------------
# SQL EXPLANATION ENGINE
# -------------------------------------------------

def explain_sql_with_ai(
    client,
    sql_query,
    user_query
):

    try:

        explanation_prompt = f"""
You are a business intelligence expert.

User Question:
{user_query}

Generated SQL:
{sql_query}

Explain this SQL query in simple business English.

Rules:
- Maximum 3 sentences
- Easy for non-technical users
- Explain what data is being analyzed
- Explain what result the query will produce
- Do not explain SQL syntax
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": explanation_prompt
                }
            ]
        )

        return response.choices[0].message.content

    except Exception:

        return "Unable to generate SQL explanation."
# -------------------------------------------------
# AI MERGE COLUMN SUGGESTION
# -------------------------------------------------

def suggest_merge_columns_with_ai(
    client,
    db_columns,
    file_columns
):

    try:

        prompt = f"""
You are a data integration expert.

Suggest the best matching merge columns between database data and uploaded file data.

Database Columns:
{db_columns}

File Columns:
{file_columns}

Return output in this exact format:

Database Column: column_name
File Column: column_name
Confidence: High/Medium/Low

Rules:
- Do not explain
- Use only given column names
- Pick only one best match
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content

    except Exception:

        return "Unable to suggest merge columns."
# -------------------------------------------------
# PARSE AI MERGE SUGGESTION
# -------------------------------------------------

def parse_merge_suggestion(
    suggestion_text
):

    db_column = ""
    file_column = ""
    confidence = ""

    try:

        lines = suggestion_text.splitlines()

        for line in lines:

            if line.lower().startswith("database column:"):
                db_column = line.split(":", 1)[1].strip()

            elif line.lower().startswith("file column:"):
                file_column = line.split(":", 1)[1].strip()

            elif line.lower().startswith("confidence:"):
                confidence = line.split(":", 1)[1].strip()

    except Exception:

        pass

    return db_column, file_column, confidence
def classify_user_intent(user_question):
    question = user_question.lower()

    trend_keywords = [
        "trend", "growth", "monthly", "yearly",
        "over time", "fastest growing"
    ]

    insight_keywords = [
        "insight", "insights",
        "business performance",
        "summary", "summarize"
    ]

    recommendation_keywords = [
        "recommend",
        "management focus",
        "what should",
        "improve",
        "hurting profitability"
    ]

    chart_keywords = [
        "chart", "graph",
        "visualize", "bar chart",
        "pie chart", "line chart"
    ]

    if any(word in question for word in recommendation_keywords):
        return "RECOMMENDATION"

    elif any(word in question for word in insight_keywords):
        return "BUSINESS_INSIGHT"

    elif any(word in question for word in trend_keywords):
        return "TREND_ANALYSIS"

    elif any(word in question for word in chart_keywords):
        return "CHART_REQUEST"

    return "SQL_QUERY"
def generate_recommendation_summary(
    client,
    user_question,
    df
):
    prompt = f"""
You are a Senior Business Intelligence Consultant.

Analyze the business data and provide:

1. Key Findings
2. Root Cause Analysis
3. Recommendations
4. Business Impact

Rules:
- Use actual data only
- Do not make up numbers
- Be concise and professional
- Give actionable recommendations

User Question:
{user_question}

Data:
{df.head(50).to_string()}
"""

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Recommendation generation failed: {e}"
def generate_ai_response(prompt):
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Unable to generate AI response: GROQ_API_KEY is not configured."

    try:
        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as error:
        return f"AI response generation failed: {error}"


def ask_groq(prompt):
    return generate_ai_response(prompt)