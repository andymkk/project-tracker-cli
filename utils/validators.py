"""Input validation helpers."""
from datetime import datetime

DATE_FORMAT = "%Y-%m-%d"


def parse_date(value):
    """Validate a YYYY-MM-DD date string and return it normalised.

    Raises ValueError with a friendly message if the format is wrong.
    """
    try:
        return datetime.strptime(value.strip(), DATE_FORMAT).strftime(DATE_FORMAT)
    except (ValueError, AttributeError):
        raise ValueError(f"'{value}' is not a valid date. Use YYYY-MM-DD.") from None
