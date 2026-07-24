"""LocalAdapter — 读取本地单个文件。

支持两种构造方式（向后兼容）：

    # V2 推荐：Source 对象
    adapter = LocalAdapter(LocalSource(Path("/data/report.pdf")))

    # V1 兼容：直接传路径
    adapter = LocalAdapter(Path("/data/report.pdf"))
"""

from pathlib import Path

from ..model.input_file import InputFile
from ..model.source import LocalSource
from ..model.source_type import SourceType
from ..service.input_file_factory import InputFileFactory
from .base_adapter import BaseAdapter


class LocalAdapter(BaseAdapter):
    """本地单文件适配器。"""

    def __init__(self, source: str | Path | LocalSource):
        """构造器 — 支持 LocalSource 或直接路径（向后兼容）。"""
        if isinstance(source, LocalSource):
            self._path = source.path
        else:
            self._path = Path(source)

        if not self._path.is_file():
            raise FileNotFoundError(f"不是文件: {self._path}")

    def load(self) -> InputFile:
        return InputFileFactory.create(self._path, SourceType.LOCAL)
