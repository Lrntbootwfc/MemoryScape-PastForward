import os
from typing import List, Dict
import streamlit as st
import plotly.graph_objects as go
from utils import is_locked
from emotions import PLANT_BY_EMOTION

PLANT_EMOJIS = {
    "happy": "🌻", "romantic": "🌹", "sad": "🌿", "calm": "🌲",
    "angry":"🌵","nostalgic":"🌼","excited":"🌷","proud":"🌺"
}
BUD = "🌱"

def counters(memories: List[Dict]):
    planted = len(memories)
    locked = sum(1 for m in memories if is_locked(m["unlock_at"]))
    bloomed = planted - locked
    c1,c2,c3 = st.columns(3)
    c1.metric("Planted", planted)
    c2.metric("Locked (buds)", locked)
    c3.metric("Bloomed", bloomed)

def memory_card(m: Dict):
    lock = is_locked(m["unlock_at"])
    emoji = BUD if lock else PLANT_EMOJIS.get(m["emotion"], "🌼")
    st.markdown(f"### {emoji} {m['title']}")
    st.caption(f"Emotion: {m['emotion'].title()} • {'Locked until ' + m['unlock_at'] if lock and m['unlock_at'] else 'Unlocked'}")
    if m.get("media_path") and not lock:
        mt = m.get("media_type")
        p = m["media_path"]
        if mt == "image": st.image(p, use_container_width=True)
        elif mt == "audio": st.audio(p)
        elif mt == "video": st.video(p)
        elif mt == "text":
            with open(p, "rb") as f: st.download_button("Download file", data=f, file_name=os.path.basename(p))
    st.write(m.get("description") or "")

def garden_grid(memories: List[Dict], columns: int = 4):
    st.subheader("🌳 Garden View")
    counters(memories)
    if not memories:
        st.info("No memories yet. Plant your first memory from the sidebar.")
        return
    rows = [memories[i:i+columns] for i in range(0, len(memories), columns)]
    for row in rows:
        cols = st.columns(columns)
        for col, m in zip(cols, row):
            lock = is_locked(m["unlock_at"])
            emoji = BUD if lock else PLANT_EMOJIS.get(m["emotion"], "🌼")
            with col:
                with st.expander(f"{emoji} {m['title']}", expanded=False):
                    memory_card(m)

def galaxy_view(memories: List[Dict]):
    st.subheader("🌌 Galaxy View (3D)")
    if not memories:
        st.info("No memories to show.")
        return
    # Map to points
    xs, ys, zs, texts, colors, symbols = [],[],[],[],[],[]
    color_map = {
        "happy":"gold","romantic":"crimson","sad":"teal","calm":"forestgreen",
        "angry":"darkorange","nostalgic":"violet","excited":"deeppink","proud":"red"
    }
    symbol_map = {"locked":"circle","open":"diamond"}
    for i, m in enumerate(memories):
        xs.append(i % 10)
        ys.append((i // 10) % 10)
        zs.append((i // 100))
        texts.append(f"{m['title']} ({m['emotion']})")
        colors.append(color_map.get(m["emotion"], "gray"))
        symbols.append(symbol_map["locked"] if is_locked(m["unlock_at"]) else symbol_map["open"])

    fig = go.Figure(data=[go.Scatter3d(
        x=xs, y=ys, z=zs, mode='markers',
        marker=dict(size=8, symbol=symbols, opacity=0.9, line=dict(width=1), color=colors),
        text=texts, hoverinfo='text'
    )])
    fig.update_layout(height=500, margin=dict(l=0,r=0,b=0,t=0), scene=dict(
        xaxis_title='Row', yaxis_title='Col', zaxis_title='Layer'
    ))
    st.plotly_chart(fig, use_container_width=True)

