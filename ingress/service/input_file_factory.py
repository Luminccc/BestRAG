"""InputFileFactory — the ONLY way to create an InputFile.

Adapters MUST NOT create InputFile directly.
"""

from pathlib import Path
from uuid import uuid4

from ..model.input_file import InputFile
from ..model.source_type import SourceType
from .checksum import calculate
from .metadata_reader import created_time, extension, size
from .mime_detector import detect


class InputFileFactory:
    """Factory that assembles an InputFile with all metadata populated."""

    @staticmethod
    def create(path: Path, source: SourceType) -> InputFile:
        """Build an InputFile from a file on disk.

        Args:
            path: Absolute path to the file on disk.
            source: Origin of the file (UPLOAD, LOCAL, FOLDER).

        Returns:
            A fully-populated InputFile (frozen dataclass).
        """
        return InputFile(
            id=uuid4(),
            filename=path.name,
            extension=extension(path),
            mime=detect(path),
            path=path.resolve(),
            size=size(path),
            checksum=calculate(path),
            source=source,
            created_at=created_time(path),
        )
