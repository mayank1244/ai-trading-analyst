"""Launcher script for AI Trading Analyst (FastAPI + Streamlit)."""

import os
import subprocess
import sys
import time


def main():
    print("=" * 60)
    print("      AI Trading Analyst -- Production-Grade Launch")
    print("=" * 60)

    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    print("\n[1/2] Starting FastAPI Backend on http://localhost:8000...")
    api_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=project_dir,
    )

    time.sleep(3)

    print("\n[2/2] Starting Streamlit Dashboard on http://localhost:8501...")
    dashboard_proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "dashboard/main.py",
            "--server.port",
            "8501",
            "--browser.gatherUsageStats",
            "false",
            "--server.headless",
            "true",
        ],
        cwd=project_dir,
    )

    print("\n" + "=" * 60)
    print("AI Trading Analyst is running!")
    print("   FastAPI Docs:        http://localhost:8000/docs")
    print("   Streamlit Dashboard: http://localhost:8501")
    print("=" * 60)

    try:
        api_proc.wait()
        dashboard_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping services...")
        api_proc.terminate()
        dashboard_proc.terminate()


if __name__ == "__main__":
    main()
