# app.py

import os
from datetime import datetime
import streamlit as st
import requests 
import api_client

# Import the new API client function for creation

from auth import ensure_db, signup, login, logout
from emotions import classify
from utils import iso_or_none
import ui
from streamlit_cookies_manager import EncryptedCookieManager  

st.set_page_config(page_title="MemoryScape:", page_icon="🌻", layout="wide")
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

ensure_db()

cookie_password = os.getenv("COOKIE_PASSWORD", "a_default_password_for_local_use")

cookies = EncryptedCookieManager(
    prefix="memscape_",
    password=cookie_password
)
if not cookies.ready(): 
    st.stop() 

if "user" not in st.session_state and cookies.get("logged_in") == "true": 
    st.session_state.user = {
        "id": int(cookies.get("user_id")), # Ensure user_id is an integer
        "name": cookies.get("user_name"),
        "email": cookies.get("user_email")
    }

# --- Sidebar: Auth or Actions ---
with st.sidebar:
    st.title("MemoryScape 🌿")
    # --- NO CHANGES TO LOGIN/SIGNUP LOGIC ---
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
            if "user" in st.session_state:
                del st.session_state.user

            cookies["logged_in"] = "false"
            cookies["user_id"] = ""
            cookies["user_name"] = ""
            cookies["user_email"] = ""
            cookies.save()
            st.rerun()

        st.divider()
        st.header("Plant a Memory")
        
        # --- REVISED MEMORY CREATION FORM ---
        with st.form("plant_form", clear_on_submit=True):
            title = st.text_input("Title *")
            desc = st.text_area("Description (optional)")
            file = st.file_uploader("Upload media (image/audio/video)", type=None)
            unlock_date = st.date_input("Unlock date (optional)", value=None)
            
            flower_options = {
                "Alien Flower": "alien_flower_optimized.glb",
                "Blue Flower": "blue_flower_optimized.glb",
                "Calendula": "calendula_flower.glb",
                "Pink Animated Flower": "flower_optimized.glb",
                "Detailed Pink Flower": "flower_original_optimized.glb",
                "Sunflower": "sunflower.glb",
                "White Flower": "white_flower_optimized.glb",
                "Lotus Flower": "lotus_flower_by_geometry_nodes.glb",
            }
            selected_flower_name = st.selectbox(
                "Choose a flower for your 3D garden *",
                options=list(flower_options.keys())
            )

            submit = st.form_submit_button("Plant 🌱")

        if submit:
            if not title or not selected_flower_name:
                st.error("Title and a chosen flower are required.")
            else:
                label, _ = classify(f"{title}\n{desc or ''}")
                
                # 2. Prepare data for the API call
                api_base = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/")
                memory_data = {
                    "user_id": user["id"],
                    "title": title,
                    "desc": desc or "",
                    "emotion": label,
                    "model_path": flower_options[selected_flower_name] # Pass the selected model filename
                }

                # Add unlock date if provided
                if unlock_date:
                    unlock_iso = datetime(unlock_date.year, unlock_date.month, unlock_date.day).isoformat()
                    memory_data["unlock_at_iso"] = unlock_iso

                # 3. Prepare file for upload if it exists
                file_content, file_name = (None, None)
                if file:
                    file_content = file.getvalue()
                    file_name = file.name

                # 4. Call the API client function to create the memory
                created = api_client.create_memory_via_api(
                    api_base=api_base,
                    memory_data=memory_data,
                    file=file_content,
                    filename=file_name
                )
                
                if created:
                    # Rerun to refresh the memory list from the API
                    st.rerun()
                # Errors are handled within the api_client function

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

    view = st.segmented_control("View", options=["Home", "Garden", "Enhanced Garden"])
    
    # Ensure api_base is defined for fetching and deleting
    api_base = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api")
    memories = api_client.fetch_memories_from_api(user["id"], api_base=api_base)

    if view == "Enhanced Garden":
        st.subheader("Your 3D Memory Garden")
        frontend_base = os.getenv("FRONTEND_URL", "http://localhost:5173")
        garden_url = f"{frontend_base}/?user_id={user['id']}&api_base={api_base}"
        st.markdown(f"**Click here to view the 3D garden:** [Memory Garden]({garden_url})")
        
    elif view == "Garden":
        # The user_id and api_base are passed correctly for deletion to work
        ui.garden_grid(memories, user['id'], api_base=api_base)
        
    else:  # Home view
        st.subheader("🏠 Welcome to Your Memory Garden")
        st.markdown("""
        This is your personal space for planting and nurturing memories. 
        Choose a view from above to explore your memories in different ways:
        
        - **Home**: A summary of your most recent entries.
        - **Garden**: A grid of all your memories, where you can select them for deletion.
        - **Enhanced Garden**: Your interactive 3D garden experience.
        """)
        ui.counters(memories)
        
        if memories:
            st.subheader("🌱 Recent Memories")
            recent_memories = memories[:3]
            for memory in recent_memories:
                with st.expander(f"📝 {memory.get('title', 'Untitled')}", expanded=False):
                    # ui.memory_card(memory)
                    ui.memory_card(memory, api_base)
        else:
            st.info("No memories yet. Plant your first memory from the sidebar! 🌱")