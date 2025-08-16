import streamlit as st
import os
from ui import garden_grid, counters
from db import list_memories
from utils import is_locked

st.set_page_config(page_title="Garden View", page_icon="🌳", layout="wide")

# Get the absolute path to the assets directory
current_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(os.path.dirname(current_dir), "assets")
garden_image_path = os.path.join(assets_dir, "gardenview.jpeg")

# Set Garden background: blue sky in upper half, green grass in lower half + image overlay
st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(
            to bottom,
            rgba(135, 206, 235, 0.8) 0%,      /* Light Sky Blue - sky with transparency */
            rgba(70, 130, 180, 0.8) 25%,      /* Steel Blue - sky with transparency */
            rgba(32, 178, 170, 0.8) 50%,      /* Light Sea Green - transition with transparency */
            rgba(50, 205, 50, 0.8) 75%,      /* Lime Green - grass with transparency */
            rgba(34, 139, 34, 0.8) 100%      /* Forest Green - grass with transparency */
        ), url('file://{garden_image_path.replace(os.sep, "/")}');
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    .stMarkdown, .stText, .stTitle {{
        color: #1f2937 !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🌳 Garden View")
user = st.session_state.get("user")
if user:
    memories = list_memories(user["id"])
    # Only show counters once here, not in garden_grid
    counters(memories)
    # Remove the duplicate subheader from garden_grid
    garden_grid(memories, show_header=False, columns=4)
else:
    st.info("Please log in from the main page.")

