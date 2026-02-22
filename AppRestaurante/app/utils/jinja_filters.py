import json
import re
from typing import Any, Optional


def from_json(value: Any) -> Optional[dict]:
    """Parse a JSON string into a dict for use in Jinja templates.

    Returns None if parsing fails or if the decoded value isn't a JSON object.
    """
    if value is None:
        return None

    if isinstance(value, dict):
        return value

    if not isinstance(value, str):
        return None

    text = value.strip()
    if not text:
        return None

    def _try_load(s: str) -> Optional[dict]:
        try:
            obj = json.loads(s)
        except Exception:
            return None
        return obj if isinstance(obj, dict) else None

    decoded = _try_load(text)
    if decoded is None:
        # Some stored values look like JSON objects but are missing commas between
        # properties (e.g. lines like: "lunes": "..."\n"martes": "...").
        # This normalizes that format into valid JSON.
        repaired = text
        repaired = repaired.replace("\r\n", "\n")
        repaired = repaired.replace("\t", " ")

    # Heuristic repair: if a line ends with a quoted string value and the next
    # non-empty line starts with a quoted key, add a trailing comma.
    # Example to fix:
    #   "lunes": "..."\n"martes": "..."
        repaired = re.sub(
            r'(\"\s*)\n(\s*\"[^\"]+\"\s*:)',
            r'\1,\n\2',
            repaired,
        )
        decoded = _try_load(repaired)

    if decoded is None:
        return None

    return decoded
