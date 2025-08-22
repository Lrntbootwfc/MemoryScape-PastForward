import os
from typing import List, Dict
import streamlit as st
import plotly.graph_objects as go
from utils import get_memory_state, is_locked
from emotions import PLANT_BY_EMOTION
from datetime import datetime, timezone

PLANT_EMOJIS = {
    "happy": "🌻", "romantic": "🌹", "sad": "🌿", "calm": "🌲",
    "angry": "🌵", "nostalgic": "🌼", "excited": "🌷", "proud": "🌺"
}
STATE_EMOJIS = {
    "bud": "🌱",
    "bloom": "🌸",
    "fruit": "🍎"
}

def counters(memories: List[Dict]):
    buds = sum(1 for m in memories if get_memory_state(m) == "bud")
    blooms = sum(1 for m in memories if get_memory_state(m) == "bloom")
    fruits = sum(1 for m in memories if get_memory_state(m) == "fruit")
    c1, c2, c3 = st.columns(3)
    c1.metric("Buds", buds)
    c2.metric("Blooms", blooms)
    c3.metric("Fruits", fruits)

def memory_card(m: Dict):
    lock = is_locked(m.get("unlock_at"))
    state = get_memory_state(m)

    if state in STATE_EMOJIS:
        emoji = STATE_EMOJIS[state]
    else:
        emoji = PLANT_EMOJIS.get(m.get("emotion"), "🌼")

    st.markdown(f"### {emoji} {m.get('title', 'Untitled')}")
    unlock_str = m.get("unlock_at")
    status = f"Locked until {unlock_str}" if lock and unlock_str else "Unlocked"

    st.caption(
        f"Emotion: {m.get('emotion', 'Unknown').title()} • {status}"
    )

    media_path = m.get("media_path")
    if media_path:
        # CORRECTED: Hum media_path ko seedhe use kar rahe hain
        # Kyunki ab aapki server.py file full URL bhejegi
        # Ab Streamlit ko file path nahi, balki URL milega.
        mt = m.get("media_type")
        if "image" in mt:
            st.image(media_path, use_container_width=True)
        elif "audio" in mt:
            st.audio(media_path)
        elif "video" in mt:
            st.video(media_path)
        elif mt == "text":
            st.warning("Cannot preview text files, but you can download it.")


    st.write(m.get("description") or "")

    size_map = {"bud": 30, "bloom": 50, "fruit": 70}
    st.markdown(
        f"<div style='font-size:{size_map.get(state, 40)}px'>{emoji}</div>",
        unsafe_allow_html=True
    )

def garden_grid(memories: List[Dict], show_header: bool = True, columns: int = 4):
    if show_header:
        st.subheader("🌳 Garden View")
        counters(memories)
    
    if not memories:
        st.info("No memories yet. Plant your first memory from the sidebar.")
        return

    rows = [memories[i:i + columns] for i in range(0, len(memories), columns)]
    for row in rows:
        cols = st.columns(columns)
        for col, m in zip(cols, row):
            with col:
                with st.expander(f"{PLANT_EMOJIS.get(m.get('emotion'), '🌼')} {m.get('title', 'Untitled')}", expanded=False):
                    memory_card(m)

def galaxy_view(memories: List[Dict]):
    st.subheader("🌌 Galaxy View (3D)")
    if not memories:
        st.info("No memories to show.")
        return

    xs, ys, zs, texts, colors, symbols = [], [], [], [], [], []
    color_map = {
        "happy": "gold", "romantic": "crimson", "sad": "teal", "calm": "forestgreen",
        "angry": "darkorange", "nostalgic": "violet", "excited": "deeppink", "proud": "red"
    }
    symbol_map = {"locked": "circle", "open": "diamond"}

    for i, m in enumerate(memories):
        xs.append(i % 10)
        ys.append((i // 10) % 10)
        zs.append((i // 100))
        texts.append(f"{m.get('title', 'Untitled')} ({m.get('emotion', 'Unknown')})")
        colors.append(color_map.get(m.get("emotion"), "gray"))
        symbols.append(
            symbol_map["locked"] if is_locked(m.get("unlock_at")) else symbol_map["open"]
        )

    fig = go.Figure(data=[go.Scatter3d(
        x=xs, y=ys, z=zs, mode='markers',
        marker=dict(size=8, symbol=symbols, opacity=0.9, line=dict(width=1), color=colors),
        text=texts, hoverinfo='text'
    )])
    fig.update_layout(
        height=500, margin=dict(l=0, r=0, b=0, t=0),
        scene=dict(xaxis_title='Row', yaxis_title='Col', zaxis_title='Layer')
    )
    
    st.plotly_chart(fig, use_container_width=True)
