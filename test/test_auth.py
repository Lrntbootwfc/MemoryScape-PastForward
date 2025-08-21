# backend/tests/test_auth.py
import requests

BASE_URL = "http://127.0.0.1:8000/api"
TEST_USER_EMAIL = "testuser@example.com"
TEST_USER_NAME = "Test User"
TEST_USER_PASSWORD = "test_password"

# --- Test 1: Signup ---
print("--- Testing Signup API ---")
try:
    response = requests.post(f"{BASE_URL}/signup", data={
        "email": TEST_USER_EMAIL,
        "name": TEST_USER_NAME,
        "password": TEST_USER_PASSWORD,
    })
    response.raise_for_status()
    user = response.json()
    print("Signup successful! User:", user)
    # Return user ID for next tests
    user_id = user.get('id')
    print("User ID:", user_id)

except requests.exceptions.HTTPError as err:
    print(f"Signup failed: {err}")
    print("Response:", err.response.text)
    user_id = None # Signup failed, so we can't get a user ID
except Exception as e:
    print("An unexpected error occurred:", e)
    user_id = None

# --- Test 2: Login ---
print("\n--- Testing Login API ---")
try:
    response = requests.post(f"{BASE_URL}/login", data={
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
    })
    response.raise_for_status()
    user = response.json()
    print("Login successful! User:", user)
    user_id = user.get('id') # Update user ID in case signup was skipped
except requests.exceptions.HTTPError as err:
    print(f"Login failed: {err}")
    print("Response:", err.response.text)

print("\nAuthentication tests finished.")