"""
AirGuard Root Application Launcher.
Allows launching the Streamlit app directly from the workspace root directory:
    python run.py
"""

import sys
import subprocess
from pathlib import Path

if __name__ == "__main__":
    app_path = Path(__file__).resolve().parent / "airguard" / "app" / "Home.py"
    print(f"Starting AirGuard Dashboard: {app_path}")
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nShutting down AirGuard Dashboard. Goodbye!")
