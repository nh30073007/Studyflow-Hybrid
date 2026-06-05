import requests
import json

url = "http://localhost:8000/ask"
data = {
    "user_id": "test_user",
    "question": "অ শেখাও"
}

try:
    response = requests.post(url, json=data, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")