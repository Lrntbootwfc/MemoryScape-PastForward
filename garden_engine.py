import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Tuple, Optional
import random
import math
from datetime import datetime

class GardenEngine:
    def __init__(self):
        self.flower_types = {
            "happy": {"emoji": "🌻", "color": "#FFD700", "name": "Sunflower"},
            "romantic": {"emoji": "🌹", "color": "#FF69B4", "name": "Rose"},
            "sad": {"emoji": "🌿", "color": "#228B22", "name": "Fern"},
            "calm": {"emoji": "🌲", "color": "#32CD32", "name": "Pine"},
            "angry": {"emoji": "🌵", "color": "#8B4513", "name": "Cactus"},
            "nostalgic": {"emoji": "🌼", "color": "#FFA500", "name": "Daisy"},
            "excited": {"emoji": "🌷", "color": "#FF1493", "name": "Tulip"},
            "proud": {"emoji": "🌺", "color": "#FF4500", "name": "Hibiscus"}
        }
        
        # Garden dimensions and layout
        self.garden_width = 20
        self.garden_depth = 15
        self.flower_spacing = 2
        
    def generate_garden_layout(self, memories: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Generate garden layout with flowers and empty spots"""
        flowers = []
        empty_spots = []
        
        # Place flowers with memories
        for i, memory in enumerate(memories):
            emotion = memory.get("emotion", "happy")
            flower_info = self.flower_types.get(emotion, self.flower_types["happy"])
            
            # Calculate position (avoid edges)
            x = random.uniform(2, self.garden_width - 2)
            z = random.uniform(2, self.garden_depth - 2)
            y = 0.5  # Slightly above ground for 3D effect
            
            flowers.append({
                "id": f"flower_{i}",
                "memory_id": memory.get("id"),
                "emotion": emotion,
                "title": memory.get("title", "Untitled"),
                "description": memory.get("description", ""),
                "media_path": memory.get("media_path"),
                "media_type": memory.get("media_type"),
                "unlock_at": memory.get("unlock_at"),
                "x": x,
                "y": y,
                "z": z,
                "emoji": flower_info["emoji"],
                "color": flower_info["color"],
                "name": flower_info["name"],
                "size": 1.0,  # Base size
                "bloomed": False,
                "has_memory": True
            })
        
        # Generate empty flower spots for planting new memories
        num_empty_spots = max(10, len(memories) // 2)  # At least 10 empty spots
        
        for i in range(num_empty_spots):
            # Find a spot away from existing flowers
            attempts = 0
            while attempts < 50:
                x = random.uniform(1, self.garden_width - 1)
                z = random.uniform(1, self.garden_depth - 1)
                
                # Check distance from existing flowers
                too_close = False
                for flower in flowers:
                    distance = math.sqrt((x - flower["x"])**2 + (z - flower["z"])**2)
                    if distance < self.flower_spacing:
                        too_close = True
                        break
                
                if not too_close:
                    break
                attempts += 1
            
            if attempts < 50:
                empty_spots.append({
                    "id": f"empty_{i}",
                    "x": x,
                    "y": 0.3,  # Slightly below existing flowers
                    "z": z,
                    "emoji": "🌱",  # Seed emoji for empty spots
                    "color": "#8B4513",  # Brown color
                    "size": 0.8,
                    "has_memory": False,
                    "bloomed": False
                })
        
        return flowers, empty_spots
    
    def create_garden_visualization(self, flowers: List[Dict], empty_spots: List[Dict]) -> go.Figure:
        """Create the 3D garden visualization using Plotly"""
        
        # Prepare data for plotting
        flower_x = [f["x"] for f in flowers]
        flower_y = [f["y"] for f in flowers]
        flower_z = [f["z"] for f in flowers]
        flower_text = [f"🌺 {f['title']}" for f in flowers]
        flower_colors = [f["color"] for f in flowers]
        flower_sizes = [f["size"] * 15 for f in flowers]  # Scale up for visibility
        
        empty_x = [e["x"] for e in empty_spots]
        empty_y = [e["y"] for e in empty_spots]
        empty_z = [e["z"] for e in empty_spots]
        empty_text = ["🌱 Plant New Memory" for _ in empty_spots]
        empty_colors = ["#8B4513" for _ in empty_spots]
        empty_sizes = [e["size"] * 12 for e in empty_spots]
        
        # Create the 3D scatter plot
        fig = go.Figure()
        
        # Add flowers with memories
        if flowers:
            fig.add_trace(go.Scatter3d(
                x=flower_x,
                y=flower_y,
                z=flower_z,
                mode='markers+text',
                marker=dict(
                    size=flower_sizes,
                    color=flower_colors,
                    symbol='circle',
                    opacity=0.9,
                    line=dict(width=2, color='white')
                ),
                text=flower_text,
                textposition="middle center",
                name="Memories",
                hovertemplate="<b>%{text}</b><br>" +
                            "Click to view memory<br>" +
                            "<extra></extra>"
            ))
        
        # Add empty spots
        if empty_spots:
            fig.add_trace(go.Scatter3d(
                x=empty_x,
                y=empty_y,
                z=empty_z,
                mode='markers+text',
                marker=dict(
                    size=empty_sizes,
                    color=empty_colors,
                    symbol='diamond',
                    opacity=0.7,
                    line=dict(width=1, color='#654321')
                ),
                text=empty_text,
                textposition="middle center",
                name="Empty Spots",
                hovertemplate="<b>%{text}</b><br>" +
                            "Click to plant new memory<br>" +
                            "<extra></extra>"
            ))
        
        # Update layout for garden appearance
        fig.update_layout(
            title="🌳 Memory Garden - Interactive 3D View",
            scene=dict(
                xaxis_title="Garden Width",
                yaxis_title="Height",
                zaxis_title="Garden Depth",
                xaxis=dict(range=[0, self.garden_width], showgrid=True, gridcolor='lightgreen'),
                yaxis=dict(range=[0, 2], showgrid=True, gridcolor='lightblue'),
                zaxis=dict(range=[0, self.garden_depth], showgrid=True, gridcolor='lightgreen'),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5),
                    center=dict(x=self.garden_width/2, y=0.5, z=self.garden_depth/2)
                )
            ),
            height=600,
            margin=dict(l=0, r=0, b=0, t=50),
            showlegend=True,
            legend=dict(
                x=0.02,
                y=0.98,
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='rgba(0, 0, 0, 0.2)'
            )
        )
        
        return fig
    
    def handle_flower_click(self, click_data: Dict, flowers: List[Dict], empty_spots: List[Dict]) -> Optional[Dict]:
        """Handle flower clicks and return memory data or empty spot info"""
        if not click_data:
            return None
            
        point_index = click_data.get("points", [{}])[0].get("pointIndex", -1)
        curve_number = click_data.get("points", [{}])[0].get("curveNumber", -1)
        
        if curve_number == 0 and point_index >= 0 and point_index < len(flowers):
            # Clicked on a flower with memory
            flower = flowers[point_index]
            return {
                "type": "memory",
                "data": flower,
                "action": "view_memory"
            }
        elif curve_number == 1 and point_index >= 0 and point_index < len(empty_spots):
            # Clicked on empty spot
            empty_spot = empty_spots[point_index]
            return {
                "type": "empty_spot",
                "data": empty_spot,
                "action": "plant_memory"
            }
        
        return None
