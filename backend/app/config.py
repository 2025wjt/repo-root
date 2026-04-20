from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / 'data'
DB_PATH = DATA_DIR / 'app.db'
PROJECTS_DIR = ROOT_DIR / 'projects'
EXPORTS_DIR = DATA_DIR / 'exports'
LOGS_DIR = DATA_DIR / 'logs'

DEFAULT_REVIEWER = 'human_reviewer'
DEFAULT_CREATED_BY = 'user'

for path in (DATA_DIR, PROJECTS_DIR, EXPORTS_DIR, LOGS_DIR):
    path.mkdir(parents=True, exist_ok=True)
