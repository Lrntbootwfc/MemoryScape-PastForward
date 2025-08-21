# app.py

import os
from datetime import datetime
import streamlit as st

from auth import ensure_db, signup, login, logout
from db import list_memories, insert_memory # Note: insert_memory is no longer needed directly
from storage import save_upload # Note: save_upload is no longer needed directly
from emotions import classify # Note: classify is no longer needed directly
from utils import iso_or_none, is_locked
import ui
from streamlit_cookies_manager import EncryptedCookieManager 

st.set_page_config(page_title="MemoryScape:", page_icon="🌻", layout="wide")
ensure_db()

cookies = EncryptedCookieManager(
    prefix="memscape_", 
    password="super_secret_key_change_me"  
)

if not cookies.ready(): 
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
        
        # CHANGED: 'Plant a Memory' form has been removed from here. 
        # It will be a React component now.
        st.divider()
        st.markdown("You can now plant a memory from the React frontend.")


# --- Helper: Set Background for each view ---
def set_background(view: str):
    pass

# --- Main Area ---
st.title("🌼 MemoryScape: PastForward Edition")

if "user" not in st.session_state:
    st.info("Please log in or create an account from the sidebar.")
else:
    user = st.session_state.user
    theme = st.segmented_control("Theme", options=["Default","Spring","Autumn","Night"], key="theme", help="Garden themes")
    if theme == "Spring":
        st.markdown("<style>.stApp { background: linear-gradient(180deg,#f0fff4,#ffffff); }</style>", unsafe_allow_html=True)
    elif theme == "Autumn":
        st.markdown("<style>.stApp { background: linear-gradient(180deg,#fff7ed,#ffffff); }</style>", unsafe_allow_html=True)
    elif theme == "Night":
        st.markdown("<style>.stApp { background: linear-gradient(180deg,#0f172a,#1f2937); color:#e5e7eb; }</style>", unsafe_allow_html=True)

    view = st.segmented_control("View", options=["Home","Garden","Enhanced Garden","Galaxy"])
    
    memories = list_memories(user["id"])

    if view == "Garden":
        ui.garden_grid(memories, columns=4)
    elif view == "Enhanced Garden":
        from enhanced_garden_page import *
    elif view == "Galaxy":
        ui.counters(memories)
        ui.galaxy_view(memories)
    else: 
        st.subheader("🏠 Welcome to Your Memory Garden")
        st.markdown("""
        This is your personal space for planting and nurturing memories. 
        Choose a view from above to explore your memories in different ways:
        
        - **Home**: Your cozy space to start your journey
        - **Garden**: A grid view of all your planted memories
        - **Galaxy**: A 3D visualization of your memory universe
        """)
        ui.counters(memories)
        
        if memories:
            st.subheader("🌱 Recent Memories")
            recent_memories = memories[:3]  
            for memory in recent_memories:
                with st.expander(f"📝 {memory.get('title', 'Untitled')}", expanded=False):
                    ui.memory_card(memory)
        else:
            st.info("No memories yet. Plant your first memory from the sidebar! 🌱")
    
    st.divider()
    st.caption("💡 Tip: Emotion engine is rule-based by default. Set EMOTION_BACKEND=hf or openai in deployment to upgrade.")
