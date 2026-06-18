import streamlit as st


def load_css():
    with open("assets/style.css", "r") as file:
        css = file.read()

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True
    )