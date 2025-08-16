import streamlit as st
import os
from ui import galaxy_view, counters
from db import list_memories
from utils import is_locked

st.set_page_config(page_title="Galaxy View", page_icon="🌌", layout="wide")

# Get the absolute path to the assets directory
current_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(os.path.dirname(current_dir), "assets")
galaxy_image_path = os.path.join(assets_dir, "galaxy.jpeg")

# Set lighter Galaxy background: cosmic blues and purples without pink + image overlay
st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(
            135deg,
            rgba(30, 58, 138, 0.8) 0%,      /* Dark Blue - deep space with transparency */
            rgba(59, 130, 246, 0.8) 25%,      /* Blue - space with transparency */
            rgba(99, 102, 241, 0.8) 50%,      /* Indigo - nebula with transparency */
            rgba(139, 92, 246, 0.8) 75%,      /* Violet - cosmic with transparency */
            rgba(168, 85, 247, 0.8) 100%      /* Purple - galaxy with transparency */
        ), url('file://{galaxy_image_path.replace(os.sep, "/")}');
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    .stMarkdown, .stText, .stTitle {{
        color: #f1f5f9 !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🌌 Galaxy View")
user = st.session_state.get("user")
if user:
    memories = list_memories(user["id"])
    counters(memories)
    galaxy_view(memories)
else:
    st.info("Please log in from the main page.")



