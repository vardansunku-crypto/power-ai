import streamlit as st
import yaml


def check_authentication(page_key="default"):

    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    users = config["credentials"]["usernames"]

    if "authentication_status" not in st.session_state:
        st.session_state.authentication_status = False

    if "name" not in st.session_state:
        st.session_state.name = ""

    if st.session_state.authentication_status is True:
        with st.sidebar:
            st.success(f"Welcome {st.session_state.name}")

            if st.button("Logout", key=f"logout_{page_key}"):
                st.session_state.authentication_status = False
                st.session_state.name = ""
                st.rerun()

        return

    st.title("🔐 Power AI Login")

    username = st.text_input("Username", key=f"username_{page_key}")
    password = st.text_input("Password", type="password", key=f"password_{page_key}")

    if st.button("Login", key=f"login_{page_key}"):

        if username in users and password == users[username]["password"]:
            st.session_state.authentication_status = True
            st.session_state.name = users[username]["name"]
            st.rerun()

        else:
            st.error("Invalid username or password")

    st.stop()