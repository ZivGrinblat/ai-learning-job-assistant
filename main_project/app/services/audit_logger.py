"""
Append-only API request log for text analysis endpoints.

LOG_FILE_PATH is monkeypatched in tests to write to a temp directory.
Side effect only — callers don't use the return value.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LOG_FILE_PATH = Path("logs/api_requests.log")
LOG_ENTRY_SEPARATOR = "\n---\n\n"


def write_api_log(
    method: str,
    url: str,
    status_code: int,
    result: dict[str, Any],
) -> None:
    LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": method,
        "url": url,
        "status_code": status_code,
        "result": result,
    }

    formatted_entry = json.dumps(log_entry, indent=2, ensure_ascii=False)
    needs_separator = LOG_FILE_PATH.exists() and LOG_FILE_PATH.stat().st_size > 0

    with LOG_FILE_PATH.open("a", encoding="utf-8") as log_file:
        if needs_separator:
            log_file.write(LOG_ENTRY_SEPARATOR)
        log_file.write(formatted_entry)
        log_file.write("\n")
