$root = Split-Path -Parent $PSScriptRoot
python -m uvicorn app.main:app --app-dir "$root/backend" --host 127.0.0.1 --port 8000 --reload
