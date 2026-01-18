# backend/main.py

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.websocket import interview_socket

app = FastAPI()

# Add CORS middleware for better cross-origin support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


@app.get("/")
def home():
    """
    HTTP is used only to LOAD the frontend.
    """
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse(
            "<h1>Error: frontend/index.html not found</h1>"
            "<p>Please ensure the frontend directory exists with index.html</p>",
            status_code=500
        )


@app.get("/health")
def health_check():
    """
    Simple health check endpoint
    """
    return {
        "status": "ok",
        "service": "AI Interview System",
        "version": "1.0.0"
    }


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """
    Delegate WebSocket handling to websocket.py
    """
    await interview_socket(ws)