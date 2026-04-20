from datetime import datetime, timezone
from uuid import uuid4


def generate_id(prefix: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{prefix}_{timestamp}_{uuid4().hex[:6]}"
