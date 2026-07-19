"""File metadata reader — size, extension, creation time, etc."""

import os
from datetime import datetime, timezone
from pathlib import Path


def read(path: Path) -> dict:
    """Return basic file metadata as a dict.

    Keys: size, filename, extension, created_time
    """
    stat = path.stat()
    return {
        "size": stat.st_size,
        "filename": path.name,
        "extension": path.suffix.lower(),
        "created_time": datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc),
    }


def size(path: Path) -> int:
    return path.stat().st_size


def extension(path: Path) -> str:
    return path.suffix.lower()


def created_time(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_ctime, tz=timezone.utc)
