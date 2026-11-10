import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
SERVICES = [
    ("assistant_subsystem/backend/src", "main:app", 8000),
    ("classification_subsystem/backend", "src.main:app", 8001),
    ("dashboard_subsystem", "waste_analytics.api:app", 8002),
]

if __name__ == "__main__":
    load_dotenv(ROOT / ".env")
    processes = [
        subprocess.Popen([sys.executable, "-m", "uvicorn", app, "--port", str(port)], cwd=ROOT / folder)
        for folder, app, port in SERVICES
    ]
    try:
        for process in processes:
            process.wait()
    except KeyboardInterrupt:
        pass
    finally:
        for process in processes:
            process.terminate()
