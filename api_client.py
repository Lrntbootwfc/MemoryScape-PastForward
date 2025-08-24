# api_client.py
import requests
import streamlit as st

def fetch_memories_from_api(user_id: int, api_base: str):
    """Fetch memories from FastAPI server with proper URLs"""
    try:
        response = requests.get(f"{api_base}/memories", params={"user_id": user_id})
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch memories: {response.status_code} - {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return []

def delete_memory_via_api(memory_id: int, api_base: str):
    """Sends a DELETE request to the backend API for a single memory."""
    try:
        response = requests.delete(f"{api_base}/memories/{memory_id}")
        if response.status_code == 204:  # 204 means success
            st.toast("Memory deleted! 🗑️")
            return True
        else:
            st.error(f"Failed to delete memory: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error while deleting: {e}")
        return False