"""ASGI entry: Adds ``app/`` to ``sys.path`` and exposes the FastAPI ``app``.
Production server configuration using uvicorn.
"""

from __future__ import annotations
import sys
import os
from pathlib import Path

# Add 'app' directory to sys.path
_APP_DIR = Path(__file__).resolve().parent / 'app'
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

# Import the configured settings and the app
from config import settings
from api.app import app

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment (Railway/Render standard)
    port = int(os.environ.get("PORT", settings.port))
    
    print(f"Starting server on port {port}...")
    uvicorn.run(
        "server:app", 
        host=settings.host, 
        port=port, 
        reload=settings.debug,
        log_level="info"
    )

__all__ = ['app']
