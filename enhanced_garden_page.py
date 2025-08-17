import streamlit as st
import os
from garden_hybrid import GardenHybrid
from db import list_memories, insert_memory
from storage import save_upload
from emotions import classify
from datetime import datetime
from ui import counters

st.set_page_config(page_title="Enhanced Memory Garden", page_icon="🌳", layout="wide")

# Get the absolute path to the assets directory
current_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(current_dir, "assets")
garden_image_path = os.path.join(assets_dir, "gardenview.jpeg")

# Set Garden background
st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(
            to bottom,
            rgba(135, 206, 235, 0.8) 0%,
            rgba(70, 130, 180, 0.8) 25%,
            rgba(32, 178, 170, 0.8) 50%,
            rgba(50, 205, 50, 0.8) 75%,
            rgba(34, 139, 34, 0.8) 100%
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

st.title("🌳 Enhanced Interactive Memory Garden")
st.markdown("**Navigate through your memory garden, plant new memories, and explore your emotional landscape!**")

# Check if user is logged in
user = st.session_state.get("user")
if not user:
    st.error("Please log in to access your memory garden.")
    st.stop()

# Initialize the enhanced garden
garden = GardenHybrid()

# Get existing memories from database
existing_memories = list_memories(user["id"])

# Show memory statistics
st.subheader("📊 Your Memory Garden Overview")
counters(existing_memories)

# Generate garden layout
flowers, empty_buds = garden.generate_garden_layout(existing_memories)

# Display garden statistics
garden.display_garden_stats(flowers, empty_buds)

# Create the interactive garden visualization
st.subheader("🌸 Your Interactive Garden")
st.markdown("**Use the controls below to navigate and interact with your garden!**")

# Create the 3D garden visualization
fig = garden.create_hybrid_garden_visualization(flowers, empty_buds)

# Display the garden with click events
selected_point = st.plotly_chart(fig, use_container_width=True, key="garden_plot")

# Handle garden interactions
garden.handle_garden_interactions(flowers, empty_buds)

# Memory planting integration
st.subheader("🌱 Memory Planting Integration")

# Check if there's new memory data to save
if st.session_state.garden_new_memory_data and st.button("💾 Save Planted Memory to Database"):
    memory_data = st.session_state.garden_new_memory_data
    
    try:
        # Save media file if provided
        media_path, media_type = None, None
        if memory_data.get("media_file"):
            media_path, media_type = save_upload(user["id"], memory_data["media_file"])
        
        # Convert unlock date to ISO format
        unlock_iso = None
        if memory_data.get("unlock_date"):
            unlock_iso = datetime(
                memory_data["unlock_date"].year,
                memory_data["unlock_date"].month,
                memory_data["unlock_date"].day
            ).isoformat()
        
        # Insert memory into database
        mem_id = insert_memory(
            user_id=user["id"],
            title=memory_data["title"],
            desc=memory_data["description"],
            emotion=memory_data["emotion"],
            unlock_at_iso=unlock_iso,
            media_path=media_path,
            media_type=media_type
        )
        
        st.success(f"🌱 Memory '{memory_data['title']}' successfully planted in your garden!")
        
        # Clear the planting data
        st.session_state.garden_new_memory_data = {}
        st.rerun()
        
    except Exception as e:
        st.error(f"Failed to save memory: {e}")

# Garden tips and instructions
with st.expander("💡 Garden Tips & Instructions", expanded=False):
    st.markdown("""
    ### 🌸 How to Use Your Memory Garden
    
    **Navigation:**
    - Use the arrow buttons to move around the garden
    - Use mouse wheel to zoom in/out
    - Drag to rotate the garden view
    - Touch and drag on mobile devices
    
    **Interactions:**
    - Click on flowers to view memory details
    - Click on empty buds (🌱) to plant new memories
    - Flowers are clustered by emotion type
    - Each cluster has a different color boundary
    
    **Planting Memories:**
    1. Click "Start Planting Mode"
    2. Fill in the memory details
    3. Click "Plant Memory"
    4. Click on an empty bud in the garden
    5. Save to database when ready
    
    **3D Features:**
    - Flowers have realistic 3D structure with stems and petals
    - Different emotions have different flower types
    - Flowers bloom and grow based on interaction
    - Player position is shown with a red diamond
    
    **Clustering:**
    - Similar emotions are grouped together
    - Each cluster has a colored boundary
    - Empty buds are placed away from clusters
    - Natural, walkable garden layout
    """)

# Show current garden state
with st.expander("🔍 Current Garden State", expanded=False):
    st.json({
        "total_flowers": len(flowers),
        "empty_buds": len(empty_buds),
        "player_position": (st.session_state.garden_player_x, st.session_state.garden_player_y),
        "selected_flower": st.session_state.garden_selected_flower,
        "planting_mode": st.session_state.garden_planting_mode
    })
