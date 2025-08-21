import os
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components 

from auth import ensure_db, signup, login, logout
from db import list_memories, insert_memory
from storage import save_upload
from emotions import classify
from utils import iso_or_none, is_locked
import ui
from streamlit_cookies_manager import EncryptedCookieManager  

st.set_page_config(page_title="MemoryScape:", page_icon="🌻", layout="wide")
ensure_db()

cookies = EncryptedCookieManager(
    prefix="memscape_",  # unique key prefix for app
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





# --- Helper: Set Background for each view ---
def set_background(view: str):
    # No background for main page - backgrounds will be on separate pages
    pass

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

    view = st.segmented_control("View", options=["Home","Garden","Enhanced Garden","Galaxy"])
    
    # No background setting here - backgrounds will be on separate pages
    memories = list_memories(user["id"])

    if view == "Enhanced Garden":
        # Check if the build folder exists
        react_build_path = r"D:\.vscode\memoryscapegarden\memoryscape-garden\Memory_Garden\build"

        # react_build_path = os.path.join(os.path.dirname(__file__), "..", "Memory_Garden", "build")
        if not os.path.exists(react_build_path):
            st.error("React build folder not found! Please run 'npm run build' in your React project directory first.")
        else:
            # Read the index.html file
            with open(os.path.join(react_build_path, "index.html"), "r") as f:
                html_code = f.read()

            # IMPORTANT: We pass the user's ID to the React app via a global JavaScript variable.
            html_code = html_code.replace(
                "<head>",
                f"<head><script>window.memoryscape_user_id = {user['id']};</script>"
            )

            # Embed the HTML component
            # NEW: The key is used to force a refresh when the number of memories changes
            components.html(html_code, height=600, key=f"garden-{len(memories)}", scrolling=False)

    elif view == "Garden":
        ui.garden_grid(memories, columns=4)
        
    elif view == "Galaxy":
        ui.counters(memories)
        ui.galaxy_view(memories)
    else:  # Home view
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
            recent_memories = memories[:3]  # Show last 3 memories
            for memory in recent_memories:
                with st.expander(f"📝 {memory.get('title', 'Untitled')}", expanded=False):
                    ui.memory_card(memory)
        else:
            st.info("No memories yet. Plant your first memory from the sidebar! 🌱")
    
    st.divider()
    st.caption("💡 Tip: Emotion engine is rule-based by default. Set EMOTION_BACKEND=hf or openai in deployment to upgrade.")

