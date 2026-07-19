"""FastAPI Upload 入口 — Web 端文件上传。

流程：
    Browser → HTTP Multipart → Upload API → IngressService → UploadAdapter → InputFile

依赖注入链（由 main.py 创建）：
    WorkspaceManager → IngressService → FastAPI Depends
"""

from dataclasses import dataclass

from fastapi import APIRouter, Depends, File, UploadFile

from ..model.source import UploadSource
from ..service.ingress_service import IngressService

router = APIRouter(prefix="/ingress", tags=["ingress"])


# ---- 响应模型 ----

@dataclass
class InputFileResponse:
    """上传成功的响应体。"""
    id: str
    filename: str
    mime: str
    size: int
    checksum: str
    source: str

    @classmethod
    def from_input_file(cls, f):
        return cls(
            id=str(f.id),
            filename=f.filename,
            mime=f.mime,
            size=f.size,
            checksum=f.checksum,
            source=f.source.name,
        )


# ---- FastAPI 依赖注入（替代全局变量） ----

_ingress_service: IngressService | None = None


def _get_ingress_service() -> IngressService:
    """FastAPI Depends 工厂 — 由 main.py 在启动时注入实例。"""
    if _ingress_service is None:
        raise RuntimeError(
            "IngressService 未初始化，请在 main.py 中调用 init_ingress_service()"
        )
    return _ingress_service


def init_ingress_service(service: IngressService) -> None:
    """初始化 IngressService（由 main.py 启动时调用一次）。"""
    global _ingress_service
    _ingress_service = service


# ---- 路由 ----

@router.post("/upload", response_model=InputFileResponse)
async def upload(
    file: UploadFile = File(...),
    svc: IngressService = Depends(_get_ingress_service),
):
    """上传单个文件 → InputFile 摘要。

    curl::

        curl -F "file=@report.pdf" http://localhost:8000/ingress/upload
    """
    content = await file.read()
    source = UploadSource(
        filename=file.filename or "unknown",
        content=content,
    )
    input_file = svc.ingest(source)
    return InputFileResponse.from_input_file(input_file)
