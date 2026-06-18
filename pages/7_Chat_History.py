import streamlit as st
import pandas as pd
from datetime import datetime

from utils.auth import check_authentication
from utils.style import load_css


st.set_page_config(
    page_title="Chat History",
    page_icon="💬",
    layout="wide"
)

check_authentication("chat")
load_css()


st.title("💬 Chat History Center")

st.write("View, search, export, and clear AI query history.")


# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# -------------------------------------------------
# EMPTY STATE
# -------------------------------------------------

if not st.session_state.chat_history:

    st.info("No chat history yet.")

    st.stop()


# -------------------------------------------------
# CREATE DATAFRAME
# -------------------------------------------------

history_data = []

for index, chat in enumerate(st.session_state.chat_history, start=1):

    history_data.append(
        {
            "No": index,
            "Role": chat.get("role", ""),
            "Message": chat.get("message", ""),
            "Time": chat.get(
                "time",
                datetime.now().strftime("%d-%m-%Y %I:%M %p")
            )
        }
    )


history_df = pd.DataFrame(history_data)


# -------------------------------------------------
# KPI CARDS
# -------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Messages", len(history_df))

with col2:
    st.metric(
        "User Questions",
        len(history_df[history_df["Role"] == "user"])
    )

with col3:
    st.metric(
        "AI Responses",
        len(history_df[history_df["Role"] == "assistant"])
    )


# -------------------------------------------------
# SEARCH
# -------------------------------------------------

st.markdown("---")

search_text = st.text_input("Search Chat History")

filtered_df = history_df.copy()

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


# -------------------------------------------------
# DISPLAY HISTORY
# -------------------------------------------------

st.subheader("Conversation History")

st.dataframe(
    filtered_df,
    use_container_width=True
)


# -------------------------------------------------
# EXPORT
# -------------------------------------------------

st.subheader("Export Chat History")

csv_data = filtered_df.to_csv(index=False)

st.download_button(
    "Download Chat History CSV",
    data=csv_data,
    file_name="chat_history.csv",
    mime="text/csv"
)


# -------------------------------------------------
# CLEAR HISTORY
# -------------------------------------------------

st.markdown("---")

if st.button("Clear Chat History"):

    st.session_state.chat_history = []

    st.success("Chat history cleared successfully.")

    st.rerun()
