# run.py

"""
Main entry point to start the FastAPI server
"""

import uvicorn
from backend.config import HOST, PORT

if __name__ == "__main__":
    print(f"Starting AI Interview System on {HOST}:{PORT}")
    print(f"Open browser at: http://localhost:{PORT}")
    
    uvicorn.run(
        "backend.main:app",
        host=HOST,
        port=PORT,
        reload=True
    )