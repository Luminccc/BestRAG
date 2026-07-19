"""FolderAdapter — 扫描本地目录，为每个文件生成 InputFile。

支持两种构造方式（向后兼容）：

    # V2 推荐：Source 对象
    adapter = FolderAdapter(FolderSource(Path("/data/docs"), recursive=True))

    # V1 兼容：直接传参数
    adapter = FolderAdapter(Path("/data/docs"), recursive=True)
"""

from pathlib import Path

from ..model.input_file import InputFile
from ..model.source import FolderSource
from ..model.source_type import SourceType
from ..service.input_file_factory import InputFileFactory
from .base_adapter import BaseBatchAdapter


class FolderAdapter(BaseBatchAdapter):
    """文件夹批量适配器。"""

    def __init__(self, source_or_dir, recursive=False):
        """构造器 — 支持 FolderSource 或直接传目录（向后兼容）。"""
        if isinstance(source_or_dir, FolderSource):
            self._dir = source_or_dir.directory
            self._recursive = source_or_dir.recursive
        else:
            self._dir = Path(source_or_dir)
            self._recursive = recursive

        if not self._dir.is_dir():
            raise NotADirectoryError(f"不是目录: {self._dir}")

    def load(self) -> list[InputFile]:
        pattern = "**/*" if self._recursive else "*"
        files: list[InputFile] = []
        for p in self._dir.glob(pattern):
            if p.is_file():
                files.append(InputFileFactory.create(p, SourceType.FOLDER))
        return files
