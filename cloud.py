# cloud.py

import requests

CLOUD_ENDPOINT = "https://your-cloud-service.com/api/logs"  # Replace with your cloud endpoint
API_KEY = "your_api_key_here"  # Replace with your API key

def log_data_to_cloud(temperature, humidity, presence, light_state):
    data = {
        "temperature": temperature,
        "humidity": humidity,
        "presence": presence,
        "light_state": light_state
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    try:
        response = requests.post(CLOUD_ENDPOINT, json=data, headers=headers)
        if response.status_code == 200:
            print("Data logged to cloud successfully.")
        else:
            print(f"Failed to log data to cloud. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while logging data to cloud: {e}")
