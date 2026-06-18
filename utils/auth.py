import os
import re
import yaml
import bcrypt
import streamlit as st
from dotenv import load_dotenv


CONFIG_FILE = "config.yaml"
MAX_LOGIN_ATTEMPTS = 5

load_dotenv()
ADMIN_SIGNUP_CODE = os.getenv("ADMIN_SIGNUP_CODE", "POWERAI_ADMIN_2026")


def _login_logo_path():
    primary_logo = "assets/power_ai_logo.png"
    fallback_logo = "assets/icons/ai.png.svg"

    if os.path.exists(primary_logo):
        return primary_logo

    return fallback_logo


def load_config():
    with open(CONFIG_FILE, "r") as file:
        return yaml.safe_load(file)


def save_config(config):
    with open(CONFIG_FILE, "w") as file:
        yaml.dump(config, file, default_flow_style=False)


def hash_password(password):
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(password, stored_password):
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            stored_password.encode("utf-8")
        )
    except Exception:
        return password == stored_password


def is_strong_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters."

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."

    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number."

    return True, ""


def init_auth_state():
    defaults = {
        "authentication_status": False,
        "name": "",
        "username": "",
        "failed_attempts": 0
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def logout_user():
    st.session_state.authentication_status = False
    st.session_state.name = ""
    st.session_state.username = ""
    st.rerun()


def check_authentication(page_key="default"):
    init_auth_state()

    config = load_config()
    users = config["credentials"]["usernames"]

    if st.session_state.authentication_status is True:
        with st.sidebar:
            st.success(f"Welcome {st.session_state.name}")

            if st.button("Logout", key=f"logout_{page_key}"):
                logout_user()

        return

    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #0B1020 0%, #111827 100%);
            color: #F9FAFB;
        }

        header {
            visibility: hidden;
        }

        [data-testid="stSidebar"] {
            display: none;
        }

        .block-container {
            max-width: 1400px;
            padding-top: 8vh;
            padding-bottom: 0rem;
        }

        .brand-desc {
            color: #AAB2C0;
            font-size: 17px;
            line-height: 1.7;
            max-width: 520px;
            margin-top: 24px;
            margin-bottom: 28px;
        }

        .feature {
            color: #E5E7EB;
            font-size: 17px;
            margin: 16px 0;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.08);
        }

        .feature span {
            color: #00F5D4;
            margin-right: 10px;
        }

        .version-text {
            color: #64748B;
            margin-top: 35px;
            font-size: 14px;
        }

        .login-card {
            background: rgba(17, 24, 39, 0.95);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 22px;
            padding: 45px 42px;
            box-shadow: 0 20px 55px rgba(0,0,0,0.35);
            margin-top: 45px;
        }

        .login-heading {
            font-size: 34px;
            font-weight: 800;
            color: #F9FAFB;
            margin-bottom: 8px;
        }

        .login-subtitle {
            color: #9CA3AF;
            font-size: 16px;
            margin-bottom: 30px;
        }

        .stTextInput label,
        .stRadio label {
            color: #E5E7EB !important;
            font-weight: 600;
        }

        .stTextInput input {
            background-color: #0B1020 !important;
            color: #F9FAFB !important;
            border: 1px solid rgba(255,255,255,0.20) !important;
            border-radius: 12px !important;
            height: 48px;
        }

        .stTextInput input:focus {
            border: 1px solid #3B82F6 !important;
            box-shadow: 0 0 0 1px #3B82F6 !important;
        }

        .stButton > button {
            width: 100%;
            height: 48px;
            background: #2563EB;
            color: white;
            border: none;
            border-radius: 12px;
            font-weight: 700;
            font-size: 16px;
            margin-top: 14px;
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

    space1, left, right, space2 = st.columns(
        [0.15, 1, 1, 0.15],
        gap="large"
    )

    with left:
        logo_col1, logo_col2, logo_col3 = st.columns([1, 3, 1])

        with logo_col2:
            st.image(
                _login_logo_path(),
                use_container_width=True
            )

        st.markdown(
            """
            <div class="brand-desc">
                Transform data into actionable intelligence through a secure
                AI-powered analytics platform. Connect, analyze, visualize,
                and make smarter business decisions from a single workspace.
            </div>

            <div class="feature"><span>✓</span> Secure Login System</div>
            <div class="feature"><span>✓</span> Password Hashing</div>
            <div class="feature"><span>✓</span> Admin-Controlled Signup</div>
            <div class="feature"><span>✓</span> Protected Dashboard Access</div>
            <div class="feature"><span>✓</span> Enterprise Reporting</div>

            <div class="version-text">Power AI Enterprise v2.0</div>
            """,
            unsafe_allow_html=True
        )

    with right:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)

        auth_mode = st.radio(
            "Choose Option",
            ["Login", "Sign Up"],
            horizontal=True,
            key=f"auth_mode_{page_key}"
        )

        if auth_mode == "Login":
            st.markdown(
                """
                <div class="login-heading">Welcome Back</div>
                <div class="login-subtitle">Sign in to continue to Power AI</div>
                """,
                unsafe_allow_html=True
            )

            username = st.text_input(
                "Username",
                placeholder="Enter your username",
                key=f"username_{page_key}"
            )

            password = st.text_input(
                "Password",
                placeholder="Enter your password",
                type="password",
                key=f"password_{page_key}"
            )

            if st.button("Sign In", key=f"login_{page_key}"):

                if st.session_state.failed_attempts >= MAX_LOGIN_ATTEMPTS:
                    st.error(
                        "Too many failed login attempts. Please restart the app or contact admin."
                    )
                    st.stop()

                if username in users:
                    stored_password = users[username]["password"]

                    if verify_password(password, stored_password):
                        st.session_state.authentication_status = True
                        st.session_state.name = users[username].get("name", username)
                        st.session_state.username = username
                        st.session_state.failed_attempts = 0
                        st.rerun()

                    else:
                        st.session_state.failed_attempts += 1
                        st.error("Invalid username or password")

                else:
                    st.session_state.failed_attempts += 1
                    st.error("Invalid username or password")

        else:
            st.markdown(
                """
                <div class="login-heading">Create Account</div>
                <div class="login-subtitle">Only authorized users can register</div>
                """,
                unsafe_allow_html=True
            )

            new_name = st.text_input(
                "Full Name",
                placeholder="Enter full name",
                key=f"signup_name_{page_key}"
            )

            new_username = st.text_input(
                "New Username",
                placeholder="Create username",
                key=f"signup_username_{page_key}"
            )

            new_password = st.text_input(
                "New Password",
                placeholder="Create password",
                type="password",
                key=f"signup_password_{page_key}"
            )

            confirm_password = st.text_input(
                "Confirm Password",
                placeholder="Confirm password",
                type="password",
                key=f"confirm_password_{page_key}"
            )

            admin_code = st.text_input(
                "Admin Registration Code",
                placeholder="Enter admin code",
                type="password",
                key=f"admin_code_{page_key}"
            )

            if st.button("Create Account", key=f"signup_{page_key}"):

                password_ok, password_message = is_strong_password(new_password)

                if admin_code != ADMIN_SIGNUP_CODE:
                    st.error("Invalid admin registration code.")

                elif not new_name or not new_username or not new_password:
                    st.error("Please fill all fields.")

                elif new_username in users:
                    st.error("Username already exists.")

                elif new_password != confirm_password:
                    st.error("Passwords do not match.")

                elif not password_ok:
                    st.error(password_message)

                else:
                    users[new_username] = {
                        "name": new_name,
                        "password": hash_password(new_password)
                    }

                    config["credentials"]["usernames"] = users
                    save_config(config)

                    st.success("Account created successfully. Please login now.")

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()