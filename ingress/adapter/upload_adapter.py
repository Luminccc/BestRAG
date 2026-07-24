"""UploadAdapter — 处理浏览器上传的文件。

支持两种构造方式（向后兼容）：

    # V2 推荐：Source 对象
    adapter = UploadAdapter(UploadSource("report.pdf", content), wm)

    # V1 兼容：直接传参数
    adapter = UploadAdapter(file_content, original_filename, wm)
"""

from ..model.input_file import InputFile
from ..model.source import UploadSource
from ..model.source_type import SourceType
from ..service.checksum import calculate_bytes
from ..service.input_file_factory import InputFileFactory
from .base_adapter import BaseAdapter


class UploadAdapter(BaseAdapter):
    """浏览器上传适配器。"""

    def __init__(self, source_or_content, filename_or_wm=None, workspace_manager=None):
        """构造器 — 支持 UploadSource 或原始参数（向后兼容）。"""
        if isinstance(source_or_content, UploadSource):
            # V2: UploadSource + WorkspaceManager
            self._content = source_or_content.content
            self._filename = source_or_content.filename
            self._wm = filename_or_wm  # 第二个参数是 workspace_manager
        else:
            # V1: content + filename + workspace_manager
            self._content = source_or_content
            self._filename = filename_or_wm
            self._wm = workspace_manager

    def load(self) -> InputFile:
        # 1. 计算原始字节的 checksum（用于去重 + 命名）
        checksum = calculate_bytes(self._content)
        ext = self._extract_extension()

        # 2. 保存到 workspace，文件名 = <sha256>.<ext>
        saved_path = self._wm.save_upload(self._content, checksum, ext)

        # 3. 通过 Factory 创建 InputFile（唯一方式）
        input_file = InputFileFactory.create(saved_path, SourceType.UPLOAD)

        # 4. 覆盖 filename 保留原始上传文件名
        object.__setattr__(input_file, "filename", self._filename)
        return input_file

    def _extract_extension(self) -> str:
        """从原始文件名提取扩展名。"""
        if "." in self._filename:
            return self._filename.rsplit(".", 1)[1]
        return ""
