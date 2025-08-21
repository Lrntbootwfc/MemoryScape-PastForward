# backend/tests/test_memories.py
import requests
import os
from PIL import Image

BASE_URL = "http://127.0.0.1:8000/api"
TEST_USER_ID = 2 # Change this to the user ID you got from test_auth.py
TEST_IMAGE_PATH = "test_image.jpg"
TEST_VIDEO_PATH = "test_video.mp4"

# --- Create dummy files for upload ---
if not os.path.exists(TEST_IMAGE_PATH):
    # CORRECTED: Create a valid, empty image file using Pillow
    img = Image.new('RGB', (1, 1))
    img.save(TEST_IMAGE_PATH)
if not os.path.exists(TEST_VIDEO_PATH):
    # CORRECTED: Create a valid, empty text file for video.
    # We will not validate video, so this is fine.
    with open(TEST_VIDEO_PATH, "w") as f:
        f.write("This is a dummy video file.")

# --- Test 1: Create a memory with an image ---
print("--- Testing Create Memory API (Image) ---")
try:
    # We open the file in binary mode for the POST request
    with open(TEST_IMAGE_PATH, "rb") as image_file:
        files = {'file': (TEST_IMAGE_PATH, image_file, 'image/jpeg')}
        data = {
            "user_id": str(TEST_USER_ID),
            "title": "My first test memory",
            "desc": "A memory created via a test script.",
            "emotion": "happy"
        }
        response = requests.post(f"{BASE_URL}/memories", files=files, data=data)
        response.raise_for_status()
        memory = response.json()
        print("Memory created successfully:", memory)
except requests.exceptions.HTTPError as err:
    print(f"Create memory failed: {err}")
    print("Response:", err.response.text)

# --- Test 2: Create a memory with a video ---
print("\n--- Testing Create Memory API (Video) ---")
try:
    with open(TEST_VIDEO_PATH, "rb") as video_file:
        files = {'file': (TEST_VIDEO_PATH, video_file, 'video/mp4')}
        data = {
            "user_id": str(TEST_USER_ID),
            "title": "A video memory",
            "desc": "Testing video upload.",
            "emotion": "excitement"
        }
        response = requests.post(f"{BASE_URL}/memories", files=files, data=data)
        response.raise_for_status()
        memory = response.json()
        print("Memory created successfully:", memory)
except requests.exceptions.HTTPError as err:
    print(f"Create memory failed: {err}")
    print("Response:", err.response.text)
    
# --- Test 3: Get all memories for the user ---
print("\n--- Testing Get Memories API ---")
try:
    response = requests.get(f"{BASE_URL}/memories?user_id={TEST_USER_ID}")
    response.raise_for_status()
    memories = response.json()
    print(f"Successfully retrieved {len(memories)} memories.")
    print("First memory:", memories[0] if memories else "No memories found.")
except requests.exceptions.HTTPError as err:
    print(f"Get memories failed: {err}")
    print("Response:", err.response.text)