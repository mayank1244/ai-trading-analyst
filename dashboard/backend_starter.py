"""Automatic Background FastAPI Server Starter for Streamlit Cloud Deployment."""

import os
import socket
import sys
import threading
import time

# Ensure project root is in sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


def ensure_backend_running():
    """Ensure FastAPI backend is running on 127.0.0.1:8000."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    is_running = sock.connect_ex(("127.0.0.1", 8000)) == 0
    sock.close()

    if not is_running:
        try:
            import uvicorn
            from app.main import app as fastapi_app

            def _run():
                uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="warning")

            t = threading.Thread(target=_run, daemon=True)
            t.start()
            # Give backend 2 seconds to initialize SQLite DB and bind port
            time.sleep(2)
        except Exception:
            pass
