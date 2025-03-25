import threading
import subprocess
import time
import os
import sys

def run_fastapi():
    """Run the FastAPI backend server"""
    subprocess.run(["uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000"])

def run_streamlit():
    subprocess.run(["streamlit", "run", "frontend/frontend.py"])

if __name__ == "__main__":
    # Start FastAPI in a separate thread
    backend_thread = threading.Thread(target=run_fastapi, daemon=True)
    backend_thread.start()

    # Give the backend a moment to start up
    print("Starting FastAPI backend on http://127.0.0.1:8000...")
    time.sleep(2)

    # Run the Streamlit app in the main thread
    print("Starting Streamlit frontend...")
    run_streamlit()
