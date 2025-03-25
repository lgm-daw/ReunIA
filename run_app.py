"""
Wrapper script to run both the FastAPI backend and Streamlit frontend.
Usage: streamlit run run_app.py
"""

import os
import sys
import subprocess

if __name__ == "__main__":
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    subprocess.run([sys.executable, "backend/main.py"])
