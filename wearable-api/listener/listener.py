from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

current_data = {
    "user_id": "123",
    "timestamp": str(datetime.utcnow()),
    "heart_rate": 72,
    "steps": 5000,
    "sleep_hours": 6.5
}

@app.get("/")
def root():
    return {"message": "Wearable Listener API is running"}

@app.get("/wearables/user/{user_id}")
def get_wearable_data(user_id: str):
    if user_id == current_data.get("user_id"):
        return current_data
    return {"error": "User not found"}, 404

@app.post("/internal/update")
async def update_data(request: Request):
    global current_data
    new_data = await request.json()
    current_data = new_data
    current_data["timestamp"] = str(datetime.utcnow())
    return {"status": "updated", "data": current_data}

