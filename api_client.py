# api_client.py

import requests
import streamlit as st
from typing import Optional, Dict, Any

def fetch_memories_from_api(user_id: int, api_base: str):
    """Fetches memories from the FastAPI server."""
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

def create_memory_via_api(api_base: str, memory_data: Dict[str, Any], file: Optional[bytes] = None, filename: Optional[str] = None):
    """
    Creates a new memory by sending data and an optional file to the backend.
    """
    files = {}
    if file and filename:
        files['file'] = (filename, file, 'application/octet-stream')

    try:
        # We send form fields as 'data' and files as 'files'
        response = requests.post(f"{api_base}/memories", data=memory_data, files=files)
        
        if response.status_code == 201: # Created
            st.toast("Memory planted! 🌱")
            return response.json()
        else:
            st.error(f"Failed to create memory: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error while creating memory: {e}")
        return None

def delete_multiple_memories_via_api(user_id: int, memory_ids: list, api_base: str):
    """Sends a single POST request to the backend to delete memories."""
    try:
        # Use POST for reliability, sending user_id for security
        response = requests.post(
            f"{api_base}/memories/delete",
            json={"user_id": user_id, "memory_ids": memory_ids}
        )
        if response.status_code == 204:  # Success (No Content)
            st.toast(f"Deleted {len(memory_ids)} memories! 🗑️")
            return True
        else:
            st.error(f"Failed to delete: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error while deleting: {e}")
        return False