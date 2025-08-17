import streamlit as st
import plotly.graph_objects as go
from typing import List, Dict, Tuple, Optional
import random
import math
import os
from datetime import datetime
import json

class GardenHybrid:
    def __init__(self):
        # Garden dimensions for 2D view
        self.garden_width = 100
        self.garden_height = 80
        self.flower_spacing = 15
        
        # Navigation state
        self.selected_flower_id = None
        self.player_x = 50
        self.player_y = 40
        
        # Enhanced flower types with 3D properties and clustering
        self.flower_types = {
            "happy": {
                "emoji": "🌻", 
                "color": "#FFD700", 
                "name": "Sunflower",
                "petals": 12,
                "height": 1.2,
                "bloom_size": 1.5,
                "stem_color": "#228B22",
                "petal_colors": ["#FFD700", "#FFA500", "#FF8C00"],
                "cluster_center": (25, 20),  # Cluster position
                "cluster_radius": 20
            },
            "romantic": {
                "emoji": "🌹", 
                "color": "#FF69B4", 
                "name": "Rose",
                "petals": 8,
                "height": 1.0,
                "bloom_size": 1.3,
                "stem_color": "#006400",
                "petal_colors": ["#FF69B4", "#FF1493", "#DC143C"],
                "cluster_center": (75, 20),
                "cluster_radius": 20
            },
            "sad": {
                "emoji": "🌿", 
                "color": "#228B22", 
                "name": "Fern",
                "petals": 6,
                "height": 0.8,
                "bloom_size": 1.1,
                "stem_color": "#556B2F",
                "petal_colors": ["#228B22", "#32CD32", "#90EE90"],
                "cluster_center": (25, 60),
                "cluster_radius": 20
            },
            "calm": {
                "emoji": "🌲", 
                "color": "#32CD32", 
                "name": "Pine",
                "petals": 0,
                "height": 2.0,
                "bloom_size": 1.8,
                "stem_color": "#8B4513",
                "petal_colors": ["#32CD32", "#228B22", "#006400"],
                "cluster_center": (75, 60),
                "cluster_radius": 20
            },
            "angry": {
                "emoji": "🌵", 
                "color": "#8B4513", 
                "name": "Cactus",
                "petals": 3,
                "height": 1.5,
                "bloom_size": 1.2,
                "stem_color": "#556B2F",
                "petal_colors": ["#8B4513", "#A0522D", "#CD853F"],
                "cluster_center": (50, 40),
                "cluster_radius": 15
            },
            "nostalgic": {
                "emoji": "🌼", 
                "color": "#FFA500", 
                "name": "Daisy",
                "petals": 10,
                "height": 0.9,
                "bloom_size": 1.4,
                "stem_color": "#228B22",
                "petal_colors": ["#FFA500", "#FFD700", "#FFFF00"],
                "cluster_center": (15, 40),
                "cluster_radius": 15
            },
            "excited": {
                "emoji": "🌷", 
                "color": "#FF1493", 
                "name": "Tulip",
                "petals": 6,
                "height": 1.1,
                "bloom_size": 1.3,
                "stem_color": "#006400",
                "petal_colors": ["#FF1493", "#FF69B4", "#FFB6C1"],
                "cluster_center": (85, 40),
                "cluster_radius": 15
            },
            "proud": {
                "emoji": "🌺", 
                "color": "#FF4500", 
                "name": "Hibiscus",
                "petals": 5,
                "height": 1.3,
                "bloom_size": 1.6,
                "stem_color": "#228B22",
                "petal_colors": ["#FF4500", "#FF6347", "#FF7F50"],
                "cluster_center": (50, 10),
                "cluster_radius": 15
            }
        }
        
        # Initialize session state for garden interactions
        if 'garden_selected_flower' not in st.session_state:
            st.session_state.garden_selected_flower = None
        if 'garden_player_x' not in st.session_state:
            st.session_state.garden_player_x = 50
        if 'garden_player_y' not in st.session_state:
            st.session_state.garden_player_y = 40
        if 'garden_planting_mode' not in st.session_state:
            st.session_state.garden_planting_mode = False
        if 'garden_new_memory_data' not in st.session_state:
            st.session_state.garden_new_memory_data = {}
    
    def generate_garden_layout(self, memories: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Generate clustered garden layout with flowers and empty buds"""
        flowers = []
        empty_buds = []
        
        # Group memories by emotion for clustering
        emotion_groups = {}
        for memory in memories:
            emotion = memory.get("emotion", "happy")
            if emotion not in emotion_groups:
                emotion_groups[emotion] = []
            emotion_groups[emotion].append(memory)
        
        # Place flowers in emotion-based clusters
        for emotion, emotion_memories in emotion_groups.items():
            flower_info = self.flower_types.get(emotion, self.flower_types["happy"])
            cluster_center = flower_info["cluster_center"]
            cluster_radius = flower_info["cluster_radius"]
            
            for i, memory in enumerate(emotion_memories):
                # Calculate position within cluster
                angle = (i / len(emotion_memories)) * 2 * math.pi
                distance = random.uniform(0, cluster_radius * 0.8)
                
                x = cluster_center[0] + math.cos(angle) * distance + random.uniform(-3, 3)
                y = cluster_center[1] + math.sin(angle) * distance + random.uniform(-3, 3)
                
                # Ensure flowers stay within garden bounds
                x = max(10, min(self.garden_width - 10, x))
                y = max(10, min(self.garden_height - 10, y))
                
                flowers.append({
                    "id": f"flower_{memory.get('id', i)}",
                    "memory_id": memory.get("id"),
                    "emotion": emotion,
                    "title": memory.get("title", "Untitled"),
                    "description": memory.get("description", ""),
                    "media_path": memory.get("media_path"),
                    "media_type": memory.get("media_type"),
                    "unlock_at": memory.get("unlock_at"),
                    "x": x,
                    "y": y,
                    "emoji": flower_info["emoji"],
                    "color": flower_info["color"],
                    "name": flower_info["name"],
                    "height": flower_info["height"],
                    "bloom_size": flower_info["bloom_size"],
                    "petals": flower_info["petals"],
                    "stem_color": flower_info["stem_color"],
                    "petal_colors": flower_info["petal_colors"],
                    "bloomed": False,
                    "has_memory": True,
                    "interaction_count": 0,
                    "cluster": emotion
                })
        
        # Generate empty flower buds for planting new memories
        num_empty_buds = max(20, len(memories) // 2)  # At least 20 empty buds
        
        for i in range(num_empty_buds):
            # Find a spot away from existing flowers and clusters
            attempts = 0
            while attempts < 100:
                x = random.uniform(10, self.garden_width - 10)
                y = random.uniform(10, self.garden_height - 10)
                
                # Check distance from existing flowers
                too_close = False
                for flower in flowers:
                    distance = math.sqrt((x - flower["x"])**2 + (y - flower["y"])**2)
                    if distance < self.flower_spacing:
                        too_close = True
                        break
                
                # Check distance from cluster centers
                for emotion, flower_info in self.flower_types.items():
                    cluster_center = flower_info["cluster_center"]
                    cluster_radius = flower_info["cluster_radius"]
                    distance = math.sqrt((x - cluster_center[0])**2 + (y - cluster_center[1])**2)
                    if distance < cluster_radius:
                        too_close = True
                        break
                
                if not too_close:
                    break
                attempts += 1
            
            if attempts < 100:
                empty_buds.append({
                    "id": f"empty_bud_{i}", 
                    "x": x,
                    "y": y,
                    "emoji": "🌱",  # Seed/bud emoji
                    "color": "#8B4513",  # Brown color
                    "height": 0.5,
                    "bloom_size": 0.8,
                    "has_memory": False,
                    "bloomed": False,
                    "ready_to_plant": True,
                    "cluster": "empty"
                })
        
        return flowers, empty_buds
    
    def create_hybrid_garden_visualization(self, flowers: List[Dict], empty_buds: List[Dict]) -> go.Figure:
        """Create an interactive hybrid garden: 2D layout with 3D flowers"""
        
        fig = go.Figure()
        
        # 1. Create 2D ground plane (flat garden) - make it more visible
        ground_x = [0, self.garden_width, self.garden_width, 0, 0]
        ground_y = [0, 0, self.garden_height, self.garden_height, 0]
        ground_z = [0, 0, 0, 0, 0]
        
        fig.add_trace(go.Scatter3d(
            x=ground_x,
            y=ground_y,
            z=ground_z,
            mode='lines',
            line=dict(color='rgba(34, 139, 34, 0.8)', width=3),
            name="Garden Ground",
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Add a filled ground surface for better visibility
        fig.add_trace(go.Surface(
            x=[[0, self.garden_width], [0, self.garden_width]],
            y=[[0, 0], [self.garden_height, self.garden_height]],
            z=[[0, 0], [0, 0]],
            colorscale=[[0, 'rgba(34, 139, 34, 0.3)'], [1, 'rgba(34, 139, 34, 0.1)']],
            showscale=False,
            name="Ground Surface",
            hoverinfo='skip'
        ))
        
        # 2. Add cluster boundaries (visual guides)
        for emotion, flower_info in self.flower_types.items():
            cluster_center = flower_info["cluster_center"]
            cluster_radius = flower_info["cluster_radius"]
            
            # Create cluster boundary circle
            angles = [i * 0.1 for i in range(63)]  # 6.3 radians = 360 degrees
            cluster_x = [cluster_center[0] + cluster_radius * math.cos(angle) for angle in angles]
            cluster_y = [cluster_center[1] + cluster_radius * math.sin(angle) for angle in angles]
            cluster_z = [0.1] * len(angles)  # Slightly above ground
            
            fig.add_trace(go.Scatter3d(
                x=cluster_x,
                y=cluster_y,
                z=cluster_z,
                mode='lines',
                line=dict(color=flower_info["color"], width=1),
                opacity=0.3,
                name=f"{emotion.title()} Cluster",
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # 3. Add 3D flowers with memories
        for flower in flowers:
            flower_traces = self._create_3d_flower(flower)
            for trace in flower_traces:
                fig.add_trace(trace)
        
        # 4. Add 3D empty buds
        for bud in empty_buds:
            bud_traces = self._create_3d_bud(bud)
            for trace in bud_traces:
                fig.add_trace(trace)
        ######################################################
        # 5. Add navigation grid for better orientation
        grid_spacing = 10
        # for x in range(0, self.garden_width + 1, grid_spacing):
        #     fig.add_trace(go.Scatter3d(
        #         x=[x, x],
        #         y=[0, self.garden_height],
        #         z=[0.05, 0.05],
        #         mode='lines',
        #         line=dict(color='rgba(144, 238, 144, 0.2)', width=1),
        #         showlegend=False,
        #         hoverinfo='skip'
        #     ))
        ####################################################################################
        # for y in range(0, self.garden_height + 1, grid_spacing):
        #     fig.add_trace(go.Scatter3d(
        #         x=[0, self.garden_width],
        #         y=[y, y],
        #         z=[0.05, 0.05],
        #         mode='lines',
        #         line=dict(color='rgba(144, 238, 144, 0.2)', width=1),
        #         showlegend=False,
        #         hoverinfo='skip'
        #     ))
        
        # 6. Add player position indicator
        player_trace = go.Scatter3d(
            x=[st.session_state.garden_player_x],
            y=[st.session_state.garden_player_y],
            z=[0.3],
            mode='markers+text',
            marker=dict(
                size=20,
                color='red',
                symbol='diamond',
                opacity=0.9,
                line=dict(width=2, color='white')
            ),
            text=["👤"],
            textposition="middle center",
            name="Player Position",
            showlegend=False,
            hovertemplate="<b>👤 You are here</b><br>Use navigation controls below<br><extra></extra>"
        )
        fig.add_trace(player_trace)
        
        # Update layout for hybrid garden appearance
        fig.update_layout(
            title="🌳 Interactive Memory Garden - Navigate and Plant Memories",
            scene=dict(
                xaxis=dict(
                    title="Garden Width",
                    range=[0, self.garden_width],
                    showgrid=True,
                    gridcolor='rgba(144, 238, 144, 0.4)',
                    showline=True,
                    linecolor='rgba(34, 139, 34, 0.6)',
                    zeroline=False
                ),
                yaxis=dict(
                    title="Garden Height",
                    range=[0, self.garden_height],
                    showgrid=True,
                    gridcolor='rgba(144, 238, 144, 0.4)',
                    showline=True,
                    linecolor='rgba(34, 139, 34, 0.6)',
                    zeroline=False
                ),
                zaxis=dict(
                    title="Height",
                    range=[0, 4],
                    showgrid=True,
                    gridcolor='rgba(144, 238, 144, 0.3)',
                    showline=True,
                    linecolor='rgba(34, 139, 34, 0.4)',
                    zeroline=False
                ),
                camera=dict(
                    eye=dict(x=1.8, y=1.8, z=1.5),
                    center=dict(x=self.garden_width/2, y=self.garden_height/2, z=1.5)
                ),
                dragmode=False,
                aspectmode='manual',
                aspectratio=dict(x=1, y=0.8, z=0.4)
            ),
            height=700,
            margin=dict(l=0, r=0, b=0, t=50),
            showlegend=True,
            legend=dict(
                x=0.02,
                y=0.98,
                bgcolor='rgba(255, 255, 255, 0.9)',
                bordercolor='rgba(0, 0, 0, 0.3)',
                borderwidth=1
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            # Enable 3D navigation and interactions
            modebar=dict(
                add=['zoom', 'reset', 'toimage']  # Only zoom and reset allowed
            ),
            # Add click events
            clickmode='event+select'
        )
        
        return fig
    
    def _create_3d_flower(self, flower_data: Dict) -> List[go.Scatter3d]:
        """Create a 3D flower with bloom effect and interaction"""
        flower_type = self.flower_types.get(flower_data.get("emotion", "happy"), self.flower_types["happy"])
        x, y = flower_data["x"], flower_data["y"]
        z = 0  # Ground level

        traces = []

        # 1. Stem
        stem_height = flower_type["height"]
        stem_trace = go.Scatter3d(
            x=[x, x],
            y=[y, y],
            z=[z, z + stem_height],
            mode='lines',
            line=dict(color=flower_type["stem_color"], width=6),
            name=f"Stem of {flower_data.get('title', 'Flower')}",
            showlegend=False,
            hoverinfo='skip'
        )
        traces.append(stem_trace)

        # 2. Bloom effect
        bloom_multiplier = 1.5 if flower_data.get("bloomed") else 1.0
        bloom_size = flower_type["bloom_size"] * bloom_multiplier

        bloom_trace = go.Scatter3d(
            x=[x],
            y=[y],
            z=[z + stem_height],
            mode='markers+text',
            marker=dict(
                size=bloom_size * 25,
                color=flower_type["color"] if flower_data.get("bloomed") else "#888",
                symbol='circle',
                opacity=1.0 if flower_data.get("bloomed") else 0.7,
                line=dict(width=5 if flower_data.get("bloomed") else 3, color='white')
            ),
            text=[flower_data.get("emoji", flower_type["emoji"])],
            textposition="middle center",
            textfont=dict(size=22 if flower_data.get("bloomed") else 16),
            name=f"{flower_type['name']} - {flower_data.get('title', 'Memory')}",
            hovertemplate=f"<b>{flower_data.get('emoji', flower_type['emoji'])} {flower_data.get('title', 'Memory')}</b><br>" +
                    f"Emotion: {flower_data.get('emotion', 'Unknown').title()}<br>" +
                    "Click to view memory<br>" +
                    "<extra></extra>",
            customdata=[flower_data["id"]],
        )
        traces.append(bloom_trace)

        # 3. Petals
        if flower_type["petals"] > 0:
            petal_colors = flower_type["petal_colors"]
            for i in range(flower_type["petals"]):
                angle = (i / flower_type["petals"]) * 2 * math.pi
                petal_x = x + math.cos(angle) * bloom_size * 0.4
                petal_y = y + math.sin(angle) * bloom_size * 0.4
                petal_z = z + stem_height + 0.15

                petal_trace = go.Scatter3d(
                    x=[petal_x],
                    y=[petal_y],
                    z=[petal_z],
                    mode='markers',
                    marker=dict(
                        size=bloom_size * 12,
                        color=petal_colors[i % len(petal_colors)],
                        symbol='circle',
                        opacity=0.8
                    ),
                    showlegend=False,
                    hoverinfo='skip'
                )
                traces.append(petal_trace)

        # 4. Shadow
        shadow_trace = go.Scatter3d(
            x=[x],
            y=[y],
            z=[z],
            mode='markers',
            marker=dict(
                size=bloom_size * 30,
                color='rgba(0,0,0,0.4)',
                symbol='circle',
                opacity=0.5
            ),
            showlegend=False,
            hoverinfo='skip'
        )
        traces.append(shadow_trace)

        return traces


    def _create_3d_bud(self, bud_data: Dict) -> List[go.Scatter3d]:
        """Create a 3D bud with bloom effect (🌱 → 🌸 when bloomed)"""
        x, y = bud_data["x"], bud_data["y"]
        z = 0  # Ground level

        traces = []

        # 1. Bud stem
        stem_trace = go.Scatter3d(
            x=[x, x],
            y=[y, y],
            z=[z, z + 0.6],
            mode='lines',
            line=dict(color="#654321", width=4),
            showlegend=False,
            hoverinfo='skip'
        )
        traces.append(stem_trace)

        # 2. Bud head (changes if bloomed)
        bloom_multiplier = 1.5 if bud_data.get("bloomed") else 1.0
        bud_size = 10 * bloom_multiplier

        bud_trace = go.Scatter3d(
            x=[x],
            y=[y],
            z=[z + 0.6],
            mode='markers+text',
            marker=dict(
                size=bud_size,
                color="#FFD700" if bud_data.get("bloomed") else "#8B4513",
                symbol='diamond',
                opacity=1.0 if bud_data.get("bloomed") else 0.7,
                line=dict(width=3, color='white')
            ),
            text=["🌸" if bud_data.get("bloomed") else "🌱"],
            textposition="middle center",
            textfont=dict(size=18 if bud_data.get("bloomed") else 14),
            name="Bud",
            hovertemplate="Click to plant a memory<br><extra></extra>",
            customdata=[bud_data["id"]],
        )
        traces.append(bud_trace)

        # 3. Shadow
        shadow_trace = go.Scatter3d(
            x=[x],
            y=[y],
            z=[z],
            mode='markers',
            marker=dict(
                size=22,
                color='rgba(0,0,0,0.4)',
                symbol='circle',
                opacity=0.5
            ),
            showlegend=False,
            hoverinfo='skip'
        )
        traces.append(shadow_trace)

        # 4. Pulse effect
        pulse_trace = go.Scatter3d(
            x=[x],
            y=[y],
            z=[z + 0.8],
            mode='markers',
            marker=dict(
                size=25,
                color='rgba(139, 69, 19, 0.2)',
                symbol='circle',
                opacity=0.6
            ),
            showlegend=False,
            hoverinfo='skip'
        )
        traces.append(pulse_trace)

        return traces
    
    def handle_garden_interactions(self, flowers: List[Dict], empty_buds: List[Dict]):
        """Handle garden interactions: navigation, planting, viewing"""
        
        st.subheader("🎮 Garden Controls")
        
        # Navigation controls with better styling
        st.markdown("### 🧭 Navigation")
        
        # Create a more intuitive navigation layout
        nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
        
        with nav_col1:
            st.markdown("**Movement:**")
        
        with nav_col2:
            # Up/Down controls
            up_col, down_col = st.columns(2)
            with up_col:
                if st.button("⬆️ Up", key="nav_up", use_container_width=True):
                    st.session_state.garden_player_y = max(5, st.session_state.garden_player_y - 8)
                    st.rerun()
            
            with down_col:
                if st.button("⬇️ Down", key="nav_down", use_container_width=True):
                    st.session_state.garden_player_y = min(self.garden_height - 5, st.session_state.garden_player_y + 8)
                    st.rerun()
            
            # Left/Right controls
            left_col, right_col = st.columns(2)
            with left_col:
                if st.button("⬅️ Left", key="nav_left", use_container_width=True):
                    st.session_state.garden_player_x = max(5, st.session_state.garden_player_x - 8)
                    st.rerun()
            
            with right_col:
                if st.button("➡️ Right", key="nav_right", use_container_width=True):
                    st.session_state.garden_player_x = min(self.garden_width - 5, st.session_state.garden_player_x + 8)
                    st.rerun()
        
        with nav_col3:
            st.markdown("**Quick Actions:**")
            if st.button("🏠 Center", key="nav_center", use_container_width=True):
                st.session_state.garden_player_x = self.garden_width // 2
                st.session_state.garden_player_y = self.garden_height // 2
                st.rerun()
        
        # Show current position
        st.markdown(f"**📍 Current Position:** ({st.session_state.garden_player_x:.0f}, {st.session_state.garden_player_y:.0f})")
        
        # Enhanced navigation instructions
        st.markdown("""
        **🎮 Navigation Tips:**
        - **Arrow Buttons:** Move 8 units at a time for faster navigation
        - **Mouse Wheel:** Zoom in/out of the garden view
        - **Drag:** Rotate the 3D garden view around
        - **Touch:** On mobile, touch and drag to navigate
        - **Double Click:** Reset camera to default view
        """)
        
        # Flower selection and interaction
        st.subheader("🌸 Flower Interactions")
        
        # Add click event handling for flowers and buds
        st.markdown("**💡 Click on any flower or bud in the 3D garden above to interact!**")
        
        # Show selected flower details
        if st.session_state.garden_selected_flower:
            selected_flower = None
            for flower in flowers:
                if flower["id"] == st.session_state.garden_selected_flower:
                    selected_flower = flower
                    break
            
            if selected_flower:
                with st.expander(f"🌺 {selected_flower['title']} Details", expanded=True):
                    st.markdown(f"**Emotion:** {selected_flower['emotion'].title()}")
                    st.markdown(f"**Description:** {selected_flower['description']}")
                    
                    if selected_flower.get("media_path"):
                        media_type = selected_flower.get("media_type")
                        if media_type == "image":
                            st.image(selected_flower["media_path"], use_container_width=True)
                        elif media_type == "audio":
                            st.audio(selected_flower["media_path"])
                        elif media_type == "video":
                            st.video(selected_flower["media_path"])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("❌ Close", key="close_flower"):
                            st.session_state.garden_selected_flower = None
                            st.rerun()
                    with col2:
                        if st.button("🌱 Plant Nearby", key="plant_nearby"):
                            # Move player near the selected flower for planting
                            st.session_state.garden_player_x = selected_flower["x"] + 5
                            st.session_state.garden_player_y = selected_flower["y"] + 5
                            st.session_state.garden_planting_mode = True
                            st.rerun()
        
        # Show nearby flowers and buds for easier interaction
        st.markdown("### 🔍 Nearby Objects")
        player_x, player_y = st.session_state.garden_player_x, st.session_state.garden_player_y
        
        # Find nearby flowers
        nearby_flowers = []
        for flower in flowers:
            distance = math.sqrt((flower["x"] - player_x)**2 + (flower["y"] - player_y)**2)
            if distance <= 15:  # Within 15 units
                nearby_flowers.append((flower, distance))
        
        # Find nearby buds
        nearby_buds = []
        for bud in empty_buds:
            distance = math.sqrt((bud["x"] - player_x)**2 + (bud["y"] - player_y)**2)
            if distance <= 15:  # Within 15 units
                nearby_buds.append((bud, distance))
        
        if nearby_flowers or nearby_buds:
            col1, col2 = st.columns(2)
            
            with col1:
                if nearby_flowers:
                    st.markdown("**🌸 Nearby Flowers:**")
                    for flower, distance in sorted(nearby_flowers, key=lambda x: x[1]):
                        if st.button(f"{flower['emoji']} {flower['title']} ({distance:.1f} units)", 
                                key=f"nearby_flower_{flower['id']}"):
                            st.session_state.garden_selected_flower = flower["id"]
                            st.rerun()
            
            with col2:
                if nearby_buds:
                    st.markdown("**🌱 Nearby Buds:**")
                    for bud, distance in sorted(nearby_buds, key=lambda x: x[1]):
                        if st.button(f"🌱 Empty Bud ({distance:.1f} units)", 
                                key=f"nearby_bud_{bud['id']}"):
                            st.session_state.garden_planting_mode = True
                            st.rerun()
        else:
            st.info("No flowers or buds nearby. Use navigation controls to move around the garden.")
        
        # Planting new memories
        st.subheader("🌱 Plant New Memories")
        
        if st.button("🌱 Start Planting Mode", key="planting_mode"):
            st.session_state.garden_planting_mode = not st.session_state.garden_planting_mode
            st.rerun()
        
        if st.session_state.garden_planting_mode:
            st.info("🌱 **Planting Mode Active!** Click on any empty bud (🌱) in the garden to plant a new memory.")
            
            with st.form("plant_memory_form", clear_on_submit=True):
                st.markdown("### New Memory Details")
                title = st.text_input("Memory Title", key="plant_title")
                description = st.text_area("Memory Description", key="plant_description")
                emotion = st.selectbox("Emotion", list(self.flower_types.keys()), key="plant_emotion")
                media_file = st.file_uploader("Upload Media (optional)", type=['jpg', 'jpeg', 'png', 'mp3', 'mp4', 'txt'], key="plant_media")
                unlock_date = st.date_input("Unlock Date (optional)", key="plant_unlock")
                
                if st.form_submit_button("🌱 Plant Memory"):
                    if title:
                        # Store planting data in session state
                        st.session_state.garden_new_memory_data = {
                            "title": title,
                            "description": description,
                            "emotion": emotion,
                            "media_file": media_file,
                            "unlock_date": unlock_date,
                            "planted_at": datetime.now().isoformat()
                        }
                        st.success(f"🌱 Memory '{title}' ready to plant! Click on an empty bud in the garden.")
                        st.session_state.garden_planting_mode = False
                        st.rerun()
                    else:
                        st.error("Please provide a title for your memory.")
    
    def get_cluster_info(self, flowers: List[Dict]) -> Dict:
        """Get information about flower clusters"""
        cluster_stats = {}
        
        for emotion in self.flower_types.keys():
            cluster_flowers = [f for f in flowers if f.get("cluster") == emotion]
            cluster_stats[emotion] = {
                "count": len(cluster_flowers),
                "center": self.flower_types[emotion]["cluster_center"],
                "radius": self.flower_types[emotion]["cluster_radius"],
                "name": self.flower_types[emotion]["name"]
            }
        
        return cluster_stats


    def display_garden_stats(self, flowers: List[Dict], empty_buds: List[Dict]):
        """Display garden statistics and cluster information"""
        st.subheader("📊 Garden Statistics")

        # Basic stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Flowers", len(flowers))
        with col2:
            st.metric("Empty Buds", len(empty_buds))
        with col3:
            st.metric("Total Spots", len(flowers) + len(empty_buds))
        with col4:
            st.metric("Garden Coverage", f"{(len(flowers) / (len(flowers) + len(empty_buds)) * 100):.1f}%")

        # Cluster information
        cluster_stats = self.get_cluster_info(flowers)

        st.subheader("🌸 Flower Clusters")
        cluster_cols = st.columns(4)

        for i, (emotion, stats) in enumerate(cluster_stats.items()):
            with cluster_cols[i % 4]:
                flower_info = self.flower_types[emotion]
                st.markdown(f"**{flower_info['emoji']} {emotion.title()}**")
                st.markdown(f"Flowers: {stats['count']}")
                st.markdown(f"Center: ({stats['center'][0]:.0f}, {stats['center'][1]:.0f})")
                st.markdown(f"Radius: {stats['radius']}")

