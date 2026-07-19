"""MIME type detection — filetype first, extension fallback, python-magic last."""

import mimetypes
from pathlib import Path


def detect(path: Path) -> str:
    """Detect MIME type of a file.

    1. ``filetype`` (magic bytes, cross-platform)
    2. Extension-based fallback (stdlib mimetypes)
    3. ``python-magic`` if available
    4. ``application/octet-stream``
    """
    import filetype  # type: ignore

    kind = filetype.guess(str(path))
    if kind is not None:
        return kind.mime

    # Extension-based fallback
    mime, _ = mimetypes.guess_type(str(path))
    if mime:
        return mime

    return _magic_fallback(path)


def _magic_fallback(path: Path) -> str:
    try:
        import magic  # type: ignore
        m = magic.Magic(mime=True)
        return m.from_file(str(path))
    except Exception:
        return "application/octet-stream"
