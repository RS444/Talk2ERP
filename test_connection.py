# test_connection.py

import requests

HEADERS = {
    "Authorization": "token c9c6c138eadf3b9:2429ffa3e38edd2",
    "Content-Type": "application/json"
}

url = "http://localhost:8000/api/resource/Material Request"

response = requests.get(url, headers=HEADERS)

print("✅ Status:", response.status_code)
print("📄 Response:", response.json())
