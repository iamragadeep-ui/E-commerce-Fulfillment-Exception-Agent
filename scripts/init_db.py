from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database.seed import create_database_and_seed


if __name__ == "__main__":
    create_database_and_seed()
    print("Database initialized successfully.")
