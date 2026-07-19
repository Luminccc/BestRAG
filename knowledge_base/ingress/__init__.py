"""BestRAG Ingress — 所有外部数据源的统一入口。

完整调用链：

    Entry (API/CLI) → IngressService → Adapter → InputFileFactory → InputFile

所有 Adapter 将外部资源转换为单一领域对象：InputFile。
"""

from .adapter import (
    BaseAdapter,
    BaseBatchAdapter,
    FolderAdapter,
    LocalAdapter,
    UploadAdapter,
)
from .entry import cli_app
from .api.upload_api import router as upload_router
from .model import FolderSource, InputFile, LocalSource, SourceType, UploadSource
from .service import (
    IngressService,
    InputFileFactory,
    calculate,
    calculate_bytes,
    created_time,
    detect,
    extension,
    read,
    size,
)

__all__ = [
    # model
    "InputFile",
    "SourceType",
    "LocalSource",
    "FolderSource",
    "UploadSource",
    # adapter
    "BaseAdapter",
    "BaseBatchAdapter",
    "UploadAdapter",
    "LocalAdapter",
    "FolderAdapter",
    # service
    "IngressService",
    "InputFileFactory",
    "calculate",
    "calculate_bytes",
    "detect",
    "read",
    "size",
    "extension",
    "created_time",
    # entry
    "upload_router",
    "cli_app",
]
