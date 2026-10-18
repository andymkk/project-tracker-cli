"""JSON persistence for users, projects and tasks."""
import json
import logging
import os
import tempfile
from pathlib import Path

from models.user import User

logger = logging.getLogger(__name__)

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "data.json"


class StorageError(Exception):
    """Raised when the data file cannot be read or written."""


def load_users(path=DEFAULT_PATH):
    """Load all users from a JSON file.

    A missing file is treated as an empty database. A corrupt file raises
    StorageError so the CLI can show a clear message instead of a traceback.
    """
    path = Path(path)
    if not path.exists():
        logger.info("No data file at %s; starting empty.", path)
        return []
    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
        return [User.from_dict(item) for item in raw.get("users", [])]
    except json.JSONDecodeError as err:
        raise StorageError(f"{path} is not valid JSON: {err}") from err
    except (KeyError, TypeError, AttributeError, ValueError) as err:
        raise StorageError(f"{path} has unexpected contents: {err!r}") from err
    except OSError as err:
        raise StorageError(f"Could not read {path}: {err}") from err


def save_users(users, path=DEFAULT_PATH):
    """Save all users to a JSON file (written atomically)."""
    path = Path(path)
    payload = {"users": [user.to_dict() for user in users]}
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        os.replace(tmp_name, path)
    except OSError as err:
        raise StorageError(f"Could not write {path}: {err}") from err
    logger.info("Saved %d user(s) to %s", len(users), path)
