import threading
import webbrowser
import time
import os
import sys
from app.main import app
import uvicorn

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def start_server():
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)


# Run server in background thread
thread = threading.Thread(target=start_server, daemon=True)
thread.start()

# Wait a bit
time.sleep(2)

# Open UI
html_path = resource_path("index.html")
webbrowser.open(f"file://{html_path}")

# Keep app alive
while True:
    time.sleep(1)