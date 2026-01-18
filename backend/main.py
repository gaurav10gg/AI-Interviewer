# backend/main.py

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from backend.websocket import interview_socket

app = FastAPI()

# Serve frontend static files
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


@app.get("/")
def home():
    """
    HTTP is used only to LOAD the frontend.
    """
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """
    Delegate WebSocket handling to websocket.py
    """
    await interview_socket(ws)
