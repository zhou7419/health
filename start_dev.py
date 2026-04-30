import subprocess
import os
import sys
import time

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "web")

    print("=" * 45)
    print("       Health Metrics Project")
    print("    Starting Backend and Frontend...")
    print("=" * 45)

    try:
        # Start backend
        print("[1/2] Starting FastAPI Backend on port 8000...")
        backend_cmd = ["uvicorn", "app.main:app", "--reload", "--port", "8000"]
        # Use shell=True on Windows to resolve executable path, otherwise False
        is_windows = sys.platform.startswith("win")
        backend_process = subprocess.Popen(
            backend_cmd, 
            cwd=backend_dir, 
            shell=is_windows
        )

        time.sleep(1) # Give backend a slight head start

        # Start frontend
        print("[2/2] Starting Vue Frontend on port 5173...")
        frontend_cmd = ["npm", "run", "dev"]
        frontend_process = subprocess.Popen(
            frontend_cmd, 
            cwd=frontend_dir, 
            shell=is_windows
        )

        print("\nBoth services are running!")
        print("- Backend API: http://127.0.0.1:8000/docs")
        print("- Frontend UI: http://localhost:5173/\n")
        print("Press Ctrl+C to stop both services.")

        # Wait for both processes to keep script alive
        backend_process.wait()
        frontend_process.wait()

    except KeyboardInterrupt:
        print("\nStopping services...")
        backend_process.terminate()
        frontend_process.terminate()
        print("All services stopped.")

if __name__ == "__main__":
    main()
