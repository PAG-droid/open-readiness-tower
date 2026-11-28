"""UTC policy for allocation windows, evidence expiry, and evaluation times."""

from datetime import UTC, datetime


def as_utc(value: datetime) -> datetime:
    """Interpret legacy naive timestamps as UTC; convert explicit offsets to UTC."""
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
