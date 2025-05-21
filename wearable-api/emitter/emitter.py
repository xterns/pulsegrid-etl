import time
import random
import requests
from datetime import datetime

while True:
    simulated_data = {
        "user_id": "123",
        "timestamp": str(datetime.utcnow()),
        "heart_rate": random.randint(60, 100),
        "steps": random.randint(3000, 10000),
        "sleep_hours": round(random.uniform(5.5, 8.5), 1)
    }

    try:
        response = requests.post("http://listener:8000/internal/update", json=simulated_data)
        print(f"[{datetime.utcnow()}] Sent update to listener - Status: {response.status_code}")
    except Exception as e:
        print("❌ Failed to send data:", e)

    time.sleep(10)

