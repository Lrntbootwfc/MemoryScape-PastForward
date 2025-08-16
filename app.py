import os
from datetime import datetime
import streamlit as st

from auth import ensure_db, signup, login, logout
from db import list_memories, insert_memory
from storage import save_upload
from emotions import classify
from utils import iso_or_none, is_locked
import ui
from streamlit_cookies_manager import EncryptedCookieManager  

st.set_page_config(page_title="MemoryScape: PastForward", page_icon="🌻", layout="wide")
ensure_db()

cookies = EncryptedCookieManager(
    prefix="memscape_",  # unique key prefix for app
    password="super_secret_key_change_me"  
)

if not cookies.ready():  # NEW
    st.stop() 

if "user" not in st.session_state and cookies.get("logged_in") == "true": 
    st.session_state.user = {
        "id": cookies.get("user_id"),
        "name": cookies.get("user_name"),
        "email": cookies.get("user_email")
    }

# --- Sidebar: Auth or Actions ---
with st.sidebar:
    st.title("MemoryScape 🌿")
    if "user" not in st.session_state:
        st.header("Login")
        email = st.text_input("Email", key="login_email")
        pwd = st.text_input("Password", type="password", key="login_pwd")
        if st.button("Log in"):
            user = login(email, pwd)
            if user:
                st.session_state.user = user
                cookies["logged_in"] = "true"
                cookies["user_id"] = str(user["id"])
                cookies["user_name"] = user["name"]
                cookies["user_email"] = user["email"]
                cookies.save()
                st.rerun()

        st.divider()
        st.header("Create Account")
        se = st.text_input("Email", key="signup_email")
        sn = st.text_input("Name", key="signup_name")
        sp = st.text_input("Password", type="password", key="signup_pwd")
        if st.button("Sign up"):
            if se and sn and sp:
                if signup(se, sn, sp):
                    st.success("Account created. Please log in.")
            else:
                st.error("Fill all fields.")
    else:
        user = st.session_state.user
        st.markdown(f"**Logged in as:** {user['name']} ({user['email']})")
        if st.button("Logout"):
            logout()
            cookies["logged_in"] = "false"  
            cookies["user_id"] = ""  
            cookies["user_name"] = "" 
            cookies["user_email"] = ""  
            cookies.save()  
            st.session_state.clear()
            st.rerun()

        st.divider()
        st.header("Plant a Memory")
        with st.form("plant_form", clear_on_submit=True):
            title = st.text_input("Title")
            desc = st.text_area("Description (used for emotion classification)")
            file = st.file_uploader("Upload media (image/audio/video/text)", type=None)
            unlock_date = st.date_input("Unlock date (optional, future date allowed)", value=None)
            submit = st.form_submit_button("Plant 🌱")
        if submit:
            if not title:
                st.error("Title is required.")
            else:
                # Emotion classification (text only; you can add multimodal later)
                label, plant = classify(f"{title}\n{desc or ''}")
                media_path, media_type = (None, None)
                try:
                    if file is not None:
                        media_path, media_type = save_upload(user["id"], file)
                except Exception as e:
                    st.error(f"Upload failed: {e}")
                    media_path, media_type = (None, None)

                unlock_iso = None
                if unlock_date:
                    # interpret as midnight local; store ISO
                    unlock_iso = datetime(unlock_date.year, unlock_date.month, unlock_date.day).isoformat()

                mem_id = insert_memory(
                    user_id=user["id"], title=title, desc=desc or "",
                    emotion=label, unlock_at_iso=unlock_iso,
                    media_path=media_path, media_type=media_type
                )
                st.success(f"Planted as {plant} ({label}).")
                st.rerun()

# --- Main Area ---
st.title("🌼 MemoryScape: PastForward Edition")

if "user" not in st.session_state:
    st.info("Please log in or create an account from the sidebar.")
else:
    user = st.session_state.user
    # theme toggle
    theme = st.segmented_control("Theme", options=["Default","Spring","Autumn","Night"], key="theme", help="Garden themes")
    if theme == "Spring":
        st.markdown("<style>.stApp { background: linear-gradient(180deg,#f0fff4,#ffffff); }</style>", unsafe_allow_html=True)
    elif theme == "Autumn":
        st.markdown("<style>.stApp { background: linear-gradient(180deg,#fff7ed,#ffffff); }</style>", unsafe_allow_html=True)
    elif theme == "Night":
        st.markdown("<style>.stApp { background: linear-gradient(180deg,#0f172a,#1f2937); color:#e5e7eb; }</style>", unsafe_allow_html=True)

    view = st.segmented_control("View", options=["Garden","Galaxy"])

    memories = list_memories(user["id"])

    if view == "Garden":
        ui.garden_grid(memories, columns=4)
    else:
        ui.counters(memories)
        ui.galaxy_view(memories)

    st.divider()
    st.caption("Tip: Emotion engine is rule-based by default. Set EMOTION_BACKEND=hf or openai in deployment to upgrade.")

