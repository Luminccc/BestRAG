"""SHA256 checksum calculation for files."""

import hashlib
from pathlib import Path


def calculate(path: Path, chunk_size: int = 64 * 1024) -> str:
    """Return the SHA256 hex digest of a file.

    Reads in chunks to handle large files without loading into memory.
    """
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            sha.update(chunk)
    return sha.hexdigest()


def calculate_bytes(content: bytes) -> str:
    """Return the SHA256 hex digest of raw bytes."""
    return hashlib.sha256(content).hexdigest()
