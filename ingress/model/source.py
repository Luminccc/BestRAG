"""Source 抽象对象 — 解耦 Adapter 与原始输入。

所有外部数据在进入 Ingress 前先封装为 Source 对象，
Adapter 只认识 Source，不认识 bytes / Path / URL。
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class LocalSource:
    """本地单文件来源。

    Usage::

        source = LocalSource(path=Path("/data/report.pdf"))
        result = ingress_service.ingest(source)
    """
    path: Path

    def __post_init__(self):
        if not self.path.is_file():
            raise FileNotFoundError(f"文件不存在: {self.path}")


@dataclass(frozen=True)
class FolderSource:
    """本地文件夹来源（批量导入）。

    Usage::

        source = FolderSource(directory=Path("/data/docs"), recursive=True)
        results = ingress_service.ingest(source)
    """
    directory: Path
    recursive: bool = False

    def __post_init__(self):
        if not self.directory.is_dir():
            raise NotADirectoryError(f"目录不存在: {self.directory}")


@dataclass
class UploadSource:
    """浏览器上传来源。

    Usage::

        source = UploadSource(filename="report.pdf", content=file_bytes)
        result = ingress_service.ingest(source)
    """
    filename: str
    content: bytes
    metadata: dict | None = None
