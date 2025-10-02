# server.py
import asyncio
import json
import random
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocketDisconnect
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/containers")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Mock data, normally you'd fetch this from Docker API
            data = [
                {
                    "name": "analytica_django",
                    "cpu": round(random.uniform(0, 5), 2),
                    "memory": f"{random.randint(200, 500)}MB / 3919MB",
                    "status": "running",
                    "health": "N/A",
                },
                {
                    "name": "analytica-hub-project-celery-1",
                    "cpu": round(random.uniform(0, 5), 2),
                    "memory": f"{random.randint(400, 600)}MB / 3919MB",
                    "status": "running",
                    "health": "N/A",
                },
                {
                    "name": "analytica_flask",
                    "cpu": round(random.uniform(0, 5), 2),
                    "memory": f"{random.randint(250, 350)}MB / 3919MB",
                    "status": "running",
                    "health": "N/A",
                },
                {
                    "name": "analytica_redis",
                    "cpu": round(random.uniform(0, 5), 2),
                    "memory": f"{random.randint(20, 30)}MB / 3919MB",
                    "status": "running",
                    "health": "N/A",
                },
                {
                    "name": "analytica_mysql",
                    "cpu": round(random.uniform(0, 5), 2),
                    "memory": f"{random.randint(450, 500)}MB / 3919MB",
                    "status": "running",
                    "health": "N/A",
                },
            ]
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(3)  # send every 3 seconds
    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
