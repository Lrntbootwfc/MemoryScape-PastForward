import requests

# Set the URL of your FastAPI endpoint
url = "http://127.0.0.1:8000/api/signup"

# Prepare the data to be sent in the request body
# This is equivalent to what Postman's form-data should do
data = {
    "email": "testuser@example.com",
    "name": "Test User",
    "password": "test_password"
}

# Make the POST request
try:
    response = requests.post(url, data=data)
    response.raise_for_status() # This will raise an HTTPError if the status code is bad
    
    # Print the response details
    print("Request was successful!")
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())

except requests.exceptions.RequestException as e:
    print("An error occurred during the request:")
    print(e)
    if response:
        print("Response Status Code:", response.status_code)
        print("Response Body:", response.text)