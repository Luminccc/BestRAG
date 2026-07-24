"""IngressService — 统一入口协调器。

所有外部请求必须经过 IngressService，不允许直接调用 Adapter。
职责：根据 Source 类型路由到对应 Adapter。
不负责：文件保存、文件解析、Document 生成。

注意：Adapter 导入使用延迟加载（方法内部 import），
以避免 service/__init__.py → adapter/ 的循环导入。
"""

from __future__ import annotations

from ..model.input_file import InputFile
from ..model.source import FolderSource, LocalSource, UploadSource


class IngressService:
    """Ingress 核心服务 — 统一协调 Entry → Adapter → Factory 流程。

    Usage::

        wm = WorkspaceManager()
        svc = IngressService(wm)

        # 本地文件
        input_file = svc.ingest(LocalSource(Path("./report.pdf")))

        # 文件夹批量
        input_files = svc.ingest(FolderSource(Path("./docs"), recursive=True))

        # 上传文件
        input_file = svc.ingest(UploadSource("report.pdf", content))
    """

    def __init__(self, workspace_manager):
        self._wm = workspace_manager

    def ingest(
        self,
        source: LocalSource | FolderSource | UploadSource,
    ) -> InputFile | list[InputFile]:
        """接收 Source 对象，路由到对应 Adapter，返回 InputFile。

        Args:
            source: LocalSource / FolderSource / UploadSource

        Returns:
            单文件返回 InputFile，批量返回 list[InputFile]
        """
        adapter = self._resolve(source)
        return adapter.load()

    # ---- 内部路由 ----

    def _resolve(self, source):
        """根据 Source 类型创建对应 Adapter（延迟导入以避免循环依赖）。"""
        if isinstance(source, LocalSource):
            from ..adapter.local_adapter import LocalAdapter
            return LocalAdapter(source.path)

        if isinstance(source, FolderSource):
            from ..adapter.folder_adapter import FolderAdapter
            return FolderAdapter(source.directory, recursive=source.recursive)

        if isinstance(source, UploadSource):
            from ..adapter.upload_adapter import UploadAdapter
            return UploadAdapter(source.content, source.filename, self._wm)

        raise TypeError(f"不支持的 Source 类型: {type(source)}")
