"""InputFile — the one and only domain object of the Ingress module.

All adapters MUST return InputFile (or List[InputFile]).
InputFile MUST be created via InputFileFactory — never directly by adapters.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from .source_type import SourceType


@dataclass(frozen=True)
class InputFile:
    id: UUID
    filename: str
    extension: str
    mime: str
    path: Path
    size: int
    checksum: str
    source: SourceType
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
