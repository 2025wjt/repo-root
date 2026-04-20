from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.legacy.db import Database


if __name__ == "__main__":
    database = Database()
    database.init()
    print(f"Initialized database at {database.db_path}")
