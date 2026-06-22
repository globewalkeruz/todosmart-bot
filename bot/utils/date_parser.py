from __future__ import annotations
from datetime import datetime, timedelta


def parse_due_date(text: str) -> datetime | None:
    """
    Parse natural-language or explicit date strings into a datetime.
    Accepts: 'tomorrow', 'next week', 'skip', DD.MM.YYYY, DD/MM/YYYY, YYYY-MM-DD
    Returns None if parsing fails or user types 'skip'.
    """
    text = text.strip().lower()

    if text in ("skip", "no", "-", "none"):
        return None

    now = datetime.now()

    if text == "tomorrow":
        return datetime(now.year, now.month, now.day, 9, 0) + timedelta(days=1)

    if text in ("next week", "week"):
        return datetime(now.year, now.month, now.day, 9, 0) + timedelta(days=7)

    if text in ("today", "now"):
        return now.replace(second=0, microsecond=0)

    # Try common explicit formats
    for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d", "%d.%m.%Y %H:%M", "%d/%m/%Y %H:%M"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    return None


def compute_reminder_offset(offset: str) -> datetime | None:
    now = datetime.now()
    mapping = {
        "1h":       now + timedelta(hours=1),
        "3h":       now + timedelta(hours=3),
        "tomorrow": datetime(now.year, now.month, now.day, 9, 0) + timedelta(days=1),
        "week":     datetime(now.year, now.month, now.day, 9, 0) + timedelta(days=7),
    }
    return mapping.get(offset)
