import streamlit as st

from utils.auth import check_authentication
from utils.style import load_css
from ai.ai_engine import ask_groq


st.set_page_config(
    page_title="AI Copilot | Power AI",
    page_icon="🤖",
    layout="wide"
)

check_authentication("ai_copilot")

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

    .copilot-card {
        background: #111827;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 14px 35px rgba(0,0,0,0.35);
    }

    .section-title {
        color: #F9FAFB;
        font-size: 24px;
        font-weight: 800;
        margin-top: 28px;
        margin-bottom: 16px;
    }

    .prompt-chip {
        background: rgba(37,99,235,0.15);
        border: 1px solid rgba(59,130,246,0.35);
        border-radius: 14px;
        padding: 14px;
        color: #E5E7EB;
        font-size: 15px;
        margin-bottom: 12px;
    }

    .answer-box {
        background: rgba(0,245,212,0.08);
        border-left: 4px solid #00F5D4;
        border-radius: 12px;
        padding: 18px;
        color: #E5E7EB;
        line-height: 1.7;
        font-size: 16px;
    }

    .stTextArea textarea {
        background-color: #111827 !important;
        color: #F9FAFB !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        border-radius: 14px !important;
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
    <div class="main-title">AI Copilot</div>
    <div class="main-subtitle">
        Ask business questions, generate recommendations, summarize analytics, and explore data insights using AI.
    </div>
    """,
    unsafe_allow_html=True
)


left, right = st.columns([2, 1])

with left:
    st.markdown('<div class="section-title">Ask Power AI</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="copilot-card">
        """,
        unsafe_allow_html=True
    )

    user_question = st.text_area(
        "Enter your business question",
        placeholder="Example: What business actions should we take to improve revenue?",
        height=140
    )

    if st.button("Ask AI Copilot", use_container_width=True):
        if user_question.strip() == "":
            st.warning("Please enter a question.")
        else:
            try:
                prompt = f"""
You are Power AI, an enterprise business intelligence copilot.

User question:
{user_question}

Power AI system context:
- Supports MySQL analytics
- Supports MongoDB analytics
- Supports CSV and Excel analytics
- Supports integrated database + file analytics
- Generates KPI cards, charts, summaries, recommendations, and reports

Rules:
- Answer like a business intelligence assistant.
- Keep the response practical and clear.
- Give recommendations when useful.
- Do not invent exact numbers unless user provides data.
- If data is needed, ask the user to open the relevant analytics module.
"""

                answer = ask_groq(prompt)

                st.markdown(
                    f"""
                    <div class="answer-box">
                        {answer}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            except Exception as e:
                st.error(f"AI Copilot Error: {e}")

    st.markdown("</div>", unsafe_allow_html=True)


with right:
    st.markdown('<div class="section-title">Suggested Questions</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="prompt-chip">Which business area should I analyze first?</div>
        <div class="prompt-chip">How can I improve revenue using analytics?</div>
        <div class="prompt-chip">What data quality issues should I check?</div>
        <div class="prompt-chip">How should I present this project in viva?</div>
        <div class="prompt-chip">What features make Power AI enterprise-level?</div>
        """,
        unsafe_allow_html=True
    )


st.markdown('<div class="section-title">AI Copilot Capabilities</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        """
        <div class="copilot-card">
            <h3>📊 Business Insights</h3>
            <p style="color:#9CA3AF;">Understand KPIs, trends, revenue, profit, and customers.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        """
        <div class="copilot-card">
            <h3>💡 Recommendations</h3>
            <p style="color:#9CA3AF;">Generate action points for business improvement.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        """
        <div class="copilot-card">
            <h3>🧹 Data Quality</h3>
            <p style="color:#9CA3AF;">Identify missing values, duplicates, and data issues.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with c4:
    st.markdown(
        """
        <div class="copilot-card">
            <h3>📄 Reports</h3>
            <p style="color:#9CA3AF;">Create summaries for reports, documentation, and presentations.</p>
        </div>
        """,
        unsafe_allow_html=True
    )